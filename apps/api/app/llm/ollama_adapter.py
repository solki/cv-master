from typing import Any, AsyncIterator
from app.llm.base import LLMClient
from app.core.settings import get_settings


class OllamaClient(LLMClient):
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def _get_client(self):
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            api_key="ollama",
            base_url=f"{self.base_url}/v1",
        )

    async def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> dict:
        client = await self._get_client()
        kwargs = {"model": self.model, "messages": messages, **options}
        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if response_schema and content:
            import json
            return json.loads(content)
        return {"content": content or ""}

    async def stream(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> AsyncIterator[str]:
        client = await self._get_client()
        kwargs = {"model": self.model, "messages": messages, "stream": True, **options}
        stream = await client.chat.completions.create(**kwargs)
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    async def embed(self, texts: list[str], **options: Any) -> list[list[float]]:
        client = await self._get_client()
        response = await client.embeddings.create(
            model=options.get("embedding_model", self.model),
            input=texts,
        )
        return [d.embedding for d in response.data]
