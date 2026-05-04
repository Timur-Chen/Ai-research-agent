import logging

import requests

import config
from tools import register
from tools.schemas import ToolResult

logger = logging.getLogger(__name__)

TAVILY_URL = "https://api.tavily.com/search"


@register
def web_search_tool(query: str) -> ToolResult:
    """Search the web for current information and return the top three results."""
    try:
        logger.debug(f"web_search_tool: {query}")
        response = requests.post(
            TAVILY_URL,
            json={
                "api_key": config.TAVILY_API_KEY,
                "query": query,
                "max_results": 3,
            },
            timeout=10,
        )
        if response.status_code == 429:
            return ToolResult(
                success=False,
                output="",
                error="Rate limit exceeded. Try again in 60 seconds.",
            )
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return ToolResult(success=True, output="No results found for this query.")

        parts = []
        for r in results:
            parts.append(
                f"Title: {r.get('title', '')}\n"
                f"URL:   {r.get('url', '')}\n"
                f"Snippet: {r.get('content', '')}\n"
            )
        return ToolResult(success=True, output="\n".join(parts))

    except requests.exceptions.Timeout:
        return ToolResult(success=False, output="", error="Search request timed out.")
    except Exception as e:
        logger.warning(f"web_search_tool error: {e}")
        return ToolResult(success=False, output="", error=str(e))
