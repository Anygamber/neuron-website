"""Build square white OG image from NeurON-light.png for Telegram previews."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "NeurON-light.png"
OUT = ROOT / "NeurON-square-light.png"
SIZE = 1024
PAD_RATIO = 0.82  # logo max side relative to canvas


def main() -> None:
    im = Image.open(SRC).convert("RGBA")
    max_side = int(SIZE * PAD_RATIO)
    w, h = im.size
    scale = min(max_side / w, max_side / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    logo = im.resize((nw, nh), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 255))
    ox = (SIZE - nw) // 2
    oy = (SIZE - nh) // 2
    canvas.alpha_composite(logo, (ox, oy))
    canvas.convert("RGB").save(OUT, "PNG", optimize=True)
    print(f"Saved {OUT} ({SIZE}x{SIZE}), logo {nw}x{nh}")


if __name__ == "__main__":
    main()
