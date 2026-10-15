"""Inline / reply keyboards for booking FSM."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

# Popular NeurON directions (short list for Telegram UX)
SERVICE_OPTIONS = [
    "МРТ головного мозга",
    "МСКТ / КТ",
    "Консультация нейрохирурга",
    "Лабораторные анализы",
    "Нейрохирургия",
    "Другая услуга",
]


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🩺 Записаться на приём")],
            [KeyboardButton(text="ℹ️ О клинике NeurON"), KeyboardButton(text="📞 Контакты")],
            [KeyboardButton(text="🧑‍⚕️ Регистрация сотрудника")],
        ],
        resize_keyboard=True,
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить мой номер", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def services_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=name, callback_data=f"svc:{idx}")]
        for idx, name in enumerate(SERVICE_OPTIONS)
    ]
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="booking:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def skip_comment_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="booking:skip_comment")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="booking:cancel")],
        ]
    )


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Отправить заявку", callback_data="booking:confirm"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="booking:cancel"),
            ]
        ]
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
