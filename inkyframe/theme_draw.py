"""Headers and frames of the studio designs (Bauhaus, Newspaper, Art déco …).

Everything is drawn in the normal light palette; dark designs are produced afterwards by
gfx.postprocess (e.g. black -> white, white -> black). Draw "ink" in BLACK, decoration in
the accent colour, and it comes out right in every design.
Each function returns None for designs it does not handle (classic/modern/playful live in gfx).
"""
import datetime as dt
import math
import random

from . import gfx
from .gfx import BLACK, BLUE, GREEN, H, RED, W, WHITE, YELLOW


def _diamond(d, cx, cy, r, fill):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def _sprig(d, x, y, s, flip=1, col=GREEN):
    """Small botanical twig: stem + three leaves."""
    d.line((x, y, x + flip * 4 * s, y - 26 * s), fill=col, width=max(2, int(2 * s)))
    for k, (lx, ly, side) in enumerate(((1, -8, 1), (2, -15, -1), (3.4, -24, 1))):
        bx, by = x + flip * lx * s, y + ly * s
        tx, ty = bx + flip * side * 11 * s, by - 6 * s
        d.polygon([(bx, by), ((bx + tx) / 2 + flip * side * 2 * s, by - 7 * s), (tx, ty),
                   ((bx + tx) / 2, by + 2 * s)], outline=col, fill=None)


def _wobbly_line(d, pts, fill, width, seed=1, amp=2.0):
    rnd = random.Random(seed)
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) // 18))
        for i in range(n):
            t = i / n
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp), y0 + (y1 - y0) * t + rnd.uniform(-amp, amp)))
    out.append(pts[-1])
    d.line(out, fill=fill, width=width, joint="curve")


