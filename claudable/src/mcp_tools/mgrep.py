import subprocess
import shutil
from fastmcp import FastMCP
from typing import Optional, List, Dict, Any
import json

mcp = FastMCP("MultiGrep")

# Find ripgrep executable
RG_PATH = shutil.which('rg') or '/usr/bin/rg'


def execute_grep(search_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute single grep search using ripgrep.
    
    Returns dict with pattern, path, output, error, matches_found keys.
    """
    pattern = search_config.get('pattern')
    if not pattern:
        return {"error": "Pattern is required", "pattern": None}

    # Build ripgrep command
    cmd = [RG_PATH, pattern]

    # Add optional parameters
    if search_config.get('case_insensitive'):
        cmd.append('-i')

    if search_config.get('multiline'):
        cmd.extend(['-U', '--multiline-dotall'])

    if search_config.get('show_line_numbers', True):
        cmd.append('-n')

    output_mode = search_config.get('output_mode', 'files_with_matches')
    if output_mode == 'files_with_matches':
        cmd.append('-l')
    elif output_mode == 'count':
        cmd.append('-c')

    if search_config.get('glob'):
        cmd.extend(['--glob', search_config['glob']])

    if search_config.get('type'):
        cmd.extend(['--type', search_config['type']])

    context = search_config.get('context_lines')
    if context:
        cmd.extend(['-C', str(context)])

    path = search_config.get('path', '.')
    cmd.append(path)

    # Execute command
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "pattern": pattern,
            "path": path,
            "output": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "error": result.stderr.strip() if result.returncode != 0 and result.returncode != 1 else None,
            "matches_found": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "pattern": pattern,
            "path": path,
            "output": "",
            "error": "Search timed out after 30 seconds",
            "matches_found": False
        }
    except Exception as e:
        return {
            "pattern": pattern,
            "path": path,
            "output": "",
            "error": str(e),
            "matches_found": False
        }


@mcp.tool
def multigrep(
    searches: List[Dict[str, Any]],
    consolidate: Optional[bool] = False
) -> str:
    """
    Perform multiple grep searches in a single operation.

    Args:
        searches: List of search operations, each containing:
            - pattern (required): The regex pattern to search for
            - path (optional): File or directory to search in (default: current directory)
            - output_mode (optional): "content"|"files_with_matches"|"count" (default: "files_with_matches")
            - glob (optional): File pattern like "*.js" or "*.{ts,tsx}"
            - type (optional): File type like "py", "js", "rust"
            - case_insensitive (optional): Boolean for case-insensitive search
            - show_line_numbers (optional): Boolean to show line numbers (default: True)
            - context_lines (optional): Number of context lines before/after match
            - multiline (optional): Boolean for multiline mode

        consolidate: If True, merge results by file path. If False, show separate results per search.

    Example:
        searches = [
            {"pattern": "TODO", "glob": "*.py", "output_mode": "content"},
            {"pattern": "FIXME", "glob": "*.py", "output_mode": "content"},
            {"pattern": "class.*Error", "path": "src/", "type": "py"}
        ]
    """
    if not searches:
        return "Error: At least one search configuration is required"

    results = []
    all_outputs = []

    for i, search in enumerate(searches, 1):
        result = execute_grep(search)
        results.append(result)

        if consolidate:
            if result['output']:
                all_outputs.append(result['output'])
        else:
            # Format individual result
            output_parts = [f"\n{'='*60}"]
            output_parts.append(f"Search {i}: pattern='{result['pattern']}' path='{result.get('path', '.')}'")
            output_parts.append('='*60)

            if result.get('error'):
                output_parts.append(f"Error: {result['error']}")
            elif result['matches_found']:
                output_parts.append(result['output'])
            else:
                output_parts.append("No matches found")

            all_outputs.append('\n'.join(output_parts))

    if consolidate:
        # Consolidate all results
        header = f"MultiGrep Results: {len(searches)} search(es) executed\n{'='*60}"
        if all_outputs:
            return header + "\n\n" + "\n\n".join(all_outputs)
        else:
            return header + "\n\nNo matches found in any search"
    else:
        # Return separate results
        summary = f"Executed {len(searches)} search(es)\n"
        return summary + "\n".join(all_outputs)


if __name__ == "__main__":
    mcp.run()
