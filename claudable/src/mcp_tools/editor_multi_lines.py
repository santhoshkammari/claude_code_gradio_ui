from fastmcp import FastMCP
import os
from typing import Optional, List, Dict, Any


mcp = FastMCP("File Tools Optimized Server")

@mcp.tool
def replace_str_in_file(file_path: str, edits: List[Dict[str, Any]]) -> str:
    """
    Replace multiple sections in a file with new content.
    
    Args:
        file_path: Path to the file
        edits: List of dictionaries, each containing:
            - line_start(int): Starting line number (1-indexed)
            - line_end(int): Ending line number (1-indexed, inclusive)
            - new_string(str): New content to replace with
    
    Edits are applied from bottom to top to maintain line number validity.

    Example:
        edits = [
            {"line_start": 5, "line_end": 7, "new_string": "new content for lines 5-7\\n"},
            {"line_start": 10, "line_end": 10, "new_string": "replacement for line 10\\n"}
        ]
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist"
    if not os.path.isfile(file_path):
        return f"Error: '{file_path}' is not a file"
    
    # Validate edits
    for i, edit in enumerate(edits):
        if 'line_start' not in edit or 'line_end' not in edit or 'new_string' not in edit:
            return f"Error: Edit {i+1} missing required fields (line_start, line_end, new_string)"
        
        line_start = edit['line_start']
        line_end = edit['line_end']
        
        if line_start < 1 or line_end < line_start:
            return f"Error: Edit {i+1}: line_start must be >= 1 and line_end must be >= line_start"
    
    # Sort edits by line_start in descending order (bottom to top)
    sorted_edits = sorted(edits, key=lambda x: x['line_start'], reverse=True)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = []
        
        # Apply each edit from bottom to top
        for edit in sorted_edits:
            line_start = edit['line_start']
            line_end = edit['line_end']
            new_string = edit['new_string']
            
            # Adjust to 0-based indexing
            start_idx = line_start - 1
            end_idx = line_end - 1
            
            # Check if line numbers are within bounds
            if start_idx >= len(lines) or end_idx >= len(lines):
                return f"Error: Lines {line_start}-{line_end} out of range. File has {len(lines)} lines."
            # Split new_string into lines, preserving EXACTLY as provided
            if new_string:
                new_lines = new_string.splitlines(keepends=True)
            else:
                new_lines = []
            
            # Replace the lines
            lines = lines[:start_idx] + new_lines + lines[end_idx+1:]
            lines = lines[:start_idx] + new_lines + lines[end_idx+1:]
            
            results.append(f"Replaced lines {line_start}-{line_end}")
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return f"Successfully applied {len(edits)} edit(s) to '{file_path}':\n" + "\n".join(results)
    
    except Exception as e:
        return f"Error replacing content in file '{file_path}': {str(e)}"


if __name__ == "__main__":
    mcp.run()
