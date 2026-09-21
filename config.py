from typing import Optional
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


import re


def normalize_db_url(url: str) -> str:
    """Normalizes database URL to ensure compatibility with asyncpg (e.g. Neon, Render)."""
    if not url:
        return url
    url = url.strip().strip("'\"")
    if url.startswith("psql "):
        url = url[5:].strip().strip("'\"")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Neon adds &channel_binding=require which asyncpg does not support
    url = re.sub(r"[&?]channel_binding=[^&]+", "", url)

    # asyncpg expects ssl=require rather than sslmode=require
    if "sslmode=require" in url:
        url = url.replace("sslmode=require", "ssl=require")

    # If removing query params left an orphan & at the start of query
    if "?" not in url and "&" in url:
        url = url.replace("&", "?", 1)

    return url


class Settings(BaseSettings):
    BOT_TOKEN: str = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    DB_URL: str = "sqlite+aiosqlite:///subscriptions.db"
    DEFAULT_TIMEZONE: str = "UTC+3"
    REMINDER_HOUR: int = 10
    REMINDER_MINUTE: int = 0
    PORT: int = 0
    WEBAPP_URL: str = ""

    @field_validator("WEBAPP_URL", mode="before")
    @classmethod
    def set_default_webapp_url(cls, v: Optional[str]) -> str:
        import os
        if not v:
            return os.getenv("RENDER_EXTERNAL_URL", "https://sub-tracker-bot.onrender.com")
        return v

    @field_validator("DB_URL", mode="after")
    @classmethod
    def format_db_url(cls, v: str) -> str:
        return normalize_db_url(v)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
