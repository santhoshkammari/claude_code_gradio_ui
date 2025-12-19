"""
Scrapling MCP Server - Comprehensive web scraping tools with anti-bot bypass capabilities.

Provides 6 powerful tools:
- get: Fast HTTP requests with browser fingerprint impersonation
- bulk_get: Async version for scraping multiple URLs simultaneously
- fetch: Dynamic content scraping with Chromium/Chrome browser
- bulk_fetch: Async version for fetching multiple URLs in parallel
- stealthy_fetch: Bypass Cloudflare Turnstile using Camoufox browser
- bulk_stealthy_fetch: Async version for stealthy scraping of multiple URLs

Based on official Scrapling MCP server implementation.
"""

from asyncio import gather
from typing import Optional, Tuple, Dict, List, Any
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from scrapling.core.shell import Convertor
from scrapling.engines.toolbelt.custom import Response as _ScraplingResponse
from scrapling.engines.static import ImpersonateType
from scrapling.fetchers import (
    Fetcher,
    FetcherSession,
    DynamicFetcher,
    AsyncDynamicSession,
    StealthyFetcher,
    AsyncStealthySession,
)
from scrapling.core._types import extraction_types, SelectorWaitStates

mcp = FastMCP("Scrapling Web Scraper")


class ResponseModel(BaseModel):
    """Request's response information structure."""
    status: int = Field(description="The status code returned by the website.")
    content: list[str] = Field(description="The content as Markdown/HTML or the text content of the page.")
    url: str = Field(description="The URL given by the user that resulted in this response.")


def _ContentTranslator(content, page: _ScraplingResponse) -> ResponseModel:
    """Convert a content generator to ResponseModel."""
    return ResponseModel(status=page.status, content=[result for result in content], url=page.url)


# ============================================================================
# Basic HTTP Scraping Tools
# ============================================================================

@mcp.tool
def get(
    url: str,
    impersonate: str = "chrome",
    extraction_type: str = "markdown",
    css_selector: Optional[str] = None,
    main_content_only: bool = True,
    timeout: Optional[int] = 30,
    retries: Optional[int] = 3,
    retry_delay: Optional[int] = 1,
    proxy: Optional[str] = None,
) -> ResponseModel:
    """Make GET HTTP request with browser fingerprint impersonation.

    Best for: Static websites with low-mid protection levels.

    Args:
        url: The URL to request
        impersonate: Browser to impersonate (default: chrome)
        extraction_type: Content type - "markdown", "html", or "text" (default: markdown)
        css_selector: CSS selector to extract specific content
        main_content_only: Extract only main content (default: True)
        timeout: Request timeout in seconds (default: 30)
        retries: Number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 1)
        proxy: Proxy URL (format: "http://username:password@host:port")

    Returns:
        ResponseModel with status, content list, and final URL
    """
    page = Fetcher.get(
        url,
        proxy=proxy,
        timeout=timeout,
        retries=retries,
        retry_delay=retry_delay,
        impersonate=impersonate,
    )
    return _ContentTranslator(
        Convertor._extract_content(
            page,
            css_selector=css_selector,
            extraction_type=extraction_type,
            main_content_only=main_content_only,
        ),
        page,
    )


@mcp.tool
async def bulk_get(
    urls: Tuple[str, ...],
    impersonate: str = "chrome",
    extraction_type: str = "markdown",
    css_selector: Optional[str] = None,
    main_content_only: bool = True,
    timeout: Optional[int] = 30,
    retries: Optional[int] = 3,
    retry_delay: Optional[int] = 1,
    proxy: Optional[str] = None,
) -> List[ResponseModel]:
    """Make GET HTTP requests to multiple URLs concurrently.

    Best for: Scraping multiple static pages in parallel.

    Args:
        urls: Tuple of URLs to request
        impersonate: Browser to impersonate (default: chrome)
        extraction_type: Content type - "markdown", "html", or "text" (default: markdown)
        css_selector: CSS selector to extract specific content
        main_content_only: Extract only main content (default: True)
        timeout: Request timeout in seconds (default: 30)
        retries: Number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 1)
        proxy: Proxy URL (format: "http://username:password@host:port")

    Returns:
        List of ResponseModel objects, one for each URL
    """
    async with FetcherSession() as session:
        tasks: List[Any] = [
            session.get(
                url,
                proxy=proxy,
                timeout=timeout,
                retries=retries,
                retry_delay=retry_delay,
                impersonate=impersonate,
            )
            for url in urls
        ]
        responses = await gather(*tasks)
        return [
            _ContentTranslator(
                Convertor._extract_content(
                    page,
                    css_selector=css_selector,
                    extraction_type=extraction_type,
                    main_content_only=main_content_only,
                ),
                page,
            )
            for page in responses
        ]


