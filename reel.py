#!/usr/bin/env python3
"""Showcase reel: hook → six /effects2 commands typed in a chat → code-word poster.

    python3 reel.py my_clip.mp4 -o reel.mp4 --music track.mp3 --word вирусно

Cuts land on the music's beat (--bpm, --offset). The clip's own sound is dropped;
the result has the music plus keyboard / send / sparkle / whoosh / pop sounds.
"""
import argparse, os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from lib.core import *
from lib.ctx import Ctx
from lib import ui, audio
from effects2 import ORDER, load

SRC_SHIFT = {"freeze-frame": 1.7, "glass-graph": 3.6, "color-grade": 1.5}   # take these from a better moment of the clip
DELAY = {"text-behind": 0.75, "over-the-shoulder": 0.3, "tier-list": 0.4,
         "freeze-frame": 0.82, "glass-graph": 0.45, "color-grade": 0.6}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("-o", "--out", default="reel.mp4")
    ap.add_argument("--music"); ap.add_argument("--music-start", type=float, default=0.0)
    ap.add_argument("--bpm", type=float, default=107.67); ap.add_argument("--offset", type=float, default=0.035)
    ap.add_argument("--word", default="вирусно")
    ap.add_argument("--hook", default="", help='opening title "LINE 1|LINE 2"; empty = start straight with the effects')
    ap.add_argument("--sub", default="6 эффектов — одной командой")
    ap.add_argument("--sfx-gain", type=float, default=0.5)
    ap.add_argument("--effects", default=",".join(ORDER))
    ap.add_argument("--preview", type=float)
    a = ap.parse_args()

    ctx = Ctx(a.video)
    mods = [load(n) for n in a.effects.split(",")]
    n = len(mods)
    beat = 60 / a.bpm
    T0 = a.offset + (3 * beat if a.hook else 0)   # optional hook = 3 beats
    SEG = 6 * beat                           # each effect = 6 beats
    TEND = T0 + n * SEG
    total = max(TEND + 4 * beat, TEND + 2.0)
    if a.music:
        mdur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.music]))
        total = max(total, min(mdur - a.music_start, TEND + 4.5))
    span = ctx.clip.duration - 0.15
    SH = 1.45                                # reel time − clip time inside the effect part

    def src_t(t):
        return clamp(t - SH, 0.05, span)

    # phases inside a segment, in seconds
    TY0, TY1, SEND, CHAT, D0, D1, Z0, Z1, EFF = .10, .62, .70, .75, .85, 1.35, 1.40, 1.72, .90

    def cmd_of(m):
        return "/effects2 " + m.NAME

    def popup(s):
        if not s.startswith("/"):
            return None
        part = s.split(" ", 1)[1] if " " in s else ""
        hits = [m for m in mods if part and m.NAME.startswith(part)]
        if hits:
            return [(hits[0].NAME, hits[0].DESC)]
        return [("/effects2", f"{n} видеоэффектов для твоего клипа")]

    print("stills…", flush=True)
    stills = []
    for i, m in enumerate(mods):
        k_full = T0 + i * SEG + Z1 + 0.9
        stills.append((m.NAME, m.render(ctx, 1.6, src_t(k_full + SRC_SHIFT.get(m.NAME, 0)))))
    thumb = ctx.clip.frame(2.0)

    def hook(t):
        img = grade(ctx.clip.frame(t + 0.05), sat=0.9, bright=-55, contrast=1.05)
        l1, l2 = a.hook.split("|")
        q = ease_out(prog(t, 0.0, 0.18))
        s = 1.35 - 0.35 * q
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        f = font("oswald", 190, 700)
        f = font("oswald", int(190 * min(1, 1000 / max(tw(l1, f), tw(l2, f)))), 700)
        d.text((W / 2, 980), l1, font=f, fill=(255, 255, 255), anchor="ms")
        d.text((W / 2, 1180), l2, font=f, fill=CLAY, anchor="ms")
        big = ov.resize((int(W * s), int(H * s)), Image.LANCZOS)
        ov = big.crop((int((big.width - W) / 2), int((big.height - H) / 2), int((big.width + W) / 2), int((big.height + H) / 2)))
        if q < 1:
            ov.putalpha(ov.split()[3].point(lambda v: int(v * q)))
        out = img.convert("RGBA"); out.alpha_composite(ov)
        q2 = ease_out(prog(t, 0.55, 0.3))
        if q2 > 0:
            o2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(o2).text((W / 2, 1290), a.sub, font=font("playfair", 60, 500), fill=(255, 255, 255, int(255 * q2)), anchor="mm")
            out.alpha_composite(o2)
        return out.convert("RGB")

    def poster(t):
        img = Image.new("RGB", (W, H), (26, 26, 25))
        d = ImageDraw.Draw(img)
        q = ease_back(prog(t, 0.0, 0.35))
        title = f"Напиши «{a.word}»"
        f = font("oswald", 130, 700)
        f = font("oswald", int(130 * min(1, 980 / tw(title, f))), 700)
        d.text((W // 2, 250 - 30 * (1 - q)), title, font=f, fill=(255, 255, 255), anchor="mm")
        fp = font("sans", 40, 700)
        s = f"и получи все {n} эффектов"
        pw = tw(s, fp) + 70
        d.rounded_rectangle((W / 2 - pw / 2, 350, W / 2 + pw / 2, 432), 41, fill=CLAY)
        d.text((W // 2, 391), s, font=fp, fill=(255, 255, 255), anchor="mm")
        cols, gap, x0 = 3, 24, 60
        tw_ = (W - 2 * x0 - (cols - 1) * gap) // cols
        th_ = int(tw_ * 16 / 9)
        for i, (lab, im) in enumerate(stills):
            r, c = divmod(i, cols)
            x, y = x0 + c * (tw_ + gap), 500 + r * (th_ + 66)
            p = ease_back(prog(t, 0.12 + i * 0.07, 0.3), 2)
            if p <= 0:
                continue
            paste_scaled(img, im.resize((tw_, th_), Image.LANCZOS), (x + tw_ / 2, y + th_ / 2), p, radius=18)
            if p > 0.8:
                d.text((x + tw_ / 2, y + th_ + 30), lab, font=font("mono", 22, 600), fill=UI_DIM, anchor="mm")
        d.text((W // 2, 1840), ctx.cfg["handle"], font=font("sans", 34, 600), fill=CLAY, anchor="mm")
        return img

    def frame_at(t):
        if t < T0 and a.hook:
            return hook(t)
        if t >= TEND:
            return poster(t - TEND)
        k = int(clamp((t - T0) // SEG, 0, n - 1))
        m = mods[k]
        ts_ = max(0.0, t - T0 - k * SEG)
        cmd = cmd_of(m)
        if ts_ < CHAT:
            nch = int(len(cmd) * clamp((ts_ - TY0) / (TY1 - TY0)))
            s = cmd[:nch]
            key = s[-1] if s and ts_ < TY1 + 0.05 else None
            return ui.compose(s, thumb, popup(s), key)
        tl = ts_ - EFF - DELAY.get(m.NAME, 0.5)
        eff = m.render(ctx, tl, src_t(t + SRC_SHIFT.get(m.NAME, 0)))
        status = f"Монтирую: {m.NAME}…"
        if ts_ < Z0:
            return ui.chat(cmd, thumb, status, eff, ease_in_out(prog(ts_, D0, D1 - D0)), show_card=ts_ >= D0 - 0.05)
        if ts_ < Z1:
            return ui.chat(cmd, thumb, status, eff, 1, zoom=prog(ts_, Z0, Z1 - Z0))
        return eff

    if a.preview is not None:
        frame_at(a.preview).save(a.out)
        return

    # ---- sound design (all times in reel seconds)
    ev = [(0.0 + a.offset, "impact", 0.9), (0.55, "pop", 0.6)] if a.hook else []
    for k, m in enumerate(mods):
        t0 = T0 + k * SEG
        cmd = cmd_of(m)
        for i in range(len(cmd)):
            ev.append((t0 + TY0 + (TY1 - TY0) * (i + 1) / len(cmd), "key", 0.45))
        ev += [(t0 + SEND, "send", 0.8), (t0 + D0, "sparkle", 1.0), (t0 + Z0 - 0.05, "whoosh", 0.8)]
        d0 = t0 + EFF + DELAY.get(m.NAME, 0.5)
        for st, name in m.SFX:
            if d0 + st < t0 + SEG - 0.05:
                ev.append((d0 + st, name, 0.8))
    ev.append((TEND, "impact", 0.9))
    for i in range(n):
        ev.append((TEND + 0.12 + i * 0.07, "pop", 0.6))
    ev = [(t, nm, g * a.sfx_gain) for t, nm, g in ev]
    wav = a.out + ".wav"
    audio.build(total, ev, [(0, total + 1, 1.0)], wav, a.bpm, music_file=a.music, music_start=a.music_start)

    tmp = a.out + ".video.mp4"
    wr = Writer(tmp, crf=14)
    N = int(round(total * FPS))
    for i in range(N):
        wr.write(frame_at(i / FPS))
        if i % 60 == 0:
            print(f"frame {i}/{N}", flush=True)
    wr.close()
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a",
                           "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", a.out])
    os.remove(tmp)
    print("done:", a.out)


if __name__ == "__main__":
    main()
