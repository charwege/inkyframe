"""Drawing toolkit for the studio designs' signature layouts.

Layouts are written like the HTML mockups they come from: positions in CSS pixels,
font sizes in px, `line-height`, `letter-spacing`, text-transform … so a design can be
ported from a mockup almost line by line. See inkyframe/designs/ for the layouts.
"""
import math
import os
import re

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import gfx, store, themes
from .studio_fonts import FACES

W, H = 800, 480
K, Wh, R, Y, G, B = gfx.BLACK, gfx.WHITE, gfx.RED, gfx.YELLOW, gfx.GREEN, gfx.BLUE
_fonts = {}
# OpenType features per role (Libre Caslon turns "st" into a long-s ligature by default)
FEATURES = {"lc400": ["-liga", "-dlig", "-hlig"], "lc400i": ["-liga", "-dlig", "-hlig"]}


def _r(v):
    return int(math.floor(v + 0.5))


def face_path(theme, role):
    """data/fonts/<theme>/st-<role>.ttf, else the theme's base kind (via themes.font_path)."""
    p = os.path.join(store.FONT_DIR, theme, f"st-{role}.ttf")
    if os.path.exists(p):
        return p, True
    kind = FACES.get(theme, {}).get(role, (None, None, None, "sans"))[3]
    return themes.font_path(theme, kind, store.FONT_DIR), False


