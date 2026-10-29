"""Chat domain service: sessions, forum topics, dashboard board."""

from __future__ import annotations

import logging
import uuid
from html import escape

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_config
from app.models.chat import ChatMessage, ChatMeta, ChatSession, MessageSender, SessionStatus
from app import telegram as tg

logger = logging.getLogger("neuron.chat")

META_BOARD_MSG = "dashboard_message_id"
META_MODE = "support_mode"  # topics | dashboard


def get_meta(db: Session, key: str) -> str | None:
    row = db.get(ChatMeta, key)
    return row.value if row else None


def set_meta(db: Session, key: str, value: str) -> None:
    row = db.get(ChatMeta, key)
    if row:
        row.value = value
    else:
        row = ChatMeta(key=key, value=value)
    db.add(row)
    db.commit()


def get_or_create_session(
    db: Session,
    session_id: str | None,
    patient_name: str | None,
) -> ChatSession:
    sid = (session_id or "").strip() or str(uuid.uuid4())
    row = db.scalar(select(ChatSession).where(ChatSession.session_id == sid))
    if row:
        if patient_name and patient_name.strip() and row.patient_name in {
            "Гость",
            "Гость сайта",
            "Пациент сайта",
        }:
            row.patient_name = patient_name.strip()[:120]
            db.add(row)
            db.commit()
            db.refresh(row)
        if row.status == SessionStatus.closed:
            row.status = SessionStatus.active
            db.add(row)
            db.commit()
            db.refresh(row)
        return row

    row = ChatSession(
        session_id=sid,
        patient_name=(patient_name or "Гость").strip()[:120] or "Гость",
        status=SessionStatus.active,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    logger.info("Created chat session %s (%s)", row.session_id, row.patient_name)
    return row


def add_message(
    db: Session,
    session: ChatSession,
    sender: MessageSender,
    text: str,
    manager_telegram_id: str | None = None,
) -> ChatMessage:
    msg = ChatMessage(
        session_pk=session.id,
        sender=sender,
        text=text,
        manager_telegram_id=manager_telegram_id,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def list_messages(db: Session, session_id: str, after_id: int = 0) -> tuple[ChatSession | None, list[ChatMessage]]:
    session = db.scalar(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.session_id == session_id)
    )
    if not session:
        return None, []
    msgs = [m for m in session.messages if m.id > after_id]
    return session, msgs


def get_session_by_topic(db: Session, topic_id: int) -> ChatSession | None:
    return db.scalar(
        select(ChatSession).where(
            ChatSession.telegram_topic_id == int(topic_id),
            ChatSession.status == SessionStatus.active,
        )
    )


def list_active_sessions(db: Session) -> list[ChatSession]:
    rows = db.scalars(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.status == SessionStatus.active)
        .order_by(ChatSession.created_at.desc())
    ).all()
    return list(rows)


def session_wait_state(session: ChatSession) -> str:
    """waiting = patient wrote last; active = manager replied last / empty."""
    if not session.messages:
        return "waiting"
    last = session.messages[-1]
    sender = last.sender.value if hasattr(last.sender, "value") else str(last.sender)
    return "waiting" if sender == "patient" else "active"


def message_to_dict(session_id: str, msg: ChatMessage) -> dict:
    return {
        "id": msg.id,
        "session_id": session_id,
        "sender": msg.sender.value if hasattr(msg.sender, "value") else str(msg.sender),
        "text": msg.text,
        "timestamp": msg.timestamp,
    }


def resolve_support_mode(db: Session, cfg: dict) -> str:
    forced = (get_meta(db, META_MODE) or "").strip().lower()
    if forced in {"topics", "dashboard"}:
        return forced
    if tg.is_forum_chat(cfg):
        set_meta(db, META_MODE, "topics")
        return "topics"
    set_meta(db, META_MODE, "dashboard")
    return "dashboard"


def _ensure_topic(db: Session, cfg: dict, session: ChatSession) -> int | None:
    if session.telegram_topic_id:
        return int(session.telegram_topic_id)
    name = f"{session.patient_name}"[:100]
    short_id = session.session_id.split("-")[0]
    topic_name = f"{name} · {short_id}"
    try:
        topic_id = tg.create_forum_topic(cfg, topic_name)
    except Exception:  # noqa: BLE001
        logger.exception("createForumTopic failed — falling back to dashboard")
        set_meta(db, META_MODE, "dashboard")
        return None
    session.telegram_topic_id = topic_id
    db.add(session)
    db.commit()
    db.refresh(session)
    # Intro in topic (no buttons)
    tg.send_telegram_message(
        cfg,
        (
            f"🧵 Диалог с <b>{escape(session.patient_name)}</b>\n"
            f"ID: <code>{escape(session.session_id)}</code>\n\n"
            f"Пишите в этой теме — сообщения уйдут пациенту на сайт.\n"
            f"/close_topic — закрыть диалог"
        ),
        message_thread_id=topic_id,
    )
    return topic_id


