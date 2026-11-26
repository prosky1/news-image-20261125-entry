#!/usr/bin/env python3
"""Draw Wednesday 25 November 2026 world news as one broadsheet page (1024x1024)."""
import os
import random
import shutil
import textwrap

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # harness container is stdlib-only; main() falls back to the bundled PNG
    Image = ImageDraw = ImageFont = None

W = H = 1024
CREAM = (250, 246, 236)
INK = (28, 26, 22)
NAVY = (16, 32, 62)
RED = (178, 34, 34)
GREY = (110, 104, 92)
RULE = (60, 56, 48)
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

REGION_COLORS = {
    "GLOBAL": (70, 70, 120),
    "N. AMERICA": (36, 92, 160),
    "LATIN AM.": (200, 120, 30),
    "EUROPE": (30, 120, 90),
    "MIDDLE EAST": (180, 60, 50),
    "EAST ASIA": (150, 40, 110),
    "S & SE ASIA": (20, 140, 140),
    "AFRICA": (140, 90, 20),
    "OCEANIA": (60, 140, 60),
}

BADGE_COLORS = {
    "OFFICIAL": (20, 110, 60),
    "REPORTED": (36, 92, 160),
    "CLAIM": (178, 34, 34),
    "PREVIEW": (120, 80, 160),
}


def font(size, bold=False):
    return ImageFont.truetype(SERIF_B if bold else SERIF, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, fnt, max_w, fill=INK, leading=None, max_lines=None):
    x, y = xy
    if leading is None:
        leading = fnt.size + 2
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def badge(draw, x, y, label):
    f = font(7, True)
    tw = draw.textlength(label, font=f)
    draw.rounded_rectangle([x, y, x + tw + 8, y + 11], 3, fill=BADGE_COLORS[label])
    draw.text((x + 4, y + 1), label, font=f, fill=WHITE)
    return x + tw + 8


def num_chip(draw, x, y, n, region):
    c = REGION_COLORS[region]
    draw.ellipse([x, y, x + 16, y + 16], fill=c)
    f = font(9, True)
    s = str(n)
    tw = draw.textlength(s, font=f)
    draw.text((x + 8 - tw / 2, y + 2), s, font=f, fill=WHITE)


# ---------------- illustrations ----------------

