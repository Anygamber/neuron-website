"""Pydantic models for callback request API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CallbackRequest(BaseModel):
    client_name: str = Field(default="Обратный звонок", max_length=120)
    phone: str = Field(..., min_length=7, max_length=32)
    service_name: str | None = Field(default=None, max_length=300)
    comment: str | None = Field(default=None, max_length=2000)
    preferred_time: str | None = Field(default=None, max_length=120)
    source: str = Field(default="NeurON website", max_length=120)


class CallbackResponse(BaseModel):
    ok: bool = True
    message: str = "Заявка на звонок принята. Ожидайте звонка."
    telegram_delivered: bool = False


class StaffRegisterRequest(BaseModel):
    telegram_id: int
    display_name: str = Field(default="Сотрудник", max_length=200)
    username: str | None = Field(default=None, max_length=128)


class StaffUnregisterRequest(BaseModel):
    telegram_id: int