class Canvas:
    """A 800×480 page with CSS-like text helpers. All y values are the TOP of a line box."""

    def __init__(self, theme, bg=Wh):
        self.theme = theme
        self.img, self.d = gfx.canvas(bg)
        self.bg = bg

    # ---------------------------------------------------------------- fonts & metrics
    def font(self, role, size):
        key = (self.theme, role, int(round(size)))
        f = _fonts.get(key)
        if f is None:
            path, own = face_path(self.theme, role)
            f = ImageFont.truetype(path, max(6, int(round(size))))
            f.own = own
            _fonts[key] = f
        return f

    def line_h(self, role, size, lh=None):
        """CSS line-height: number (factor) or None for 'normal'."""
        if lh is not None:
            return size * lh
        a, dsc = self.font(role, size).getmetrics()
        return a + dsc

    def tw(self, text, role, size, track=0.0):
        if not text:
            return 0.0
        f = self.font(role, size)
        if not track:
            return self.d.textlength(text, font=f, features=FEATURES.get(role))
        return sum(_adv(self.d, c, f) for c in text) + track * len(text)

    def _baseline(self, top, role, size, lh):
        f = self.font(role, size)
        a, dsc = f.getmetrics()
        L = self.line_h(role, size, lh)
        return top + (L - (a + dsc)) / 2 + a

    # ---------------------------------------------------------------- text
    def text(self, x, top, text, role, size, fill=K, track=0.0, lh=None, align="l",
             upper=False, stroke=0, stroke_fill=None, draw=None):
        """One line. x is the left edge (align l), centre (c) or right edge (r). Returns line height."""
        if upper:
            text = text.upper()
        d = draw or self.d
        f = self.font(role, size)
        w = self.tw(text, role, size, track) - (track if track else 0)
        x0 = x if align == "l" else x - w / 2 if align == "c" else x - w
        base = self._baseline(top, role, size, lh)
        kw = {"stroke_width": stroke, "stroke_fill": stroke_fill} if stroke else {}
        if FEATURES.get(role):
            kw["features"] = FEATURES[role]
        if not track:
            d.text((x0, base), text, font=f, fill=fill, anchor="ls", **kw)
        else:
            for c in text:
                d.text((x0, base), c, font=f, fill=fill, anchor="ls", **kw)
                x0 += _adv(d, c, f) + track
        return self.line_h(role, size, lh)

    def wrap(self, text, role, size, width, track=0.0):
        lines = []
        for para in text.split("\n"):
            cur = ""
            for w in para.split():
                t = (cur + " " + w).strip()
                if not cur or self.tw(t, role, size, track) <= width:
                    cur = t
                else:
                    lines.append(cur)
                    cur = w
            lines.append(cur)
        return lines

    def fit(self, text, role, max_size, width, height, lh=1.2, track=0.0, min_size=14, upper=False,
            track_scale=True):
        """Largest size ≤ max_size whose wrapped lines fit width × height. Returns (size, lines, line_h, track)."""
        if upper:
            text = text.upper()
        size = max_size
        while True:
            tr = track * size / max_size if track_scale else track
            lines = self.wrap(text, role, size, width, tr)
            L = self.line_h(role, size, lh)
            ok = len(lines) * L <= height + 0.5 and all(self.tw(l, role, size, tr) - tr <= width + 0.5 for l in lines)
            if ok or size <= min_size:
                return size, lines, L, tr
            size -= 1

    def para(self, x, top, width, lines, role, size, L, fill=K, track=0.0, align="l", highlight=None,
             hfill=R, underline=None):
        """Draw wrapped lines; highlight = word to colour. Returns total height."""
        y = top
        for line in lines:
            xx = x if align == "l" else x + width / 2 if align == "c" else x + width
            if highlight and highlight in line.split(" ") or (highlight and any(
                    _clean(w) == _clean(highlight) for w in line.split(" "))):
                self.rich_line(xx, y, line, role, size, L, fill, track, align, highlight, hfill, underline)
            else:
                self.text(xx, y, line, role, size, fill, track, lh=L / size, align=align)
            y += L
        return y - top

    def rich_line(self, x, top, line, role, size, L, fill, track, align, word, hfill, underline):
        parts = line.split(" ")
        total = self.tw(line, role, size, track) - track
        x0 = x if align == "l" else x - total / 2 if align == "c" else x - total
        sp = self.tw(" ", role, size, track)
        for i, p in enumerate(parts):
            hit = _clean(p) == _clean(word)
            col = hfill if hit else fill
            self.text(x0, top, p, role, size, col, track, lh=L / size)
            w = self.tw(p, role, size, track) - track
            if hit and underline:
                base = self._baseline(top, role, size, L / size)
                self.dashed((x0, base + underline, x0 + w, base + underline), hfill, 1, 4, 3)
            x0 += w + track + sp

    def last_line_end(self, x, lines, role, size, track=0.0):
        return x + self.tw(lines[-1], role, size, track) - track if lines else x

    # ---------------------------------------------------------------- shapes
    def rect(self, box, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        a, b, c, d = _r(x0), _r(y0), max(_r(x0), _r(x1) - 1), max(_r(y0), _r(y1) - 1)
        self.d.rectangle((a, b, c, d), fill=fill, outline=outline, width=width)

    def rrect(self, box, r, fill=None, outline=None, width=1):
        x0, y0, x1, y1 = box
        self.d.rounded_rectangle((_r(x0), _r(y0), max(_r(x0), _r(x1) - 1), max(_r(y0), _r(y1) - 1)), r,
                                 fill=fill, outline=outline, width=width)

    def hline(self, x0, x1, y, fill=K, width=1):
        self.rect((x0, y, x1, y + width), fill=fill)

    def vline(self, x, y0, y1, fill=K, width=1):
        self.rect((x, y0, x + width, y1), fill=fill)

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse(tuple(round(v) for v in box), fill=fill, outline=outline, width=width)

    def circle(self, cx, cy, r, fill=None, outline=None, width=1):
        self.ellipse((cx - r, cy - r, cx + r, cy + r), fill, outline, width)

    def poly(self, pts, fill=None, outline=None, width=1):
        pts = [(round(x), round(y)) for x, y in pts]
        if fill is not None:
            self.d.polygon(pts, fill=fill)
        if outline is not None:
            self.stroke(pts + [pts[0]], outline, width)

    def stroke(self, pts, fill, width=1, cap=True):
        """Polyline with round joins/caps."""
        pts = [(x, y) for x, y in pts]
        if len(pts) < 2:
            return
        self.d.line(pts, fill=fill, width=max(1, round(width)), joint="curve")
        if cap and width > 2:
            r = width / 2
            for x, y in (pts[0], pts[-1]):
                self.d.ellipse((x - r + .5, y - r + .5, x + r - .5, y + r - .5), fill=fill)

    def dashed(self, line, fill, width=1, dash=6, gap=4):
        x0, y0, x1, y1 = line
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        s = 0.0
        while s < L:
            e = min(L, s + dash)
            self.d.line((x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e), fill=fill, width=width)
            s = e + gap

    def path(self, d, stroke=None, width=1, fill=None, dx=0, dy=0, sx=1.0, sy=None, closed_fill=True):
        """Draw an SVG path string (M L H V Q T C A Z, absolute and relative)."""
        sy = sx if sy is None else sy
        for pts, closed in svg_path(d):
            pts = [(dx + x * sx, dy + y * sy) for x, y in pts]
            if fill is not None and (closed or closed_fill) and len(pts) > 2:
                self.d.polygon([(round(x), round(y)) for x, y in pts], fill=fill)
            if stroke is not None:
                self.stroke(pts + ([pts[0]] if closed else []), stroke, width * sx)

    def diamond(self, cx, cy, s, fill):
        h = s * math.sqrt(2) / 2
        self.poly([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)], fill=fill)

    # ---------------------------------------------------------------- compositing
    def layer(self, w, h, bg=None):
        """Transparent sub-canvas (for rotated labels etc.)."""
        img = Image.new("RGBA", (int(math.ceil(w)), int(math.ceil(h))), bg or (0, 0, 0, 0))
        d = gfx.Draw(img)
        d.fontmode = self.d.fontmode
        return img, d

    def paste_rotated(self, img, cx, cy, deg):
        r = img.rotate(deg, resample=Image.NEAREST, expand=True)
        self.img.paste(r, (round(cx - r.width / 2), round(cy - r.height / 2)), r)

    def outline_text(self, x, top, text, role, size, fill, lh=None, ring=2, track=0.0):
        """-webkit-text-stroke with a transparent fill: only the outline is drawn."""
        f = self.font(role, size)
        m = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(m)
        md.fontmode = "1"
        base = self._baseline(top, role, size, lh)
        xx = x
        for c in (text if track else [text]):
            md.text((xx, base), c, font=f, fill=255, anchor="ls")
            xx += md.textlength(c, font=f) + track
        k = 2 * (ring // 2) + 1
        outer = m.filter(ImageFilter.MaxFilter(k))
        inner = m.filter(ImageFilter.MinFilter(k))
        ringmask = Image.fromarray(__import__("numpy").array(outer, dtype="int16").__sub__(
            __import__("numpy").array(inner, dtype="int16")).clip(0, 255).astype("uint8"))
        self.img.paste(fill, (0, 0, W, H), ringmask.point(lambda v: 255 if v > 127 else 0))

    def finish(self):
        self.img.info["studio"] = True       # tells the pipeline not to recolour this image
        return self.img


def _adv(d, ch, f):
    """Advance of one character, measured with the fallback font if the design font lacks it."""
    if gfx._has_glyphs(f, ch):
        return d.textlength(ch, font=f)
    fb = ImageFont.truetype(themes.font_path("classic", "sans", store.FONT_DIR), int(f.size))
    return d.textlength(ch, font=fb)


def _clean(w):
    return re.sub(r"[^\w]", "", w.lower())


def longest_word(text):
    words = [_clean(w) for w in text.split()]
    words = [w for w in words if len(w) >= 4]
    if not words:
        return None
    best = max(words, key=len)
    for w in text.split():
        if _clean(w) == best:
            return w
    return None


# ------------------------------------------------------------------ SVG path flattening
_TOK = re.compile(r"[MmLlHhVvQqTtCcAaZz]|-?\d*\.?\d+(?:e-?\d+)?")


def svg_path(d, steps=24):
    """Flatten an SVG path into [(points, closed)]."""
    toks = _TOK.findall(d)
    out, pts = [], []
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    lcx = lcy = None          # last control point (for T / smooth)
    prev = None

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                if pts:
                    out.append((pts, True))
                pts = []
                x, y = sx, sy
                prev = "Z"
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            nx, ny = num(), num()
            if rel:
                nx += x
                ny += y
            if pts:
                out.append((pts, False))
            pts = [(nx, ny)]
            x, y, sx, sy = nx, ny, nx, ny
            cmd = "l" if rel else "L"
            lcx = None
        elif c == "L":
            nx, ny = num(), num()
            if rel:
                nx += x
                ny += y
            pts.append((nx, ny))
            x, y = nx, ny
            lcx = None
        elif c == "H":
            nx = num() + (x if rel else 0)
            pts.append((nx, y))
            x = nx
            lcx = None
        elif c == "V":
            ny = num() + (y if rel else 0)
            pts.append((x, ny))
            y = ny
            lcx = None
        elif c in "QT":
            if c == "Q":
                qx, qy = num(), num()
                if rel:
                    qx += x
                    qy += y
            else:
                qx, qy = (2 * x - lcx, 2 * y - lcy) if lcx is not None and prev in "QT" else (x, y)
            nx, ny = num(), num()
            if rel:
                nx += x
                ny += y
            for k in range(1, steps + 1):
                s = k / steps
                pts.append(((1 - s) ** 2 * x + 2 * (1 - s) * s * qx + s * s * nx,
                            (1 - s) ** 2 * y + 2 * (1 - s) * s * qy + s * s * ny))
            lcx, lcy = qx, qy
            x, y = nx, ny
        elif c == "C":
            c1x, c1y, c2x, c2y, nx, ny = (num() for _ in range(6))
            if rel:
                c1x += x
                c1y += y
                c2x += x
                c2y += y
                nx += x
                ny += y
            for k in range(1, steps + 1):
                s = k / steps
                m = 1 - s
                pts.append((m ** 3 * x + 3 * m * m * s * c1x + 3 * m * s * s * c2x + s ** 3 * nx,
                            m ** 3 * y + 3 * m * m * s * c1y + 3 * m * s * s * c2y + s ** 3 * ny))
            lcx = None
            x, y = nx, ny
        elif c == "A":
            rx, ry, rot, large, sweep, nx, ny = (num() for _ in range(7))
            if rel:
                nx += x
                ny += y
            pts += _arc(x, y, rx, ry, rot, int(large), int(sweep), nx, ny)
            x, y = nx, ny
            lcx = None
        prev = c
    if pts:
        out.append((pts, False))
    return out


def _arc(x1, y1, rx, ry, phi, fa, fs, x2, y2, steps=48):
    """SVG endpoint arc -> points (spec F.6.5)."""
    phi = math.radians(phi)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0, num / den)) * (-1 if fa == fs else 1)
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    out = []
    for k in range(1, steps + 1):
        t = t1 + dt * k / steps
        out.append((cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp,
                    cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp))
    return out


# ------------------------------------------------------------------ shared data helpers
ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
         (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def roman(n):
    s = ""
    for v, r in ROMAN:
        while n >= v:
            s += r
            n -= v
    return s
