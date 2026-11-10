"""Drawing helpers: Spectra 6 colours, fonts, text wrapping, cached HTTP."""
import os
import threading
import time

import requests
from PIL import Image, ImageDraw, ImageFont

from . import store, themes

W, H = 800, 480

# Pure Spectra 6 colours -> shown by the panel without dithering
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
COLORS = {"black": BLACK, "white": WHITE, "red": RED, "yellow": YELLOW,
          "green": GREEN, "blue": BLUE}

_font_cache = {}
_tl = threading.local()


def clear_font_cache():
    _font_cache.clear()
    _cmaps.clear()


def set_theme(name):
    """Active display theme for the current thread (set by the plugin Context)."""
    _tl.theme = name if name in themes.THEMES else themes.DEFAULT


def theme():
    return getattr(_tl, "theme", themes.DEFAULT)


def accent():
    return COLORS[themes.get(theme())["accent"]]


def font(kind, size):
    """Theme-aware font. Custom fonts: data/fonts/<theme>/<kind>.ttf or data/fonts/<kind>.ttf."""
    key = (theme(), kind, size)
    if key in _font_cache:
        return _font_cache[key]
    path = themes.font_path(theme(), kind, store.FONT_DIR)
    # size tweaks are tuned for the design's own fonts – not for the DejaVu fallback
    if kind != "symbols" and path and path.startswith(os.path.join(store.FONT_DIR, theme(), "")):
        size = max(6, int(round(size * themes.size_factor(theme()))))
    f = ImageFont.truetype(path, size) if path else ImageFont.load_default(size)
    _font_cache[key] = f
    return f


_cmaps = {}


def _has_glyphs(f, text):
    """True if font f covers every character (needs fontTools; assumes yes without it)."""
    path = getattr(f, "path", None)
    if not path:
        return True
    cmap = _cmaps.get(path)
    if cmap is None:
        try:
            from fontTools.ttLib import TTFont
            cmap = set(TTFont(path, fontNumber=0, lazy=True).getBestCmap())
        except Exception:
            cmap = False
        _cmaps[path] = cmap
    return cmap is False or all(ord(c) in cmap or c in "\n\r\t" for c in text)


class Draw(ImageDraw.ImageDraw):
    """ImageDraw that falls back to DejaVu for characters a theme font lacks (→ ↑ ≈ …)."""

    def text(self, xy, text, fill=None, font=None, anchor=None, *args, **kwargs):
        if font is None or not text or "\n" in text or _has_glyphs(font, text):
            return super().text(xy, text, fill, font, anchor, *args, **kwargs)
        fb = ImageFont.truetype(themes.font_path("classic", "sans", store.FONT_DIR), int(font.size))
        runs, cur, cur_f = [], "", None
        for ch in text:
            fnt = font if _has_glyphs(font, ch) else fb
            if fnt is not cur_f and cur:
                runs.append((cur, cur_f))
                cur = ""
            cur, cur_f = cur + ch, fnt
        runs.append((cur, cur_f))
        total = sum(self.textlength(t, font=f) for t, f in runs)
        anchor = anchor or "la"
        x, y = xy
        x -= total / 2 if anchor[0] == "m" else total if anchor[0] == "r" else 0
        for t, f in runs:
            super().text((x, y), t, fill, f, "l" + anchor[1], *args, **kwargs)
            x += self.textlength(t, font=f)


def canvas(color=WHITE):
    img = Image.new("RGB", (W, H), color)
    d = Draw(img)
    if store.get()["display"].get("crisp_text", True):
        d.fontmode = "1"   # no anti-aliasing -> crisp text on e-ink
    return img, d


def text_w(d, text, f):
    l, _, r, _ = d.textbbox((0, 0), text, font=f)
    return r - l


def wrap(d, text, f, max_w):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        if not words:
            lines.append("")
            continue
        for w in words:
            test = (cur + " " + w).strip()
            if text_w(d, test, f) <= max_w or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit_text(d, text, kind, box_w, box_h, max_size=96, min_size=18, spacing=1.25):
    """Find the largest font size at which the wrapped text fits the box."""
    size = max_size
    while size >= min_size:
        f = font(kind, size)
        lines = wrap(d, text, f, box_w)
        lh = int(size * spacing)
        if len(lines) * lh <= box_h and all(text_w(d, l, f) <= box_w for l in lines):
            return f, lines, lh
        size -= 2
    f = font(kind, min_size)
    return f, wrap(d, text, f, box_w), int(min_size * spacing)


def draw_lines(d, lines, f, lh, x, y, w, fill=BLACK, align="center"):
    for i, line in enumerate(lines):
        tw = text_w(d, line, f)
        if align == "center":
            lx = x + (w - tw) // 2
        elif align == "right":
            lx = x + w - tw
        else:
            lx = x
        d.text((lx, y + i * lh), line, font=f, fill=fill)


def text_center(d, text, f, cx, y, fill=BLACK):
    d.text((cx - text_w(d, text, f) // 2, y), text, font=f, fill=fill)


# --- theme-aware decorations ------------------------------------------------------
_CONFETTI = [RED, YELLOW, GREEN, BLUE]


def frame(d, inset=22, color=None):
    """Decorative border in the style of the active theme."""
    t = theme()
    from . import theme_draw
    if theme_draw.frame(t, d, inset, color or BLACK):
        return
    col = color or BLACK
    x0, y0, x1, y1 = inset, inset, W - 1 - inset, H - 1 - inset
    if t == "modern":
        d.rectangle((0, 0, W, 9), fill=accent())
    elif t == "playful":
        d.rounded_rectangle((x0, y0, x1, y1), radius=28, outline=col, width=3)
        step, i = 26, 0
        for x in range(x0 + 40, x1 - 30, step):
            for y in (y0 - 9, y1 + 9):
                c = _CONFETTI[i % 4]
                d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=c)
                i += 1
    else:
        d.rectangle((x0, y0, x1, y1), outline=col, width=2)
        d.rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), outline=col, width=1)