def sky(draw, box, top=(120, 170, 220), bottom=(210, 230, 245)):
    x0, y0, x1, y1 = box
    steps = 24
    for i in range(steps):
        t = i / steps
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        yy = y0 + (y1 - y0) * i // steps
        draw.rectangle([x0, yy, x1, yy + (y1 - y0) // steps + 1], fill=c)


def ill_ship(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box)
    sea_y = y0 + (y1 - y0) * 2 // 3
    draw.rectangle([x0, sea_y, x1, y1], fill=(30, 90, 150))
    for i in range(6):
        yy = sea_y + 4 + i * 6
        draw.line([x0 + 4 + (i % 2) * 14, yy, x0 + 40 + (i % 2) * 14, yy], fill=(120, 180, 225), width=2)
        draw.line([x1 - 60 - (i % 2) * 10, yy, x1 - 24 - (i % 2) * 10, yy], fill=(120, 180, 225), width=2)
    hx0, hx1 = x0 + 14, x1 - 14
    hy = sea_y - 6
    draw.polygon([(hx0, hy), (hx1, hy), (hx1 - 16, hy + 18), (hx0 + 12, hy + 18)], fill=(40, 40, 48))
    cols = [(200, 60, 50), (40, 120, 200), (240, 170, 40), (60, 160, 90), (150, 60, 150), (230, 110, 40)]
    cw = (hx1 - hx0 - 24) // 6
    for r in range(3):
        for c in range(6):
            cx = hx0 + 8 + c * cw
            cy = hy - 14 - r * 13
            draw.rectangle([cx, cy, cx + cw - 3, cy + 11], fill=cols[(r * 6 + c) % 6], outline=(30, 30, 30))
    draw.rectangle([hx1 - 40, hy - 34, hx1 - 18, hy - 6], fill=(235, 235, 230), outline=(30, 30, 30))
    draw.rectangle([hx1 - 36, hy - 30, hx1 - 22, hy - 24], fill=(60, 90, 130))
    draw.rectangle([x0 + 6, y0 + 5, x0 + 74, y0 + 17], fill=(178, 34, 34))
    draw.text((x0 + 10, y0 + 6), "CHINA 20%", font=font(8, True), fill=WHITE)
    draw.rectangle([x0 + 78, y0 + 5, x0 + 140, y0 + 17], fill=(36, 92, 160))
    draw.text((x0 + 82, y0 + 6), "EU · JP 15%", font=font(8, True), fill=WHITE)
    draw.rectangle([x0 + 144, y0 + 5, x0 + 216, y0 + 17], fill=(120, 80, 160))
    draw.text((x0 + 148, y0 + 6), "14 ECONOMIES", font=font(8, True), fill=WHITE)


def ill_chart(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(24, 26, 34))
    for i in range(1, 5):
        yy = y0 + (y1 - y0) * i // 5
        draw.line([x0 + 6, yy, x1 - 6, yy], fill=(70, 74, 90), width=1)
    pts = []
    vals = [0.86, 0.82, 0.85, 0.78, 0.80, 0.66, 0.60, 0.64, 0.48, 0.40, 0.44, 0.30, 0.34, 0.22]
    for i, v in enumerate(vals):
        px = x0 + 12 + i * (x1 - x0 - 24) // (len(vals) - 1)
        py = y1 - 12 - int(v * (y1 - y0 - 34))
        pts.append((px, py))
    draw.line(pts, fill=(240, 80, 70), width=3)
    for p in pts:
        draw.ellipse([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2], fill=(255, 200, 90))
    draw.text((x0 + 8, y0 + 5), "KOSPI CLOSE 4,697.51", font=font(10, True), fill=(255, 220, 120))
    draw.text((x1 - 98, y0 + 5), "KOSPI  -6.16%", font=font(8, True), fill=(240, 110, 100))
    draw.text((x1 - 98, y0 + 17), "NIKKEI -2.78%", font=font(8, True), fill=(240, 110, 100))
    draw.text((x1 - 98, y0 + 29), "NVIDIA -3.9%", font=font(8, True), fill=(240, 110, 100))
    draw.text((x1 - 98, y0 + 41), "NASDAQ -0.62%", font=font(8, True), fill=(240, 110, 100))


def ill_station(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(10, 18, 44))
    rng = random.Random(25)
    for _ in range(70):
        sx = rng.randint(x0 + 3, x1 - 3)
        sy = rng.randint(y0 + 3, y1 - 26)
        draw.point((sx, sy), fill=(230, 235, 255))
    draw.ellipse([x0 - 40, y1 - 26, x1 + 40, y1 + 70], fill=(36, 96, 180))
    draw.ellipse([x0 - 40, y1 - 26, x1 + 40, y1 + 70], outline=(140, 200, 255), width=2)
    cx, cy = x0 + (x1 - x0) * 3 // 5, y0 + (y1 - y0) // 3
    draw.rectangle([cx - 6, cy - 26, cx + 6, cy + 26], fill=(225, 228, 235), outline=(20, 20, 30))
    draw.rectangle([cx - 52, cy - 5, cx - 8, cy + 5], fill=(70, 110, 200), outline=(20, 20, 30))
    draw.rectangle([cx + 8, cy - 5, cx + 52, cy + 5], fill=(70, 110, 200), outline=(20, 20, 30))
    for i in range(4):
        draw.line([cx - 48 + i * 10, cy - 5, cx - 48 + i * 10, cy + 5], fill=(30, 50, 110))
        draw.line([cx + 12 + i * 10, cy - 5, cx + 12 + i * 10, cy + 5], fill=(30, 50, 110))
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(245, 245, 250), outline=(20, 20, 30))
    draw.rectangle([cx - 3, cy + 26, cx + 3, cy + 38], fill=(200, 205, 215), outline=(20, 20, 30))
    rx, ry = x0 + 46, y1 - 44
    draw.polygon([(rx, ry - 30), (rx + 7, ry - 14), (rx + 7, ry + 8), (rx - 7, ry + 8), (rx - 7, ry - 14)], fill=(235, 235, 240), outline=(20, 20, 30))
    draw.polygon([(rx - 7, ry + 2), (rx - 16, ry + 12), (rx - 7, ry + 12)], fill=(200, 60, 50))
    draw.polygon([(rx + 7, ry + 2), (rx + 16, ry + 12), (rx + 7, ry + 12)], fill=(200, 60, 50))
    draw.polygon([(rx - 4, ry + 9), (rx + 4, ry + 9), (rx, ry + 22)], fill=(250, 180, 60))
    draw.arc([rx + 8, ry - 30, cx - 4, cy + 30], 300, 80, fill=(255, 220, 120), width=1)
    draw.rectangle([x0 + 6, y0 + 5, x0 + 96, y0 + 18], fill=(178, 34, 34))
    draw.text((x0 + 10, y0 + 7), "00:18 UTC LIFTOFF", font=font(8, True), fill=WHITE)
    draw.text((cx + 14, cy - 24), "TIANGONG", font=font(8, True), fill=(200, 225, 255))


def ill_refinery(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box, top=(200, 170, 130), bottom=(240, 220, 180))
    gy = y1 - 16
    draw.rectangle([x0, gy, x1, y1], fill=(120, 100, 80))
    for i, tx in enumerate([x0 + 14, x0 + 52, x0 + 90]):
        draw.rectangle([tx, gy - 26, tx + 30, gy], fill=(210, 205, 195), outline=(60, 55, 45))
        draw.ellipse([tx, gy - 32, tx + 30, gy - 20], fill=(225, 220, 210), outline=(60, 55, 45))
    draw.rectangle([x1 - 52, gy - 44, x1 - 44, gy], fill=(160, 60, 50), outline=(60, 40, 35))
    draw.rectangle([x1 - 40, gy - 36, x1 - 33, gy], fill=(160, 60, 50), outline=(60, 40, 35))
    for cxp, cyp, r in [(x1 - 48, gy - 50, 6), (x1 - 44, gy - 58, 8)]:
        draw.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=(90, 85, 80))
    draw.polygon([(x0 + 128, gy - 8), (x1 - 62, gy - 8), (x1 - 70, gy), (x0 + 136, gy)], fill=(50, 50, 60))
    draw.rectangle([x0 + 150, gy - 16, x0 + 186, gy - 8], fill=(180, 70, 60))
    draw.polygon([(x0 + 160, gy - 30), (x0 + 168, gy - 18), (x0 + 176, gy - 30)], fill=(250, 140, 40))
    draw.polygon([(x0 + 164, gy - 36), (x0 + 170, gy - 24), (x0 + 174, gy - 32)], fill=(255, 210, 80))
    draw.rectangle([x0 + 6, y0 + 4, x0 + 120, y0 + 16], fill=(178, 34, 34))
    draw.text((x0 + 10, y0 + 5), "RAS TANURA · CLAIM", font=font(8, True), fill=WHITE)


def ill_wage(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box, top=(150, 200, 180), bottom=(225, 245, 235))
    gy = y1 - 12
    draw.rectangle([x0, gy, x1, y1], fill=(90, 130, 100))
    fx = x0 + 16
    draw.rectangle([fx, gy - 26, fx + 86, gy], fill=(200, 120, 60), outline=(80, 50, 30))
    draw.polygon([(fx - 4, gy - 26), (fx + 20, gy - 38), (fx + 44, gy - 26)], fill=(140, 80, 40))
    draw.polygon([(fx + 40, gy - 26), (fx + 64, gy - 38), (fx + 90, gy - 26)], fill=(140, 80, 40))
    for i in range(4):
        draw.rectangle([fx + 8 + i * 20, gy - 18, fx + 20 + i * 20, gy - 6], fill=(255, 240, 190), outline=(80, 50, 30))
    draw.rectangle([fx + 96, gy - 40, fx + 104, gy], fill=(120, 110, 100), outline=(70, 65, 55))
    draw.ellipse([fx + 94, gy - 52, fx + 110, gy - 38], fill=(170, 165, 155))
    ax = x1 - 44
    draw.line([ax, gy - 8, ax, gy - 34], fill=(20, 140, 70), width=5)
    draw.polygon([(ax - 9, gy - 32), (ax + 9, gy - 32), (ax, gy - 46)], fill=(20, 140, 70))
    draw.rectangle([x0 + 5, y0 + 3, x0 + 56, y0 + 23], fill=(255, 255, 255))
    draw.text((x0 + 8, y0 + 4), "+36%", font=font(16, True), fill=(20, 120, 60))


