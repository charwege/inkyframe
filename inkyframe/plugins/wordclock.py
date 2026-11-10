"""Word clock – classic 11×10 letter grid in German or English, square face with side panels.

E-ink note: every change is a full refresh (~25–30 s), so it updates every 5 minutes.
There are deliberately no minute dots – that would mean a refresh every minute.
"""
import math

from PIL import Image, ImageDraw

from inkyframe import gfx
from inkyframe.gfx import BLACK, RED, WHITE
from inkyframe.plugin import Plugin, Setting

from . import _calendar as C


def _span(r, c, n):
    return {(r, c + i) for i in range(n)}


# ---------------------------------------------------------------- German
DE_GRID = ["ESKISTAFÜNF", "ZEHNZWANZIG", "DREIVIERTEL", "VORFUNKNACH", "HALBAELFÜNF",
           "EINSXAMZWEI", "DREIPMJVIER", "SECHSNLACHT", "SIEBENZWÖLF", "ZEHNEUNKUHR"]
DE_W = {"ES": (0, 0, 2), "IST": (0, 3, 3), "FÜNF": (0, 7, 4), "ZEHN": (1, 0, 4), "ZWANZIG": (1, 4, 7),
        "VIERTEL": (2, 4, 7), "VOR": (3, 0, 3), "NACH": (3, 7, 4), "HALB": (4, 0, 4), "UHR": (9, 8, 3)}
DE_H = {1: (5, 0, 4), 2: (5, 7, 4), 3: (6, 0, 4), 4: (6, 7, 4), 5: (4, 7, 4), 6: (7, 0, 5),
        7: (8, 0, 6), 8: (7, 7, 4), 9: (9, 3, 4), 10: (9, 0, 4), 11: (4, 5, 3), 12: (8, 6, 5)}
DE_T = {0: [], 1: ["FÜNF", "NACH"], 2: ["ZEHN", "NACH"], 3: ["VIERTEL", "NACH"], 4: ["ZWANZIG", "NACH"],
        5: ["FÜNF", "VOR", "HALB"], 6: ["HALB"], 7: ["FÜNF", "NACH", "HALB"], 8: ["ZWANZIG", "VOR"],
        9: ["VIERTEL", "VOR"], 10: ["ZEHN", "VOR"], 11: ["FÜNF", "VOR"]}

# ---------------------------------------------------------------- English
EN_GRID = ["ITLISASAMPM", "ACQUARTERDC", "TWENTYFIVEX", "HALFSTENFTO", "PASTERUNINE",
           "ONESIXTHREE", "FOURFIVETWO", "EIGHTELEVEN", "SEVENTWELVE", "TENSEOCLOCK"]
EN_W = {"IT": (0, 0, 2), "IS": (0, 3, 2), "A": (1, 0, 1), "QUARTER": (1, 2, 7), "TWENTY": (2, 0, 6),
        "FIVE": (2, 6, 4), "HALF": (3, 0, 4), "TEN": (3, 5, 3), "TO": (3, 9, 2), "PAST": (4, 0, 4),
        "OCLOCK": (9, 5, 6)}
EN_H = {1: (5, 0, 3), 2: (6, 8, 3), 3: (5, 6, 5), 4: (6, 0, 4), 5: (6, 4, 4), 6: (5, 3, 3),
        7: (8, 0, 5), 8: (7, 0, 5), 9: (4, 7, 4), 10: (9, 0, 3), 11: (7, 5, 6), 12: (8, 5, 6)}
EN_T = {0: [], 1: ["FIVE", "PAST"], 2: ["TEN", "PAST"], 3: ["A", "QUARTER", "PAST"], 4: ["TWENTY", "PAST"],
        5: ["TWENTY", "FIVE", "PAST"], 6: ["HALF", "PAST"], 7: ["TWENTY", "FIVE", "TO"], 8: ["TWENTY", "TO"],
        9: ["A", "QUARTER", "TO"], 10: ["TEN", "TO"], 11: ["FIVE", "TO"]}


