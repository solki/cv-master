from app.llm import get_llm_client


class EmbeddingService:
    def __init__(self):
        self._client = None

    async def _get_client(self):
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    async def embed_texts(
        self, texts: list[str], model: str | None = None
    ) -> list[list[float]]:
        client = await self._get_client()
        options = {}
        if model:
            options["embedding_model"] = model
        return await client.embed(texts, **options)

    async def embed_single(self, text: str, model: str | None = None) -> list[float]:
        embeddings = await self.embed_texts([text], model)
        return embeddings[0]
