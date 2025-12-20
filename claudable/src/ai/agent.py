import json
import asyncio

from dataclasses import dataclass
from typing import Callable, Optional
import aiohttp
from transformers.utils import get_json_schema


@dataclass
class AssistantResponse:
    content:str

@dataclass
class ToolCall:
    id:str
    name:str
    arguments:str


@dataclass
class StepResult:
    """
    Result of a single LLM step.

    - Tool execution MAY have already started (early execution).
    - execute_tools() starts execution for remaining tools.
    - tool_results() ONLY awaits already-started tools.
    """
    message: dict
    tool_calls: list[dict]
    usage: dict | None

    _tool_registry: dict[str, Callable]
    _tool_futures: dict[str, asyncio.Future] = field(default_factory=dict)
    _executed: bool = False

    async def execute_tools(
        self,
        only: list[str] | None = None,
    ) -> list["ToolResult"]:
        """
        Start executing tools that have NOT been started yet.

        - only=None → execute all remaining tools
        - only=[...] → execute selected tools
        """
        if self._executed:
            raise RuntimeError("Tools already executed for this StepResult")

        for tc in self.tool_calls:
            tool_id = tc["id"]
            name = tc["function"]["name"]

            if only and name not in only:
                continue

            if tool_id in self._tool_futures:
                continue  # already running (early execution)

            fn = self._tool_registry.get(name)
            if not fn:
                self._tool_futures[tool_id] = asyncio.create_task(
                    asyncio.sleep(
                        0,
                        result=ToolResult(
                            tool_call_id=tool_id,
                            output=f"Tool '{name}' not found",
                            is_error=True,
                        ),
                    )
                )
                continue

            self._tool_futures[tool_id] = asyncio.create_task(
                _execute_tool(
                    tool_name=name,
                    tool_args_str=tc["function"]["arguments"],
                    tool_id=tool_id,
                    tool_registry=self._tool_registry,
                )
            )

        self._executed = True
        return await self.tool_results()

    async def tool_results(self) -> list["ToolResult"]:
        """
        Await results of tools that HAVE already been started.
        Does NOT start execution.
        """
        results = []


        for tool_call in self.tool_calls:
          future = self._tool_futures[tool_call["id"]]
          result = await future
          results.append(result)

        return results

@dataclass
class ToolResult:
    """Result from executing a single tool"""
    tool_call_id: str
    output: str
    is_error: bool = False

    @property
    def message(self) -> dict:
        """Convert to message format for history"""
        return {
            "role": "tool",
            "tool_call_id": self.tool_call_id,
            "content": self.output
        }

@dataclass
class AgentResult:
    history: list[dict]
    iterations: int
    final_response: str
    tool_calls_total: int

