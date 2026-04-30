"""Application settings.

Centralizes environment-backed configuration so API, LLM, and persistence
settings are defined in one place.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    app_name: str
    app_version: str
    openai_api_key: str
    openai_model: str
    openai_temperature: float
    request_timeout_seconds: float
    database_url: str
    log_level: str
    save_analysis_results: bool
    search_provider: str
    tavily_api_key: str
    search_results_limit: int
    retrieval_results_limit: int


def _get_bool(name: str, default: bool) -> bool:
    """Parse a bool-like environment variable."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    """Build a settings object from environment variables."""
    return Settings(
        app_name=os.getenv("APP_NAME", "Idea Validator API"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
        request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./idea_validator.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        save_analysis_results=_get_bool("SAVE_ANALYSIS_RESULTS", True),
        search_provider=os.getenv("SEARCH_PROVIDER", "tavily"),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        search_results_limit=int(os.getenv("SEARCH_RESULTS_LIMIT", "5")),
        retrieval_results_limit=int(os.getenv("RETRIEVAL_RESULTS_LIMIT", "3")),
    )


settings = get_settings()
