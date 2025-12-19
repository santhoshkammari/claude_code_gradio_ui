from fastmcp import FastMCP
import os
from typing import Optional, Literal

def read_file_lines(file_path: str):
    """Helper function to read file lines"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist")
    if not os.path.isfile(file_path):
        raise ValueError(f"'{file_path}' is not a file")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def write_file_lines(file_path: str, lines: list):
    """Helper function to write file lines"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def copy_paste_within_file_impl(
    file_path: str,
    source_start: int,
    source_end: int,
    target_line: int,
    mode: Literal["insert", "replace"] = "insert"
) -> str:
    """
    Copy lines from one location to another within the same file.

    Args:
        file_path: Path to the file
        source_start: Starting line number to copy from (1-indexed)
        source_end: Ending line number to copy from (1-indexed, inclusive)
        target_line: Line number where to paste (1-indexed)
        mode: "insert" (push existing lines down) or "replace" (overwrite lines)
    """
    try:
        lines = read_file_lines(file_path)
        total_lines = len(lines)

        # Validate line numbers
        if source_start < 1 or source_end < source_start or source_start > total_lines:
            return f"Error: Invalid source range. File has {total_lines} lines."
        if target_line < 1:
            return f"Error: target_line must be >= 1"

        # Adjust to 0-based indexing
        src_start_idx = source_start - 1
        src_end_idx = min(source_end, total_lines) - 1
        target_idx = target_line - 1

        # Extract source lines
        copied_lines = lines[src_start_idx:src_end_idx + 1]
        num_copied = len(copied_lines)

        if mode == "insert":
            # Insert at target position
            new_lines = lines[:target_idx] + copied_lines + lines[target_idx:]
        else:  # replace
            # Replace lines starting from target
            end_replace_idx = target_idx + num_copied
            new_lines = lines[:target_idx] + copied_lines + lines[end_replace_idx:]

        write_file_lines(file_path, new_lines)

        return f"Successfully copied lines {source_start}-{source_end} to line {target_line} ({mode} mode). Copied {num_copied} line(s)."

    except Exception as e:
        return f"Error: {str(e)}"

def copy_paste_between_files_impl(
    source_file: str,
    source_start: int,
    source_end: int,
    target_file: str,
    target_line: int,
    mode: Literal["insert", "replace"] = "insert"
) -> str:
    """
    Copy lines from one file and paste into another file.

    Args:
        source_file: Path to the source file
        source_start: Starting line number to copy from (1-indexed)
        source_end: Ending line number to copy from (1-indexed, inclusive)
        target_file: Path to the target file
        target_line: Line number where to paste (1-indexed)
        mode: "insert" (push existing lines down) or "replace" (overwrite lines)
    """
    try:
        # Read source file
        source_lines = read_file_lines(source_file)
        source_total = len(source_lines)

        # Read target file
        target_lines = read_file_lines(target_file)
        target_total = len(target_lines)

        # Validate source range
        if source_start < 1 or source_end < source_start or source_start > source_total:
            return f"Error: Invalid source range. Source file has {source_total} lines."
        if target_line < 1:
            return f"Error: target_line must be >= 1"

        # Adjust to 0-based indexing
        src_start_idx = source_start - 1
        src_end_idx = min(source_end, source_total) - 1
        target_idx = target_line - 1

        # Extract source lines
        copied_lines = source_lines[src_start_idx:src_end_idx + 1]
        num_copied = len(copied_lines)

        if mode == "insert":
            # Insert at target position
            new_lines = target_lines[:target_idx] + copied_lines + target_lines[target_idx:]
        else:  # replace
            # Replace lines starting from target
            end_replace_idx = target_idx + num_copied
            new_lines = target_lines[:target_idx] + copied_lines + target_lines[end_replace_idx:]

        write_file_lines(target_file, new_lines)

        return f"Successfully copied {num_copied} line(s) from '{source_file}' (lines {source_start}-{source_end}) to '{target_file}' at line {target_line} ({mode} mode)."

    except Exception as e:
        return f"Error: {str(e)}"

