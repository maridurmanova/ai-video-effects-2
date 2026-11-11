# ai-video-effects-2 · `/effects2`

Шесть эффектов для разговорных рилс. Каждый — одна команда, без монтажки и таймлайна.
Сначала ты видишь кадры-превью, рендер идёт только после твоего «да».

| команда | что получится |
|---|---|
| `/effects2 text-behind` | огромное слово встаёт за твоей головой |
| `/effects2 over-the-shoulder` | камера наезжает, у головы появляются карточки «до / после» |
| `/effects2 tier-list` | стеклянный рейтинг S–D заполняется сам |
| `/effects2 freeze-frame` | стоп-кадр со вспышкой, белая обводка и плашка с именем |
| `/effects2 glass-graph` | стеклянная карточка на груди, график растёт |
| `/effects2 color-grade` | из плоской картинки в киношный цвет со шторкой «до / после» |
| `/effects2 reel` | шоу-рилс со всеми эффектами под твою музыку |

## Установка

**Проще всего:** скачай [effects2-skill.zip](https://github.com/maridurmanova/ai-video-effects-2/raw/main/effects2-skill.zip)
и добавь его в настройках ассистента: Настройки → Персонализация → Скиллы → «Добавить скилл».

**На своём компьютере** (быстрее рендер):

```bash
git clone https://github.com/maridurmanova/ai-video-effects-2 ~/.claude/skills/effects2
pip install -r ~/.claude/skills/effects2/requirements.txt
```

Нужны Python 3.10+ и ffmpeg. При первом запуске один раз скачается модель, которая вырезает человека из кадра (~170 МБ).

## Вручную

```bash
cd ~/.claude/skills/effects2
python3 run.py list
python3 run.py text-behind my_clip.mp4 --preview 1,2,4
python3 run.py text-behind my_clip.mp4 -o out.mp4
python3 reel.py my_clip.mp4 -o reel.mp4 --music track.mp3 --word вирусно
```

Имя, @ник и подпись под именем — в `config.json`. Остальные тексты лежат в начале файлов `effects2/*.py`.
Звуки интерфейса синтезируются кодом. Шрифты Oswald, Playfair Display, Montserrat, JetBrains Mono (SIL OFL).

---
[@maria.aiart](https://instagram.com/maria.aiart) · AI без хаоса
