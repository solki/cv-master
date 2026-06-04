from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_ENV: Literal["development", "production"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # LLM Provider
    LLM_PROVIDER: Literal["openai_compatible", "openai", "anthropic", "ollama"] = "openai_compatible"

    OPENAI_COMPATIBLE_API_KEY: str = ""
    OPENAI_COMPATIBLE_BASE_URL: str = "https://api.deepseek.com"
    OPENAI_COMPATIBLE_MODEL: str = "deepseek-v4-pro"
    OPENAI_COMPATIBLE_PROVIDER_NAME: str = "deepseek"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = ""

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = ""

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = ""

    # Search Provider
    TAVILY_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cv_master:cv_master@postgres:5432/cv_master"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://cv_master:cv_master@postgres:5432/cv_master"

    POSTGRES_USER: str = "cv_master"
    POSTGRES_PASSWORD: str = "cv_master"
    POSTGRES_DB: str = "cv_master"

    # Redis / Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # Storage
    VAULT_PATH: str = "/app/vault"
    GENERATED_FILES_PATH: str = "/app/generated"

    def validate_provider_config(self) -> dict:
        """Validate that required provider variables are set. Returns status dict."""
        provider = self.LLM_PROVIDER
        status: dict[str, bool | str] = {"provider": provider, "configured": False}

        if provider == "openai_compatible":
            status["configured"] = bool(
                self.OPENAI_COMPATIBLE_API_KEY
                and self.OPENAI_COMPATIBLE_BASE_URL
                and self.OPENAI_COMPATIBLE_MODEL
            )
        elif provider == "openai":
            status["configured"] = bool(self.OPENAI_API_KEY and self.OPENAI_MODEL)
        elif provider == "anthropic":
            status["configured"] = bool(self.ANTHROPIC_API_KEY and self.ANTHROPIC_MODEL)
        elif provider == "ollama":
            status["configured"] = bool(self.OLLAMA_BASE_URL and self.OLLAMA_MODEL)

        return status

    def search_configured(self) -> bool:
        return bool(self.TAVILY_API_KEY)


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
