"""SQLAlchemy engine / session for NeurON (SQLite auto-create on startup)."""

from __future__ import annotations

import logging
from collections.abc import Generator
from pathlib import Path
from urllib.parse import unquote, urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import DATA_DIR, get_config

logger = logging.getLogger("neuron.api")


class Base(DeclarativeBase):
    pass


def _sqlite_path_from_url(url: str) -> Path | None:
    """Return filesystem path for sqlite:///... URL, else None."""
    if not url.startswith("sqlite:"):
        return None
    # sqlite:////abs/path or sqlite:///rel/path or sqlite:///:memory:
    raw = urlparse(url)
    # path may be like /C:/... on Windows absolute URLs
    path = unquote(raw.path or "")
    if not path or path == "/:memory:":
        return None
    # sqlite:///C:/foo → path /C:/foo on some parsers; sqlite:////var/db → /var/db
    if path.startswith("/") and len(path) > 2 and path[2] == ":":
        path = path.lstrip("/")
    return Path(path)


def _ensure_sqlite_parent(url: str) -> None:
    """Create parent directory for the SQLite file if missing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_path = _sqlite_path_from_url(url)
    if db_path is None:
        return
    parent = db_path.parent
    if str(parent) and str(parent) != ".":
        parent.mkdir(parents=True, exist_ok=True)


def _make_engine():
    cfg = get_config()
    url = str(cfg["database_url"])
    _ensure_sqlite_parent(url)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def _migrate_sqlite() -> None:
    cfg = get_config()
    if not str(cfg["database_url"]).startswith("sqlite"):
        return
    with engine.begin() as conn:
        cols = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(chat_sessions)")).fetchall()
        }
        if cols and "telegram_topic_id" not in cols:
            conn.execute(
                text("ALTER TABLE chat_sessions ADD COLUMN telegram_topic_id INTEGER")
            )


def init_db() -> None:
    """Create SQLite file + tables if they do not exist yet."""
    cfg = get_config()
    url = str(cfg["database_url"])
    _ensure_sqlite_parent(url)

    # Import models so metadata is populated
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_sqlite()

    db_path = _sqlite_path_from_url(url)
    if db_path is not None:
        logger.info("SQLite ready: %s (exists=%s)", db_path, db_path.is_file())
    else:
        logger.info("Database ready: %s", url)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