def ill_fire(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box, top=(240, 190, 130), bottom=(250, 230, 200))
    gy = y1 - 12
    draw.rectangle([x0, gy, x1, y1], fill=(70, 65, 60))
    draw.rectangle([x0 + 20, gy - 16, x0 + 120, gy - 2], fill=(180, 180, 185), outline=(50, 50, 55))
    draw.rectangle([x0 + 120, gy - 13, x0 + 142, gy - 2], fill=(90, 110, 150), outline=(50, 50, 55))
    draw.ellipse([x0 + 34, gy - 8, x0 + 48, gy + 4], fill=(30, 30, 32))
    draw.ellipse([x0 + 96, gy - 8, x0 + 110, gy + 4], fill=(30, 30, 32))
    for fx, fh in [(x0 + 44, 30), (x0 + 66, 40), (x0 + 88, 26)]:
        draw.polygon([(fx - 10, gy - 14), (fx, gy - 14 - fh), (fx + 10, gy - 14)], fill=(240, 110, 30))
        draw.polygon([(fx - 5, gy - 14), (fx, gy - 14 - fh + 12), (fx + 5, gy - 14)], fill=(255, 210, 80))
    for cxp, cyp, r in [(x0 + 70, gy - 58, 9), (x0 + 92, gy - 68, 11)]:
        draw.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=(70, 65, 60))
    draw.rectangle([x1 - 108, y0 + 4, x1 - 6, y0 + 17], fill=(178, 34, 34))
    draw.text((x1 - 102, y0 + 6), "AT LEAST 21 DEAD", font=font(8, True), fill=WHITE)


def ill_mine(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box, top=(140, 180, 200), bottom=(215, 235, 240))
    gy = y0 + 18
    draw.rectangle([x0, gy, x1, y1], fill=(100, 78, 55))
    draw.rectangle([x0, gy, x1, gy + 8], fill=(80, 140, 70))
    draw.polygon([(x0 + 60, y1 - 4), (x0 + 76, gy + 8), (x0 + 92, gy + 8), (x0 + 108, y1 - 4)], fill=(45, 35, 25))
    draw.rectangle([x0 + 70, y1 - 18, x0 + 98, y1 - 4], fill=(40, 90, 150))
    draw.rectangle([x0 + 62, gy + 2, x0 + 106, gy + 10], fill=(120, 90, 55), outline=(70, 50, 30))
    for i in range(3):
        draw.rectangle([x0 + 14 + i * 16, gy - 12, x0 + 24 + i * 16, gy + 2], fill=(230, 120, 40), outline=(90, 50, 20))
    draw.text((x0 + 118, gy + 10), "26 TRAPPED", font=font(9, True), fill=(255, 230, 160))
    draw.text((x0 + 118, gy + 23), "100 M DEEP", font=font(8, True), fill=(255, 230, 160))
    draw.rectangle([x0 + 4, y0 + 3, x0 + 104, y0 + 14], fill=(255, 255, 255))
    draw.text((x0 + 7, y0 + 4), "FLOODED GOLD MINE", font=font(8, True), fill=(30, 60, 90))


def ill_store(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box, top=(170, 200, 235), bottom=(235, 245, 252))
    gy = y1 - 10
    draw.rectangle([x0, gy, x1, y1], fill=(150, 145, 135))
    bx = x0 + 22
    draw.rectangle([bx, gy - 40, bx + 130, gy], fill=(235, 230, 215), outline=(90, 85, 70))
    draw.rectangle([bx, gy - 40, bx + 130, gy - 28], fill=(200, 40, 40))
    draw.text((bx + 8, gy - 37), "ÉXITO", font=font(10, True), fill=WHITE)
    for i in range(4):
        draw.rectangle([bx + 8 + i * 31, gy - 22, bx + 32 + i * 31, gy - 4], fill=(150, 190, 220), outline=(90, 85, 70))
    draw.rectangle([bx + 52, gy - 22, bx + 78, gy - 4], fill=(110, 160, 200), outline=(90, 85, 70))
    draw.line([bx + 65, gy - 22, bx + 65, gy - 4], fill=(90, 85, 70))
    draw.rectangle([x1 - 66, gy - 24, x1 - 16, gy - 8], fill=(60, 60, 70), outline=(30, 30, 35))
    draw.rectangle([x1 - 58, gy - 31, x1 - 28, gy - 24], fill=(60, 60, 70), outline=(30, 30, 35))
    draw.ellipse([x1 - 58, gy - 12, x1 - 46, gy], fill=(25, 25, 28))
    draw.ellipse([x1 - 32, gy - 12, x1 - 20, gy], fill=(25, 25, 28))
    draw.rectangle([x0 + 4, y0 + 3, x0 + 132, y0 + 14], fill=(255, 255, 255))
    draw.text((x0 + 7, y0 + 4), "~30 HOSTAGES FREED 01:00", font=font(8, True), fill=(30, 60, 110))


def ill_treaty(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box, top=(120, 190, 220), bottom=(220, 245, 250))
    gy = y1 - 14
    draw.rectangle([x0, gy, x1, y1], fill=(40, 130, 170))
    draw.ellipse([x0 + 10, gy - 6, x0 + 90, gy + 8], fill=(240, 220, 160))
    draw.ellipse([x1 - 90, gy - 6, x1 - 10, gy + 8], fill=(240, 220, 160))
    px = x0 + 30
    draw.line([px, gy - 2, px, gy - 40], fill=(80, 70, 55), width=3)
    draw.rectangle([px, gy - 40, px + 34, gy - 24], fill=(20, 40, 130))
    draw.ellipse([px + 12, gy - 36, px + 22, gy - 28], fill=(255, 255, 255))
    qx = x1 - 64
    draw.line([qx, gy - 2, qx, gy - 40], fill=(80, 70, 55), width=3)
    draw.rectangle([qx, gy - 40, qx + 34, gy - 24], fill=(30, 140, 70))
    draw.polygon([(qx, gy - 24), (qx + 34, gy - 40), (qx + 34, gy - 24)], fill=(250, 200, 60))
    draw.rectangle([x0 + 66, gy - 30, x1 - 66, gy - 14], fill=(255, 252, 240), outline=(90, 85, 70))
    draw.text((x0 + 72, gy - 27), "PACT SIGNED", font=font(8, True), fill=(60, 55, 45))
    draw.text((x0 + 72, y0 + 3), "AU$740M", font=font(8, True), fill=(20, 70, 110))


