"""over-the-shoulder — proof cards pop up beside your head while the camera pushes in."""
import math
from PIL import Image, ImageDraw, ImageFilter
from lib.core import *

NAME = "over-the-shoulder"
DESC = "карточки с цифрами у твоей головы"
TITLE = "карточки у головы"
BEFORE = ("ДО", "1 204", "просмотра")
AFTER = ("ПОСЛЕ", 412, "K просмотров")     # counts up to 412K
SFX = [(0.15, "pop"), (0.45, "pop")] + [(0.55 + i * 0.12, "tick") for i in range(6)] + [(1.3, "chime")]
GREEN = (36, 180, 90)


def _card(lines, w=280, h=190, accent=None):
    c = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 40, w + 30, h + 40), 28, fill=(0, 0, 0, 120))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((30, 30, w + 30, h + 30), 28, fill=(255, 255, 255, 250))
    k, big, small = lines
    d.text((56, 52), k, font=font("mono", 22, 700), fill=(120, 120, 120))
    d.text((52, 82), big, font=font("oswald", 74, 700), fill=INK)
    d.text((56, 178), small, font=font("sans", 22, 600), fill=accent or (110, 110, 110))
    return c


def render(ctx, tl, ts):
    t = tl
    z = 1.0 + 0.12 * ease_in_out(prog(t, 0.0, 1.8))
    base, mask = ctx.src(ts, zoom=z, anchor=(540, 600))
    img = grade(base, sat=1.05, contrast=1.05)
    hx, htop, hw = head_from_mask(mask) if mask is not None else (540, 430, 300)

    cnt = ease_out(prog(t, 0.55, 0.75))
    n = int(AFTER[1] * cnt)
    cards = [
        (_card(BEFORE), (min(200, hx - hw / 2 - 190), htop - 10), -5, 0.15),
        (_card((AFTER[0], f"{n}K", "+34 000%"), accent=GREEN), (max(880, hx + hw / 2 + 190), htop - 50), 5, 0.45),
    ]
    out = img.convert("RGBA")
    for c, (cx, cy), rot, st in cards:
        q = ease_back(prog(t, st, 0.35), 2.0)
        if q <= 0.01:
            continue
        cc = c.rotate(rot * q, resample=Image.BICUBIC, expand=True)
        cc = cc.resize((max(2, int(cc.width * q)), max(2, int(cc.height * q))), Image.LANCZOS)
        cx = clamp(cx, cc.width / 2 + 10, W - cc.width / 2 - 10)
        out.alpha_composite(cc, (int(cx - cc.width / 2), int(cy - cc.height / 2)))
    return caption(out.convert("RGB"), TITLE, t, 0.6)
