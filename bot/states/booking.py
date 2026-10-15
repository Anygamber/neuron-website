"""FSM states for NeurON appointment booking in Telegram."""

from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_service = State()
    waiting_date = State()
    waiting_time = State()
    waiting_comment = State()
    confirm = State()