def ill_power(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box, top=(90, 100, 140), bottom=(190, 195, 210))
    gy = y1 - 12
    draw.rectangle([x0, gy, x1, y1], fill=(90, 95, 85))
    for tx in [x0 + 30, x0 + 110, x0 + 180]:
        draw.line([tx - 12, gy, tx, gy - 44], fill=(45, 45, 50), width=3)
        draw.line([tx + 12, gy, tx, gy - 44], fill=(45, 45, 50), width=3)
        draw.line([tx - 16, gy - 38, tx + 16, gy - 38], fill=(45, 45, 50), width=2)
        draw.line([tx - 12, gy - 30, tx + 12, gy - 30], fill=(45, 45, 50), width=2)
    draw.line([x0 + 14, gy - 38, x0 + 126, gy - 34], fill=(45, 45, 50), width=1)
    draw.line([x0 + 126, gy - 34, x0 + 196, gy - 38], fill=(45, 45, 50), width=1)
    draw.polygon([(x0 + 150, gy - 44), (x0 + 142, gy - 28), (x0 + 150, gy - 28), (x0 + 140, gy - 12), (x0 + 156, gy - 32), (x0 + 148, gy - 32)], fill=(255, 200, 60))
    draw.rectangle([x0 + 6, y0 + 4, x0 + 118, y0 + 17], fill=(178, 34, 34))
    draw.text((x0 + 10, y0 + 6), "POWER CUT · 5 REGIONS", font=font(8, True), fill=WHITE)
    draw.rectangle([x1 - 88, gy - 21, x1 - 8, gy - 10], fill=(255, 255, 255))
    draw.text((x1 - 84, gy - 20), "ODESA 2 DEAD", font=font(7, True), fill=(40, 40, 45))


def ill_bars(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(245, 242, 232))
    # slate only: Q3 GDP 2nd estimate 4.3% (was 3.4%); PCE 3.8%, core PCE 3.3%
    draw.text((x0 + 8, y0 + 3), "US Q3 GDP — REVISED UP", font=font(8, True), fill=(40, 40, 45))
    base = y1 - 14
    scale = 4.2  # px per percentage point; value above bar, WAS/NOW below baseline
    bars = [(x0 + 16, 3.4, (120, 130, 145), "3.4%", "WAS"), (x0 + 60, 4.3, (20, 140, 70), "4.3%", "NOW")]
    for bx, v, col, val, tag in bars:
        bh = int(v * scale)
        draw.rectangle([bx, base - bh, bx + 30, base], fill=col, outline=(60, 55, 45))
        tw = draw.textlength(val, font=font(8, True))
        draw.text((bx + 15 - tw / 2, base - bh - 10), val, font=font(8, True), fill=(40, 40, 45))
        tw2 = draw.textlength(tag, font=font(7, True))
        draw.text((bx + 15 - tw2 / 2, base + 2), tag, font=font(7, True), fill=(90, 84, 70))
    draw.line([x0 + 8, base, x0 + 100, base], fill=(60, 55, 45), width=2)
    draw.text((x0 + 108, y0 + 18), "PCE 3.8%", font=font(9, True), fill=(178, 34, 34))
    draw.text((x0 + 108, y0 + 31), "CORE 3.3%", font=font(8, True), fill=(178, 34, 34))


def ill_parliament(draw, box):
    x0, y0, x1, y1 = box
    sky(draw, box, top=(160, 190, 225), bottom=(235, 242, 250))
    gy = y1 - 10
    draw.rectangle([x0, gy, x1, y1], fill=(140, 135, 125))
    bx = x0 + 30
    draw.rectangle([bx, gy - 34, bx + 120, gy], fill=(225, 220, 205), outline=(90, 85, 70))
    draw.polygon([(bx - 4, gy - 34), (bx + 60, gy - 50), (bx + 124, gy - 34)], fill=(110, 105, 95))
    for i in range(5):
        cx = bx + 12 + i * 24
        draw.rectangle([cx, gy - 30, cx + 8, gy - 4], fill=(240, 236, 224), outline=(90, 85, 70))
    draw.rectangle([bx + 52, gy - 58, bx + 68, gy - 48], fill=(200, 200, 205), outline=(90, 85, 70))
    draw.text((x0 + 6, y0 + 3), "BERLIN · BUNDESTAG", font=font(8, True), fill=(30, 60, 110))
    draw.text((x1 - 118, gy - 22), "€11.6BN FOR KYIV", font=font(8, True), fill=(40, 40, 45))


def ill_meeting(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(240, 232, 215))
    draw.rectangle([x0, y1 - 16, x1, y1], fill=(120, 90, 60))
    tx = x0 + 40
    draw.rectangle([tx, y1 - 30, tx + 120, y1 - 16], fill=(150, 110, 70), outline=(90, 65, 40))
    for px, col in [(tx + 18, (40, 60, 120)), (tx + 84, (120, 40, 40))]:
        draw.ellipse([px, y1 - 52, px + 18, y1 - 34], fill=(235, 195, 160), outline=(90, 65, 40))
        draw.rectangle([px - 2, y1 - 36, px + 20, y1 - 22], fill=col, outline=(50, 45, 40))
    draw.rectangle([x0 + 8, y0 + 6, x0 + 42, y0 + 28], fill=(20, 40, 130))
    draw.rectangle([x0 + 8, y0 + 6, x0 + 42, y0 + 12], fill=(200, 40, 40))
    draw.rectangle([x1 - 42, y0 + 6, x1 - 8, y0 + 28], fill=(20, 40, 130))
    draw.ellipse([x1 - 32, y0 + 10, x1 - 18, y0 + 24], outline=(255, 255, 255), width=2)
    draw.text((x0 + 52, y0 + 8), "19:00 ET", font=font(8, True), fill=(60, 50, 35))


