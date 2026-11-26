# Renderer for the 25 Nov 2026 front page (1024x1024 PNG).
# Cream newspaper, 3 big features, 10 illustrated mediums, 24 briefs,
# numbered map pins, verification badges. Build-time only (Pillow).

import math
import os
from PIL import Image, ImageDraw, ImageFont

from stories import FEATURES, MEDIUM, BRIEFS, REGIONS, STATS

W = H = 1024
BG = (247, 243, 232)
INK = (26, 24, 22)
MUTED = (96, 90, 80)
RED = (178, 34, 34)
BLUE = (28, 74, 140)
GOLD = (176, 124, 22)
GREEN = (26, 110, 62)
TEAL = (14, 110, 110)
PURPLE = (92, 52, 140)
CARD = (255, 253, 247)
LINE = (201, 194, 178)

FDIR = "/usr/share/fonts/truetype"
SERIF_B = f"{FDIR}/dejavu/DejaVuSerif-Bold.ttf"
SERIF = f"{FDIR}/dejavu/DejaVuSerif.ttf"
SANS_B = f"{FDIR}/dejavu/DejaVuSans-Bold.ttf"
SANS = f"{FDIR}/dejavu/DejaVuSans.ttf"
MONO = f"{FDIR}/dejavu/DejaVuSansMono.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
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


def badge(draw, x, y, label):
    colors = {"CONFIRMED": GREEN, "OFFICIAL": BLUE, "REPORTED": GOLD, "CLAIM": RED}
    c = colors.get(label, MUTED)
    f = font(SANS_B, 11)
    tw = draw.textlength(label, font=f)
    draw.rounded_rectangle([x, y, x + tw + 12, y + 18], radius=4, fill=c)
    draw.text((x + 6, y + 3), label, font=f, fill=(255, 255, 255))
    return x + tw + 12


# ---------- illustrations (each ~40% of its card) ----------

def art_market(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(20, 28, 52))
    pts = []
    vals = [0.25, 0.35, 0.30, 0.55, 0.85, 0.45, 0.38, 0.28, 0.22]
    for i, v in enumerate(vals):
        px = x0 + 14 + i * (x1 - x0 - 28) / (len(vals) - 1)
        py = y1 - 12 - v * (y1 - y0 - 26)
        pts.append((px, py))
    for i in range(5):
        gy = y0 + 10 + i * (y1 - y0 - 20) / 4
        d.line([x0 + 10, gy, x1 - 10, gy], fill=(60, 80, 130), width=1)
    d.line(pts, fill=(255, 90, 90), width=4)
    for p in pts:
        d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(255, 220, 120))
    d.text((x0 + 12, y0 + 6), "NVDA $155.38  -5.9%", font=font(MONO, 12), fill=(255, 220, 120))
    d.text((x0 + 12, y1 - 20), "KOSPI -6.16%  NIKKEI -2.78%", font=font(MONO, 11), fill=(170, 200, 255))


def art_refinery(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(38, 30, 34))
    for i, fx in enumerate([0.22, 0.45, 0.68]):
        tx = x0 + fx * (x1 - x0)
        d.rectangle([tx - 9, y0 + 34, tx + 9, y1 - 8], fill=(150, 150, 160))
        d.rectangle([tx - 13, y0 + 30, tx + 13, y0 + 38], fill=(190, 190, 200))
        d.polygon([(tx - 14, y0 + 34), (tx, y0 + 6), (tx + 14, y0 + 34)], fill=(255, 130, 40))
        d.polygon([(tx - 7, y0 + 34), (tx, y0 + 16), (tx + 7, y0 + 34)], fill=(255, 210, 90))
    d.rectangle([x0 + 8, y1 - 16, x1 - 8, y1 - 8], fill=(90, 90, 100))
    d.text((x0 + 10, y0 + 6), "SAMARA · 2 REFINERIES HIT", font=font(SANS_B, 11), fill=(255, 200, 150))


