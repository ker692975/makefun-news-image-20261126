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

_G = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
    "3": [0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    " ": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
    ",": [0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08],
    "-": [0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00],
    "%": [0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "/": [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10],
    "'": [0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00],
    ":": [0x00, 0x0C, 0x00, 0x00, 0x00, 0x0C, 0x00],
    ";": [0x00, 0x0C, 0x00, 0x0C, 0x04, 0x08, 0x00],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
    "?": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04],
    "+": [0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00],
    "=": [0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00],
    "$": [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
}

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

    def set(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pix[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            row = bytes(colour) * (x1 - x0)
            self.pix[base:base + (x1 - x0) * 3] = row

    def line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, colour)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def thick_line(self, x0, y0, x1, y1, w, colour):
        for i in range(w):
            self.line(x0, y0 + i, x1, y1 + i, colour)

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, colour)

    def tri(self, cx, y_top, half, h, colour):
        for i in range(h):
            w = half * (h - i) // h
            if w < 1:
                w = 1
            self.rect(cx - w, y_top + i, 2 * w, 1, colour)

    def char(self, x, y, ch, scale, colour):
        glyph = _G.get(ch, _G[" "])
        for r, bits in enumerate(glyph):
            for c in range(5):
                if bits & (1 << (4 - c)):
                    px = x + c * scale
                    py = y + r * scale
                    self.rect(px, py, scale, scale, colour)

    def text(self, x, y, s, scale, colour):
        s = s.upper()
        cx = x
        for ch in s:
            self.char(cx, y, ch, scale, colour)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def centred(self, y, s, scale, colour):
        w = self.text_width(s, scale)
        self.text((self.width - w) // 2, y, s, scale, colour)

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

# Cards 4-15: (number, region, headline)
MID = [
    (4, "MIDDLE EAST", "HORMUZ: IRGC SAYS SHIP STRUCK; TWO TANKERS ABLAZE"),
    (5, "MIDDLE EAST", "HOUTHIS VOW REVENGE AFTER HODEIDAH PORT HIT"),
    (6, "EUROPE", "NATO JET CLEARED TO DOWN RUSSIAN MISSILE OVER POLAND"),
    (7, "ASIA", "RUSSIAN BOMBERS NEAR S KOREA; JETS SCRAMBLED"),
    (8, "AMERICAS", "HUAWEI GUILTY IN US COURT ON TRADE SECRETS, FRAUD"),
    (9, "AFRICA", "S AFRICA COURT: RAMAPHOSA REPORT UNLAWFUL"),
    (10, "AMERICAS", "WHO CHIEF: END US FUEL BLOCKADE ON CUBA"),
    (11, "AMERICAS", "6 DEAD IN PLANE CRASH OFF SOUTHERN US COAST"),
    (12, "GLOBAL", "UN: 5 WOMEN KILLED EVERY HOUR BY PARTNER OR KIN"),
    (13, "AMERICAS", "TRUMP SEEKS FASTER FEDERAL EXECUTIONS"),
    (14, "ASIA", "N KOREA EXPELS SWISS ENVOY OVER SANCTIONS"),
    (15, "OCEANIA", "AUSTRALIA-SOLOMON PACT SIGNED TO THWART CHINA"),
]

# Bottom list 16-49, each kept to one line where possible
LIST = [
    (16, "US THANKSGIVING TRAVEL: LONG LINES"),
    (17, "NEARLY 2,000 MIGRANTS REACH CANARY ISLANDS"),
    (18, "CHINA, CAMBODIA HOLD JOINT MILITARY DRILLS"),
    (19, "COLOMBIA TROOPS FREE SUPERMARKET HOSTAGES"),
    (20, "BANGLADESH GARMENT WAGE +36%"),
    (21, "KUALA LUMPUR SUES GOOGLE FOR $146M"),
    (22, "CHINA PROBES POLITBURO MEMBER CHEN JINING"),
    (23, "UN: WORLD HIV FIGHT UNDER PRESSURE"),
    (24, "VANCE DEFENDS NVIDIA CEO HUANG"),
    (25, "TRUMP PARDONS TURKEYS FREEDOM AND FEATHERS"),
    (26, "US ARMY DETONATES 5 TONS OF BOMB CHEMICALS"),
    (27, "INDIA: RS15,000 CRORE AID FOR NEPAL"),
    (28, "INDIA URGES HUMAN CONTROL OVER AI IN WAR"),
    (29, "SHEIKH HASINA SEEKS RETURN TO DHAKA DEC 16"),
    (30, "DURAN DURAN GUITARIST ANDY TAYLOR DIES AT 65"),
    (31, "GORDON RAMSAY TO LEAD TOP GEAR REVIVAL"),
    (32, "U2 ANNOUNCE NEW ALBUM, N AMERICA TOUR"),
    (33, "SB19, BINI MAKE GRAMMY HISTORY FOR P-POP"),
    (34, "HONG KONG REMEMBERS FIRE VICTIMS"),
    (35, "MEN CHARGED OVER WINDSOR BREAK-IN"),
    (36, "MEGHAN'S FATHER INDICTED"),
    (37, "CANADA HOLDS INFLATION PLAN"),
    (38, "BRAZIL: PETROBRAS UNVEILS $122BN INVESTMENT"),
    (39, "COLOMBIA MARKS 10 YEARS SINCE PEACE DEAL"),
    (40, "VENEZUELA REVEALS $237.5BN PUBLIC DEBT"),
    (41, "EL SALVADOR ALLOCATES $860M DEBT"),
    (42, "BARBADOS SETS FEB DEADLINE FOR CARIBBEAN AI RULES"),
    (43, "UN CHIEF URGES TALKS ON GLOBAL AI SAFETY"),
    (44, "UN RIGHTS CHIEF WARNS ON W NIGERIA"),
    (45, "UN WARNS OF ATROCITY RISK AGAINST PALESTINIANS"),
    (46, "EU COURT BACKS END THE CAGE AGE CAMPAIGN"),
    (47, "NATO BOOSTS AIR WATCH ON EASTERN FLANK"),
    (48, "ETHIOPIA PUSHES HEALTHCARE INDEPENDENCE"),
    (49, "EGYPT: SUEZ CANAL REVENUES RECOVERING"),
]

DOTS = [
    (1, 116, 39), (2, -120, 45), (3, -88, 33), (4, 65, 28), (5, 45, 18),
    (6, 25, 55), (7, 110, 30), (8, -70, 42), (9, 28, -26), (10, -80, 18),
    (11, -105, 35), (12, 0, 40), (13, -95, 28), (14, 140, 45), (15, 160, -9),
]

FOOTER1 = "DATE CHECK: ALL STORIES FIRST REPORTED THURSDAY 26 NOVEMBER 2026"
FOOTER2 = "SOURCES: AP, REUTERS, WSJ, JUST SECURITY, QATAR TRIBUNE, MANILA TIMES - 26 NOV 2026"

def draw_icon(c, kind, x, y, w, h):
    cx = x + w // 2
    cy = y + h // 2
    if kind == "tanker":
        c.rect(x, y + h - 12, w, 12, BLUE)
        c.rect(x + 30, y + 12, w - 70, 14, INK)
        c.rect(x + 44, y + 2, 16, 10, RED)
        c.tri(x + 60, y + 2, 7, 10, ORANGE)
        c.tri(x + 78, y + 6, 5, 8, GOLD)
    elif kind == "refinery":
        c.rect(x + 10, y + 12, 14, h - 12, GREY)
        c.rect(x + 30, y + 6, 14, h - 6, INK)
        c.rect(x + 50, y + 16, 16, h - 16, GREY)
        c.tri(x + 37, y, 6, 10, ORANGE)
        c.rect(x, y + h - 4, w, 4, RED)
    elif kind == "drone":
        c.line(x + 8, y + 8, x + w - 8, y + h - 8, INK)
        c.line(x + w - 8, y + 8, x + 8, y + h - 8, INK)
        c.disc(cx, cy, 7, RED)
        c.disc(cx, cy, 3, WHITE)
    elif kind == "court":
        c.tri(cx, y + 2, 30, 10, NAVY)
        c.rect(x + 6, y + 14, 8, h - 18, NAVY)
        c.rect(cx - 4, y + 14, 8, h - 18, NAVY)
        c.rect(x + w - 14, y + 14, 8, h - 18, NAVY)
        c.rect(x, y + h - 4, w, 4, NAVY)
    elif kind == "market":
        c.rect(x + 8, y + 12, w - 16, h - 12, BLUE)
        for i in range(5):
            col = RED if i % 2 == 0 else WHITE
            c.rect(x + 8 + i * (w - 16) // 5, y + 4, (w - 16) // 5, 8, col)
        c.rect(x + 22, y + 20, 20, 10, WHITE)
    elif kind == "treaty":
        c.rect(x + 30, y + 6, 52, 24, BLUE)
        c.rect(x + 90, y + 6, 52, 24, GREEN)
        c.rect(x + 36, y + 12, 40, 2, WHITE)
        c.rect(x + 96, y + 12, 40, 2, WHITE)
        c.rect(x + 36, y + 18, 28, 2, WHITE)
        c.rect(x + 96, y + 18, 28, 2, WHITE)
        c.disc(cx, y + h - 8, 9, RED)
        c.line(cx - 4, y + h - 8, cx - 1, y + h - 4, WHITE)
        c.line(cx - 1, y + h - 4, cx + 5, y + h - 12, WHITE)
    elif kind == "strike":
        for dx, dy in ((-14, -8), (0, -12), (14, -8), (-16, 6), (16, 6)):
            c.line(cx, cy, cx + dx, cy + dy, ORANGE)
        c.disc(cx, cy, 8, RED)
        c.disc(cx, cy, 4, GOLD)
    elif kind == "shirt":
        c.rect(cx - 22, y + 10, 44, h - 10, GREEN)
        c.rect(x + 8, y + 10, 22, 12, GREEN)
        c.rect(x + w - 30, y + 10, 22, 12, GREEN)
        c.rect(x + 28, y + 10, 4, 12, PAPER)
        c.rect(x + w - 32, y + 10, 4, 12, PAPER)
        c.tri(cx, y + 10, 7, 8, WHITE)
    elif kind == "mine":
        c.tri(cx, y + 2, 30, h - 2, (120, 90, 60))
        c.rect(cx - 8, y + h - 14, 16, 14, INK)
        c.disc(cx, y + 8, 4, GOLD)
    elif kind == "cpi":
        for i, bh in enumerate((10, 18, 14, 24)):
            c.rect(x + 10 + i * 16, y + h - 4 - bh, 10, bh, GREEN)
    elif kind == "jet":
        c.tri(cx, y + 6, 10, 20, NAVY)
        c.rect(cx - 22, y + 18, 44, 6, NAVY)
        c.rect(cx - 4, y + 26, 8, 12, NAVY)
        c.rect(x + 8, y + h - 8, w - 16, 4, RED)
    elif kind == "plane":
        c.rect(x + 10, y + 10, w - 20, 10, BLUE)
        c.tri(x + w - 10, y + 10, 8, 10, BLUE)
        c.rect(cx - 4, y + 20, 8, 14, BLUE)
    else:
        c.rect(x, y, w, h, GREY)

ICON_KIND = {4: "tanker", 5: "refinery", 6: "jet", 7: "jet",
             8: "court", 9: "court", 10: "treaty", 11: "plane",
             12: "strike", 13: "court", 14: "treaty", 15: "treaty"}

def draw_rocket(c, x, y, w, h):
    c.rect(x, y, w, h, SKY)
    for sx, sy in ((12, 10), (40, 26), (w - 20, 14), (w - 50, 34), (24, 48), (w - 30, 52)):
        c.rect(x + sx, y + sy, 2, 2, WHITE)
    cx = x + w // 2
    c.tri(cx, y + 12, 8, 14, RED)
    c.rect(cx - 8, y + 26, 16, 42, WHITE)
    c.rect(cx - 8, y + 40, 16, 4, BLUE)
    c.rect(cx - 16, y + 52, 8, 16, RED)
    c.rect(cx + 8, y + 52, 8, 16, RED)
    c.tri(cx, y + 68, 7, 16, ORANGE)
    c.tri(cx, y + 72, 4, 12, GOLD)
    c.disc(x + 26, y + 26, 9, (220, 220, 200))
    c.rect(x + w - 52, y + h - 16, 40, 4, GREY)

def draw_chart(c, x, y, w, h):
    c.rect(x, y, w, h, WHITE)
    for gy in range(4):
        yy = y + 12 + gy * 22
        c.rect(x + 8, yy, w - 16, 1, RULE)
    pts = [(x + 12, y + 30), (x + 60, y + 38), (x + 110, y + 36),
           (x + 160, y + 54), (x + 210, y + 66), (x + w - 14, y + 90)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        c.thick_line(ax, ay, bx, by, 3, RED)
    for px, py in pts:
        c.disc(px, py, 3, RED)
    c.text(x + 10, y + 4, "-3%", 3, RED)
    c.text(x + w - 110, y + h - 16, "NASDAQ FUTURES", 1, INK)

def draw_bars(c, x, y, w, h):
    c.rect(x, y, w, h, WHITE)
    data = [("CHINA", 20, NAVY), ("EU", 15, BLUE), ("INDIA", 25, RED), ("VIETNAM", 35, ORANGE)]
    bw = 52
    gap = (w - 4 * bw) // 5
    for i, (label, val, col) in enumerate(data):
        bx = x + gap + i * (bw + gap)
        bh = val * 2
        c.rect(bx, y + h - 22 - bh, bw, bh, col)
        c.text(bx + (bw - c.text_width(str(val) + "%", 1)) // 2, y + h - 18 - bh, str(val) + "%", 1, WHITE)
        c.text(bx + (bw - c.text_width(label, 1)) // 2, y + h - 16, label, 1, INK)
    c.rect(x + 8, y + h - 22, w - 16, 2, INK)

def render():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    c.centred(12, "THURSDAY 26 NOVEMBER 2026", 3, INK)
    c.centred(48, "49 STORIES - 7 REGIONS - ONE DAY", 2, RED)
    c.rect(20, 70, WIDTH - 40, 4, RED)
    c.centred(82, "ASIA 12  MIDDLE EAST 4  EUROPE 7  AFRICA 3  AMERICAS 18  OCEANIA 1  GLOBAL 4", 1, INK)
    c.rect(20, 100, WIDTH - 40, 30, NAVY)
    c.centred(108, "-3% NASDAQ  -  1ST ASTRONAUT  -  14 ECONOMIES  -  2,000 MIGRANTS  -  +36% WAGE", 2, WHITE)
    c.centred(140, "THANKSGIVING IN THE US  -  MARKETS CLOSED  -  TIANGONG CREW IN ORBIT  -  HORMUZ SHIPS HIT  -  NATO JETS SCRAMBLE", 1, GREY)
    hx = [20, 352, 684]
    hw = 320
    hy = 158
    draw_rocket(c, hx[0], hy, hw, 104)
    c.text(hx[0], hy + 112, "1. SHENZHOU-24 CREW", 2, INK)
    c.text(hx[0], hy + 134, "ABOARD TIANGONG", 2, INK)
    c.text(hx[0], hy + 156, "PAKISTAN'S FIRST ASTRONAUT, ZEESHAN ALI, IN ORBIT", 1, GREY)
    draw_chart(c, hx[1], hy, hw, 104)
    c.text(hx[1], hy + 112, "2. THANKSGIVING DAY,", 2, INK)
    c.text(hx[1], hy + 134, "AI SELLOFF RESUMES", 2, INK)
    c.text(hx[1], hy + 156, "US MARKETS CLOSED - NASDAQ FUTURES -3%", 1, GREY)
    draw_bars(c, hx[2], hy, hw, 104)
    c.text(hx[2], hy + 112, "3. US TO UNVEIL TARIFF", 2, INK)
    c.text(hx[2], hy + 134, "PROBE ON 14 ECONOMIES", 2, INK)
    c.text(hx[2], hy + 156, "CHINA 20% - EU 15% - INDIA 25% - VIETNAM 35%", 1, GREY)
    # Middle cards 4-15: 6 cols x 2 rows
    mw, mh = 160, 118
    for i, (num, region, text) in enumerate(MID):
        col, row = i % 6, i // 6
        x = 20 + col * (mw + 8)
        y = 336 + row * (mh + 10)
        c.rect(x, y, mw, mh, CARD)
        c.rect(x, y, mw, 2, REGION_COL[region])
        c.rect(x, y + 6, 24, 20, NAVY)
        c.text(x + (24 - c.text_width(str(num), 2)) // 2, y + 10, str(num), 2, WHITE)
        c.text(x + mw - 4 - c.text_width(region, 1), y + 10, region, 1, REGION_COL[region])
        draw_icon(c, ICON_KIND[num], x + 8, y + 32, mw - 16, 34)
        lines = wrap(text, 24)[:3]
        ly = y + 72
        for line in lines:
            c.text(x + 6, ly, line, 1, INK)
            ly += 10
    # Bottom: map (left) + list 16-49 (right, 2 cols)
    by = 592
    c.rect(20, by, 300, 340, CARD)
    c.rect(20, by, 300, 2, NAVY)
    c.text(32, by + 10, "WHERE IT HAPPENED", 2, NAVY)
    mx, my, mw2, mh2 = 32, by + 34, 276, 260
    c.rect(mx, my, mw2, mh2, (232, 238, 244))
    c.rect(mx + 28, my + 40, 66, 56, (190, 200, 190))
    c.rect(mx + 104, my + 30, 56, 66, (190, 200, 190))
    c.rect(mx + 170, my + 50, 76, 56, (190, 200, 190))
    c.rect(mx + 190, my + 130, 48, 38, (190, 200, 190))
    c.rect(mx + 38, my + 130, 38, 48, (190, 200, 190))
    for num, lon, lat in DOTS:
        dx = mx + int((lon + 180) / 360.0 * mw2)
        dy = my + int((90 - lat) / 180.0 * mh2)
        c.rect(dx - 7, dy - 7, 14, 14, RED)
        c.text(dx - c.text_width(str(num), 1) // 2, dy - 4, str(num), 1, WHITE)
    c.text(32, by + 306, "DOTS 1-15 MARK THE TOP STORIES", 1, GREY)
    list_cols = [LIST[:17], LIST[17:]]
    list_x = [336, 688]
    for col_idx, items in enumerate(list_cols):
        x = list_x[col_idx]
        ly = by + 6
        for num, text in items:
            lines = wrap(str(num) + ". " + text, 48)[:2]
            for line in lines:
                c.text(x, ly, line, 1, INK)
                ly += 11
            ly += 4
    c.rect(20, 956, WIDTH - 40, 2, RULE)
    c.text(20, 970, FOOTER1, 1, RED)
    c.text(20, 988, FOOTER2, 1, GREY)
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
