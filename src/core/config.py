import enum
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # LLM Provider config
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    # Llama Parse config
    LLAMA_CLOUD_API_KEY: str | None = None

    LOGGER_FORMAT: str = "[{time:YYYY-MM-DD HH:mm:ss}] | {level:<8} | {name}:{function}:{line} - {message}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()

settings = get_settings()