# --------------------------------------------------------------------------- headers
def header(theme, d, title, subtitle, x, color):
    f = gfx.font
    acc = gfx.accent()
    ink = color or BLACK
    if theme == "bauhaus":
        t = title.upper()
        ft = f("display", 26)
        tw = gfx.text_w(d, t, ft)
        d.rectangle((x - 12, 22, x + tw + 14, 64), fill=BLACK)
        d.text((x + 1, 27), t, font=ft, fill=WHITE)
        d.ellipse((x + tw + 26, 31, x + tw + 50, 55), fill=RED)
        d.rectangle((x + tw + 58, 31, x + tw + 82, 55), fill=BLUE)
        if subtitle:
            d.text((x - 12, 72), subtitle.upper(), font=f("sans-bold", 13), fill=ink)
            return 104
        return 80
    if theme == "newspaper":
        d.text((x, 18), title, font=f("display", 34), fill=ink)
        d.line((x, 66, W - x, 66), fill=BLACK, width=3)
        d.line((x, 71, W - x, 71), fill=BLACK, width=1)
        if subtitle:
            d.text((x, 76), subtitle, font=f("serif-italic", 16), fill=ink)
            return 104
        return 84
    if theme == "deco":
        _diamond(d, x + 6, 46, 7, acc)
        d.text((x + 22, 24), title, font=f("display", 30), fill=ink)
        tw = gfx.text_w(d, title, f("display", 30))
        d.line((x + 22, 68, x + 22 + tw, 68), fill=acc, width=1)
        _diamond(d, x + 22 + tw + 8, 68, 4, acc)
        if subtitle:
            d.text((x + 22, 76), subtitle.upper(), font=f("sans", 13), fill=ink)
            return 104
        return 84
    if theme == "pixel":
        ft = f("display", 15)
        tw = gfx.text_w(d, title.upper(), ft)
        d.rectangle((x - 10, 20, x + tw + 14, 58), outline=BLACK, width=3)
        d.rectangle((x - 5, 25, x + tw + 9, 53), outline=BLACK, width=1)
        d.text((x + 2, 31), title.upper(), font=ft, fill=ink)
        d.rectangle((x + tw + 24, 33, x + tw + 36, 45), fill=acc)
        if subtitle:
            d.text((x - 8, 64), subtitle, font=f("sans", 18), fill=ink)
            return 100
        return 76
    if theme == "zen":
        d.rectangle((x, 26, x + 34, 60), fill=RED)
        d.text((x + 50, 20), title, font=f("serif", 34), fill=ink)
        if subtitle:
            d.text((x + 50, 66), subtitle.upper(), font=f("sans", 12), fill=ink)
            return 104
        return 80
    if theme == "swiss":
        d.rectangle((x, 20, W - x, 25), fill=BLACK)
        d.text((x, 32), title, font=f("display", 30), fill=ink)
        d.rectangle((W - x - 18, 34, W - x, 52), fill=RED)
        if subtitle:
            d.text((x, 72), subtitle, font=f("sans", 13), fill=ink)
            return 102
        return 80
    if theme == "memphis":
        ft = f("display", 24)
        tw = gfx.text_w(d, title, ft)
        d.rectangle((x - 4, 26, x + tw + 26, 66), fill=BLACK)
        d.rectangle((x - 10, 20, x + tw + 20, 60), fill=acc, outline=BLACK, width=3)
        d.text((x + 5, 25), title, font=ft, fill=WHITE)
        pts = [(x + tw + 38 + i * 4, 40 + 7 * math.sin(i / 1.6)) for i in range(18)]
        d.line(pts, fill=BLUE, width=4, joint="curve")
        if subtitle:
            d.text((x - 10, 74), subtitle, font=f("sans", 16), fill=ink)
            return 106
        return 84
    if theme == "blueprint":
        t = title.upper()
        ft = f("display", 24)
        tw = gfx.text_w(d, t, ft)
        d.text((x, 22), t, font=ft, fill=ink)
        y = 60
        d.line((x, y, x + tw, y), fill=BLACK, width=1)
        d.polygon([(x, y), (x + 8, y - 4), (x + 8, y + 4)], fill=BLACK)
        d.polygon([(x + tw, y), (x + tw - 8, y - 4), (x + tw - 8, y + 4)], fill=BLACK)
        d.line((x, y - 8, x, y + 8), fill=BLACK)
        d.line((x + tw, y - 8, x + tw, y + 8), fill=BLACK)
        if subtitle:
            d.text((x, 72), subtitle.upper(), font=f("sans", 12), fill=ink)
            return 102
        return 80
    if theme == "botanical":
        _sprig(d, x + 6, 60, 1.3)
        d.text((x + 34, 20), title, font=f("display", 32), fill=ink)
        if subtitle:
            d.text((x + 34, 66), subtitle, font=f("serif", 15), fill=ink)
            return 104
        return 82
    if theme == "chalk":
        ft = f("display", 40)
        tw = gfx.text_w(d, title, ft)
        d.text((x, 14), title, font=ft, fill=ink)
        _wobbly_line(d, [(x - 4, 66), (x + tw + 12, 63)], acc, 3, seed=len(title))
        if subtitle:
            d.text((x, 72), subtitle, font=f("sans", 18), fill=ink)
            return 106
        return 84
    return None


