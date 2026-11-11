"""glass-graph — a liquid-glass card with a climbing graph on your chest."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib.core import *

NAME = "glass-graph"
DESC = "стеклянная карточка с растущим графиком"
TITLE = "стеклянный график"
LABEL = ("УДЕРЖАНИЕ", "в среднем по рилс")
FROM, TO = 21, 68
SFX = [(0.0, "swoosh")] + [(0.3 + i * 0.13, "tick") for i in range(8)] + [(1.4, "chime")]
GREEN = (60, 220, 120)
BOX = (110, 1040, 970, 1450)


def _curve(n=60):
    xs = np.linspace(0, 1, n)
    ys = 0.08 + 0.75 * xs ** 1.6 + 0.04 * np.sin(xs * 11) * (1 - xs)
    return xs, ys


def render(ctx, tl, ts):
    t = tl
    img, mask = ctx.src(ts, zoom=1.04, anchor=(540, 600))
    img = grade(img, sat=1.04, contrast=1.04)
    q = ease_back(prog(t, 0.0, 0.4), 1.4)
    x0, y0, x1, y1 = BOX
    if mask is not None:                      # keep the card below the face
        hx, htop, hw = head_from_mask(mask)
        shift = clamp(htop + 1.35 * hw - y0, 0, 330)
        y0, y1 = y0 + shift, y1 + shift
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) * q, (y1 - y0) * q
    if q > 0.02:
        glass(img, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), r=44, tint=(255, 255, 255), alpha=0.10, blur=28, border=0.4)
    p = ease_in_out(prog(t, 0.25, 1.15))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    a = int(255 * clamp(prog(t, 0.2, 0.2)))
    if a > 0:
        d.text((x0 + 44, y0 + 50), LABEL[0], font=font("sans", 30, 800), fill=(255, 255, 255, a))
        d.text((x0 + 44, y0 + 92), LABEL[1], font=font("sans", 24, 500), fill=(255, 255, 255, int(a * .75)))
        val = int(round(FROM + (TO - FROM) * p))
        fb = font("oswald", 110, 700)
        d.text((x1 - 90, y0 + 30), f"{val}", font=fb, fill=(255, 255, 255, a), anchor="ra")
        d.text((x1 - 44, y0 + 120), "%", font=font("oswald", 48, 700), fill=(255, 255, 255, a), anchor="rs")
        # chart
        gx0, gx1, gy0, gy1 = x0 + 44, x1 - 44, y0 + 175, y1 - 40
        for i in range(4):
            yy = gy0 + (gy1 - gy0) * i / 3
            d.line((gx0, yy, gx1, yy), fill=(255, 255, 255, 40), width=2)
        xs, ys = _curve()
        k = max(2, int(len(xs) * p))
        pts = [(gx0 + (gx1 - gx0) * xs[i], gy1 - (gy1 - gy0) * ys[i]) for i in range(k)]
        if len(pts) > 1:
            fill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(fill).polygon(pts + [(pts[-1][0], gy1), (pts[0][0], gy1)], fill=GREEN + (70,))
            ov.alpha_composite(fill)
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(glow).line(pts, fill=GREEN + (255,), width=14, joint="curve")
            ov.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
            d.line(pts, fill=GREEN + (255,), width=6, joint="curve")
            ex, ey = pts[-1]
            d.ellipse((ex - 12, ey - 12, ex + 12, ey + 12), fill=(255, 255, 255))
            d.ellipse((ex - 7, ey - 7, ex + 7, ey + 7), fill=GREEN)
    out = img.convert("RGBA"); out.alpha_composite(ov)
    return caption(out.convert("RGB"), TITLE, t, 0.55, y=min(1730, y1 + 90))
