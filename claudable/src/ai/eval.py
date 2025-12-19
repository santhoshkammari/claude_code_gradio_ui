"""
Minimal evaluation framework - parallel to agent.step() and agent.agent()

Evaluates conversation histories using the agent system:
1. Single step: eval_example(history, target, metric, lm, tools, use_agent=False)
2. Agent loop: eval_example(history, target, metric, lm, tools, use_agent=True)
"""

import asyncio
from dataclasses import dataclass, field
from typing import Callable, List, AsyncIterator, Any, Optional
import tqdm.asyncio
import tqdm
from .agent import step, agent


@dataclass
class EvalResult:
    """Result for ONE evaluation"""
    history: list[dict]
    prediction: Any
    score: float
    metadata: dict = field(default_factory=dict)

    def __repr__(self):
        return f"EvalResult(score={self.score:.2f}, metadata={self.metadata})"


async def eval_example(
    history: list[dict],
    target: Any,
    metric: Callable,
    lm: Any,
    tools: List[Callable] = None,
    use_agent: bool = False,
    max_iterations: int = 10,
    **kwargs
) -> EvalResult:
    """
    Evaluate ONE conversation history.

    Two modes:
    1. Single step (use_agent=False): Use step() for one LLM generation
    2. Agent loop (use_agent=True): Use agent() for multi-turn interactions

    Args:
        history: Conversation history (same format as agent.step/agent.agent)
        target: Expected output for comparison
        metric: Callable(target, prediction) → float [0-1]
        lm: LM instance
        tools: List of tools
        use_agent: If True, use agent() loop; if False, use single step()
        max_iterations: Max iterations for agent mode
        **kwargs: Extra params passed to agent/step

    Returns:
        EvalResult with prediction and score
    """
    try:
        if use_agent:
            # Full agent loop evaluation
            result = await agent(
                lm=lm,
                history=history.copy(),  # Copy to avoid modifying original
                tools=tools,
                max_iterations=max_iterations,
                **kwargs
            )

            # Extract final response as prediction
            pred = result["final_response"]
            eval_metadata = {
                "iterations": result["iterations"],
                "tool_calls_total": result["tool_calls_total"]
            }
        else:
            # Single step evaluation
            result = await step(
                lm=lm,
                history=history.copy(),
                tools=tools,
                **kwargs
            )

            # Extract content as prediction
            pred = result.message.get("content", "")

            # If there are tool calls, wait for results and include them
            if result.tool_calls:
                try:
                    tool_results = await result.tool_results()
                    # Combine content and tool results
                    tool_outputs = [f"{tr.tool_call_id}: {tr.output}" for tr in tool_results]
                    if pred:
                        pred = f"{pred}\n" + "\n".join(tool_outputs)
                    else:
                        pred = "\n".join(tool_outputs)
                except Exception as tool_err:
                    # If tool execution fails, just use content
                    pass

            eval_metadata = {"tool_calls": len(result.tool_calls)}

        # Calculate metric
        score = metric(target, pred)

        return EvalResult(
            history=history,
            prediction=pred,
            score=score,
            metadata=eval_metadata
        )
    except Exception as e:
        return EvalResult(
            history=history,
            prediction=None,
            score=0.0,
            metadata={"error": str(e)}
        )


async def eval_stream(
    histories: List[list[dict]],
    targets: List[Any],
    metric: Callable,
    lm: Any,
    tools: List[Callable] = None,
    use_agent: bool = False,
    max_iterations: int = 10,
    **kwargs
) -> AsyncIterator[EvalResult]:
    """
    Stream evaluation results one-by-one.

    Parallel to LM.stream() - yields results as they complete.
    Useful for real-time monitoring and early stopping.

    Args:
        histories: List of conversation histories
        targets: List of expected outputs (same length as histories)
        metric: Callable(target, prediction) → float [0-1]
        lm: LM instance
        tools: List of tools
        use_agent: If True, use agent() loop; if False, use single step()
        max_iterations: Max iterations for agent mode
        **kwargs: Extra params passed to agent/step

    Yields:
        EvalResult for each history

    Usage:
        async for result in eval_stream(histories, targets, metric, lm):
            print(f"Score: {result.score}")
            if result.score < 0.5:
                break  # Early stop
    """
    for history, target in zip(histories, targets):
        result = await eval_example(
            history, target, metric, lm,
            tools=tools, use_agent=use_agent,
            max_iterations=max_iterations,
            **kwargs
        )
        yield result


async def eval_batch(
    histories: List[list[dict]],
    targets: List[Any],
    metric: Callable,
    lm: Any,
    tools: List[Callable] = None,
    batch_size: int = 4,
    parallel: bool = False,
    progress: bool = True,
    use_agent: bool = False,
    max_iterations: int = 10,
    **kwargs
) -> dict:
    """
    Batch evaluate conversation histories.

    Parallel to LM.batch() - processes multiple histories together.
    Can be sequential or concurrent.

    Args:
        histories: List of conversation histories
        targets: List of expected outputs (same length as histories)
        metric: Callable(target, prediction) → float [0-1]
        lm: LM instance
        tools: List of tools
        batch_size: Size for concurrent batches (if parallel=True)
        parallel: If True, evaluate batch_size histories concurrently
        progress: Show progress bar
        use_agent: If True, use agent() loop; if False, use single step()
        max_iterations: Max iterations for agent mode
        **kwargs: Extra params passed to agent/step

    Returns:
        {
            "score": float (0-100%),
            "passed": int (count where score > 0.5),
            "total": int,
            "results": List[EvalResult]
        }

    Usage:
        result = await eval_batch(
            histories=[history1, history2, ...],
            targets=[target1, target2, ...],
            metric=exact_match,
            lm=lm,
            batch_size=8,
            parallel=True
        )
        print(f"Score: {result['score']:.1f}%")
    """
    results = []
    scores = []

    if parallel:
        # Process in concurrent batches
        async def process_batch(batch_histories, batch_targets):
            tasks = [
                eval_example(hist, tgt, metric, lm,
                           tools=tools, use_agent=use_agent,
                           max_iterations=max_iterations,
                           **kwargs)
                for hist, tgt in zip(batch_histories, batch_targets)
            ]
            return await asyncio.gather(*tasks)

        # Create batches
        history_batches = [
            histories[i:i + batch_size]
            for i in range(0, len(histories), batch_size)
        ]
        target_batches = [
            targets[i:i + batch_size]
            for i in range(0, len(targets), batch_size)
        ]

        # Process all batches concurrently
        pbar = tqdm.asyncio.tqdm(list(zip(history_batches, target_batches)), desc="Evaluating") if progress else zip(history_batches, target_batches)
        async for hist_batch, tgt_batch in pbar:
            batch_results = await process_batch(hist_batch, tgt_batch)
            results.extend(batch_results)
            scores.extend([r.score for r in batch_results])
    else:
        # Sequential processing
        iterator = tqdm.tqdm(list(zip(histories, targets)), desc="Evaluating") if progress else zip(histories, targets)
        for history, target in iterator:
            result = await eval_example(history, target, metric, lm,
                                      tools=tools, use_agent=use_agent,
                                      max_iterations=max_iterations,
                                      **kwargs)
            results.append(result)
            scores.append(result.score)

    final_score = (sum(scores) / len(scores) * 100) if scores else 0.0
    passed = sum(1 for s in scores if s > 0.5)

    return {
        "score": final_score,
        "passed": passed,
        "total": len(histories),
        "results": results
    }
