from typing import Any, AsyncIterator
from app.llm.base import LLMClient
from app.core.settings import get_settings


class OpenAIClient(LLMClient):
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    async def _get_client(self):
        from openai import AsyncOpenAI
        return AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> dict:
        client = await self._get_client()
        kwargs = {"model": self.model, "messages": messages, **options}
        if response_schema:
            kwargs["response_format"] = {"type": "json_schema", "json_schema": response_schema}
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
            model=options.get("embedding_model", "text-embedding-ada-002"),
            input=texts,
        )
        return [d.embedding for d in response.data]
