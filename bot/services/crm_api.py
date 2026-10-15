"""POST booking JSON to NeurON API with Bearer auth."""

from __future__ import annotations

import json
from typing import Any

import aiohttp
from loguru import logger

from core.config import Settings


async def submit_booking_to_api(settings: Settings, payload: dict[str, Any]) -> dict[str, Any]:
    """Send completed FSM data to POST /api/submit-booking."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    token = settings.api_bearer_token.strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = settings.booking_api_url.strip()
    logger.info(
        "Submitting booking to API | url={} | patient={} | phone={}",
        url,
        payload.get("client_name"),
        payload.get("phone"),
    )
    logger.debug("Booking JSON: {}", json.dumps(payload, ensure_ascii=False))

    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            text = await resp.text()
            logger.info("API response status={} body={}", resp.status, text[:500])
            if resp.status >= 400:
                try:
                    data = json.loads(text)
                    detail = data.get("detail") or data.get("message") or text
                except json.JSONDecodeError:
                    detail = text or f"HTTP {resp.status}"
                raise RuntimeError(str(detail))
            try:
                return json.loads(text) if text else {"ok": True}
            except json.JSONDecodeError:
                return {"ok": True, "message": text}
