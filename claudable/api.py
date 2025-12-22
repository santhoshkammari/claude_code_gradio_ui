from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import base64
import os
from typing import Optional, Dict, Any
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from src.mcp_tools.web import async_web_search
from database import ChatDatabase
import tiktoken

# Claude Agent SDK imports
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# For internal API calls
import aiohttp

# Session management
class SessionData:
    def __init__(self, client: ClaudeSDKClient, options: ClaudeAgentOptions, created_at: datetime):
        self.client = client
        self.options = options
        self.created_at = created_at
        self.last_activity = datetime.now()
        self.status = "ready"
        self.event_queue = asyncio.Queue()

# In-memory session store (use Redis in production)
session_store: Dict[str, SessionData] = {}

# Pydantic models for API requests and responses
class CreateSessionRequest(BaseModel):
    profile: Optional[str] = "default"
    system_prompt: Optional[str] = None
    allowed_tools: Optional[list[str]] = []
    permission_mode: Optional[str] = None
    model: Optional[str] = None
    cwd: Optional[str] = None

class CreateSessionResponse(BaseModel):
    session_id: str
    model: Optional[str]
    created_at: str
    status: str

class QueryRequest(BaseModel):
    prompt: str

class InterruptRequest(BaseModel):
    pass

class ResetRequest(BaseModel):
    hard_reset: Optional[bool] = False

DUMMY_RESPONSE = """## ⚠️ One important thing is missing
To act as **Scout**, I need the **actual user query** to analyze.

Right now, you've provided:
- ✅ the role (Scout)
- ✅ the rules and process
- ✅ the output format
- ❌ but **not the query Scout is supposed to interpret**"""

app = FastAPI(title="Claude API", version="1.0.0")
db = ChatDatabase()

# Mount static files directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024
    temperature: float = 0.7


class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5


class ClaudeRequest(BaseModel):
    message: str
    option1: str  # "claudecode" or "qwen"
    option2: str  # model name like "Claude Sonnet 4.5"


@app.get("/")
async def read_root():
    """
    Serve the main HTML page
    """
    html_path = Path(__file__).parent / "index.html"
    response = FileResponse(html_path)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    # Check if Claude Code CLI is available
    try:
        # Try to import to check if SDK is available
        import claude_agent_sdk
        claude_available = True
    except ImportError:
        claude_available = False

    return {
        "status": "healthy",
        "message": "Claude API is running",
        "claude_available": claude_available,
        "session_count": len(session_store)
    }


@app.post("/rbi")
async def claude_message(request: MessageRequest):
    pass


from src.agents.agent_search import search_agent


