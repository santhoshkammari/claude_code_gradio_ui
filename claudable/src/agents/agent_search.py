"""
Search Agent - Multi-agent system for web search, content fetching, and analysis

Flow:
1. Async web search (returns multiple links)
2. Parallel fetch for all links and store in SQLite
3. Pass DB IDs to DocAgent in parallel for analysis
4. Synthesize all analyses into final answer
"""

import asyncio
import sqlite3
from pathlib import Path
from typing import List, Dict
import json

from src.ai import agent,LM
from src.mcp_tools.web import async_web_search
from src.logger.logger import get_logger

# Import scrapling fetchers for fallback mechanism
from scrapling import Fetcher, DynamicFetcher, StealthyFetcher
from scrapling.core.shell import Convertor

logger = get_logger(__name__,level="CRITICAL")

# Configuration
MAX_SEARCH_RESULTS = 4
DB_PATH = "search_cache.db"


# =============================================================================
# Database Setup
# =============================================================================

def init_db():
    """Initialize SQLite database with link and text columns"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT NOT NULL,
            text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_to_db(link: str, text: str) -> int:
    """Save fetched content to database and return row ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO search_results (link, text) VALUES (?, ?)', (link, text))
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def get_from_db(row_id: int) -> Dict[str, str]:
    """Get link and text from database by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT link, text FROM search_results WHERE id = ?', (row_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"link": result[0], "text": result[1]}
    return None


# Import DB-based markdown tools
from src.mcp_tools.markdown.markdown_db import MarkdownTool


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
Your goal is to analyze this document and answer the user's query accurately and comprehensively:

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


async def final_answer_agent(doc_analyses: List[Dict[str, str]], query: str, lm: LM) -> str:
    """
    FinalAnswerAgent - Synthesizes multiple document analyses into coherent answer

    Args:
        doc_analyses: List of dicts with 'link' and 'analysis' keys
        query: Original user query
        lm: Language model instance

    Returns:
        Final synthesized answer as string
    """
    system_prompt = """You are a synthesis expert. You receive multiple document analyses from different web sources and must create a comprehensive, coherent answer.

Your task:
1. Identify key information from each source
2. Find common themes and patterns
3. Resolve any contradictions
4. Synthesize into a well-structured, informative answer
5. Cite sources when making specific claims

Provide a clear, concise, and accurate answer based on all the analyzed documents."""

    # Build context from all analyses
    analyses_context = "\n\n".join([
        f"SOURCE: {item['link']}\nANALYSIS:\n{item['analysis']}\n---"
        for item in doc_analyses
    ])

    history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""Original Query: {query}

Here are the analyses from {len(doc_analyses)} different sources:

{analyses_context}

Please synthesize these analyses into a comprehensive answer to the query."""}
    ]

    result = await agent(
        lm=lm,
        history=history,
        tools=[],
        max_iterations=3
    )

    return result['final_response']


# =============================================================================
# Main Search Agent Function
# =============================================================================

