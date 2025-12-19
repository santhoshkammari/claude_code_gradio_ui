"""
Agent Framework Usage Examples

Demonstrates the agent.py framework for streaming-based agent execution
with async tool calling and early execution optimization.
"""

import asyncio

from .agent import step, gen, AssistantResponse, ToolCall, agent
from .lm import LM


def get_weather(city: str, unit: str = "celsius"):
    """
    Get the current weather for a city

    Args:
        city: The name of the city
        unit: Temperature unit (choices: ["celsius", "fahrenheit"])
    """
    return f"Weather in {city}: 22 degrees {unit}"


def search(query: str) -> str:
    """
    Search for information

    Args:
        query: Search query
    """
    return f"Search results for '{query}': [mock results]"


async def demo_simple_loop():
    """Demo 1: Simple agent loop"""
    print("\n" + "="*60)
    print("DEMO 1: Simple Agent Loop")
    print("="*60)

    lm = LM()
    tools = [get_weather, search]

    history = [{"role": "user", "content": "What is the weather in London and Paris? /no_think"}]
    result = await agent(
        lm=lm,
        history=history,
        tools=tools,
        max_iterations=5
    )

    print(f"Iterations: {result['iterations']}")
    print(f"Total tool calls: {result['tool_calls_total']}")
    print(f"\nFinal Response: {result['final_response'][:200]}...")

    print(f"\nConversation History ({len(result['history'])} messages):")
    for i, msg in enumerate(result['history']):
        role = msg.get("role", "unknown")
        if role == "assistant":
            content = msg.get("content", "")[:50] if msg.get("content") else "[no content]"
            print(f"  {i}: {role:10} → {content}...")
        elif role == "tool":
            content = msg.get("content", "")[:50]
            print(f"  {i}: {role:10} → {content}...")
        else:
            content = msg.get("content", "")[:50]
            print(f"  {i}: {role:10} → {content}...")


async def example_multi_turn_agent_loop():
    """
    Example 1: Multi-turn agent loop with early tool execution (default)

    Demonstrates:
    - Single step() calls for LLM generation
    - Async tool execution and waiting for results
    - Multi-turn conversation handling
    - Early tool execution optimization (enabled by default)
    """
    lm = LM()
    history = [
        {"role": "user", "content": "what is weather in london and canada?, do two parallel tool calls to get the weather in both cities /no_think"}
    ]
    tools = [get_weather]

    print("=== Multi-turn Agent Loop Demo (Early Tool Execution Enabled) ===\n")

    iteration = 0
    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # Single LLM generation with async tool execution
        result = await step(lm=lm, history=history, tools=tools, early_tool_execution=True)

        print(f"Assistant message: {result.message}")
        print(f"Tool calls: {len(result.tool_calls)}")

        # Wait for tool execution (tools running in parallel)
        tool_results = await result.tool_results()

        # Add to history
        history.append(result.message)
        for tr in tool_results:
            print(f"Tool result: {tr}")
            history.append(tr.message)

        # Stop if no more tool calls
        if not result.tool_calls:
            print(f"\nFinal response: {result.message.get('content', '')}")
            break

        if iteration > 10:
            print("\nMax iterations reached!")
            break

    print("\n=== Conversation History ===")
    for i, msg in enumerate(history):
        print(f"{i}: {msg}")


async def example_streaming_gen():
    """
    Example 3: Low-level streaming generation

    Demonstrates:
    - Direct use of gen() function for streaming LLM responses
    - Receiving raw AssistantResponse and ToolCall chunks
    - Manual handling of streaming chunks
    """
    lm = LM()
    messages = [{"role": "user", "content": "what is weather in london and canada?, do two parallel tool calls to get the weather in both cities /no_think"}]
    tools = [get_weather]

    print("\n\n=== Low-level Streaming Demo ===\n")

    async for chunk in gen(lm=lm, history=messages, tools=tools):
        if isinstance(chunk, AssistantResponse):
            print(f"[Text] {chunk.content}", end="", flush=True)
        elif isinstance(chunk, ToolCall):
            print(f"\n[Tool] {chunk.name} called with ID {chunk.id}")
            print(f"       Args: {chunk.arguments}")


async def main():
    """Run all examples"""
    # Demo 1: Simple agent loop
    await demo_simple_loop()

    # Example 1: Multi-turn with early execution (recommended)
    await example_multi_turn_agent_loop()

    # Example 3: Low-level streaming
    await example_streaming_gen()


if __name__ == "__main__":
    asyncio.run(main())
