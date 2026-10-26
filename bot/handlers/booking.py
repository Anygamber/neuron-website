"""FSM handlers: collect booking lead and POST to NeurON API."""

from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from core.config import get_settings
from keyboards.booking import (
    SERVICE_OPTIONS,
    cancel_kb,
    confirm_kb,
    main_menu_kb,
    phone_kb,
    remove_kb,
    services_kb,
    skip_comment_kb,
)
from services.crm_api import submit_booking_to_api
from states.booking import BookingStates

router = Router(name="booking")

PHONE_RE = re.compile(r"\D+")


def _normalize_phone(value: str) -> str | None:
    digits = PHONE_RE.sub("", value or "")
    if digits.startswith("8") and len(digits) == 11:
        digits = "998" + digits[1:]
    if len(digits) == 9:
        digits = "998" + digits
    if len(digits) != 12 or not digits.startswith("998"):
        return None
    return f"+{digits[:3]} {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"


def _summary(data: dict) -> str:
    lines = [
        "<b>Проверьте заявку</b>",
        "",
        f"👤 Имя: {data.get('client_name')}",
        f"📱 Телефон: {data.get('phone')}",
        f"🩺 Услуга: {data.get('service_name')}",
    ]
    if data.get("appointment_date"):
        lines.append(f"🗓 Дата: {data['appointment_date']}")
    if data.get("time_slot"):
        lines.append(f"🕒 Время: {data['time_slot']}")
    if data.get("comment"):
        lines.append(f"💬 Комментарий: {data['comment']}")
    return "\n".join(lines)


async def _cancel(message: Message, state: FSMContext) -> None:
    logger.info("Booking cancelled | user_id={}", message.from_user.id if message.from_user else None)
    await state.clear()
    await message.answer("Запись отменена. Можете начать снова в любой момент.", reply_markup=main_menu_kb())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    settings = get_settings()
    logger.info(
        "User started bot | user_id={} | username={}",
        message.from_user.id if message.from_user else None,
        message.from_user.username if message.from_user else None,
    )
    await message.answer(
        "Здравствуйте! Я бот клиники <b>NeurON Medical Centre</b>.\n\n"
        "• Заявки на обратный звонок с сайта приходят сюда автоматически\n"
        "• Сотрудникам: /register — подписаться на заявки\n"
        "• /unregister — отписаться · /staff — список сотрудников\n\n"
        "📞 Колл-центр: +998 71 200 00 20\n"
        "🌐 neuronmedical.uz\n\n"
        "Также могу помочь записаться на приём прямо в чате.",
        reply_markup=main_menu_kb(),
    )
    logger.debug("Bot username setting: {}", settings.bot_username)


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await _cancel(message, state)


