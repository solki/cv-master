from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class LLMClient(ABC):
    """Abstract interface for LLM provider adapters."""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> dict:
        """Generate a completion. Returns structured output if schema provided."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[dict[str, str]],
        response_schema: dict | None = None,
        **options: Any,
    ) -> AsyncIterator[str]:
        """Stream completion tokens."""
        ...

    @abstractmethod
    async def embed(self, texts: list[str], **options: Any) -> list[list[float]]:
        """Generate embeddings for input texts."""
        ...