def art_hormuz(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 54, 84))
    d.polygon([(x0, y0), (x0 + 90, y0), (x0 + 55, y0 + 55), (x0, y1)], fill=(222, 198, 140))
    d.polygon([(x1, y0), (x1 - 70, y0), (x1 - 40, y0 + 60), (x1, y1)], fill=(222, 198, 140))
    d.polygon([(x0 + 30, y1), (x0 + 90, y1 - 40), (x1 - 60, y1 - 40), (x1 - 20, y1)], fill=(222, 198, 140))
    for sx, sy in [(0.42, 0.42), (0.58, 0.55)]:
        cx, cy = x0 + sx * (x1 - x0), y0 + sy * (y1 - y0)
        d.rectangle([cx - 22, cy - 5, cx + 22, cy + 5], fill=(240, 240, 240))
        d.polygon([(cx + 22, cy - 5), (cx + 32, cy), (cx + 22, cy + 5)], fill=(240, 240, 240))
        d.polygon([(cx - 8, cy - 22), (cx, cy - 8), (cx + 8, cy - 22)], fill=(255, 130, 40))
    d.text((x0 + 10, y0 + 6), "STRAIT OF HORMUZ", font=font(SANS_B, 11), fill=(255, 255, 255))
    d.text((x0 + 10, y1 - 20), "TRAFFIC -40%", font=font(MONO, 11), fill=(255, 220, 120))


