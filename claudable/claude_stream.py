

from typing import Iterator, Dict, Any

def claude(prompt: str,claude_session_id=None) -> Iterator[Dict[str, Any]]:
    """
    Mock response with the same formatting.
    Yields entries from the predefined `data` list.
    """
    
    data =[
  {
    "type": "system",
    "subtype": "init",
    "cwd": "/home/ntlpt24",
    "session_id": "204c87e3-5bc4-46cf-afa8-8bd0e613b9f1",
    "tools": [
      "Task",
      "TaskOutput",
      "Bash",
      "Glob",
      "Grep",
      "ExitPlanMode",
      "Read",
      "Edit",
      "Write",
      "NotebookEdit",
      "WebFetch",
      "TodoWrite",
      "WebSearch",
      "KillShell",
      "AskUserQuestion",
      "Skill",
      "EnterPlanMode",
      "mcp__MultiRead__multi_read",
      "ListMcpResourcesTool",
      "ReadMcpResourceTool",
      "mcp__MultiGrep__multigrep",
      "mcp__MultiEdit__replace_str_in_file",
      "mcp__qwen-parallel-agents__run_multiple_qwen_agents_in_parallel",
      "mcp__qwen-agent__task_subagent"
    ],
    "mcp_servers": [
      {
        "name": "MultiRead",
        "status": "connected"
      },
      {
        "name": "MultiGrep",
        "status": "connected"
      },
      {
        "name": "MultiEdit",
        "status": "connected"
      },
      {
        "name": "chrome-mcp-server",
        "status": "failed"
      },
      {
        "name": "qwen-parallel-agents",
        "status": "connected"
      },
      {
        "name": "qwen-agent",
        "status": "connected"
      }
    ],
    "model": "claude-sonnet-4-5-20250929",
    "permissionMode": "bypassPermissions",
    "slash_commands": [
      "haiku",
      "opus",
      "sonnet",
      "compact",
      "context",
      "cost",
      "init",
      "pr-comments",
      "release-notes",
      "review",
      "security-review"
    ],
    "apiKeySource": "none",
    "claude_code_version": "2.0.75",
    "output_style": "default",
    "agents": [
      "general-purpose",
      "statusline-setup",
      "Explore",
      "Plan"
    ],
    "skills": [],
    "plugins": [],
    "uuid": "5a32875d-93b7-4c17-8b58-32a9a2f4db55"
  },
  {
    "type": "assistant",
    "message": {
      "model": "claude-sonnet-4-5-20250929",
      "id": "msg_014SHcZF2SMLHdxDik4Wkkx4",
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "I'll help you read the file and then run the sleep command."
        }
      ],
      "stop_reason": "",
      "stop_sequence": "",
      "usage": {
        "input_tokens": 2,
        "cache_creation_input_tokens": 7447,
        "cache_read_input_tokens": 12673,
        "cache_creation": {
          "ephemeral_5m_input_tokens": 7447,
          "ephemeral_1h_input_tokens": 0
        },
        "output_tokens": 8,
        "service_tier": "standard"
      },
      "context_management": ""
    },
    "parent_tool_use_id": "",
    "session_id": "204c87e3-5bc4-46cf-afa8-8bd0e613b9f1",
    "uuid": "2b0c752a-5bde-42de-9193-c122f6a955bd"
  },
  {
    "type": "assistant",
    "message": {
      "model": "claude-sonnet-4-5-20250929",
      "id": "msg_014SHcZF2SMLHdxDik4Wkkx4",
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "tool_use",
          "id": "toolu_01WK2z4UPH4GUY77DhWPkeK2",
          "name": "Read",
          "input": {
            "file_path": "/home/ntlpt24/Documents/dummy.txt"
          }
        }
      ],
      "stop_reason": "",
      "stop_sequence": "",
      "usage": {
        "input_tokens": 2,
        "cache_creation_input_tokens": 7447,
        "cache_read_input_tokens": 12673,
        "cache_creation": {
          "ephemeral_5m_input_tokens": 7447,
          "ephemeral_1h_input_tokens": 0
        },
        "output_tokens": 8,
        "service_tier": "standard"
      },
      "context_management": ""
    },
    "parent_tool_use_id": "",
    "session_id": "204c87e3-5bc4-46cf-afa8-8bd0e613b9f1",
    "uuid": "25c4d389-c0cf-450d-89a9-21c906d51c6e"
  },
  {
    "type": "assistant",
    "message": {
      "model": "claude-sonnet-4-5-20250929",
      "id": "msg_014SHcZF2SMLHdxDik4Wkkx4",
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "tool_use",
          "id": "toolu_0167wXcM6uvJwGZrcAt64bc6",
          "name": "Bash",
          "input": {
            "command": "sleep 2",
            "description": "Sleep for 2 seconds"
          }
        }
      ],
      "stop_reason": "tool_use",
      "stop_sequence": "",
      "usage": {
        "input_tokens": 2,
        "cache_creation_input_tokens": 7447,
        "cache_read_input_tokens": 12673,
        "cache_creation": {
          "ephemeral_5m_input_tokens": 7447,
          "ephemeral_1h_input_tokens": 0
        },
        "output_tokens": 139,
        "service_tier": "standard"
      },
      "context_management": ""
    },
    "parent_tool_use_id": "",
    "session_id": "204c87e3-5bc4-46cf-afa8-8bd0e613b9f1",
    "uuid": "99e7bc44-24bf-4897-b2ed-1cf61e4ecc53"
  },
  {
    "type": "user",
    "message": {
      "role": "user",
      "content": [
        {
          "tool_use_id": "toolu_01WK2z4UPH4GUY77DhWPkeK2",
          "type": "tool_result",
          "content": "     1→hi, just dummy file here\n     2→\n\n<system-reminder>\nWhenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.\n</system-reminder>\n"
        }
      ]
    },
    "parent_tool_use_id": "",
    "session_id": "204c87e3-5bc4-46cf-afa8-8bd0e613b9f1",
    "uuid": "83a34380-4681-4fbf-9096-c97403b98d56",
    "tool_use_result": {
      "type": "text",
      "file": {
        "filePath": "/home/ntlpt24/Documents/dummy.txt",
        "content": "hi, just dummy file here\n",
        "numLines": 2,
        "startLine": 1,
        "totalLines": 2
      }
    }
  },
  {
    "type": "user",
    "message": {
      "role": "user",
      "content": [
        {
          "tool_use_id": "toolu_0167wXcM6uvJwGZrcAt64bc6",
          "type": "tool_result",
          "content": "",
          "is_error": False
        }
      ]
    },
    "parent_tool_use_id": "",
    "session_id": "204c87e3-5bc4-46cf-afa8-8bd0e613b9f1",
    "uuid": "e41adb82-23b6-4544-a66c-bba07a433b46",
    "tool_use_result": {
      "stdout": "",
      "stderr": "",
      "interrupted": False,
      "isImage": False
    }
  },
  {
    "type": "assistant",
    "message": {
      "model": "claude-sonnet-4-5-20250929",
      "id": "msg_011EJzdjqgWX2r9VXxDYRwsP",
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "Task done!\n\nThe file `/home/ntlpt24/Documents/dummy.txt` contains:\n```\nhi, just dummy file here\n```\n\nAnd I've completed the 2-second sleep as requested."
        }
      ],
      "stop_reason": "",
      "stop_sequence": "",
      "usage": {
        "input_tokens": 6,
        "cache_creation_input_tokens": 294,
        "cache_read_input_tokens": 20120,
        "cache_creation": {
          "ephemeral_5m_input_tokens": 294,
          "ephemeral_1h_input_tokens": 0
        },
        "output_tokens": 1,
        "service_tier": "standard"
      },
      "context_management": ""
    },
    "parent_tool_use_id": "",
    "session_id": "204c87e3-5bc4-46cf-afa8-8bd0e613b9f1",
    "uuid": "e57be79d-517c-4dd2-a332-97c9d4e1d7f9"
  },
  {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "duration_ms": 21308,
    "duration_api_ms": 35881,
    "num_turns": 3,
    "result": "Task done!\n\nThe file `/home/ntlpt24/Documents/dummy.txt` contains:\n```\nhi, just dummy file here\n```\n\nAnd I've completed the 2-second sleep as requested.",
    "session_id": "204c87e3-5bc4-46cf-afa8-8bd0e613b9f1",
    "total_cost_usd": 0.047063749999999994,
    "usage": {
      "input_tokens": 8,
      "cache_creation_input_tokens": 7741,
      "cache_read_input_tokens": 32793,
      "output_tokens": 189,
      "server_tool_use": {
        "web_search_requests": 0,
        "web_fetch_requests": 0
      },
      "service_tier": "standard",
      "cache_creation": {
        "ephemeral_1h_input_tokens": 0,
        "ephemeral_5m_input_tokens": 7741
      }
    },
    "modelUsage": {
      "claude-haiku-4-5-20251001": {
        "inputTokens": 1240,
        "outputTokens": 200,
        "cacheReadInputTokens": 0,
        "cacheCreationInputTokens": 0,
        "webSearchRequests": 0,
        "costUSD": 0.00224,
        "contextWindow": 200000
      },
      "claude-sonnet-4-5-20250929": {
        "inputTokens": 10,
        "outputTokens": 374,
        "cacheReadInputTokens": 33850,
        "cacheCreationInputTokens": 7741,
        "webSearchRequests": 0,
        "costUSD": 0.044823749999999996,
        "contextWindow": 200000
      }
    },
    "permission_denials": [],
    "uuid": "1f5f8e9c-d775-4849-99d1-0924740d3739"
  }
]


    for entry in data:
        yield entry




