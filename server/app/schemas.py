"""Validation helpers for booking payloads."""

from __future__ import annotations

import re
from typing import Any

PHONE_DIGITS_RE = re.compile(r"\D+")


def normalize_phone(value: str) -> str:
    digits = PHONE_DIGITS_RE.sub("", value or "")
    if digits.startswith("8") and len(digits) == 11:
        digits = "998" + digits[1:]
    if len(digits) == 9:
        digits = "998" + digits
    return digits


def format_phone_display(digits: str) -> str:
    d = normalize_phone(digits)
    if len(d) == 12 and d.startswith("998"):
        return f"+{d[:3]} {d[3:5]} {d[5:8]} {d[8:10]} {d[10:12]}"
    return f"+{d}" if d else ""


def _clean_str(value: Any, max_len: int) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return s[:max_len]


def validate_booking(raw: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Return (payload, error_message)."""
    if not isinstance(raw, dict):
        return None, "Некорректное тело запроса"

    form_type = (_clean_str(raw.get("form_type"), 32) or "booking").lower()
    if form_type not in {"booking", "callback"}:
        form_type = "booking"

    phone_raw = _clean_str(raw.get("phone"), 32)
    if not phone_raw:
        return None, "Укажите номер телефона"
    digits = normalize_phone(phone_raw)
    if len(digits) != 12 or not digits.startswith("998"):
        return None, "Введите корректный номер телефона (+998 XX XXX XX XX)"

    name = _clean_str(raw.get("client_name"), 120) or ""
    if form_type == "booking":
        if len(name) < 2:
            return None, "Укажите имя пациента"
        service = _clean_str(raw.get("service_name"), 300)
        if not service:
            return None, "Выберите услугу или направление"
    else:
        name = name or "Обратный звонок"
        service = _clean_str(raw.get("service_name"), 300)

    payload = {
        "client_name": name,
        "phone": format_phone_display(digits),
        "service_name": service,
        "category": _clean_str(raw.get("category"), 200),
        "appointment_date": _clean_str(raw.get("appointment_date"), 32),
        "time_slot": _clean_str(raw.get("time_slot"), 64),
        "preferred_time": _clean_str(raw.get("preferred_time"), 120),
        "comment": _clean_str(raw.get("comment"), 2000),
        "source": _clean_str(raw.get("source"), 120) or "NeurON website",
        "form_type": form_type,
    }
    return payload, None
