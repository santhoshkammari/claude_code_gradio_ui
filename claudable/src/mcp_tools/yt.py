import json
from typing import Optional
from youtube_search import YoutubeSearch
from fastmcp import FastMCP

mcp = FastMCP("YouTube Search")

@mcp.tool
def search_youtube(query: str, max_results: Optional[int] = 10):
    """
    Searches YouTube for a given query.

    Args:
        query: The search query.
        max_results: The maximum number of results to return.
    """
    results = YoutubeSearch(query, max_results=max_results).to_json()
    data = json.loads(results)
    url_list = [("https://www.youtube.com" + video["url_suffix"]) for video in data["videos"]]
    return url_list

if __name__ == "__main__":
    mcp.run()