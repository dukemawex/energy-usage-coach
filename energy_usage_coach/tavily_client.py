from __future__ import annotations

import os
from typing import Protocol

from .models import Guideline


class GuidelinesRetriever(Protocol):
    def fetch_guidelines(self, topic: str, *, max_results: int = 5) -> list[Guideline]:
        ...


class TavilyGuidelinesRetriever:
    """Fetch energy efficiency guidance using Tavily search."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is required for TavilyGuidelinesRetriever")

    def fetch_guidelines(self, topic: str, *, max_results: int = 5) -> list[Guideline]:
        try:
            from tavily import TavilyClient
        except ImportError as exc:
            raise RuntimeError(
                "tavily-python is not installed. Install with `pip install .[integrations]`."
            ) from exc

        client = TavilyClient(api_key=self.api_key)
        response = client.search(
            query=f"Energy efficiency guidelines for {topic}",
            search_depth="advanced",
            max_results=max_results,
        )

        results = response.get("results", [])
        return [
            Guideline(
                title=item.get("title", "Untitled guideline"),
                url=item.get("url", ""),
                snippet=item.get("content", "").strip(),
            )
            for item in results
            if item.get("url")
        ]
