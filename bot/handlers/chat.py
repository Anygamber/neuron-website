"""Manager support chat — forum topics (A) + dashboard fallback (B)."""

from __future__ import annotations

import json
from typing import Any

import aiohttp
from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from core.config import get_settings

router = Router(name="live_chat")

_manager_sessions: dict[str, str] = {}
_GROUP = {ChatType.GROUP, ChatType.SUPERGROUP}


class ManagerChatStates(StatesGroup):
    waiting_reply = State()


def _mgr_id(user_id: int | None) -> str:
    return str(user_id or 0)


async def _api_get(path: str) -> dict[str, Any]:
    settings = get_settings()
    base = settings.booking_api_url.rsplit("/api/", 1)[0]
    url = f"{base}{path}"
    headers = {"Accept": "application/json"}
    if settings.api_bearer_token.strip():
        headers["Authorization"] = f"Bearer {settings.api_bearer_token.strip()}"
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(text[:300] or f"HTTP {resp.status}")
            return json.loads(text) if text else {}


async def _api_post(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = get_settings()
    base = settings.booking_api_url.rsplit("/api/", 1)[0]
    url = f"{base}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if settings.api_bearer_token.strip():
        headers["Authorization"] = f"Bearer {settings.api_bearer_token.strip()}"
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload or {}, headers=headers) as resp:
            text = await resp.text()
            logger.info("Chat API {} → {}", path, resp.status)
            if resp.status >= 400:
                try:
                    detail = json.loads(text).get("detail") or text
                except json.JSONDecodeError:
                    detail = text
                raise RuntimeError(str(detail)[:400])
            return json.loads(text) if text else {"ok": True}


