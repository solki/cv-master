import json
from typing import Any, AsyncIterator
from app.llm.base import LLMClient
from app.core.settings import get_settings


class OpenAICompatibleClient(LLMClient):
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_COMPATIBLE_API_KEY
        self.base_url = settings.OPENAI_COMPATIBLE_BASE_URL
        self.model = settings.OPENAI_COMPATIBLE_MODEL

    async def _get_client(self):
        from openai import AsyncOpenAI
        return AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> dict:
        client = await self._get_client()
        kwargs = {"model": self.model, "messages": messages, **options}

        if response_schema:
            schema_name = response_schema.get("name", "response")
            # Add schema instruction to the prompt for providers that don't support json_schema
            schema_desc = json.dumps(response_schema, indent=2)
            messages = list(messages)  # Don't mutate original
            messages.append({
                "role": "system",
                "content": f"Respond with a JSON object matching this schema: {schema_desc}\nReturn ONLY valid JSON, no other text."
            })
            kwargs["messages"] = messages
            # Try json_object format (more widely supported than json_schema)
            try:
                kwargs["response_format"] = {"type": "json_object"}
                response = await client.chat.completions.create(**kwargs)
            except Exception:
                # Fallback: no response_format constraint
                kwargs.pop("response_format", None)
                response = await client.chat.completions.create(**kwargs)
        else:
            response = await client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content
        if response_schema and content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                    return json.loads(json_str)
                if "```" in content:
                    json_str = content.split("```")[1].split("```")[0]
                    return json.loads(json_str)
                return {"content": content, "parse_error": "Could not parse JSON from response"}
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
