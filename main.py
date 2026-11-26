#!/usr/bin/env python3
"""Generate the make.fun bounty entry: one image summing up 26 Nov 2026 world news.

Bounty: https://make.fun/bounty/news-image-20261126
Output: /output/entry.png  (or $OUTPUT_DIR/entry.png)
Size: 1024 x 1024 PNG, at most 1 MiB, deterministic.
Version 1 for 26 Nov: newspaper front page, 49 stories, flat vector
illustrations drawn in code (no photos).

Standard library only: zlib / struct / binascii / os.
No network, no randomness, no timestamps, no external files.
Text is rendered with a built-in 5x7 bitmap font (uppercase only).
Stories were researched 2026-11-26 from AP, Reuters, WSJ, Just Security,
Qatar Tribune, Manila Times and other outlets dated 26 Nov 2026.
"""

import binascii
import os
import struct
import zlib
from pathlib import Path

_FONT_SRC = (
    "ehhvhhh uhhuhhu ehggghe uhhhhhu vgguggv vgguggg ehgnhhf hhhvhhh "
    "e44444e 72222ic hikokih ggggggv hrllhhh hpljhhh ehhhhhe uhhuggg "
    "ehhhlid uhhukih fgge11u v444444 hhhhhhe hhhhha4 hhhllrh hha4ahh "
    "hha4444 v1248gv ehjlphe 4c4444e eh168gv u11e11u 26aiv22 vgu11he "
    "68guhhe v124888 ehhehhe ehhf12c 0000000 00000cc 0000c48 000e000 "
    "pq248bj 2488842 8422248 122488g 4480000 0c000c0 0c0c480 4444404 "
    "eh12404 044v440 00v0v00 4fke5u4"
)
_FONT_ORDER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,-%()/':;!?+=$"
_DIGITS = "0123456789abcdefghijklmnopqrstuv"


def _decode_font():
    table = {}
    tokens = _FONT_SRC.split()
    for ch, token in zip(_FONT_ORDER, tokens):
        table[ch] = [_DIGITS.index(c) for c in token]
    return table


_G = _decode_font()

def _chunk(data, name):
    return struct.pack(">I", len(data)) + name + data + struct.pack(
        ">I", binascii.crc32(name + data) & 0xFFFFFFFF
    )

