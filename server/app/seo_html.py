"""Inject per-language title, description, and canonical into the homepage.

Apache ``index.php`` applies the same replacements. Both read ``seo-meta.json``
so a crawler that does not run JavaScript still sees the ``?lang=`` variant.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from html import escape

from .config import PROJECT_ROOT

_META_PATH = PROJECT_ROOT / "seo-meta.json"


@lru_cache(maxsize=1)
def load_catalog() -> dict:
    data = json.loads(_META_PATH.read_text(encoding="utf-8"))
    languages = data.get("languages")
    if not isinstance(languages, dict) or not languages:
        raise RuntimeError(f"seo-meta.json has no languages: {_META_PATH}")
    return data


def resolve_lang(lang: str | None) -> str:
    catalog = load_catalog()
    chosen = (lang or "").strip().lower()
    if chosen in catalog["languages"]:
        return chosen
    return str(catalog.get("default") or "uz")


def _swap(html: str, pattern: str, value: str) -> str:
    escaped = escape(value, quote=True)

    def repl(match: re.Match[str]) -> str:
        return f"{match.group(1)}{escaped}{match.group(2)}"

    updated, _count = re.subn(pattern, repl, html, count=1, flags=re.IGNORECASE)
    return updated


def inject_lang_meta(html: str, lang: str) -> tuple[str, str]:
    """Return HTML with head tags for ``lang``, and the BCP 47 html lang code."""
    catalog = load_catalog()
    code = resolve_lang(lang)
    pack = catalog["languages"][code]
    html_lang = str(pack["htmlLang"])
    title = str(pack["title"])
    description = str(pack["description"])
    keywords = str(pack["keywords"])
    locale = str(pack["ogLocale"])
    url = str(pack["url"])

    # Match the html lang attribute itself. A greedy scan also hits data-lang.
    html = _swap(html, r'(<html\s+lang=")[^"]*(")', html_lang)
    html = _swap(html, r'(<html\b[^>]*\sdata-lang=")[^"]*(")', html_lang)
    html = _swap(html, r"(<title>)[^<]*(</title>)", title)
    html = _swap(html, r'(<meta\s+name="description"\s+content=")[^"]*(")', description)
    html = _swap(html, r'(<meta\s+name="keywords"\s+content=")[^"]*(")', keywords)
    for prop, value in (
        ("og:title", title),
        ("og:description", description),
        ("og:locale", locale),
        ("og:url", url),
    ):
        html = _swap(
            html,
            rf'(<meta\s+property="{re.escape(prop)}"\s+content=")[^"]*(")',
            value,
        )
    for name, value in (
        ("twitter:title", title),
        ("twitter:description", description),
    ):
        html = _swap(
            html,
            rf'(<meta\s+name="{re.escape(name)}"\s+content=")[^"]*(")',
            value,
        )
    html = _swap(html, r'(<link\s+rel="canonical"\s+href=")[^"]*(")', url)
    return html, html_lang
