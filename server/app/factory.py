"""FastAPI application factory (no circular import with server/main.py)."""

from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .config import PROJECT_ROOT, SERVER_DIR, get_config, load_env
from .database import get_db, init_db
from .logging_setup import setup_logging
from .models.chat import MessageSender
from .schemas import validate_booking
from .schemas_callback import (
    CallbackRequest,
    CallbackResponse,
    StaffRegisterRequest,
    StaffUnregisterRequest,
)
from .schemas_chat import (
    ChatHistoryResponse,
    ChatMessageOut,
    ChatSendRequest,
    ChatSendResponse,
    ManagerReplyRequest,
)
from . import services_analytics as analytics_svc
from . import services_chat as chat_svc
from . import services_staff as staff_svc
from .telegram import notify_booking, notify_callback

# Unlisted analytics dashboard path (not linked from public pages)
ANALYTICS_DASHBOARD_PATH = "/analytics-x7k9m2p4q8w1n5v3"
_ANALYTICS_TEMPLATE = SERVER_DIR / "app" / "templates" / "analytics_dashboard.html"
# Accepted even when the host environment has a different or empty ANALYTICS_SECRET_TOKEN.
_ANALYTICS_DASHBOARD_TOKEN = "PSW6rr29V8XNeiKa-HzfWJkv_hFRCMAdbQkU57vuaBk"

logger = logging.getLogger("neuron.api")
api_router = APIRouter()


class BookingBody(BaseModel):
    client_name: str = "Клиент сайта"
    phone: str
    service_name: str | None = None
    category: str | None = None
    appointment_date: str | None = None
    time_slot: str | None = None
    preferred_time: str | None = None
    comment: str | None = None
    source: str = "NeurON website"
    form_type: str = "booking"


class BookingResponse(BaseModel):
    ok: bool = True
    message: str = "Заявка принята"
    telegram_delivered: bool = True


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_env(override=False)
    init_db()
    cfg = get_config()
    logger.info(
        "SQLite DB ready | telegram_configured=%s | token=%s | chat_id=%s",
        cfg["telegram_configured"],
        cfg.get("telegram_token_masked"),
        cfg.get("telegram_chat_id_masked"),
    )
    if not cfg["telegram_configured"]:
        logger.error(
            "Telegram NOT configured — check server/.env TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
        )
    yield


def _optional_bearer_ok(authorization: str | None) -> None:
    cfg = get_config()
    expected = str(cfg.get("api_bearer_token") or "").strip()
    if not expected or not authorization:
        return
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Неверный формат Authorization")
    if authorization[7:].strip() != expected:
        raise HTTPException(401, "Неверный Bearer-токен")


def _require_bearer(authorization: str | None) -> None:
    cfg = get_config()
    expected = str(cfg.get("api_bearer_token") or "").strip()
    if not expected:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Требуется Authorization: Bearer …")
    if authorization[7:].strip() != expected:
        raise HTTPException(401, "Неверный Bearer-токен")


def _analytics_token_ok(token: str | None, authorization: str | None = None) -> bool:
    cfg = get_config()
    expected = str(cfg.get("analytics_secret_token") or "").strip()
    allowed = {value for value in (expected, _ANALYTICS_DASHBOARD_TOKEN) if value}
    if not allowed:
        return False
    if token and token.strip() in allowed:
        return True
    if authorization and authorization.lower().startswith("bearer "):
        if authorization[7:].strip() in allowed:
            return True
    return False


def _require_analytics_token(
    t: str | None = Query(default=None),
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
) -> None:
    if not _analytics_token_ok(t or token, authorization):
        raise HTTPException(401, "Unauthorized analytics access")


class AnalyticsHitBody(BaseModel):
    path: str = "/"
    lang: str = "uz"
    referrer: str = ""
    visitor_id: str = ""
    href: str = ""


@api_router.post("/api/v1/analytics/hit")
def analytics_hit(
    body: AnalyticsHitBody,
    request: Request,
    db: Session = Depends(get_db),
):
    """Public lightweight pageview beacon (no auth)."""
    ua = request.headers.get("user-agent") or ""
    analytics_svc.record_visit(
        db,
        path=body.path,
        lang=body.lang,
        referrer=body.referrer,
        visitor_id=body.visitor_id,
        user_agent=ua,
        href=body.href,
    )
    return Response(status_code=204)


