from abc import ABC, abstractmethod


class SearchProvider(ABC):
    """Abstract interface for web search providers."""

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
    ) -> list[dict]:
        """Search the web. Returns list of {title, url, snippet} dicts."""
        ...
