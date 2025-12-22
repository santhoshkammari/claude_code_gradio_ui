(ntlpt24) ntlpt24@NTLPT24:~/code/claude_code_gradio_ui/claudable$ python api.py 
/home/ntlpt24/.venv/lib/python3.13/site-packages/websockets/legacy/__init__.py:6: DeprecationWarning: websockets.legacy is deprecated; see https://websockets.readthedocs.io/en/stable/howto/upgrade.html for upgrade instructions
  warnings.warn(  # deprecated in 14.0 - 2024-11-09
/home/ntlpt24/.venv/lib/python3.13/site-packages/uvicorn/protocols/websockets/websockets_impl.py:17: DeprecationWarning: websockets.server.WebSocketServerProtocol is deprecated
  from websockets.server import WebSocketServerProtocol
INFO:     Started server process [332788]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:35964 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:48852 - "POST /api/chat/create HTTP/1.1" 200 OK
INFO:     127.0.0.1:48852 - "GET /chat/98fc9a54-d63a-4c20-9b92-5c558f3ba968 HTTP/1.1" 200 OK
INFO:     127.0.0.1:48852 - "GET /api/chat/98fc9a54-d63a-4c20-9b92-5c558f3ba968/messages HTTP/1.1" 200 OK
INFO:     127.0.0.1:48856 - "GET /api/chats HTTP/1.1" 200 OK
[CHAT 98fc9a54-d63a-4c20-9b92-5c558f3ba968] Added user message: hi, run bash sleep for 2 second and then say hi
[CHAT 98fc9a54-d63a-4c20-9b92-5c558f3ba968] Mode: code, Model: sonnet
2025-12-23 04:51:57,865 - INFO - Using bundled Claude Code CLI: /home/ntlpt24/.venv/lib/python3.13/site-packages/claude_agent_sdk/_bundled/claude
INFO:     127.0.0.1:48868 - "POST /sessions HTTP/1.1" 200 OK
INFO:     127.0.0.1:48856 - "POST /api/chat/98fc9a54-d63a-4c20-9b92-5c558f3ba968/message HTTP/1.1" 200 OK
2025-12-23 04:52:14,363 - INFO - [CLAUDE REQUEST] Sending query to Claude session 338b76a4-6078-4116-bf80-02e19ac77178 for chat 98fc9a54-d63a-4c20-9b92-5c558f3ba968
2025-12-23 04:52:14,363 - INFO - [CLAUDE REQUEST] Input prompt: hi, run bash sleep for 2 second and then say hi
INFO:     127.0.0.1:43712 - "POST /sessions/338b76a4-6078-4116-bf80-02e19ac77178/query HTTP/1.1" 200 OK
2025-12-23 04:52:14,365 - INFO - Query sent successfully to Claude session 338b76a4-6078-4116-bf80-02e19ac77178
2025-12-23 04:52:14,365 - INFO - [CLAUDE STREAM] Starting to stream response from session 338b76a4-6078-4116-bf80-02e19ac77178
INFO:     127.0.0.1:43724 - "GET /sessions/338b76a4-6078-4116-bf80-02e19ac77178/events HTTP/1.1" 200 OK
2025-12-23 04:52:14,368 - INFO - [CLAUDE STREAM] Starting to read Claude events stream for chat 98fc9a54-d63a-4c20-9b92-5c558f3ba968...
----------
message=SystemMessage(subtype='init', data={'type': 'system', 'subtype': 'init', 'cwd': '/home/ntlpt24/code/claude_code_gradio_ui/claudable', 'session_id': '268bfcb5-4366-4d54-b818-7df70466d50b', 'tools': ['Task', 'Bash', 'Glob', 'Grep', 'ExitPlanMode', 'Read', 'Edit', 'Write', 'NotebookEdit', 'WebFetch', 'TodoWrite', 'WebSearch', 'BashOutput', 'KillShell', 'Skill', 'SlashCommand', 'EnterPlanMode'], 'mcp_servers': [], 'model': 'claude-sonnet-4-5-20250929', 'permissionMode': 'bypassPermissions', 'slash_commands': ['compact', 'context', 'cost', 'init', 'pr-comments', 'release-notes', 'todos', 'review', 'security-review'], 'apiKeySource': 'none', 'claude_code_version': '2.0.53', 'output_style': 'default', 'agents': ['general-purpose', 'statusline-setup', 'Explore', 'Plan'], 'skills': [], 'plugins': [], 'uuid': 'a23f6934-523a-4bce-84c0-712f9b8df3b7'})
----------
@@@@@@
data: {"subtype": "init", "data": {"type": "system", "subtype": "init", "cwd": "/home/ntlpt24/code/claude_code_gradio_ui/claudable", "session_id": "268bfcb5-4366-4d54-b818-7df70466d50b", "tools": ["Task", "Bash", "Glob", "Grep", "ExitPlanMode", "Read", "Edit", "Write", "NotebookEdit", "WebFetch", "TodoWrite", "WebSearch", "BashOutput", "KillShell", "Skill", "SlashCommand", "EnterPlanMode"], "mcp_servers": [], "model": "claude-sonnet-4-5-20250929", "permissionMode": "bypassPermissions", "slash_commands": ["compact", "context", "cost", "init", "pr-comments", "release-notes", "todos", "review", "security-review"], "apiKeySource": "none", "claude_code_version": "2.0.53", "output_style": "default", "agents": ["general-purpose", "statusline-setup", "Explore", "Plan"], "skills": [], "plugins": [], "uuid": "a23f6934-523a-4bce-84c0-712f9b8df3b7"}}

@@@@@@
@@@@@@


@@@@@@
----------
message=AssistantMessage(content=[TextBlock(text='I\'ll run a bash command to sleep for 2 seconds and then display "hi".')], model='claude-sonnet-4-5-20250929', parent_tool_use_id=None, error=None)
----------
@@@@@@
data: {"content": [{"text": "I'll run a bash command to sleep for 2 seconds and then display \"hi\"."}], "model": "claude-sonnet-4-5-20250929", "parent_tool_use_id": null, "error": null}

@@@@@@
@@@@@@


@@@@@@
----------
message=AssistantMessage(content=[ToolUseBlock(id='toolu_01KdPTYMqrZWwTwaUEd9vnD8', name='Bash', input={'command': 'sleep 2 && echo "hi"', 'description': 'Sleep for 2 seconds then echo hi'})], model='claude-sonnet-4-5-20250929', parent_tool_use_id=None, error=None)
----------
@@@@@@
data: {"content": [{"id": "toolu_01KdPTYMqrZWwTwaUEd9vnD8", "name": "Bash", "input": {"command": "sleep 2 && echo \"hi\"", "description": "Sleep for 2 seconds then echo hi"}}], "model": "claude-sonnet-4-5-20250929", "parent_tool_use_id": null, "error": null}

@@@@@@
@@@@@@


@@@@@@
----------
message=UserMessage(content=[ToolResultBlock(tool_use_id='toolu_01KdPTYMqrZWwTwaUEd9vnD8', content='hi', is_error=False)], parent_tool_use_id=None)
----------
@@@@@@
data: {"content": [{"tool_use_id": "toolu_01KdPTYMqrZWwTwaUEd9vnD8", "content": "hi", "is_error": false}], "parent_tool_use_id": null}

@@@@@@
@@@@@@


@@@@@@
----------
message=AssistantMessage(content=[TextBlock(text='Done! The command slept for 2 seconds and then printed "hi". 👋')], model='claude-sonnet-4-5-20250929', parent_tool_use_id=None, error=None)
----------
@@@@@@
data: {"content": [{"text": "Done! The command slept for 2 seconds and then printed \"hi\". \ud83d\udc4b"}], "model": "claude-sonnet-4-5-20250929", "parent_tool_use_id": null, "error": null}

@@@@@@
@@@@@@


@@@@@@
----------
message=ResultMessage(subtype='success', duration_ms=13679, duration_api_ms=17405, is_error=False, num_turns=2, session_id='268bfcb5-4366-4d54-b818-7df70466d50b', total_cost_usd=0.013975349999999997, usage={'input_tokens': 9, 'cache_creation_input_tokens': 449, 'cache_read_input_tokens': 27442, 'output_tokens': 128, 'server_tool_use': {'web_search_requests': 0, 'web_fetch_requests': 0}, 'service_tier': 'standard', 'cache_creation': {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 449}}, result='Done! The command slept for 2 seconds and then printed "hi". 👋', structured_output=None)
----------
@@@@@@
data: {"subtype": "success", "duration_ms": 13679, "duration_api_ms": 17405, "is_error": false, "num_turns": 2, "session_id": "268bfcb5-4366-4d54-b818-7df70466d50b", "total_cost_usd": 0.013975349999999997, "usage": {"input_tokens": 9, "cache_creation_input_tokens": 449, "cache_read_input_tokens": 27442, "output_tokens": 128, "server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0}, "service_tier": "standard", "cache_creation": {"ephemeral_1h_input_tokens": 0, "ephemeral_5m_input_tokens": 449}}, "result": "Done! The command slept for 2 seconds and then printed \"hi\". \ud83d\udc4b", "structured_output": null}

@@@@@@
2025-12-23 04:52:28,048 - INFO - [CLAUDE STREAM] Yielding accumulated response: 'I\'ll run a bash command to sleep for 2 seconds and then display "hi". Done! The command slept for 2 seconds and then printed "hi". 👋 Done! The command slept for 2 seconds and then printed "hi". 👋'
2025-12-23 04:52:28,048 - INFO - [CLAUDE STREAM] Final message received with subtype: success for chat 98fc9a54-d63a-4c20-9b92-5c558f3ba968
2025-12-23 04:52:28,048 - INFO - [CLAUDE STREAM] Finished reading Claude events stream for chat 98fc9a54-d63a-4c20-9b92-5c558f3ba968
2025-12-23 04:52:28,049 - INFO - [CLAUDE RESPONSE] Complete response for chat 98fc9a54-d63a-4c20-9b92-5c558f3ba968: 'I\'ll run a bash command to sleep for 2 seconds and then display "hi". Done! The command slept for 2 '...
2025-12-23 04:52:28,090 - INFO - [CHAT 98fc9a54-d63a-4c20-9b92-5c558f3ba968] Claude response saved to database



