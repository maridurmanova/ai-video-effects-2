"""color-grade — flat footage turns into a cinematic grade with a before/after wipe."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib.core import *

NAME = "color-grade"
DESC = "из плоской картинки в киношный цвет"
TITLE = "цветокор"
SFX = [(0.15, "whoosh")]


def flat(img):
    a = np.asarray(img, np.float32)
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * 0.55
    a = (a - 128) * 0.72 + 128 + 22
    return np.clip(a, 0, 255)


def cinematic(img):
    a = np.asarray(img, np.float32) / 255
    L = a @ np.array([.299, .587, .114], np.float32)
    a = (a - 0.5) * 1.18 + 0.5
    sh = np.clip(1 - L * 1.6, 0, 1)[..., None]
    hi = np.clip((L - 0.45) * 1.8, 0, 1)[..., None]
    a = a + sh * np.array([-0.03, 0.03, 0.07]) + hi * np.array([0.08, 0.03, -0.05])
    g = a.mean(axis=2, keepdims=True)
    a = g + (a - g) * 1.15
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    v = 1 - 0.35 * (((xx - a.shape[1] / 2) / (a.shape[1] * .65)) ** 2 + ((yy - a.shape[0] / 2) / (a.shape[0] * .6)) ** 2)
    a = a * np.clip(v, 0.55, 1)[..., None]
    return np.clip(a * 255, 0, 255)


def _pill(d, xy, text, anchor):
    f = font("mono", 26, 700)
    w = tw(text, f) + 36
    x, y = xy
    x0 = x if anchor == "l" else x - w
    d.rounded_rectangle((x0, y - 26, x0 + w, y + 26), 26, fill=(0, 0, 0, 150))
    d.text((x0 + w / 2, y), text, font=f, fill=(255, 255, 255), anchor="mm")


def render(ctx, tl, ts):
    t = tl
    src, _ = ctx.src(ts, zoom=1.03, anchor=(540, 600), with_mask=False)
    A, B = cinematic(src), flat(src)
    xw = int(W * ease_in_out(prog(t, 0.2, 1.1)))
    out = B.copy()
    out[:, :xw] = A[:, :xw]
    img = Image.fromarray(out.astype(np.uint8))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    if 0 < xw < W:
        d.rectangle((xw - 3, 0, xw + 3, H), fill=(255, 255, 255, 230))
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).rectangle((xw - 10, 0, xw + 10, H), fill=(255, 255, 255, 120))
        ov.alpha_composite(gl.filter(ImageFilter.GaussianBlur(12)))
        d = ImageDraw.Draw(ov)
    if xw < W - 200:
        _pill(d, (W - 50, 1400), "ДО", "r")
    if xw > 260:
        _pill(d, (50, 1400), "ПОСЛЕ", "l")
    o = img.convert("RGBA"); o.alpha_composite(ov)
    return caption(o.convert("RGB"), TITLE, t, 0.9, y=1560)