async def search_agent(query: str, max_results: int = MAX_SEARCH_RESULTS) -> str:
    """
    Main search agent function - orchestrates web search, fetching, analysis, and synthesis

    Args:
        query: User's search query
        max_results: Maximum number of search results to process (default: 4)

    Returns:
        Final answer as string
    """
    # Initialize database
    init_db()

    # Initialize LM
    lm = LM(model="vllm:", api_base="http://192.168.170.76:8000")

    print(f"🔍 Searching for: {query}")

    # Step 1: Async web search
    search_results = await async_web_search(query, max_results=max_results)
    print(f"✓ Found {len(search_results)} search results")

    if not search_results:
        return "No search results found for the query."

    # Step 2: Parallel fetch and store in DB with fallback mechanism
    async def fetch_and_store(result: Dict) -> Dict:
        """Fetch content with fallback: get -> fetch -> stealthy_fetch

        Tries three methods in order:
        1. get: Fast HTTP with browser fingerprint impersonation
        2. fetch: Dynamic content with Playwright/Chromium
        3. stealthy_fetch: Cloudflare bypass with Camoufox
        """
        url = result['url']
        text = None
        method_used = None

        # Method 1: Try basic HTTP get with browser impersonation
        try:
            print(f"📥 Trying GET: {url}")
            page = Fetcher.get(url, timeout=30, retries=2, retry_delay=1)

            if page.status == 200:
                content = list(Convertor._extract_content(
                    page,
                    extraction_type="markdown",
                    main_content_only=True,
                ))
                text = "".join(content)

                # Validate content is not empty
                if text and text.strip():
                    method_used = "get"
                    print(f"✓ GET succeeded for {url}")
                else:
                    print(f"⚠ GET returned empty content for {url}")
                    text = None
        except Exception as e:
            print(f"✗ GET failed for {url}: {str(e)}")

        # Method 2: Try dynamic fetch with Playwright if GET failed
        if not text:
            try:
                print(f"📥 Trying FETCH (Playwright): {url}")
                page = await DynamicFetcher.async_fetch(
                    url,
                    headless=True,
                    timeout=30000,
                    wait=1000,  # Wait 1s after page load
                )

                if page.status == 200:
                    content = list(Convertor._extract_content(
                        page,
                        extraction_type="markdown",
                        main_content_only=True,
                    ))
                    text = "".join(content)

                    if text and text.strip():
                        method_used = "fetch"
                        print(f"✓ FETCH succeeded for {url}")
                    else:
                        print(f"⚠ FETCH returned empty content for {url}")
                        text = None
            except Exception as e:
                print(f"✗ FETCH failed for {url}: {str(e)}")

        # Method 3: Try stealthy fetch with Camoufox if both failed
        if not text:
            try:
                print(f"📥 Trying STEALTHY_FETCH (Camoufox): {url}")
                page = await StealthyFetcher.async_fetch(
                    url,
                    headless=True,
                    timeout=45000,
                    wait=2000,  # Wait 2s after page load
                    solve_cloudflare=True,  # Auto-solve Cloudflare challenges
                    humanize=True,
                )

                if page.status == 200:
                    content = list(Convertor._extract_content(
                        page,
                        extraction_type="markdown",
                        main_content_only=True,
                    ))
                    text = "".join(content)

                    if text and text.strip():
                        method_used = "stealthy_fetch"
                        print(f"✓ STEALTHY_FETCH succeeded for {url}")
                    else:
                        print(f"⚠ STEALTHY_FETCH returned empty content for {url}")
                        text = None
            except Exception as e:
                print(f"✗ STEALTHY_FETCH failed for {url}: {str(e)}")

        # Store result in database
        if text and text.strip():
            db_id = save_to_db(url, text)
            print(f"✓ Stored in DB with ID: {db_id} (method: {method_used})")
            return {"db_id": db_id, "link": url, "method": method_used}
        else:
            # All methods failed - store error message
            error_msg = f"Failed to fetch content: All methods (get, fetch, stealthy_fetch) failed or returned empty content"
            db_id = save_to_db(url, error_msg)
            print(f"✗ All methods failed for {url}, stored error with ID: {db_id}")
            return {"db_id": db_id, "link": url, "method": "failed"}

    fetch_tasks = [fetch_and_store(result) for result in search_results]
    db_entries = await asyncio.gather(*fetch_tasks)

    print(f"✓ Fetched and stored {len(db_entries)} documents")

    # Step 3: Parallel DocAgent analysis for all DB entries
    async def analyze_document(entry: Dict) -> Dict:
        """Run DocAgent on a DB entry"""
        # Skip analysis for failed fetches
        if entry.get('method') == 'failed':
            print(f"⊘ Skipping analysis for failed fetch: {entry['link']}")
            return {"link": entry['link'], "analysis": "Failed to fetch content from this URL."}

        print(f"📖 Analyzing DB ID: {entry['db_id']} ({entry['link']}) [method: {entry.get('method', 'unknown')}]")
        try:
            analysis = await doc_agent(entry['db_id'], query, lm)
            print(f"✓ Analysis complete for DB ID: {entry['db_id']}")
            return {"link": entry['link'], "analysis": analysis}
        except Exception as e:
            print(f"✗ Analysis failed for DB ID: {entry['db_id']}: {str(e)}")
            return {"link": entry['link'], "analysis": f"Analysis failed: {str(e)}"}

    analysis_tasks = [analyze_document(entry) for entry in db_entries]
    doc_analyses = await asyncio.gather(*analysis_tasks)

    print(f"✓ Completed {len(doc_analyses)} document analyses")
    for doc in doc_analyses:
        print(f"--- Analysis for {doc['link']} ---\n{doc['analysis']}\n")

    # Step 4: Final synthesis
    print("🔮 Synthesizing final answer...")
    final_answer = await final_answer_agent(doc_analyses, query, lm)

    print("✓ Search agent complete!")
    return final_answer


# =============================================================================
# Example Usage
# =============================================================================

import argparse
import asyncio

async def main(query: str, max_results: int):
    """Example usage of search_agent"""
    result = await search_agent(query, max_results=max_results)

    print("\n" + "=" * 80)
    print("FINAL ANSWER:")
    print("=" * 80)
    print(result)
    print("=" * 80)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run search_agent with a query"
    )
    parser.add_argument(
        "--query",
        type=str,
        default="What is the latest in AI agent frameworks?",
        help="Search query string",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=4,
        help="Maximum number of results to return",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.query, args.max_results))
