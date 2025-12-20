import asyncio

from .agent import step, gen, AssistantResponse, ToolCall, agent,LM


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
    print("DEMO 1: Simple Agent Loop")

    lm = LM(api_base="http://192.168.170.76:8000")
    await lm.start()
    tools = [get_weather, search]
    history = [{"role": "user", "content": "What is the weather in London and Paris? /no_think"}]
    async for chunk in  agent(lm=lm,history=history,tools=tools, max_iterations=5):
        print(chunk)

async def example_streaming_gen():
    lm = LM(api_base="http://192.168.170.76:8000")
    await lm.start()
    messages = [{"role": "user", "content": "what is weather in london and canada?, do two parallel tool calls to get the weather in both cities /no_think"}]
    tools = [get_weather]
    print("\n\n=== Low-level Streaming Demo ===\n")
    async for chunk in gen(lm=lm, history=messages, tools=tools):
        print(chunk)

async def example_streaming_step():
    lm = LM(api_base="http://192.168.170.76:8000")
    await lm.start()
    messages = [{"role": "user", "content": "what is weather in london and canada?, do two parallel tool calls to get the weather in both cities /no_think"}]
    tools = [get_weather]
    print("\n\n=== Low-level Streaming Demo ===\n")
    async for chunk in step(lm=lm, history=messages, tools=tools):
        print(chunk)

    tool_results = await chunk.tool_results()
    print('----------')
    print(tool_results)


async def main():
    # Demo 1: Simple agent loop
    await demo_simple_loop()

    # Example 3: Low-level streaming
    # await example_streaming_gen()

    # await example_streaming_step()


if __name__ == "__main__":
    asyncio.run(main())
