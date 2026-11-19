#!/usr/bin/env python3
"""Build-time font table for the front-page renderer.

Renders each needed glyph from the local DejaVu fonts with Pillow and
writes font_data.py: for every (weight, character) a bit-packed bitmap plus
its metrics. This script never runs inside the graded program; only the
generated font_data.py ships, and main.py is pure stdlib.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 64
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CHARS = "".join(chr(c) for c in range(32, 127))
CHARS += "\u2014\u2013\u2022\u2019\u2018\u201c\u201d\u20ac\u00d7\u00b0\u2026\u00e9\u00fc"


def render_glyph(font, ch):
    # Wide canvas so no glyph is clipped; find the ink bounding box.
    img = Image.new("L", (SIZE * 2, SIZE * 2), 0)
    d = ImageDraw.Draw(img)
    d.text((SIZE // 2, SIZE // 2), ch, font=font, fill=255)
    bbox = img.getbbox()
    if bbox is None:  # blank glyph (space)
        return 0, 0, int(font.getlength(ch)), 0, b""
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    # Ink-top offset from the ascender line (text drawn at y=SIZE//2, so
    # the ascender line sits at SIZE//2). The renderer adds this so every
    # glyph shares one baseline.
    yoff = y0 - SIZE // 2
    # Pack bits: 1 bit per pixel, MSB first, rows top to bottom.
    bits = bytearray()
    cur = 0
    nbits = 0
    px = img.load()
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            cur = (cur << 1) | (1 if px[xx, yy] > 110 else 0)
            nbits += 1
            if nbits == 8:
                bits.append(cur)
                cur = 0
                nbits = 0
    if nbits:
        bits.append(cur << (8 - nbits))
    adv = int(round(font.getlength(ch)))
    return w, h, adv, yoff, bytes(bits)


def main():
    out_path = Path(__file__).resolve().parent.parent / "font_data.py"
    fonts = {"regular": ImageFont.truetype(REGULAR, SIZE),
             "bold": ImageFont.truetype(BOLD, SIZE)}
    lines = []
    lines.append("# Glyph bitmaps generated at build time by")
    lines.append("# tools/generate_font_data.py from local DejaVu fonts.")
    lines.append("# Format: GLYPHS[(weight, char)] = "
                 "(width, height, advance, y-offset, hex-bytes)")
    lines.append("# Bitmaps are 1 bit per pixel, MSB first, row-major from the ink box.")
    lines.append("FONT_SIZE = %d" % SIZE)
    lines.append("GLYPHS = {")
    total = 0
    for weight, font in fonts.items():
        for ch in CHARS:
            w, h, adv, yoff, data = render_glyph(font, ch)
            total += 1
            lines.append("    (%r, %r): (%d, %d, %d, %d, %r)," % (
                weight, ch, w, h, adv, yoff, data.hex()))
    lines.append("}")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", out_path, "glyphs:", total,
          "bytes:", out_path.stat().st_size)


if __name__ == "__main__":
    main()
