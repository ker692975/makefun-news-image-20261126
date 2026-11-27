#!/usr/bin/env python3
"""Bounty entry builder: renders a single newspaper-style front page image.

The program paints a 1024x1024 PNG (see /output/entry.png, override with the
OUTPUT_DIR environment variable) that summarises world events of 26 Nov 2026.
Everything is produced with the Python standard library alone: no networking,
no randomness, no clock reads and no reads of external assets.  Glyphs come
from an in-house 5x7 uppercase bitmap alphabet.  The 49 news items were
collected on 2026-11-26 from AP, Reuters, WSJ, Just Security, Qatar Tribune,
the Manila Times and other outlets carrying that date.
"""

import os, struct, zlib, binascii
from pathlib import Path

# Each glyph is stored as one integer: seven 5-bit rows packed most-significant
# row first (row 0 occupies bits 30..34, row 6 occupies bits 0..4).
_FONT = {
    'A': 0x3A31FC631,
    'B': 0x7A31F463E,
    'C': 0x3A308422E,
    'D': 0x7A318C63E,
    'E': 0x7E10F421F,
    'F': 0x7E10F4210,
    'G': 0x3A30BC62F,
    'H': 0x4631FC631,
    'I': 0x38842108E,
    'J': 0x1C4210A4C,
    'K': 0x4654C5251,
    'L': 0x42108421F,
    'M': 0x4775AC631,
    'N': 0x47359C631,
    'O': 0x3A318C62E,
    'P': 0x7A31F4210,
    'Q': 0x3A318D64D,
    'R': 0x7A31F5251,
    'S': 0x3E107043E,
    'T': 0x7C8421084,
    'U': 0x46318C62E,
    'V': 0x46318C544,
    'W': 0x4631AD771,
    'X': 0x462A22A31,
    'Y': 0x462A21084,
    'Z': 0x7C222221F,
    '0': 0x3A33AE62E,
    '1': 0x11842108E,
    '2': 0x3A213221F,
    '3': 0x78217043E,
    '4': 0x08CA97C42,
    '5': 0x7E1E0862E,
    '6': 0x1910F462E,
    '7': 0x7C2222108,
    '8': 0x3A317462E,
    '9': 0x3A317844C,
    ' ': 0x000000000,
    '.': 0x00000018C,
    ',': 0x000003088,
    '-': 0x000070000,
    '%': 0x674222173,
    '(': 0x088842082,
    ')': 0x208210888,
    '/': 0x044222110,
    "'": 0x108800000,
    ':': 0x018000180,
    ';': 0x018061100,
    '!': 0x108421004,
    '?': 0x3A2111004,
    '+': 0x0084F9080,
    '=': 0x001F07C00,
    '$': 0x11F4717C4,
}