def words_for(t, lang="de"):
    """Return (lit cells, hour cells) for time t."""
    m5 = t.minute // 5
    if lang == "en":
        words, table, hours = EN_W, EN_T, EN_H
        lit = ["IT", "IS"] + table[m5] + (["OCLOCK"] if m5 == 0 else [])
        hour = t.hour % 12 + (1 if m5 >= 7 else 0)
    else:
        words, table, hours = DE_W, DE_T, DE_H
        lit = ["ES", "IST"] + table[m5] + (["UHR"] if m5 == 0 else [])
        hour = t.hour % 12 + (1 if m5 >= 5 else 0)
    hour = hour % 12 or 12
    cells = set()
    for w in lit:
        cells |= _span(*words[w])
    r, c, n = hours[hour]
    if lang != "en" and m5 == 0 and hour == 1:
        n = 3                              # "ES IST EIN UHR"
    return cells, _span(r, c, n)


STYLES = {
    #               background, other letters, time, hour
    "dark":       (BLACK, WHITE, RED, RED),      # black, time in red, other letters white
    "dark-dim":   (BLACK, "dim", WHITE, RED),    # other letters finely dotted (looks grey on e-ink)
    "dark-clean": (BLACK, None, WHITE, RED),     # only the lit words
    "light":      (WHITE, "dim", BLACK, RED),
}


