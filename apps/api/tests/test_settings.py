import os
import pytest
from app.core.settings import Settings


class TestSettings:
    def test_default_provider(self):
        settings = Settings()
        assert settings.LLM_PROVIDER == "openai_compatible"

    def test_validate_openai_compatible_configured(self):
        settings = Settings(
            OPENAI_COMPATIBLE_API_KEY="test-key",
            OPENAI_COMPATIBLE_BASE_URL="https://api.test.com",
            OPENAI_COMPATIBLE_MODEL="test-model",
        )
        status = settings.validate_provider_config()
        assert status["provider"] == "openai_compatible"
        assert status["configured"] is True

    def test_validate_openai_compatible_not_configured(self):
        settings = Settings(
            OPENAI_COMPATIBLE_API_KEY="",
            OPENAI_COMPATIBLE_BASE_URL="",
        )
        status = settings.validate_provider_config()
        assert status["configured"] is False

    def test_validate_openai_configured(self):
        settings = Settings(
            LLM_PROVIDER="openai",
            OPENAI_API_KEY="test-key",
            OPENAI_MODEL="gpt-4",
        )
        status = settings.validate_provider_config()
        assert status["provider"] == "openai"
        assert status["configured"] is True

    def test_validate_anthropic_not_configured(self):
        settings = Settings(
            LLM_PROVIDER="anthropic",
            ANTHROPIC_API_KEY="",
            ANTHROPIC_MODEL="",
        )
        status = settings.validate_provider_config()
        assert status["configured"] is False

    def test_validate_ollama_configured(self):
        settings = Settings(
            LLM_PROVIDER="ollama",
            OLLAMA_BASE_URL="http://localhost:11434",
            OLLAMA_MODEL="llama3",
        )
        status = settings.validate_provider_config()
        assert status["provider"] == "ollama"
        assert status["configured"] is True

    def test_search_not_configured_by_default(self):
        settings = Settings(TAVILY_API_KEY="")
        assert settings.search_configured() is False

    def test_search_configured_with_key(self):
        settings = Settings(TAVILY_API_KEY="tvly-test")
        assert settings.search_configured() is True

    def test_cors_origins_default(self):
        settings = Settings()
        assert "http://localhost:3000" in settings.CORS_ORIGINS
        assert "http://127.0.0.1:3000" in settings.CORS_ORIGINS

    def test_app_env_default(self):
        settings = Settings()
        assert settings.APP_ENV == "development"
