from typing import Any, AsyncIterator
from app.llm.base import LLMClient
from app.core.settings import get_settings


class AnthropicClient(LLMClient):
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL

    async def _get_client(self):
        import anthropic
        return anthropic.AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> dict:
        client = await self._get_client()
        kwargs = {
            "model": self.model,
            "max_tokens": options.pop("max_tokens", 4096),
            "messages": messages,
            **options,
        }
        response = await client.messages.create(**kwargs)
        content = response.content[0].text if response.content else ""
        if response_schema and content:
            import json
            return json.loads(content)
        return {"content": content}

    async def stream(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> AsyncIterator[str]:
        client = await self._get_client()
        kwargs = {
            "model": self.model,
            "max_tokens": options.pop("max_tokens", 4096),
            "messages": messages,
            "stream": True,
            **options,
        }
        async with client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, texts: list[str], **options: Any) -> list[list[float]]:
        raise NotImplementedError("Anthropic does not support embeddings. Configure a separate embedding provider.")