ILLUSTRATIONS = {
    "ship": ill_ship, "chart": ill_chart, "station": ill_station,
    "refinery": ill_refinery, "wage": ill_wage, "fire": ill_fire,
    "mine": ill_mine, "store": ill_store, "treaty": ill_treaty,
    "power": ill_power, "bars": ill_bars, "parliament": ill_parliament,
    "meeting": ill_meeting,
}


# ---------------- story data (slate of Wednesday 25 Nov 2026) ----------------
# display number -> (region, kicker, headline, body, why, badge, source, illustration)
FEATURES = [
    (1, "GLOBAL", "WASHINGTON · TRADE", "Washington proposes tariffs on 14 economies",
     "The USTR proposed new Section 301 duties on 14 partners: China highest at 20%, "
     "caps of 15% for the EU, Japan, South Korea, Taiwan and Switzerland.",
     "WHY IT MATTERS — Nothing is in force yet; hearings open 25 January.",
     "OFFICIAL", "REUTERS", "ship"),
    (2, "GLOBAL", "SEOUL · TOKYO · NEW YORK · MARKETS", "AI shakeout rattles world markets",
     "Nvidia fell 3.9% to $149.30 as the AI trade unwound; the KOSPI fell 6.16%, "
     "Europe closed lower and Wall Street finished mixed (Dow +0.33%, Nasdaq -0.62%) "
     "after a 1,100-point intraday swing.",
     "WHY IT MATTERS — The week's AI rally is being repriced worldwide.",
     "REPORTED", "REUTERS · AP", "chart"),
    (3, "EAST ASIA", "JIUQUAN, CHINA · SPACE", "Shenzhou-24 flies a Pakistani to Tiangong",
     "Muhammad Zeeshan Ali, 40, is the first Pakistani in orbit and first foreigner "
     "aboard Tiangong; Shenzhou-24 lifted off 00:18 UTC and docked 11:56 Beijing.",
     "WHY IT MATTERS — China's station takes its first foreign guest.",
     "OFFICIAL", "REUTERS · XINHUA", "station"),
]

MEDIUMS = [
    (4, "MIDDLE EAST", "HORMUZ · ENERGY", "Gulf energy alarm: mine and drone claims",
     "Iran claims two tankers mined; Houthis claim a Ras Tanura hit. Brent $94.61, +3.5%.",
     "CLAIM", "REUTERS", "refinery"),
    (5, "S & SE ASIA", "DHAKA · LABOUR", "Garment workers win a 36% pay rise",
     "Wage board lifts the minimum to 17,000 taka (~$138) from 1 December.",
     "OFFICIAL", "REUTERS", "wage"),
    (6, "AFRICA", "GIZA, EGYPT · DISASTER", "Fuel truck blaze kills at least 21",
     "A fuel vehicle overturned on the Cairo/Giza ring road; 15 wounded.",
     "REPORTED", "REUTERS", "fire"),
    (7, "S & SE ASIA", "BOGOR, INDONESIA", "Rescuers pull bodies from flooded mine",
     "26 miners trapped 100 m down at Pongkor since Monday; bodies recovered Wed.",
     "REPORTED", "REUTERS", "mine"),
    (8, "LATIN AM.", "CARTAGENA, COLOMBIA", "Cartagena hostages freed after siege",
     "~30 freed at the Éxito store at 01:00; one gunman killed, four detained.",
     "REPORTED", "REUTERS · AP", "store"),
    (9, "OCEANIA", "CANBERRA · DIPLOMACY", "Australia signs security treaty with Solomons",
     "Australia becomes principal security partner; AU$740m over 10 years, no foreign bases.",
     "OFFICIAL", "PM.GOV.AU", "treaty"),
    (10, "EUROPE", "UKRAINE · ENERGY", "Russian strikes cut power in five regions",
     "Energy and gas sites hit; in Odesa two people were killed, three wounded.",
     "REPORTED", "REUTERS", "power"),
    (11, "GLOBAL", "WASHINGTON · ECONOMY", "US growth revised up; inflation sticky",
     "Q3 GDP 4.3% annualised (was 3.4%); October PCE 3.8%, core 3.3%.",
     "OFFICIAL", "BEA VIA REUTERS", "bars"),
    (12, "EUROPE", "BERLIN · DEFENCE", "Merz: “Russia wants more than Ukraine”",
     "Chancellor defends ~€11.6bn Ukraine aid in the 2027 draft budget.",
     "OFFICIAL", "REUTERS", "parliament"),
    (13, "N. AMERICA", "MAR-A-LAGO · DIPLOMACY", "Trump hosts NATO's Rutte at Mar-a-Lago",
     "Evening meeting and dinner on the Ukraine and Iran wars, per joint statement.",
     "OFFICIAL", "NATO STATEMENT", "meeting"),
]