async def _forward_to_site(message: Message, session_id: str, text: str, quiet: bool = False) -> None:
    mid = _mgr_id(message.from_user.id if message.from_user else None)
    try:
        await _api_post(
            "/api/v1/chat/manager-reply",
            {
                "session_id": session_id,
                "text": text,
                "manager_telegram_id": mid,
                "manager_name": message.from_user.full_name if message.from_user else None,
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("manager-reply failed")
        await message.reply(f"⚠ Не удалось отправить на сайт: {exc}")
        return
    if not quiet:
        await message.reply("✅ На сайте")


# ---------- Forum topics: write in topic → site ----------
@router.message(F.text, F.message_thread_id, F.chat.type.in_(_GROUP))
async def topic_message_to_site(message: Message) -> None:
    """Any manager text inside a patient topic goes to the website."""
    if not message.from_user or message.from_user.is_bot:
        return
    if message.text and message.text.startswith("/"):
        return
    # Ignore General topic noise if needed — patient topics always have custom ids
    thread_id = message.message_thread_id
    if not thread_id:
        return
    try:
        data = await _api_get(f"/api/v1/chat/by-topic/{thread_id}")
    except Exception:
        return  # not our topic
    session_id = data.get("session_id")
    if not session_id:
        return
    text = (message.text or "").strip()
    if not text:
        return
    logger.info("Topic {} → session {} | manager {}", thread_id, session_id, message.from_user.id)
    await _forward_to_site(message, session_id, text, quiet=True)


@router.message(Command("close_topic"), F.chat.type.in_(_GROUP))
async def close_topic_cmd(message: Message) -> None:
    thread_id = message.message_thread_id
    if not thread_id:
        await message.answer("Команда только внутри темы пациента.")
        return
    try:
        data = await _api_get(f"/api/v1/chat/by-topic/{thread_id}")
        await _api_post(f"/api/v1/chat/close/{data['session_id']}", {})
    except Exception as exc:  # noqa: BLE001
        await message.answer(f"Не закрыто: {exc}")
        return
    await message.answer("✅ Диалог закрыт.")


# ---------- Dashboard mode (non-forum chat) ----------
@router.callback_query(F.data == "chat:board:refresh")
async def board_refresh(callback: CallbackQuery) -> None:
    await callback.answer("Обновляю…")
    try:
        await _api_post("/api/v1/chat/board/refresh", {})
    except Exception as exc:  # noqa: BLE001
        await callback.message.answer(f"Ошибка: {exc}")


@router.callback_query(F.data.startswith("chat:open:"))
async def board_open_dialog(callback: CallbackQuery, state: FSMContext) -> None:
    session_id = callback.data.split("chat:open:", 1)[1].strip()
    mid = _mgr_id(callback.from_user.id if callback.from_user else None)
    _manager_sessions[mid] = session_id
    await state.set_state(ManagerChatStates.waiting_reply)
    await state.update_data(chat_session_id=session_id, manager_id=mid)
    await callback.answer("Диалог открыт")
    # Load short history
    try:
        hist = await _api_get(f"/api/v1/chat/history/{session_id}")
    except Exception as exc:  # noqa: BLE001
        await callback.message.answer(f"Не удалось открыть: {exc}")
        return
    lines = [
        f"✉️ <b>{hist.get('patient_name')}</b>",
        f"<code>{session_id}</code>",
        "Пишите ответы сюда. /done — выход из диалога.",
        "",
    ]
    for m in (hist.get("messages") or [])[-8:]:
        who = "👤" if m.get("sender") == "patient" else "🧑‍💼"
        lines.append(f"{who} {m.get('text')}")
    await callback.message.answer("\n".join(lines)[:3900])


@router.message(Command("done"))
async def done_reply(message: Message, state: FSMContext) -> None:
    mid = _mgr_id(message.from_user.id if message.from_user else None)
    await state.clear()
    _manager_sessions.pop(mid, None)
    await message.answer("Вышли из режима ответа. Список — в закреплённом сообщении.")


@router.message(Command("chats"))
@router.message(Command("board"))
async def show_board(message: Message) -> None:
    try:
        await _api_post("/api/v1/chat/board/refresh", {})
        await message.answer("📋 Список активных диалогов обновлён (см. закреплённое сообщение).")
    except Exception as exc:  # noqa: BLE001
        data = await _api_get("/api/v1/chat/active")
        mode = data.get("mode") or "?"
        lines = [f"Режим: <b>{mode}</b>", ""]
        for item in data.get("items") or []:
            icon = "🟡" if item.get("wait_state") == "waiting" else "🟢"
            lines.append(f"{icon} {item.get('patient_name')} · <code>{item.get('session_id')}</code>")
        await message.answer("\n".join(lines) or "Нет активных диалогов")
        if mode != "topics":
            await message.answer(f"(refresh board failed: {exc})")


@router.message(ManagerChatStates.waiting_reply, F.text)
async def dashboard_manager_text(message: Message, state: FSMContext) -> None:
    """Dashboard mode: replies while FSM attached to a session."""
    if message.message_thread_id:
        return  # handled by topic handler
    if message.text and message.text.startswith("/"):
        return
    data = await state.get_data()
    mid = _mgr_id(message.from_user.id if message.from_user else None)
    session_id = data.get("chat_session_id") or _manager_sessions.get(mid)
    if not session_id:
        await state.clear()
        await message.answer("Нет активного диалога. Выберите пациента в закреплённом списке.")
        return
    text = (message.text or "").strip()
    if not text:
        return
    await _forward_to_site(message, session_id, text, quiet=False)


@router.message(StateFilter(ManagerChatStates.waiting_reply))
async def dashboard_non_text(message: Message) -> None:
    if message.message_thread_id:
        return
    await message.answer("Отправьте текст или /done")


@router.message(Command("start"))
async def support_start(message: Message) -> None:
    await message.answer(
        "NeurON Support (@uzneuron_bot)\n\n"
        "• Если группа — <b>форум с темами</b>: каждый пациент = своя тема, пишите прямо там.\n"
        "• Иначе: закреплённый список «Активные диалоги» → /board\n"
        "• /done — выйти из режима ответа (dashboard)"
    )