@app.post("/claude")
async def claude_search_endpoint(request: ClaudeRequest):
    """
    Direct search endpoint (not used in chat flow)
    """
    async def generate_stream():
        response = await search_agent(request.message)
        words = response.split(' ')
        for word in words:
            yield f"data: {word} \n\n"
            await asyncio.sleep(0.05)

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.post("/sample")
async def sample(request: ClaudeRequest):
    """
    Claude streaming endpoint that mimics LLM token-by-token response
    Later this will be replaced with actual LLM integration
    """
    async def generate_stream():
        # Dummy response that will be streamed token by token
        dummy_response = f"""Hello! I received your message: "{request.message}"

You selected:
- Mode: {request.option1}
- Model: {request.option2}

This is a dummy streaming response to demonstrate the streaming functionality.
In the future, this will be replaced with actual LLM responses from Claude or Qwen.

The system is working correctly and ready for integration with real language models.
Each word is being streamed token by token to simulate real LLM behavior.
This provides a smooth user experience with progressive text rendering.

Thank you for testing the Claudable interface!"""

        # Split into words and stream with delay
        words = dummy_response.split(' ')
        for word in words:
            yield f"data: {word} \n\n"
            await asyncio.sleep(0.05)  # Simulate processing delay

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.post("/web")
async def web_search_endpoint(request: WebSearchRequest):
    """
    Web search endpoint that performs a search using async_web_search
    """
    try:
        results = await async_web_search(request.query, request.max_results)
        return {"query": request.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New Chat Session Endpoints

@app.post("/api/chat/create")
async def create_chat(request: ClaudeRequest):
    """
    Create a new chat session with the first message
    Returns the chat UUID
    """
    try:
        # Generate title from first message
        title = db.generate_title_from_message(request.message)

        # Create chat session
        chat_uuid = db.create_chat(title=title)

        # Add user message
        db.add_message(chat_uuid, "user", request.message)

        return JSONResponse({
            "chat_uuid": chat_uuid,
            "title": title
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/{chat_uuid}")
async def serve_chat_page(chat_uuid: str):
    """
    Serve the chat page for a specific chat session
    """
    # Verify chat exists
    chat = db.get_chat(chat_uuid)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    html_path = Path(__file__).parent / "chat.html"
    response = FileResponse(html_path)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/api/chats")
async def get_all_chats():
    """
    Get all chat sessions
    """
    try:
        chats = db.get_all_chats()
        return JSONResponse({"chats": chats})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/{chat_uuid}/messages")
async def get_chat_messages(chat_uuid: str):
    """
    Get all messages for a specific chat
    """
    try:
        chat = db.get_chat(chat_uuid)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        messages = db.get_messages(chat_uuid)
        return JSONResponse({
            "chat": chat,
            "messages": messages
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/{chat_uuid}/message")
async def send_message_to_chat(chat_uuid: str, request: ClaudeRequest):
    """
    Send a message to an existing chat and stream the response
    """
    # Verify chat exists
    chat = db.get_chat(chat_uuid)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Always add the user message regardless of duplicates
    db.add_message(chat_uuid, "user", request.message)
    print(f"[CHAT {chat_uuid}] Added user message: {request.message}")
    message_added = True

    print(f"[CHAT {chat_uuid}] Mode: {request.option1}, Model: {request.option2}")

    # Check if this is a Claude "Code" mode request
    # Based on the UI, "code" is the value for Claude mode, "scout" for search agent
    if request.option1.lower() == "code":
        # This is a Claude request, use Claude API with session management
        return await handle_claude_request(chat_uuid, request)
    else:
        # This is a Scout or other mode, use existing search_agent
        return await handle_scout_request(chat_uuid, request)


async def handle_scout_request(chat_uuid: str, request: ClaudeRequest):
    """
    Handle Scout requests using existing search_agent
    """
    import logging
    logger = logging.getLogger(__name__)

    async def generate_stream():
        logger.info(f"[SCOUT REQUEST] Starting search_agent for chat {chat_uuid}")
        logger.info(f"[SCOUT REQUEST] Input prompt: {request.message}")

        response = await search_agent(request.message)
        logger.info(f"[SCOUT RESPONSE] Received response from search_agent: {repr(response[:100])}...")

        # Split response into words/tokens for streaming
        words = response.split(' ')

        # Stream each word/token
        accumulated_response = []
        for word in words:
            accumulated_response.append(word)
            # Send accumulated response so far
            current_response = ' '.join(accumulated_response)
            # Escape newlines for SSE format (use a placeholder)
            escaped_response = current_response.replace('\n', '\\n')
            logger.debug(f"[SCOUT STREAM] Yielding word: {repr(word)}")
            yield f"data: {escaped_response}\n\n"
            await asyncio.sleep(0.05)

        # Store the complete response
        complete_response = ' '.join(accumulated_response)
        logger.info(f"[SCOUT RESPONSE] Complete response for chat {chat_uuid}: {repr(complete_response[:100])}...")

        # Save assistant's response to database
        db.add_message(chat_uuid, "assistant", complete_response.strip())
        logger.info(f"[CHAT {chat_uuid}] Scout response saved to database")

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


async def handle_claude_request(chat_uuid: str, request: ClaudeRequest):
    """
    Handle Claude requests using Claude API with session management
    """
    # Map UI model names to valid Claude CLI model names
    model_name_mapping = {
        "Claude Sonnet 4.5": "sonnet",
        "Claude Opus 4.5": "opus",
        "Claude Haiku 4.5": "haiku",
        "Claude Claude": "claude",  # Direct mapping for 'claude'
        "sonnet": "sonnet",
        "opus": "opus",
        "haiku": "haiku",
        "claude": "claude"
    }

    # Get the mapped model name, defaulting to 'sonnet' if not found
    mapped_model = model_name_mapping.get(request.option2, "sonnet")

    # Get or create Claude session ID for this chat
    claude_session_id = db.get_claude_session_id(chat_uuid)

    if not claude_session_id:
        # Create a new Claude session
        from claude_agent_sdk import ClaudeAgentOptions
        options = ClaudeAgentOptions(
            # allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
            permission_mode="bypassPermissions",
        )

        # Create session via the Claude API
        create_session_data = {
            "profile": "dev",
            "system_prompt": "You are a helpful coding assistant",
            "allowed_tools": ["Read", "Write", "Edit", "Glob", "Grep"],
            "permission_mode": "acceptEdits",
            "model": mapped_model  # Use the mapped model name
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
                        line_str = line.decode("utf-8")
                        logger.debug(f"[CLAUDE STREAM] Raw line received: {repr(line_str)}")

                        if line_str.startswith("data:"):
                            # Process the SSE data
                            data_content = line_str[5:].strip()  # Remove "data:" prefix
                            logger.debug(f"[CLAUDE STREAM] Data content: {repr(data_content)}")

                            if data_content == "[DONE]":
                                logger.info(f"[CLAUDE STREAM] Received DONE signal for chat {chat_uuid}")
                                break
                            elif data_content and data_content != "":
                                # Parse the JSON message
                                import json
                                try:
                                    message_data = json.loads(data_content)
                                    logger.debug(f"[CLAUDE STREAM] Parsed JSON: {type(message_data)}, keys: {list(message_data.keys()) if isinstance(message_data, dict) else "N/A"}")

                                    # Extract text content from Claude"s response based on message type
                                    if isinstance(message_data, dict):
                                        # Handle different Claude message types based on the SDK documentation

                                        # Check if it"s an AssistantMessage (has "content" as list of ContentBlocks)
                                        if "content" in message_data and isinstance(message_data["content"], list):
                                            # This is likely an AssistantMessage with content blocks
                                            content_blocks = message_data["content"]
                                            logger.debug(f"[CLAUDE STREAM] Processing AssistantMessage with {len(content_blocks)} content blocks")

                                            for block in content_blocks:
                                                logger.debug(f"[CLAUDE STREAM] Processing content block: {type(block)}, value: {repr(block)}")
                                                if isinstance(block, dict):
                                                    # Handle different content block types
                                                    block_type = block.get("type", "unknown")
                                                    if "text" in block:
                                                        # This could be a TextBlock
                                                        text_content = block["text"]
                                                        if isinstance(text_content, str):
                                                            accumulated_response.append(text_content)
                                                            # Yield the accumulated response
                                                            current_response = " ".join(accumulated_response)
                                                            logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                                            yield f"data: {current_response}\n\n"
                                                    elif block_type == "text" and "text" in block:
                                                        # Explicit text block
                                                        text_content = block["text"]
                                                        accumulated_response.append(text_content)
                                                        # Yield the accumulated response
                                                        current_response = " ".join(accumulated_response)
                                                        logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                                        yield f"data: {current_response}\n\n"
                                                    elif block_type == "tool_use":
                                                        # Tool use block
                                                        tool_name = block.get("name", "unknown")
                                                        tool_input = block.get("input", {})
                                                        tool_text = f"[Using tool: {tool_name} with input: {tool_input}]"
                                                        accumulated_response.append(tool_text)
                                                        # Yield the accumulated response
                                                        current_response = " ".join(accumulated_response)
                                                        logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                                        yield f"data: {current_response}\n\n"
                                                    elif block_type == "tool_result":
                                                        ## passing as tool result yield everytign which we don't need
                                                        pass
                                                        # # Tool result block
                                                        # tool_result = block.get("content", "Tool completed")
                                                        # result_text = str(tool_result)
                                                        # accumulated_response.append(result_text)
                                                        # # Yield the accumulated response
                                                        # current_response = " ".join(accumulated_response)
                                                        # logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                                        # yield f"data: {current_response}\n\n"
                                                    elif block_type == "thinking":
                                                        # Thinking block
                                                        thinking = block.get("thinking", "")
                                                        thinking_text = f"[Thinking: {thinking}]"
                                                        accumulated_response.append(thinking_text)
                                                        # Yield the accumulated response
                                                        current_response = " ".join(accumulated_response)
                                                        logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                                        yield f"data: {current_response}\n\n"
                                                    else:
                                                        # Unknown block type, try to extract any text
                                                        logger.debug(f"[CLAUDE STREAM] Unknown block type: {block_type}, trying to extract text")
                                                        for key, value in block.items():
                                                            if key == "text" and isinstance(value, str):
                                                                accumulated_response.append(value)
                                                                # Yield the accumulated response
                                                                current_response = " ".join(accumulated_response)
                                                                logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                                                yield f"data: {current_response}\n\n"
                                        elif message_data.get("subtype") in ["success", "error"]:
                                            # This is a ResultMessage, contains final result
                                            result_text = message_data.get("result", "")
                                            if result_text:
                                                accumulated_response.append(result_text)
                                                # Yield the accumulated response
                                                current_response = " ".join(accumulated_response)
                                                logger.info(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                                yield f"data: {current_response}\n\n"
                                            logger.info(f"[CLAUDE STREAM] Final message received with subtype: {message_data["subtype"]} for chat {chat_uuid}")
                                            break
                                        elif "message" in message_data and isinstance(message_data["message"], str):
                                            # This might be a system or error message
                                            message_text = message_data["message"]
                                            accumulated_response.append(message_text)
                                            # Yield the accumulated response
                                            current_response = " ".join(accumulated_response)
                                            logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                            yield f"data: {current_response}\n\n"
                                        else:
                                            # Try to find text content in any field
                                            logger.debug(f"[CLAUDE STREAM] Unknown message type, searching for text content in: {message_data}")
                                            for key, value in message_data.items():
                                                if isinstance(value, str) and key in ["text", "content", "message", "result"]:
                                                    accumulated_response.append(value)
                                                    # Yield the accumulated response
                                                    current_response = " ".join(accumulated_response)
                                                    logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                                    yield f"data: {current_response}\n\n"
                                    else:
                                        # If it"s not a dict, just yield it as string
                                        message_str = str(message_data)
                                        accumulated_response.append(message_str)
                                        # Yield the accumulated response
                                        current_response = " ".join(accumulated_response)
                                        logger.debug(f"[CLAUDE STREAM] Yielding accumulated response: {repr(current_response)}")
                                        yield f"data: {current_response}\n\n"
                                except json.JSONDecodeError as e:
                                    # If not JSON, just yield the raw content
                                    logger.error(f"[CLAUDE STREAM] JSON decode error: {e}, raw content: {repr(data_content)}")
                                    if data_content.strip() != "":
                                        accumulated_response.append(data_content)
                                        # Yield the accumulated response
                                        current_response = " ".join(accumulated_response)
                                        yield f"data: {current_response}\n\n"
                        
                        # Check for connection issues
                        if not line_str:
                            logger.debug(f"[CLAUDE STREAM] Empty line received for chat {chat_uuid}, breaking")
                            break
                    logger.info(f"[CLAUDE STREAM] Finished reading Claude events stream for chat {chat_uuid}")
                    
        except Exception as e:
            logger.error(f"Error in Claude stream for chat {chat_uuid}: {e}")
            yield f"data: Error: {str(e)}\n\n"
        
        # Store the complete response
        complete_response = " ".join(accumulated_response) if accumulated_response else "No response from Claude"
        logger.info(f"[CLAUDE RESPONSE] Complete response for chat {chat_uuid}: {repr(complete_response[:100])}...")
        
        # Save assistant"s response to database
        db.add_message(chat_uuid, "assistant", complete_response.strip())
        logger.info(f"[CHAT {chat_uuid}] Claude response saved to database")

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.delete("/api/chat/{chat_uuid}")
async def delete_chat(chat_uuid: str):
    """
    Delete a chat session
    """
    try:
        chat = db.get_chat(chat_uuid)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        db.delete_chat(chat_uuid)
        return JSONResponse({"message": "Chat deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tool profile configurations
TOOL_PROFILES = {
    "default": {
        "allowed_tools": ["Read", "Write", "Edit", "Glob", "Grep"],
        "permission_mode": "default"
    },
    "readonly": {
        "allowed_tools": ["Read", "Glob", "Grep"],
        "permission_mode": "default"
    },
    "dev": {
        "allowed_tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits"
    },
    "ci": {
        "allowed_tools": ["Read", "Grep", "Glob"],
        "permission_mode": "plan"
    },
    "sandboxed": {
        "allowed_tools": ["Read", "Write", "Edit", "Bash"],
        "permission_mode": "default",
        "sandbox": {"enabled": True}
    }
}

@app.post("/sessions")
async def create_session(request: CreateSessionRequest) -> CreateSessionResponse:
    """
    Create a Claude session
    """
    try:
        # Validate request parameters
        if request.profile and request.profile not in TOOL_PROFILES:
            raise HTTPException(status_code=400, detail=f"Invalid profile: {request.profile}. Valid profiles: {list(TOOL_PROFILES.keys())}")

        # Get tool profile configuration
        profile_config = TOOL_PROFILES.get(request.profile, TOOL_PROFILES["default"])

        # Build options from request and profile
        options = ClaudeAgentOptions(
            # allowed_tools=request.allowed_tools or profile_config["allowed_tools"],
            # system_prompt=request.system_prompt,
            # permission_mode=request.permission_mode or profile_config["permission_mode"],
            permission_mode="bypassPermissions",
            model=request.model,
            cwd=request.cwd
        )

        # Add sandbox settings if needed
        if request.profile == "sandboxed" or profile_config.get("sandbox"):
            from claude_agent_sdk import SandboxSettings
            sandbox_settings: SandboxSettings = profile_config.get("sandbox", {"enabled": True})
            options.sandbox = sandbox_settings

        # Create ClaudeSDKClient
        client = ClaudeSDKClient(options)

        # Connect to Claude (with optional initial prompt)
        await client.connect()

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Store session data
        session_data = SessionData(
            client=client,
            options=options,
            created_at=datetime.now()
        )
        session_store[session_id] = session_data

        return CreateSessionResponse(
            session_id=session_id,
            model=request.model,
            created_at=session_data.created_at.isoformat(),
            status="ready"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.post("/sessions/{session_id}/query")
async def query_session(session_id: str, request: QueryRequest):
    """
    Send a user message to a Claude session
    """
    # Validate session ID format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Check if session exists
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = session_store[session_id]
    session_data.last_activity = datetime.now()

    try:
        # Validate prompt
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        # Send the query to Claude
        await session_data.client.query(request.prompt)

        # For now, return a 202 Accepted status
        # The actual response will be streamed via the events endpoint
        return {"status": "accepted", "session_id": session_id}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query session: {str(e)}")


@app.get("/sessions/{session_id}/events")
async def stream_session_events(session_id: str):
    """
    Stream Claude's response as Server-Sent Events (SSE)
    """
    # Validate session ID format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Check if session exists
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = session_store[session_id]
    session_data.last_activity = datetime.now()

    async def event_generator():
        try:
            # Receive messages from Claude
            async for message in session_data.client.receive_messages():
                # Convert message to JSON and send as SSE event
                import json

                def serialize_message(obj):
                    """Recursively serialize Claude SDK message objects to JSON-compatible format."""
                    if hasattr(obj, '__dict__'):
                        # Handle dataclass instances like AssistantMessage, TextBlock, etc.
                        result = {}
                        for key, value in obj.__dict__.items():
                            result[key] = serialize_message(value)
                        return result
                    elif hasattr(obj, '__dataclass_fields__'):
                        # For dataclass instances
                        result = {}
                        for field in obj.__dataclass_fields__:
                            result[field] = serialize_message(getattr(obj, field))
                        return result
                    elif isinstance(obj, list):
                        # Handle lists of objects
                        return [serialize_message(item) for item in obj]
                    elif isinstance(obj, dict):
                        # Handle dictionaries
                        return {key: serialize_message(value) for key, value in obj.items()}
                    else:
                        # For primitive types or string representations
                        return obj if obj is None or isinstance(obj, (str, int, float, bool)) else str(obj)

                message_dict = serialize_message(message)

                # Send the message as an SSE event
                yield f"data: {json.dumps(message_dict)}\n\n"

                # Check if this is a final ResultMessage
                if hasattr(message, 'subtype') and message.subtype in ['success', 'error']:
                    break
        except asyncio.CancelledError:
            # Client disconnected
            pass
        except Exception as e:
            # Send error message
            import json
            error_msg = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_msg)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/sessions/{session_id}/interrupt")
async def interrupt_session(session_id: str, request: InterruptRequest):
    """
    Stop current agent run in a Claude session
    """
    # Validate session ID format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Check if session exists
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = session_store[session_id]
    session_data.last_activity = datetime.now()

    try:
        # Call Claude's interrupt method
        await session_data.client.interrupt()

        return {"status": "interrupted", "session_id": session_id}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to interrupt session: {str(e)}")


@app.post("/sessions/{session_id}/reset")
async def reset_session(session_id: str, request: ResetRequest):
    """
    Reset conversation in a Claude session
    """
    # Validate session ID format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Check if session exists
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = session_store[session_id]
    session_data.last_activity = datetime.now()

    try:
        if request.hard_reset:
            # Hard reset: destroy and recreate the client
            try:
                await session_data.client.disconnect()
            except:
                # If disconnect fails, continue anyway
                pass

            # Recreate the client with the same options
            new_client = ClaudeSDKClient(session_data.options)
            await new_client.connect()

            # Update the client in the session data
            session_data.client = new_client
        else:
            # Soft reset: disconnect and reconnect
            try:
                await session_data.client.disconnect()
            except:
                # If disconnect fails, continue anyway
                pass
            await session_data.client.connect()

        return {"status": "reset", "session_id": session_id, "reset_type": "hard" if request.hard_reset else "soft"}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset session: {str(e)}")


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Destroy a Claude session
    """
    # Validate session ID format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Check if session exists
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = session_store[session_id]

    try:
        # Disconnect the Claude client
        try:
            await session_data.client.disconnect()
        except:
            # If disconnect fails, continue anyway
            pass

        # Remove session from store
        del session_store[session_id]

        return {"status": "deleted", "session_id": session_id}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get session information
    """
    # Validate session ID format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    # Check if session exists
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = session_store[session_id]

    return {
        "session_id": session_id,
        "status": session_data.status,
        "created_at": session_data.created_at.isoformat(),
        "last_activity": session_data.last_activity.isoformat(),
        "model": session_data.options.model,
        "allowed_tools": session_data.options.allowed_tools,
        "permission_mode": session_data.options.permission_mode
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