# --------------------------------------------------------------------------- frames
def frame(theme, d, inset, col):
    x0, y0, x1, y1 = inset, inset, W - 1 - inset, H - 1 - inset
    acc = gfx.accent()
    if theme == "bauhaus":
        d.ellipse((W - 110, -110, W + 110, 110), fill=YELLOW)
        d.rectangle((0, H - 70, 70, H), fill=BLUE)
        d.rectangle((0, 0, 14, H - 90), fill=BLACK)
        d.polygon([(W - 120, H), (W - 60, H - 70), (W, H)], fill=RED)
        return True
    if theme == "newspaper":
        d.line((x0, y0, x1, y0), fill=col, width=3)
        d.line((x0, y0 + 6, x1, y0 + 6), fill=col, width=1)
        d.line((x0, y1, x1, y1), fill=col, width=1)
        return True
    if theme == "deco":
        d.rectangle((x0 - 8, y0 - 8, x1 + 8, y1 + 8), outline=acc, width=2)
        d.rectangle((x0, y0, x1, y1), outline=acc, width=1)
        for cx, cy in ((W // 2, y0 - 8), (W // 2, y1 + 8), (x0 - 8, H // 2), (x1 + 8, H // 2)):
            _diamond(d, cx, cy, 7, acc)
        return True
    if theme == "pixel":
        d.rectangle((x0 - 10, y0 - 10, x1 + 10, y1 + 10), outline=col, width=4)
        d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), outline=col, width=2)
        for cx, cy in ((x0 - 10, y0 - 10), (x1 + 2, y0 - 10), (x0 - 10, y1 + 2), (x1 + 2, y1 + 2)):
            d.rectangle((cx, cy, cx + 8, cy + 8), fill=acc)
        return True
    if theme == "zen":
        d.line((x0, y0 + 40, x0, y1 - 40), fill=col, width=1)
        day = str(dt.date.today().day)
        d.rectangle((x1 - 48, y1 - 48, x1, y1), fill=RED)
        d.text((x1 - 24, y1 - 24), day, font=gfx.font("sans-bold", 20), fill=WHITE, anchor="mm")
        return True
    if theme == "swiss":
        d.rectangle((x0, y0 - 4, x1, y0 + 2), fill=col)
        d.rectangle((x1 - 22, y0 + 12, x1, y0 + 34), fill=RED)
        return True
    if theme == "memphis":
        pts = [(26 + i * 5, 36 + 9 * math.sin(i / 1.4)) for i in range(24)]
        d.line(pts, fill=BLUE, width=5, joint="curve")
        zz = [(W - 160 + i * 18, 24 + (i % 2) * 18) for i in range(8)]
        d.line(zz, fill=BLACK, width=4)
        d.polygon([(W - 70, H - 30), (W - 30, H - 100), (W + 10, H - 30)], fill=GREEN, outline=BLACK)
        for r in range(4):
            for c in range(5):
                cx, cy = 30 + c * 14, H - 80 + r * 14
                d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=BLACK)
        d.ellipse((W - 60, 70, W - 20, 110), fill=YELLOW, outline=BLACK, width=3)
        return True
    if theme == "blueprint":
        d.rectangle((x0, y0, x1, y1), outline=col, width=2)
        for i in range(x0 + 40, x1, 40):
            d.line((i, y0, i, y0 + 6), fill=col)
            d.line((i, y1 - 6, i, y1), fill=col)
        bw, bh = 210, 40
        d.rectangle((x1 - bw, y1 - bh, x1, y1), outline=col, width=2)
        d.line((x1 - bw, y1 - bh // 2, x1, y1 - bh // 2), fill=col)
        fs = gfx.font("sans", 11)
        d.text((x1 - bw + 8, y1 - bh + 4), "INKYFRAME · SHEET " + dt.date.today().strftime("%j"), font=fs, fill=col)
        d.text((x1 - bw + 8, y1 - bh // 2 + 4), "DATE " + dt.date.today().isoformat() + " · 1:1", font=fs, fill=col)
        return True
    if theme == "botanical":
        d.rectangle((x0, y0, x1, y1), outline=col, width=1)
        _sprig(d, x0 + 14, y0 + 56, 1.6)
        _sprig(d, x1 - 14, y1 - 6, 1.6, flip=-1)
        return True
    if theme == "chalk":
        _wobbly_line(d, [(x0, y0), (x1, y0 + 2), (x1 - 2, y1), (x0 + 2, y1 - 1), (x0, y0)], col, 3, seed=7, amp=2.5)
        _wobbly_line(d, [(x0 + 8, y1 + 9), (x0 + 160, y1 + 8)], acc, 3, seed=3)
        return True
    return None
