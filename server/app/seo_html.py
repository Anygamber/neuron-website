"""Inject per-language title, description, canonical, and JSON-LD.

Apache ``index.php`` applies the same replacements. Both read ``seo-meta.json``
and ``schema-i18n.json`` so a crawler that does not run JavaScript still sees
the ``?lang=`` variant, including FAQ and physician names.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from html import escape

from .config import PROJECT_ROOT

_META_PATH = PROJECT_ROOT / "seo-meta.json"
_SCHEMA_PATH = PROJECT_ROOT / "schema-i18n.json"
_SCHEMA_RE = re.compile(
    r'(<script\s+type="application/ld\+json"\s+id="neuron-schema-org">)(.*?)(</script>)',
    re.DOTALL | re.IGNORECASE,
)


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


def _swap(html: str, pattern: str, value: str, *, quote: bool = True) -> str:
    escaped = escape(value, quote=quote)

    def repl(match: re.Match[str]) -> str:
        return f"{match.group(1)}{escaped}{match.group(2)}"

    updated, _count = re.subn(pattern, repl, html, count=1, flags=re.IGNORECASE)
    return updated


_GEO_METAS = (
    ("geo.region", "UZ-TK"),
    ("geo.placename", "Tashkent"),
    ("geo.position", "41.3549516;69.3108567"),
    ("ICBM", "41.3549516, 69.3108567"),
)


def inject_geo(html: str) -> str:
    """Keep the Tashkent clinic pin in the head for every language."""
    missing: list[str] = []
    for name, value in _GEO_METAS:
        pattern = rf'(<meta\s+name="{re.escape(name)}"\s+content=")[^"]*(")'
        if re.search(pattern, html, flags=re.IGNORECASE):
            html = _swap(html, pattern, value)
        else:
            missing.append(
                f'<meta name="{escape(name, quote=True)}" content="{escape(value, quote=True)}" />'
            )
    if not missing:
        return html
    block = "\n  ".join(missing)
    updated, count = re.subn(
        r'(<meta\s+name="theme-color"\s+content="[^"]*"\s*/?>)',
        block + r"\n  \1",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    if count:
        return updated
    return html.replace("</head>", f"  {block}\n</head>", 1)


@lru_cache(maxsize=1)
def load_schema() -> dict:
    data = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    graphs = data.get("graphs")
    if not isinstance(graphs, dict) or not graphs:
        raise RuntimeError(f"schema-i18n.json has no graphs: {_SCHEMA_PATH}")
    return data


def _node_types(node: dict) -> list[str]:
    raw = node.get("@type")
    if isinstance(raw, list):
        return [str(item) for item in raw]
    if isinstance(raw, str):
        return [raw]
    return []


def _apply_visible_copy(html: str, graph: dict) -> str:
    """Put the same FAQ and physician strings into the visible markup."""
    nodes = graph.get("@graph")
    if not isinstance(nodes, list):
        return html
    for node in nodes:
        if not isinstance(node, dict):
            continue
        types = _node_types(node)
        if "FAQPage" in types:
            entities = node.get("mainEntity")
            if not isinstance(entities, list):
                continue
            for index, question in enumerate(entities, start=1):
                if not isinstance(question, dict):
                    continue
                name = question.get("name")
                answer = (question.get("acceptedAnswer") or {}).get("text")
                if isinstance(name, str) and name:
                    html = _swap(
                        html,
                        rf'(<[^>]*\sdata-i18n="faq\.q{index}"[^>]*>)[^<]*(</)',
                        name,
                        quote=False,
                    )
                if isinstance(answer, str) and answer:
                    html = _swap(
                        html,
                        rf'(<[^>]*\sdata-i18n="faq\.a{index}"[^>]*>)[^<]*(</)',
                        answer,
                        quote=False,
                    )
        if "Physician" not in types:
            continue
        node_id = str(node.get("@id") or "")
        slug = node_id.rsplit("#doctor-", 1)[-1] if "#doctor-" in node_id else ""
        if not slug:
            continue
        name = node.get("name")
        role = node.get("medicalSpecialty")
        if isinstance(name, str) and name:
            key = f"doc.{slug}.name"
            html = _swap(
                html,
                rf'(<[^>]*\sdata-i18n="{re.escape(key)}"[^>]*>)[^<]*(</)',
                name,
                quote=False,
            )
            html = _swap(
                html,
                rf'(alt=")[^"]*("\s+data-i18n-alt="{re.escape(key)}")',
                name,
            )
        if isinstance(role, str) and role:
            html = _swap(
                html,
                rf'(<[^>]*\sdata-i18n="doc\.{re.escape(slug)}\.role"[^>]*>)[^<]*(</)',
                role,
                quote=False,
            )
    return html


def inject_schema(html: str, lang: str) -> str:
    catalog = load_schema()
    graphs = catalog["graphs"]
    code = lang if lang in graphs else str(catalog.get("default") or "uz")
    graph = graphs.get(code)
    if not isinstance(graph, dict):
        return html
    payload = json.dumps(graph, ensure_ascii=False, indent=2)

    def repl(match: re.Match[str]) -> str:
        return f"{match.group(1)}\n{payload}\n  {match.group(3)}"

    updated, count = _SCHEMA_RE.subn(repl, html, count=1)
    if not count:
        return html
    return _apply_visible_copy(updated, graph)


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
    html = inject_geo(html)
    html = inject_schema(html, code)
    return html, html_lang
