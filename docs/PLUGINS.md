# Writing a plugin

A plugin is **one Python file** with one class. It decides what is drawn on the 800×480 panel.
The web app, rotation, interrupts and settings form are handled by inkyframe – you only draw.

You don't need a Raspberry Pi to develop: everything renders to PNG on any computer.

## 1. Set up (any computer)

```bash
git clone https://github.com/charwege/inkyframe.git && cd inkyframe
python3 -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install flask requests pillow chess pytest
python -m inkyframe.dev new moonquote               # creates data/plugins/moonquote.py
python -m inkyframe.dev render moonquote --sample   # -> preview/moonquote.png
```

Edit the file, re-run `render`, look at the PNG. Repeat.

## 2. Anatomy

```python
from inkyframe.plugin import Plugin, Setting


class MoonQuote(Plugin):
    id = "moonquote"                          # unique, lowercase, letters/digits/_
    name = {"en": "Moon Quote", "de": "Mondspruch"}   # or a plain string
    icon = "☾"                                # one character for the web app
    description = "A quote that matches the moon phase."
    author = "your-github-name"

    settings = [                              # -> form in the web app, values in ctx.settings
        Setting("signature", "text", "Signature", default=""),
        Setting("frame", "bool", "Draw a frame", default=True),
    ]
    refresh_minutes = 0                       # 0 = only when content_key() changes

    def content_key(self, ctx):               # cheap; a new value triggers a redraw
        return f"{ctx.today}|{ctx.lang}|{sorted(ctx.settings.items())}"

    def sample(self, ctx):                    # offline demo data for previews + CI
        return {"text": "Even the moon has phases."}

    def render(self, ctx, data=None):         # must return an 800×480 RGB image
        text = (data or self.fetch(ctx))["text"]
        img, d = ctx.canvas()                 # PIL Image + ImageDraw, white background
        if ctx.settings["frame"]:
            d.rectangle((20, 20, ctx.W - 21, ctx.H - 21), outline=ctx.BLACK, width=2)
        ctx.fit_center(d, text, kind="serif-bold", max_size=72)
        return img

    def fetch(self, ctx):
        return ctx.fetch_json("https://example.org/api/quote", ttl=3600)
```

## 3. The `ctx` object

| | |
|---|---|
| `ctx.settings` | this plugin's settings (defaults merged with what the user saved) |
| `ctx.now`, `ctx.today` | current datetime / date (overridable for previews: `--time 13:37`) |
| `ctx.lang` | display language, `"en"` or `"de"` |
| `ctx.t("Hello", "Hallo", name=…)` | pick the text for the display language (with `str.format`) |
| `ctx.location` | `{"name", "lat", "lon", "holidays"}` from the general settings |
| `ctx.W`, `ctx.H` | 800, 480 |
| `ctx.BLACK … ctx.BLUE`, `ctx.COLORS` | the six panel colours – use these for crisp results |
| `ctx.canvas(color=WHITE)` | new image + draw object |
| `ctx.font(kind, size)` | `serif`, `serif-bold`, `serif-italic`, `sans`, `sans-bold`, `sans-cond`, `symbols` |
| `ctx.fit_center(d, text, box=…)` | wrap + shrink text to fit and centre it |
| `ctx.fit_text`, `ctx.wrap`, `ctx.draw_lines`, `ctx.text_center`, `ctx.text_w` | lower-level text helpers |
| `ctx.fetch_json(url, ttl=…, params=…)` | cached HTTP GET → JSON |
| `ctx.fetch_text(url, ttl=…, params=…)` | cached HTTP GET → text (CSV, iCal …) |
| `ctx.fetch_image(url)` | cached image download |
| `ctx.cover_fit(img, w, h)`, `ctx.punch(img)` | crop to fill / boost colours for photos |
| `ctx.header(d, title, subtitle)`, `ctx.footer(d, text)`, `ctx.frame(d)` | title, source line and border in the chosen design |
| `ctx.ACCENT`, `ctx.theme` | accent colour and name of the chosen design |
| `ctx.qr(d, text, x, y, size)` | draw a QR code (built in, no dependency) |
| `ctx.message(title, text)` | standard notice screen ("not configured yet" etc.) |
| `ctx.save_settings(key=value)` | persist values such as OAuth tokens (not shown in the form) |
| `ctx.load_state()`, `ctx.save_state(dict)` | private JSON storage in `data/state/<id>.json` (logs, history …) |