# ============================================================================
# Dynamic Content Scraping Tools (Playwright/Chromium)
# ============================================================================

@mcp.tool
async def fetch(
    url: str,
    extraction_type: str = "markdown",
    css_selector: Optional[str] = None,
    main_content_only: bool = True,
    headless: bool = True,
    wait: int = 0,
    timeout: int = 30000,
    wait_selector: Optional[str] = None,
    network_idle: bool = False,
    disable_resources: bool = False,
    proxy: Optional[str] = None,
) -> ResponseModel:
    """Use Playwright/Chromium browser to fetch dynamic content.

    Best for: JavaScript-heavy websites, SPAs, dynamic content.

    Args:
        url: The URL to request
        extraction_type: Content type - "markdown", "html", or "text" (default: markdown)
        css_selector: CSS selector to extract specific content
        main_content_only: Extract only main content (default: True)
        headless: Run browser in headless mode (default: True)
        wait: Wait time in milliseconds after page load (default: 0)
        timeout: Operation timeout in milliseconds (default: 30000)
        wait_selector: Wait for specific CSS selector before extracting
        network_idle: Wait for network to be idle (default: False)
        disable_resources: Disable images/fonts/media for speed boost (default: False)
        proxy: Proxy URL or dict with 'server', 'username', 'password'

    Returns:
        ResponseModel with status, content list, and final URL
    """
    page = await DynamicFetcher.async_fetch(
        url,
        wait=wait,
        proxy=proxy,
        timeout=timeout,
        headless=headless,
        network_idle=network_idle,
        wait_selector=wait_selector,
        disable_resources=disable_resources,
    )
    return _ContentTranslator(
        Convertor._extract_content(
            page,
            css_selector=css_selector,
            extraction_type=extraction_type,
            main_content_only=main_content_only,
        ),
        page,
    )


@mcp.tool
async def bulk_fetch(
    urls: Tuple[str, ...],
    extraction_type: str = "markdown",
    css_selector: Optional[str] = None,
    main_content_only: bool = True,
    headless: bool = True,
    wait: int = 0,
    timeout: int = 30000,
    wait_selector: Optional[str] = None,
    network_idle: bool = False,
    disable_resources: bool = False,
    proxy: Optional[str] = None,
) -> List[ResponseModel]:
    """Use Playwright to fetch multiple URLs in parallel browser tabs.

    Best for: Scraping multiple dynamic pages concurrently.

    Args:
        urls: Tuple of URLs to request
        extraction_type: Content type - "markdown", "html", or "text" (default: markdown)
        css_selector: CSS selector to extract specific content
        main_content_only: Extract only main content (default: True)
        headless: Run browser in headless mode (default: True)
        wait: Wait time in milliseconds after page load (default: 0)
        timeout: Operation timeout in milliseconds (default: 30000)
        wait_selector: Wait for specific CSS selector before extracting
        network_idle: Wait for network to be idle (default: False)
        disable_resources: Disable images/fonts/media for speed boost (default: False)
        proxy: Proxy URL or dict with 'server', 'username', 'password'

    Returns:
        List of ResponseModel objects, one for each URL
    """
    async with AsyncDynamicSession(
        wait=wait,
        proxy=proxy,
        timeout=timeout,
        headless=headless,
        max_pages=len(urls),
        network_idle=network_idle,
        wait_selector=wait_selector,
        disable_resources=disable_resources,
    ) as session:
        tasks = [session.fetch(url) for url in urls]
        responses = await gather(*tasks)
        return [
            _ContentTranslator(
                Convertor._extract_content(
                    page,
                    css_selector=css_selector,
                    extraction_type=extraction_type,
                    main_content_only=main_content_only,
                ),
                page,
            )
            for page in responses
        ]


# ============================================================================
# Stealth Scraping Tools (Camoufox - Cloudflare Bypass)
# ============================================================================