# display number -> (region, text with source, badge letter)
BRIEFS = [
    (14, "GLOBAL", "GOLD & BITCOIN: gold dipped near $3,429, closed ~$3,590; Bitcoin fell to ~$57,200, closed ~$60,372. Pipback · Finnhub", "R"),
    (15, "N. AMERICA", "MICROSOFT AI: chief Mustafa Suleyman warns newest models are “powerful” enough that safety cannot be assumed. Suleyman post, 25 Nov", "R"),
    (16, "EUROPE", "UKRAINE: 112 drones overnight 24–25 Nov, 88 downed or jammed; a man killed near Kyiv. Ukrainian Air Force via Ukrinform", "R"),
    (17, "EUROPE", "KYIV: ballistic missiles hit a mall late Wed; 7 wounded, 2 seriously. Reuters (Klitschko)", "R"),
    (18, "EUROPE", "SAMARA: Ukrainian drones set two Rosneft refineries ablaze overnight; 1 dead. Reuters, 25 Nov", "R"),
    (19, "EUROPE", "SAVASLEYKA: Kyiv claims 3 MiG-31 + 2 Su-34 damaged at air base — unverified. Reuters", "C"),
    (20, "EUROPE", "KYIV CLAIMS 2,091 Russian troops lost in a day amid 203 clashes — unverified. Ukrainian General Staff via Kyiv24", "C"),
    (21, "EUROPE", "LASER CLAIM: Ukraine says its 4 kW “Blysk” laser downed a jet drone; video released Wed. Defence24 · Forbes", "C"),
    (22, "EUROPE", "POLAND proposes a border no-fly zone after drone and missile incidents. Reuters, 25 Nov", "O"),
    (23, "EUROPE", "EUROPEAN SHARES CLOSE LOWER: STOXX 600 −1.06%, DAX −1.26%, CAC −0.75%, FTSE −0.38%. Morningstar/Dow Jones", "R"),
    (24, "EUROPE", "SPAIN PREVIEW: snap poll Sunday 29 Nov; final polls PP ~31%, PSOE ~29–30%, Vox ~18%. Reuters explainer", "R"),
    (25, "MIDDLE EAST", "GAZA: Israeli strike kills Hamas security chief Col. Abuelouf, his wife and two daughters. Reuters, 25 Nov", "R"),
    (26, "MIDDLE EAST", "ISRAEL: Eisenkot forges anti-Netanyahu coalition pact (agreed Tue, reported Wed). Al Jazeera", "R"),
    (27, "MIDDLE EAST", "RAS TANURA: Houthis claim a hit on Saudi Arabia's largest refinery; coalition says 4 drones intercepted. Reuters · OilPrice", "C"),
    (28, "MIDDLE EAST", "HORMUZ: Iran's IRGC claims two tankers struck mines and burned — Reuters could not verify. Reuters/Fars", "C"),
    (29, "MIDDLE EAST", "HODEIDAH: Saudi-led strikes hit the port early Wed; Houthis threaten Jeddah. Reuters/Al Jazeera", "R"),
    (30, "MIDDLE EAST", "IRAQ: top court backs federal troops at Kurdistan borders. Reuters, 25 Nov", "O"),
    (31, "MIDDLE EAST", "SYRIA: Islamic State attack in Hasaka kills 2 security personnel, wounds 5. Reuters (state media)", "R"),
    (32, "GLOBAL", "F1 PREVIEW: Lusail Sunday 29 Nov, title settled — Antonelli 402 pts; Verstappen chases a 4th straight win. F1 previews", "R"),
    (33, "EAST ASIA", "SHANGHAI: party leadership rallies a day after chief Chen Jining was put under probe. Reuters, 25 Nov", "R"),
    (34, "EAST ASIA", "ASIA SLIDES; INDIA BUCKS IT: Nikkei −2.78%, Taiex −4.8%, Shanghai −2.03%; Nifty +1.85%. Barchart/AP", "R"),
    (35, "S & SE ASIA", "INDIA: foreign ministry says activist Saurav Das was told not to use his passport. Reuters, 25 Nov", "O"),
    (36, "AFRICA", "SUDAN: UAE condemns Khartoum drone strike (strike Sun 22 Nov, 4 dead; statement Wed). WAM, 25 Nov", "O"),
]

STATS = [
    ("20%", "top proposed US tariff — on China"),
    ("−6.16%", "KOSPI close — worst of the AI rout"),
    ("00:18", "UTC — Shenzhou-24 lifts off"),
    ("$94.61", "Brent settle, +3.5% on the day"),
    ("+36%", "Dhaka garment workers' pay rise"),
    ("4.3%", "US Q3 GDP growth, revised up"),
    ("112", "drones over Ukraine overnight"),
    ("AU$740m", "Solomons treaty, 10 years"),
]

REGION_BAR = [
    ("GLOBAL", 5), ("N. AMERICA", 2), ("LATIN AM.", 1), ("EUROPE", 11),
    ("MIDDLE EAST", 8), ("EAST ASIA", 3), ("S & SE ASIA", 3), ("AFRICA", 2), ("OCEANIA", 1),
]

# map pin positions on a simple world sketch (x, y in 0..1 of map box)
# 1 Washington trade · 2 Seoul markets · 3 Jiuquan · 4 Hormuz · 5 Dhaka ·
# 6 Giza · 7 Bogor (Java) · 8 Cartagena · 9 Canberra · 10 Ukraine ·
# 11 Washington economy · 12 Berlin · 13 Mar-a-Lago (Florida)
PINS = {
    1: (0.235, 0.30), 2: (0.845, 0.30), 3: (0.775, 0.34), 4: (0.605, 0.40),
    5: (0.695, 0.48), 6: (0.545, 0.44), 7: (0.775, 0.66), 8: (0.26, 0.56),
    9: (0.885, 0.76), 10: (0.555, 0.30), 11: (0.19, 0.38), 12: (0.485, 0.20),
    13: (0.245, 0.44),
}
PIN_REGION = {1: "GLOBAL", 2: "GLOBAL", 3: "EAST ASIA", 4: "MIDDLE EAST",
              5: "S & SE ASIA", 6: "AFRICA", 7: "S & SE ASIA", 8: "LATIN AM.",
              9: "OCEANIA", 10: "EUROPE", 11: "GLOBAL", 12: "EUROPE", 13: "N. AMERICA"}


# ---------------- page layout ----------------