def art_generic(d, box, kind, label):
    x0, y0, x1, y1 = box
    palettes = {
        "court": ((52, 40, 30), (230, 200, 140)), "rocket": ((10, 16, 48), (255, 255, 255)),
        "city": ((30, 50, 70), (255, 220, 150)), "ballot": ((90, 20, 30), (255, 255, 255)),
        "ball": ((18, 90, 44), (255, 255, 255)), "mine": ((40, 34, 28), (255, 200, 110)),
        "factory": ((60, 60, 70), (255, 220, 140)), "trophy": ((70, 52, 10), (255, 220, 90)),
        "island": ((14, 80, 100), (255, 240, 190)), "tariff": ((40, 30, 60), (255, 200, 120)),
    }
    bg, fg = palettes.get(kind, ((40, 40, 40), (255, 255, 255)))
    d.rectangle(box, fill=bg)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "rocket":
        d.polygon([(cx, y0 + 6), (cx - 10, cy + 8), (cx + 10, cy + 8)], fill=fg)
        d.rectangle([cx - 10, cy + 8, cx + 10, y1 - 16], fill=fg)
        d.polygon([(cx - 8, y1 - 16), (cx, y1 - 4), (cx + 8, y1 - 16)], fill=(255, 150, 50))
        for sx, sy in [(0.2, 0.3), (0.8, 0.25), (0.7, 0.7), (0.25, 0.75)]:
            d.ellipse([x0 + sx * (x1 - x0) - 2, y0 + sy * (y1 - y0) - 2, x0 + sx * (x1 - x0) + 2, y0 + sy * (y1 - y0) + 2], fill=fg)
    elif kind == "ball":
        d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=fg)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=bg)
        for a in range(0, 360, 60):
            px = cx + 15 * math.cos(math.radians(a)); py = cy + 15 * math.sin(math.radians(a))
            d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=bg)
    elif kind == "trophy":
        d.rectangle([cx - 18, y0 + 10, cx + 18, cy + 4], fill=fg)
        d.arc([cx - 30, y0 + 12, cx - 8, cy + 2], 90, 270, fill=fg, width=4)
        d.arc([cx + 8, y0 + 12, cx + 30, cy + 2], 270, 90, fill=fg, width=4)
        d.rectangle([cx - 5, cy + 4, cx + 5, y1 - 12], fill=fg)
        d.rectangle([cx - 16, y1 - 12, cx + 16, y1 - 6], fill=fg)
    elif kind == "court":
        for i in range(4):
            bx = x0 + 18 + i * ((x1 - x0 - 36) / 3)
            d.rectangle([bx - 4, y0 + 18, bx + 4, y1 - 10], fill=fg)
        d.polygon([(x0 + 10, y0 + 18), (cx, y0 + 6), (x1 - 10, y0 + 18)], fill=fg)
    elif kind == "mine":
        d.polygon([(x0 + 10, y1 - 8), (cx - 30, y0 + 14), (cx + 30, y0 + 14), (x1 - 10, y1 - 8)], fill=(110, 95, 80))
        d.rectangle([cx - 10, cy - 2, cx + 10, y1 - 8], fill=(15, 12, 10))
        d.text((cx - 3, cy + 4), "100m", font=font(MONO, 10), fill=fg)
    elif kind == "island":
        d.ellipse([cx - 34, cy - 6, cx + 34, cy + 14], fill=(232, 208, 150))
        d.line([cx - 6, cy - 4, cx - 10, y0 + 12], fill=(60, 120, 60), width=4)
        d.line([cx - 10, y0 + 12, cx - 24, y0 + 18], fill=(60, 160, 60), width=3)
        d.line([cx - 10, y0 + 12, cx + 4, y0 + 18], fill=(60, 160, 60), width=3)
    elif kind == "tariff":
        d.rectangle([cx - 26, y0 + 14, cx + 26, y1 - 10], fill=fg)
        d.text((cx - 16, cy - 8), "301", font=font(SANS_B, 20), fill=bg)
    elif kind == "ballot":
        d.rectangle([cx - 30, cy - 2, cx + 30, y1 - 8], fill=fg)
        d.rectangle([cx - 14, y0 + 8, cx + 14, cy + 8], fill=(255, 255, 255))
        d.line([cx - 8, cy - 2, cx - 2, cy + 4], fill=RED, width=3)
        d.line([cx - 2, cy + 4, cx + 9, cy - 6], fill=RED, width=3)
    elif kind == "factory":
        for i in range(3):
            bx = x0 + 16 + i * 34
            d.rectangle([bx, cy - 6, bx + 26, y1 - 8], fill=(180, 180, 190))
            d.rectangle([bx + 8, y0 + 10, bx + 16, cy - 6], fill=(150, 150, 160))
    else:  # city
        heights = [0.5, 0.8, 0.6, 0.9, 0.55]
        bw = (x1 - x0 - 24) / len(heights)
        for i, hh in enumerate(heights):
            bx = x0 + 12 + i * bw
            top = y1 - 8 - hh * (y1 - y0 - 18)
            d.rectangle([bx, top, bx + bw - 6, y1 - 8], fill=(120, 140, 170))
            for wy in range(int(top) + 6, y1 - 14, 9):
                d.rectangle([bx + 4, wy, bx + 8, wy + 4], fill=fg)
    d.text((x0 + 8, y0 + 5), label, font=font(SANS_B, 10), fill=fg)


ART = {"market": art_market, "refinery": art_refinery, "hormuz": art_hormuz}


