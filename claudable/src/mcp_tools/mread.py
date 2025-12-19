from typing import Dict, Any, List, Optional
import os
from fastmcp import FastMCP

mcp = FastMCP("MultiRead")

# Max file size: 20MB
MAX_FILE_SIZE = 20 * 1024 * 1024
# Max lines to read per file (default)
DEFAULT_MAX_LINES = 2000
# Max characters per line before truncation
MAX_LINE_LENGTH = 2000


@mcp.tool
def multi_read(
    file_paths: List[str],
    offset: Optional[int] = None,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Read multiple files at once. Handles large files automatically.

    Args:
        file_paths: List of absolute file paths to read
        offset: Optional line number to start reading from (applies to all files)
        limit: Optional number of lines to read (applies to all files, default 2000)

    Returns:
        Dict with results for each file:
        {
            "files": [
                {
                    "path": str,
                    "status": "success" | "error" | "too_large",
                    "content": str (if success),
                    "error": str (if error),
                    "size_mb": float (if too_large),
                    "lines_read": int,
                    "total_lines": int,
                    "truncated_lines": int (number of lines that were truncated)
                }
            ],
            "summary": {
                "total_files": int,
                "successful": int,
                "failed": int,
                "too_large": int
            }
        }
    """
    results = []
    stats = {"total_files": len(file_paths), "successful": 0, "failed": 0, "too_large": 0}

    # Set default limit
    read_limit = limit if limit is not None else DEFAULT_MAX_LINES
    read_offset = offset if offset is not None else 0

    for file_path in file_paths:
        try:
            # Check if file exists
            if not os.path.isfile(file_path):
                results.append({
                    "path": file_path,
                    "status": "error",
                    "error": f"File not found: {file_path}"
                })
                stats["failed"] += 1
                continue

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                results.append({
                    "path": file_path,
                    "status": "too_large",
                    "error": f"File too large ({size_mb:.2f} MB). Maximum size is 20 MB.",
                    "size_mb": size_mb
                })
                stats["too_large"] += 1
                continue

            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                all_lines = f.readlines()

            total_lines = len(all_lines)

            # Apply offset and limit
            if read_offset >= total_lines:
                selected_lines = []
            else:
                end_line = min(read_offset + read_limit, total_lines)
                selected_lines = all_lines[read_offset:end_line]

            # Truncate long lines and track how many were truncated
            truncated_count = 0
            processed_lines = []
            for line in selected_lines:
                if len(line) > MAX_LINE_LENGTH:
                    processed_lines.append(line[:MAX_LINE_LENGTH] + "...[truncated]\n")
                    truncated_count += 1
                else:
                    processed_lines.append(line)

            # Format with line numbers (starting from 0 like Read tool)
            formatted_lines = []
            for i, line in enumerate(processed_lines, start=read_offset):
                # Remove trailing newline for formatting
                line_content = line.rstrip('\n')
                formatted_lines.append(f"{i:6d}→{line_content}")

            content = '\n'.join(formatted_lines)

            results.append({
                "path": file_path,
                "status": "success",
                "content": content,
                "lines_read": len(selected_lines),
                "total_lines": total_lines,
                "truncated_lines": truncated_count,
                "offset": read_offset,
                "limit": read_limit
            })
            stats["successful"] += 1

        except UnicodeDecodeError:
            results.append({
                "path": file_path,
                "status": "error",
                "error": f"Cannot read file (binary or encoding issue): {file_path}"
            })
            stats["failed"] += 1
        except Exception as e:
            results.append({
                "path": file_path,
                "status": "error",
                "error": f"Error reading {file_path}: {str(e)}"
            })
            stats["failed"] += 1

    return {
        "files": results,
        "summary": stats
    }


if __name__ == "__main__":
    mcp.run()
