from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


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
    if "sslmode=require" in url:
        url = url.replace("sslmode=require", "ssl=require")
    return url


class Settings(BaseSettings):
    BOT_TOKEN: str = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    DB_URL: str = "sqlite+aiosqlite:///subscriptions.db"
    DEFAULT_TIMEZONE: str = "UTC+3"
    REMINDER_HOUR: int = 10
    REMINDER_MINUTE: int = 0
    PORT: int = 0

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
