"""Application configuration via environment variables and .env file."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    db_path: str = "newsgraber.db"

    # Fetcher
    fetch_timeout: int = 15  # seconds per source
    fetch_concurrency: int = 10  # max concurrent requests
    user_agent: str = "NewsGraber/0.1 (RSS Aggregator)"

    # Web server
    host: str = "0.0.0.0"
    port: int = 8000

    # Filtering
    default_language: str = ""  # empty = all languages
    max_articles_per_source: int = 20

    model_config = {
        "env_prefix": "NEWSGRABER_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        env_path = Path(".env")
        if env_path.exists():
            _settings = Settings(_env_file=str(env_path))
        else:
            _settings = Settings()
    return _settings
