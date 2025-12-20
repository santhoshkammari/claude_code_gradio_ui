import asyncio
import aiohttp
import json
from typing import Optional

class LM:
    def __init__(
        self,
        model: str = "",
        api_base: str = "http://localhost:8000",
        api_key: str = "-",
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ):
        self.provider, self.model = model.split(":", 1) if ":" in model else ("vllm", "")
        self.api_base = api_base
        self.api_key = api_key

        self._session: Optional[aiohttp.ClientSession] = None

        # Default timeout suitable for streaming
        self._timeout = timeout or aiohttp.ClientTimeout(
            total=None,     # streaming: no global timeout
            connect=10,     # fail fast on connection issues
            sock_read=None  # allow long token streams
        )

    # ---------- lifecycle ----------

    async def start(self):
        """Initialize shared HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)

    async def close(self):
        """Close shared HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def _require_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError("LM session not started. Call `await lm.start()` first.")
        return self._session

    # ---------- streaming ----------

    async def stream(self, messages, tools=None, **params):
        """Streaming interface for LLM."""

        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        session = self._require_session()

        body = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            **params,
        }

        if tools:
            body["tools"] = tools

        try:
            async with session.post(
                f"{self.api_base}/v1/chat/completions",
                json=body,
            ) as resp:
                resp.raise_for_status()

                async for line in resp.content:
                    line = line.decode().strip()

                    if not line or line == "data: [DONE]":
                        continue

                    if line.startswith("data: "):
                        yield json.loads(line[6:])

        except asyncio.CancelledError:
            # Client disconnected / request cancelled
            raise

    # ---------- batch ----------

    async def batch(self, messages_batch, **params):
        """Handle batch of conversations asynchronously."""
        session = self._require_session()

        async def _single(messages):
            if isinstance(messages, str):
                messages = [{"role": "user", "content": messages}]

            body = {
                "model": self.model,
                "messages": messages,
                **params,
            }

            async with session.post(
                f"{self.api_base}/v1/chat/completions",
                json=body,
            ) as resp:
                data = await resp.json()
                if resp.status >= 400:
                    raise RuntimeError(f"LLM error: {data}")
                return data

        tasks = [_single(msgs) for msgs in messages_batch]
        return await asyncio.gather(*tasks, return_exceptions=True)



"""
{
  "messages": [
    {
      "content": "string",
      "role": "developer",
      "name": "string"
    },
    {
      "content": "string",
      "role": "system",
      "name": "string"
    },
    {
      "content": "string",
      "role": "user",
      "name": "string"
    },
    {
      "role": "assistant",
      "audio": {
        "id": "string"
      },
      "content": "string",
      "function_call": {
        "arguments": "string",
        "name": "string"
      },
      "name": "string",
      "refusal": "string",
      "tool_calls": [
        {
          "id": "string",
          "function": {
            "arguments": "string",
            "name": "string"
          },
          "type": "function"
        },
        {
          "id": "string",
          "custom": {
            "input": "string",
            "name": "string"
          },
          "type": "custom"
        }
      ]
    },
    {
      "content": "string",
      "role": "tool",
      "tool_call_id": "string"
    },
    {
      "content": "string",
      "name": "string",
      "role": "function"
    },
    {
      "role": "string",
      "content": "string",
      "name": "string",
      "tool_call_id": "string",
      "tool_calls": [
        {
          "id": "string",
          "function": {
            "arguments": "string",
            "name": "string"
          },
          "type": "function"
        }
      ]
    },
    {
      "author": {
        "role": "user",
        "name": "string"
      },
      "content": [
        {}
      ],
      "channel": "string",
      "recipient": "string",
      "content_type": "string"
    }
  ],
  "model": "string",
  "frequency_penalty": 0,
  "logit_bias": {
    "additionalProp1": 0,
    "additionalProp2": 0,
    "additionalProp3": 0
  },
  "logprobs": false,
  "top_logprobs": 0,
  "max_completion_tokens": 0,
  "n": 1,
  "presence_penalty": 0,
  "response_format": {
    "type": "text",
    "json_schema": {
      "name": "string",
      "description": "string",
      "schema": {
        "additionalProp1": {}
      },
      "strict": true,
      "additionalProp1": {}
    },
    "additionalProp1": {}
  },
  "seed": -9223372036854776000,
  "stop": [],
  "stream": false,
  "stream_options": {
    "include_usage": true,
    "continuous_usage_stats": false,
    "additionalProp1": {}
  },
  "temperature": 0,
  "top_p": 0,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "string",
        "description": "string",
        "parameters": {
          "additionalProp1": {}
        },
        "additionalProp1": {}
      },
      "additionalProp1": {}
    }
  ],
  "tool_choice": "none",
  "reasoning_effort": "low",
  "include_reasoning": true,
  "parallel_tool_calls": false,
  "user": "string",
  "best_of": 0,
  "use_beam_search": false,
  "top_k": 0,
  "min_p": 0,
  "repetition_penalty": 0,
  "length_penalty": 1,
  "stop_token_ids": [],
  "include_stop_str_in_output": false,
  "ignore_eos": false,
  "min_tokens": 0,
  "skip_special_tokens": true,
  "spaces_between_special_tokens": true,
  "truncate_prompt_tokens": -1,
  "prompt_logprobs": 0,
  "allowed_token_ids": [
    0
  ],
  "bad_words": [
    "string"
  ],
  "echo": false,
  "add_generation_prompt": true,
  "continue_final_message": false,
  "add_special_tokens": false,
  "documents": [
    {
      "additionalProp1": "string",
      "additionalProp2": "string",
      "additionalProp3": "string"
    }
  ],
  "chat_template": "string",
  "chat_template_kwargs": {
    "additionalProp1": {}
  },
  "mm_processor_kwargs": {
    "additionalProp1": {}
  },
  "guided_json": "string",
  "guided_regex": "string",
  "guided_choice": [
    "string"
  ],
  "guided_grammar": "string",
  "structural_tag": "string",
  "guided_decoding_backend": "string",
  "guided_whitespace_pattern": "string",
  "priority": 0,
  "request_id": "string",
  "logits_processors": [
    "string",
    {
      "qualname": "string",
      "args": [
        "string"
      ],
      "kwargs": {
        "additionalProp1": {}
      }
    }
  ],
  "return_tokens_as_token_ids": true,
  "return_token_ids": true,
  "cache_salt": "string",
  "kv_transfer_params": {
    "additionalProp1": {}
  },
  "vllm_xargs": {
    "additionalProp1": "string",
    "additionalProp2": "string",
    "additionalProp3": "string"
  },
  "additionalProp1": {}
}
"""