"""HTTP helpers: register/unregister clinic staff via NeurON API."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from core.config import get_settings


def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = get_settings()
    url = f"{settings.api_base_url.rstrip('/')}{path}"
    headers = {"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"}
    token = settings.api_bearer_token.strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(detail or f"HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"API недоступен: {exc.reason}") from exc

    if not raw:
        return {"ok": True}
    return json.loads(raw)


def register_staff(*, telegram_id: int, display_name: str, username: str | None) -> dict[str, Any]:
    return _request(
        "POST",
        "/api/v1/staff/register",
        {
            "telegram_id": int(telegram_id),
            "display_name": display_name,
            "username": username,
        },
    )


def unregister_staff(*, telegram_id: int) -> dict[str, Any]:
    return _request(
        "POST",
        "/api/v1/staff/unregister",
        {"telegram_id": int(telegram_id)},
    )


def list_staff() -> dict[str, Any]:
    return _request("GET", "/api/v1/staff", None)