def _notify_via_topic(db: Session, cfg: dict, session: ChatSession, text: str) -> bool:
    topic_id = _ensure_topic(db, cfg, session)
    if not topic_id:
        return False
    short = text if len(text) <= 3500 else text[:3497] + "…"
    tg.send_telegram_message(
        cfg,
        f"👤 <b>{escape(session.patient_name)}</b>:\n{escape(short)}",
        message_thread_id=topic_id,
    )
    return True


def _build_dashboard(db: Session) -> tuple[str, dict]:
    sessions = list_active_sessions(db)
    lines = [
        "📋 <b>Активные диалоги NeurON Support</b>",
        "Нажмите на пациента, чтобы ответить. Без кнопок под каждым сообщением.",
        "",
    ]
    keyboard: list[list[dict]] = []
    if not sessions:
        lines.append("Пока нет открытых диалогов.")
    for s in sessions[:20]:
        state = session_wait_state(s)
        icon = "🟡" if state == "waiting" else "🟢"
        label_state = "ждёт ответа" if state == "waiting" else "активен"
        lines.append(f"{icon} <b>{escape(s.patient_name)}</b> — {label_state}")
        btn_text = f"{icon} {s.patient_name[:28]} ({label_state})"
        keyboard.append(
            [{"text": btn_text, "callback_data": f"chat:open:{s.session_id}"}]
        )
    keyboard.append([{"text": "🔄 Обновить список", "callback_data": "chat:board:refresh"}])
    return "\n".join(lines), {"inline_keyboard": keyboard}


def refresh_dashboard(db: Session, cfg: dict) -> None:
    text, markup = _build_dashboard(db)
    raw_id = get_meta(db, META_BOARD_MSG)
    if raw_id and raw_id.isdigit():
        try:
            tg.edit_telegram_message(cfg, int(raw_id), text, reply_markup=markup)
            return
        except Exception:  # noqa: BLE001
            logger.info("Dashboard edit failed — sending a new board message")
    result = tg.send_telegram_message(cfg, text, reply_markup=markup)
    msg_id = result.get("message_id")
    if msg_id:
        set_meta(db, META_BOARD_MSG, str(msg_id))
        tg.pin_telegram_message(cfg, int(msg_id))


def _notify_via_dashboard(db: Session, cfg: dict, session: ChatSession, text: str) -> None:
    # One quiet line in the general chat (no per-message buttons)
    short = text if len(text) <= 280 else text[:277] + "…"
    tg.send_telegram_message(
        cfg,
        f"💬 {escape(session.patient_name)}: {escape(short)}\n"
        f"<i>Откройте диалог в закреплённом списке ↓</i>",
    )
    refresh_dashboard(db, cfg)


def notify_managers_new_patient_message(db: Session, session: ChatSession, text: str) -> None:
    """Route patient message to forum topic OR dashboard (no button spam)."""
    cfg = get_config()
    if not cfg["telegram_configured"]:
        logger.warning("Telegram not configured — skip chat notify")
        return

    mode = resolve_support_mode(db, cfg)
    try:
        if mode == "topics":
            ok = _notify_via_topic(db, cfg, session, text)
            if not ok:
                _notify_via_dashboard(db, cfg, session, text)
        else:
            _notify_via_dashboard(db, cfg, session, text)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to notify managers about chat %s", session.session_id)


def on_manager_activity(db: Session, session: ChatSession) -> None:
    """Refresh dashboard after manager reply (topics need nothing)."""
    cfg = get_config()
    if not cfg["telegram_configured"]:
        return
    mode = get_meta(db, META_MODE) or resolve_support_mode(db, cfg)
    if mode == "dashboard":
        try:
            refresh_dashboard(db, cfg)
        except Exception:  # noqa: BLE001
            logger.exception("dashboard refresh after manager reply failed")


def assign_manager(db: Session, session: ChatSession, manager_telegram_id: str) -> ChatSession:
    session.assigned_manager_id = str(manager_telegram_id)
    if session.status == SessionStatus.closed:
        session.status = SessionStatus.active
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def close_session(db: Session, session_id: str) -> ChatSession | None:
    session = db.scalar(select(ChatSession).where(ChatSession.session_id == session_id))
    if not session:
        return None
    session.status = SessionStatus.closed
    db.add(session)
    db.commit()
    db.refresh(session)

    cfg = get_config()
    if cfg["telegram_configured"] and session.telegram_topic_id:
        tg.close_forum_topic(cfg, int(session.telegram_topic_id))
    if cfg["telegram_configured"]:
        mode = get_meta(db, META_MODE) or "dashboard"
        if mode == "dashboard":
            try:
                refresh_dashboard(db, cfg)
            except Exception:  # noqa: BLE001
                logger.exception("dashboard refresh on close failed")
    return session