def _side_panels(ctx, d, fg, accent):
    now, lang = ctx.now, ctx.lang
    cx = 80
    wd = C.weekday(now, lang).upper()
    gfx.text_center(d, wd, gfx.font("serif", 15 if len(wd) <= 8 else 13), cx, 68, fg)
    d.line((cx - 34, 96, cx + 34, 96), fill=fg, width=1)
    special = C.is_special(now.date(), ctx.location.get("holidays", "none"))
    d.text((cx, 166), str(now.day), font=gfx.font("serif", 88), fill=accent if special else fg, anchor="mm")
    d.line((cx - 34, 236, cx + 34, 236), fill=fg, width=1)
    gfx.text_center(d, C.month(now, lang), gfx.font("serif", 17), cx, 250, fg)
    gfx.text_center(d, str(now.year), gfx.font("serif-italic", 18), cx, 276, fg)
    for i, yy in enumerate((340, 364, 388)):
        r = 5 if i == 1 else 3
        d.polygon([(cx, yy - r), (cx + r, yy), (cx, yy + r), (cx - r, yy)], fill=accent if i == 1 else fg)

    # classic dial on the right
    rx, ry, rr = ctx.W - 80, 140, 58
    d.ellipse((rx - rr, ry - rr, rx + rr, ry + rr), outline=fg, width=2)
    d.ellipse((rx - rr + 5, ry - rr + 5, rx + rr - 5, ry + rr - 5), outline=fg, width=1)
    for i in range(0, 60, 5):
        a = -math.pi / 2 + i * math.pi / 30
        r1 = rr - (14 if i % 15 == 0 else 11)
        d.line((rx + math.cos(a) * r1, ry + math.sin(a) * r1, rx + math.cos(a) * (rr - 5), ry + math.sin(a) * (rr - 5)),
               fill=fg, width=3 if i % 15 == 0 else 1)
    fr = gfx.font("serif", 12)
    numerals = ("XII", "III", "VI", "IX") if gfx.theme() == "classic" else ("12", "3", "6", "9")
    for num, ang in zip(numerals, (-90, 0, 90, 180)):
        a = math.radians(ang)
        d.text((rx + math.cos(a) * (rr - 25), ry + math.sin(a) * (rr - 25)), num, font=fr, fill=fg, anchor="mm")
    m = (now.minute // 5) * 5
    ah = math.radians(-90 + ((now.hour % 12) + m / 60) * 30)
    am = math.radians(-90 + m * 6)
    d.line((rx, ry, rx + math.cos(ah) * rr * .45, ry + math.sin(ah) * rr * .45), fill=fg, width=4)
    d.line((rx, ry, rx + math.cos(am) * rr * .72, ry + math.sin(am) * rr * .72), fill=accent, width=2)
    d.ellipse((rx - 4, ry - 4, rx + 4, ry + 4), fill=accent)

    ph = C.moon_phase(now)
    C.draw_moon(d, rx, 300, 26, ph, fg, None, fg)
    fm = gfx.font("serif-italic", 16)
    for i, line in enumerate(gfx.wrap(d, C.moon_name(ph, lang), fm, 140)):
        gfx.text_center(d, line, fm, rx, 340 + i * 20, fg)


class WordClock(Plugin):
    id = "wordclock"
    name = {"en": "Word Clock", "de": "Wortuhr"}
    theme_remap = False      # has its own dark/light styles
    icon = "◷"
    description = "Classic word clock (German or English grid) with date, dial and moon phase. Updates every 5 min."
    author = "inkyframe"
    settings = [
        Setting("style", "select", "Style", default="dark", options=[
            ("dark", "Black, time in red"), ("dark-dim", "Black, other letters dotted"),
            ("dark-clean", "Black, only lit words"), ("light", "Light")]),
        Setting("grid", "select", "Letter grid", default="auto",
                options=[("auto", "Same as display language"), ("de", "German"), ("en", "English")]),
    ]

    def _grid_lang(self, ctx):
        g = ctx.settings.get("grid", "auto")
        g = ctx.lang if g == "auto" else g
        return "de" if g == "de" else "en"        # letter grids exist for German and English

    def content_key(self, ctx):
        n = ctx.now
        return f"{n:%Y-%m-%d %H}:{n.minute // 5}|{sorted(ctx.settings.items())}|{ctx.lang}"

    def sample(self, ctx):
        return {"offline": True}      # needs no data – lets previews/CI render it

    def render(self, ctx, data=None):
        bg, off, on, hour_col = STYLES.get(ctx.settings.get("style", "dark"), STYLES["dark"])
        lang = self._grid_lang(ctx)
        grid = EN_GRID if lang == "en" else DE_GRID
        img, d = ctx.canvas(bg)
        cells, hour_cells = words_for(ctx.now, lang)
        deco = WHITE if bg == BLACK else BLACK

        side = ctx.H - 24
        sx0, sy0 = (ctx.W - side) // 2, 12
        theme = gfx.theme()
        if theme == "modern":            # no frame – just two hairlines left and right
            for x in (sx0 - 4, sx0 + side + 4):
                d.line((x, sy0 + 40, x, sy0 + side - 40), fill=deco, width=1)
        elif theme == "playful":         # rounded frame with coloured corner dots
            d.rounded_rectangle((sx0, sy0, sx0 + side, sy0 + side), radius=30, outline=deco, width=3)
            for (x, y), c in zip(((sx0 + 16, sy0 + 16), (sx0 + side - 16, sy0 + 16), (sx0 + 16, sy0 + side - 16),
                                  (sx0 + side - 16, sy0 + side - 16)), (RED, gfx.YELLOW, gfx.GREEN, gfx.BLUE)):
                d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=c)
        else:                            # classic: double rule with diamonds
            d.rectangle((sx0, sy0, sx0 + side, sy0 + side), outline=deco, width=2)
            d.rectangle((sx0 + 7, sy0 + 7, sx0 + side - 7, sy0 + side - 7), outline=deco, width=1)
            for (x, y) in ((sx0, sy0), (sx0 + side, sy0), (sx0, sy0 + side), (sx0 + side, sy0 + side)):
                d.polygon([(x, y - 6), (x + 6, y), (x, y + 6), (x - 6, y)], fill=bg, outline=deco)

        pad = 30
        cw, ch = (side - 2 * pad) / 11, (side - 2 * pad) / 10
        f_off, f_on = gfx.font("serif", 26), gfx.font("serif-bold", 26)
        dim = Image.new("1", img.size, 0) if off == "dim" else None
        dd = ImageDraw.Draw(dim) if dim is not None else None
        if dd is not None:
            dd.fontmode = "1"
        for r, row in enumerate(grid):
            for c, letter in enumerate(row):
                pos = (sx0 + pad + c * cw + cw / 2, sy0 + pad + r * ch + ch / 2)
                if (r, c) in hour_cells:
                    d.text(pos, letter, font=f_on, fill=hour_col, anchor="mm")
                elif (r, c) in cells:
                    d.text(pos, letter, font=f_on, fill=on, anchor="mm")
                elif dd is not None:
                    dd.text(pos, letter, font=f_off, fill=1, anchor="mm")
                elif off is not None:
                    d.text(pos, letter, font=f_off, fill=off, anchor="mm")
        if dim is not None:   # every 2nd pixel of every 2nd row -> ~25 % coverage = soft grey
            px, ip = dim.load(), img.load()
            for y in range(0, img.size[1], 2):
                for x in range(y // 2 % 2, img.size[0], 2):
                    if px[x, y]:
                        ip[x, y] = deco
        _side_panels(ctx, d, deco, RED)
        return img