"""
LM Input paramas
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
    

async def gen(
    lm,
    history,
    tools=None
):
    tools = [get_json_schema(x) if callable(x) else x for x in tools] if tools else []
    tool_call_id = None
    tool_call_name = None

    async for x in lm.stream(messages=history,tools=tools):
        delta = x['choices'][0]['delta']
        if 'tool_calls' in delta:
            tool_call = delta['tool_calls'][0]
            if 'id' in tool_call:
                tool_call_id = tool_call['id']
                tool_call_name = tool_call['function']['name']
            yield ToolCall(id=tool_call_id,name=tool_call_name,arguments=tool_call['function'].get('arguments',""))
        elif 'content' in delta:
            yield AssistantResponse(content=delta['content'])
        else:
            raise ValueError("Unknown delta format")


async def _execute_tool(
    tool_name: str,
    tool_args_str: str,
    tool_id: str,
    tool_registry: dict,
    logger=None,
) -> ToolResult:
    """Execute a single tool asynchronously"""
    try:
        # Parse arguments
        tool_args = json.loads(tool_args_str) if tool_args_str else {}

        # Get tool function
        if tool_name not in tool_registry:
            result = ToolResult(
                tool_call_id=tool_id,
                output=f"Error: Tool '{tool_name}' not found",
                is_error=True
            )
            if logger:
                logger.error({"tool": tool_name, "error": "not found"})
        else:
            tool_fn = tool_registry[tool_name]

            # Call tool (sync or async)
            if asyncio.iscoroutinefunction(tool_fn):
                output = await tool_fn(**tool_args)
            else:
                output = tool_fn(**tool_args)

            result = ToolResult(
                tool_call_id=tool_id,
                output=str(output),
                is_error=False
            )

    except Exception as e:
        result = ToolResult(
            tool_call_id=tool_id,
            output=f"Error executing tool: {str(e)}",
            is_error=True
        )
        if logger:
            logger.error({"tool": tool_name, "error": str(e)})

    return result


from typing import AsyncGenerator, Union
async def step(
    lm,
    history: list[dict],
    tools: list[Callable] = None,
    early_tool_execution: bool = True,
    execute_tools: bool = True,
    logger=None,
):
    """
    Execute ONE LLM generation.

    Controls:
    - early_tool_execution → WHEN tools become eligible
    - execute_tools → WHETHER tools auto-execute

    Yields:
    - AssistantResponse
    - ToolCall
    - StepResult (final)
    """
    tools = tools or []

    tool_registry = {t.__name__: t for t in tools}
    tool_schemas = [get_json_schema(t) if callable(t) else t for t in tools]

    assistant_message = {
        "role": "assistant",
        "content": "",
        "tool_calls": [],
    }

    tool_call_buffer = {}   # id → tool_call dict
    tool_futures = {}       # id → asyncio.Future
    last_tool_id = None

    # ---- stream LLM output ----
    async for chunk in gen(lm=lm, history=history, tools=tool_schemas):

        if isinstance(chunk, AssistantResponse):
            assistant_message["content"] += chunk.content
            yield chunk

        elif isinstance(chunk, ToolCall):

            # new tool call starts
            if chunk.id and chunk.id not in tool_call_buffer:

                # early execution of previous tool (UNCHANGED logic)
                if (
                    early_tool_execution
                    and execute_tools
                    and last_tool_id
                    and last_tool_id in tool_call_buffer
                ):
                    prev = tool_call_buffer[last_tool_id]
                    tool_futures[prev["id"]] = asyncio.create_task(
                        _execute_tool(
                            tool_name=prev["function"]["name"],
                            tool_args_str=prev["function"]["arguments"],
                            tool_id=prev["id"],
                            tool_registry=tool_registry,
                            logger=logger,
                        )
                    )

                # start buffering new tool
                tool_call_buffer[chunk.id] = {
                    "id": chunk.id,
                    "type": "function",
                    "function": {
                        "name": chunk.name,
                        "arguments": chunk.arguments or "",
                    },
                }
                last_tool_id = chunk.id

            # continuation of arguments
            else:
                if chunk.id in tool_call_buffer:
                    tool_call_buffer[chunk.id]["function"]["arguments"] += (
                        chunk.arguments or ""
                    )

            yield chunk

        else:
            raise ValueError("Unknown streaming chunk type")

    # ---- finalize assistant message ----
    tool_calls = list(tool_call_buffer.values())

    if not assistant_message["content"]:
        assistant_message.pop("content", None)

    if tool_calls:
        assistant_message["tool_calls"] = tool_calls

    # ---- post-stream execution ----
    if execute_tools:
        for tc in tool_calls:
            if tc["id"] in tool_futures:
                continue

            tool_futures[tc["id"]] = asyncio.create_task(
                _execute_tool(
                    tool_name=tc["function"]["name"],
                    tool_args_str=tc["function"]["arguments"],
                    tool_id=tc["id"],
                    tool_registry=tool_registry,
                    logger=logger,
                )
            )

    # ---- final yield ----
    yield StepResult(
        message=assistant_message,
        tool_calls=tool_calls,
        usage=None,
        _tool_registry=tool_registry,
        _tool_futures=tool_futures,
    )

async def agent(
    lm,
    history: list[dict],
    tools: list[Callable] = None,
    max_iterations: int = 10,
    early_tool_execution: bool = True,
    logger=None,
) -> dict:
    tools = tools or []
    iteration = 0
    total_tool_calls = 0

    # Log user messages at start
    if logger:
        for msg in history:
            if msg.get("role") == "user":
                logger.ai(msg.get("content", ""), "user")

    while iteration < max_iterations:
        iteration += 1
        async for result in step(
            lm=lm,
            history=history,
            tools=tools,
            early_tool_execution=early_tool_execution,
            logger=logger
        ):
            yield result

        history.append(result.message)

        if logger and result.message.get("content"):
            logger.ai(result.message["content"], "assistant")

        if result.tool_calls:
            total_tool_calls += len(result.tool_calls)

            # Log tool calls
            if logger:
                for tc in result.tool_calls:
                    logger.ai(f"Tool: {tc['function']['name']}\nArgs: {tc['function']['arguments']}", "tool")

            tool_results = await result.tool_results()
            history.extend([tr.message for tr in tool_results])
        else:
            break

    final_response = history[-1].get("content", "")
    yield AgentResult(
        history=history,
        iterations=iteration,
        final_response=final_response,
        tool_calls_total=total_tool_calls
    )
