# -*- coding: utf-8 -*-
import re
from pathlib import Path

p = Path(__file__).resolve().parent / "index.html"
text = p.read_text(encoding="utf-8")
start = text.find(
    '        <div class="doctors-grid">\n'
    '          <article class="doctor reveal fade-item" id="doctor-burnashev">'
)
end = text.find('        <div class="team-banner reveal fade-item">', start)
if start < 0 or end < 0:
    raise SystemExit(f"markers {start} {end}")
block = text[start:end]
articles = re.findall(
    r"[ \t]*<article class=\"doctor reveal fade-item\"[\s\S]*?</article>",
    block,
)
if len(articles) != 39:
    raise SystemExit(f"expected 39 articles, got {len(articles)}")

VISIBLE = 6


def normalize(article: str, hidden: bool) -> str:
    lines = article.split("\n")
    indents = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip()]
    base = min(indents) if indents else 0
    body = "\n".join(
        (line[base:] if line.startswith(" " * base) else line) for line in lines
    )
    klass = "doctor reveal fade-item is-hidden" if hidden else "doctor reveal fade-item"
    body = body.replace(
        '<article class="doctor reveal fade-item"',
        f'<article class="{klass}"',
        1,
    )
    return "\n".join(("          " + line if line else line) for line in body.split("\n"))


parts = [normalize(article, index >= VISIBLE) for index, article in enumerate(articles)]
grid = (
    '        <div class="doctors-grid" id="doctorsGrid">\n'
    + "\n\n".join(parts)
    + "\n        </div>\n"
    '        <div class="doctors-more">\n'
    '          <button type="button" class="btn btn-ghost" id="doctorsMore" '
    'data-i18n="doctors.more" aria-expanded="false" aria-controls="doctorsGrid">'
    "Посмотреть всех специалистов</button>\n"
    "        </div>\n\n"
)
text = text[:start] + grid + text[end:]
if '<details class="doctors-more">' in text:
    raise SystemExit("details still present")
p.write_text(text, encoding="utf-8")
print(f"rewritten {len(articles)} cards, hidden from {VISIBLE + 1}")
