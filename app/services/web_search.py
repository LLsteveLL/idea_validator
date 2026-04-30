"""Web search helpers for market and competitor analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """Normalized search result."""

    title: str
    url: str
    content: str


class SearchUnavailableError(Exception):
    """Raised when search cannot run because it is not configured."""


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    """Send a JSON POST request using the standard library."""
    request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urlopen(request, timeout=settings.request_timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def tavily_search(query: str, max_results: int | None = None) -> list[SearchResult]:
    """Run a Tavily search and normalize the response."""
    if not settings.tavily_api_key:
        raise SearchUnavailableError("TAVILY_API_KEY is not set.")

    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "max_results": max_results or settings.search_results_limit,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
    }
    headers = {"Content-Type": "application/json"}

    try:
        data = _post_json("https://api.tavily.com/search", payload, headers)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise SearchUnavailableError(str(exc)) from exc

    results = []
    for item in data.get("results", []):
        results.append(
            SearchResult(
                title=item.get("title", "").strip(),
                url=item.get("url", "").strip(),
                content=item.get("content", "").strip(),
            )
        )
    return results


def search_web(query: str, max_results: int | None = None) -> list[SearchResult]:
    """Run the configured search provider."""
    provider = settings.search_provider.strip().lower()
    if provider == "tavily":
        return tavily_search(query, max_results=max_results)
    raise SearchUnavailableError(f"Unsupported search provider: {settings.search_provider}")


def format_search_context(results: list[SearchResult]) -> str:
    """Convert normalized search results into a compact prompt context block."""
    if not results:
        return "No external search results were available."

    lines: list[str] = []
    for index, result in enumerate(results, start=1):
        lines.append(f"[{index}] {result.title}")
        lines.append(f"URL: {result.url}")
        lines.append(f"Summary: {result.content}")
    return "\n".join(lines)