@mcp.tool
async def stealthy_fetch(
    url: str,
    extraction_type: str = "markdown",
    css_selector: Optional[str] = None,
    main_content_only: bool = True,
    headless: bool = True,
    solve_cloudflare: bool = False,
    wait: int = 0,
    timeout: int = 30000,
    wait_selector: Optional[str] = None,
    network_idle: bool = False,
    disable_resources: bool = False,
    proxy: Optional[str] = None,
    humanize: bool = True,
) -> ResponseModel:
    """Use Camoufox browser to bypass Cloudflare Turnstile and anti-bot protections.

    Best for: High-protection websites, Cloudflare-protected sites.
    Note: Slower than other tools but most effective against bot detection.

    Args:
        url: The URL to request
        extraction_type: Content type - "markdown", "html", or "text" (default: markdown)
        css_selector: CSS selector to extract specific content
        main_content_only: Extract only main content (default: True)
        headless: Run browser in headless mode (default: True)
        solve_cloudflare: Auto-solve Cloudflare challenges (default: False)
        wait: Wait time in milliseconds after page load (default: 0)
        timeout: Operation timeout in milliseconds (default: 30000)
        wait_selector: Wait for specific CSS selector before extracting
        network_idle: Wait for network to be idle (default: False)
        disable_resources: Disable images/fonts/media for speed boost (default: False)
        proxy: Proxy URL or dict with 'server', 'username', 'password'
        humanize: Humanize cursor movement (default: True)

    Returns:
        ResponseModel with status, content list, and final URL
    """
    page = await StealthyFetcher.async_fetch(
        url,
        wait=wait,
        proxy=proxy,
        timeout=timeout,
        headless=headless,
        humanize=humanize,
        network_idle=network_idle,
        wait_selector=wait_selector,
        solve_cloudflare=solve_cloudflare,
        disable_resources=disable_resources,
    )
    return _ContentTranslator(
        Convertor._extract_content(
            page,
            css_selector=css_selector,
            extraction_type=extraction_type,
            main_content_only=main_content_only,
        ),
        page,
    )


@mcp.tool
async def bulk_stealthy_fetch(
    urls: Tuple[str, ...],
    extraction_type: str = "markdown",
    css_selector: Optional[str] = None,
    main_content_only: bool = True,
    headless: bool = True,
    solve_cloudflare: bool = False,
    wait: int = 0,
    timeout: int = 30000,
    wait_selector: Optional[str] = None,
    network_idle: bool = False,
    disable_resources: bool = False,
    proxy: Optional[str] = None,
    humanize: bool = True,
) -> List[ResponseModel]:
    """Use Camoufox browser to fetch multiple protected URLs in parallel.

    Best for: Scraping multiple high-protection pages concurrently.
    Note: Slower than other tools but most effective against bot detection.

    Args:
        urls: Tuple of URLs to request
        extraction_type: Content type - "markdown", "html", or "text" (default: markdown)
        css_selector: CSS selector to extract specific content
        main_content_only: Extract only main content (default: True)
        headless: Run browser in headless mode (default: True)
        solve_cloudflare: Auto-solve Cloudflare challenges (default: False)
        wait: Wait time in milliseconds after page load (default: 0)
        timeout: Operation timeout in milliseconds (default: 30000)
        wait_selector: Wait for specific CSS selector before extracting
        network_idle: Wait for network to be idle (default: False)
        disable_resources: Disable images/fonts/media for speed boost (default: False)
        proxy: Proxy URL or dict with 'server', 'username', 'password'
        humanize: Humanize cursor movement (default: True)

    Returns:
        List of ResponseModel objects, one for each URL
    """
    async with AsyncStealthySession(
        wait=wait,
        proxy=proxy,
        timeout=timeout,
        headless=headless,
        humanize=humanize,
        max_pages=len(urls),
        network_idle=network_idle,
        wait_selector=wait_selector,
        solve_cloudflare=solve_cloudflare,
        disable_resources=disable_resources,
    ) as session:
        tasks = [session.fetch(url) for url in urls]
        responses = await gather(*tasks)
        return [
            _ContentTranslator(
                Convertor._extract_content(
                    page,
                    css_selector=css_selector,
                    extraction_type=extraction_type,
                    main_content_only=main_content_only,
                ),
                page,
            )
            for page in responses
        ]


if __name__ == "__main__":
    mcp.run()
