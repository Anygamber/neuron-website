"""Record and aggregate page visits."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analytics import PageVisit


def classify_source(referrer: str, href: str = "") -> str:
    """Map referrer / UTM into coarse traffic buckets."""
    ref = (referrer or "").strip().lower()
    href_l = (href or "").strip().lower()

    qs = ""
    try:
        qs = urlparse(href_l).query
    except Exception:
        qs = ""
    params = parse_qs(qs)
    utm_medium = (params.get("utm_medium") or [""])[0].lower()
    utm_source = (params.get("utm_source") or [""])[0].lower()
    has_gclid = "gclid" in params or "fbclid" in params or "yclid" in params

    if has_gclid or utm_medium in {"cpc", "ppc", "paid", "paidsocial", "display", "retargeting"}:
        return "ads"
    if utm_source in {"facebook", "fb", "instagram", "ig", "telegram", "vk", "tiktok"} and utm_medium in {
        "cpc",
        "paid",
        "paidsocial",
    }:
        return "ads"

    if not ref:
        if utm_source:
            if utm_source in {"facebook", "fb", "instagram", "ig", "telegram", "t.me", "vk", "twitter", "x", "youtube"}:
                return "social"
            if utm_source in {"google", "yandex", "bing"}:
                return "search"
            return "referral"
        return "direct"

    host = ""
    try:
        host = (urlparse(ref).hostname or "").lower()
    except Exception:
        host = ref

    if any(
        x in host
        for x in (
            "facebook.com",
            "fb.com",
            "instagram.com",
            "t.me",
            "telegram.org",
            "vk.com",
            "twitter.com",
            "x.com",
            "linkedin.com",
            "youtube.com",
            "tiktok.com",
            "ok.ru",
        )
    ):
        return "social"

    if any(x in host for x in ("google.", "yandex.", "bing.com", "duckduckgo.com", "yahoo.")):
        return "search"

    if "neuronmedical" in host or host in {"localhost", "127.0.0.1"}:
        return "direct"

    return "referral"


def record_visit(
    db: Session,
    *,
    path: str,
    lang: str,
    referrer: str,
    visitor_id: str,
    user_agent: str,
    href: str = "",
) -> PageVisit:
    clean_path = (path or "/")[:500]
    clean_lang = (lang or "uz").lower()[:8]
    if clean_lang not in {"ru", "uz", "en"}:
        clean_lang = "uz"
    clean_ref = (referrer or "")[:1000]
    clean_vid = (visitor_id or "")[:64] or "anonymous"
    clean_ua = (user_agent or "")[:400]
    source = classify_source(clean_ref, href)

    row = PageVisit(
        path=clean_path,
        lang=clean_lang,
        referrer=clean_ref,
        source=source,
        visitor_id=clean_vid,
        user_agent=clean_ua,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _bucket_counts(rows: list[tuple[str, int]]) -> dict[str, int]:
    return {str(k): int(v) for k, v in rows if k is not None}


def get_stats(db: Session, *, days: int = 30) -> dict:
    days = max(1, min(int(days or 30), 365))
    since = datetime.now(timezone.utc) - timedelta(days=days)

    geo_prefix = "/geo-click/"
    is_geo = PageVisit.path.like(geo_prefix + "%")
    is_page = ~is_geo

    total = db.query(func.count(PageVisit.id)).filter(is_page).scalar() or 0
    period_total = (
        db.query(func.count(PageVisit.id))
        .filter(is_page, PageVisit.created_at >= since)
        .scalar()
        or 0
    )
    unique_all = (
        db.query(func.count(func.distinct(PageVisit.visitor_id))).filter(is_page).scalar() or 0
    )
    unique_period = (
        db.query(func.count(func.distinct(PageVisit.visitor_id)))
        .filter(is_page, PageVisit.created_at >= since)
        .scalar()
        or 0
    )

    by_lang = _bucket_counts(
        db.query(PageVisit.lang, func.count(PageVisit.id))
        .filter(is_page, PageVisit.created_at >= since)
        .group_by(PageVisit.lang)
        .all()
    )
    by_source = _bucket_counts(
        db.query(PageVisit.source, func.count(PageVisit.id))
        .filter(is_page, PageVisit.created_at >= since)
        .group_by(PageVisit.source)
        .all()
    )
    geo_rows = (
        db.query(PageVisit.path, func.count(PageVisit.id))
        .filter(is_geo, PageVisit.created_at >= since)
        .group_by(PageVisit.path)
        .order_by(func.count(PageVisit.id).desc())
        .all()
    )

    # SQLite: date(created_at) / strftime hour
    by_day_rows = (
        db.query(func.strftime("%Y-%m-%d", PageVisit.created_at), func.count(PageVisit.id))
        .filter(is_page, PageVisit.created_at >= since)
        .group_by(func.strftime("%Y-%m-%d", PageVisit.created_at))
        .order_by(func.strftime("%Y-%m-%d", PageVisit.created_at))
        .all()
    )
    by_hour_rows = (
        db.query(func.strftime("%H", PageVisit.created_at), func.count(PageVisit.id))
        .filter(is_page, PageVisit.created_at >= since)
        .group_by(func.strftime("%H", PageVisit.created_at))
        .order_by(func.strftime("%H", PageVisit.created_at))
        .all()
    )
    top_paths = (
        db.query(PageVisit.path, func.count(PageVisit.id))
        .filter(is_page, PageVisit.created_at >= since)
        .group_by(PageVisit.path)
        .order_by(func.count(PageVisit.id).desc())
        .limit(15)
        .all()
    )

    hours = {f"{i:02d}": 0 for i in range(24)}
    for h, c in by_hour_rows:
        key = str(h).zfill(2) if h is not None else "00"
        hours[key] = int(c)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days": days,
        "totals": {
            "pageviews_all": int(total),
            "pageviews_period": int(period_total),
            "unique_visitors_all": int(unique_all),
            "unique_visitors_period": int(unique_period),
        },
        "by_lang": by_lang,
        "by_source": by_source,
        "geo_clicks": [
            {"map": str(path)[len(geo_prefix) :] or "map", "views": int(count)}
            for path, count in geo_rows
        ],
        "by_day": [{"date": str(d), "views": int(c)} for d, c in by_day_rows if d],
        "by_hour": [{"hour": h, "views": hours[h]} for h in sorted(hours.keys())],
        "top_paths": [{"path": str(p), "views": int(c)} for p, c in top_paths],
    }