@router.callback_query(F.data == "booking:cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    logger.info("Booking cancelled via callback | user_id={}", callback.from_user.id)
    await callback.message.answer("Запись отменена.", reply_markup=main_menu_kb())
    await callback.answer()


@router.message(F.text == "ℹ️ О клинике NeurON")
async def about_clinic(message: Message) -> None:
    await message.answer(
        "<b>NeurON</b> — медицинский центр нейрохирургии и диагностики.\n"
        "Запись через этого бота или сайт клиники.",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "📞 Контакты")
async def contacts(message: Message) -> None:
    await message.answer(
        "Связь с клиникой NeurON:\n"
        "• Через этого бота — кнопка «Записаться на приём»\n"
        "• Или оставьте заявку на сайте",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "🩺 Записаться на приём")
@router.message(Command("book"))
async def start_booking(message: Message, state: FSMContext) -> None:
    logger.info("Booking FSM started | user_id={}", message.from_user.id if message.from_user else None)
    await state.set_state(BookingStates.waiting_name)
    await message.answer(
        "Шаг 1/6. Как зовут пациента?\nНапишите имя и фамилию.",
        reply_markup=cancel_kb(),
    )


@router.message(BookingStates.waiting_name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Укажите имя полностью (минимум 2 символа).")
        return
    await state.update_data(client_name=name)
    logger.info("FSM name saved | user_id={} | name={}", message.from_user.id, name)
    await state.set_state(BookingStates.waiting_phone)
    await message.answer(
        "Шаг 2/6. Укажите номер телефона в формате +998 XX XXX XX XX\n"
        "или нажмите кнопку ниже.",
        reply_markup=phone_kb(),
    )


@router.message(BookingStates.waiting_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext) -> None:
    phone = _normalize_phone(message.contact.phone_number if message.contact else "")
    if not phone:
        await message.answer("Не удалось распознать номер. Введите вручную: +998 XX XXX XX XX")
        return
    await state.update_data(phone=phone)
    logger.info("FSM phone (contact) | user_id={} | phone={}", message.from_user.id, phone)
    await state.set_state(BookingStates.waiting_service)
    await message.answer("Шаг 3/6. Выберите услугу / направление:", reply_markup=remove_kb())
    await message.answer("Список услуг:", reply_markup=services_kb())


@router.message(BookingStates.waiting_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отмена":
        await _cancel(message, state)
        return
    phone = _normalize_phone(message.text or "")
    if not phone:
        await message.answer("Введите корректный номер: +998 XX XXX XX XX")
        return
    await state.update_data(phone=phone)
    logger.info("FSM phone (text) | user_id={} | phone={}", message.from_user.id, phone)
    await state.set_state(BookingStates.waiting_service)
    await message.answer("Шаг 3/6. Выберите услугу / направление:", reply_markup=remove_kb())
    await message.answer("Список услуг:", reply_markup=services_kb())


@router.callback_query(BookingStates.waiting_service, F.data.startswith("svc:"))
async def process_service(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        idx = int(callback.data.split(":", 1)[1])
        service = SERVICE_OPTIONS[idx]
    except (IndexError, ValueError):
        await callback.answer("Некорректный выбор", show_alert=True)
        return

    if service == "Другая услуга":
        await state.update_data(service_name=None)
        await callback.message.answer("Напишите название нужной услуги текстом:")
        await callback.answer()
        return

    await state.update_data(service_name=service)
    logger.info("FSM service | user_id={} | service={}", callback.from_user.id, service)
    await state.set_state(BookingStates.waiting_date)
    await callback.message.answer(
        "Шаг 4/6. Желаемая дата приёма (например 20.09.2026 или 2026-09-20):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(BookingStates.waiting_service, F.text)
async def process_service_text(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отмена":
        await _cancel(message, state)
        return
    service = (message.text or "").strip()
    if len(service) < 2:
        await message.answer("Укажите услугу подробнее.")
        return
    await state.update_data(service_name=service)
    logger.info("FSM service (text) | user_id={} | service={}", message.from_user.id, service)
    await state.set_state(BookingStates.waiting_date)
    await message.answer(
        "Шаг 4/6. Желаемая дата приёма (например 20.09.2026):",
        reply_markup=cancel_kb(),
    )


@router.message(BookingStates.waiting_date, F.text)
async def process_date(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отмена":
        await _cancel(message, state)
        return
    date_val = (message.text or "").strip()
    if len(date_val) < 4:
        await message.answer("Укажите дату, например 20.09.2026")
        return
    await state.update_data(appointment_date=date_val)
    logger.info("FSM date | user_id={} | date={}", message.from_user.id, date_val)
    await state.set_state(BookingStates.waiting_time)
    await message.answer("Шаг 5/6. Желаемое время (например 10:00):", reply_markup=cancel_kb())


@router.message(BookingStates.waiting_time, F.text)
async def process_time(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отмена":
        await _cancel(message, state)
        return
    time_val = (message.text or "").strip()
    if len(time_val) < 3:
        await message.answer("Укажите время, например 10:00")
        return
    await state.update_data(time_slot=time_val)
    logger.info("FSM time | user_id={} | time={}", message.from_user.id, time_val)
    await state.set_state(BookingStates.waiting_comment)
    await message.answer(
        "Шаг 6/6. Комментарий к заявке (или нажмите «Пропустить»):",
        reply_markup=remove_kb(),
    )
    await message.answer("Комментарий:", reply_markup=skip_comment_kb())


@router.callback_query(BookingStates.waiting_comment, F.data == "booking:skip_comment")
async def skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(comment=None)
    data = await state.get_data()
    await state.set_state(BookingStates.confirm)
    logger.info("FSM comment skipped | user_id={}", callback.from_user.id)
    await callback.message.answer(_summary(data), reply_markup=confirm_kb())
    await callback.answer()


@router.message(BookingStates.waiting_comment, F.text)
async def process_comment(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отмена":
        await _cancel(message, state)
        return
    comment = (message.text or "").strip() or None
    await state.update_data(comment=comment)
    data = await state.get_data()
    await state.set_state(BookingStates.confirm)
    logger.info("FSM comment saved | user_id={}", message.from_user.id)
    await message.answer(_summary(data), reply_markup=confirm_kb())


@router.callback_query(BookingStates.confirm, F.data == "booking:confirm")
async def confirm_booking(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    settings = get_settings()

    if not data.get("service_name"):
        await callback.answer("Не выбрана услуга", show_alert=True)
        return

    payload = {
        "client_name": data.get("client_name"),
        "phone": data.get("phone"),
        "service_name": data.get("service_name"),
        "appointment_date": data.get("appointment_date"),
        "time_slot": data.get("time_slot"),
        "comment": data.get("comment"),
        "category": None,
        "source": f"Telegram @{settings.bot_username}",
        "form_type": "booking",
    }

    logger.info("FSM confirm → API | user_id={} | payload_keys={}", callback.from_user.id, list(payload.keys()))
    await callback.answer()
    await callback.message.answer("Отправляю заявку…")

    try:
        result = await submit_booking_to_api(settings, payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Booking API failed | user_id={} | error={}", callback.from_user.id, exc)
        await callback.message.answer(
            f"Не удалось отправить заявку: {exc}\nПопробуйте позже или /book",
            reply_markup=main_menu_kb(),
        )
        await state.clear()
        return

    await state.clear()
    logger.success("Booking created via @uzneuron_bot | user_id={}", callback.from_user.id)
    msg = result.get("message") or "Заявка принята. Мы свяжемся с вами."
    await callback.message.answer(f"✅ {msg}", reply_markup=main_menu_kb())


@router.message(StateFilter(BookingStates), F.text)
async def fallback_in_fsm(message: Message) -> None:
    await message.answer("Пожалуйста, ответьте на текущий шаг или нажмите «❌ Отмена» / /cancel")
