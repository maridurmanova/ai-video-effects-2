"""freeze-frame — the frame freezes, you get a white sticker outline and a name tag."""
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
from lib.core import *

NAME = "freeze-frame"
DESC = "стоп-кадр, обводка и плашка с именем"
TITLE = None
SFX = [(0.0, "shutter"), (0.35, "pop")]


def render(ctx, tl, ts):
    t = tl
    if t < 0:
        base, _ = ctx.src(ts, zoom=1.0, with_mask=False)
        return base
    tf = ts - t                       # frozen moment
    base, mask = ctx.src(tf, zoom=1.0, anchor=(540, 700))
    if mask is None:
        return base
    pop = 1 + 0.05 * ease_back(prog(t, 0.0, 0.35), 2)
    # dim background
    bg = grade(base, sat=0.35, contrast=0.9, bright=-70)
    # outline
    m8 = (mask > 0.5).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    dil = cv2.dilate(m8, k)
    dil = cv2.GaussianBlur(dil, (0, 0), 1.5).astype(np.float32) / 255
    a = np.asarray(bg, np.float32)
    a = a * (1 - dil[..., None]) + 255 * dil[..., None]           # white sticker edge
    a = a * (1 - mask[..., None]) + np.asarray(base, np.float32) * mask[..., None]
    fg = Image.fromarray(a.astype(np.uint8))
    # scale the sticker around the person's centre
    cx, cy = 540, 1000
    if pop != 1:
        fgs = fg.resize((int(W * pop), int(H * pop)), Image.LANCZOS)
        ds = cv2.resize(dil, (fgs.width, fgs.height))
        ox, oy = int(cx * (pop - 1)), int(cy * (pop - 1))
        fgc = fgs.crop((ox, oy, ox + W, oy + H))
        dc = ds[oy:oy + H, ox:ox + W]
        out = Image.fromarray((np.asarray(bg, np.float32) * (1 - dc[..., None]) + np.asarray(fgc, np.float32) * dc[..., None]).astype(np.uint8))
        shadow_mask = dc
    else:
        out = Image.fromarray((np.asarray(bg, np.float32) * (1 - dil[..., None]) + np.asarray(fg, np.float32) * dil[..., None]).astype(np.uint8))
    # flash
    fl = 1 - clamp(t / 0.15)
    if fl > 0:
        out = Image.blend(out, Image.new("RGB", (W, H), (255, 255, 255)), 0.85 * fl)
    # name tag
    q = ease_back(prog(t, 0.35, 0.35), 2.2)
    if q > 0.01:
        name = ctx.cfg["name"].split()[0].upper()
        f1 = font("oswald", 96, 700)
        w = int(tw(name, f1) + 90)
        tag = Image.new("RGBA", (w + 40, 220), (0, 0, 0, 0))
        d = ImageDraw.Draw(tag)
        d.rounded_rectangle((20, 20, w + 20, 190), 22, fill=(255, 255, 255), outline=(20, 20, 20), width=5)
        d.text((w / 2 + 20, 92), name, font=f1, fill=INK, anchor="mm")
        d.text((w / 2 + 20, 158), ctx.cfg.get("role", "АВТОР"), font=font("mono", 26, 700), fill=CLAY, anchor="mm")
        tag = tag.rotate(-4, resample=Image.BICUBIC, expand=True)
        tag = tag.resize((max(2, int(tag.width * q)), max(2, int(tag.height * q))), Image.LANCZOS)
        o = out.convert("RGBA")
        o.alpha_composite(tag, (int(540 - tag.width / 2), int(1560 - tag.height / 2)))
        out = o.convert("RGB")
    return out
