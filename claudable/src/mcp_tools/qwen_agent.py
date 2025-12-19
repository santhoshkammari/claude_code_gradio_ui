import subprocess
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP("Qwen Agent")

@mcp.tool
def run_qwen(prompt: str, model: Optional[str] = None, sandbox: bool = False):
    """
    Run Qwen Code with a prompt in YOLO mode (auto-accept all actions).

    Args:
        prompt: The prompt/query to send to Qwen Code.
        model: Optional model to use (e.g., 'qwen-plus', 'qwen-turbo').
        sandbox: Whether to run in sandbox mode.
    """
    cmd = ["qwen", "-y", "-p", prompt]

    if model:
        cmd.extend(["-m", model])

    if sandbox:
        cmd.append("-s")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        output = result.stdout
        if result.stderr:
            output += f"\n\nErrors:\n{result.stderr}"

        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 5 minutes"
    except Exception as e:
        return f"Error running qwen: {str(e)}"

if __name__ == "__main__":
    mcp.run()
