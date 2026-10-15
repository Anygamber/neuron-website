"""Settings for @uzneuron_bot (pydantic-settings + shared server/.env)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BOT_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BOT_DIR.parent
SERVER_ENV = PROJECT_ROOT / "server" / ".env"
BOT_ENV = BOT_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(SERVER_ENV), str(BOT_ENV)),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    api_bearer_token: str = ""
    booking_api_url: str = "http://127.0.0.1:8000/api/submit-booking"
    callback_api_url: str = "http://127.0.0.1:8000/api/request-callback"
    bot_username: str = "uzneuron_bot"

    @property
    def telegram_configured(self) -> bool:
        return bool(self.telegram_bot_token.strip() and self.telegram_chat_id.strip())

    @property
    def api_base_url(self) -> str:
        from urllib.parse import urlparse

        for candidate in (self.callback_api_url, self.booking_api_url):
            raw = (candidate or "").strip()
            if not raw:
                continue
            parsed = urlparse(raw)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
        return "http://127.0.0.1:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
