import json
import asyncio

from dataclasses import dataclass
from typing import Callable
from transformers.utils import get_json_schema

from .lm import LM

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
    """Result from one LLM generation with async tool execution"""
    message: dict                           # The assistant's message
    tool_calls: list[dict]                  # Tool calls made
    usage: dict | None                      # Token usage if available
    _tool_futures: dict[str, asyncio.Future]  # Futures for tool results

    async def tool_results(self) -> list["ToolResult"]:
        """Wait for and return all tool execution results"""
        if not self._tool_futures:
            return []

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


async def step(
    lm,
    history: list[dict],
    tools: list[Callable] = None,
    early_tool_execution: bool = True,
    logger=None,
) -> StepResult:
    """
    Execute ONE LLM generation with async tool execution.

    This function:
    1. Calls gen() once to get LLM response
    2. Spawns async tasks for tool calls (runs in parallel)
    3. Returns immediately with StepResult (tools still running)
    4. Call await result.tool_results() to get tool outputs

    Args:
        lm: Language model instance
        history: Conversation history
        tools: List of callable tools (functions with docstrings)
        early_tool_execution: If True, execute tools as soon as they are complete
                             while LLM is still streaming. If False, execute all
                             tools only after LLM finishes streaming.

    Returns:
        StepResult with message and tool futures
    """
    tools = tools or []

    # Build tool registry and schemas
    tool_registry = {tool.__name__: tool for tool in tools}
    tool_schemas = [get_json_schema(t) if callable(t) else t for t in tools]

    # Accumulate the assistant message
    assistant_message = {
        "role": "assistant",
        "content": "",
        "tool_calls": []
    }

    tool_call_buffer = {}  # id -> partial tool call data
    tool_futures = {}      # id -> future (for early execution)
    last_tool_id = None    # Track the last tool call being streamed

    # Stream LLM response
    async for chunk in gen(lm=lm, history=history, tools=tool_schemas):
        if isinstance(chunk, AssistantResponse):
            # Text content
            assistant_message["content"] += chunk.content

        elif isinstance(chunk, ToolCall):
            # Tool call streaming
            if chunk.id and chunk.id not in tool_call_buffer:
                # New tool call starting
                # If early execution enabled and previous tool is complete, execute it
                if early_tool_execution and last_tool_id and last_tool_id in tool_call_buffer:
                    prev_tool_call = tool_call_buffer[last_tool_id]
                    tool_id = prev_tool_call["id"]
                    tool_name = prev_tool_call["function"]["name"]
                    tool_args_str = prev_tool_call["function"]["arguments"]

                    # Spawn previous tool immediately
                    future = asyncio.create_task(
                        _execute_tool(tool_name, tool_args_str, tool_id, tool_registry, logger)
                    )
                    tool_futures[tool_id] = future

                # Start new tool call
                tool_call_buffer[chunk.id] = {
                    "id": chunk.id,
                    "type": "function",
                    "function": {
                        "name": chunk.name,
                        "arguments": chunk.arguments or ""
                    }
                }
                last_tool_id = chunk.id
            else:
                # Continue accumulating arguments
                if chunk.id in tool_call_buffer:
                    tool_call_buffer[chunk.id]["function"]["arguments"] += chunk.arguments or ""

    # Finalize tool calls
    tool_calls = list(tool_call_buffer.values())

    # Clean up message
    if not assistant_message["content"]:
        del assistant_message["content"]

    if tool_calls:
        assistant_message["tool_calls"] = tool_calls

    # Execute remaining tools that haven't been spawned yet
    for tool_call in tool_calls:
        tool_id = tool_call["id"]

        # Skip if already spawned (early execution)
        if tool_id in tool_futures:
            continue


        tool_name = tool_call["function"]["name"]
        tool_args_str = tool_call["function"]["arguments"]

        # Create async task for this tool
        future = asyncio.create_task(
            _execute_tool(tool_name, tool_args_str, tool_id, tool_registry, logger)
        )
        tool_futures[tool_id] = future

    return StepResult(
        message=assistant_message,
        tool_calls=tool_calls,
        usage=None,
        _tool_futures=tool_futures
    )


async def agent(
    lm,
    history: list[dict],
    tools: list[Callable] = None,
    max_iterations: int = 10,
    early_tool_execution: bool = True,
    logger=None,
) -> dict:
    """
    Execute a multi-turn agent loop with max iterations.

    This function repeatedly calls step() until:
    - No more tool calls are made, OR
    - max_iterations is reached

    Args:
        lm: Language model instance
        history: Conversation history (list of messages)
        tools: List of callable tools (functions with docstrings)
        max_iterations: Maximum number of agent steps
        early_tool_execution: If True, execute tools while LLM is streaming

    Returns:
        {
            "history": list[dict],  # Full conversation history
            "iterations": int,      # Number of iterations executed
            "final_response": str,  # Last assistant message
            "tool_calls_total": int # Total tool calls made
        }
    """
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

        # Single LLM generation step
        result = await step(
            lm=lm,
            history=history,
            tools=tools,
            early_tool_execution=early_tool_execution,
            logger=logger
        )

        # Add assistant message to history
        history.append(result.message)

        # Log assistant message
        if logger and result.message.get("content"):
            logger.ai(result.message["content"], "assistant")

        # Count and execute tool calls
        if result.tool_calls:
            total_tool_calls += len(result.tool_calls)

            # Log tool calls
            if logger:
                for tc in result.tool_calls:
                    logger.ai(f"Tool: {tc['function']['name']}\nArgs: {tc['function']['arguments']}", "tool")

            # Wait for tool results
            tool_results = await result.tool_results()

            # Add tool results to history
            history.extend([tr.message for tr in tool_results])
        else:
            # No tool calls, agent is done
            break

    # Extract final response
    final_response = ""
    for msg in reversed(history):
        if msg.get("role") == "assistant" and msg.get("content"):
            final_response = msg["content"]
            break

    if logger:
        logger.info({"status": "completed", "iterations": iteration, "total_tool_calls": total_tool_calls})

    return {
        "history": history,
        "iterations": iteration,
        "final_response": final_response,
        "tool_calls_total": total_tool_calls
    }


