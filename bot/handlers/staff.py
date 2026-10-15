"""Staff registration: employees who receive website callback leads."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from loguru import logger

from keyboards.booking import main_menu_kb
from services.staff_api import list_staff, register_staff, unregister_staff

router = Router(name="staff")


class StaffRegStates(StatesGroup):
    waiting_name = State()


@router.message(Command("register"))
@router.message(F.text.casefold() == "регистрация сотрудника")
async def cmd_register(message: Message, state: FSMContext) -> None:
    """Start staff registration — this chat will receive callback leads."""
    await state.set_state(StaffRegStates.waiting_name)
    suggested = ""
    if message.from_user:
        parts = [message.from_user.first_name or "", message.from_user.last_name or ""]
        suggested = " ".join(p for p in parts if p).strip()
    hint = f"\n\nМожно просто отправить: <b>{suggested}</b>" if suggested else ""
    await message.answer(
        "🧑‍⚕️ <b>Регистрация сотрудника NeurON</b>\n\n"
        "После регистрации сюда будут приходить заявки на обратный звонок с сайта "
        "(имя, телефон, направление, дата и время заявки).\n\n"
        "Напишите, как вас подписать в списке сотрудников"
        f"{hint}\n\n"
        "Или /cancel чтобы отменить.",
    )


@router.message(StaffRegStates.waiting_name, Command("cancel"))
@router.message(StaffRegStates.waiting_name, F.text == "❌ Отмена")
async def reg_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Регистрация отменена.", reply_markup=main_menu_kb())


@router.message(StaffRegStates.waiting_name, F.text)
async def reg_save_name(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить ваш Telegram ID.")
        return
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Укажите имя не короче 2 символов.")
        return
    try:
        result = register_staff(
            telegram_id=message.from_user.id,
            display_name=name,
            username=message.from_user.username,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Staff register API failed | user_id={}", message.from_user.id)
        await message.answer(
            f"Не удалось зарегистрировать: {exc}\n"
            "Проверьте, что API запущен (server) и API_BEARER_TOKEN совпадает."
        )
        return

    await state.clear()
    logger.success(
        "Staff registered | telegram_id={} | name={}",
        message.from_user.id,
        name,
    )
    await message.answer(
        "✅ <b>Вы зарегистрированы</b> как получатель заявок.\n\n"
        f"👤 Имя: {result.get('display_name', name)}\n"
        f"🆔 Telegram ID: <code>{message.from_user.id}</code>\n\n"
        "Новые заявки с сайта будут приходить в этот чат.\n"
        "Отписаться: /unregister",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("unregister"))
async def cmd_unregister(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        return
    try:
        unregister_staff(telegram_id=message.from_user.id)
    except Exception as exc:  # noqa: BLE001
        await message.answer(f"Не удалось отписаться: {exc}")
        return
    await message.answer(
        "🔕 Вы больше не получаете заявки на обратный звонок.\n"
        "Снова подписаться: /register",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("staff"))
async def cmd_staff_list(message: Message) -> None:
    """List registered staff (for admins / self-check)."""
    try:
        data = list_staff()
    except Exception as exc:  # noqa: BLE001
        await message.answer(f"Не удалось получить список: {exc}")
        return
    items = data.get("items") or []
    active = [i for i in items if i.get("active")]
    if not active:
        await message.answer("Пока нет активных сотрудников. Команда: /register")
        return
    lines = ["👥 <b>Сотрудники, получающие заявки</b>", ""]
    for i, row in enumerate(active, 1):
        uname = f" @{row['username']}" if row.get("username") else ""
        lines.append(f"{i}. {row.get('display_name')}{uname} — <code>{row.get('telegram_id')}</code>")
    await message.answer("\n".join(lines))


@router.message(StateFilter(None), F.text == "🧑‍⚕️ Регистрация сотрудника")
async def menu_register(message: Message, state: FSMContext) -> None:
    await cmd_register(message, state)
