async def handle_claude_request(chat_uuid: str, request: ClaudeRequest):
    """
    Handle Claude requests using Claude API with session management
    """
    # Get or create Claude session ID for this chat
    claude_session_id = db.get_claude_session_id(chat_uuid)
    
    if not claude_session_id:
        # Create a new Claude session
        from claude_agent_sdk import ClaudeAgentOptions
        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
            permission_mode="acceptEdits"
        )

        # Create session via the Claude API
        create_session_data = {
            "profile": "dev",
            "system_prompt": "You are a helpful coding assistant",
            "allowed_tools": ["Read", "Write", "Edit", "Glob", "Grep"],
            "permission_mode": "acceptEdits",
            "model": request.option2  # Use the selected model
        }

        # Create session in our API
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post("http://localhost:8000/sessions", json=create_session_data) as resp:
                    if resp.status == 200:
                        session_result = await resp.json()
                        claude_session_id = session_result["session_id"]
                        # Store the session ID in the database
                        db.set_claude_session_id(chat_uuid, claude_session_id)
                    else:
                        error_text = await resp.text()
                        print(f"Failed to create Claude session: {resp.status}, {error_text}")
                        raise HTTPException(status_code=500, detail="Failed to create Claude session")
            except Exception as e:
                print(f"Error creating Claude session: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to create Claude session: {str(e)}")

    async def generate_stream():
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"[CLAUDE REQUEST] Sending query to Claude session {claude_session_id} for chat {chat_uuid}")
            logger.info(f"[CLAUDE REQUEST] Input prompt: {request.message}")
            
            # Send the query to Claude via our API
            query_data = {"prompt": request.message}
            
            async with aiohttp.ClientSession() as session:
                # Send the query
                async with session.post(f"http://localhost:8000/sessions/{claude_session_id}/query", json=query_data) as query_resp:
                    if query_resp.status != 200:
                        error_text = await query_resp.text()
                        logger.error(f"Failed to send query to Claude: {query_resp.status}, {error_text}")
                        yield f"data: Error: Failed to send query to Claude\n\n"
                        yield "data: [DONE]\n\n"
                        return
                    else:
                        logger.info(f"Query sent successfully to Claude session {claude_session_id}")

            # Stream the response from Claude events endpoint
            logger.info(f"[CLAUDE STREAM] Starting to stream response from session {claude_session_id}")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:8000/sessions/{claude_session_id}/events") as events_resp:
                    if events_resp.status != 200:
                        error_text = await events_resp.text()
                        logger.error(f"Failed to get Claude events: {events_resp.status}, {error_text}")
                        yield f"data: Error: Failed to get Claude response\n\n"
                        yield "data: [DONE]\n\n"
                        return

                    # Read the SSE stream and forward it
                    accumulated_response = []
                    logger.info(f"[CLAUDE STREAM] Starting to read Claude events stream for chat {chat_uuid}...")
                    async for line in events_resp.content:
                        line_str = line.decode('utf-8')
                        logger.debug(f"[CLAUDE STREAM] Raw line received: {repr(line_str)}")
                        
                        if line_str.startswith('data:'):
                            # Process the SSE data
                            data_content = line_str[5:].strip()  # Remove 'data:' prefix
                            logger.debug(f"[CLAUDE STREAM] Data content: {repr(data_content)}")
                            
                            if data_content == '[DONE]':
                                logger.info(f"[CLAUDE STREAM] Received DONE signal for chat {chat_uuid}")
                                break
                            elif data_content and data_content != '':
                                # Parse the JSON message
                                import json
                                try:
                                    message_data = json.loads(data_content)
                                    logger.debug(f"[CLAUDE STREAM] Parsed JSON: {type(message_data)}, keys: {list(message_data.keys()) if isinstance(message_data, dict) else 'N/A'}")
                                    
                                    # Extract text content from Claude's response based on message type
                                    if isinstance(message_data, dict):
                                        # Handle different Claude message types based on the SDK documentation
                                        
                                        # Check if it's an AssistantMessage (has 'content' as list of ContentBlocks)
                                        if 'content' in message_data and isinstance(message_data['content'], list):
                                            # This is likely an AssistantMessage with content blocks
                                            content_blocks = message_data['content']
                                            logger.debug(f"[CLAUDE STREAM] Processing AssistantMessage with {len(content_blocks)} content blocks")
                                            
                                            for block in content_blocks:
                                                logger.debug(f"[CLAUDE STREAM] Processing content block: {type(block)}, value: {repr(block)}")
                                                if isinstance(block, dict):
                                                    # Handle different content block types
                                                    block_type = block.get('type', 'unknown')
                                                    if 'text' in block:
                                                        # This could be a TextBlock
                                                        text_content = block['text']
                                                        if isinstance(text_content, str):
                                                            accumulated_response.append(text_content)
                                                            logger.debug(f"[CLAUDE STREAM] Yielding text content: {repr(text_content)}")
                                                            yield f"data: {text_content}\n\n"
                                                    elif block_type == 'text' and 'text' in block:
                                                        # Explicit text block
                                                        text_content = block['text']
                                                        accumulated_response.append(text_content)
                                                        logger.debug(f"[CLAUDE STREAM] Yielding explicit text block: {repr(text_content)}")
                                                        yield f"data: {text_content}\n\n"
                                                    elif block_type == 'tool_use':
                                                        # Tool use block
                                                        tool_name = block.get('name', 'unknown')
                                                        tool_input = block.get('input', {})
                                                        tool_text = f"[Using tool: {tool_name} with input: {tool_input}]"
                                                        accumulated_response.append(tool_text)
                                                        logger.debug(f"[CLAUDE STREAM] Yielding tool use: {repr(tool_text)}")
                                                        yield f"data: {tool_text}\n\n"
                                                    elif block_type == 'tool_result':
                                                        # Tool result block
                                                        tool_result = block.get('content', 'Tool completed')
                                                        result_text = str(tool_result)
                                                        accumulated_response.append(result_text)
                                                        logger.debug(f"[CLAUDE STREAM] Yielding tool result: {repr(result_text)}")
                                                        yield f"data: {result_text}\n\n"
                                                    elif block_type == 'thinking':
                                                        # Thinking block
                                                        thinking = block.get('thinking', '')
                                                        thinking_text = f"[Thinking: {thinking}]"
                                                        accumulated_response.append(thinking_text)
                                                        logger.debug(f"[CLAUDE STREAM] Yielding thinking: {repr(thinking_text)}")
                                                        yield f"data: {thinking_text}\n\n"
                                                    else:
                                                        # Unknown block type, try to extract any text
                                                        logger.debug(f"[CLAUDE STREAM] Unknown block type: {block_type}, trying to extract text")
                                                        for key, value in block.items():
                                                            if key == 'text' and isinstance(value, str):
                                                                accumulated_response.append(value)
                                                                logger.debug(f"[CLAUDE STREAM] Yielding text from unknown block: {repr(value)}")
                                                                yield f"data: {value}\n\n"
                                        elif message_data.get('subtype') in ['success', 'error']:
                                            # This is a ResultMessage, contains final result
                                            result_text = message_data.get('result', '')
                                            if result_text:
                                                accumulated_response.append(result_text)
                                                logger.info(f"[CLAUDE STREAM] Yielding final result: {repr(result_text)}")
                                                yield f"data: {result_text}\n\n"
                                            logger.info(f"[CLAUDE STREAM] Final message received with subtype: {message_data['subtype']} for chat {chat_uuid}")
                                            break
                                        elif 'message' in message_data and isinstance(message_data['message'], str):
                                            # This might be a system or error message
                                            message_text = message_data['message']
                                            accumulated_response.append(message_text)
                                            logger.debug(f"[CLAUDE STREAM] Yielding system/error message: {repr(message_text)}")
                                            yield f"data: {message_text}\n\n"
                                        else:
                                            # Try to find text content in any field
                                            logger.debug(f"[CLAUDE STREAM] Unknown message type, searching for text content in: {message_data}")
                                            for key, value in message_data.items():
                                                if isinstance(value, str) and key in ['text', 'content', 'message', 'result']:
                                                    accumulated_response.append(value)
                                                    logger.debug(f"[CLAUDE STREAM] Yielding text from {key}: {repr(value)}")
                                                    yield f"data: {value}\n\n"
                                    else:
                                        # If it's not a dict, just yield it as string
                                        message_str = str(message_data)
                                        accumulated_response.append(message_str)
                                        logger.debug(f"[CLAUDE STREAM] Yielding non-dict message: {repr(message_str)}")
                                        yield f"data: {message_str}\n\n"
                                except json.JSONDecodeError as e:
                                    # If not JSON, just yield the raw content
                                    logger.error(f"[CLAUDE STREAM] JSON decode error: {e}, raw content: {repr(data_content)}")
                                    if data_content.strip() != '':
                                        accumulated_response.append(data_content)
                                        yield f"data: {data_content}\n\n"
                        
                        # Check for connection issues
                        if not line_str:
                            logger.debug(f"[CLAUDE STREAM] Empty line received for chat {chat_uuid}, breaking")
                            break
                    logger.info(f"[CLAUDE STREAM] Finished reading Claude events stream for chat {chat_uuid}")
                    
        except Exception as e:
            logger.error(f"Error in Claude stream for chat {chat_uuid}: {e}")
            yield f"data: Error: {str(e)}\n\n"
        
        # Store the complete response
        complete_response = ' '.join(accumulated_response) if accumulated_response else "No response from Claude"
        logger.info(f"[CLAUDE RESPONSE] Complete response for chat {chat_uuid}: {repr(complete_response[:100])}...")
        
        # Save assistant's response to database
        db.add_message(chat_uuid, "assistant", complete_response.strip())
        logger.info(f"[CHAT {chat_uuid}] Claude response saved to database")

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")