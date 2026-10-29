"""CRUD for clinic staff Telegram subscribers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.staff import StaffSubscriber


def list_active_staff(db: Session) -> list[StaffSubscriber]:
    return list(
        db.scalars(
            select(StaffSubscriber).where(StaffSubscriber.active.is_(True)).order_by(StaffSubscriber.id)
        ).all()
    )


def list_all_staff(db: Session) -> list[StaffSubscriber]:
    return list(db.scalars(select(StaffSubscriber).order_by(StaffSubscriber.id)).all())


def register_staff(
    db: Session,
    *,
    telegram_id: int,
    display_name: str,
    username: str | None = None,
) -> StaffSubscriber:
    row = db.scalar(select(StaffSubscriber).where(StaffSubscriber.telegram_id == int(telegram_id)))
    name = (display_name or "").strip() or "Сотрудник"
    uname = (username or "").strip().lstrip("@") or None
    if row:
        row.display_name = name[:200]
        row.username = uname[:128] if uname else row.username
        row.active = True
    else:
        row = StaffSubscriber(
            telegram_id=int(telegram_id),
            display_name=name[:200],
            username=uname[:128] if uname else None,
            active=True,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


def unregister_staff(db: Session, telegram_id: int) -> bool:
    row = db.scalar(select(StaffSubscriber).where(StaffSubscriber.telegram_id == int(telegram_id)))
    if not row:
        return False
    row.active = False
    db.commit()
    return True


def active_chat_ids(db: Session) -> list[int]:
    return [int(s.telegram_id) for s in list_active_staff(db)]
