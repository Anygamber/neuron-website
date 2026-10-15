"""File + console logging for NeurON API / Telegram delivery."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import SERVER_DIR

_LOGS_DIR = SERVER_DIR / "logs"
_CONFIGURED = False


def setup_logging() -> Path:
    global _CONFIGURED
    _LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if _CONFIGURED:
        return _LOGS_DIR

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Avoid duplicate handlers on reload
    for h in list(root.handlers):
        root.removeHandler(h)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console.setLevel(logging.INFO)
    root.addHandler(console)

    api_file = RotatingFileHandler(
        _LOGS_DIR / "api.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    api_file.setFormatter(fmt)
    api_file.setLevel(logging.INFO)
    root.addHandler(api_file)

    tg_file = RotatingFileHandler(
        _LOGS_DIR / "telegram.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    tg_file.setFormatter(fmt)
    tg_file.setLevel(logging.INFO)
    logging.getLogger("neuron.telegram").addHandler(tg_file)
    logging.getLogger("neuron.telegram").propagate = True

    _CONFIGURED = True
    logging.getLogger("neuron.api").info("Logging to %s", _LOGS_DIR)
    return _LOGS_DIR