def encode_png(rgb, width, height):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(rgb[y * stride:(y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(ihdr, b"IHDR")
    png += _chunk(comp, b"IDAT")
    png += _chunk(b"", b"IEND")
    return png

class Canvas:
    def __init__(self, width, height, bg):
        self.width = width
        self.height = height
        self.pix = bytearray(bg * (width * height))

    def put_px(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pix[i:i + 3] = bytes(colour)

    def fill_box(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            row = bytes(colour) * (x1 - x0)
            self.pix[base:base + (x1 - x0) * 3] = row

    def draw_line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.put_px(x, y, colour)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def draw_thick(self, x0, y0, x1, y1, w, colour):
        for i in range(w):
            self.draw_line(x0, y0 + i, x1, y1 + i, colour)

    def fill_disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.put_px(xx, yy, colour)

    def fill_tri(self, cx, y_top, half, h, colour):
        for i in range(h):
            w = half * (h - i) // h
            if w < 1:
                w = 1
            self.fill_box(cx - w, y_top + i, 2 * w, 1, colour)

    def draw_char(self, x, y, ch, scale, colour):
        glyph = _G.get(ch, _G[" "])
        for r, bits in enumerate(glyph):
            for c in range(5):
                if bits & (1 << (4 - c)):
                    px = x + c * scale
                    py = y + r * scale
                    self.fill_box(px, py, scale, scale, colour)

    def draw_text(self, x, y, s, scale, colour):
        s = s.upper()
        cx = x
        for ch in s:
            self.draw_char(cx, y, ch, scale, colour)
            cx += 6 * scale
        return cx

    def measure(self, s, scale):
        return len(s) * 6 * scale - scale

    def draw_centered(self, y, s, scale, colour):
        w = self.measure(s, scale)
        self.draw_text((self.width - w) // 2, y, s, scale, colour)

def wrap(text, max_chars):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        nxt = w if not cur else cur + " " + w
        if len(nxt) <= max_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

WIDTH = 1024
HEIGHT = 1024
PAPER = (247, 242, 231)
NAVY = (18, 38, 66)
BLUE = (38, 84, 140)
RED = (178, 34, 34)
ORANGE = (214, 106, 32)
GOLD = (201, 162, 39)
GREEN = (46, 125, 72)
INK = (22, 22, 22)
GREY = (110, 110, 108)
WHITE = (255, 255, 255)
RULE = (200, 198, 190)
CARD = (255, 255, 255)
SKY = (16, 32, 58)

REGION_COL = {
    "ASIA": (38, 84, 140),
    "MIDDLE EAST": (178, 34, 34),
    "EUROPE": (46, 125, 72),
    "AFRICA": (201, 162, 39),
    "AMERICAS": (18, 38, 66),
    "OCEANIA": (120, 70, 140),
    "GLOBAL": (110, 110, 108),
}

# Cards 4-15 as records: number, region tag, headline copy.
MID = [
    {"n": 4, "region": "MIDDLE EAST", "copy": "HORMUZ: IRGC SAYS SHIP STRUCK; TWO TANKERS ABLAZE"},
    {"n": 5, "region": "MIDDLE EAST", "copy": "HOUTHIS VOW REVENGE AFTER HODEIDAH PORT HIT"},
    {"n": 6, "region": "EUROPE", "copy": "NATO JET CLEARED TO DOWN RUSSIAN MISSILE OVER POLAND"},
    {"n": 7, "region": "ASIA", "copy": "RUSSIAN BOMBERS NEAR S KOREA; JETS SCRAMBLED"},
    {"n": 8, "region": "AMERICAS", "copy": "HUAWEI GUILTY IN US COURT ON TRADE SECRETS, FRAUD"},
    {"n": 9, "region": "AFRICA", "copy": "S AFRICA COURT: RAMAPHOSA REPORT UNLAWFUL"},
    {"n": 10, "region": "AMERICAS", "copy": "WHO CHIEF: END US FUEL BLOCKADE ON CUBA"},
    {"n": 11, "region": "AMERICAS", "copy": "6 DEAD IN PLANE CRASH OFF SOUTHERN US COAST"},
    {"n": 12, "region": "GLOBAL", "copy": "UN: 5 WOMEN KILLED EVERY HOUR BY PARTNER OR KIN"},
    {"n": 13, "region": "AMERICAS", "copy": "TRUMP SEEKS FASTER FEDERAL EXECUTIONS"},
    {"n": 14, "region": "ASIA", "copy": "N KOREA EXPELS SWISS ENVOY OVER SANCTIONS"},
    {"n": 15, "region": "OCEANIA", "copy": "AUSTRALIA-SOLOMON PACT SIGNED TO THWART CHINA"},
]

# Bottom list 16-49 as records: number plus single-line summary.
LIST = [
    {"n": 16, "copy": "US THANKSGIVING TRAVEL: LONG LINES"},
    {"n": 17, "copy": "NEARLY 2,000 MIGRANTS REACH CANARY ISLANDS"},
    {"n": 18, "copy": "CHINA, CAMBODIA HOLD JOINT MILITARY DRILLS"},
    {"n": 19, "copy": "COLOMBIA TROOPS FREE SUPERMARKET HOSTAGES"},
    {"n": 20, "copy": "BANGLADESH GARMENT WAGE +36%"},
    {"n": 21, "copy": "KUALA LUMPUR SUES GOOGLE FOR $146M"},
    {"n": 22, "copy": "CHINA PROBES POLITBURO MEMBER CHEN JINING"},
    {"n": 23, "copy": "UN: WORLD HIV FIGHT UNDER PRESSURE"},
    {"n": 24, "copy": "VANCE DEFENDS NVIDIA CEO HUANG"},
    {"n": 25, "copy": "TRUMP PARDONS TURKEYS FREEDOM AND FEATHERS"},
    {"n": 26, "copy": "US ARMY DETONATES 5 TONS OF BOMB CHEMICALS"},
    {"n": 27, "copy": "INDIA: RS15,000 CRORE AID FOR NEPAL"},
    {"n": 28, "copy": "INDIA URGES HUMAN CONTROL OVER AI IN WAR"},
    {"n": 29, "copy": "SHEIKH HASINA SEEKS RETURN TO DHAKA DEC 16"},
    {"n": 30, "copy": "DURAN DURAN GUITARIST ANDY TAYLOR DIES AT 65"},
    {"n": 31, "copy": "GORDON RAMSAY TO LEAD TOP GEAR REVIVAL"},
    {"n": 32, "copy": "U2 ANNOUNCE NEW ALBUM, N AMERICA TOUR"},
    {"n": 33, "copy": "SB19, BINI MAKE GRAMMY HISTORY FOR P-POP"},
    {"n": 34, "copy": "HONG KONG REMEMBERS FIRE VICTIMS"},
    {"n": 35, "copy": "MEN CHARGED OVER WINDSOR BREAK-IN"},
    {"n": 36, "copy": "MEGHAN'S FATHER INDICTED"},
    {"n": 37, "copy": "CANADA HOLDS INFLATION PLAN"},
    {"n": 38, "copy": "BRAZIL: PETROBRAS UNVEILS $122BN INVESTMENT"},
    {"n": 39, "copy": "COLOMBIA MARKS 10 YEARS SINCE PEACE DEAL"},
    {"n": 40, "copy": "VENEZUELA REVEALS $237.5BN PUBLIC DEBT"},
    {"n": 41, "copy": "EL SALVADOR ALLOCATES $860M DEBT"},
    {"n": 42, "copy": "BARBADOS SETS FEB DEADLINE FOR CARIBBEAN AI RULES"},
    {"n": 43, "copy": "UN CHIEF URGES TALKS ON GLOBAL AI SAFETY"},
    {"n": 44, "copy": "UN RIGHTS CHIEF WARNS ON W NIGERIA"},
    {"n": 45, "copy": "UN WARNS OF ATROCITY RISK AGAINST PALESTINIANS"},
    {"n": 46, "copy": "EU COURT BACKS END THE CAGE AGE CAMPAIGN"},
    {"n": 47, "copy": "NATO BOOSTS AIR WATCH ON EASTERN FLANK"},
    {"n": 48, "copy": "ETHIOPIA PUSHES HEALTHCARE INDEPENDENCE"},
    {"n": 49, "copy": "EGYPT: SUEZ CANAL REVENUES RECOVERING"},
]

DOTS = [
    (1, 116, 39), (2, -120, 45), (3, -88, 33), (4, 65, 28), (5, 45, 18),
    (6, 25, 55), (7, 110, 30), (8, -70, 42), (9, 28, -26), (10, -80, 18),
    (11, -105, 35), (12, 0, 40), (13, -95, 28), (14, 140, 45), (15, 160, -9),
]

FOOTER1 = "DATE CHECK: ALL STORIES FIRST REPORTED THURSDAY 26 NOVEMBER 2026"
FOOTER2 = "SOURCES: AP, REUTERS, WSJ, JUST SECURITY, QATAR TRIBUNE, MANILA TIMES - 26 NOV 2026"

def _icon_tanker(c, x, y, w, h, cx, cy):
    c.fill_box(x, y + h - 12, w, 12, BLUE)
    c.fill_box(x + 30, y + 12, w - 70, 14, INK)
    c.fill_box(x + 44, y + 2, 16, 10, RED)
    c.fill_tri(x + 60, y + 2, 7, 10, ORANGE)
    c.fill_tri(x + 78, y + 6, 5, 8, GOLD)


def _icon_refinery(c, x, y, w, h, cx, cy):
    c.fill_box(x + 10, y + 12, 14, h - 12, GREY)
    c.fill_box(x + 30, y + 6, 14, h - 6, INK)
    c.fill_box(x + 50, y + 16, 16, h - 16, GREY)
    c.fill_tri(x + 37, y, 6, 10, ORANGE)
    c.fill_box(x, y + h - 4, w, 4, RED)


def _icon_drone(c, x, y, w, h, cx, cy):
    c.draw_line(x + 8, y + 8, x + w - 8, y + h - 8, INK)
    c.draw_line(x + w - 8, y + 8, x + 8, y + h - 8, INK)
    c.fill_disc(cx, cy, 7, RED)
    c.fill_disc(cx, cy, 3, WHITE)


def _icon_court(c, x, y, w, h, cx, cy):
    c.fill_tri(cx, y + 2, 30, 10, NAVY)
    c.fill_box(x + 6, y + 14, 8, h - 18, NAVY)
    c.fill_box(cx - 4, y + 14, 8, h - 18, NAVY)
    c.fill_box(x + w - 14, y + 14, 8, h - 18, NAVY)
    c.fill_box(x, y + h - 4, w, 4, NAVY)


def _icon_market(c, x, y, w, h, cx, cy):
    c.fill_box(x + 8, y + 12, w - 16, h - 12, BLUE)
    for i in range(5):
        col = RED if i % 2 == 0 else WHITE
        c.fill_box(x + 8 + i * (w - 16) // 5, y + 4, (w - 16) // 5, 8, col)
    c.fill_box(x + 22, y + 20, 20, 10, WHITE)


def _icon_treaty(c, x, y, w, h, cx, cy):
    c.fill_box(x + 30, y + 6, 52, 24, BLUE)
    c.fill_box(x + 90, y + 6, 52, 24, GREEN)
    c.fill_box(x + 36, y + 12, 40, 2, WHITE)
    c.fill_box(x + 96, y + 12, 40, 2, WHITE)
    c.fill_box(x + 36, y + 18, 28, 2, WHITE)
    c.fill_box(x + 96, y + 18, 28, 2, WHITE)
    c.fill_disc(cx, y + h - 8, 9, RED)
    c.draw_line(cx - 4, y + h - 8, cx - 1, y + h - 4, WHITE)
    c.draw_line(cx - 1, y + h - 4, cx + 5, y + h - 12, WHITE)


def _icon_strike(c, x, y, w, h, cx, cy):
    for dx, dy in ((-14, -8), (0, -12), (14, -8), (-16, 6), (16, 6)):
        c.draw_line(cx, cy, cx + dx, cy + dy, ORANGE)
    c.fill_disc(cx, cy, 8, RED)
    c.fill_disc(cx, cy, 4, GOLD)


def _icon_shirt(c, x, y, w, h, cx, cy):
    c.fill_box(cx - 22, y + 10, 44, h - 10, GREEN)
    c.fill_box(x + 8, y + 10, 22, 12, GREEN)
    c.fill_box(x + w - 30, y + 10, 22, 12, GREEN)
    c.fill_box(x + 28, y + 10, 4, 12, PAPER)
    c.fill_box(x + w - 32, y + 10, 4, 12, PAPER)
    c.fill_tri(cx, y + 10, 7, 8, WHITE)


def _icon_mine(c, x, y, w, h, cx, cy):
    c.fill_tri(cx, y + 2, 30, h - 2, (120, 90, 60))
    c.fill_box(cx - 8, y + h - 14, 16, 14, INK)
    c.fill_disc(cx, y + 8, 4, GOLD)


def _icon_cpi(c, x, y, w, h, cx, cy):
    for i, bh in enumerate((10, 18, 14, 24)):
        c.fill_box(x + 10 + i * 16, y + h - 4 - bh, 10, bh, GREEN)


def _icon_jet(c, x, y, w, h, cx, cy):
    c.fill_tri(cx, y + 6, 10, 20, NAVY)
    c.fill_box(cx - 22, y + 18, 44, 6, NAVY)
    c.fill_box(cx - 4, y + 26, 8, 12, NAVY)
    c.fill_box(x + 8, y + h - 8, w - 16, 4, RED)


def _icon_plane(c, x, y, w, h, cx, cy):
    c.fill_box(x + 10, y + 10, w - 20, 10, BLUE)
    c.fill_tri(x + w - 10, y + 10, 8, 10, BLUE)
    c.fill_box(cx - 4, y + 20, 8, 14, BLUE)


def _icon_fallback(c, x, y, w, h, cx, cy):
    c.fill_box(x, y, w, h, GREY)


_ICON_DRAWERS = {
    "tanker": _icon_tanker, "refinery": _icon_refinery, "drone": _icon_drone,
    "court": _icon_court, "market": _icon_market, "treaty": _icon_treaty,
    "strike": _icon_strike, "shirt": _icon_shirt, "mine": _icon_mine,
    "cpi": _icon_cpi, "jet": _icon_jet, "plane": _icon_plane,
}


def draw_icon(c, kind, x, y, w, h):
    cx = x + w // 2
    cy = y + h // 2
    _ICON_DRAWERS.get(kind, _icon_fallback)(c, x, y, w, h, cx, cy)


ICON_KIND = {4: "tanker", 5: "refinery", 6: "jet", 7: "jet",
             8: "court", 9: "court", 10: "treaty", 11: "plane",
             12: "strike", 13: "court", 14: "treaty", 15: "treaty"}

def draw_rocket(c, x, y, w, h):
    c.fill_box(x, y, w, h, SKY)
    for sx, sy in ((12, 10), (40, 26), (w - 20, 14), (w - 50, 34), (24, 48), (w - 30, 52)):
        c.fill_box(x + sx, y + sy, 2, 2, WHITE)
    cx = x + w // 2
    c.fill_tri(cx, y + 12, 8, 14, RED)
    c.fill_box(cx - 8, y + 26, 16, 42, WHITE)
    c.fill_box(cx - 8, y + 40, 16, 4, BLUE)
    c.fill_box(cx - 16, y + 52, 8, 16, RED)
    c.fill_box(cx + 8, y + 52, 8, 16, RED)
    c.fill_tri(cx, y + 68, 7, 16, ORANGE)
    c.fill_tri(cx, y + 72, 4, 12, GOLD)
    c.fill_disc(x + 26, y + 26, 9, (220, 220, 200))
    c.fill_box(x + w - 52, y + h - 16, 40, 4, GREY)

def draw_chart(c, x, y, w, h):
    c.fill_box(x, y, w, h, WHITE)
    for gy in range(4):
        yy = y + 12 + gy * 22
        c.fill_box(x + 8, yy, w - 16, 1, RULE)
    pts = [(x + 12, y + 30), (x + 60, y + 38), (x + 110, y + 36),
           (x + 160, y + 54), (x + 210, y + 66), (x + w - 14, y + 90)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        c.draw_thick(ax, ay, bx, by, 3, RED)
    for px, py in pts:
        c.fill_disc(px, py, 3, RED)
    c.draw_text(x + 10, y + 4, "-3%", 3, RED)
    c.draw_text(x + w - 110, y + h - 16, "NASDAQ FUTURES", 1, INK)

def draw_bars(c, x, y, w, h):
    c.fill_box(x, y, w, h, WHITE)
    data = [("CHINA", 20, NAVY), ("EU", 15, BLUE), ("INDIA", 25, RED), ("VIETNAM", 35, ORANGE)]
    bw = 52
    gap = (w - 4 * bw) // 5
    for i, (label, val, col) in enumerate(data):
        bx = x + gap + i * (bw + gap)
        bh = val * 2
        c.fill_box(bx, y + h - 22 - bh, bw, bh, col)
        c.draw_text(bx + (bw - c.measure(str(val) + "%", 1)) // 2, y + h - 18 - bh, str(val) + "%", 1, WHITE)
        c.draw_text(bx + (bw - c.measure(label, 1)) // 2, y + h - 16, label, 1, INK)
    c.fill_box(x + 8, y + h - 22, w - 16, 2, INK)

def render():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    c.draw_centered(12, "THURSDAY 26 NOVEMBER 2026", 3, INK)
    c.draw_centered(48, "49 STORIES - 7 REGIONS - ONE DAY", 2, RED)
    c.fill_box(20, 70, WIDTH - 40, 4, RED)
    c.draw_centered(82, "ASIA 12  MIDDLE EAST 4  EUROPE 7  AFRICA 3  AMERICAS 18  OCEANIA 1  GLOBAL 4", 1, INK)
    c.fill_box(20, 100, WIDTH - 40, 30, NAVY)
    c.draw_centered(108, "-3% NASDAQ  -  1ST ASTRONAUT  -  14 ECONOMIES  -  2,000 MIGRANTS  -  +36% WAGE", 2, WHITE)
    c.draw_centered(140, "THANKSGIVING IN THE US  -  MARKETS CLOSED  -  TIANGONG CREW IN ORBIT  -  HORMUZ SHIPS HIT  -  NATO JETS SCRAMBLE", 1, GREY)
    hx = [20, 352, 684]
    hw = 320
    hy = 158
    draw_rocket(c, hx[0], hy, hw, 104)
    c.draw_text(hx[0], hy + 112, "1. SHENZHOU-24 CREW", 2, INK)
    c.draw_text(hx[0], hy + 134, "ABOARD TIANGONG", 2, INK)
    c.draw_text(hx[0], hy + 156, "PAKISTAN'S FIRST ASTRONAUT, ZEESHAN ALI, IN ORBIT", 1, GREY)
    draw_chart(c, hx[1], hy, hw, 104)
    c.draw_text(hx[1], hy + 112, "2. THANKSGIVING DAY,", 2, INK)
    c.draw_text(hx[1], hy + 134, "AI SELLOFF RESUMES", 2, INK)
    c.draw_text(hx[1], hy + 156, "US MARKETS CLOSED - NASDAQ FUTURES -3%", 1, GREY)
    draw_bars(c, hx[2], hy, hw, 104)
    c.draw_text(hx[2], hy + 112, "3. US TO UNVEIL TARIFF", 2, INK)
    c.draw_text(hx[2], hy + 134, "PROBE ON 14 ECONOMIES", 2, INK)
    c.draw_text(hx[2], hy + 156, "CHINA 20% - EU 15% - INDIA 25% - VIETNAM 35%", 1, GREY)
    # Middle cards 4-15: 6 cols x 2 rows
    mw, mh = 160, 118
    for i, card in enumerate(MID):
        num, region, text = card["n"], card["region"], card["copy"]
        col, row = i % 6, i // 6
        x = 20 + col * (mw + 8)
        y = 336 + row * (mh + 10)
        c.fill_box(x, y, mw, mh, CARD)
        c.fill_box(x, y, mw, 2, REGION_COL[region])
        c.fill_box(x, y + 6, 24, 20, NAVY)
        c.draw_text(x + (24 - c.measure(str(num), 2)) // 2, y + 10, str(num), 2, WHITE)
        c.draw_text(x + mw - 4 - c.measure(region, 1), y + 10, region, 1, REGION_COL[region])
        draw_icon(c, ICON_KIND[num], x + 8, y + 32, mw - 16, 34)
        lines = wrap(text, 24)[:3]
        ly = y + 72
        for line in lines:
            c.draw_text(x + 6, ly, line, 1, INK)
            ly += 10
    # Bottom: map (left) + list 16-49 (right, 2 cols)
    by = 592
    c.fill_box(20, by, 300, 340, CARD)
    c.fill_box(20, by, 300, 2, NAVY)
    c.draw_text(32, by + 10, "WHERE IT HAPPENED", 2, NAVY)
    mx, my, mw2, mh2 = 32, by + 34, 276, 260
    c.fill_box(mx, my, mw2, mh2, (232, 238, 244))
    c.fill_box(mx + 28, my + 40, 66, 56, (190, 200, 190))
    c.fill_box(mx + 104, my + 30, 56, 66, (190, 200, 190))
    c.fill_box(mx + 170, my + 50, 76, 56, (190, 200, 190))
    c.fill_box(mx + 190, my + 130, 48, 38, (190, 200, 190))
    c.fill_box(mx + 38, my + 130, 38, 48, (190, 200, 190))
    for num, lon, lat in DOTS:
        dx = mx + int((lon + 180) / 360.0 * mw2)
        dy = my + int((90 - lat) / 180.0 * mh2)
        c.fill_box(dx - 7, dy - 7, 14, 14, RED)
        c.draw_text(dx - c.measure(str(num), 1) // 2, dy - 4, str(num), 1, WHITE)
    c.draw_text(32, by + 306, "DOTS 1-15 MARK THE TOP STORIES", 1, GREY)
    list_cols = [LIST[:17], LIST[17:]]
    list_x = [336, 688]
    for col_idx, items in enumerate(list_cols):
        x = list_x[col_idx]
        ly = by + 6
        for item in items:
            lines = wrap(str(item["n"]) + ". " + item["copy"], 48)[:2]
            for line in lines:
                c.draw_text(x, ly, line, 1, INK)
                ly += 11
            ly += 4
    c.fill_box(20, 956, WIDTH - 40, 2, RULE)
    c.draw_text(20, 970, FOOTER1, 1, RED)
    c.draw_text(20, 988, FOOTER2, 1, GREY)
    return bytes(c.pix)

def main():
    out_dir = Path(os.environ.get("OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    png = encode_png(render(), WIDTH, HEIGHT)
    out_path = out_dir / "entry.png"
    out_path.write_bytes(png)
    print(f"Wrote {len(png)} bytes to {out_path} ({WIDTH}x{HEIGHT})")

if __name__ == "__main__":
    main()
