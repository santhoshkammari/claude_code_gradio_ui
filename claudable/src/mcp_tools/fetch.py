import json
import asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import asdict

from scrapling.fetchers import Fetcher
from scrapling.core.shell import Convertor
from fastmcp import FastMCP

SYSTEM_PROMPT = """You are a minimal web fetching assistant. Expose only the web_fetch tool for saving a URL to Markdown using a simple GET-based extractor."""

# Create FastMCP server
mcp = FastMCP("Scrapling Fetch Server")


def scrapling_get(
    url: str,
    impersonate: Optional[str] = "chrome",
    extraction_type: str = "markdown",
    css_selector: Optional[str] = None,
    main_content_only: bool = True,
    timeout: Optional[int] = 30,
    retries: Optional[int] = 3,
    retry_delay: Optional[int] = 1,
) -> Dict:
    """Make a simple GET request and extract content.

    Args:
        url: The URL to fetch
        impersonate: Browser to impersonate (default: chrome)
        extraction_type: Type of content extraction (default: markdown)
        css_selector: CSS selector for specific content extraction
        main_content_only: Extract only main content (default: True)
        timeout: Request timeout in seconds (default: 30)
        retries: Number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 1)

    Returns:
        Dict with status, content, and url
    """
    try:
        page = Fetcher.get(
            url,
            timeout=timeout,
            retries=retries,
            retry_delay=retry_delay,
            impersonate=impersonate,
        )
        content = list(Convertor._extract_content(
            page,
            css_selector=css_selector,
            extraction_type=extraction_type,
            main_content_only=main_content_only,
        ))
        return {"status": page.status, "content": content, "url": page.url}
    except Exception as e:
        return {"status": 0, "content": [f"Error: {str(e)}"], "url": url}


# Removed bulk and browser-based MCP tools to keep only web_fetch


 


 


 


 


# Removed sync wrappers for deleted async tools


@mcp.tool
def web_fetch_content(url: str):
    """Fetch URL and return Markdown content without saving.

    Returns:
    - On success: a dict with keys `status`, `url`, and `markdown` (string).
    - On failure: a dict with `status` and `error` message.
    """
    result = scrapling_get(url, extraction_type="markdown")
    if not result["content"] or result["status"] != 200:
        return {"status": result.get("status", 0), "error": "Failed to fetch content", "url": url}
    return {"status": result["status"], "url": result["url"], "markdown": "".join(result["content"]) }


# Only expose web_fetch in the registry
tool_functions = {"web_fetch_content": web_fetch_content}

if __name__ == '__main__':
    mcp.run()
