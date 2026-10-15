# -*- coding: utf-8 -*-
"""Parse price_list extract into JSON for NeurON landing."""
import json
import re
from pathlib import Path

text = Path(r"C:\Users\user\Projects\presentation\Website neuron\_price_extract.txt").read_text(encoding="utf-8")

# Known category headers in order of appearance
CATEGORIES = [
    "Биохимические анализы",
    "Гематология и трансфузиология",
    "Иммунофлюоресцентный анализ и ревмопробы",
    "ИХЛА — гормоны, инфекции, маркеры",
    "Клинические анализы",
    "Коагулограмма",
    "Онкомаркеры",
    "Лучевая диагностика — МРТ",
    "Лучевая диагностика — МСКТ (КТ)",
    "Нейрохирургия",
]

SKIP = {
    "Официальный прейскурант цен",
    "NeurON medical centre",
    "Наименование услуги",
    "Стоимость, сум",
}

# Flatten lines, join broken names carefully
raw_lines = []
for line in text.splitlines():
    line = line.strip()
    if not line or line.startswith("====="):
        continue
    if line.startswith("г. Ташкент"):
        continue
    if "Все цены указаны" in line or line.startswith("NeurON medical centre ·"):
        continue
    if line.startswith("предварительного"):
        continue
    raw_lines.append(line)

# Merge lines that are continuations of names (no price yet) with next lines
# Pattern: name lines until a price line appears
price_re = re.compile(
    r"^(?:по |до )?[\d\s]+(?:000|600)?(?:\s*[–-]\s*(?:по |до )?[\d\s]+(?:000)?)?\s*сум$",
    re.IGNORECASE,
)
# Also match ranges like "18 000 000 – 20 000 000" then "сум" on next line
price_num_re = re.compile(
    r"^(?:по |до )?[\d\s]{2,}(?:\s*[–-]\s*(?:по |до )?[\d\s]{2,})?\s*(?:сум)?$",
    re.IGNORECASE,
)

def is_price(s: str) -> bool:
    s2 = s.strip()
    if s2.lower() == "сум":
        return True
    if "сум" in s2.lower() and re.search(r"\d", s2):
        return True
    # large number lines without сум (neurosurgery split)
    if re.fullmatch(r"(?:по |до )?[\d\s]{5,}(?:\s*[–-]\s*(?:по |до )?[\d\s]{5,})?", s2):
        return True
    return False


def normalize_price(parts: list[str]) -> str:
    joined = " ".join(parts)
    joined = re.sub(r"\s+", " ", joined).strip()
    if not joined.lower().endswith("сум"):
        joined = joined + " сум"
    joined = joined.replace(" - ", " – ").replace("–", "–")
    return joined


current_cat = None
items = []
i = 0
buf_name = []
buf_price = []

while i < len(raw_lines):
    line = raw_lines[i]
    if line in CATEGORIES:
        current_cat = line
        i += 1
        continue
    if line in SKIP or line == "Стоимость, сум":
        i += 1
        continue

    if is_price(line):
        # orphan price? attach to previous incomplete
        buf_price.append(line)
        # look ahead for bare "сум"
        while i + 1 < len(raw_lines) and raw_lines[i + 1].lower() == "сум":
            i += 1
            buf_price.append(raw_lines[i])
        if buf_name and current_cat:
            name = " ".join(buf_name)
            name = re.sub(r"\s+", " ", name).strip()
            price = normalize_price(buf_price)
            items.append({"category": current_cat, "name": name, "price": price})
        buf_name, buf_price = [], []
        i += 1
        continue

    # name line — may continue until price
    buf_name.append(line)
    i += 1
    # peek: accumulate name lines until price
    while i < len(raw_lines):
        nxt = raw_lines[i]
        if nxt in CATEGORIES or nxt in SKIP:
            break
        if is_price(nxt):
            buf_price.append(nxt)
            while i + 1 < len(raw_lines) and raw_lines[i + 1].lower() == "сум":
                i += 1
                buf_price.append(raw_lines[i])
            if current_cat and buf_name:
                name = re.sub(r"\s+", " ", " ".join(buf_name)).strip()
                price = normalize_price(buf_price)
                items.append({"category": current_cat, "name": name, "price": price})
            buf_name, buf_price = [], []
            i += 1
            break
        # continuation of name
        buf_name.append(nxt)
        i += 1

# Dedupe exact duplicates
seen = set()
unique = []
for it in items:
    key = (it["category"], it["name"], it["price"])
    if key in seen:
        continue
    seen.add(key)
    unique.append(it)

out = {
    "updated": "09.09.2026",
    "currency": "сум",
    "categories": CATEGORIES,
    "items": unique,
}

Path(r"C:\Users\user\Projects\presentation\Website neuron\price-data.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("items", len(unique))
from collections import Counter
c = Counter(x["category"] for x in unique)
for k, v in c.items():
    print(f"  {v:3d}  {k}")
# sample neurosurgery
print("--- neuro sample ---")
for x in unique:
    if x["category"] == "Нейрохирургия":
        print(x["name"][:60], "=>", x["price"])