def draw_map(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(214, 230, 240), outline=RULE, width=1)
    land = (196, 210, 178)
    # simplified but recognisable continents (relative coords):
    # N America (Alaska-Canada-US-Mexico, Florida bump), S America, Europe (+UK),
    # Africa, Asia (Siberia-China), Arabia, India triangle, SE Asia + Java, Australia
    conts = [
        [(0.02, 0.30), (0.04, 0.18), (0.07, 0.12), (0.13, 0.08), (0.20, 0.07), (0.26, 0.09), (0.30, 0.14), (0.31, 0.22), (0.29, 0.28), (0.265, 0.33), (0.26, 0.40), (0.255, 0.47), (0.235, 0.44), (0.21, 0.40), (0.18, 0.44), (0.165, 0.50), (0.14, 0.44), (0.09, 0.38), (0.03, 0.35)],
        [(0.21, 0.52), (0.27, 0.50), (0.32, 0.54), (0.34, 0.62), (0.31, 0.74), (0.27, 0.88), (0.24, 0.84), (0.22, 0.68), (0.20, 0.58)],
        [(0.44, 0.20), (0.46, 0.12), (0.51, 0.09), (0.57, 0.12), (0.60, 0.20), (0.59, 0.28), (0.54, 0.33), (0.47, 0.30), (0.44, 0.26)],
        [(0.435, 0.16), (0.45, 0.14), (0.455, 0.20), (0.44, 0.21)],
        [(0.45, 0.40), (0.52, 0.36), (0.58, 0.38), (0.61, 0.46), (0.59, 0.62), (0.55, 0.78), (0.51, 0.82), (0.47, 0.66), (0.44, 0.50)],
        [(0.59, 0.14), (0.70, 0.08), (0.82, 0.09), (0.90, 0.14), (0.93, 0.24), (0.89, 0.34), (0.82, 0.40), (0.76, 0.42), (0.70, 0.38), (0.64, 0.32), (0.59, 0.24)],
        [(0.58, 0.32), (0.64, 0.34), (0.65, 0.44), (0.60, 0.48), (0.57, 0.40)],
        [(0.66, 0.38), (0.72, 0.40), (0.70, 0.52), (0.67, 0.56), (0.64, 0.46)],
        [(0.74, 0.42), (0.78, 0.44), (0.77, 0.56), (0.74, 0.58), (0.72, 0.48)],
        [(0.72, 0.60), (0.82, 0.58), (0.84, 0.66), (0.78, 0.72), (0.72, 0.68)],
        [(0.81, 0.64), (0.89, 0.62), (0.94, 0.68), (0.92, 0.78), (0.84, 0.80), (0.80, 0.72)],
    ]
    mw, mh = x1 - x0, y1 - y0
    for c in conts:
        pts = [(x0 + px * mw, y0 + py * mh) for px, py in c]
        draw.polygon(pts, fill=land, outline=(150, 165, 140))
    for n, (px, py) in PINS.items():
        cx, cy = x0 + px * mw, y0 + py * mh
        col = REGION_COLORS[PIN_REGION[n]]
        r = 10
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=WHITE, width=1)
        f = font(8, True)
        s = str(n)
        tw = draw.textlength(s, font=f)
        draw.text((cx - tw / 2, cy - 5), s, font=f, fill=WHITE)


def card_frame(draw, box):
    draw.rectangle(box, fill=(255, 253, 247), outline=RULE, width=1)


def draw_ill(img, name, box):
    """Render an illustration clipped to its box so nothing spills over text."""
    x0, y0, x1, y1 = box
    layer = Image.new("RGB", (x1 - x0, y1 - y0), CREAM)
    ILLUSTRATIONS[name](ImageDraw.Draw(layer), (0, 0, x1 - x0, y1 - y0))
    img.paste(layer, (x0, y0))


def feature_card(img, draw, box, story):
    n, region, kicker, head, body, why, bdg, src, ill = story
    x0, y0, x1, y1 = box
    card_frame(draw, box)
    ih = 104
    draw_ill(img, ill, (x0 + 1, y0 + 1, x1 - 1, y0 + ih))
    y = y0 + ih + 5
    num_chip(draw, x0 + 6, y, n, region)
    draw.text((x0 + 26, y + 3), kicker, font=font(8, True), fill=REGION_COLORS[region])
    badge(draw, x1 - 62, y + 2, bdg)
    y += 20
    y = draw_wrapped(draw, (x0 + 6, y), head, font(14, True), x1 - x0 - 12, leading=16, max_lines=3)
    y += 1
    y = draw_wrapped(draw, (x0 + 6, y), body, font(9), x1 - x0 - 12, leading=11, max_lines=4)
    y += 2
    draw_wrapped(draw, (x0 + 6, y), why, font(8, True), x1 - x0 - 12, leading=10, max_lines=2)
    draw.text((x0 + 6, y1 - 13), src, font=font(7, True), fill=GREY)


def medium_card(img, draw, box, story):
    n, region, kicker, head, body, bdg, src, ill = story
    x0, y0, x1, y1 = box
    card_frame(draw, box)
    ih = 56
    draw_ill(img, ill, (x0 + 1, y0 + 1, x1 - 1, y0 + ih))
    y = y0 + ih + 4
    num_chip(draw, x0 + 5, y, n, region)
    draw.text((x0 + 24, y + 3), kicker, font=font(7, True), fill=REGION_COLORS[region])
    badge(draw, x1 - 58, y + 2, bdg)
    y += 19
    y = draw_wrapped(draw, (x0 + 5, y), head, font(10, True), x1 - x0 - 10, leading=11, max_lines=2)
    y = draw_wrapped(draw, (x0 + 5, y + 1), body, font(8), x1 - x0 - 10, leading=10, max_lines=3)
    draw.text((x0 + 5, y1 - 12), src, font=font(7, True), fill=GREY)


