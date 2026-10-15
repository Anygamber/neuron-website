"""NeurON Telegram bot — @uzneuron_bot

Запуск (рядом с API на :8000):
  cd bot
  python main.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

# Allow `python main.py` from bot/
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import get_settings
from handlers.booking import router as booking_router
from handlers.chat import router as chat_router
from handlers.staff import router as staff_router


def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    logger.add(
        logs / "uzneuron_bot.log",
        rotation="5 MB",
        retention="14 days",
        level="DEBUG",
        encoding="utf-8",
    )


async def main() -> None:
    setup_logging()
    settings = get_settings()

    if not settings.telegram_bot_token.strip():
        logger.error("TELEGRAM_BOT_TOKEN пуст — укажите токен в server/.env")
        raise SystemExit(1)

    # Mask token in logs
    tok = settings.telegram_bot_token
    masked = f"{tok[:10]}…{tok[-4:]}" if len(tok) > 16 else "***"
    logger.info("Starting bot | token={}", masked)
    logger.info("API base: {}", settings.api_base_url)
    logger.info("Callback API: {}", settings.callback_api_url)
    logger.info("Admin chat_id: {}", settings.telegram_chat_id)

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(staff_router)
    dp.include_router(chat_router)
    dp.include_router(booking_router)

    me = await bot.get_me()
    logger.success("Connected as @{} (id={})", me.username, me.id)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Polling started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