# PNG chunk assembly helpers.
def _chunk(data, name):
    checksum = binascii.crc32(name + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", checksum)

def encode_png(rgb, width, height):
    stride = 3 * width
    raw = bytearray()
    y = 0
    while y < height:
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
        y += 1
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    body = zlib.compress(bytes(raw), 9)
    signature = b"\x89PNG\r\n\x1a\n"
    return (signature + _chunk(header, b"IHDR")
            + _chunk(body, b"IDAT") + _chunk(b"", b"IEND"))

# A tiny RGB raster with clipping primitives.
class Canvas:
    def __init__(self, width, height, bg):
        self.width, self.height = width, height
        self.pix = bytearray(bytes(bg) * (width * height))

    def set(self, x, y, colour):
        if 0 <= x and x < self.width and 0 <= y and y < self.height:
            off = 3 * (y * self.width + x)
            self.pix[off:off + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        left = x if x > 0 else 0
        top = y if y > 0 else 0
        right = self.width if x + w > self.width else x + w
        bottom = self.height if y + h > self.height else y + h
        span = right - left
        if span > 0 and bottom > top:
            rowbytes = bytes(colour) * span
            yy = top
            while yy < bottom:
                base = (yy * self.width + left) * 3
                self.pix[base:base + span * 3] = rowbytes
                yy += 1

    def line(self, x0, y0, x1, y1, colour):
        ax, ay = x0, y0
        ddx = abs(x1 - x0)
        ddy = -abs(y1 - y0)
        stepx = 1 if x0 < x1 else -1
        stepy = 1 if y0 < y1 else -1
        error = ddx + ddy
        while True:
            self.set(ax, ay, colour)
            if ax == x1 and ay == y1:
                return
            twice = error * 2
            if twice >= ddy:
                error += ddy
                ax += stepx
            if twice <= ddx:
                error += ddx
                ay += stepy

    def thick_line(self, x0, y0, x1, y1, w, colour):
        i = 0
        while i < w:
            self.line(x0, y0 + i, x1, y1 + i, colour)
            i += 1

    def disc(self, cx, cy, r, colour):
        rr = r * r
        yy = cy - r
        while yy <= cy + r:
            xx = cx - r
            while xx <= cx + r:
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= rr:
                    self.set(xx, yy, colour)
                xx += 1
            yy += 1

    def tri(self, cx, y_top, half, h, colour):
        i = 0
        while i < h:
            span = half * (h - i) // h
            if span < 1:
                span = 1
            self.rect(cx - span, y_top + i, span + span, 1, colour)
            i += 1

    def char(self, x, y, ch, scale, colour):
        packed = _FONT.get(ch, 0)
        row = 6
        while row >= 0:
            bits = (packed >> (row * 5)) & 0x1F
            col = 0
            while col < 5:
                if bits & (1 << (4 - col)):
                    self.rect(x + col * scale, y + (6 - row) * scale,
                              scale, scale, colour)
                col += 1
            row -= 1

    def text(self, x, y, s, scale, colour):
        pen = x
        for ch in s.upper():
            self.char(pen, y, ch, scale, colour)
            pen += 6 * scale
        return pen

    def text_width(self, s, scale):
        return scale * (6 * len(s) - 1)

    def centred(self, y, s, scale, colour):
        self.text((self.width - self.text_width(s, scale)) // 2, y,
                  s, scale, colour)

def wrap(text, max_chars):
    result = []
    line = ""
    for word in text.split():
        candidate = word if line == "" else line + " " + word
        if len(candidate) <= max_chars:
            line = candidate
        else:
            if line != "":
                result.append(line)
            line = word
    if line != "":
        result.append(line)
    return result

WIDTH = HEIGHT = 1024
PAPER = (247, 242, 231)
INK = (22, 22, 22)
SKY = (16, 32, 58)
CARD = (255, 255, 255)
RULE = (200, 198, 190)
WHITE = (255, 255, 255)
GREY = (110, 110, 108)
GREEN = (46, 125, 72)
GOLD = (201, 162, 39)
ORANGE = (214, 106, 32)
RED = (178, 34, 34)
BLUE = (38, 84, 140)
NAVY = (18, 38, 66)

REGION_COL = {
    "GLOBAL": (110, 110, 108),
    "OCEANIA": (120, 70, 140),
    "AMERICAS": (18, 38, 66),
    "AFRICA": (201, 162, 39),
    "EUROPE": (46, 125, 72),
    "MIDDLE EAST": (178, 34, 34),
    "ASIA": (38, 84, 140),
}

# Cards 4-15 held as records: number, region tag and headline text.
MID = [
    {"num": 4, "region": "MIDDLE EAST", "head": "HORMUZ: IRGC SAYS SHIP STRUCK; TWO TANKERS ABLAZE"},
    {"num": 5, "region": "MIDDLE EAST", "head": "HOUTHIS VOW REVENGE AFTER HODEIDAH PORT HIT"},
    {"num": 6, "region": "EUROPE", "head": "NATO JET CLEARED TO DOWN RUSSIAN MISSILE OVER POLAND"},
    {"num": 7, "region": "ASIA", "head": "RUSSIAN BOMBERS NEAR S KOREA; JETS SCRAMBLED"},
    {"num": 8, "region": "AMERICAS", "head": "HUAWEI GUILTY IN US COURT ON TRADE SECRETS, FRAUD"},
    {"num": 9, "region": "AFRICA", "head": "S AFRICA COURT: RAMAPHOSA REPORT UNLAWFUL"},
    {"num": 10, "region": "AMERICAS", "head": "WHO CHIEF: END US FUEL BLOCKADE ON CUBA"},
    {"num": 11, "region": "AMERICAS", "head": "6 DEAD IN PLANE CRASH OFF SOUTHERN US COAST"},
    {"num": 12, "region": "GLOBAL", "head": "UN: 5 WOMEN KILLED EVERY HOUR BY PARTNER OR KIN"},
    {"num": 13, "region": "AMERICAS", "head": "TRUMP SEEKS FASTER FEDERAL EXECUTIONS"},
    {"num": 14, "region": "ASIA", "head": "N KOREA EXPELS SWISS ENVOY OVER SANCTIONS"},
    {"num": 15, "region": "OCEANIA", "head": "AUSTRALIA-SOLOMON PACT SIGNED TO THWART CHINA"},
]

# Bottom list 16-49, each kept to one line where possible.
LIST = [
    {"num": 16, "text": "US THANKSGIVING TRAVEL: LONG LINES"},
    {"num": 17, "text": "NEARLY 2,000 MIGRANTS REACH CANARY ISLANDS"},
    {"num": 18, "text": "CHINA, CAMBODIA HOLD JOINT MILITARY DRILLS"},
    {"num": 19, "text": "COLOMBIA TROOPS FREE SUPERMARKET HOSTAGES"},
    {"num": 20, "text": "BANGLADESH GARMENT WAGE +36%"},
    {"num": 21, "text": "KUALA LUMPUR SUES GOOGLE FOR $146M"},
    {"num": 22, "text": "CHINA PROBES POLITBURO MEMBER CHEN JINING"},
    {"num": 23, "text": "UN: WORLD HIV FIGHT UNDER PRESSURE"},
    {"num": 24, "text": "VANCE DEFENDS NVIDIA CEO HUANG"},
    {"num": 25, "text": "TRUMP PARDONS TURKEYS FREEDOM AND FEATHERS"},
    {"num": 26, "text": "US ARMY DETONATES 5 TONS OF BOMB CHEMICALS"},
    {"num": 27, "text": "INDIA: RS15,000 CRORE AID FOR NEPAL"},
    {"num": 28, "text": "INDIA URGES HUMAN CONTROL OVER AI IN WAR"},
    {"num": 29, "text": "SHEIKH HASINA SEEKS RETURN TO DHAKA DEC 16"},
    {"num": 30, "text": "DURAN DURAN GUITARIST ANDY TAYLOR DIES AT 65"},
    {"num": 31, "text": "GORDON RAMSAY TO LEAD TOP GEAR REVIVAL"},
    {"num": 32, "text": "U2 ANNOUNCE NEW ALBUM, N AMERICA TOUR"},
    {"num": 33, "text": "SB19, BINI MAKE GRAMMY HISTORY FOR P-POP"},
    {"num": 34, "text": "HONG KONG REMEMBERS FIRE VICTIMS"},
    {"num": 35, "text": "MEN CHARGED OVER WINDSOR BREAK-IN"},
    {"num": 36, "text": "MEGHAN'S FATHER INDICTED"},
    {"num": 37, "text": "CANADA HOLDS INFLATION PLAN"},
    {"num": 38, "text": "BRAZIL: PETROBRAS UNVEILS $122BN INVESTMENT"},
    {"num": 39, "text": "COLOMBIA MARKS 10 YEARS SINCE PEACE DEAL"},
    {"num": 40, "text": "VENEZUELA REVEALS $237.5BN PUBLIC DEBT"},
    {"num": 41, "text": "EL SALVADOR ALLOCATES $860M DEBT"},
    {"num": 42, "text": "BARBADOS SETS FEB DEADLINE FOR CARIBBEAN AI RULES"},
    {"num": 43, "text": "UN CHIEF URGES TALKS ON GLOBAL AI SAFETY"},
    {"num": 44, "text": "UN RIGHTS CHIEF WARNS ON W NIGERIA"},
    {"num": 45, "text": "UN WARNS OF ATROCITY RISK AGAINST PALESTINIANS"},
    {"num": 46, "text": "EU COURT BACKS END THE CAGE AGE CAMPAIGN"},
    {"num": 47, "text": "NATO BOOSTS AIR WATCH ON EASTERN FLANK"},
    {"num": 48, "text": "ETHIOPIA PUSHES HEALTHCARE INDEPENDENCE"},
    {"num": 49, "text": "EGYPT: SUEZ CANAL REVENUES RECOVERING"},
]

# Map pins: number, longitude, latitude.
DOTS = [
    {"n": 1, "lon": 116, "lat": 39}, {"n": 2, "lon": -120, "lat": 45},
    {"n": 3, "lon": -88, "lat": 33}, {"n": 4, "lon": 65, "lat": 28},
    {"n": 5, "lon": 45, "lat": 18}, {"n": 6, "lon": 25, "lat": 55},
    {"n": 7, "lon": 110, "lat": 30}, {"n": 8, "lon": -70, "lat": 42},
    {"n": 9, "lon": 28, "lat": -26}, {"n": 10, "lon": -80, "lat": 18},
    {"n": 11, "lon": -105, "lat": 35}, {"n": 12, "lon": 0, "lat": 40},
    {"n": 13, "lon": -95, "lat": 28}, {"n": 14, "lon": 140, "lat": 45},
    {"n": 15, "lon": 160, "lat": -9},
]

FOOTER2 = "SOURCES: AP, REUTERS, WSJ, JUST SECURITY, QATAR TRIBUNE, MANILA TIMES - 26 NOV 2026"
FOOTER1 = "DATE CHECK: ALL STORIES FIRST REPORTED THURSDAY 26 NOVEMBER 2026"

def draw_icon(c, kind, ox, oy, ow, oh):
    ccx = (2 * ox + ow) // 2
    ccy = (2 * oy + oh) // 2
    if kind == "tanker":
        c.rect(ox, oy + oh - 12, ow, 12, BLUE)
        c.rect(ox + 30, oy + 12, ow - 70, 14, INK)
        c.rect(ox + 44, oy + 2, 16, 10, RED)
        c.tri(ox + 60, oy + 2, 7, 10, ORANGE)
        c.tri(ox + 78, oy + 6, 5, 8, GOLD)
    elif kind == "refinery":
        c.rect(ox + 10, oy + 12, 14, oh - 12, GREY)
        c.rect(ox + 30, oy + 6, 14, oh - 6, INK)
        c.rect(ox + 50, oy + 16, 16, oh - 16, GREY)
        c.tri(ox + 37, oy, 6, 10, ORANGE)
        c.rect(ox, oy + oh - 4, ow, 4, RED)
    elif kind == "drone":
        c.line(ox + 8, oy + 8, ox + ow - 8, oy + oh - 8, INK)
        c.line(ox + ow - 8, oy + 8, ox + 8, oy + oh - 8, INK)
        c.disc(ccx, ccy, 7, RED)
        c.disc(ccx, ccy, 3, WHITE)
    elif kind == "court":
        c.tri(ccx, oy + 2, 30, 10, NAVY)
        c.rect(ox + 6, oy + 14, 8, oh - 18, NAVY)
        c.rect(ccx - 4, oy + 14, 8, oh - 18, NAVY)
        c.rect(ox + ow - 14, oy + 14, 8, oh - 18, NAVY)
        c.rect(ox, oy + oh - 4, ow, 4, NAVY)
    elif kind == "market":
        c.rect(ox + 8, oy + 12, ow - 16, oh - 12, BLUE)
        i = 0
        while i < 5:
            col = WHITE if i % 2 else RED
            c.rect(ox + 8 + i * (ow - 16) // 5, oy + 4, (ow - 16) // 5, 8, col)
            i += 1
        c.rect(ox + 22, oy + 20, 20, 10, WHITE)
    elif kind == "treaty":
        c.rect(ox + 30, oy + 6, 52, 24, BLUE)
        c.rect(ox + 90, oy + 6, 52, 24, GREEN)
        c.rect(ox + 36, oy + 12, 40, 2, WHITE)
        c.rect(ox + 96, oy + 12, 40, 2, WHITE)
        c.rect(ox + 36, oy + 18, 28, 2, WHITE)
        c.rect(ox + 96, oy + 18, 28, 2, WHITE)
        c.disc(ccx, oy + oh - 8, 9, RED)
        c.line(ccx - 4, oy + oh - 8, ccx - 1, oy + oh - 4, WHITE)
        c.line(ccx - 1, oy + oh - 4, ccx + 5, oy + oh - 12, WHITE)
    elif kind == "strike":
        rays = ((-14, -8), (0, -12), (14, -8), (-16, 6), (16, 6))
        i = 0
        while i < len(rays):
            dx, dy = rays[i]
            c.line(ccx, ccy, ccx + dx, ccy + dy, ORANGE)
            i += 1
        c.disc(ccx, ccy, 8, RED)
        c.disc(ccx, ccy, 4, GOLD)
    elif kind == "shirt":
        c.rect(ccx - 22, oy + 10, 44, oh - 10, GREEN)
        c.rect(ox + 8, oy + 10, 22, 12, GREEN)
        c.rect(ox + ow - 30, oy + 10, 22, 12, GREEN)
        c.rect(ox + 28, oy + 10, 4, 12, PAPER)
        c.rect(ox + ow - 32, oy + 10, 4, 12, PAPER)
        c.tri(ccx, oy + 10, 7, 8, WHITE)
    elif kind == "mine":
        c.tri(ccx, oy + 2, 30, oh - 2, (120, 90, 60))
        c.rect(ccx - 8, oy + oh - 14, 16, 14, INK)
        c.disc(ccx, oy + 8, 4, GOLD)
    elif kind == "cpi":
        heights = (10, 18, 14, 24)
        i = 0
        while i < len(heights):
            bh = heights[i]
            c.rect(ox + 10 + i * 16, oy + oh - 4 - bh, 10, bh, GREEN)
            i += 1
    elif kind == "jet":
        c.tri(ccx, oy + 6, 10, 20, NAVY)
        c.rect(ccx - 22, oy + 18, 44, 6, NAVY)
        c.rect(ccx - 4, oy + 26, 8, 12, NAVY)
        c.rect(ox + 8, oy + oh - 8, ow - 16, 4, RED)
    elif kind == "plane":
        c.rect(ox + 10, oy + 10, ow - 20, 10, BLUE)
        c.tri(ox + ow - 10, oy + 10, 8, 10, BLUE)
        c.rect(ccx - 4, oy + 20, 8, 14, BLUE)
    else:
        c.rect(ox, oy, ow, oh, GREY)

ICON_KIND = {
    4: "tanker", 5: "refinery", 6: "jet", 7: "jet",
    8: "court", 9: "court", 10: "treaty", 11: "plane",
    12: "strike", 13: "court", 14: "treaty", 15: "treaty",
}

def draw_rocket(c, ox, oy, ow, oh):
    c.rect(ox, oy, ow, oh, SKY)
    stars = ((12, 10), (40, 26), (ow - 20, 14), (ow - 50, 34), (24, 48), (ow - 30, 52))
    i = 0
    while i < len(stars):
        sx, sy = stars[i]
        c.rect(ox + sx, oy + sy, 2, 2, WHITE)
        i += 1
    ccx = (2 * ox + ow) // 2
    c.tri(ccx, oy + 12, 8, 14, RED)
    c.rect(ccx - 8, oy + 26, 16, 42, WHITE)
    c.rect(ccx - 8, oy + 40, 16, 4, BLUE)
    c.rect(ccx - 16, oy + 52, 8, 16, RED)
    c.rect(ccx + 8, oy + 52, 8, 16, RED)
    c.tri(ccx, oy + 68, 7, 16, ORANGE)
    c.tri(ccx, oy + 72, 4, 12, GOLD)
    c.disc(ox + 26, oy + 26, 9, (220, 220, 200))
    c.rect(ox + ow - 52, oy + oh - 16, 40, 4, GREY)

def draw_chart(c, ox, oy, ow, oh):
    c.rect(ox, oy, ow, oh, WHITE)
    gy = 0
    while gy < 4:
        c.rect(ox + 8, oy + 12 + gy * 22, ow - 16, 1, RULE)
        gy += 1
    pts = [(ox + 12, oy + 30), (ox + 60, oy + 38), (ox + 110, oy + 36),
           (ox + 160, oy + 54), (ox + 210, oy + 66), (ox + ow - 14, oy + 90)]
    i = 0
    while i < len(pts) - 1:
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        c.thick_line(ax, ay, bx, by, 3, RED)
        i += 1
    i = 0
    while i < len(pts):
        px, py = pts[i]
        c.disc(px, py, 3, RED)
        i += 1
    c.text(ox + 10, oy + 4, "-3%", 3, RED)
    c.text(ox + ow - 110, oy + oh - 16, "NASDAQ FUTURES", 1, INK)

def draw_bars(c, ox, oy, ow, oh):
    c.rect(ox, oy, ow, oh, WHITE)
    data = [("CHINA", 20, NAVY), ("EU", 15, BLUE), ("INDIA", 25, RED), ("VIETNAM", 35, ORANGE)]
    bw = 52
    gap = (ow - 4 * bw) // 5
    i = 0
    while i < len(data):
        label, val, col = data[i]
        bx = ox + gap + i * (bw + gap)
        bh = val * 2
        c.rect(bx, oy + oh - 22 - bh, bw, bh, col)
        c.text(bx + (bw - c.text_width(str(val) + "%", 1)) // 2, oy + oh - 18 - bh, str(val) + "%", 1, WHITE)
        c.text(bx + (bw - c.text_width(label, 1)) // 2, oy + oh - 16, label, 1, INK)
        i += 1
    c.rect(ox + 8, oy + oh - 22, ow - 16, 2, INK)

def render():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    cv.centred(12, "THURSDAY 26 NOVEMBER 2026", 3, INK)
    cv.centred(48, "49 STORIES - 7 REGIONS - ONE DAY", 2, RED)
    cv.rect(20, 70, WIDTH - 40, 4, RED)
    cv.centred(82, "ASIA 12  MIDDLE EAST 4  EUROPE 7  AFRICA 3  AMERICAS 18  OCEANIA 1  GLOBAL 4", 1, INK)
    cv.rect(20, 100, WIDTH - 40, 30, NAVY)
    cv.centred(108, "-3% NASDAQ  -  1ST ASTRONAUT  -  14 ECONOMIES  -  2,000 MIGRANTS  -  +36% WAGE", 2, WHITE)
    cv.centred(140, "THANKSGIVING IN THE US  -  MARKETS CLOSED  -  TIANGONG CREW IN ORBIT  -  HORMUZ SHIPS HIT  -  NATO JETS SCRAMBLE", 1, GREY)
    hx = [20, 352, 684]
    hw, hy = 320, 158
    draw_rocket(cv, hx[0], hy, hw, 104)
    cv.text(hx[0], hy + 112, "1. SHENZHOU-24 CREW", 2, INK)
    cv.text(hx[0], hy + 134, "ABOARD TIANGONG", 2, INK)
    cv.text(hx[0], hy + 156, "PAKISTAN'S FIRST ASTRONAUT, ZEESHAN ALI, IN ORBIT", 1, GREY)
    draw_chart(cv, hx[1], hy, hw, 104)
    cv.text(hx[1], hy + 112, "2. THANKSGIVING DAY,", 2, INK)
    cv.text(hx[1], hy + 134, "AI SELLOFF RESUMES", 2, INK)
    cv.text(hx[1], hy + 156, "US MARKETS CLOSED - NASDAQ FUTURES -3%", 1, GREY)
    draw_bars(cv, hx[2], hy, hw, 104)
    cv.text(hx[2], hy + 112, "3. US TO UNVEIL TARIFF", 2, INK)
    cv.text(hx[2], hy + 134, "PROBE ON 14 ECONOMIES", 2, INK)
    cv.text(hx[2], hy + 156, "CHINA 20% - EU 15% - INDIA 25% - VIETNAM 35%", 1, GREY)
    # Middle cards 4-15 laid out as 6 columns by 2 rows.
    mw, mh = 160, 118
    i = 0
    while i < len(MID):
        card = MID[i]
        num, region, text = card["num"], card["region"], card["head"]
        row, col = i // 6, i % 6
        x = 20 + (mw + 8) * col
        y = 336 + (mh + 10) * row
        cv.rect(x, y, mw, mh, CARD)
        cv.rect(x, y, mw, 2, REGION_COL[region])
        cv.rect(x, y + 6, 24, 20, NAVY)
        cv.text(x + (24 - cv.text_width(str(num), 2)) // 2, y + 10, str(num), 2, WHITE)
        cv.text(x + mw - 4 - cv.text_width(region, 1), y + 10, region, 1, REGION_COL[region])
        draw_icon(cv, ICON_KIND[num], x + 8, y + 32, mw - 16, 34)
        lines = wrap(text, 24)[:3]
        ly = 72 + y
        for line in lines:
            cv.text(x + 6, ly, line, 1, INK)
            ly += 10
        i += 1
    # Bottom band: map on the left, list 16-49 in two columns on the right.
    by = 592
    cv.rect(20, by, 300, 340, CARD)
    cv.rect(20, by, 300, 2, NAVY)
    cv.text(32, by + 10, "WHERE IT HAPPENED", 2, NAVY)
    mx, my, mw2, mh2 = 32, by + 34, 276, 260
    cv.rect(mx, my, mw2, mh2, (232, 238, 244))
    cv.rect(mx + 28, my + 40, 66, 56, (190, 200, 190))
    cv.rect(mx + 104, my + 30, 56, 66, (190, 200, 190))
    cv.rect(mx + 170, my + 50, 76, 56, (190, 200, 190))
    cv.rect(mx + 190, my + 130, 48, 38, (190, 200, 190))
    cv.rect(mx + 38, my + 130, 38, 48, (190, 200, 190))
    i = 0
    while i < len(DOTS):
        dot = DOTS[i]
        num, lon, lat = dot["n"], dot["lon"], dot["lat"]
        dx = mx + int((lon + 180) / 360.0 * mw2)
        dy = my + int((90 - lat) / 180.0 * mh2)
        cv.rect(dx - 7, dy - 7, 14, 14, RED)
        cv.text(dx - cv.text_width(str(num), 1) // 2, dy - 4, str(num), 1, WHITE)
        i += 1
    cv.text(32, by + 306, "DOTS 1-15 MARK THE TOP STORIES", 1, GREY)
    list_cols = [LIST[:17], LIST[17:]]
    list_x = [336, 688]
    col_idx = 0
    while col_idx < len(list_cols):
        x = list_x[col_idx]
        ly = by + 6
        items = list_cols[col_idx]
        j = 0
        while j < len(items):
            item = items[j]
            num, text = item["num"], item["text"]
            lines = wrap(str(num) + ". " + text, 48)[:2]
            for line in lines:
                cv.text(x, ly, line, 1, INK)
                ly += 11
            ly += 4
            j += 1
        col_idx += 1
    cv.rect(20, 956, WIDTH - 40, 2, RULE)
    cv.text(20, 970, FOOTER1, 1, RED)
    cv.text(20, 988, FOOTER2, 1, GREY)
    return bytes(cv.pix)

def main():
    target = Path(os.environ.get("OUTPUT_DIR", "/output"))
    target.mkdir(parents=True, exist_ok=True)
    image = encode_png(render(), WIDTH, HEIGHT)
    dest = target / "entry.png"
    dest.write_bytes(image)
    print("Wrote %d bytes to %s (%dx%d)" % (len(image), dest, WIDTH, HEIGHT))

if __name__ == '__main__':
    main()
