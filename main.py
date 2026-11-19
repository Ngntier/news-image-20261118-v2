#!/usr/bin/env python3
"""news-image-20261118 v2 — dense newspaper front page for 18 November 2026.

Draws a 1024x1024 PNG front page ("THE WORLD IN ONE IMAGE") in pure
Python 3 standard library: hand-rolled rasterizer, a 5x7 bitmap font
written out below, and a minimal PNG encoder (zlib + struct). No network,
no timestamps, no randomness: two runs write byte-identical output.

Usage: python3 main.py   (writes entry.png to $MAKEFUN_OUTPUT_DIR or /output)
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font -----
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is on, '.' is off.
FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": (".....", ".....", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": (".....", ".....", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": (".....", ".....", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    "g": (".....", ".....", "01110", "10001", "10001", "01111", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", ".....", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", ".....", "00110", "00010", "00010", "00010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": (".....", ".....", "11010", "10101", "10101", "10101", "10101"),
    "n": (".....", ".....", "11110", "10001", "10001", "10001", "10001"),
    "o": (".....", ".....", "01110", "10001", "10001", "10001", "01110"),
    "p": (".....", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": (".....", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": (".....", ".....", "10110", "11001", "10000", "10000", "10000"),
    "s": (".....", ".....", "01111", "10000", "01110", "00001", "11110"),
    "t": ("00100", "00100", "11111", "00100", "00100", "00100", "00110"),
    "u": (".....", ".....", "10001", "10001", "10001", "10011", "01101"),
    "v": (".....", ".....", "10001", "10001", "10001", "01010", "00100"),
    "w": (".....", ".....", "10001", "10101", "10101", "10101", "01010"),
    "x": (".....", ".....", "10001", "01010", "00100", "01010", "10001"),
    "y": (".....", "10001", "10001", "10001", "01111", "00001", "01110"),
    "z": (".....", ".....", "11111", "00010", "00100", "01000", "11111"),
    ".": (".....", ".....", ".....", ".....", ".....", "01100", "01100"),
    ",": (".....", ".....", ".....", ".....", "01100", "00100", "01100"),
    ":": (".....", "01100", "01100", ".....", "01100", "01100", "....."),
    ";": (".....", "01100", "01100", ".....", "01100", "00100", "01100"),
    "!": ("00100", "00100", "00100", "00100", "00100", ".....", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", ".....", "00100"),
    "'": ("00100", "00100", "01000", ".....", ".....", ".....", "....."),
    '"': ("01010", "01010", "01010", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "01110", ".....", ".....", "....."),
    "\u2013": (".....", ".....", ".....", "01110", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "11111", ".....", ".....", "....."),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": (".....", "00100", "00100", "11111", "00100", "00100", "....."),
    "=": (".....", ".....", "11111", ".....", "11111", ".....", "....."),
    "*": (".....", "10101", "01110", "10101", ".....", ".....", "....."),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "\u2022": (".....", ".....", "01100", "01100", ".....", ".....", "....."),
    "\u00b7": (".....", ".....", ".....", "01100", ".....", ".....", "....."),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "11111"),
    "~": (".....", ".....", "01001", "10110", ".....", ".....", "....."),
    "^": ("00100", "01010", "10001", ".....", ".....", ".....", "....."),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "`": ("01000", "00100", ".....", ".....", ".....", ".....", "....."),
    "{": ("00010", "00100", "00100", "01100", "00100", "00100", "00010"),
    "}": ("01000", "00100", "00100", "00110", "00100", "00100", "01000"),
}

# ------------------------------------------------------------- canvas ------
PAPER = (246, 241, 227)
INK = (26, 26, 26)
NAVY = (22, 35, 63)
NAVY2 = (38, 54, 92)
RED = (176, 30, 36)
GOLD = (201, 162, 39)
TEAL = (15, 95, 92)
GREY = (96, 96, 90)
LGREY = (214, 208, 192)
SKY = (58, 84, 128)
ORANGE = (214, 120, 44)
SEA = (24, 52, 84)
WHITE = (250, 248, 242)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3 * i] = bg[0]
            self.px[3 * i + 1] = bg[1]
            self.px[3 * i + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = 3 * (y * self.w + x)
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = 3 * (yy * self.w + x0)
            for xx in range(x0, x1):
                i = base + 3 * (xx - x0)
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if t == 1:
                self.set(x0, y0, c)
            else:
                self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(-r, r + 1):
            dx = int((r * r - yy * yy) ** 0.5)
            self.fill_rect(cx - dx, cy + yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(-r, r + 1):
            dx = int((r * r - yy * yy) ** 0.5)
            self.fill_rect(cx - dx, cy + yy, t, 1, c)
            self.fill_rect(cx + dx - t + 1, cy + yy, t, 1, c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), 1, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT["?"])
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_c(self, x, y, w, s, scale, c):
        tw = self.text_w(s, scale)
        self.text(x + (w - tw) // 2, y, s, scale, c)

    def wrap(self, s, max_chars):
        words, lines, cur = s.split(" "), [], ""
        for wd in words:
            if cur and len(cur) + 1 + len(wd) > max_chars:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, w, s, scale, c, lh=None):
        max_chars = max(1, w // (6 * scale))
        lh = lh or (8 * scale + 2)
        yy = y
        for ln in self.wrap(s, max_chars):
            self.text(x, yy, ln, scale, c)
            yy += lh
        return yy


# ---------------------------------------------------------------- png -------
def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------- illustrations ---
def draw_gulf(cv, x, y, w, h):
    """Stylised Gulf night: sky, low sun, sea, air base, missile arcs."""
    cv.fill_rect(x, y, w, h, NAVY)
    cv.fill_rect(x, y + int(h * 0.42), w, h - int(h * 0.42), (64, 52, 44))
    # low sun
    cv.circle(x + int(w * 0.78), y + int(h * 0.34), 22, ORANGE)
    cv.circle(x + int(w * 0.78), y + int(h * 0.34), 15, (232, 164, 80))
    # stars
    for sx, sy in ((0.08, 0.10), (0.22, 0.06), (0.38, 0.14), (0.55, 0.08),
                   (0.66, 0.18), (0.90, 0.10), (0.30, 0.24), (0.48, 0.28)):
        cv.fill_rect(x + int(w * sx), y + int(h * sy), 3, 3, WHITE)
    # sea
    sea_y = y + int(h * 0.62)
    cv.fill_rect(x, sea_y, w, h - int(h * 0.62), SEA)
    for wy in range(sea_y + 8, y + h - 4, 12):
        cv.hline(x + 8, wy, w - 16, (52, 96, 140), 2)
    # air base silhouette on the shore
    base_y = sea_y
    cv.fill_rect(x + 14, base_y - 26, 150, 26, (14, 20, 36))
    cv.fill_rect(x + 30, base_y - 44, 8, 44, (14, 20, 36))          # tower
    cv.fill_rect(x + 24, base_y - 52, 20, 8, (14, 20, 36))
    cv.fill_rect(x + 180, base_y - 18, 60, 18, (14, 20, 36))        # hangar
    cv.fill_rect(x + 252, base_y - 14, 44, 14, (14, 20, 36))        # hangar
    # radar dish
    cv.line(x + 300, base_y, x + 300, base_y - 30, (14, 20, 36), 3)
    cv.line(x + 288, base_y - 34, x + 312, base_y - 26, (200, 200, 190), 3)
    # lit windows
    for wx in range(x + 22, x + 150, 14):
        cv.fill_rect(wx, base_y - 18, 5, 5, GOLD)
    # missile arcs (parabolas) with smoke trails
    for (ax, ay, bx, by, peak) in (
            (0.10, 0.95, 0.55, 0.30, 0.55),
            (0.30, 0.95, 0.80, 0.22, 0.42),
            (0.55, 0.95, 0.95, 0.40, 0.60)):
        px0, py0 = x + int(w * ax), y + int(h * ay)
        px1, py1 = x + int(w * bx), y + int(h * by)
        top = y + int(h * peak)
        prev = None
        for t in range(0, 21):
            f = t / 20.0
            mx = int(px0 + (px1 - px0) * f)
            # quadratic bezier toward the peak
            my = int((1 - f) * (1 - f) * py0 + 2 * (1 - f) * f * top
                     + f * f * py1)
            if prev:
                cv.line(prev[0], prev[1], mx, my, (232, 200, 140), 2)
            prev = (mx, my)
        cv.circle(px1, py1, 4, WHITE)
        cv.circle(px1, py1, 8, (232, 164, 80))
    # explosion starbursts where arcs end low
    for ex, ey in ((0.18, 0.55), (0.62, 0.48)):
        cxp, cyp = x + int(w * ex), y + int(h * ey)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (-1, -1), (1, -1), (-1, 1)):
            cv.line(cxp, cyp, cxp + dx * 12, cyp + dy * 12, GOLD, 2)
        cv.circle(cxp, cyp, 4, WHITE)


def draw_shenzhen(cv, x, y, w, h):
    """Shenzhen skyline at dusk, red sun, lit towers."""
    cv.fill_rect(x, y, w, h, (30, 32, 58))
    cv.circle(x + int(w * 0.72), y + int(h * 0.22), 16, RED)
    cv.circle(x + int(w * 0.72), y + int(h * 0.22), 10, (220, 90, 80))
    base = y + h
    towers = ((0.02, 0.55, 0.12), (0.16, 0.42, 0.12), (0.30, 0.62, 0.10),
              (0.42, 0.34, 0.12), (0.56, 0.50, 0.12), (0.70, 0.40, 0.12),
              (0.84, 0.58, 0.12))
    for fx, fh, fw in towers:
        tx, tw, th = x + int(w * fx), int(w * fw), int(h * fh)
        cv.fill_rect(tx, base - th, tw, th, (12, 14, 26))
        for wy in range(base - th + 6, base - 4, 12):
            for wx in range(tx + 3, tx + tw - 3, 9):
                if (wx + wy) % 3 == 0:
                    cv.fill_rect(wx, wy, 3, 4, GOLD)
    # tallest tower with spire
    cv.line(x + int(w * 0.48), base - int(h * 0.34),
            x + int(w * 0.48), base - int(h * 0.52), GOLD, 2)
    cv.fill_rect(x, base - 4, w, 4, GOLD)


def draw_kerch(cv, x, y, w, h):
    """Kerch Bridge: deck with a collapsed span, smoke, strait below."""
    cv.fill_rect(x, y, w, h, (176, 188, 204))
    cv.fill_rect(x, y, w, int(h * 0.18), (120, 140, 168))
    sea_y = y + int(h * 0.66)
    cv.fill_rect(x, sea_y, w, h - int(h * 0.66), (40, 78, 118))
    for wy in range(sea_y + 6, y + h - 4, 10):
        cv.hline(x + 6, wy, w - 12, (96, 140, 180), 2)
    # bridge deck, left and right of the gap
    deck_y = y + int(h * 0.42)
    cv.fill_rect(x, deck_y, int(w * 0.38), 8, (52, 52, 56))
    cv.fill_rect(x + int(w * 0.62), deck_y, int(w * 0.38), 8, (52, 52, 56))
    # piers
    cv.fill_rect(x + int(w * 0.10), deck_y + 8, 8, sea_y - deck_y - 8,
                 (52, 52, 56))
    cv.fill_rect(x + int(w * 0.88), deck_y + 8, 8, sea_y - deck_y - 8,
                 (52, 52, 56))
    # fallen arch segment, tilted into the strait
    cv.poly([(x + int(w * 0.40), deck_y + 2),
             (x + int(w * 0.58), deck_y + 16),
             (x + int(w * 0.56), deck_y + 24),
             (x + int(w * 0.38), deck_y + 10)], (52, 52, 56))
    # smoke puffs over the gap
    for sx, sy, sr in ((0.47, 0.26, 9), (0.54, 0.20, 11)):
        cv.circle(x + int(w * sx), y + int(h * sy), sr, (110, 110, 108))
        cv.circle(x + int(w * sx), y + int(h * sy), sr - 4, (140, 140, 138))
    # splash
    for sx in (0.46, 0.52, 0.58):
        cv.line(x + int(w * sx), sea_y + 2, x + int(w * sx) + 4,
                sea_y - 8, WHITE, 2)


def draw_capitol(cv, x, y, w, h):
    """US Capitol dome, flat silhouette on pale sky."""
    cv.fill_rect(x, y, w, h, (214, 208, 192))
    base = y + h
    # steps and base
    cv.fill_rect(x + 8, base - 18, w - 16, 18, (120, 116, 104))
    cv.fill_rect(x + 16, base - 30, w - 32, 12, (150, 146, 134))
    # drum and dome
    cxp = x + w // 2
    cv.fill_rect(cxp - 26, base - 62, 52, 32, WHITE)
    for i, r in enumerate((26, 24, 21, 17, 12, 6)):
        cv.fill_rect(cxp - r, base - 62 - (i + 1) * 6, 2 * r, 6, WHITE)
    # lantern and flag
    cv.fill_rect(cxp - 4, base - 62 - 40, 8, 6, WHITE)
    cv.line(cxp, base - 62 - 40, cxp, base - 62 - 54, INK, 2)
    cv.poly([(cxp, base - 62 - 54), (cxp + 16, base - 62 - 50),
             (cxp, base - 62 - 46)], RED)
    # columns
    for i in range(5):
        colx = cxp - 44 + i * 20
        cv.fill_rect(colx, base - 62, 6, 32, (200, 196, 184))
    # wings
    cv.fill_rect(x + 4, base - 44, 22, 26, (200, 196, 184))
    cv.fill_rect(x + w - 26, base - 44, 22, 26, (200, 196, 184))


# ----------------------------------------------------------------- page ------
GRID = [
    ("RUSSIA", "SIBERIA PLANE CRASH KILLS 19"),
    ("ISRAEL", "KAHANA ELECTED KNESSET SPEAKER"),
    ("GAZA", "BOARD FAULTS ISRAEL, HAMAS"),
    ("HEALTH", "EBOLA TOPS 11,000 IN CONGO"),
    ("YEMEN", "HOUTHIS CLAIM PIPELINE ATTACK"),
    ("US NAVY", "THIRD US CARRIER TO GULF"),
    ("WEST BANK", "UK, AUSTRALIA HIT SETTLERS"),
    ("CLIMATE", "COP31 SPLIT ON FOSSIL FUELS"),
    ("EUROPE", "FRANCE REJECTS RUSSIAN CLAIM"),
    ("FRANCE", "LE PEN: RETIRE AT 60-62"),
    ("TECH", "OPENAI LAUNCHES GPT-6.2 ASTRA"),
    ("CANADA", "CARNEY MEETS TRUMP AT APEC"),
    ("INDIA", "CYCLONE AKVAN: 47,000 FLEE"),
    ("GULF", "HORMUZ TANKER FIRE: 1 MISSING"),
    ("VATICAN", "POPE LEO HIT BY THROWN ROSARY"),
    ("COURTS", "C-130 DISABLED WITH GALLIUM"),
    ("USA", "JEFFRIES WINS SPEAKER NOD"),
    ("USA", "MUSK: 'FOOLISH' ON $458M"),
    ("SPORT", "INDIA WINS 10TH SAFF TITLE"),
    ("SPORT", "ALCARAZ BEATS TIAFOE 6-2, 6-2"),
]

TIMELINE = [
    ("00:16", "IRAN STRIKES", "KUWAIT"),
    ("~02:00", "KERCH SPAN", "COLLAPSES"),
    ("~06:00", "COP31 SPLITS", "FOSSIL FUELS"),
    ("~12:00", "XI & PUTIN", "IN SHENZHEN"),
    ("~15:00", "US LOSES", "MEASLES-FREE"),
    ("~18:00", "PELTOLA WINS", "SENATE FLIPS"),
]


def build():
    cv = Canvas(W, H, PAPER)
    cv.fill_rect(0, 0, W, H, NAVY)
    cv.fill_rect(8, 8, W - 16, H - 16, PAPER)

    # ---- masthead ------------------------------------------------------
    cv.fill_rect(8, 8, W - 16, 96, NAVY)
    cv.text(24, 26, "VOL. I", 2, GOLD)
    cv.text(1024 - 24 - cv.text_w("LATE EDITION", 2), 26, "LATE EDITION", 2, GOLD)
    cv.text_c(8, 18, W - 16, "THE WORLD IN ONE IMAGE", 5, WHITE)
    cv.fill_rect(182, 62, 660, 2, GOLD)
    cv.text_c(8, 70, W - 16, "WEDNESDAY, 18 NOVEMBER 2026", 3, GOLD)

    # ---- kicker --------------------------------------------------------
    cv.text_c(8, 112, W - 16,
              "FRONT PAGE - EVERY STORY BELOW WAS FIRST REPORTED TODAY", 2, RED)

    # ---- lead story ----------------------------------------------------
    draw_gulf(cv, 12, 132, 344, 168)
    cv.text(12, 304, "DRONES OVER THE GULF", 2, GREY)
    tx = 372
    cv.text(tx, 132, "MIDDLE EAST - WAR IN THE GULF", 2, RED)
    cv.text(tx, 154, "IRAN STRIKES", 6, INK)
    cv.text(tx, 202, "KUWAIT & BAHRAIN", 6, INK)
    cv.para(tx, 252, 640,
            "Iranian drones hit the US-hosted Ali Al Salem air base in "
            "Kuwait, and Bahrain reports fresh attacks - hours after US "
            "jets struck a missile site on Qeshm Island. Both say the "
            "attacks were intercepted.",
            2, INK)
    cv.hline(8, 328, W - 16, NAVY, 3)

    # ---- row 2: Shenzhen / Kerch ---------------------------------------
    y2 = 336
    draw_shenzhen(cv, 12, y2, 120, 148)
    cv.text(144, y2, "CHINA - APEC", 2, RED)
    cv.text(144, y2 + 24, "XI & PUTIN MEET", 3, INK)
    cv.text(144, y2 + 48, "IN SHENZHEN", 3, INK)
    cv.para(144, y2 + 76, 362,
            "Xi and Putin meet in Shenzhen ahead of Thursday's trilateral "
            "with Trump, who flew in via Manila.",
            2, INK, lh=16)
    cv.vline(508, y2, 148, LGREY, 2)

    draw_kerch(cv, 520, y2, 120, 148)
    cv.text(652, y2, "UKRAINE - CRIMEA", 2, RED)
    cv.text(652, y2 + 24, "KERCH BRIDGE", 3, INK)
    cv.text(652, y2 + 48, "HIT AGAIN", 3, INK)
    cv.para(652, y2 + 76, 360,
            "A Ukrainian drone-and-missile attack collapses a road-span "
            "arch. Traffic halted; rail runs. Two dead.",
            2, INK, lh=16)
    cv.hline(8, 490, W - 16, NAVY, 3)

    # ---- row 3: Senate / Nvidia / measles -------------------------------
    y3 = 498
    draw_capitol(cv, 12, y3, 120, 130)
    cv.text(144, y3, "UNITED STATES - ELECTION", 2, RED)
    cv.text(144, y3 + 24, "DEMOCRATS TAKE", 3, INK)
    cv.text(144, y3 + 48, "THE SENATE", 3, INK)
    cv.para(144, y3 + 76, 362,
            "Peltola beats Sen. Sullivan in Alaska; Democrats take a "
            "projected 56-44 majority.",
            2, INK, lh=16)
    cv.vline(508, y3, 130, LGREY, 2)

    cv.text(520, y3, "TECH", 2, RED)
    cv.text(520, y3 + 20, "NVIDIA: RECORD $115.84BN", 2, INK)
    cv.text(520, y3 + 38, "Revenue doubles; Huang's return barred.", 2, INK)
    cv.hline(520, y3 + 60, 492, LGREY, 2)
    cv.text(520, y3 + 68, "HEALTH", 2, RED)
    cv.text(520, y3 + 88, "US LOSES MEASLES-FREE STATUS", 2, INK)
    cv.text(520, y3 + 106, "First loss in 26 years; 5,400+ cases.", 2, INK)
    cv.hline(8, 634, W - 16, NAVY, 3)

    # ---- timeline ------------------------------------------------------
    yt = 640
    cv.text(12, yt, "THE DAY IN UTC", 2, RED)
    cv.text(1024 - 12 - cv.text_w("TIMES APPROXIMATE", 2), yt,
            "TIMES APPROXIMATE", 2, GREY)
    cv.hline(12, yt + 30, W - 24, NAVY, 2)
    slot = (W - 24) // len(TIMELINE)
    for i, (tm, l1, l2) in enumerate(TIMELINE):
        cxp = 12 + slot * i + slot // 2
        cv.circle(cxp, yt + 31, 5, RED)
        cv.text_c(12 + slot * i, yt + 42, slot, tm, 2, INK)
        cv.text_c(12 + slot * i, yt + 58, slot, l1, 2, INK)
        cv.text_c(12 + slot * i, yt + 74, slot, l2, 2, INK)
    cv.hline(8, 734, W - 16, NAVY, 3)

    # ---- story grid ----------------------------------------------------
    yg = 742
    cv.text(12, yg, "MORE OF THE DAY - IN BRIEF", 2, RED)
    cv.text(1024 - 12 - cv.text_w("20 STORIES", 2), yg, "20 STORIES", 2, GREY)
    cols, rows = 5, 4
    gw = (W - 24 - (cols - 1) * 12) // cols
    gh = 44
    gy0 = yg + 22
    for idx, (tag, head) in enumerate(GRID):
        r, c = divmod(idx, cols)
        gx = 12 + c * (gw + 12)
        gy = gy0 + r * gh
        cv.text(gx, gy, tag, 1, RED)
        lines = cv.wrap(head, max(1, gw // 12))
        yy = gy + 10
        for ln in lines[:2]:
            cv.text(gx, yy, ln, 2, INK)
            yy += 15
    cv.hline(8, 946, W - 16, NAVY, 3)

    # ---- footer: date check + also reported ----------------------------
    yf = 954
    cv.rect(12, yf, 348, 54, RED, 3)
    cv.text(24, yf + 4, "DATE CHECK", 2, RED)
    cv.text(24, yf + 20, "TODAY IS WEDNESDAY", 2, INK)
    cv.text(24, yf + 35, "18 NOVEMBER 2026.", 2, INK)
    cv.text(372, yf, "ALSO REPORTED TODAY:", 2, RED)
    cv.para(372, yf + 18, 640,
            "Quad leaders meet in Manila - Philippines trade deal - "
            "Gaza ceasefire wobbles.",
            2, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
