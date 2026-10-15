"""Run NeurON FastAPI (bookings + chat + static site).

  cd server
  python run.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn

from app.config import get_config, load_env
from app.logging_setup import setup_logging

logger = logging.getLogger("neuron")


def main() -> None:
    logs_dir = setup_logging()
    load_env(override=False)
    cfg = get_config()
    host = str(cfg["host"])
    port = int(cfg["port"])
    if not cfg["telegram_configured"]:
        logger.error(
            "TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID не заданы в server/.env — заявки не уйдут в Telegram"
        )
    else:
        logger.info(
            "Telegram OK | token=%s | chat_id=%s",
            cfg.get("telegram_token_masked"),
            cfg.get("telegram_chat_id_masked"),
        )
    logger.info("NeurON API: http://%s:%s/", host, port)
    logger.info("Callback: POST /api/request-callback")
    logger.info("Logs directory: %s", logs_dir)
    uvicorn.run("app.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
