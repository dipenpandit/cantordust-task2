import enum
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
    
class LLMProvider(enum.StrEnum):
    GROQ = "groq"
    GEMINI = "gemini"
    NVIDIA = "nvidia"


class Settings(BaseSettings):

    # LLM Provider config
    LLM_PROVIDER: LLMProvider = LLMProvider.NVIDIA
    GROQ_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    NVIDIA_API_KEY: str | None = None
    LLM_MODEL: str = "gemini-2.5-flash"

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