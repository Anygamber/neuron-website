"""Telegram Bot API helpers (sendMessage, forum topics, edit/pin)."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from datetime import datetime
from html import escape
from typing import Any
from zoneinfo import ZoneInfo

logger = logging.getLogger("neuron.telegram")

TELEGRAM_API = "https://api.telegram.org"
TASHKENT = ZoneInfo("Asia/Tashkent")


def _normalize_chat_id(chat_id: str | int) -> str | int:
    """Telegram accepts int or str; prefer int for numeric private chats."""
    raw = str(chat_id).strip()
    if not raw:
        raise RuntimeError("Пустой chat_id")
    if raw.lstrip("-").isdigit():
        try:
            return int(raw)
        except ValueError:
            return raw
    return raw


def _api(config: dict[str, Any], method: str, payload: dict[str, Any]) -> dict[str, Any]:
    token = str(config.get("telegram_bot_token") or "").strip()
    if not token:
        raise RuntimeError(
            "Telegram не настроен: укажите TELEGRAM_BOT_TOKEN в server/.env"
        )
    # Never log full token
    token_hint = config.get("telegram_token_masked") or f"{token[:6]}…"
    safe_payload = dict(payload)
    if "chat_id" in safe_payload:
        safe_payload["chat_id"] = _normalize_chat_id(safe_payload["chat_id"])
        payload = {**payload, "chat_id": safe_payload["chat_id"]}
    if "text" in safe_payload and isinstance(safe_payload["text"], str):
        safe_payload["text"] = safe_payload["text"][:180] + (
            "…" if len(safe_payload["text"]) > 180 else ""
        )

    url = f"{TELEGRAM_API}/bot{token}/{method}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    logger.info(
        "Telegram → %s | token=%s | payload=%s",
        method,
        token_hint,
        json.dumps(safe_payload, ensure_ascii=False),
    )
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = getattr(resp, "status", 200)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        logger.error("Telegram ← %s HTTP %s | body=%s", method, exc.code, detail)
        raise RuntimeError(f"Telegram {method} error ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        logger.error("Telegram ← %s network error: %s", method, exc.reason)
        raise RuntimeError(f"Не удалось связаться с Telegram: {exc.reason}") from exc

    logger.info("Telegram ← %s HTTP %s | body=%s", method, status, raw[:800])
    data = json.loads(raw)
    if not data.get("ok"):
        raise RuntimeError(data.get("description") or f"Telegram {method} failed")
    return data.get("result") or {}


def get_chat(config: dict[str, Any]) -> dict[str, Any]:
    return _api(config, "getChat", {"chat_id": config["telegram_chat_id"]})


def is_forum_chat(config: dict[str, Any]) -> bool:
    try:
        chat = get_chat(config)
        return bool(chat.get("is_forum"))
    except Exception:  # noqa: BLE001
        logger.exception("getChat failed")
        return False


def create_forum_topic(config: dict[str, Any], name: str) -> int:
    """Create topic; returns message_thread_id."""
    title = (name or "Пациент").strip()[:128] or "Пациент"
    result = _api(
        config,
        "createForumTopic",
        {"chat_id": config["telegram_chat_id"], "name": title},
    )
    thread_id = result.get("message_thread_id")
    if not thread_id:
        raise RuntimeError("createForumTopic не вернул message_thread_id")
    return int(thread_id)


def close_forum_topic(config: dict[str, Any], message_thread_id: int) -> None:
    try:
        _api(
            config,
            "closeForumTopic",
            {
                "chat_id": config["telegram_chat_id"],
                "message_thread_id": int(message_thread_id),
            },
        )
    except Exception:  # noqa: BLE001
        logger.warning("closeForumTopic failed for %s", message_thread_id, exc_info=True)


def send_telegram_to_chat(
    config: dict[str, Any],
    chat_id: str | int,
    text: str,
    reply_markup: dict[str, Any] | None = None,
    message_thread_id: int | None = None,
) -> dict[str, Any]:
    payload_body: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup:
        payload_body["reply_markup"] = reply_markup
    if message_thread_id is not None:
        payload_body["message_thread_id"] = int(message_thread_id)
    return _api(config, "sendMessage", payload_body)


def send_telegram_message(
    config: dict[str, Any],
    text: str,
    reply_markup: dict[str, Any] | None = None,
    message_thread_id: int | None = None,
) -> dict[str, Any]:
    if not config.get("telegram_chat_id"):
        raise RuntimeError(
            "Telegram не настроен: укажите TELEGRAM_CHAT_ID в server/.env"
        )
    return send_telegram_to_chat(
        config,
        config["telegram_chat_id"],
        text,
        reply_markup=reply_markup,
        message_thread_id=message_thread_id,
    )


def edit_telegram_message(
    config: dict[str, Any],
    message_id: int,
    text: str,
    reply_markup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "chat_id": config["telegram_chat_id"],
        "message_id": int(message_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    return _api(config, "editMessageText", payload)


def pin_telegram_message(config: dict[str, Any], message_id: int) -> None:
    try:
        _api(
            config,
            "pinChatMessage",
            {
                "chat_id": config["telegram_chat_id"],
                "message_id": int(message_id),
                "disable_notification": True,
            },
        )
    except Exception:  # noqa: BLE001
        logger.warning("pinChatMessage failed", exc_info=True)


def _now_tashkent_str() -> str:
    return datetime.now(TASHKENT).strftime("%d.%m.%Y %H:%M")


def _clinic_block(data: dict[str, Any] | None = None) -> list[str]:
    """Clinic info block; values may come from notify payload or defaults."""
    data = data or {}
    name = data.get("clinic_name") or "NeurON Medical Centre"
    location = data.get("clinic_location") or "Ташкент, Узбекистан"
    phone = data.get("clinic_phone") or "+998 (71) 200-00-20"
    email = data.get("clinic_email") or "info@neuronmedical.uz"
    address = data.get("clinic_address") or (
        "Ташкент, Юнусабадский район, махалля Отчопар-2, 3-й проезд Чинабад, дом 2"
    )
    site = data.get("clinic_site_url") or "https://neuronmedical.uz/"
    return [
        "",
        "———",
        "🏥 <b>О клинике</b>",
        f"🏢 <b>Клиника:</b> {escape(str(name))}",
        f"📍 <b>Локация:</b> {escape(str(location))}",
        f"🗺 <b>Адрес:</b> {escape(str(address))}",
        f"📞 <b>Контакты:</b> {escape(str(phone))}",
        f"✉️ <b>Email:</b> {escape(str(email))}",
        f"🌐 <b>Сайт:</b> {escape(str(site))}",
    ]


def build_callback_message(data: dict[str, Any]) -> str:
    lines = [
        "🔔 <b>Новая заявка с сайта NeurON!</b>",
        "",
        f"👤 <b>Имя:</b> {escape(str(data.get('client_name') or 'Обратный звонок'))}",
        f"📞 <b>Телефон клиента:</b> {escape(str(data.get('phone') or '—'))}",
    ]
    direction = data.get("service_name") or data.get("category")
    if direction:
        lines.append(f"🎯 <b>Направление:</b> {escape(str(direction))}")
    if data.get("preferred_time"):
        lines.append(f"🕒 <b>Удобное время:</b> {escape(str(data['preferred_time']))}")
    if data.get("comment"):
        lines.append(f"💬 <b>Комментарий:</b> {escape(str(data['comment']))}")
    lines.append(f"⏰ <b>Время обращения:</b> {escape(_now_tashkent_str())} (Ташкент)")
    lines.extend(_clinic_block(data))
    if data.get("source"):
        lines += ["", f"📎 Источник заявки: {escape(str(data['source']))}"]
    return "\n".join(lines)


def build_booking_message(data: dict[str, Any]) -> str:
    if data.get("form_type") == "callback":
        return build_callback_message(data)

    lines = [
        "🆕 <b>Новая запись на приём — NeurON</b>",
        "",
        f"👤 <b>Пациент:</b> {escape(data['client_name'])}",
        f"📱 <b>Телефон:</b> {escape(data['phone'])}",
    ]
    if data.get("service_name"):
        lines.append(f"🩺 <b>Услуга:</b> {escape(data['service_name'])}")
    if data.get("category"):
        lines.append(f"📁 <b>Категория:</b> {escape(data['category'])}")
    if data.get("appointment_date") or data.get("time_slot"):
        when = " · ".join(
            p for p in (data.get("appointment_date"), data.get("time_slot")) if p
        )
        lines.append(f"🗓 <b>Дата / время:</b> {escape(when)}")
    if data.get("comment"):
        lines.append(f"💬 <b>Комментарий:</b> {escape(data['comment'])}")
    lines.append(f"⏰ <b>Время заявки:</b> {escape(_now_tashkent_str())} (Ташкент)")
    lines += ["", f"🌐 Источник: {escape(data['source'])}"]
    return "\n".join(lines)


def collect_recipient_ids(config: dict[str, Any], extra_ids: list[int] | None = None) -> list[str]:
    """Primary clinic chat + registered staff (unique)."""
    ids: list[str] = []
    primary = str(config.get("telegram_chat_id") or "").strip()
    if primary:
        ids.append(primary)
    for raw in extra_ids or []:
        sid = str(raw).strip()
        if sid and sid not in ids:
            ids.append(sid)
    return ids


def notify_many(
    config: dict[str, Any],
    text: str,
    chat_ids: list[str],
) -> tuple[int, int]:
    """Send to many chats. Returns (ok_count, fail_count)."""
    if not str(config.get("telegram_bot_token") or "").strip():
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")
    if not chat_ids:
        raise RuntimeError("Нет получателей Telegram (CHAT_ID / сотрудники)")

    logger.info(
        "notify_many | recipients=%s | token=%s",
        chat_ids,
        config.get("telegram_token_masked"),
    )
    ok = 0
    fail = 0
    for chat_id in chat_ids:
        try:
            result = send_telegram_to_chat(config, chat_id, text)
            ok += 1
            msg_id = result.get("message_id")
            logger.info("notify_many OK | chat_id=%s | message_id=%s", chat_id, msg_id)
        except Exception as exc:  # noqa: BLE001
            fail += 1
            logger.exception("notify_many FAIL | chat_id=%s | error=%s", chat_id, exc)
    if ok == 0:
        raise RuntimeError("Не удалось доставить заявку ни одному получателю в Telegram")
    return ok, fail


def _with_clinic_meta(config: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    return {
        **data,
        "clinic_name": config.get("clinic_name"),
        "clinic_location": config.get("clinic_location"),
        "clinic_phone": config.get("clinic_phone"),
        "clinic_email": config.get("clinic_email"),
        "clinic_address": config.get("clinic_address"),
        "clinic_site_url": config.get("clinic_site_url"),
    }


def notify_booking(
    config: dict[str, Any],
    data: dict[str, Any],
    extra_chat_ids: list[int] | None = None,
) -> tuple[int, int]:
    enriched = _with_clinic_meta(config, data)
    text = build_booking_message(enriched)
    recipients = collect_recipient_ids(config, extra_chat_ids)
    logger.info(
        "notify_booking | form_type=%s | phone=%s | recipients=%s",
        data.get("form_type"),
        data.get("phone"),
        recipients,
    )
    return notify_many(config, text, recipients)


def notify_callback(
    config: dict[str, Any],
    data: dict[str, Any],
    extra_chat_ids: list[int] | None = None,
) -> tuple[int, int]:
    enriched = _with_clinic_meta(config, data)
    text = build_callback_message(enriched)
    recipients = collect_recipient_ids(config, extra_chat_ids)
    logger.info(
        "notify_callback | name=%s | phone=%s | service=%s | recipients=%s",
        data.get("client_name"),
        data.get("phone"),
        data.get("service_name"),
        recipients,
    )
    if not recipients:
        raise RuntimeError(
            "TELEGRAM_CHAT_ID пуст и нет зарегистрированных сотрудников (/register)"
        )
    return notify_many(config, text, recipients)
