"""
Sample evaluation run demonstrating eval framework with real LM
Uses history-based evaluation with agent.step() and agent.agent()

Combines basic demos and advanced tool-based evaluation demos.
"""

import asyncio
import re

from .eval import eval_example, eval_stream, eval_batch
from .lm import LM


# Metric functions
def exact_match(target, prediction):
    """Check if prediction matches expected answer"""
    expected = str(target).strip()
    # Extract first number from prediction
    match = re.search(r'\d+(?:\.\d+)?', str(prediction))
    if match:
        predicted = match.group(0)
        return 1.0 if expected == predicted else 0.0
    return 0.0


def contains_match(target, prediction):
    """Check if prediction contains expected answer"""
    expected = str(target).strip().lower()
    predicted = str(prediction).strip().lower()
    return 1.0 if expected in predicted or predicted in expected else 0.0


# Tool definitions
def calculator(expression: str) -> str:
    """
    Simple calculator tool for math expressions

    Args:
        expression: Math expression like "2+2" or "5*5"

    Returns:
        Result of the calculation
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def search(query: str) -> str:
    """
    Mock search tool

    Args:
        query: Search query

    Returns:
        Search results
    """
    return f"Results for '{query}': [mock data]"


# Create sample dataset with histories and targets
dev_data = [
    {
        "history": [{"role": "user", "content": "Answer with ONLY the number. Q: What is 2+2"}],
        "target": "4"
    },
    {
        "history": [{"role": "user", "content": "Answer with ONLY the number. Q: What is 5+5"}],
        "target": "10"
    },
    {
        "history": [{"role": "user", "content": "Answer with ONLY the number. Q: What is 3*3"}],
        "target": "9"
    },
    {
        "history": [{"role": "user", "content": "Answer with ONLY the number. Q: What is 10-2"}],
        "target": "8"
    },
    {
        "history": [{"role": "user", "content": "Answer with ONLY the number. Q: What is 100/10"}],
        "target": "10"
    },
    {
        "history": [{"role": "user", "content": "Answer with ONLY the number. Q: What is 7+7"}],
        "target": "14"
    },
    {
        "history": [{"role": "user", "content": "Answer with ONLY the number. Q: What is 9*9"}],
        "target": "81"
    },
]


async def demo_single_eval():
    """Demo 1: Evaluate single example"""
    print("\n" + "="*60)
    print("DEMO 1: Single Example Evaluation")
    print("="*60)

    lm = LM()
    history = dev_data[0]["history"]
    target = dev_data[0]["target"]

    result = await eval_example(
        history=history,
        target=target,
        metric=exact_match,
        lm=lm,
        use_agent=False
    )

    print(f"Question: {history[0]['content']}")
    print(f"Expected: {target}")
    print(f"Predicted: {result.prediction}")
    print(f"Score: {result.score}")
    print(f"Metadata: {result.metadata}")


async def demo_stream_eval():
    """Demo 2: Stream evaluation with early stopping"""
    print("\n" + "="*60)
    print("DEMO 2: Streaming Evaluation (Real-time Results)")
    print("="*60)

    lm = LM()
    histories = [d["history"] for d in dev_data[:4]]
    targets = [d["target"] for d in dev_data[:4]]

    results = []
    passed = 0
    async for result in eval_stream(
        histories=histories,
        targets=targets,
        metric=exact_match,
        lm=lm,
        use_agent=False
    ):
        results.append(result)
        if result.score > 0.5:
            passed += 1
        question = result.history[0]["content"][:40] + "..." if len(result.history[0]["content"]) > 40 else result.history[0]["content"]
        pred_str = str(result.prediction)[:10]
        print(f"  Q: {question:43} | Pred: {pred_str:10} | Score: {result.score:.2f}")

    avg_score = (sum([r.score for r in results]) / len(results) * 100) if results else 0.0
    print(f"\nRunning Average: {avg_score:.1f}% ({passed}/{len(results)})")


async def demo_batch_sequential():
    """Demo 3: Sequential batch evaluation"""
    print("\n" + "="*60)
    print("DEMO 3: Sequential Batch Evaluation")
    print("="*60)

    lm = LM()
    histories = [d["history"] for d in dev_data]
    targets = [d["target"] for d in dev_data]

    result = await eval_batch(
        histories=histories,
        targets=targets,
        metric=exact_match,
        lm=lm,
        batch_size=4,
        parallel=False,
        progress=True,
        use_agent=False
    )

    print(f"\nFinal Score: {result['score']:.1f}%")
    print(f"Passed: {result['passed']}/{result['total']}")
    print("\nDetailed Results:")
    for i, r in enumerate(result['results']):
        status = "✓" if r.score > 0.5 else "✗"
        question = r.history[0]["content"].split("Q: ")[-1] if "Q: " in r.history[0]["content"] else r.history[0]["content"]
        pred_str = str(r.prediction)[:10]
        print(f"  {status} {question:25} → {pred_str:10} (score: {r.score:.2f})")


async def demo_batch_parallel():
    """Demo 4: Parallel batch evaluation"""
    print("\n" + "="*60)
    print("DEMO 4: Parallel Batch Evaluation")
    print("="*60)

    lm = LM()
    histories = [d["history"] for d in dev_data]
    targets = [d["target"] for d in dev_data]

    result = await eval_batch(
        histories=histories,
        targets=targets,
        metric=exact_match,
        lm=lm,
        batch_size=2,
        parallel=True,
        progress=True,
        use_agent=False
    )

    print(f"\nFinal Score: {result['score']:.1f}%")
    print(f"Passed: {result['passed']}/{result['total']}")
    print("\nDetailed Results:")
    for i, r in enumerate(result['results']):
        status = "✓" if r.score > 0.5 else "✗"
        question = r.history[0]["content"].split("Q: ")[-1] if "Q: " in r.history[0]["content"] else r.history[0]["content"]
        pred_str = str(r.prediction)[:10]
        print(f"  {status} {question:25} → {pred_str:10} (score: {r.score:.2f})")


async def demo_multiple_metrics():
    """Demo 5: Compare multiple metrics"""
    print("\n" + "="*60)
    print("DEMO 5: Multiple Metrics Comparison")
    print("="*60)

    lm = LM()
    histories = [d["history"] for d in dev_data]
    targets = [d["target"] for d in dev_data]

    result_exact = await eval_batch(
        histories=histories,
        targets=targets,
        metric=exact_match,
        lm=lm,
        parallel=False,
        progress=False,
        use_agent=False
    )

    result_contains = await eval_batch(
        histories=histories,
        targets=targets,
        metric=contains_match,
        lm=lm,
        parallel=False,
        progress=False,
        use_agent=False
    )

    print(f"Exact Match:     {result_exact['score']:.1f}% ({result_exact['passed']}/{result_exact['total']})")
    print(f"Contains Match:  {result_contains['score']:.1f}% ({result_contains['passed']}/{result_contains['total']})")


async def demo_step_based_eval():
    """Demo 6: Evaluate using agent.step() with tools"""
    print("\n" + "="*60)
    print("DEMO 6: Agent-Based Evaluation (Using step())")
    print("="*60)
    print(f"Module: Agent with calculator and search tools")

    lm = LM()
    tools = [calculator, search]

    # Create tool-compatible dataset
    tool_data = [
        {
            "history": [{"role": "user", "content": "What is 2+2?"}],
            "target": "4"
        },
        {
            "history": [{"role": "user", "content": "What is 5*5?"}],
            "target": "25"
        },
    ]

    histories = [d["history"] for d in tool_data]
    targets = [d["target"] for d in tool_data]

    result = await eval_batch(
        histories=histories,
        targets=targets,
        metric=exact_match,
        lm=lm,
        tools=tools,
        batch_size=2,
        parallel=False,
        progress=True,
        use_agent=False
    )

    print(f"\nScore: {result['score']:.1f}%")
    print(f"Passed: {result['passed']}/{result['total']}")
    print("\nDetailed Results:")
    for i, r in enumerate(result['results']):
        status = "✓" if r.score > 0.5 else "✗"
        question = r.history[0]["content"]
        target = targets[i]
        print(f"  {status} Q: {question:30} | Expected: {target:5} | Score: {r.score:.2f}")


async def demo_single_step_eval_with_tools():
    """Demo 7: Single example with step-based evaluation and tools"""
    print("\n" + "="*60)
    print("DEMO 7: Single Example with Tools (Using step())")
    print("="*60)

    lm = LM()
    tools = [calculator, search]

    history = [{"role": "user", "content": "What is 2+2?"}]
    target = "4"

    result = await eval_example(
        history=history,
        target=target,
        metric=exact_match,
        lm=lm,
        tools=tools,
        use_agent=False
    )

    print(f"Question: {history[0]['content']}")
    print(f"Expected: {target}")
    print(f"Predicted: {result.prediction[:100]}..." if len(str(result.prediction)) > 100 else f"Predicted: {result.prediction}")
    print(f"Score: {result.score}")
    print(f"Metadata: {result.metadata}")


async def demo_stream_step_eval_with_tools():
    """Demo 8: Streaming evaluation with step() and tools"""
    print("\n" + "="*60)
    print("DEMO 8: Streaming Evaluation with Tools (Using step())")
    print("="*60)

    lm = LM()
    tools = [calculator]

    tool_data = [
        {"history": [{"role": "user", "content": "What is 2+2?"}], "target": "4"},
        {"history": [{"role": "user", "content": "What is 10-3?"}], "target": "7"},
        {"history": [{"role": "user", "content": "What is 100/10?"}], "target": "10.0"},
    ]

    histories = [d["history"] for d in tool_data]
    targets = [d["target"] for d in tool_data]

    print("Evaluating examples in streaming mode:\n")
    count = 0
    async for result in eval_stream(
        histories=histories,
        targets=targets,
        metric=exact_match,
        lm=lm,
        tools=tools,
        use_agent=False
    ):
        count += 1
        status = "✓" if result.score > 0.5 else "✗"
        question = result.history[0]["content"]
        print(f"  {status} Example {count}: {question:35} | Score: {result.score:.2f}")


async def demo_agent_loop_eval():
    """Demo 9: Evaluate using full agent loop with multiple iterations"""
    print("\n" + "="*60)
    print("DEMO 9: Agent Loop Evaluation (Using agent())")
    print("="*60)

    lm = LM()
    tools = [calculator, search]

    # More complex history that might need multiple steps
    history = [{"role": "user", "content": "What is 2+2? Then multiply that by 5."}]
    target = "20"

    result = await eval_example(
        history=history,
        target=target,
        metric=exact_match,
        lm=lm,
        tools=tools,
        use_agent=True,  # Use full agent loop
        max_iterations=5
    )

    print(f"Question: {history[0]['content']}")
    print(f"Expected: {target}")
    print(f"Predicted: {result.prediction}")
    print(f"Score: {result.score}")
    print(f"Metadata: {result.metadata}")


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("EVALUATION FRAMEWORK DEMOS")
    print("="*60)
    print(f"Evaluation Mode: History-based with agent.step() and agent.agent()")
    print(f"Dataset: {len(dev_data)} examples")
    print(f"Metrics: exact_match, contains_match")

    # Basic demos
    await demo_single_eval()
    await demo_stream_eval()
    await demo_batch_sequential()
    await demo_batch_parallel()
    await demo_multiple_metrics()

    # Tool-based demos
    await demo_step_based_eval()
    await demo_single_step_eval_with_tools()
    await demo_stream_step_eval_with_tools()
    await demo_agent_loop_eval()

    print("\n" + "="*60)
    print("ALL DEMOS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
