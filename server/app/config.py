"""Load env and expose settings for NeurON website API."""

from __future__ import annotations

import os
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SERVER_DIR.parent
ENV_PATH = SERVER_DIR / ".env"
DATA_DIR = SERVER_DIR / "data"

# Keys that must be taken from server/.env even if empty shell vars exist
_FORCE_FROM_ENV_FILE = {
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "API_BEARER_TOKEN",
    "HOST",
    "PORT",
    "DATABASE_URL",
    "BOOKING_API_URL",
    "CALLBACK_API_URL",
    "CLINIC_NAME",
    "CLINIC_LOCATION",
    "CLINIC_PHONE",
    "CLINIC_EMAIL",
    "CLINIC_ADDRESS",
    "CLINIC_SITE_URL",
    "ANALYTICS_SECRET_TOKEN",
}


def load_env(path: Path = ENV_PATH, *, override: bool = False) -> dict[str, str]:
    """Load KEY=VALUE from .env into os.environ.

    - Fills missing / empty keys
    - For Telegram/API keys prefers non-empty values from the .env file
      (fixes hosting panels that inject empty TELEGRAM_* variables)
    """
    loaded: dict[str, str] = {}
    if not path.is_file():
        return loaded

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Strip accidental brackets from pasted secrets: [token]
        if len(value) >= 2 and value[0] == "[" and value[-1] == "]":
            value = value[1:-1].strip()
        if not key:
            continue

        existing = os.environ.get(key)
        existing_empty = existing is None or not str(existing).strip()
        force_from_file = key in _FORCE_FROM_ENV_FILE and bool(value)

        if override or existing_empty or force_from_file:
            os.environ[key] = value
            loaded[key] = value
    return loaded


def mask_secret(value: str, keep: int = 4) -> str:
    v = (value or "").strip()
    if not v:
        return "(empty)"
    if len(v) <= keep * 2:
        return "***"
    return f"{v[:keep]}…{v[-keep:]}"


def get_config() -> dict[str, str | int | bool]:
    load_env()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    # Normalize chat_id (digits / negative group ids only)
    if chat_id.endswith(".0"):
        chat_id = chat_id[:-2]
    api_bearer = os.environ.get("API_BEARER_TOKEN", "").strip()
    analytics_token = os.environ.get("ANALYTICS_SECRET_TOKEN", "").strip()
    host = os.environ.get("HOST", "127.0.0.1").strip() or "127.0.0.1"
    try:
        port = int(os.environ.get("PORT", "8000"))
    except ValueError:
        port = 8000
    db_url = os.environ.get("DATABASE_URL", "").strip() or f"sqlite:///{(DATA_DIR / 'neuron.db').as_posix()}"
    return {
        "telegram_bot_token": token,
        "telegram_chat_id": chat_id,
        "telegram_configured": bool(token and chat_id),
        "api_bearer_token": api_bearer,
        "analytics_secret_token": analytics_token,
        "host": host,
        "port": port,
        "project_root": PROJECT_ROOT,
        "server_dir": SERVER_DIR,
        "database_url": db_url,
        "telegram_token_masked": mask_secret(token, 6),
        "telegram_chat_id_masked": mask_secret(chat_id, 2),
        "clinic_name": os.environ.get("CLINIC_NAME", "").strip() or "NeurON Medical Centre",
        "clinic_location": os.environ.get("CLINIC_LOCATION", "").strip() or "Ташкент, Узбекистан",
        "clinic_phone": os.environ.get("CLINIC_PHONE", "").strip() or "+998 (71) 200-00-20",
        "clinic_email": os.environ.get("CLINIC_EMAIL", "").strip() or "info@neuronmedical.uz",
        "clinic_address": os.environ.get("CLINIC_ADDRESS", "").strip()
        or "Ташкент, Юнусабадский район, махалля Отчопар-2, 3-й проезд Чинабад, дом 2",
        "clinic_site_url": os.environ.get("CLINIC_SITE_URL", "").strip() or "https://neuronmedical.uz/",
    }
