from typing import Dict, Any, List
import json
import uuid
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastmcp import FastMCP

mcp = FastMCP("Run-Agents")


@mcp.tool
def run_multiple_qwen_agents_in_parallel(path: str) -> Dict[str, Any]:
    """
    Execute multiple independent Qwen agents in parallel from a JSON manifest file.

    Runs up to 4 Qwen agents concurrently, each in YOLO mode (-y flag). This is useful
    for running multiple independent tasks simultaneously (e.g., git operations,
    file processing, code generation) without waiting for sequential completion.

    Args:
        path: Absolute path to JSON file containing array of agent configurations.
              Each agent config must have:
                - system_prompt (required): The prompt/instructions for the Qwen agent
                - task (optional): Additional task description appended to system_prompt
                - id (optional): Custom identifier for the agent (defaults to "agent-N")

              Example agents.json:
              [
                {
                  "id": "git-committer",
                  "system_prompt": "You are a git expert",
                  "task": "Create a commit for the CSS changes and push to origin/dev"
                },
                {
                  "id": "code-formatter",
                  "system_prompt": "Format all TypeScript files",
                  "task": "Run prettier on src/**/*.ts"
                }
              ]

    Returns:
        Dict containing:
          - run_id: Unique identifier for this parallel execution
          - status: "completed" | "completed_with_errors" | "validation_failed"
          - agents: List of execution results (stdout, stderr, returncode per agent)
          - errors: List of error messages if any agents failed
    """
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    errors: List[str] = []

    # --- Step 1: Load file ---
    if not os.path.isfile(path):
        return {
            "run_id": None,
            "status": "validation_failed",
            "agents": [],
            "errors": [f"agents.json not found at path: {path}"]
        }

    try:
        with open(path, "r", encoding="utf-8") as f:
            agents_data = json.load(f)
    except Exception as e:
        return {
            "run_id": None,
            "status": "validation_failed",
            "agents": [],
            "errors": [f"Failed to read agents.json: {str(e)}"]
        }

    # --- Step 2: Validate structure ---
    if not isinstance(agents_data, list):
        return {
            "run_id": None,
            "status": "validation_failed",
            "agents": [],
            "errors": ["agents.json must be a JSON array"]
        }

    # --- Step 3: Execute agents in parallel (max 4 at a time) ---
    executed_agents = []

    def execute_agent(idx: int, agent: dict) -> dict:
        """Execute a single agent using qwen command."""
        if not isinstance(agent, dict):
            return {"id": f"agent-{idx}", "state": "failed", "error": "Invalid agent format"}

        if "system_prompt" not in agent or not isinstance(agent["system_prompt"], str):
            return {"id": agent.get("id", f"agent-{idx}"), "state": "failed", "error": "Missing system_prompt"}

        agent_id = agent.get("id", f"agent-{idx}")
        system_prompt = agent["system_prompt"]
        task = agent.get("task", "")

        # Combine system_prompt and task if task exists
        full_prompt = f"{system_prompt}\n\nTask: {task}" if task else system_prompt

        try:
            # Run qwen with the prompt in yolo mode
            cmd = ["qwen", "-p", full_prompt, "-y"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=os.getcwd())

            return {
                "id": agent_id,
                "state": "completed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"id": agent_id, "state": "failed", "error": "Execution timed out (300s)"}
        except Exception as e:
            return {"id": agent_id, "state": "failed", "error": str(e)}

    # Execute agents in parallel with max 4 workers
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(execute_agent, idx, agent): idx for idx, agent in enumerate(agents_data)}
        
        for future in as_completed(futures):
            result = future.result()
            executed_agents.append(result)
            if "error" in result:
                errors.append(f"Agent {result['id']}: {result['error']}")

    if errors:
        return {
            "run_id": run_id,
            "status": "completed_with_errors",
            "agents": executed_agents,
            "errors": errors
        }

    # --- Step 4: Return execution results ---
    return {
        "run_id": run_id,
        "status": "completed",
        "agents": executed_agents,
        "errors": []
    }

if __name__=="__main__":
    mcp.run()