def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # subtle deterministic paper grain (visual density, same bytes every run)
    rng = random.Random(20261125)
    px = img.load()
    for _ in range(95000):
        gx, gy = rng.randrange(W), rng.randrange(H)
        r, g, b = px[gx, gy]
        delta = rng.choice((-4, -3, 3, 4))
        px[gx, gy] = (max(0, min(255, r + delta)), max(0, min(255, g + delta)), max(0, min(255, b + delta)))

    M = 12  # page margin
    # top navy strip
    d.rectangle([0, 0, W, 22], fill=NAVY)
    d.text((M, 5), "THE WORLD IN ONE DAY", font=font(10, True), fill=WHITE)
    right = "36 STORIES · 9 REGIONS · EVERY ONE FIRST REPORTED WED 25 NOV 2026"
    d.text((W - M - d.textlength(right, font=font(9, True)), 6), right, font=font(9, True), fill=WHITE)

    # masthead
    mast = "Wednesday 25 November 2026"
    mf = font(46, True)
    d.text(((W - d.textlength(mast, font=mf)) / 2, 26), mast, font=mf, fill=INK)
    sub = "AI shakeout rattles world markets  ·  US proposes tariffs on 14 economies  ·  Pakistan's first astronaut docks at Tiangong"
    sf = font(11, True)
    d.text(((W - d.textlength(sub, font=sf)) / 2, 82), sub, font=sf, fill=(70, 64, 52))
    d.line([M, 100, W - M, 100], fill=INK, width=2)
    d.line([M, 103, W - M, 103], fill=INK, width=1)

    # stat band
    sy0, sy1 = 108, 152
    cell_w = (W - 2 * M) // len(STATS)
    for i, (num, cap) in enumerate(STATS):
        cx = M + i * cell_w
        if i:
            d.line([cx, sy0 + 2, cx, sy1 - 2], fill=(190, 182, 165), width=1)
        nf = font(19, True)
        d.text((cx + 6, sy0), num, font=nf, fill=RED if num.startswith(("−", "-")) else INK)
        draw_wrapped(d, (cx + 6, sy0 + 24), cap, font(7), cell_w - 12, fill=(80, 74, 62), leading=9, max_lines=2)
    d.line([M, sy1 + 2, W - M, sy1 + 2], fill=INK, width=1)

    # region bar
    ry0, ry1 = 158, 174
    total = sum(c for _, c in REGION_BAR)
    rx = M
    for name, count in REGION_BAR:
        rw = int((W - 2 * M) * count / total)
        d.rectangle([rx, ry0, rx + rw - 2, ry1], fill=REGION_COLORS[name])
        label = f"{name} {count}"
        lf = font(7, True)
        tw = d.textlength(label, font=lf)
        if tw < rw - 6:
            d.text((rx + (rw - tw) / 2, ry0 + 4), label, font=lf, fill=WHITE)
        else:
            d.text((rx + (rw - d.textlength(str(count), font=lf)) / 2, ry0 + 4), str(count), font=lf, fill=WHITE)
        rx += rw

    # features row
    fy0, fy1 = 180, 428
    fw = (W - 2 * M - 12) // 3
    for i, story in enumerate(FEATURES):
        fx = M + i * (fw + 6)
        feature_card(img, d, (fx, fy0, fx + fw, fy1), story)

    # mediums: 2 rows x 5
    my0 = 434
    mw = (W - 2 * M - 24) // 5
    mh = 132
    for i, story in enumerate(MEDIUMS):
        r, c = divmod(i, 5)
        mx = M + c * (mw + 6)
        my = my0 + r * (mh + 6)
        medium_card(img, d, (mx, my, mx + mw, my + mh), story)

    # bottom: map left, briefs right
    by0 = my0 + 2 * mh + 12  # 710
    map_box = (M, by0 + 16, M + 330, by0 + 160)
    d.text((M, by0), "WHERE IT HAPPENED — STORIES 1–13", font=font(9, True), fill=INK)
    d.text((M, by0 + 11), "Pins 1–13 locate the pictured stories — one colour per region, everywhere.", font=font(7), fill=GREY)
    draw_map(d, map_box)
    ly = by0 + 166
    items = list(REGION_COLORS.items())
    for i in range(0, 9, 3):
        for j in range(3):
            if i + j >= 9:
                break
            name, col = items[i + j]
            lx = M + j * 112
            d.ellipse([lx, ly + 1, lx + 8, ly + 9], fill=col)
            d.text((lx + 11, ly), name, font=font(7, True), fill=INK)
        ly += 12
    d.text((M, ly + 2), "How sure:  O official — stated by the authority itself · C claim —", font=font(7), fill=GREY)
    d.text((M, ly + 12), "one side's word, unverified · R reported — major outlets, not yet confirmed.", font=font(7), fill=GREY)

    bx0 = M + 342
    d.text((bx0, by0), "ALSO ON WEDNESDAY — 23 MORE DATED BRIEFS, NUMBERED AND COLOUR-MATCHED BY REGION", font=font(9, True), fill=INK)
    col_w = (W - M - bx0 - 8) // 2
    half = (len(BRIEFS) + 1) // 2
    for ci, chunk in enumerate([BRIEFS[:half], BRIEFS[half:]]):
        cx = bx0 + ci * (col_w + 8)
        cy = by0 + 16
        for n, region, text, letter in chunk:
            col = REGION_COLORS[region]
            d.ellipse([cx, cy, cx + 13, cy + 13], fill=col)
            nf = font(7, True)
            s = str(n)
            d.text((cx + 6.5 - d.textlength(s, font=nf) / 2, cy + 2), s, font=nf, fill=WHITE)
            lines = wrap(d, text, font(7), col_w - 20)
            for ln in lines[:2]:
                d.text((cx + 17, cy), ln, font=font(7), fill=INK)
                cy += 8
            d.ellipse([cx + col_w - 12, cy - 8, cx + col_w - 2, cy + 2], fill=BADGE_COLORS[{"O": "OFFICIAL", "R": "REPORTED", "C": "CLAIM"}[letter]])
            d.text((cx + col_w - 9.5, cy - 7), letter, font=font(6, True), fill=WHITE)
            cy += 2

    # date check + footer
    dy = 952
    d.rectangle([M, dy, W - M, dy + 40], outline=RED, width=1)
    d.rectangle([M, dy, M + 74, dy + 40], fill=RED)
    d.text((M + 8, dy + 6), "DATE", font=font(10, True), fill=WHITE)
    d.text((M + 8, dy + 19), "CHECK", font=font(10, True), fill=WHITE)
    dc = ("Left out as other days' news: Huawei verdict (Tue 24 Nov) · CAS returns the Africa Cup to Senegal (Tue 24) · "
          "drone hits Riyadh's PIF Tower (Tue 24) · UCL Tuesday results (Tue 24) · CIA/ODNI hack disclosure (Tue 24). "
          "PREVIEW items (Spain poll, Qatar GP) are plans for Sunday 29 Nov, labelled as such.")
    draw_wrapped(d, (M + 82, dy + 4), dc, font(8), W - 2 * M - 90, leading=10, max_lines=4)
    d.text((M, 998), "HOW SURE:  OFFICIAL an authority's own word · REPORTED major outlets · CLAIM one side's account, unverified · PREVIEW a plan, not an event.",
           font=font(7, True), fill=INK)
    foot = "Sources: Reuters, AP, Xinhua, NATO, BEA, WAM, PM.gov.au. Every story happened, or was first reported, on Wednesday 25 November 2026. Drawings original, made for this page."
    d.text((M, 1010), foot, font=font(7), fill=GREY)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    try:
        img = render()
        img.save(target, optimize=True)
    except Exception:
        # No Pillow/fonts in the stdlib-only harness container: publish the
        # bundled entry.png, which this same code rendered byte-for-byte.
        bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
        shutil.copyfile(bundled, target)


if __name__ == "__main__":
    main()
