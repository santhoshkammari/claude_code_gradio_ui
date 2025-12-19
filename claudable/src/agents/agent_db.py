# Import DB-based markdown tools
import sqlite3
from pathlib import Path
from src.ai.agent import agent
from src.ai.lm import LM
from src.logger.logger import get_logger
from src.mcp_tools.markdown.markdown_db import MarkdownTool

logger = get_logger(__name__, level="DEBUG")


# =============================================================================
# Agent Implementations
# =============================================================================

async def doc_agent(db_id: int, query: str, lm: LM) -> str:
    """
    DocAgent - Analyzes markdown content from database using markdown tools

    Args:
        db_id: Database ID containing the fetched content
        query: Original user query for context
        lm: Language model instance

    Returns:
        Analysis result as string
    """
    # Get database connection
    db_path = "search_cache.db"
    conn = sqlite3.connect(str(db_path))

    markdown_tool = MarkdownTool(conn, db_id)

    system_prompt = f"""You are a document analysis expert operating over markdown content stored in a database.

You have been given a database ID ({db_id}) that contains markdown content fetched from the web.
Your goal is to analyze this document and answer the user’s query accurately and comprehensively:

User query:
"{query}"

────────────────────────────────────────
MANDATORY TOOL USAGE RULES
────────────────────────────────────────
You MUST use the provided markdown analysis tools.
Do NOT answer from prior knowledge or assumptions.
All insights must be grounded in tool outputs.

Follow this workflow strictly:
1. Start with `get_overview` OR `get_headers` to understand the document structure.
2. Identify relevant sections, tables, lists, or code blocks based on the query.
3. Use targeted tools (headers, tables, paragraphs, lists, code, links) to extract exact evidence.
4. Synthesize findings into a clear, well-structured answer.
5. If information is missing, explicitly say so.

────────────────────────────────────────
AVAILABLE TOOLS
────────────────────────────────────────

Structural & Navigation:
- get_overview  
→ Eagle-eye view of the entire document (structure, stats, intro, tables, code, lists)

- get_headers  
→ All headers with hierarchy and line numbers

- get_header_by_line(line_number: int)  
→ Full section content under a specific header

Intro & Narrative Content:
- get_intro  
→ Extracts abstract / introduction / inferred opening section

- get_paragraphs  
→ All paragraphs with line numbers

Lists & Bullet Content:
- get_lists  
→ Ordered and unordered lists with line numbers and items

Tables:
- get_tables_metadata  
→ Summary of all tables (line number, columns, rows, header preview)

- get_table_by_line(line_number: int)  
→ Fully formatted table extracted from a specific line

Code & Technical Content:
- get_code_blocks  
→ All code blocks with language and line ranges

Links & References:
- get_links  
→ All external HTTP/HTTPS links with line numbers

────────────────────────────────────────
ANALYSIS GUIDELINES
────────────────────────────────────────
- Prefer precise extraction over summarization when possible.
- Reference line numbers or headers implicitly via tool usage.
- When tables or code blocks exist, inspect them before concluding.
- If multiple sections are relevant, compare them explicitly.
- Be concise but thorough — clarity beats verbosity.

────────────────────────────────────────
FINAL OUTPUT
────────────────────────────────────────
Produce a clear, structured answer that directly addresses the user query.
Base every claim on extracted content.
If the document does not contain enough information, state that explicitly.
"""
    tools = [
        markdown_tool.get_overview,
        markdown_tool.get_intro,
        markdown_tool.get_headers,
        # markdown_tool.get_links,
        # markdown_tool.get_code_blocks,
        markdown_tool.get_tables_metadata,
        markdown_tool.get_table_by_line,
        markdown_tool.get_header_by_line,
        # markdown_tool.get_lists,
        # markdown_tool.get_paragraphs,

    ]

    history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze the content in database ID {db_id} and extract information relevant to: {query}"}
    ]

    result = await agent(
        lm=lm,
        history=history,
        tools=tools,
        max_iterations=25,
        logger=logger
    )


    conn.close()
    return result['final_response']



if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Run DocAgent on a markdown DB entry")
    parser.add_argument("--db-id", type=int, required=True, help="Database ID containing markdown content")
    parser.add_argument("--query", type=str, required=True, help="User query to analyze against the document")
    parser.add_argument(
        "--api-base",
        type=str,
        default="http://192.168.170.76:8000",
        help="LM API base URL"
    )

    args = parser.parse_args()

    lm = LM(api_base=args.api_base)

    result = asyncio.run(
        doc_agent(
            db_id=args.db_id,
            query=args.query,
            lm=lm
        )
    )

    print(result)