## 4. Settings types

`text`, `textarea`, `number` (`min`, `max`), `bool`, `select` (`options=[(value, label), …]`),
`secret` (masked in the app), `date`, `time`, `color` (the six panel colours),
`info` (read-only text) and `action` – a button that calls `action_<key>(self, ctx, value)`.
With `input="placeholder"` the button gets a text field whose content is passed as `value`.
An action may return `{"message": "..."}`, `{"open_url": "..."}` or `{"link": "..."}`.

## 5. Optional hooks

| Hook | Use |
|---|---|
| `refresh_minutes` / a setting named `refresh_minutes` | redraw periodically (weather, prices) |
| `can_interrupt = True` + `wants_display(ctx)` | take over the screen when something happens (Spotify playing, doorbell, alarm). The user enables it under *Rotation*. Called every 15 s – keep it cheap and cached. |
| `status(ctx)` | one line shown in the plugin panel ("Connected", "Last update …") |
| `poll_minutes = N` + `poll(ctx)` | background job, runs even while the plugin is not on screen (e.g. recording a solar curve) |
| `extra_settings(ctx)` + `action(ctx, key, value)` | settings generated from the current config, e.g. one "tick" button per habit |

Shared helpers for bundled plugins live in `inkyframe/plugins/_calendar.py` (names, holidays, moon)
and `inkyframe/plugins/_ical.py` (calendar feeds).

## 6. Designs (themes)

Users pick *Classic*, *Modern* or *Playful*. Your plugin follows automatically if you
- request fonts by **kind** (`ctx.font("serif-bold", 40)`) – each design maps kinds to its own typeface,
- use `ctx.header()`, `ctx.footer()` and `ctx.frame()` instead of drawing your own title bars and borders,
- use `ctx.ACCENT` for decorative highlights (red in classic/playful, blue in modern) and the fixed colours only
  where the colour *means* something (red warning, green "good").

Dark designs (Art déco, Pixel, Blueprint, Chalkboard) are made by recolouring your finished image
(white → black/blue, black → white, blue → yellow/green). Draw text in `ctx.BLACK` on the white canvas and it
works everywhere. Plugins that show photos set `theme_remap = False` so pictures stay untouched.
`ctx.theme` tells you the active design if you want to go further. Characters a design font lacks (→ ↑ ≈)
are drawn with DejaVu automatically. Preview a design: `python -m inkyframe.dev gallery --sample --theme blueprint` (`python -m inkyframe.fonts` fetches the fonts first).

## 7. Designing for e-ink

* **Use the six pure colours.** Anything else gets dithered. Text stays crisp with the default
  "crisp text" setting.
* **A refresh takes ~25–30 s and flashes.** Make `content_key` change as rarely as possible
  (Spotify only redraws on a new album, the word clock every 5 minutes).
* **Fail gracefully.** Raise an exception when data is missing – the engine keeps the previous image
  and shows the error in the app. Never block for long; use timeouts (`fetch_json` has one).
* **Always provide `sample()`** so others (and CI) can preview your plugin offline.
* **Translate** with `ctx.t(en, de)`. German is passed inline; the other languages are looked up in `inkyframe/locales/<code>.py` by the English text (missing entries fall back to English, `pytest` lists them). Use `ctx.date()` and `ctx.num()` for dates and numbers so they follow the language.

## 8. Install & share

* **Just for you:** put the file in `data/plugins/` on the Pi and run
  `sudo systemctl restart inkyframe`. It appears in the app with a *user* tag.
* **For everyone:** move it to `inkyframe/plugins/`, run `python -m inkyframe.dev check` and
  `pytest`, add a preview image to `docs/img/` and open a pull request – see
  [CONTRIBUTING.md](../CONTRIBUTING.md). CI renders your plugin in both languages and attaches the
  images to the PR.