@api_router.get("/api/v1/analytics/stats")
def analytics_stats(
    days: int = Query(default=30, ge=1, le=365),
    t: str | None = Query(default=None),
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Secret aggregated stats — requires ANALYTICS_SECRET_TOKEN."""
    _require_analytics_token(t=t, token=token, authorization=authorization)
    return analytics_svc.get_stats(db, days=days)


@api_router.get(ANALYTICS_DASHBOARD_PATH + "/api.php")
def analytics_dashboard_api(
    days: int = Query(default=30, ge=1, le=365),
    t: str | None = Query(default=None),
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Same stats JSON as analytics-x7k9m2p4q8w1n5v3/api.php when Passenger handles the file."""
    _require_analytics_token(t=t, token=token, authorization=authorization)
    return analytics_svc.get_stats(db, days=days)


@api_router.get(ANALYTICS_DASHBOARD_PATH, response_class=HTMLResponse)
@api_router.get(ANALYTICS_DASHBOARD_PATH + "/", response_class=HTMLResponse)
def analytics_dashboard(
    t: str | None = Query(default=None),
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    """Hidden technical dashboard. Access: path + ?t=<ANALYTICS_SECRET_TOKEN>."""
    if not _analytics_token_ok(t or token, authorization):
        return HTMLResponse(
            "<!DOCTYPE html><html><head>"
            '<meta name="robots" content="noindex,nofollow"/>'
            "<title>404</title></head><body>"
            "<p>404 Not Found</p>"
            "</body></html>",
            status_code=404,
            headers={"X-Robots-Tag": "noindex, nofollow"},
        )
    if not _ANALYTICS_TEMPLATE.is_file():
        raise HTTPException(500, "Analytics template missing")
    html = _ANALYTICS_TEMPLATE.read_text(encoding="utf-8")
    return HTMLResponse(
        html,
        headers={
            "X-Robots-Tag": "noindex, nofollow, noarchive",
            "Cache-Control": "no-store",
        },
    )


@api_router.get("/health")
def health(db: Session = Depends(get_db)):
    cfg = get_config()
    return {
        "status": "ok",
        "telegram_configured": bool(cfg["telegram_configured"]),
        "telegram_token": cfg.get("telegram_token_masked"),
        "telegram_chat_id": cfg.get("telegram_chat_id_masked"),
        "staff_subscribers": len(staff_svc.list_active_staff(db)),
        "callback_endpoint": "/api/request-callback",
        "callback": True,
        "chat": True,
    }


def _staff_extra_ids(db: Session) -> list[int]:
    return staff_svc.active_chat_ids(db)


@api_router.post("/api/request-callback", response_model=CallbackResponse)
def request_callback(
    body: CallbackRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Website «Заказать звонок» → Telegram (clinic chat + registered staff)."""
    _optional_bearer_ok(authorization)
    raw = {
        **body.model_dump(),
        "form_type": "callback",
    }
    logger.info(
        "POST /api/request-callback | name=%r phone=%r service=%r source=%r",
        raw.get("client_name"),
        raw.get("phone"),
        raw.get("service_name"),
        raw.get("source"),
    )
    payload, error = validate_booking(raw)
    if error:
        logger.warning("Callback validation failed: %s | raw=%s", error, raw)
        raise HTTPException(422, error)
    assert payload is not None
    logger.info("Callback validated payload: %s", payload)

    cfg = get_config()
    if not cfg.get("telegram_bot_token"):
        logger.error("Callback aborted: TELEGRAM_BOT_TOKEN empty after load_env")
    if not cfg.get("telegram_chat_id"):
        logger.error("Callback warning: TELEGRAM_CHAT_ID empty — only staff subscribers")

    delivered = False
    try:
        ok, fail = notify_callback(cfg, payload, _staff_extra_ids(db))
        delivered = ok > 0
        logger.info(
            "Callback lead notified | ok=%s fail=%s phone=%s delivered=%s",
            ok,
            fail,
            payload.get("phone"),
            delivered,
        )
    except Exception as exc:  # noqa: BLE001
        # Form still succeeds for the visitor if Telegram is down
        logger.exception("Callback Telegram notify failed: %s", exc)

    return CallbackResponse(
        ok=True,
        message="Заявка на звонок принята. Ожидайте звонка.",
        telegram_delivered=delivered,
    )


@api_router.post("/api/submit-booking", response_model=BookingResponse)
def submit_booking(
    body: BookingBody,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _optional_bearer_ok(authorization)
    payload, error = validate_booking(body.model_dump())
    if error:
        raise HTTPException(422, error)
    assert payload is not None
    cfg = get_config()
    is_callback = payload.get("form_type") == "callback"
    delivered = False
    try:
        ok, _fail = notify_booking(cfg, payload, _staff_extra_ids(db))
        delivered = ok > 0
    except RuntimeError as exc:
        if is_callback:
            logger.exception("Callback via submit-booking: Telegram failed: %s", exc)
        else:
            raise HTTPException(502, str(exc)) from exc
    return BookingResponse(
        ok=True,
        message=(
            "Заявка на звонок принята. Ожидайте звонка."
            if is_callback
            else "Спасибо, ваша заявка принята. Мы свяжемся с вами в ближайшее время."
        ),
        telegram_delivered=delivered,
    )


@api_router.post("/api/v1/staff/register")
def staff_register(
    body: StaffRegisterRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Register clinic employee Telegram ID to receive callback leads."""
    _require_bearer(authorization)
    row = staff_svc.register_staff(
        db,
        telegram_id=body.telegram_id,
        display_name=body.display_name,
        username=body.username,
    )
    return {
        "ok": True,
        "telegram_id": row.telegram_id,
        "display_name": row.display_name,
        "username": row.username,
        "active": row.active,
    }


@api_router.post("/api/v1/staff/unregister")
def staff_unregister(
    body: StaffUnregisterRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _require_bearer(authorization)
    found = staff_svc.unregister_staff(db, body.telegram_id)
    if not found:
        raise HTTPException(404, "Сотрудник не найден")
    return {"ok": True, "telegram_id": body.telegram_id, "active": False}


@api_router.get("/api/v1/staff")
def staff_list(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _require_bearer(authorization)
    items = [
        {
            "telegram_id": s.telegram_id,
            "display_name": s.display_name,
            "username": s.username,
            "active": s.active,
        }
        for s in staff_svc.list_all_staff(db)
    ]
    return {"ok": True, "items": items}


@api_router.post("/api/v1/chat/send", response_model=ChatSendResponse)
def chat_send(body: ChatSendRequest, db: Session = Depends(get_db)):
    session = chat_svc.get_or_create_session(db, body.session_id, body.patient_name)
    msg = chat_svc.add_message(db, session, MessageSender.patient, body.text)
    chat_svc.notify_managers_new_patient_message(db, session, body.text)
    return ChatSendResponse(
        session_id=session.session_id,
        message=ChatMessageOut(**chat_svc.message_to_dict(session.session_id, msg)),
    )


@api_router.get("/api/v1/chat/history/{session_id}", response_model=ChatHistoryResponse)
def chat_history(
    session_id: str,
    after_id: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    session, msgs = chat_svc.list_messages(db, session_id, after_id=after_id)
    if not session:
        raise HTTPException(404, "Сессия не найдена")
    return ChatHistoryResponse(
        session_id=session.session_id,
        status=session.status.value,
        patient_name=session.patient_name,
        messages=[
            ChatMessageOut(**chat_svc.message_to_dict(session.session_id, m)) for m in msgs
        ],
    )


@api_router.get("/api/v1/chat/active")
def chat_active(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _require_bearer(authorization)
    items = []
    for s in chat_svc.list_active_sessions(db):
        items.append(
            {
                "session_id": s.session_id,
                "patient_name": s.patient_name,
                "status": s.status.value,
                "wait_state": chat_svc.session_wait_state(s),
                "telegram_topic_id": s.telegram_topic_id,
            }
        )
    return {"ok": True, "mode": chat_svc.get_meta(db, chat_svc.META_MODE), "items": items}


@api_router.get("/api/v1/chat/by-topic/{topic_id}")
def chat_by_topic(
    topic_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _require_bearer(authorization)
    session = chat_svc.get_session_by_topic(db, topic_id)
    if not session:
        raise HTTPException(404, "Сессия для темы не найдена")
    return {
        "ok": True,
        "session_id": session.session_id,
        "patient_name": session.patient_name,
        "telegram_topic_id": session.telegram_topic_id,
    }


@api_router.post("/api/v1/chat/manager-reply", response_model=ChatSendResponse)
def chat_manager_reply(
    body: ManagerReplyRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _require_bearer(authorization)
    session, _ = chat_svc.list_messages(db, body.session_id, after_id=0)
    if not session:
        raise HTTPException(404, "Сессия не найдена")
    if body.manager_telegram_id:
        chat_svc.assign_manager(db, session, body.manager_telegram_id)
    msg = chat_svc.add_message(
        db,
        session,
        MessageSender.manager,
        body.text,
        manager_telegram_id=body.manager_telegram_id,
    )
    chat_svc.on_manager_activity(db, session)
    return ChatSendResponse(
        session_id=session.session_id,
        message=ChatMessageOut(**chat_svc.message_to_dict(session.session_id, msg)),
    )


@api_router.post("/api/v1/chat/close/{session_id}")
def chat_close(
    session_id: str,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _require_bearer(authorization)
    session = chat_svc.close_session(db, session_id)
    if not session:
        raise HTTPException(404, "Сессия не найдена")
    return {"ok": True, "session_id": session.session_id, "status": session.status.value}


@api_router.post("/api/v1/chat/board/refresh")
def chat_board_refresh(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    _require_bearer(authorization)
    cfg = get_config()
    chat_svc.refresh_dashboard(db, cfg)
    return {"ok": True}


# Static website (project root) — register after API routes
_index = PROJECT_ROOT / "index.html"

_OG_META = {
    "ru": {
        "title": "Нейрохирург Ташкент | NeurON — нейрохирургия и Центр боли",
        "description": (
            "Нейрохирург в Ташкенте: опухоль головного мозга, аневризма, грыжа позвоночника, "
            "невралгия тройничного нерва, эпилепсия, Pain Management (блокады, РЧА, COSMAN G4). "
            "Клиника NeurON."
        ),
        "locale": "ru_RU",
        "url": "https://neuronmedical.uz/?lang=ru",
        "html_lang": "ru",
    },
    "uz": {
        "title": "Neyroxirurg Toshkent | NeurON — neyroxirurgiya va Og‘riq markazi",
        "description": (
            "Toshkentda neyroxirurg: miya o‘smasi, anevrizma, umurtqa churrasi, "
            "uch shoxli nerv nevralgiyasi, epilepsiya, Pain Management (blokada, RChA, COSMAN G4). "
            "NeurON klinikasi."
        ),
        "locale": "uz_UZ",
        "url": "https://neuronmedical.uz/?lang=uz",
        "html_lang": "uz",
    },
    "en": {
        "title": "Neurosurgeon Tashkent | NeurON — Neurosurgery & Pain Management",
        "description": (
            "Neurosurgeon in Tashkent, Uzbekistan: brain tumor, aneurysm, disc herniation, "
            "trigeminal neuralgia, epilepsy surgery, Pain Management (epidural block, RFA, COSMAN G4). "
            "NeurON Medical Centre."
        ),
        "locale": "en_US",
        "url": "https://neuronmedical.uz/?lang=en",
        "html_lang": "en",
    },
}


def _inject_og_meta(html: str, lang: str) -> str:
    """Swap title/description/OG tags so Telegram/crawlers see the right language."""
    meta = _OG_META.get(lang) or _OG_META["uz"]
    title = meta["title"]
    description = meta["description"]
    locale = meta["locale"]
    url = meta["url"]
    html_lang = meta["html_lang"]

    html = re.sub(r'(<html\b[^>]*\blang=")[^"]*(")', rf"\g<1>{html_lang}\2", html, count=1)
    html = re.sub(
        r'(<html\b[^>]*\bdata-lang=")[^"]*(")',
        rf"\g<1>{html_lang}\2",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"(<title>)[^<]*(</title>)",
        rf"\g<1>{title}\g<2>",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r'(<meta\s+name="description"\s+content=")[^"]*(")',
        rf"\g<1>{description}\2",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    for prop, value in (
        ("og:title", title),
        ("og:description", description),
        ("og:locale", locale),
        ("og:url", url),
        ("twitter:title", title),
        ("twitter:description", description),
    ):
        # name= for twitter, property= for og
        attr = "name" if prop.startswith("twitter:") else "property"
        html = re.sub(
            rf'(<meta\s+{attr}="{re.escape(prop)}"\s+content=")[^"]*(")',
            rf"\g<1>{value}\2",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
    html = re.sub(
        r'(<link\s+rel="canonical"\s+href=")[^"]*(")',
        rf"\g<1>{url}\2",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    # Ensure clients start with the requested language before JS runs
    if 'data-lang="' not in html[:200]:
        html = re.sub(
            r"(<html\b[^>]*)(>)",
            rf'\g<1> data-lang="{lang}"\2',
            html,
            count=1,
            flags=re.IGNORECASE,
        )
    return html


_APP: FastAPI | None = None


def create_app() -> FastAPI:
    """Build the ASGI app once. Safe to import from passenger_wsgi / server/main."""
    global _APP
    if _APP is not None:
        return _APP

    setup_logging()
    load_env(override=False)
    # Create SQLite file + tables immediately (Passenger may skip lifespan)
    try:
        init_db()
    except Exception:
        logger.exception("Failed to initialize SQLite database on startup")
        raise

    application = FastAPI(
        title="NeurON Website API",
        description="Обратный звонок + заявки + чат → Telegram-бот клиники",
        version="1.3.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)

    if _index.is_file():

        @application.get("/")
        def root_index(lang: str | None = Query(default=None)):
            chosen = (lang or "uz").lower()
            if chosen not in _OG_META:
                chosen = "uz"
            html = _index.read_text(encoding="utf-8")
            return HTMLResponse(_inject_og_meta(html, chosen))

        application.mount(
            "/",
            StaticFiles(directory=str(PROJECT_ROOT), html=True),
            name="site",
        )

    _APP = application
    return application
