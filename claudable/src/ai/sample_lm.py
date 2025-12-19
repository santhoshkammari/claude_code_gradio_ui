"""
LM (Language Model) Usage Examples

Demonstrates the lm.py interface for streaming and batch LLM operations.
"""

import asyncio

from .lm import LM


async def demo_stream_basic():
    """Demo 1: Basic streaming"""
    print("\n" + "="*60)
    print("DEMO 1: Basic Streaming")
    print("="*60)

    lm = LM()
    messages = [{"role": "user", "content": "What is 2+2? Answer briefly."}]

    print("Streaming response:")
    async for chunk in lm.stream(messages):
        if chunk.get("choices"):
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta and delta["content"]:
                print(delta["content"], end="", flush=True)
    print("\n")


async def demo_stream_with_string():
    """Demo 2: Stream with string input"""
    print("\n" + "="*60)
    print("DEMO 2: Stream with String Input")
    print("="*60)

    lm = LM()

    print("Streaming response:")
    async for chunk in lm.stream("Tell me a short joke"):
        if chunk.get("choices"):
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta and delta["content"]:
                print(delta["content"], end="", flush=True)
    print("\n")


async def demo_batch():
    """Demo 3: Batch processing"""
    print("\n" + "="*60)
    print("DEMO 3: Batch Processing")
    print("="*60)

    lm = LM()

    # Batch of questions
    messages_batch = [
        [{"role": "user", "content": "What is 2+2?"}],
        [{"role": "user", "content": "What is 5*5?"}],
        [{"role": "user", "content": "What is 10-3?"}],
    ]

    print("Processing 3 questions in parallel...")
    results = await lm.batch(messages_batch)

    for i, result in enumerate(results):
        if isinstance(result, dict):
            content = result["choices"][0]["message"]["content"]
            print(f"  Q{i+1} → {content[:50]}...")
        else:
            print(f"  Q{i+1} → Error: {result}")


async def demo_batch_with_strings():
    """Demo 4: Batch with string inputs"""
    print("\n" + "="*60)
    print("DEMO 4: Batch with String Inputs")
    print("="*60)

    lm = LM()

    # Simple string queries
    queries = [
        "What is the capital of France?",
        "What is the capital of Japan?",
        "What is the capital of Brazil?",
    ]

    print("Processing 3 geography questions...")
    results = await lm.batch(queries)

    for i, result in enumerate(results):
        if isinstance(result, dict):
            content = result["choices"][0]["message"]["content"]
            print(f"  {queries[i][:30]}... → {content[:40]}...")


async def demo_multi_turn():
    """Demo 5: Multi-turn conversation"""
    print("\n" + "="*60)
    print("DEMO 5: Multi-turn Conversation")
    print("="*60)

    lm = LM()

    # Build a conversation
    history = [
        {"role": "user", "content": "My name is Alice."},
        {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
        {"role": "user", "content": "What's my name?"}
    ]

    print("Conversation:")
    for msg in history[:-1]:
        print(f"  {msg['role']}: {msg['content']}")

    print(f"  user: {history[-1]['content']}")
    print("  assistant: ", end="")

    async for chunk in lm.stream(history):
        if chunk.get("choices"):
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta and delta["content"]:
                print(delta["content"], end="", flush=True)
    print("\n")


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("LM INTERFACE DEMOS")
    print("="*60)

    await demo_stream_basic()
    await demo_stream_with_string()
    await demo_batch()
    await demo_batch_with_strings()
    await demo_multi_turn()

    print("\n" + "="*60)
    print("ALL DEMOS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
