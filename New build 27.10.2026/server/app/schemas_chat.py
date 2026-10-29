"""Pydantic schemas for live chat API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatSendRequest(BaseModel):
    session_id: str | None = Field(default=None, max_length=64)
    patient_name: str | None = Field(default=None, max_length=120)
    text: str = Field(..., min_length=1, max_length=4000)

    @field_validator("text")
    @classmethod
    def strip_text(cls, v: str) -> str:
        t = (v or "").strip()
        if not t:
            raise ValueError("Сообщение пустое")
        return t

    @field_validator("patient_name", mode="before")
    @classmethod
    def strip_name(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        return s or None


class ManagerReplyRequest(BaseModel):
    session_id: str = Field(..., min_length=8, max_length=64)
    text: str = Field(..., min_length=1, max_length=4000)
    manager_telegram_id: str | None = None
    manager_name: str | None = None

    @field_validator("text")
    @classmethod
    def strip_text(cls, v: str) -> str:
        t = (v or "").strip()
        if not t:
            raise ValueError("Сообщение пустое")
        return t


class ChatMessageOut(BaseModel):
    id: int
    session_id: str
    sender: Literal["patient", "manager", "system"]
    text: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class ChatSendResponse(BaseModel):
    ok: bool = True
    session_id: str
    message: ChatMessageOut


class ChatHistoryResponse(BaseModel):
    ok: bool = True
    session_id: str
    status: str
    patient_name: str
    messages: list[ChatMessageOut]
