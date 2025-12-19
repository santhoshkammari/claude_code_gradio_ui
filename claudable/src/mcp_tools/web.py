# /home/ntlpt59/master/own/deep-researcher/src/tool_web.py
import asyncio
import base64
import os
import re
import json
import time
import logging
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import urllib.parse
from fastmcp import FastMCP

# Configure detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PlaywrightBrowser:
    """A simplified browser interaction manager using Playwright"""

    def __init__(self, headless=True):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None
        self.headless = headless
        self._initialized = False

    async def initialize(self):
        """Initialize the browser if not already done"""
        start_time = time.time()
        logger.debug("Starting browser initialization...")

        if self._initialized and self.page is not None:
            try:
                logger.debug(f"Browser already initialized, total time: {time.time() - start_time:.3f}s")
                return
            except:
                # Page/browser is closed, reinitialize
                logger.debug("Page/browser is closed, reinitializing...")
                self._initialized = False

        cleanup_start = time.time()
        await self.cleanup()
        logger.debug(f"Cleanup took: {time.time() - cleanup_start:.3f}s")

        playwright_start = time.time()
        self.playwright = await async_playwright().start()
        logger.debug(f"Playwright start took: {time.time() - playwright_start:.3f}s")

        browser_start = time.time()
        self.browser = await self.playwright.firefox.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled']
        )
        logger.debug(f"Browser launch took: {time.time() - browser_start:.3f}s")

        context_start = time.time()
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        logger.debug(f"Context creation took: {time.time() - context_start:.3f}s")

        page_start = time.time()
        self.page = await self.context.new_page()
        logger.debug(f"Page creation took: {type(self.page)}{time.time() - page_start:.3f}s")

        self._initialized = True
        logger.debug(f"TOTAL browser initialization took: {time.time() - start_time:.3f}s")

    async def navigate_to(self, url: str, wait_until: str = "domcontentloaded"):
        """Navigate to a URL with configurable wait_until parameter"""
        nav_start = time.time()
        logger.debug(f"Starting navigation to: {url}")

        init_start = time.time()
        await self.initialize()
        logger.debug(f"Initialize for navigation took: {time.time() - init_start:.3f}s")

        try:
            # Add retry logic for navigation
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    attempt_start = time.time()
                    logger.debug(f"Navigation attempt {attempt + 1}/{max_retries}")

                    goto_start = time.time()
                    await self.page.goto(url, wait_until=wait_until, timeout=5000)
                    logger.debug(f"Page.goto with wait_until='{wait_until}' took: {time.time() - goto_start:.3f}s")
                    logger.debug(f"Navigation attempt {attempt + 1} successful in: {time.time() - attempt_start:.3f}s")
                    break
                except Exception as e:
                    logger.error(
                        f"Navigation attempt {attempt + 1} failed after {time.time() - attempt_start:.3f}s: {str(e)}")
                    if attempt == max_retries - 1:
                        raise e
                    logger.debug(f"Retrying navigation in 2 seconds...")
                    await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"TOTAL navigation failed after {time.time() - nav_start:.3f}s: {str(e)}")
            raise e

        logger.debug(f"TOTAL navigation to {url} took: {time.time() - nav_start:.3f}s")

    async def get_page_html(self):
        """Get the HTML content of the current page"""
        try:
            content_start = time.time()
            logger.debug("Getting page HTML content...")
            content = await self.page.content()
            logger.debug(
                f"Getting page content took: {time.time() - content_start:.3f}s (content length: {len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            raise e

    async def cleanup(self):
        """Clean up resources without errors"""
        cleanup_start = time.time()
        logger.debug("Starting cleanup...")

        try:
            if self.page:
                page_close_start = time.time()
                await self.page.close()
                logger.debug(f"Page close took: {time.time() - page_close_start:.3f}s")
        except Exception as e:
            logger.warning(f"Page close error: {str(e)}")

        try:
            if self.context:
                context_close_start = time.time()
                await self.context.close()
                logger.debug(f"Context close took: {time.time() - context_close_start:.3f}s")
        except Exception as e:
            logger.warning(f"Context close error: {str(e)}")

        try:
            if self.browser:
                browser_close_start = time.time()
                await self.browser.close()
                logger.debug(f"Browser close took: {time.time() - browser_close_start:.3f}s")
        except Exception as e:
            logger.warning(f"Browser close error: {str(e)}")

        try:
            if self.playwright:
                playwright_stop_start = time.time()
                await self.playwright.stop()
                logger.debug(f"Playwright stop took: {time.time() - playwright_stop_start:.3f}s")
        except Exception as e:
            logger.warning(f"Playwright stop error: {str(e)}")

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        self._initialized = False

        logger.debug(f"TOTAL cleanup took: {time.time() - cleanup_start:.3f}s")


class WebSearchTool:
    """Web search implementation using Playwright"""

    def __init__(self, browser: PlaywrightBrowser = None):
        """Initialize the search agent"""
        self.browser = browser

    async def web_search(self, query: str, search_provider: str = 'bing', max_results: int = 10) -> str:
        """Perform a web search and return results"""
        search_start = time.time()
        logger.debug(f"Starting web search for query: '{query}' (num_results: {max_results})")

        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f'https://www.{search_provider}.com/search?q={encoded_query}'

            navigation_start = time.time()
            await self.browser.navigate_to(search_url)
            logger.debug(f"Navigation to search page took: {time.time() - navigation_start:.3f}s")

            # Get the HTML content
            html_start = time.time()
            html = await self.browser.get_page_html()
            logger.debug(f"Getting HTML took: {time.time() - html_start:.3f}s")

            # Extract search results
            extraction_start = time.time()
            if search_provider == 'bing':
                logger.debug("Extracting Bing results...")
                search_results = self.get_result_from_bing_html(html, max_results)
            else:
                logger.warning(f"Unknown search provider: {search_provider}")
                search_results = []

            logger.debug(f"Result extraction took: {time.time() - extraction_start:.3f}s")
            logger.debug(f"Found {len(search_results)} results")

            return search_results

        except Exception as e:
            logger.error(f"Search error after {time.time() - search_start:.3f}s: {str(e)}")
            return []
        
    @staticmethod
    def decode_bing_url(bing_url):
        """Decode Bing's wrapped URL to get the real URL"""
        try:
            if '/ck/a?' in bing_url:
                # Extract the 'u' parameter
                parsed = urllib.parse.urlparse(bing_url)
                query_params = urllib.parse.parse_qs(parsed.query)
                if 'u' in query_params:
                    encoded_url = query_params['u'][0]
                    # Remove the prefix 'a1' and decode base64
                    if encoded_url.startswith('a1'):
                        encoded_url = encoded_url[2:]
                    try:
                        decoded_bytes = base64.b64decode(encoded_url + '==')  # Add padding
                        return decoded_bytes.decode('utf-8')
                    except Exception:
                        pass
            return bing_url
        except Exception:
            return bing_url


    @staticmethod
    def get_result_from_bing_html(html: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Extract search results from Bing HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        result_elements = soup.find_all('li', class_='b_algo')

        for result_element in result_elements[:max_results]:
            title_header = result_element.find('h2')
            if title_header:
                title_link = title_header.find('a')
                if title_link and title_link.get('href'):
                    url = WebSearchTool.decode_bing_url(title_link['href'])
                    title = title_link.get_text(strip=True)

                    description = ""
                    caption_div = result_element.find('div', class_='b_caption')
                    if caption_div:
                        p_tag = caption_div.find('p')
                        if p_tag:
                            description = p_tag.get_text(strip=True)

                    results.append({
                        "url": url,
                        "title": title,
                        "description": description
                    })
        return results

# Global browser instance for reuse
_browser_instance = None


async def _get_browser():
    """Get or create browser instance"""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = PlaywrightBrowser()
        await _browser_instance.initialize()
    return _browser_instance


def search_web(query: str, max_results: int = 5) -> str:
    """Async wrapper for playwright web search - synchronous interface"""

    async def _search():
        browser = await _get_browser()
        search_tool = WebSearchTool(browser)
        return await search_tool.web_search(query, 'bing', max_results)

    return asyncio.run(_search())


async def async_web_search(query: str, max_results: int = 5):
    """Perform an async web search using Bing search engine.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        A list of search results with url, title, and description
    """
    browser = await _get_browser()
    search_tool = WebSearchTool(browser)
    return await search_tool.web_search(query, 'bing', max_results)


# Create FastMCP server
mcp = FastMCP("Web Search Server")

@mcp.tool
async def web_search(query: str, max_results: int = 5) -> dict:
    """Perform web search and return results"""
    try:
        results = await async_web_search(query, max_results)
        result ={"query": query, "results": results}
    except Exception as e:
        result= {"error": str(e)}
        
    return result


tool_functions = {
    "async_web_search": async_web_search,
}

if __name__ == '__main__':
    mcp.run()
