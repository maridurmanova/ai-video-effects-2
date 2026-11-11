"""text-behind — a huge title appears behind your head."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib.core import *

NAME = "text-behind"
DESC = "огромный титр за твоей головой"
TITLE = "текст за головой"
WORD = "ВИРУСНО"          # change the word here
SFX = [(0.0, "whoosh"), (0.32, "impact"), (0.55, "pop")]


def render(ctx, tl, ts):
    t = tl
    base, mask = ctx.src(ts, zoom=1.05, anchor=(540, 640))
    base = grade(base, sat=1.05, contrast=1.06)
    hx, htop, hw = head_from_mask(mask) if mask is not None else (540, 430, 300)

    size = 400
    f = font("oswald", size, 700)
    size = int(size * min(1.0, 1010 / tw(WORD, f)))
    f = font("oswald", size, 700)
    total = tw(WORD, f)
    x = W / 2 - total / 2
    ytop = max(70, htop - 120)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(layer), ImageDraw.Draw(shadow)
    for i, ch in enumerate(WORD):
        q = ease_back(prog(t, 0.05 + i * 0.045, 0.35), 1.6)
        a = clamp(prog(t, 0.05 + i * 0.045, 0.15))
        if a <= 0:
            x += tw(ch, f); continue
        yy = ytop + (1 - q) * 160
        ds.text((x + 6, yy + 14), ch, font=f, fill=(0, 0, 0, int(120 * a)))
        d.text((x, yy), ch, font=f, fill=(255, 255, 255, int(255 * a)))
        x += tw(ch, f)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    out = base.convert("RGBA")
    out.alpha_composite(shadow)
    out.alpha_composite(layer)
    out = person_over(base, out.convert("RGB"), mask)
    return caption(out, TITLE, t, 0.55)