def replace_pattern_occurrences_impl(
    file_path: str,
    pattern_start_line: int,
    pattern_end_line: int,
    new_string: str
) -> str:
    """
    Find all occurrences of a specific line range pattern and replace them all.

    Args:
        file_path: Path to the file
        pattern_start_line: Starting line number of the pattern (1-indexed)
        pattern_end_line: Ending line number of the pattern (1-indexed, inclusive)
        new_string: New content to replace all occurrences with
    """
    try:
        lines = read_file_lines(file_path)
        total_lines = len(lines)

        # Validate pattern range
        if pattern_start_line < 1 or pattern_end_line < pattern_start_line or pattern_start_line > total_lines:
            return f"Error: Invalid pattern range. File has {total_lines} lines."

        # Adjust to 0-based indexing
        pattern_start_idx = pattern_start_line - 1
        pattern_end_idx = min(pattern_end_line, total_lines) - 1

        # Extract the pattern
        pattern_lines = lines[pattern_start_idx:pattern_end_idx + 1]
        pattern_content = ''.join(pattern_lines)
        pattern_length = len(pattern_lines)

        # Prepare new content
        new_lines = new_string.splitlines(keepends=True)
        if new_string and not new_string.endswith('\n') and new_lines:
            new_lines[-1] += '\n'

        # Find all occurrences of the pattern
        occurrences = []
        i = 0
        while i <= len(lines) - pattern_length:
            chunk = ''.join(lines[i:i + pattern_length])
            if chunk == pattern_content:
                occurrences.append(i)
                i += pattern_length  # Skip past this occurrence
            else:
                i += 1

        if not occurrences:
            return f"No occurrences found of the pattern from lines {pattern_start_line}-{pattern_end_line}."

        # Replace all occurrences from bottom to top to maintain indices
        result_lines = lines[:]
        for idx in reversed(occurrences):
            result_lines = result_lines[:idx] + new_lines + result_lines[idx + pattern_length:]

        write_file_lines(file_path, result_lines)

        # Convert 0-based indices to 1-based line numbers for reporting
        occurrence_lines = [f"lines {idx + 1}-{idx + pattern_length}" for idx in occurrences]

        return f"Successfully replaced {len(occurrences)} occurrence(s) of the pattern in '{file_path}'.\nLocations: {', '.join(occurrence_lines)}"

    except Exception as e:
        return f"Error: {str(e)}"

def move_lines_impl(
    file_path: str,
    source_start: int,
    source_end: int,
    target_line: int
) -> str:
    """
    Move lines from one location to another (cut & paste).

    Args:
        file_path: Path to the file
        source_start: Starting line number to move from (1-indexed)
        source_end: Ending line number to move from (1-indexed, inclusive)
        target_line: Line number where to move the lines (1-indexed)
    """
    try:
        lines = read_file_lines(file_path)
        total_lines = len(lines)

        # Validate line numbers
        if source_start < 1 or source_end < source_start or source_start > total_lines:
            return f"Error: Invalid source range. File has {total_lines} lines."
        if target_line < 1:
            return f"Error: target_line must be >= 1"

        # Adjust to 0-based indexing
        src_start_idx = source_start - 1
        src_end_idx = min(source_end, total_lines) - 1
        target_idx = target_line - 1

        # Check if target is within source range (invalid move)
        if src_start_idx <= target_idx <= src_end_idx + 1:
            return f"Error: Cannot move lines to a position within or immediately after the source range."

        # Extract lines to move
        lines_to_move = lines[src_start_idx:src_end_idx + 1]
        num_lines = len(lines_to_move)

        # Remove from source
        new_lines = lines[:src_start_idx] + lines[src_end_idx + 1:]

        # Adjust target index if it's after the source (since we removed lines)
        if target_idx > src_end_idx:
            adjusted_target_idx = target_idx - num_lines
        else:
            adjusted_target_idx = target_idx

        # Insert at target
        final_lines = new_lines[:adjusted_target_idx] + lines_to_move + new_lines[adjusted_target_idx:]

        write_file_lines(file_path, final_lines)

        return f"Successfully moved {num_lines} line(s) from lines {source_start}-{source_end} to line {target_line}."

    except Exception as e:
        return f"Error: {str(e)}"

