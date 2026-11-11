---
name: effects2
description: Six talking-head reel effects — /effects2 <name> applies one (text-behind, over-the-shoulder, tier-list, freeze-frame, glass-graph, color-grade) to the user's vertical clip; /effects2 reel builds the showcase reel with music and UI sounds. Use when the user drops a video and types /effects2.
---

# /effects2 — one command, one edit

```
/effects2 text-behind        (+ a video attached or a path)
/effects2 list
/effects2 reel               — showcase: hook → 6 effects typed in a chat → code-word poster
```

Scripts live next to this file. In Claude Code that is `~/.claude/skills/effects2/`; when the skill was
uploaded in the app (Settings → Skills) it is wherever this SKILL.md sits in the sandbox — `cd` there first.
Needs Python 3.10+, ffmpeg and `pip install -r requirements.txt` (add `--break-system-packages` if pip refuses).
The first run downloads a person-segmentation model (~170 MB, once, from github.com).

## Effects

| name | what it does | on-screen text to adapt |
|---|---|---|
| `text-behind` | a huge word rises behind the speaker's head | `WORD` |
| `over-the-shoulder` | slow push-in, two proof cards (before / after, counting up) beside the head | `BEFORE`, `AFTER` |
| `tier-list` | glass S/A/B/C/D ranking fills itself in front of the speaker | `HEADER`, `ITEMS` |
| `freeze-frame` | frame freezes with a flash, background dims, white sticker outline, name tag | `config.json` name / role |
| `glass-graph` | liquid-glass card on the chest, % counts up, green graph climbs | `LABEL`, `FROM`, `TO` |
| `color-grade` | flat footage → cinematic grade with a before/after wipe | — |

All texts are Russian by default and sit at the top of each `effects2/*.py` file.

## How to run it (you, the assistant)

1. Find the clip. If it is 4K, HEVC or >100 MB, make a proxy first:
   `ffmpeg -i in.mov -vf "scale=1080:1920,fps=30" -c:v libx264 -crf 16 -an clip.mp4`
2. Ask once for the name / @handle to show (or read `config.json`) and the words for the cards.
3. **Preview first:** `python3 run.py <effect> clip.mp4 --preview 1.0,2.0,4.0` → show the PNGs, adjust texts on request.
4. Render: `python3 run.py <effect> clip.mp4 -o out.mp4` (keeps the voice; `--no-voice --music` for music only;
   `--start 3` starts the effect at 3 s).
5. Showcase reel: `python3 reel.py clip.mp4 -o reel.mp4 --music track.mp3 --word <code word>`
   (`--bpm` / `--offset` set the beat grid, `--hook "LINE 1|LINE 2"` the opening title, `--sfx-gain` the UI-sound level).
6. Before handing over: look at a few frames and run `ffmpeg -i out.mp4 -vf blackdetect -f null -`.
