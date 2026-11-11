"""tier-list — a glass S/A/B/C/D ranking fills itself in front of you."""
from PIL import Image, ImageDraw, ImageFilter
from lib.core import *

NAME = "tier-list"
DESC = "рейтинг чего угодно, нейросеть заполняет сама"
TITLE = "тир-лист"
HEADER = ("Рейтинг нейросетей", "по задачам")
ROWS = [("S", (236, 92, 92)), ("A", (240, 152, 60)), ("B", (240, 200, 70)), ("C", (90, 190, 110)), ("D", (90, 140, 230))]
ITEMS = [("Тексты", 0, "text"), ("Картинки", 0, "image"), ("Видео", 1, "video"), ("Голос", 1, "voice"),
         ("Музыка", 2, "music"), ("Монтаж", 2, "film"), ("Слайды", 3, "slides"), ("Поиск", 3, "search"), ("Гороскоп", 4, "star")]
T0, DT = 0.2, 0.11
SFX = [(0.0, "swoosh")] + [(T0 + i * DT + 0.2, "tick") for i in range(len(ITEMS))] + [(T0 + len(ITEMS) * DT + 0.3, "chime")]
P = (60, 1000, 1020, 1730)


TILE = {"text": ((255, 170, 90), (230, 90, 60)), "image": ((120, 200, 255), (60, 110, 240)),
        "video": ((255, 110, 150), (200, 40, 110)), "voice": ((150, 120, 255), (95, 55, 220)),
        "music": ((255, 210, 80), (240, 140, 30)), "film": ((90, 220, 170), (20, 150, 120)),
        "slides": ((110, 225, 255), (30, 160, 210)), "search": ((180, 180, 195), (95, 95, 115)),
        "star": ((60, 60, 75), (25, 25, 35))}


def _icon(kind, s=96):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c1, c2 = TILE.get(kind, ((90, 90, 100), (50, 50, 60)))
    g = Image.new("RGBA", (s, s))
    gd = ImageDraw.Draw(g)
    for yy in range(s):
        k = yy / (s - 1)
        gd.line((0, yy, s, yy), fill=tuple(int(c1[i] * (1 - k) + c2[i] * k) for i in range(3)) + (255,))
    im.paste(g, (0, 0), rrect_mask((s, s), 24))
    d.rounded_rectangle((0, 0, s - 1, s - 1), 24, outline=(255, 255, 255, 70), width=2)
    c = (255, 255, 255)
    m = s / 96
    if kind == "text":
        for i, w in enumerate((56, 56, 40)):
            d.rounded_rectangle((20 * m, (26 + i * 16) * m, (20 + w) * m, (32 + i * 16) * m), 3, fill=c)
    elif kind == "image":
        d.ellipse((58 * m, 22 * m, 72 * m, 36 * m), fill=(255, 230, 120))
        d.polygon([(18 * m, 74 * m), (42 * m, 40 * m), (60 * m, 64 * m), (68 * m, 54 * m), (80 * m, 74 * m)], fill=c)
    elif kind == "video":
        d.polygon([(36 * m, 26 * m), (36 * m, 70 * m), (72 * m, 48 * m)], fill=c)
    elif kind == "voice":
        d.rounded_rectangle((38 * m, 18 * m, 58 * m, 56 * m), 10, fill=c)
        d.arc((28 * m, 34 * m, 68 * m, 66 * m), 0, 180, fill=c, width=int(5 * m))
        d.line((48 * m, 66 * m, 48 * m, 78 * m), fill=c, width=int(5 * m))
    elif kind == "music":
        d.ellipse((26 * m, 58 * m, 44 * m, 74 * m), fill=c)
        d.ellipse((54 * m, 52 * m, 72 * m, 68 * m), fill=c)
        d.line((42 * m, 66 * m, 42 * m, 26 * m), fill=c, width=int(5 * m))
        d.line((70 * m, 60 * m, 70 * m, 20 * m), fill=c, width=int(5 * m))
        d.line((42 * m, 26 * m, 70 * m, 20 * m), fill=c, width=int(7 * m))
    elif kind == "film":
        d.rectangle((22 * m, 26 * m, 74 * m, 70 * m), outline=c, width=int(5 * m))
        for i in range(4):
            d.rectangle(((26 + i * 13) * m, 30 * m, (31 + i * 13) * m, 35 * m), fill=c)
            d.rectangle(((26 + i * 13) * m, 61 * m, (31 + i * 13) * m, 66 * m), fill=c)
    elif kind == "slides":
        for i, h in enumerate((20, 34, 48)):
            d.rectangle(((24 + i * 18) * m, (72 - h) * m, (36 + i * 18) * m, 72 * m), fill=c)
    elif kind == "star":
        import math as _m
        pts = [(48 * m + (30 if i % 2 == 0 else 13) * m * _m.cos(_m.pi / 2 + i * _m.pi / 5),
                50 * m - (30 if i % 2 == 0 else 13) * m * _m.sin(_m.pi / 2 + i * _m.pi / 5)) for i in range(10)]
        d.polygon(pts, fill=(255, 215, 90))
    elif kind == "search":
        d.ellipse((24 * m, 22 * m, 60 * m, 58 * m), outline=c, width=int(7 * m))
        d.line((56 * m, 54 * m, 74 * m, 72 * m), fill=c, width=int(9 * m))
    return im


def _slot(i):
    row = ITEMS[i][1]
    k = sum(1 for j in range(i) if ITEMS[j][1] == row)
    x = P[0] + 200 + k * 170
    y = P[1] + 130 + row * 116
    return x, y


def render(ctx, tl, ts):
    t = tl
    img, _ = ctx.src(ts, zoom=1.3, anchor=(540, 1160), with_mask=False)
    img = grade(img, sat=1.04, contrast=1.04)
    q = ease_out(prog(t, 0.0, 0.4))
    off = (1 - q) * 900
    x0, y0, x1, y1 = P
    glass(img, (x0, y0 + off, x1, y1 + off), r=40, tint=(18, 18, 22), alpha=0.5, blur=26, border=0.25)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.text((x0 + 40, y0 + 52 + off), HEADER[0], font=font("sans", 38, 700), fill=(255, 255, 255), anchor="lm")
    d.text((x1 - 40, y0 + 52 + off), HEADER[1], font=font("playfair", 38, 500), fill=(255, 255, 255, 200), anchor="rm")
    for r, (lab, col) in enumerate(ROWS):
        y = y0 + 130 + r * 116 + off
        d.rounded_rectangle((x0 + 30, y - 48, x0 + 126, y + 48), 18, fill=col)
        d.text((x0 + 78, y), lab, font=font("oswald", 56, 700), fill=(255, 255, 255), anchor="mm")
        d.line((x0 + 140, y + 56, x1 - 30, y + 56), fill=(255, 255, 255, 30), width=2)
    for i, (name, row, kind) in enumerate(ITEMS):
        p = ease_out(prog(t, T0 + i * DT, 0.32))
        if p <= 0:
            continue
        tx, ty = _slot(i)
        sx, sy = W + 100, y0 - 200
        x, y = lerp(sx, tx, p), lerp(sy, ty + off, p)
        ic = _icon(kind)
        ov.alpha_composite(ic, (int(x - 48), int(y - 48)))
        if p > 0.9:
            d.text((x, y + 52), name, font=font("sans", 20, 600), fill=(255, 255, 255, 220), anchor="mt")
    out = img.convert("RGBA"); out.alpha_composite(ov)
    return out.convert("RGB")
