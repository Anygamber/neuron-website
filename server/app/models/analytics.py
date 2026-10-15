"""Page visit hits for lightweight site analytics."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PageVisit(Base):
    __tablename__ = "page_visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True, nullable=False
    )
    path: Mapped[str] = mapped_column(String(500), nullable=False, default="/")
    lang: Mapped[str] = mapped_column(String(8), nullable=False, default="uz", index=True)
    referrer: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="direct", index=True)
    visitor_id: Mapped[str] = mapped_column(String(64), nullable=False, default="", index=True)
    user_agent: Mapped[str] = mapped_column(String(400), nullable=False, default="")
