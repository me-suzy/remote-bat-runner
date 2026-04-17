"""Generate PWA icons (192 and 512 px) with a simple play glyph."""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / "static"
OUT.mkdir(exist_ok=True)


def make(size: int) -> None:
    img = Image.new("RGB", (size, size), (15, 23, 42))
    d = ImageDraw.Draw(img)
    pad = size // 8
    d.ellipse((pad, pad, size - pad, size - pad), fill=(34, 197, 94))
    cx, cy = size // 2, size // 2
    r = size // 4
    d.polygon(
        [(cx - r // 2, cy - r), (cx - r // 2, cy + r), (cx + r, cy)],
        fill=(255, 255, 255),
    )
    img.save(OUT / f"icon-{size}.png")


for s in (192, 512):
    make(s)
print("Icons written to", OUT)
