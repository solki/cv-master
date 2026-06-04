from app.search.base import SearchProvider
from app.core.settings import get_settings


class TavilySearchProvider(SearchProvider):
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.TAVILY_API_KEY

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
    ) -> list[dict]:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_domains": include_domains or [],
                    "exclude_domains": exclude_domains or [],
                },
            )
            response.raise_for_status()
            data = response.json()
            return [
                {"title": r["title"], "url": r["url"], "snippet": r.get("content", "")}
                for r in data.get("results", [])
            ]
