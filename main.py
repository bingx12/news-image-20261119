#!/usr/bin/env python3
"""THE WORLD TODAY - Thursday 19 November 2026, in one image.

Pure-stdlib Python 3.13 program. Draws a newspaper front page summing up
the day's world news and writes it to /output/entry.png (1024x1024 PNG,
under 1 MiB, byte-identical on every run: no network, no clock, no random).

Stories (all reported on Thursday 19 November 2026 - Reuters, AP, Yonhap,
NASA, The Hindu, Financial Times):
  LEAD  Gulf war spreads: Iran's drones hit the U.S. base at Ali Al Salem,
        Kuwait, after U.S. jets struck an IRGC missile site on Qeshm Island;
        tankers hit mines in the Strait of Hormuz.
  SUMMIT First-ever Trump-Xi-Putin trilateral, APEC sidelines, Shenzhen.
  CULTURE Grand Theft Auto VI launches worldwide after 13 years.
  AMERICA House Democrats nominate Hakeem Jeffries for Speaker, 251-11.
  SPACE Voyager 1 reaches one light-day from Earth; NASA confirms today.
  ALSO  Cyclone Akvan nears India's east coast; EU proposes a 45bn euro
        Ukraine loan; Australia sanctions Israeli settlers.

Run it:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import binascii
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from font_data import FONT_SIZE, GLYPHS

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (245, 239, 225)
PANEL = (255, 253, 246)
INK = (23, 19, 14)
MUTED = (90, 83, 72)
RED = (158, 27, 30)
RED_DK = (122, 18, 22)
NAVY = (30, 58, 92)
NAVY_LT = (64, 102, 148)
GOLD = (166, 124, 0)
WATER = (188, 215, 230)
WATER_DK = (143, 184, 207)
LAND = (230, 217, 184)
LAND_DK = (203, 186, 138)
PINK = (232, 90, 130)
ORANGE = (244, 140, 40)
SUN = (250, 204, 72)
WHITE = (255, 255, 255)


# ------------------------------------------------------------------- PNG
def png_bytes(rgb, w, h):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * w * 3:(y + 1) * w * 3]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = max(1, t // 2)
        for s in range(steps + 1):
            cx = x0 + dx * s // steps
            cy = y0 + dy * s // steps
            self.circle(cx, cy, r, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.rect(cx - dx, yy, dx * 2 + 1, 1, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)


# ------------------------------------------------------------ text
def text_w(s, size, weight="regular"):
    sc = size / FONT_SIZE
    return sum(GLYPHS.get((weight, ch), GLYPHS[(weight, " ")])[2] * sc
               for ch in s)


def draw_text(cv, x, y, s, size, color, weight="regular", align="left"):
    """Draw text with the ascender top at y. Returns width drawn."""
    if align == "center":
        x = x - text_w(s, size, weight) / 2
    elif align == "right":
        x = x - text_w(s, size, weight)
    sc = size / FONT_SIZE
    cx = float(x)
    for ch in s:
        g = GLYPHS.get((weight, ch))
        if g is None:
            g = GLYPHS[(weight, " ")]
        w, h, adv, yoff, data = g
        if w == 0 or h == 0 or not data:
            cx += adv * sc
            continue
        data = bytes.fromhex(data)
        dw = max(1, int(round(w * sc)))
        dh = max(1, int(round(h * sc)))
        top = int(y + yoff * sc)
        for dy in range(dh):
            sy = min(h - 1, int(dy / sc)) if sc > 0 else 0
            for dx in range(dw):
                sx = min(w - 1, int(dx / sc)) if sc > 0 else 0
                bit = sy * w + sx  # bits packed continuously, MSB first
                if data[bit // 8] & (0x80 >> (bit % 8)):
                    cv.px(int(cx) + dx, top + dy, color)
        cx += adv * sc
    return cx - x


def wrap(s, size, weight, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, size, weight) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, s, size, color, weight, maxw, leading=None):
    lead = leading if leading is not None else int(size * 1.28)
    for ln in wrap(s, size, weight, maxw):
        draw_text(cv, x, y, ln, size, color, weight)
        y += lead
    return y


# ------------------------------------------------------------ masthead
def draw_masthead(cv):
    cv.hline(26, 20, 972, INK, 3)
    cv.hline(26, 24, 972, INK, 1)
    draw_text(cv, 26, 28, "EST. 2026", 14, MUTED, "bold")
    draw_text(cv, 998, 28, "ONE DAY · ONE IMAGE", 14, MUTED, "bold",
              align="right")
    draw_text(cv, 512, 32, "THE WORLD TODAY", 68, INK, "bold",
              align="center")
    cv.hline(26, 108, 972, INK, 1)
    cv.hline(26, 112, 972, INK, 3)
    draw_text(cv, 512, 120, "THURSDAY, 19 NOVEMBER 2026",
              22, RED_DK, "bold", align="center")
    draw_text(cv, 26, 122, "THE WORLD IN FULL", 14, MUTED, "bold")
    draw_text(cv, 998, 122, "EVERY STORY REPORTED TODAY", 14, MUTED,
              "bold", align="right")


# ------------------------------------------------------------ Gulf map
def draw_gulf_map(cv, x, y, w, h):
    """Schematic of the Persian Gulf: Iran along the top, Arabia below,
    the gulf channel between them narrowing to the Strait of Hormuz."""
    cv.rect(x, y, w, h, WATER)
    # Iran: wavy band along the top.
    cv.poly([(x, y), (x + w, y), (x + w, y + 26), (x + 820, y + 40),
             (x + 640, y + 30), (x + 470, y + 44), (x + 300, y + 34),
             (x + 140, y + 44), (x, y + 30)], LAND)
    # Arabia: band along the bottom, rising to pinch the strait at right.
    cv.poly([(x, y + h), (x, y + 92), (x + 160, y + 84), (x + 330, y + 94),
             (x + 520, y + 84), (x + 690, y + 92), (x + 800, y + 74),
             (x + 880, y + 66), (x + w, y + 76), (x + w, y + h)], LAND)
    # Qeshm Island: a small island in the narrow strait, right of centre.
    cv.poly([(x + 806, y + 62), (x + 862, y + 58), (x + 856, y + 72),
             (x + 800, y + 74)], LAND_DK)
    # The strait label, in open water at the far right.
    draw_text(cv, x + w - 10, y + 96, "STRAIT OF HORMUZ", 13, NAVY, "bold",
              align="right")
    draw_text(cv, x + w - 10, y + 8, "IRAN", 13, NAVY, "bold", align="right")
    draw_text(cv, x + 10, y + h - 20, "ARABIA", 13, NAVY, "bold")
    # Tankers sailing the channel, one burning after hitting a mine.
    for tx, ty, burn in ((x + 560, y + 62, True), (x + 640, y + 66, False),
                         (x + 470, y + 58, False)):
        cv.rect(tx - 14, ty - 3, 28, 6, (40, 40, 40))
        cv.rect(tx - 14, ty - 6, 6, 3, (40, 40, 40))
        if burn:
            cv.poly([(tx - 6, ty - 6), (tx, ty - 18), (tx + 6, ty - 6)],
                    ORANGE)
            cv.circle(tx, ty - 20, 4, SUN)
    # Kuwait marker at the gulf's north-west end.
    kx, ky = x + 130, y + 58
    cv.circle(kx, ky, 7, RED)
    cv.circle(kx, ky, 3, WHITE)
    draw_text(cv, kx + 18, ky - 18, "KUWAIT", 14, INK, "bold")
    draw_text(cv, kx + 18, ky - 3, "Ali Al Salem base", 12, INK)
    # Bahrain marker on the Arabian shore.
    bx, by = x + 300, y + 74
    cv.circle(bx, by, 7, RED)
    cv.circle(bx, by, 3, WHITE)
    draw_text(cv, bx + 12, by - 18, "BAHRAIN", 14, INK, "bold")
    draw_text(cv, bx + 12, by + 10, "3rd attack in a week", 12, INK)
    # Qeshm label, in open water left of the island.
    draw_text(cv, x + 676, y + 40, "QESHM ISLAND", 14, INK, "bold")
    draw_text(cv, x + 676, y + 55, "U.S. jets hit IRGC", 12, INK)
    draw_text(cv, x + 676, y + 68, "missile site Tue.", 12, INK)
    # Drone arc: horizontal above the labels, then down to Kuwait.
    cv.line(x + 452, y + 30, x + 150, y + 30, RED, 2)
    cv.line(x + 150, y + 30, kx + 2, ky - 8, RED, 2)
    cv.circle(x + 452, y + 30, 5, RED)
    draw_text(cv, x + 462, y + 8, "IRANIAN DRONES", 12, RED_DK, "bold")


# ------------------------------------------------------------ lead story
def draw_lead(cv, y0):
    x, w = 26, 972
    y = y0
    cv.rect(x, y, w, 26, RED)
    draw_text(cv, x + 12, y + 5, "LEAD — THE GULF WAR SPREADS", 16, WHITE,
              "bold")
    draw_text(cv, x + w - 12, y + 5, "MIDDLE EAST", 16, WHITE, "bold",
              align="right")
    y += 34
    draw_text(cv, x, y, "IRAN STRIKES U.S. BASE IN KUWAIT", 40, INK, "bold")
    y += 48
    draw_text(cv, x, y, "AS THE GULF WAR WIDENS", 40, INK, "bold")
    y += 52
    y = para(cv, x, y,
             "Tehran's drones hit Patriot batteries at Ali Al Salem air base "
             "— its first strike on Kuwait since September — hours after U.S. "
             "fighter jets destroyed an Iranian missile site on Qeshm Island.",
             18, INK, "regular", w, 23)
    y += 6
    draw_gulf_map(cv, x, y, w, 120)
    y += 120 + 6
    draw_text(cv, x, y, "No U.S. personnel hurt, the U.S. military says. "
              "Three tankers caught fire after hitting mines in the strait. "
              "The war began on 28 February.", 14, MUTED, "regular")
    return y + 14 + 8


# ------------------------------------------------------------ panels
def panel_frame(cv, x, y, w, h, kicker, kcolor):
    cv.rect(x, y, w, h, PANEL)
    cv.hline(x, y, w, INK, 2)
    cv.hline(x, y + h - 2, w, INK, 2)
    cv.vline(x, y, h, INK, 2)
    cv.vline(x + w - 2, y, h, INK, 2)
    cv.rect(x, y, w, 26, kcolor)
    draw_text(cv, x + 10, y + 5, kicker, 14, WHITE, "bold")


def draw_flags(cv, x, y, w):
    fw, fh = 84, 40
    gap = (w - 3 * fw) // 2
    # USA
    fx = x
    for i in range(10):
        cv.rect(fx, y + i * 4, fw, 4, WHITE if i % 2 else RED)
    cv.rect(fx, y, 34, 22, NAVY)
    for r in range(2):
        for c in range(4):
            cv.circle(fx + 5 + c * 8, y + 5 + r * 9, 1, WHITE)
    draw_text(cv, fx + fw // 2, y + fh + 4, "U.S.A.", 12, INK, "bold",
              align="center")
    # China
    fx = x + fw + gap
    cv.rect(fx, y, fw, fh, RED)
    cv.poly([(fx + 14, y + 6), (fx + 17, y + 13), (fx + 25, y + 13),
             (fx + 19, y + 18), (fx + 21, y + 25), (fx + 14, y + 20),
             (fx + 7, y + 25), (fx + 9, y + 18), (fx + 3, y + 13),
             (fx + 11, y + 13)], SUN)
    draw_text(cv, fx + fw // 2, y + fh + 4, "CHINA", 12, INK, "bold",
              align="center")
    # Russia
    fx = x + 2 * (fw + gap)
    cv.rect(fx, y, fw, 13, WHITE)
    cv.rect(fx, y + 13, fw, 14, NAVY_LT)
    cv.rect(fx, y + 27, fw, 13, RED)
    draw_text(cv, fx + fw // 2, y + fh + 4, "RUSSIA", 12, INK, "bold",
              align="center")


def draw_summit(cv, x, y, w, h):
    panel_frame(cv, x, y, w, h, "SUMMIT · SHENZHEN, CHINA", NAVY)
    ty = y + 34
    draw_text(cv, x + 12, ty, "TRUMP, XI AND PUTIN", 26, INK, "bold")
    draw_text(cv, x + 12, ty + 31, "MEET TODAY", 26, INK, "bold")
    ty += 66
    para(cv, x + 12, ty,
         "The first-ever three-way summit, on the APEC sidelines. Nuclear "
         "arms, Ukraine and Iran on the table.",
         15, INK, "regular", w - 24, 19)
    draw_flags(cv, x + 12, y + h - 58, w - 24)


def draw_gta(cv, x, y, w, h):
    panel_frame(cv, x, y, w, h, "CULTURE · VICE CITY", (90, 24, 90))
    ty = y + 34
    draw_text(cv, x + 12, ty, "AFTER 13 YEARS,", 26, INK, "bold")
    draw_text(cv, x + 12, ty + 31, "GTA VI IS OUT", 26, INK, "bold")
    # Neon dusk sky strip with skyline.
    sx, sy, sw, sh = x + 12, y + 98, w - 24, 50
    for i in range(sh):
        t = i / sh
        r = int(46 + (232 - 46) * t)
        g = int(24 + (90 - 24) * t)
        b = int(64 + (130 - 64) * t)
        cv.hline(sx, sy + i, sw, (r, g, b))
    cv.circle(sx + sw - 60, sy + 20, 13, SUN)
    heights = [20, 30, 26, 36, 22, 32, 28, 38, 24, 34, 26, 36]
    bw = sw // len(heights)
    for i, hh in enumerate(heights):
        cv.rect(sx + i * bw + 2, sy + sh - hh, bw - 4, hh, (20, 10, 30))
    for px in (sx + 30, sx + sw - 36):
        cv.line(px, sy + sh, px, sy + sh - 22, (20, 10, 30), 3)
        for dx, dy in ((-12, -4), (-6, -10), (0, -12), (6, -10), (12, -4)):
            cv.line(px, sy + sh - 22, px + dx, sy + sh - 22 + dy,
                    (20, 10, 30), 2)
    draw_text(cv, sx + 10, sy + 6, "VI", 40, WHITE, "bold")
    para(cv, x + 12, y + 154,
         "Rockstar's epic launches today on PS5 and Xbox — $79.99, 212 GB. "
         "Early reviews: 99 on Metacritic.",
         15, INK, "regular", w - 24, 19)


def draw_jeffries(cv, x, y, w, h):
    panel_frame(cv, x, y, w, h, "AMERICA · WASHINGTON", RED_DK)
    ty = y + 34
    draw_text(cv, x + 12, ty, "JEFFRIES NOMINATED", 26, INK, "bold")
    draw_text(cv, x + 12, ty + 31, "FOR SPEAKER", 26, INK, "bold")
    ty += 66
    para(cv, x + 12, ty,
         "House Democrats pick Hakeem Jeffries — on course to be the first "
         "Black Speaker in January.",
         15, INK, "regular", w - 24, 19)
    # Capitol dome + vote tally + bar, anchored to the panel bottom.
    vx = x + 12
    base = y + h - 26  # dome base line
    cv.rect(vx, base, 100, 4, NAVY)
    for cx in range(vx + 6, vx + 96, 14):
        cv.rect(cx, base - 10, 5, 10, NAVY)
    cv.rect(vx + 28, base - 16, 44, 5, NAVY)
    cv.circle(vx + 50, base - 16, 16, NAVY)
    cv.rect(vx + 48, base - 34, 4, 6, NAVY)
    cv.circle(vx + 50, base - 36, 3, GOLD)
    draw_text(cv, vx + 118, base - 24, "251 — 11", 26, NAVY, "bold")
    draw_text(cv, vx + 118, base + 2, "of 262 votes · needs 218",
              12, MUTED)
    bx, by = x + 12, y + h - 8
    cv.rect(bx, by, int((w - 24) * 251 / 262), 6, NAVY)
    cv.rect(bx + int((w - 24) * 251 / 262), by,
            w - 24 - int((w - 24) * 251 / 262), 6, RED)


def draw_voyager(cv, x, y, w, h):
    panel_frame(cv, x, y, w, h, "SPACE · INTERSTELLAR", (10, 16, 40))
    # Starfield strip with the milestone line.
    sx, sy, sw, sh = x, y + 34, w - 24, 48
    cv.rect(sx, sy, sw, sh, (10, 16, 40))
    stars = [(24, 10), (66, 26), (120, 8), (170, 22), (210, 36), (260, 10),
             (300, 28), (350, 8), (400, 24), (100, 36), (180, 40),
             (320, 40), (48, 40), (430, 36)]
    for dx, dy in stars:
        cv.circle(sx + dx, sy + dy, 2, WHITE)
    # Voyager: gold dish + body on a diagonal path.
    vx, vy = sx + 330, sy + 24
    cv.line(vx - 44, vy + 16, vx + 24, vy - 10, (200, 200, 200), 3)
    cv.poly([(vx - 4, vy - 18), (vx + 20, vy - 4), (vx + 4, vy + 6),
             (vx - 16, vy - 8)], (232, 200, 90))
    cv.rect(vx - 24, vy - 4, 36, 10, (180, 180, 180))
    draw_text(cv, sx + 12, sy + 6, "16.1 BILLION MILES", 16, SUN, "bold")
    draw_text(cv, sx + 12, sy + 25, "1 LIGHT-DAY OUT", 16, WHITE, "bold")
    ty = y + 90
    draw_text(cv, x + 12, ty, "VOYAGER 1, ONE", 26, INK, "bold")
    draw_text(cv, x + 12, ty + 31, "LIGHT-DAY OUT", 26, INK, "bold")
    ty += 66
    para(cv, x + 12, ty,
         "Forty-nine years after launch, the probe is so far away a signal "
         "takes a full day to reach it. NASA confirms it today.",
         15, INK, "regular", w - 24, 19)


# ------------------------------------------------------------ also today
def draw_also(cv, y):
    x, w = 26, 972
    cv.hline(x, y, w, INK, 2)
    draw_text(cv, x, y + 8, "ALSO TODAY", 16, RED_DK, "bold")
    colw = (w - 40) // 3
    items = [
        ("CYCLONE AKVAN", "Landfall Friday near noon, Machilipatnam to "
         "Puri, winds 120–130 km/h."),
        ("UKRAINE AID", "The EU proposes a €45 billion loan for Kyiv, to "
         "be repaid from Russian reparations."),
        ("WEST BANK", "Australia sanctions Israeli settlers and groups "
         "over West Bank expansion."),
    ]
    ty = y + 32
    for i, (head, body) in enumerate(items):
        cx = x + i * (colw + 20)
        draw_text(cv, cx, ty, head, 14, INK, "bold")
        para(cv, cx, ty + 18, body, 13, INK, "regular", colw, 17)
    return y + 32 + 18 + 2 * 17 + 8  # bodies are two lines each


# ------------------------------------------------------------------ main
def build():
    cv = Canvas(W, H, PAPER)
    cv.hline(0, 0, W, INK, 4)
    cv.hline(0, H - 4, W, INK, 4)
    cv.vline(0, 0, H, INK, 4)
    cv.vline(W - 4, 0, H, INK, 4)
    draw_masthead(cv)
    y = draw_lead(cv, 152)
    gap, pw = 16, (972 - 16) // 2
    row1 = y + 6
    draw_summit(cv, 26, row1, pw, 194)
    draw_gta(cv, 26 + pw + gap, row1, pw, 194)
    row2 = row1 + 194 + 8
    draw_jeffries(cv, 26, row2, pw, 194)
    draw_voyager(cv, 26 + pw + gap, row2, pw, 194)
    y = draw_also(cv, row2 + 194 + 8)
    cv.hline(26, y, 972, INK, 1)
    draw_text(cv, 512, y + 8,
              "Every story above was reported on Thursday 19 November 2026  ·  "
              "Sources: Reuters, AP, Yonhap, NASA, The Hindu",
              13, MUTED, "regular", align="center")
    return cv, y + 8 + 13


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv, bottom = build()
    data = png_bytes(bytes(cv.buf), W, H)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("WROTE", path, len(data), "bytes; bottom edge at y =", bottom)


if __name__ == "__main__":
    main()