def draw_art(d, box, kind, label=""):
    if kind in ART:
        ART[kind](d, box)
    else:
        art_generic(d, box, kind, label)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    M = 22  # margin

    # Masthead
    d.text((M, 10), "THE WORLD IN ONE DAY", font=font(SERIF_B, 40), fill=INK)
    d.text((M, 56), "Wednesday 25 November 2026  ·  37 stories  ·  7 regions  ·  one page", font=font(SANS, 15), fill=MUTED)
    d.text((W - M - 250, 14), "DATE CHECK", font=font(SANS_B, 13), fill=RED)
    d.text((W - M - 250, 32), "All items happened or were", font=font(SANS, 12), fill=INK)
    d.text((W - M - 250, 47), "first reported Wed 25 Nov 2026.", font=font(SANS, 12), fill=INK)
    d.text((W - M - 250, 62), "Tue events labelled Tue.", font=font(SANS, 12), fill=INK)
    d.line([M, 82, W - M, 82], fill=INK, width=3)
    d.line([M, 87, W - M, 87], fill=INK, width=1)

    # Stat band
    y = 92
    sw = (W - 2 * M) / len(STATS)
    for i, (num, lab) in enumerate(STATS):
        x = M + i * sw
        d.text((x + 6, y), num, font=font(SERIF_B, 20), fill=INK)
        d.text((x + 6, y + 24), lab, font=font(SANS, 11), fill=MUTED)
        if i:
            d.line([x, y + 2, x, y + 38], fill=LINE, width=1)
    d.line([M, y + 44, W - M, y + 44], fill=LINE, width=1)

    # 3 big features
    fy = y + 52
    fw = (W - 2 * M - 16) / 3
    fh = 222
    for i, s in enumerate(FEATURES):
        x = M + i * (fw + 8)
        d.rectangle([x, fy, x + fw, fy + fh], fill=CARD, outline=LINE, width=1)
        draw_art(d, (x + 8, fy + 8, x + fw - 8, fy + 96), s["art"])
        d.text((x + 10, fy + 102), s["kicker"], font=font(SANS_B, 10), fill=RED)
        d.text((x + 10, fy + 117), f"{s['n']}. {s['head']}", font=font(SERIF_B, 19), fill=INK)
        badge(d, x + 10, fy + 143, s["badge"])
        d.text((x + 118, fy + 145), s["src"], font=font(SANS, 11), fill=MUTED)
        ty = fy + 166
        for ln in wrap(d, s["body"], font(SANS, 11.5), fw - 20)[:4]:
            d.text((x + 10, ty), ln, font=font(SANS, 11.5), fill=INK)
            ty += 14

    # Region bar
    ry = fy + fh + 8
    d.rectangle([M, ry, W - M, ry + 24], fill=INK)
    rx = M + 10
    for name, cnt in REGIONS:
        t = f"{name} {cnt}"
        d.text((rx, ry + 5), t, font=font(SANS_B, 11), fill=(255, 255, 255))
        rx += d.textlength(t, font=font(SANS_B, 11)) + 22

    # 10 mediums, 5 x 2
    my = ry + 32
    mw = (W - 2 * M - 32) / 5
    mh = 172
    for i, s in enumerate(MEDIUM):
        col, row = i % 5, i // 5
        x = M + col * (mw + 8)
        yy = my + row * (mh + 8)
        d.rectangle([x, yy, x + mw, yy + mh], fill=CARD, outline=LINE, width=1)
        draw_art(d, (x + 6, yy + 6, x + mw - 6, yy + 66), s["art"], s["loc"].split(",")[0].upper())
        hlines = wrap(d, f"{s['n']}. {s['head']}", font(SERIF_B, 12.5), mw - 16)
        hy = yy + 71
        for ln in hlines[:2]:
            d.text((x + 8, hy), ln, font=font(SERIF_B, 12.5), fill=INK)
            hy += 15
        badge(d, x + 8, yy + 103, s["badge"])
        for ln in wrap(d, s["loc"] + " · " + s["src"], font(SANS, 9.5), mw - 16)[:1]:
            d.text((x + 8, yy + 124), ln, font=font(SANS, 9.5), fill=MUTED)
        ty = yy + 137
        for ln in wrap(d, s["body"], font(SANS, 10), mw - 16)[:3]:
            d.text((x + 8, ty), ln, font=font(SANS, 10), fill=INK)
            ty += 12

    # Briefs + map
    by = my + 2 * mh + 14
    d.text((M, by), "BRIEFS 14-37 — every line sourced", font=font(SANS_B, 12), fill=INK)
    d.text((W - M - 330, by), "MAP — pins 1-13 = drawn stories", font=font(SANS_B, 12), fill=INK)
    by += 18
    # map box right
    mx0, mx1 = W - M - 330, W - M
    my0, my1 = by, by + 150
    d.rectangle([mx0, my0, mx1, my1], fill=(214, 230, 242), outline=LINE, width=1)
    # crude continents
    d.polygon([(mx0 + 18, my0 + 22), (mx0 + 80, my0 + 16), (mx0 + 86, my0 + 52), (mx0 + 40, my0 + 66)], fill=(150, 190, 140))
    d.polygon([(mx0 + 52, my0 + 72), (mx0 + 82, my0 + 70), (mx0 + 76, my0 + 106), (mx0 + 58, my0 + 104)], fill=(150, 190, 140))
    d.polygon([(mx0 + 130, my0 + 20), (mx0 + 250, my0 + 16), (mx0 + 262, my0 + 60), (mx0 + 150, my0 + 64)], fill=(150, 190, 140))
    d.polygon([(mx0 + 150, my0 + 66), (mx0 + 196, my0 + 64), (mx0 + 188, my0 + 104), (mx0 + 158, my0 + 100)], fill=(230, 200, 140))
    d.polygon([(mx0 + 252, my0 + 78), (mx0 + 302, my0 + 76), (mx0 + 306, my0 + 100), (mx0 + 258, my0 + 102)], fill=(230, 200, 140))
    pins = {1: (0.16, 0.32), 2: (0.56, 0.28), 3: (0.60, 0.48), 4: (0.18, 0.34), 5: (0.74, 0.36),
            6: (0.20, 0.62), 7: (0.47, 0.30), 8: (0.49, 0.28), 9: (0.72, 0.60), 10: (0.70, 0.48),
            11: (0.50, 0.30), 12: (0.84, 0.78), 13: (0.17, 0.30)}
    for n, (fx, fy2) in pins.items():
        px, py = mx0 + fx * (mx1 - mx0), my0 + fy2 * (my1 - my0)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        d.text((px - 3 if n < 10 else px - 6, py - 6), str(n), font=font(SANS_B, 9), fill=(255, 255, 255))
    d.text((mx0 + 8, my1 - 16), "Each number is the story with that number on this page.", font=font(SANS, 9), fill=INK)
    # briefs two columns left of map (compact so all 24 fit above footer)
    bw = (mx0 - M - 12) / 2
    half = (len(BRIEFS) + 1) // 2
    for c in range(2):
        x = M + c * (bw + 12)
        ty = by
        for j in range(c * half, min((c + 1) * half, len(BRIEFS))):
            lines = wrap(d, f"{j + 14}. {BRIEFS[j]}", font(SANS, 9.5), bw)
            for ln in lines[:2]:
                d.text((x, ty), ln, font=font(SANS, 9.5), fill=INK)
                ty += 11
            ty += 1

    # Footer
    fy2 = H - 42
    d.line([M, fy2, W - M, fy2], fill=INK, width=1)
    d.text((M, fy2 + 6), "HOW SURE ARE WE?  CONFIRMED = 2+ outlets · OFFICIAL = on the record · REPORTED = one outlet · CLAIM = one side, unverified", font=font(SANS_B, 11), fill=INK)
    d.text((M, fy2 + 23), "Sources on every story. Hormuz mine claim (3) and DR Congo shootdown (29) marked CLAIM. US closes Tue 24 Nov; Asia closes Wed 25 Nov.", font=font(SANS, 11), fill=MUTED)

    # Newsprint grain: subtle speckle for print texture and visual density.
    import random
    rng = random.Random(20261125)
    px = img.load()
    for _ in range(26000):
        gx, gy = rng.randrange(W), rng.randrange(H)
        r, g, b = px[gx, gy]
        delta = rng.choice((-14, -9, 9, 14))
        px[gx, gy] = (max(0, min(255, r + delta)), max(0, min(255, g + delta)), max(0, min(255, b + delta)))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    # Low compression keeps visual density high (winner files run 350KB+).
    img.save(out, compress_level=1)
    print(f"wrote {out} {os.path.getsize(out)} bytes {img.size}")


if __name__ == "__main__":
    main()
