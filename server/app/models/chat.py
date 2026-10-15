"""Chat ORM models."""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SessionStatus(str, enum.Enum):
    active = "active"
    closed = "closed"


class MessageSender(str, enum.Enum):
    patient = "patient"
    manager = "manager"
    system = "system"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    patient_name: Mapped[str] = mapped_column(String(120), default="Гость", nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, native_enum=False), default=SessionStatus.active, nullable=False
    )
    assigned_manager_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    telegram_topic_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.id",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_pk: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    sender: Mapped[MessageSender] = mapped_column(Enum(MessageSender, native_enum=False), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    manager_telegram_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="messages")


class ChatMeta(Base):
    """Key/value store (e.g. dashboard board_message_id, support_mode)."""

    __tablename__ = "chat_meta"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")