# Create FastMCP server
mcp = FastMCP("Edit Operations Server")

@mcp.tool
def copy_paste_within_file(
    file_path: str,
    source_start: int,
    source_end: int,
    target_line: int,
    mode: Literal["insert", "replace"] = "insert"
) -> str:
    """
    Copy lines from one location to another within the same file.

    Args:
        file_path: Path to the file
        source_start: Starting line number to copy from (1-indexed)
        source_end: Ending line number to copy from (1-indexed, inclusive)
        target_line: Line number where to paste (1-indexed)
        mode: "insert" (push existing lines down) or "replace" (overwrite lines)

    Example:
        Copy lines 5-7 and insert at line 10:
        copy_paste_within_file("test.py", 5, 7, 10, "insert")
    """
    return copy_paste_within_file_impl(file_path, source_start, source_end, target_line, mode)

@mcp.tool
def copy_paste_between_files(
    source_file: str,
    source_start: int,
    source_end: int,
    target_file: str,
    target_line: int,
    mode: Literal["insert", "replace"] = "insert"
) -> str:
    """
    Copy lines from one file and paste into another file.

    Args:
        source_file: Path to the source file
        source_start: Starting line number to copy from (1-indexed)
        source_end: Ending line number to copy from (1-indexed, inclusive)
        target_file: Path to the target file
        target_line: Line number where to paste (1-indexed)
        mode: "insert" (push existing lines down) or "replace" (overwrite lines)

    Example:
        Copy lines 10-15 from file1.py and insert at line 5 in file2.py:
        copy_paste_between_files("file1.py", 10, 15, "file2.py", 5, "insert")
    """
    return copy_paste_between_files_impl(source_file, source_start, source_end, target_file, target_line, mode)

@mcp.tool
def replace_pattern_occurrences(
    file_path: str,
    pattern_start_line: int,
    pattern_end_line: int,
    new_string: str
) -> str:
    """
    Find all occurrences of a specific line range pattern and replace them all.
    Finds the exact content of lines [pattern_start:pattern_end] and replaces ALL occurrences in the file.

    Args:
        file_path: Path to the file
        pattern_start_line: Starting line number of the pattern (1-indexed)
        pattern_end_line: Ending line number of the pattern (1-indexed, inclusive)
        new_string: New content to replace all occurrences with

    Example:
        Replace all occurrences of the content in lines 5-7 with new content:
        replace_pattern_occurrences("test.py", 5, 7, "new content\nmore content\n")

    Returns:
        Number of replacements made and their locations
    """
    return replace_pattern_occurrences_impl(file_path, pattern_start_line, pattern_end_line, new_string)

@mcp.tool
def move_lines(
    file_path: str,
    source_start: int,
    source_end: int,
    target_line: int
) -> str:
    """
    Move lines from one location to another (cut & paste).

    Args:
        file_path: Path to the file
        source_start: Starting line number to move from (1-indexed)
        source_end: Ending line number to move from (1-indexed, inclusive)
        target_line: Line number where to move the lines (1-indexed)

    Example:
        Move lines 5-7 to line 15:
        move_lines("test.py", 5, 7, 15)
    """
    return move_lines_impl(file_path, source_start, source_end, target_line)

tool_functions = {
    "copy_paste_within_file": copy_paste_within_file,
    "copy_paste_between_files": copy_paste_between_files,
    "replace_pattern_occurrences": replace_pattern_occurrences,
    "move_lines": move_lines,
}

if __name__ == "__main__":
    mcp.run()