def header(d, title, subtitle=None, x=40, color=None):
    """Title (+ subtitle) at the top-left in the theme's style. Returns the y below it."""
    t = theme()
    from . import theme_draw
    y = theme_draw.header(t, d, title, subtitle, x, color)
    if y is not None:
        return y
    if t == "modern":
        d.rectangle((x, 30, x + 7, 66), fill=accent())
        d.text((x + 20, 26), title, font=font("sans-bold", 32), fill=color or BLACK)
        if subtitle:
            d.text((x + 21, 70), subtitle.upper(), font=font("sans", 13), fill=BLACK)
            return 104
        return 84
    if t == "playful":
        f = font("serif-bold", 28)
        tw = text_w(d, title, f)
        d.rounded_rectangle((x - 8, 20, x + tw + 22, 64), radius=22, fill=color or accent())
        d.text((x + 7, 25), title, font=f, fill=WHITE)
        for k, c in enumerate(_CONFETTI[1:]):
            cx = x + tw + 44 + k * 18
            d.ellipse((cx - 5, 38 - 5 + (k % 2) * 8, cx + 5, 38 + 5 + (k % 2) * 8), fill=c)
        if subtitle:
            d.text((x, 72), subtitle, font=font("serif-italic", 18), fill=BLACK)
            return 108
        return 80
    d.text((x, 28), title, font=font("serif", 34), fill=color or BLACK)
    if subtitle:
        d.text((x, 70), subtitle, font=font("serif-italic", 18), fill=BLACK)
        return 104
    return 76


def footer(d, text, x=40):
    d.text((x, H - 30), text, font=font("sans", 13), fill=BLACK)


def message_screen(title, text=""):
    """Uniform notice / error screen."""
    img, d = canvas()
    frame(d, inset=16)
    f, lines, lh = fit_text(d, title, "serif-bold", W - 160, 140, 54, 24)
    draw_lines(d, lines, f, lh, 80, 150, W - 160)
    if text:
        f2, l2, lh2 = fit_text(d, text, "sans", W - 200, 120, 26, 16)
        draw_lines(d, l2, f2, lh2, 100, 160 + len(lines) * lh + 20, W - 200)
    return img


def postprocess(img, name=None, remap=True):
    """Apply a design's colour remap (dark designs) and background pattern after rendering."""
    t = themes.get(name or theme())
    if not remap or not t.get("remap"):
        return img
    import numpy as np
    a = np.array(img.convert("RGB"))
    masks = {src: np.all(a == np.array(COLORS[src], dtype=a.dtype), axis=-1) for src in t["remap"]}
    for src, dst in t["remap"].items():
        a[masks[src]] = COLORS[dst]
    if t.get("pattern") == "grid":
        bg = np.all(a == np.array(COLORS[t["remap"]["white"]], dtype=a.dtype), axis=-1)
        grid = np.zeros(bg.shape, dtype=bool)
        grid[::20, ::4] = True
        grid[::4, ::20] = True
        a[bg & grid] = COLORS["white"]
    return Image.fromarray(a)


# --- HTTP with a small cache --------------------------------------------------
_http_cache = {}
_http_lock = threading.Lock()
UA = {"User-Agent": "inkyframe/2.0 (+https://github.com/inkyframe)"}


def get_json(url, ttl=600, params=None, headers=None):
    key = (url, tuple(sorted((params or {}).items())))
    now = time.time()
    with _http_lock:
        hit = _http_cache.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1]
    h = dict(UA)
    h.update(headers or {})
    r = requests.get(url, params=params, headers=h, timeout=15)
    r.raise_for_status()
    data = r.json()
    with _http_lock:
        _http_cache[key] = (now, data)
    return data


def get_text(url, ttl=600, params=None, headers=None):
    key = ("text", url, tuple(sorted((params or {}).items())))
    now = time.time()
    with _http_lock:
        hit = _http_cache.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1]
    h = dict(UA)
    h.update(headers or {})
    r = requests.get(url, params=params, headers=h, timeout=20)
    r.raise_for_status()
    text = r.content.decode("utf-8", errors="replace")
    with _http_lock:
        _http_cache[key] = (now, text)
    return text


def get_image(url, ttl=3600):
    from io import BytesIO
    key = ("img", url)
    now = time.time()
    with _http_lock:
        hit = _http_cache.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1].copy()
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content)).convert("RGB")
    with _http_lock:
        _http_cache[key] = (now, img)
    return img.copy()


def cover_fit(img, w, h):
    """Crop an image to fill w×h, centred."""
    sw, sh = img.size
    scale = max(w / sw, h / sh)
    nw, nh = int(sw * scale + 0.5), int(sh * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def punch_for_eink(img, saturation=1.35, contrast=1.15):
    """Boost photos a little – Spectra colours are more muted than a phone screen."""
    from PIL import ImageEnhance
    img = ImageEnhance.Color(img).enhance(saturation)
    return ImageEnhance.Contrast(img).enhance(contrast)
