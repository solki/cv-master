from app.llm.base import LLMClient
from app.core.settings import get_settings


def get_llm_client() -> LLMClient:
    settings = get_settings()
    provider = settings.LLM_PROVIDER

    if provider == "openai_compatible":
        from app.llm.openai_compatible import OpenAICompatibleClient
        return OpenAICompatibleClient()
    elif provider == "openai":
        from app.llm.openai_adapter import OpenAIClient
        return OpenAIClient()
    elif provider == "anthropic":
        from app.llm.anthropic_adapter import AnthropicClient
        return AnthropicClient()
    elif provider == "ollama":
        from app.llm.ollama_adapter import OllamaClient
        return OllamaClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
