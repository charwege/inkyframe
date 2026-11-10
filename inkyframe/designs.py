"""Signature layouts of the studio designs for "Weather & Calendar" and "Thought of the Day".

Each function is a port of the matching HTML mockup (800 × 480 px) to Pillow. Plugins call
weather(ctx, data) / quote(ctx, kind, text, author); they return None for designs without a
signature layout, and the plugin falls back to its regular layout.
"""
import datetime as dt
import random

from . import i18n
from .plugins import _calendar as C
from .studio import B, G, K, R, Y, Canvas, Wh, longest_word, roman

STUDIO = ("bauhaus", "newspaper", "deco", "pixel", "zen", "swiss", "memphis", "blueprint", "botanical", "chalk")


# ================================================================== shared data
def numeric_date(d, lang, year=True):
    if lang == "en":
        return f"{d.month}/{d.day}/{d.year}" if year else f"{d.month}/{d.day}"
    if lang == "sv":
        return f"{d:%Y-%m-%d}" if year else f"{d.day}/{d.month}"
    sep = {"fr": "/", "es": "/", "it": "/", "pt": "/", "nl": "-"}.get(lang, ".")
    s = f"{d.day:02d}{sep}{d.month:02d}"
    return f"{s}{sep}{d.year}" if year else (s + ("." if sep == "." else ""))


def weather_info(ctx, data):
    from .plugins.weather import WMO
    cur, daily, hourly = data["current"], data["daily"], data["hourly"]
    en, de, kind = WMO.get(int(cur["weather_code"]), ("", "", "cloud"))
    probs = [p if p is not None else 0 for p in hourly["precipitation_probability"][:24]]
    probs += [0] * (24 - len(probs))
    sr = dt.datetime.fromisoformat(daily["sunrise"][0])
    ss = dt.datetime.fromisoformat(daily["sunset"][0])
    length = ss - sr
    today, lang = ctx.today, ctx.lang
    maxp = max(probs)
    ph = C.moon_phase(ctx.now)
    return {
        "temp": round(cur["temperature_2m"]), "cond": ctx.t(en, de), "kind": kind,
        "code": int(cur["weather_code"]),
        "hi": round(daily["temperature_2m_max"][0]), "lo": round(daily["temperature_2m_min"][0]),
        "sr": f"{sr:%H:%M}", "ss": f"{ss:%H:%M}",
        "dh": length.seconds // 3600, "dm": (length.seconds % 3600) // 60,
        "probs": probs, "maxp": maxp, "maxh": probs.index(maxp), "nowh": ctx.now.hour,
        "phase": ph, "moon": C.moon_name(ph, lang),
        "place": ctx.location.get("name", ""),
        "wd": C.weekday(today, lang), "wds": C.weekday_short(today, lang),
        "month": C.month(today, lang), "year": today.year, "day": today.day,
        "week": today.isocalendar()[1], "doy": today.timetuple().tm_yday,
        "date": numeric_date(today, lang), "today": today,
    }


def hour(h, lang="en"):
    return f"{h} Uhr" if lang == "de" else f"{h:02d}:00"


def advice(ctx, w):
    if w["maxp"] >= 50:
        return ctx.t("Pack an umbrella around {h}!", "Gegen {h} Schirm einpacken!", h=hour(w["maxh"], ctx.lang))
    if w["hi"] >= 25:
        return ctx.t("Sunglasses weather!", "Sonnenbrillen-Wetter!")
    if w["lo"] <= 0:
        return ctx.t("Wrap up warm today!", "Heute warm anziehen!")
    return ctx.t("A good day for a walk!", "Gutes Wetter für einen Spaziergang!")


def label(ctx, kind):
    return ctx.t("Question of the day", "Frage des Tages") if kind == "question" \
        else ctx.t("Thought of the day", "Gedanke des Tages")


def body(ctx, kind, text):
    if kind == "quote":
        q = i18n.get(ctx.lang, "QUOTE_MARKS")
        return f"{q[0]}{text}{q[1]}"
    return text


def lower_first(s):
    return s[:1].lower() + s[1:] if s else s


def moon_disc(cv, cx, cy, r, phase, lit, dark, outline):
    C.draw_moon(cv.d, cx, cy, r, phase, lit, dark, outline)


# ================================================================== dispatch
def weather(ctx, data):
    fn = globals().get(f"weather_{ctx.theme}")
    return fn(ctx, weather_info(ctx, data)) if fn else None


def quote(ctx, kind, text, author):
    fn = globals().get(f"quote_{ctx.theme}")
    return fn(ctx, kind, text, author) if fn else None


# ================================================================== 1 Bauhaus
def weather_bauhaus(ctx, w):
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 300, 480), fill=K)
    c.circle(80, 220, 150, fill=Y)
    c.rect((216, 0, 300, 84), fill=R)
    ds = 30
    while ds > 14 and c.tw(w["wds"].upper(), "black", ds, 1) > 70:
        ds -= 1
    c.text(282, 22 + (30 - ds) / 2, w["wds"], "black", ds, Wh, track=1, align="r", upper=True)
    day = str(w["day"])
    c.text(28, 120, day, "black", 190, K, track=-6, lh=1)
    mon = w["month"].upper()
    ms = 34
    while ms > 18 and c.tw(mon, "black", ms, 2) > 260:
        ms -= 1
    L = c.line_h("black", ms)
    c.text(28, 406 - L, mon, "black", ms, Wh, track=2)
    L = c.line_h("x600", 18)
    c.text(28, 440 - L, ctx.t("{y} · WK {n}", "{y} · KW {n}", y=w["year"], n=w["week"]), "x600", 18, Wh, track=6)

    X0, X1 = 334, 766
    y = 30
    c.text(X0, y, w["place"], "x800", 16, K, track=5, upper=True)
    c.circle(707, y + 9, 9, fill=R)
    c.rect((722, y, 740, y + 18), fill=B)
    c.poly([(746, y + 18), (766, y + 18), (756, y)], fill=Y)
    y += c.line_h("x800", 16) + 18
    tL = 130 * 0.85
    temp = f"{w['temp']}°"
    c.text(X0, y, temp, "black", 130, K, track=-4, lh=0.85)
    cx = X0 + c.tw(temp, "black", 130, -4) + 4 + 22
    lab = w["cond"].upper()
    ls = 17
    while ls > 11 and c.tw(lab, "x800", ls, 2) + 24 > X1 - cx:
        ls -= 1
    lh = c.line_h("x800", ls)
    colh = lh + 12 + 8 + c.line_h("x800", 20) + 4
    ty = y + tL - colh
    c.rect((cx, ty, cx + c.tw(lab, "x800", ls, 2) + 22, ty + lh + 12), fill=B)
    c.text(cx + 12, ty + 6, lab, "x800", ls, Wh, track=2)
    hy = ty + lh + 12 + 8
    c.text(cx, hy, f"▲ {w['hi']}°", "x800", 20, R)
    c.text(cx + c.tw(f"▲ {w['hi']}°", "x800", 20) + 16, hy, f"▼ {w['lo']}°", "x800", 20, B)
    y += tL + 18

    c.rect((X0, y, X1, y + 4), fill=K)
    cw = (X1 - X0) / 3
    top = y + 4
    rowh = 10 + c.line_h("x800", 11) + 2 + c.line_h("black", 24)
    c.vline(X0 + cw - 2, top, top + rowh, K, 2)
    c.vline(X0 + 2 * cw - 2, top, top + rowh, K, 2)
    for i, (lbl, val) in enumerate(((ctx.t("Sunrise", "Aufgang"), w["sr"]), (ctx.t("Sunset", "Untergang"), w["ss"]))):
        x = X0 + i * cw + (10 if i else 0)
        c.text(x, top + 10, lbl, "x800", 11, K, track=2, upper=True)
        c.text(x, top + 10 + c.line_h("x800", 11) + 2, val, "black", 24, K)
    mx = X0 + 2 * cw + 10
    moon_disc(c, mx + 15, top + 10 + rowh / 2 - 5, 15, w["phase"], Wh, K, K)
    c.text(mx + 40, top + 14, ctx.t("Moon", "Mond"), "x800", 11, K, track=2, upper=True)
    mn = w["moon"]
    ms = 16
    while ms > 10 and c.tw(mn, "x800", ms) > X1 - mx - 40:
        ms -= 1
    c.text(mx + 40, top + 16 + c.line_h("x800", 11), mn, "x800", ms, K)
    y = top + rowh + 18

    c.text(X0, y, ctx.t("Rain today · max {p} %", "Regen heute · max {p} %", p=w["maxp"]), "x800", 11, K,
           track=2, upper=True)
    ax = c.line_h("x800", 11)
    gtop = y + ax + 6
    gbot = 454 - ax - 6
    c.rect((X0, gbot - 4, X1, gbot), fill=K)
    bw = (X1 - X0 - 23 * 3) / 24
    for i, p in enumerate(w["probs"]):
        h = round(p * 0.95) + 2
        x = X0 + i * (bw + 3)
        c.rect((x, gbot - 4 - h, x + bw, gbot - 4), fill=R if i == w["nowh"] else B)
    for i, lbl in enumerate(("00", "06", "12", "18", "24")):
        x = X0 + (X1 - X0) * i / 4
        c.text(x, gbot + 6, lbl, "x800", 11, K, align="l" if i == 0 else "r" if i == 4 else "c")
    return c.finish()


def quote_bauhaus(ctx, kind, text, author):
    c = Canvas("bauhaus", Wh)
    c.circle(750, 40, 130, fill=R)
    c.rect((590, 370, 740, 520), fill=B)
    c.poly([(508, 450), (600, 450), (554, 370)], fill=Y)
    c.rect((0, 0, 18, 480), fill=K)
    lab = label(ctx, kind).upper()
    lw = c.tw(lab, "x800", 14, 4) - 4 + 24
    lh = c.line_h("x800", 14)
    c.rect((60, 46, 60 + lw, 46 + lh + 12), fill=K)
    c.text(72, 52, lab, "x800", 14, Wh, track=4)
    c.text(60 + lw + 14, 52, numeric_date(ctx.today, ctx.lang).replace(".", " · ").replace("/", " · "),
           "x800", 14, K, track=4)
    top = 46 + lh + 12 + 26
    txt = body(ctx, kind, text)
    room = 360 - top - (34 if author else 0)
    size, lines, L, tr = c.fit(txt, "black", 48, 560, room, lh=1.04, track=-1, upper=True)
    c.para(60, top, 560, lines, "black", size, L, K, tr, highlight=longest_word(txt.upper()))
    if author:
        c.text(60, top + len(lines) * L + 14, f"— {author}", "x800", 14, K, track=4, upper=True)
    return c.finish()


# ================================================================== 2 Newspaper
def _double_rule(c, x0, x1, y):
    c.hline(x0, x1, y, K, 1)
    c.hline(x0, x1, y + 3, K, 1)


def _rich_wrap(c, segs, width):
    """segs: [(text, role, size, fill)] -> lines of [(word, role, size, fill)]."""
    words = []
    for t, role, size, fill in segs:
        words += [(wd, role, size, fill) for wd in t.split()]
    lines, cur, cw = [], [], 0
    for wd in words:
        ww = c.tw(wd[0], wd[1], wd[2])
        sp = c.tw(" ", wd[1], wd[2])
        if cur and cw + sp + ww > width:
            lines.append(cur)
            cur, cw = [], 0
        cw += (sp if cur else 0) + ww
        cur.append(wd)
    if cur:
        lines.append(cur)
    return lines


def weather_newspaper(ctx, w):
    c = Canvas("newspaper", Wh)
    X0, X1 = 30, 770
    c.text(400, 18, ctx.t("The Daily Frame", "Der Rahmen-Anzeiger"), "pf900", 40, K, track=1, lh=1, align="c")
    y = 18 + 40 + 6
    c.hline(X0, X1, y, K, 1)
    ty = y + 1 + 4
    c.text(X0, ty, f"{ctx.t('No. {n}', 'Nr. {n}', n=w['doy'])} · {w['place']}", "ss400", 12, K)
    c.text(400, ty, C.long_date(w["today"], ctx.lang, weekday=True, year=True), "ss600", 12, K, align="c")
    c.text(X1, ty, f"{w['moon']} · {ctx.t('WK {n}', 'KW {n}', n=w['week'])}", "ss400", 12, K, align="r")
    y = ty + c.line_h("ss400", 12) + 6
    _double_rule(c, X0, X1, y)
    y += 4 + 10

    if w["maxp"] < 20:
        tail = ctx.t("staying dry all day", "es bleibt trocken")
    elif max(w["probs"][18:]) < 30 and w["maxp"] >= 50:
        tail = ctx.t("clearing up in the evening", "am Abend klart es auf")
    elif w["maxp"] >= 50:
        tail = ctx.t("wet until late", "nass bis in die Nacht")
    else:
        tail = ctx.t("a few showers possible", "vereinzelt Schauer möglich")
    head = ctx.t("{c} at {t}°,", "{c} bei {t}°,", c=w["cond"], t=w["temp"])
    size = 46
    while True:
        lines = _rich_wrap(c, [(head, "pf900", size, K), (tail, "pf700i", size, R)], X1 - X0)
        if len(lines) <= 2 or size <= 30:
            break
        size -= 2
    L = size * 1.02
    for ln in lines:
        x = X0
        for wd, role, sz, fill in ln:
            c.text(x, y, wd, role, sz, fill, track=-0.5, lh=1.02)
            x += c.tw(wd, role, sz, -0.5) + c.tw(" ", role, sz)
        y += L
    y += 10

    c.hline(X0, X1, y, K, 1)
    gtop, gbot = y + 1, 460
    cw = (X1 - X0) / 3
    c.vline(X0 + cw - 1, gtop, gbot, K, 1)
    c.vline(X0 + 2 * cw - 1, gtop, gbot, K, 1)
    hL = c.line_h("pf700", 15)
    heads = (ctx.t("The day", "Der Tag"), ctx.t("In numbers", "In Zahlen"), ctx.t("Rain over the day", "Regen im Verlauf"))
    xs = (X0, X0 + cw + 16, X0 + 2 * cw + 16)
    for x, hd in zip(xs, heads):
        c.text(x, gtop + 10, hd, "pf700", 15, K, track=1.5, upper=True)
    # column 1: running text with a drop cap
    if w["maxp"] >= 20:
        para = ctx.t("Rain chances peak at {p} % around {h}. Highs around {a}°, dropping to {b}° at night.",
                     "Gegen {h} steigt die Regenwahrscheinlichkeit auf {p} Prozent. Höchstwerte um {a} Grad, "
                     "nachts kühlt es auf {b} Grad ab.", p=w["maxp"], h=hour(w["maxh"], ctx.lang), a=w["hi"], b=w["lo"])
    else:
        para = ctx.t("A mostly dry day with highs around {a}°, dropping to {b}° at night.",
                     "Ein überwiegend trockener Tag mit Höchstwerten um {a} Grad, nachts kühlt es auf {b} Grad ab.",
                     a=w["hi"], b=w["lo"])
    _dropcap_para(c, X0, gtop + 10 + hL + 6, cw - 16, gbot - 4, para)
    # column 2: figures
    rows = ((ctx.t("Now", "Jetzt"), f"{w['temp']} °C" if ctx.settings.get("units", "celsius") == "celsius" else f"{w['temp']} °F"),
            (ctx.t("High / low", "Höchst / Tiefst"), f"{w['hi']}° / {w['lo']}°"),
            (ctx.t("Sunrise", "Sonnenaufgang"), w["sr"]), (ctx.t("Sunset", "Sonnenuntergang"), w["ss"]),
            (ctx.t("Day length", "Tageslänge"), f"{w['dh']} h {w['dm']:02d} min"))
    x0, x1 = X0 + cw + 16, X0 + 2 * cw - 16
    yy = gtop + 10 + hL + 4
    rL = c.line_h("ss400", 14)
    for i, (a, b) in enumerate(rows):
        c.text(x0, yy, a, "ss400", 14, K)
        c.text(x1, yy, b, "ss600", 14, K, align="r")
        if i < len(rows) - 1:
            for xx in range(int(x0), int(x1), 3):
                c.d.point((xx, yy + rL + 2), fill=K)
        yy += rL + 3 + 4
    # column 3: rain bars
    x0, x1 = X0 + 2 * cw + 16, X1
    btop = gtop + 10 + hL + 6
    lab = c.line_h("ss400i", 11)
    bbot = gbot - lab - 6
    c.rect((x0, bbot - 2, x1, bbot), fill=K)
    bw = (x1 - x0 - 23 * 2) / 24
    for i, p in enumerate(w["probs"]):
        h = (bbot - 2 - btop) * max(2, p) / 100
        x = x0 + i * (bw + 2)
        c.rect((x, bbot - 2 - h, x + bw, bbot - 2), fill=R if i == w["nowh"] else K)
    c.text(x0, bbot + 6, "00:00", "ss400i", 11, K)
    c.text((x0 + x1) / 2, bbot + 6, "12", "ss400i", 11, K, align="c")
    c.text(x1, bbot + 6, "24", "ss400i", 11, K, align="r")
    return c.finish()


def _dropcap_para(c, x, top, width, bottom, text):
    """Justified paragraph, 14 px / 1.4, with a 40 px Playfair drop cap over two lines."""
    size, L = 14, 14 * 1.4
    cap, rest = text[0], text[1:]
    capw = c.tw(cap, "pf900", 40) + 6
    words = rest.split()
    lines, cur = [], []
    while words:
        avail = width - (capw if len(lines) < 2 else 0)
        wd = words[0]
        t = " ".join(cur + [wd])
        if cur and c.tw(t, "ss400", size) > avail:
            lines.append(cur)
            cur = []
            continue
        cur.append(wd)
        words.pop(0)
    if cur:
        lines.append(cur)
    c.text(x, top + 2 - 4, cap, "pf900", 40, K, lh=0.9)
    y = top
    for i, ln in enumerate(lines):
        if y + L > bottom:
            break
        x0 = x + (capw if i < 2 else 0)
        avail = width - (capw if i < 2 else 0)
        last = i == len(lines) - 1
        if last or len(ln) == 1:
            c.text(x0, y, " ".join(ln), "ss400", size, K, lh=1.4)
        else:
            wsum = sum(c.tw(wd, "ss400", size) for wd in ln)
            gap = (avail - wsum) / (len(ln) - 1)
            xx = x0
            for wd in ln:
                c.text(xx, y, wd, "ss400", size, K, lh=1.4)
                xx += c.tw(wd, "ss400", size) + gap
        y += L


def quote_newspaper(ctx, kind, text, author):
    c = Canvas("newspaper", Wh)
    X0, X1 = 30, 770
    hL = c.line_h("pf900", 24)
    c.text(X0, 18, ctx.t("The Daily Frame", "Der Rahmen-Anzeiger"), "pf900", 24, K)
    base_off = c._baseline(18, "pf900", 24, None) - c._baseline(0, "ss600", 12, None)
    rt = f"{C.long_date(ctx.today, ctx.lang, weekday=True, year=True)} · {ctx.t('Features', 'Feuilleton')}"
    c.text(X1, base_off, rt, "ss600", 12, K, align="r")
    y = 18 + hL + 6
    _double_rule(c, X0, X1, y)
    y += 4 + 14
    lab = label(ctx, kind).upper()
    lL = c.line_h("ss600", 13)
    lw = c.tw(lab, "ss600", 13, 4) - 4
    c.text(400, y, lab, "ss600", 13, R, track=4, align="c")
    c.hline(X0, 400 - lw / 2 - 12, y + lL / 2, K, 1)
    c.hline(400 + lw / 2 + 12, X1, y + lL / 2, K, 1)
    y += lL + 14
    fL = c.line_h("ss400i", 13)
    ftop = 458 - fL - 9
    c.hline(X0, X1, ftop, K, 1)
    left = f"— {author}" if author else ctx.t("Food for thought on the way – and for tonight's conversation.",
                                                 "Zum Nachdenken für unterwegs – und für das Gespräch am Abend.")
    c.text(X0, ftop + 9, left, "ss400i", 13, K)
    c.text(X1, ftop + 9, ctx.t("Page 1", "Seite 1"), "ss600", 13, K, align="r")
    mark = i18n.get(ctx.lang, "QUOTE_MARKS")[0]
    c.text(50, y - 26, mark, "pf900", 170, R, lh=1)
    qx = 50 + c.tw(mark, "pf900", 170) + 18
    size, lines, L, _ = c.fit(text, "pf400i", 44, 750 - qx, ftop - 14 - (y + 6), lh=1.16)
    c.para(qx, y + 6, 750 - qx, lines, "pf400i", size, L, K)
    return c.finish()


# ================================================================== 3 Art déco
def _deco_frame(c):
    c.rect((14, 14, 786, 466), outline=Y, width=2)
    c.rect((22, 22, 778, 458), outline=Y, width=1)


def _ornament(c, cx, cy, arm, gap, dcol=Y):
    c.hline(cx - gap - 4 - arm, cx - gap - 4, cy, Y, 1)
    c.hline(cx + gap + 4, cx + gap + 4 + arm, cy, Y, 1)
    c.diamond(cx, cy + .5, 8, dcol)


def _sunburst(c, cx, by, rx, ry, n, r, sw=1.5):
    import math
    for i in range(n + 1):
        a = math.pi + i / n * math.pi
        c.d.line((cx, by, round(cx + math.cos(a) * rx), round(by + math.sin(a) * ry)), fill=Y, width=round(sw))
    c.d.chord((cx - r, by - r, cx + r, by + r), 180, 360, fill=K, outline=Y, width=2)
    c.rect((cx - r - 2, by, cx + r + 3, by + r + 2), fill=K)


def weather_deco(ctx, w):
    c = Canvas("deco", K)
    _deco_frame(c)
    c.vline(252, 23, 457, Y, 1)
    items = [("poiret", 24, w["wd"].upper(), Y, 8), ("orn",), ("lime", 130, str(w["day"]), Wh, 0), ("orn",),
             ("poiret", 22, w["month"].upper(), Y, 6), ("jos", 14, roman(w["year"]), Y, 8)]
    hs = []
    for it in items:
        hs.append(20 if it[0] == "orn" else (it[1] if it[0] == "lime" else c.line_h(it[0], it[1])))
    y = 23 + (434 - sum(hs) - 4 * 5) / 2
    for it, h in zip(items, hs):
        if it[0] == "orn":
            _ornament(c, 137, y + 10, 40, 4)
        else:
            role, size, txt, col, tr = it
            while size > 12 and c.tw(txt, role, size, tr) - tr > 210:
                size -= 1
            c.text(137 + tr / 2, y, txt, role, size, col, track=tr, lh=1 if role == "lime" else None, align="c")
        y += h + 4

    X0, X1, CX = 279, 751, 515
    _sunburst(c, CX, 41 + 80, 150, 78, 12, 34)
    temp = f"{w['temp']}°"
    tw = c.tw(temp, "lime", 108)
    col = [(w["cond"], "poiret", 26, 3), (ctx.t("High {a}° · Low {b}°", "Hoch {a}° · Tief {b}°", a=w["hi"], b=w["lo"]).upper(), "jos", 16, 4),
           (w["place"].upper(), "jos", 14, 4)]
    colw = max(c.tw(t, r, s, tr) for t, r, s, tr in col)
    rw = tw + 26 + colw
    rx = CX - rw / 2
    ry = 41 + 80 + 6 - 8
    c.text(rx, ry, temp, "lime", 108, Wh, lh=1)
    colh = sum(c.line_h(r, s) for _, r, s, _ in col) + 12
    yy = ry + (108 - colh) / 2
    for t, r, s, tr in col:
        c.text(rx + tw + 26, yy, t, r, s, Y, track=tr)
        yy += c.line_h(r, s) + 6
    y = ry + 108 + 6 + 6
    lab_h = c.line_h("jos", 11)
    val_h = c.line_h("poiret", 22)
    sh = 6 + lab_h + 2 + val_h + 6
    c.hline(X0, X1, y, Y, 1)
    c.hline(X0, X1, y + sh, Y, 1)
    cw = (X1 - X0) / 3
    cells = ((ctx.t("Sun up", "Sonne auf"), w["sr"]), (ctx.t("Sun down", "Sonne unter"), w["ss"]), (ctx.t("Moon", "Mond"), w["moon"]))
    for i, (a, b) in enumerate(cells):
        cx = X0 + cw * i + cw / 2
        if i < 2:
            c.vline(X0 + cw * (i + 1) - 1, y, y + sh, Y, 1)
        ls, lt = 11, 4
        while (ls > 8 or lt > 1) and c.tw(a.upper(), "jos", ls, lt) > cw - 8:
            if lt > 1:
                lt -= 1
            else:
                ls -= 1
        c.text(cx + lt / 2, y + 1 + 6, a.upper(), "jos", ls, Y, track=lt, align="c")
        vs = 22
        while vs > 12 and c.tw(b, "poiret", vs) > cw - 10:
            vs -= 1
        c.text(cx, y + 1 + 6 + lab_h + 2, b, "poiret", vs, Wh, align="c")
    y += sh + 1 + 4
    lbl_h = c.line_h("jos", 11)
    bbot = 443 - lbl_h - 4
    bh = bbot - y
    step = (X1 - X0 - 3) / 23
    for i, p in enumerate(w["probs"]):
        h = bh * max(4, p) / 100
        x = X0 + i * step
        c.rect((x, bbot - h, x + 3, bbot), fill=R if i == w["nowh"] else Y)
    c.text(CX + 2.5, bbot + 4, ctx.t("Rain · 0–24 h · max {p} %", "Regen · 0 – 24 Uhr · höchstens {p} %", p=w["maxp"]).upper(),
           "jos", 11, Y, track=5, align="c")
    return c.finish()


def quote_deco(ctx, kind, text, author):
    c = Canvas("deco", K)
    _deco_frame(c)
    y = 23 + 22
    _sunburst(c, 400, y + 56, 110, 54, 10, 20)
    y += 56 + 14
    lab = label(ctx, kind).upper()
    c.text(400 + 5, y, lab, "jos", 14, Y, track=10, align="c")
    y += c.line_h("jos", 14) + 14
    _ornament(c, 400, y + 4, 90, 6, R)
    y += 8 + 14
    d = ctx.today
    foot = f"{roman(d.day)} · {roman(d.month)} · {roman(d.year)}"
    fh = c.line_h("jos", 13)
    fy = 457 - 20 - fh
    room = fy - 14 - y - (36 if author else 0)
    size, lines, L, tr = c.fit(body(ctx, kind, text), "poiret", 44, 800 - 2 * 93, room, lh=1.2, track=1)
    ty = y + (room - len(lines) * L) / 2
    c.para(93, ty, 800 - 186, lines, "poiret", size, L, Wh, tr, align="c")
    if author:
        c.text(400 + 3, ty + len(lines) * L + 10, f"— {author}".upper(), "jos", 14, Y, track=6, align="c")
    c.text(400 + 4, fy, foot, "jos", 13, Y, track=8, align="c")
    return c.finish()


# ================================================================== 4 Pixel
def _pixel_box(c, box):
    x0, y0, x1, y1 = box
    c.rect(box, outline=Wh, width=4)
    c.rect((x0 + 8, y0 + 8, x1 - 8, y1 - 8), outline=Wh, width=2)


SPRITES = {
    "rain": ["....wwww......", "..wwwwwwww....", ".wwwwwwwwwww..", "wwwwwwwwwwwwww", "wwwwwwwwwwwwww",
             ".wwwwwwwwwwww.", "..............", "..b...b...b...", ".b...b...b....", "b...b...b....."],
    "snow": ["....wwww......", "..wwwwwwww....", ".wwwwwwwwwww..", "wwwwwwwwwwwwww", "wwwwwwwwwwwwww",
             ".wwwwwwwwwwww.", "..............", "..w....w....w.", "....w....w....", ".w....w....w.."],
    "storm": ["....wwww......", "..wwwwwwww....", ".wwwwwwwwwww..", "wwwwwwwwwwwwww", "wwwwwwwwwwwwww",
              ".wwwwwyywwwww.", "......yy......", ".....yy.......", "......yy......", ".....y........"],
    "cloud": [".............", "....wwww......", "..wwwwwwww....", ".wwwwwwwwwww..", "wwwwwwwwwwwwww",
              "wwwwwwwwwwwwww", ".wwwwwwwwwwww.", "..............", "..............", ".............."],
    "sun": ["......y.......", "..y...y...y...", "...y.....y....", ".....yyy......", "yy..yyyyy..yy.",
            ".....yyy......", "...y.....y....", "..y...y...y...", "......y.......", ".............."],
    "part": ["..y...........", "y.y.y.........", ".yyy..wwww....", "yyyywwwwwwww..", ".yywwwwwwwwww.",
             "y.wwwwwwwwwwww", "..wwwwwwwwwwww", "...wwwwwwwwww.", "..............", ".............."],
}
SPRITES["fog"] = SPRITES["cloud"]
PIX = {"w": Wh, "b": B, "y": Y, "r": R, "g": G}


def _sprite(c, rows, x, y, s=8, colors=PIX):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in colors:
                c.rect((x + i * s, y + j * s, x + i * s + s, y + j * s + s), fill=colors[ch])


HEART = [".rr.rr.", "rrrrrrr", "rrrrrrr", ".rrrrr.", "..rrr..", "...r..."]


def weather_pixel(ctx, w):
    c = Canvas("pixel", K)
    hL = c.line_h("ps2p", 13)
    c.text(18, 18, w["place"].upper(), "ps2p", 13, Wh)
    c.text(400, 18, f"{w['wds'].upper()} {w['date']}", "ps2p", 13, Y, align="c")
    c.text(782, 18, f"LEVEL {w['week']}", "ps2p", 13, G, align="r")
    btop = 462 - 56
    mtop, mbot = 18 + hL + 14, btop - 14
    _pixel_box(c, (18, mtop, 348, mbot))
    x0 = 38
    y = mtop + 20
    _sprite(c, SPRITES.get(w["kind"], SPRITES["cloud"]), x0, y)
    c.text(x0 + 112 + 20, y + 40 - 22, f"{w['temp']}°", "ps2p", 44, Wh, lh=1)
    y += 80 + 10
    cs = 34
    cond = w["cond"].upper()
    while cs > 18 and c.tw(cond, "vt", cs) > 290:
        cs -= 1
    c.text(x0, y, cond, "vt", cs, Wh, lh=1)
    y += cs + 10
    c.text(x0, y, f"▲{w['hi']}°", "ps2p", 14, R)
    c.text(x0 + c.tw(f"▲{w['hi']}°", "ps2p", 14) + 18, y, f"▼{w['lo']}°", "ps2p", 14, B)
    rows = ((f"☀ {ctx.t('Up', 'Auf')}", w["sr"], Y), (f"☾ {ctx.t('Down', 'Ab')}", w["ss"], Y),
            (ctx.t("Day", "Tag"), f"{w['dh']}H {w['dm']:02d}M", G))
    yy = mbot - 20 - 3 * 24 - 2 * 4
    for a, b, col in rows:
        c.text(x0, yy, a.upper(), "vt", 24, col, lh=1)
        c.text(x0 + 130, yy, b, "vt", 24, Wh, lh=1)
        yy += 28
    # radar
    _pixel_box(c, (362, mtop, 782, mbot))
    rx0, rx1 = 382, 762
    y = mtop + 18
    c.text(rx0, y, ctx.t("Rain radar", "Regen-Radar").upper(), "ps2p", 12, B)
    y += c.line_h("ps2p", 12) + 10
    moon_h = 22
    lab_h = 20
    gbot = mbot - 18 - moon_h - 10 - lab_h - 10
    c.rect((rx0, gbot - 4, rx1, gbot), fill=Wh)
    cw = (rx1 - rx0 - 23 * 3) / 24
    for i, p in enumerate(w["probs"]):
        n = max(1, round(p / 9))
        col = R if i == w["nowh"] else B if p >= 60 else G
        for k in range(n):
            yb = gbot - 4 - 3 - k * 13
            if yb - 10 < y:
                break
            x = rx0 + i * (cw + 3)
            c.rect((x, yb - 10, x + cw, yb), fill=col)
    for i, lbl in enumerate(("00", "06", "12", "18", "24")):
        c.text(rx0 + (rx1 - rx0) * i / 4, gbot + 10, lbl, "vt", 20, Wh, lh=1,
               align="l" if i == 0 else "r" if i == 4 else "c")
    my = mbot - 18 - moon_h
    c.text(rx0, my + 6, ctx.t("Moon", "Mond").upper(), "ps2p", 11, Wh)
    mx = rx0 + c.tw(ctx.t("Moon", "Mond").upper(), "ps2p", 11) + 10
    c.rect((mx, my + 3, mx + 16, my + 19), outline=Wh, width=3)
    if w["phase"] > 0.06 and w["phase"] < 0.94:
        c.rect((mx + 5, my + 8, mx + 11, my + 14), fill=Y)
    c.text(mx + 26, my, w["moon"].upper(), "vt", 22, Wh, lh=1)
    # tip box
    c.rect((18, btop, 782, 462), outline=Wh, width=4)
    tip = advice(ctx, w)
    ts = 28
    while ts > 16 and c.tw("▶ " + tip, "vt", ts) > 680:
        ts -= 1
    c.text(38, btop + 14 + (28 - ts) / 2, "▶ " + tip, "vt", ts, Wh, lh=1)
    for k in range(3):
        _sprite(c, HEART, 700 + k * 18, btop + 22, 2, {"r": R})
    return c.finish()


HERO = ["...yyyyyy...", "..yyyyyyyy..", "..kwwkkwwk..", "..wwwwwwww..", "..wwwwwwww..", "...wwrrww...",
        "....wwww....", "..bbbbbbbb..", ".bbbbbbbbbb.", "wwbbbbbbbbww", "w.bbbbbbbb.w", "..gggggggg..",
        "..gg....gg..", "..kk....kk.."]


def quote_pixel(ctx, kind, text, author):
    c = Canvas("pixel", K)
    seed = [7]

    def rnd():
        seed[0] = (seed[0] * 9301 + 49297) % 233280
        return seed[0] / 233280
    pal = [Wh, Y, B, G]
    for _ in range(34):
        x, y = round(rnd() * 780), round(rnd() * 220)
        s = 8 if rnd() > 0.8 else 4
        col = pal[int(rnd() * len(pal))]
        c.rect((x, y, x + s, y + s), fill=col)
    _sprite(c, HERO, 64, 70)
    d = ctx.today
    c.text(770, 30, f"{ctx.t('Day {n}', 'Tag {n}', n=d.timetuple().tm_yday).upper()} - {numeric_date(d, ctx.lang, year=False)}",
           "ps2p", 12, Y, align="r")
    txt = body(ctx, kind, text) + (f" — {author}" if author else "")
    size, lines, L, _ = c.fit(txt, "vt", 42, 700, 180, lh=1.02)
    lab_h = c.line_h("ps2p", 13)
    arr_h = c.line_h("ps2p", 14)
    inner = 22 + lab_h + 12 + len(lines) * L + 12 + arr_h + 22
    top = 462 - inner - 8
    c.rect((18, top, 782, 462), fill=K)
    _pixel_box(c, (18, top, 782, 462))
    y = top + 4 + 22
    c.text(50, y, label(ctx, kind).upper(), "ps2p", 13, G)
    y += lab_h + 12
    c.para(50, y, 700, lines, "vt", size, L, Wh)
    y += len(lines) * L + 12
    c.text(750, y, "▼", "ps2p", 14, R, align="r")
    return c.finish()


# ================================================================== 5 Zen
def _seal(c, x, y, s, lines):
    c.rrect((x, y, x + s, y + s), 6, fill=R)
    tot = sum(c.line_h(r, sz, 1.05) for _, r, sz, _ in lines)
    yy = y + (s - tot) / 2
    for t, r, sz, tr in lines:
        c.text(x + s / 2 + tr / 2, yy, t, r, sz, Wh, track=tr, lh=1.05, align="c")
        yy += c.line_h(r, sz, 1.05)


def _enso(c, x, y, scale, w1, w2, big=False):
    if big:
        c.path("M 330 96 A 160 160 0 1 0 362 250", stroke=K, width=w1, dx=x, dy=y, sx=scale)
        c.path("M 326 92 A 164 164 0 0 1 350 136", stroke=K, width=w2, dx=x, dy=y, sx=scale)
    else:
        c.path("M 118 38 A 56 56 0 1 0 128 92", stroke=K, width=w1, dx=x, dy=y, sx=scale)
        c.path("M 116 36 A 58 58 0 0 1 124 52", stroke=K, width=w2, dx=x, dy=y, sx=scale)


def weather_zen(ctx, w):
    c = Canvas("zen", Wh)
    _seal(c, 56, 56, 84, [(str(w["day"]), "zk700", 42, 0)])
    vt = f"{w['wd']} · {w['month']}".upper()
    lay, ld = c.layer(c.tw(vt, "zk400", 14, 8) + 4, c.line_h("zk400", 14) + 4)
    c.text(0, 2, vt, "zk400", 14, K, track=8, draw=ld)
    rot = lay.rotate(-90, expand=True)
    c.img.paste(rot, (158, 56), rot)
    temp = f"{w['temp']}°"
    c.text(230, 72, temp, "cg300", 168, K, lh=0.9)
    y = 72 + 168 * 0.9 + 2
    c.text(230, y, lower_first(w["cond"]), "cg400i", 30, K)
    y += c.line_h("cg400i", 30) + 8
    c.text(230, y, f"{w['hi']}° / {w['lo']}° · {w['place']}".upper(), "zk400", 13, K, track=4)
    _enso(c, 586, 58, 1.0, 9, 4)
    c.text(661, 58 + 150 + 10, w["moon"], "cg400i", 20, K, align="c")
    rowh = c.line_h("zk400", 12)
    ry = 480 - 44 - rowh
    gy = ry - 10 - 70
    c.hline(56, 744, gy + 69, K, 1)
    pts = [(56 + i / 23 * 688, gy + 66 - p * 0.75) for i, p in enumerate(w["probs"])]
    c.stroke(pts, B, 2, cap=False)
    nx, ny = pts[w["nowh"]]
    c.circle(nx, ny, 5, fill=R)
    c.text(56, ry, ctx.t("Sun {t}", "Sonne {t}", t=w["sr"]).upper(), "zk400", 12, K, track=4)
    mid = ctx.t("Rain up to {p} % around {h}", "Regen bis {p} % um {h}", p=w["maxp"], h=hour(w["maxh"], ctx.lang)) \
        if w["maxp"] >= 10 else ctx.t("Dry all day", "Den ganzen Tag trocken")
    c.text(400 + 2, ry, mid.upper(), "zk400", 12, K, track=4, align="c")
    c.text(744 + 4, ry, w["ss"], "zk400", 12, K, track=4, align="r")
    return c.finish()


def quote_zen(ctx, kind, text, author):
    c = Canvas("zen", Wh)
    _enso(c, -60, 30, 1.0, 22, 8, big=True)
    lab = label(ctx, kind).upper()
    lab_h = c.line_h("zk400", 12)
    room = 340 - (40 if author else 0)
    size, lines, L, _ = c.fit(body(ctx, kind, text), "cg400i", 40, 400, room, lh=1.18)
    tot = lab_h + 22 + len(lines) * L + 22 + 1 + (22 + c.line_h("cg400i", 22) if author else 0)
    y = (480 - tot) / 2
    c.text(330, y, lab, "zk400", 12, K, track=8)
    y += lab_h + 22
    c.para(330, y, 400, lines, "cg400i", size, L, K)
    y += len(lines) * L + 22
    c.hline(330, 390, y, K, 1)
    if author:
        c.text(330, y + 22, f"— {author}", "cg400i", 22, K)
    mon = C.month(ctx.today, ctx.lang)[:3].upper()
    _seal(c, 800 - 56 - 58, 480 - 44 - 58, 58, [(str(ctx.today.day), "zk700", 18, 0), (mon, "zk700", 11, 1)])
    return c.finish()


# ================================================================== 6 Swiss
SW_X0, SW_COL, SW_GAP = 32, (736 - 80) / 6, 16


def _sx(col):
    return SW_X0 + (col - 1) * (SW_COL + SW_GAP)


def _swiss_head(c, a, b, cc):
    c.rect((32, 28, 768, 34), fill=K)
    for col, t in ((1, a), (3, b), (5, cc)):
        c.text(_sx(col), 42, t, "it500", 13, K)
    return 42 + c.line_h("it500", 13)


def weather_swiss(ctx, w):
    c = Canvas("swiss", Wh)
    top = _swiss_head(c, w["place"], f"{w['wd']} {w['date']}",
                      ctx.t("Week {n}", "Kalenderwoche {n}", n=w["week"])) + 14
    lab_h = c.line_h("it500", 11)
    bot = 452
    r3 = bot - 48 - 4 - lab_h
    r2b = r3 - 14
    c.text(_sx(1) - 2, top, str(w["day"]), "it900", 230, K, track=-12, lh=0.78)
    mh = c.line_h("it700", 34, 1)
    ms = 34
    while ms > 18 and c.tw(w["month"], "it700", ms) > _sx(4) - SW_GAP - _sx(1):
        ms -= 1
    c.text(_sx(1), r2b - mh, w["month"], "it700", ms, K, lh=1)
    x = _sx(4)
    temp = f"{w['temp']}°"
    c.text(x, top, temp, "it900", 120, K, track=-6, lh=0.8)
    sqx = x + c.tw(temp, "it900", 120, -6) + 6 + 14
    c.rect((sqx, top + 6, sqx + 22, top + 28), fill=R)
    y = top + 96 + 10
    c.text(x, y, w["cond"], "it700", 22, K)
    y += c.line_h("it700", 22) + 10
    c.hline(x, 768, y, K, 1)
    y += 1 + 6
    vx = x + (768 - x - 16) / 2 + 16
    rows = ((ctx.t("High", "Höchst"), f"{w['hi']}°"), (ctx.t("Low", "Tiefst"), f"{w['lo']}°"),
            (ctx.t("Sun", "Sonne"), f"{w['sr']}–{w['ss']}"), (ctx.t("Moon", "Mond"), w["moon"]))
    rL = c.line_h("it500", 14)
    for a, b in rows:
        c.text(x, y, a, "it500", 14, K)
        c.text(vx, y, b, "it700", 14, K)
        y += rL + 2
    gb = r3 + 46
    c.rect((32, gb, 768, gb + 2), fill=K)
    bw = (736 - 23 * 2) / 24
    for i, p in enumerate(w["probs"]):
        h = 46 * max(3, p) / 100
        bx = 32 + i * (bw + 2)
        c.rect((bx, gb - h, bx + bw, gb), fill=R if i == w["nowh"] else K)
    ly = gb + 2 + 4
    labels = ("0", "6", ctx.t("Rain % · max {p}", "Regen % · max. {p}", p=w["maxp"]), "18", "24")
    for i, t in enumerate(labels):
        c.text(32 + 736 * i / 4, ly, t, "it500", 11, K, align="l" if i == 0 else "r" if i == 4 else "c")
    return c.finish()


def quote_swiss(ctx, kind, text, author):
    c = Canvas("swiss", Wh)
    d = ctx.today
    top = _swiss_head(c, label(ctx, kind), ctx.t("No. {n}", "Nr. {n}", n=d.timetuple().tm_yday),
                      numeric_date(d, ctx.lang)) + 14
    fL = c.line_h("it500", 13)
    ftop = 452 - fL - 6 - 1
    c.rect((_sx(1), top + 6, _sx(1) + 44, top + 50), fill=R)
    size, lines, L, tr = c.fit(body(ctx, kind, text), "it700", 54, 768 - _sx(2), ftop - 14 - top, lh=1.0, track=-1.5)
    c.para(_sx(2), top, 768 - _sx(2), lines, "it700", size, L, K, tr)
    c.hline(_sx(2), 768, ftop, K, 1)
    left = f"— {author}" if author else ctx.t("Answer: tonight.", "Antwort: heute Abend.")
    c.text(_sx(2), ftop + 7, left, "it500", 13, K)
    c.text(768, ftop + 7, "→", "it500", 13, K, align="r")
    return c.finish()


# ================================================================== 7 Memphis
def _squiggle(c, x, y, col, w=5):
    c.path(f"M {x} {y} q 15 -20 30 0 t 30 0 t 30 0 t 30 0", stroke=col, width=w)


def _hard_box(c, box, shadow, sh, fill=Wh, border=3):
    x0, y0, x1, y1 = box
    c.rect((x0 + sh, y0 + sh, x1 + sh, y1 + sh), fill=shadow)
    c.rect(box, fill=fill)
    c.rect(box, outline=K, width=border)


def _tag(c, text, role, size, track, cx, cy, deg, pad=(6, 12), border=3, shadow=None):
    tw = c.tw(text, role, size, track) - track
    h = c.line_h(role, size)
    bw, bh = tw + 2 * pad[1] + 2 * border, h + 2 * pad[0] + 2 * border
    s = shadow or 0
    lay, ld = c.layer(bw + s + 4, bh + s + 4)
    if shadow:
        ld.rectangle((shadow, shadow, bw + shadow - 1, bh + shadow - 1), fill=K)
    ld.rectangle((0, 0, bw - 1, bh - 1), fill=R, outline=K, width=border)
    c.text(border + pad[1], border + pad[0], text, role, size, Wh, track=track, draw=ld)
    c.paste_rotated(lay, cx, cy, deg)
    return bw, bh


def weather_memphis(ctx, w):
    c = Canvas("memphis", Wh)
    _squiggle(c, 20, 40, B)
    _squiggle(c, 640, 440, R)
    c.stroke([(560, 30), (580, 10), (600, 30), (620, 10), (640, 30), (660, 10), (680, 30)], K, 4, cap=False)
    c.poly([(740, 90), (780, 160), (700, 160)], fill=G, outline=K, width=3)
    for r in range(4):
        for cc in range(5):
            c.circle(40 + cc * 16, 380 + r * 16, 3, fill=K)
    c.circle(170, 200, 120, fill=K)
    c.circle(160, 190, 124, fill=K)
    c.circle(160, 190, 120, fill=Y)
    parts = [(w["wd"].upper(), "r800", 22, 3), (str(w["day"]), "rmo", 108, 0), (f"{C.month(w['today'], ctx.lang)[:3].upper()} {w['year']}", "r800", 20, 3)]
    hs = [c.line_h(r, s, 1 if r == "rmo" else None) for _, r, s, _ in parts]
    y = 190 - sum(hs) / 2
    for (t, r, s, tr), h in zip(parts, hs):
        while s > 12 and c.tw(t, r, s, tr) > 200:
            s -= 1
        c.text(160 + tr / 2, y, t, r, s, K, track=tr, lh=1 if r == "rmo" else None, align="c")
        y += h
    temp = f"{w['temp']}°"
    c.text(338, 68, temp, "rmo", 104, B, lh=1, stroke=2, stroke_fill=B)
    c.text(330, 60, temp, "rmo", 104, Wh, lh=1, stroke=2, stroke_fill=K)
    tx = 330 + c.tw(temp, "rmo", 104) + 18
    cond = w["cond"].upper()
    cs = 18
    while cs > 11 and c.tw(cond, "r800", cs) + 30 > 760 - tx:
        cs -= 1
    tag_h = c.line_h("r800", cs) + 18
    colh = tag_h + 8 + c.line_h("r800", 18)
    cy0 = 60 + (104 - colh) / 2
    bw, bh = c.tw(cond, "r800", cs) + 30, tag_h
    _tag(c, cond, "r800", cs, 0, tx + bw / 2 + 2.5, cy0 + bh / 2 + 2.5, 4, shadow=5)
    c.text(tx, cy0 + tag_h + 8, f"▲ {w['hi']}°  ▼ {w['lo']}°", "r800", 18, K)
    y = 60 + 104 + 12 + 6
    x = 330
    for (lbl, val, sh) in ((ctx.t("Sun", "Sonne"), f"{w['sr']}–{w['ss']}", G), (ctx.t("Moon", "Mond"), w["moon"], Y)):
        bwid = max(c.tw(lbl.upper(), "r700", 12), c.tw(val, "r800", 20)) + 24 + 6
        bh = 3 + 8 + c.line_h("r700", 12) + c.line_h("r800", 20) + 8 + 3
        _hard_box(c, (x, y, x + bwid, y + bh), sh, 5)
        c.text(x + 15, y + 11, lbl.upper(), "r700", 12, K)
        c.text(x + 15, y + 11 + c.line_h("r700", 12), val, "r800", 20, K)
        x += bwid + 12
    box = (330, 320, 760, 430)
    _hard_box(c, box, K, 8)
    c.text(345, 333, ctx.t("Rain today", "Regen heute").upper(), "r800", 12, K)
    gtop = 333 + c.line_h("r800", 12) + 4
    gbot = 430 - 3 - 8
    bw = (430 - 6 - 24 - 23 * 4) / 24
    pal = [B, G, Y]
    for i, p in enumerate(w["probs"]):
        h = (gbot - gtop) * max(8, p) / 100
        bx = 345 + i * (bw + 4)
        col = R if i == w["nowh"] else pal[i % 3]
        c.d.rounded_rectangle((round(bx), round(gbot - h), round(bx + bw) - 1, round(gbot) + 6), 6, fill=col, outline=K, width=2)
    c.rect((333, gbot, 757, 427), fill=Wh)
    return c.finish()


def quote_memphis(ctx, kind, text, author):
    c = Canvas("memphis", Y)
    c.circle(60, 60, 70, fill=B, outline=K, width=4)
    lay, ld = c.layer(130, 130)
    ld.rectangle((20, 20, 109, 109), fill=R, outline=K, width=4)
    c.paste_rotated(lay, 735, 405, -14)
    _squiggle(c, 640, 40, K)
    c.stroke([(30, 440), (50, 420), (70, 440), (90, 420), (110, 440), (130, 420), (150, 440)], G, 5, cap=False)
    c.poly([(720, 180), (760, 250), (680, 250)], fill=Wh, outline=K, width=3)
    lab = label(ctx, kind).upper() + "!"
    tag_h = c.line_h("r800", 15) + 8 + 6
    date_h = c.line_h("rmo", 14)
    txt = body(ctx, kind, text) + (f" — {author}" if author else "")
    size, lines, L, _ = c.fit(txt, "r800", 38, 560 - 68 - 8, 300 - tag_h - date_h - 32, lh=1.12)
    inner = 30 + tag_h + 16 + len(lines) * L + 16 + date_h + 28
    box = (110, 70, 670, 70 + inner + 8)
    _hard_box(c, box, K, 14, border=4)
    tw = c.tw(lab, "r800", 15, 2) - 2 + 24 + 6
    _tag(c, lab, "r800", 15, 2, 148 + tw / 2, 104 + tag_h / 2, 3, pad=(4, 12))
    y = 74 + 30 + tag_h + 16
    c.para(148, y, 560 - 76, lines, "r800", size, L, K)
    y += len(lines) * L + 16
    c.text(148, y, numeric_date(ctx.today, ctx.lang), "rmo", 14, B)
    return c.finish()


# ================================================================== 8 Blueprint
def _bp_grid(c):
    for y in range(0, 480, 20):
        for x in range(0, 800, 4):
            c.d.point((x, y), fill=Wh)
    for x in range(0, 800, 20):
        for y in range(0, 480, 4):
            c.d.point((x, y), fill=Wh)


def _bp_dim(c, x0, x1, y, text):
    c.text(x0, y, "◂", "pm400", 11, Wh)
    c.text(x1, y, "▸", "pm400", 11, Wh, align="r")
    tw = c.tw(text, "pm400", 11)
    mid = (x0 + x1) / 2
    lh = c.line_h("pm400", 11)
    c.text(mid, y, text, "pm400", 11, Wh, align="c")
    c.hline(x0 + 12, mid - tw / 2 - 4, y + lh / 2, Wh, 1)
    c.hline(mid + tw / 2 + 4, x1 - 12, y + lh / 2, Wh, 1)


def _bp_titleblock(c, title, cells):
    """cells: list of rows, each a list of 2 strings (may contain \\n)."""
    x0, x1 = 526, 786
    rows_h = []
    for row in cells:
        n = max(t.count("\n") + 1 for t in row)
        rows_h.append(5 + n * c.line_h("pm400", 11) + 5)
    head_h = 6 + c.line_h("pm600", 13) + 6
    total = 2 + head_h + 1 + sum(rows_h) + (len(rows_h) - 1) + 2
    y0 = 466 - total
    c.rect((x0, y0, x1, 466), fill=B)
    c.rect((x0, y0, x1, 466), outline=Wh, width=2)
    c.text(x0 + 2 + 8, y0 + 2 + 6, title, "pm600", 13, Wh)
    y = y0 + 2 + head_h
    c.hline(x0, x1, y, Wh, 1)
    y += 1
    mid = (x0 + x1) / 2
    for i, (row, h) in enumerate(zip(cells, rows_h)):
        c.vline(mid, y, y + h, Wh, 1)
        for j, t in enumerate(row):
            yy = y + 5
            for ln in t.split("\n"):
                fs = 11
                while fs > 7 and c.tw(ln, "pm400", fs) > (x1 - x0) / 2 - 14:
                    fs -= 1
                c.text((x0 + 2 if j == 0 else mid + 1) + 8, yy, ln, "pm400", fs, Wh)
                yy += c.line_h("pm400", 11)
        y += h
        if i < len(cells) - 1:
            c.hline(x0, x1, y, Wh, 1)
            y += 1


def weather_blueprint(ctx, w):
    c = Canvas("blueprint", B)
    _bp_grid(c)
    c.rect((14, 14, 786, 466), fill=None, outline=Wh, width=2)
    X, Y0 = 16, 16
    x, y = X + 30, Y0 + 26
    c.text(x, y, ctx.t("Fig. 1 – Date", "Fig. 1 – Datum").upper(), "pm400", 12, Wh, track=2)
    y += c.line_h("pm400", 12) + 2
    c.outline_text(x, y, str(w["day"]), "pm300", 150, Wh, lh=0.9)
    y += 135 + 2
    c.text(x, y, f"{w['wds']} · {C.month(w['today'], ctx.lang)[:3]} · {w['year']}".upper(), "pm400", 18, Wh, track=3)
    _bp_dim(c, X + 30, X + 220, Y0 + 220, ctx.t("WK {n}", "KW {n}", n=w["week"]))
    x, y = X + 280, Y0 + 26
    c.text(x, y, ctx.t("Fig. 2 – Temperature / {p}", "Fig. 2 – Temperatur / {p}", p=w["place"]).upper(), "pm400", 12, Wh, track=2)
    y += c.line_h("pm400", 12) + 2
    temp = f"{w['temp']}°"
    c.outline_text(x, y, temp, "pm300", 130, Wh, lh=0.9)
    lx = x + c.tw(temp, "pm300", 130) + 20
    c.vline(lx, y + 8, y + 118, Wh, 1)
    sL = c.line_h("pm400", 14)
    c.text(lx + 11, y + 8, f"MAX {w['hi']}°", "pm400", 14, Wh)
    c.text(lx + 11, y + 8 + 55 - sL / 2, f"Δ {w['hi'] - w['lo']} K", "pm400", 14, Y)
    c.text(lx + 11, y + 118 - sL, f"MIN {w['lo']}°", "pm400", 14, Wh)
    y += 117 + 6
    cond = ctx.t("Condition: {c}", "Zustand: {c}", c=w["cond"]).upper()
    cs = 16
    while cs > 10 and c.tw(cond, "pm400", cs, 1) > 600 - x - 26 + 160:
        cs -= 1
    c.text(x, y, cond, "pm400", cs, Wh, track=1)
    # fig 3 moon
    mx0 = 786 - 2 - 26 - 140
    y = Y0 + 26
    c.text(mx0 + 70 + 1, y, ctx.t("Fig. 3 – Moon", "Fig. 3 – Mond").upper(), "pm400", 12, Wh, track=2, align="c")
    y += c.line_h("pm400", 12) + 6
    cx, cy = mx0 + 70, y + 45
    import math
    for k in range(36):
        if k % 2 == 0:
            a0, a1 = k * 10, k * 10 + 10
            c.d.arc((cx - 34, cy - 34, cx + 34, cy + 34), a0, a1, fill=Wh, width=2)
    c.vline(cx, y + 2, y + 88, Wh, 1)
    c.hline(cx - 43, cx + 43, cy, Wh, 1)
    if 0.06 < w["phase"] < 0.94:
        C.draw_moon(c.d, cx, cy, 30, w["phase"], Wh, B, B)
    c.text(cx, y + 90 + 6, w["moon"].upper(), "pm400", 13, Wh, align="c")
    # fig 4 rain
    fx0, fx1, fy0, fy1 = X + 30, 784 - 290, 464 - 26 - 150, 464 - 26
    c.text(fx0, fy0, ctx.t("Fig. 4 – Precipitation 0–24 h", "Fig. 4 – Niederschlag 0–24 h").upper(), "pm400", 12, Wh, track=2)
    gtop = fy0 + c.line_h("pm400", 12) + 4
    lab = c.line_h("pm400", 10)
    gbot = fy1 - lab - 4
    c.vline(fx0, gtop, gbot, Wh, 1)
    c.hline(fx0, fx1, gbot - 1, Wh, 1)
    bw = (fx1 - fx0 - 1 - 23 * 3) / 24
    for i, p in enumerate(w["probs"]):
        h = (gbot - 1 - gtop) * max(3, p) / 100
        bx = fx0 + 1 + i * (bw + 3)
        col = Y if i == w["nowh"] else Wh
        c.d.line((bx, gbot - 1, bx, gbot - 1 - h, bx + bw - 1, gbot - 1 - h, bx + bw - 1, gbot - 1), fill=col, width=1)
    for i, t in enumerate(("00", "06", "12", "18", "24")):
        c.text(fx0 + (fx1 - fx0) * i / 4, gbot + 4, t, "pm400", 10, Wh, align="l" if i == 0 else "r" if i == 4 else "c")
    _bp_titleblock(c, ctx.t("Daily weather · sheet {n}", "Tageswetter · Blatt {n}", n=w["doy"]).upper(), [
        [f"{ctx.t('Sun up', 'Sonne auf').upper()}\n{w['sr']}", f"{ctx.t('Sun down', 'Sonne ab').upper()}\n{w['ss']}"],
        [ctx.t("Scale 1:1", "Maßstab 1:1").upper(), ctx.t("Drawn: inkyframe", "Gez. inkyframe").upper()]])
    return c.finish()


def quote_blueprint(ctx, kind, text, author):
    c = Canvas("blueprint", B)
    _bp_grid(c)
    c.rect((14, 14, 786, 466), outline=Wh, width=2)
    x0, x1 = 66, 734
    y = 56
    d = ctx.today
    c.text(x0, y, ctx.t("Draft no. {n} – {l}", "Entwurf Nr. {n} – {l}", n=d.timetuple().tm_yday, l=label(ctx, kind)).upper(),
           "pm400", 12, Wh, track=3)
    y += c.line_h("pm400", 12) + 18
    _bp_dim(c, x0, x1, y, ctx.t("Text width {w}", "Textbreite {w}", w=600).upper())
    y += c.line_h("pm400", 11) + 14
    txt = body(ctx, kind, text)
    size, lines, L, _ = c.fit(txt, "pm400", 36, 620, 360 - y - (30 if author else 0), lh=1.25)
    c.para(x0, y, 620, lines, "pm400", size, L, Wh, highlight=longest_word(txt), hfill=Y, underline=6)
    end_x = c.last_line_end(x0, lines, "pm400", size)
    ly = y + (len(lines) - 1) * L + (L - c.line_h("pm400", 11)) / 2
    if end_x + 24 + c.tw(ctx.t("← Start here", "← Hier ansetzen").upper(), "pm400", 11) < 760:
        c.text(end_x + 24, ly, ctx.t("← Start here", "← Hier ansetzen").upper(), "pm400", 11, Y)
    y += len(lines) * L
    if author:
        c.text(x0, y + 10, f"— {author}".upper(), "pm400", 14, Wh, track=2)
    _bp_titleblock(c, ctx.t("Sketch of thought", "Gedankenskizze").upper(),
                   [[ctx.t("Date {d}", "Datum {d}", d=numeric_date(d, ctx.lang)).upper(), "REV. A"]])
    return c.finish()


# ================================================================== 9 Botanical
SPECIMENS = [("Quercus robur", "English oak", "Stieleiche"), ("Fagus sylvatica", "European beech", "Rotbuche"),
             ("Acer platanoides", "Norway maple", "Spitzahorn"), ("Betula pendula", "Silver birch", "Hängebirke"),
             ("Tilia cordata", "Small-leaved lime", "Winterlinde"), ("Fraxinus excelsior", "Ash", "Gemeine Esche"),
             ("Salix alba", "White willow", "Silberweide"), ("Sorbus aucuparia", "Rowan", "Eberesche"),
             ("Carpinus betulus", "Hornbeam", "Hainbuche"), ("Prunus avium", "Wild cherry", "Vogelkirsche"),
             ("Hedera helix", "Ivy", "Efeu"), ("Ginkgo biloba", "Ginkgo", "Ginkgo")]


def _leaf(x, y, s, up=40, length=90):
    tx, ty = x + s * length, y - up
    mx = x + s * length / 2
    return (f"M {x} {y} Q {mx} {y - up - 5} {tx} {ty} Q {mx + s * 5} {y + 10} {x} {y} Z",
            f"M {x} {y} L {tx - s * 8} {ty + 4}")


def weather_botanical(ctx, w):
    c = Canvas("botanical", Wh)
    c.path("M 130 470 C 120 360 150 260 120 140 C 112 100 118 60 130 20", stroke=G, width=3)
    for x, y, s in ((124, 400, -1), (128, 330, 1), (124, 260, -1), (126, 190, 1), (120, 120, -1), (124, 70, 1)):
        leaf, vein = _leaf(x, y, s)
        c.path(leaf, stroke=G, width=2.5)
        c.path(vein, stroke=G, width=1.2)
    c.circle(130, 18, 10, fill=R, outline=K, width=2)
    x = 270
    c.text(x, 40, C.long_date(w["today"], ctx.lang, weekday=True), "lc400i", 18, K)
    y = 40 + c.line_h("lc400i", 18) + 6
    temp = f"{w['temp']}°"
    c.text(x, y, temp, "lc400", 120, K, lh=1)
    base = c._baseline(y, "lc400", 120, 1)
    cx = x + c.tw(temp, "lc400", 120) + 22
    ctop = base - (c._baseline(0, "lc400i", 26, None))
    c.text(cx, ctop, lower_first(w["cond"]) if ctx.lang == "de" else w["cond"], "lc400i", 26, K)
    c.text(cx, ctop + c.line_h("lc400i", 26) + 4,
           ctx.t("high {a}°, {b}° at night", "höchstens {a}°, nachts {b}°", a=w["hi"], b=w["lo"]), "cav", 26, G)
    y = max(y + 120, ctop + c.line_h("lc400i", 26) + 4 + c.line_h("cav", 26)) + 6
    rh = c.line_h("lc400", 15)
    c.hline(x, 760, y, K, 1)
    c.hline(x, 760, y + 1 + 8 + rh + 8, K, 1)
    xx = x
    for t in (f"☼ {w['sr']} – {w['ss']}", ctx.t("Day {h} h {m:02d}", "Tag {h} h {m:02d}", h=w["dh"], m=w["dm"]), f"● {w['moon']}"):
        c.text(xx, y + 9, t, "lc400", 15, K)
        xx += c.tw(t, "lc400", 15) + 26
    y += 1 + 8 + rh + 8 + 1 + 10
    note = ctx.t("Rain through the day – heaviest around {h}", "Regen über den Tag – gegen {h} am stärksten", h=hour(w["maxh"], ctx.lang)) \
        if w["maxp"] >= 20 else ctx.t("Hardly any rain today", "Heute kaum Regen")
    c.text(x, y, note, "cav", 24, K)
    y += c.line_h("cav", 24) + 4
    drop_base = y + 62
    for i, p in enumerate(w["probs"]):
        s = 3 + p / 9
        dx, dy = x + 10 + i * 20, drop_base
        c.path(f"M {dx} {dy - s * 2.4} Q {dx + s} {dy - s * 0.6} {dx} {dy} Q {dx - s} {dy - s * 0.6} {dx} {dy - s * 2.4} Z",
               fill=R if i == w["nowh"] else B)
    # specimen label
    sp = SPECIMENS[w["doy"] % len(SPECIMENS)]
    common = sp[2] if ctx.lang == "de" else sp[1] if ctx.lang == "en" else None
    lines = [(ctx.t("Herbarium of the day", "Herbarium des Tages").upper(), "lc400", 11, 2, 0),
             (f"{sp[0]} – {common}" if common else sp[0], "lc400i", 17, 0, 4),
             (f"{ctx.t('No. {n}', 'No. {n}', n=w['doy'])} · {w['place']} · {ctx.date(w['today'], 'short')}", "cav", 20, 0, 6)]
    h = sum(c.line_h(r, s) + m for _, r, s, _, m in lines) + 20 + 4
    bx0, by1 = 800 - 40 - 282, 480 - 34
    by0 = by1 - h
    c.rect((bx0, by0, 760, by1), fill=Wh, outline=K, width=2)
    yy = by0 + 12
    for t, r, s, tr, m in lines:
        yy += m
        while s > 9 and c.tw(t, r, s, tr) > 250:
            s -= 1
        c.text(bx0 + 16, yy, t, r, s, K, track=tr)
        yy += c.line_h(r, s)
    return c.finish()


def quote_botanical(ctx, kind, text, author):
    c = Canvas("botanical", Wh)
    c.path("M 40 470 C 70 380 60 300 110 230", stroke=G, width=3)
    c.path("M 760 10 C 730 100 740 160 690 240", stroke=G, width=3)
    for x, y, s, up in ((60, 400, 1, 30), (66, 340, -1, 20), (86, 280, 1, 34), (740, 80, -1, -20), (735, 140, 1, -10),
                        (716, 200, -1, -30)):
        tx, ty, mx = x + s * 70, y - up, x + s * 35
        c.path(f"M {x} {y} Q {mx} {y - up - 25} {tx} {ty} Q {mx + s * 5} {y + 8} {x} {y} Z", stroke=G, width=2.5)
    c.circle(110, 226, 9, fill=Y, outline=K, width=2)
    c.circle(690, 244, 9, fill=R, outline=K, width=2)
    y = 60
    c.text(400, y, label(ctx, kind), "cav", 30, G, align="c")
    y += c.line_h("cav", 30) + 18
    foot = ctx.t("Picked on {d}", "Gepflückt am {d}", d=C.long_date(ctx.today, ctx.lang, weekday=False)).upper()
    room = 440 - y - 18 - 7 - 18 - c.line_h("lc400", 13) - (40 if author else 0)
    size, lines, L, _ = c.fit(body(ctx, kind, text), "lc400i", 38, 500, room, lh=1.28)
    c.para(150, y, 500, lines, "lc400i", size, L, K, align="c")
    y += len(lines) * L + 18
    if author:
        c.text(400, y - 8, f"— {author}", "cav", 26, K, align="c")
        y += 32
    c.hline(400 - 10 - 3.5 - 60, 400 - 13.5, y + 3, K, 1)
    c.hline(400 + 13.5, 400 + 73.5, y + 3, K, 1)
    c.circle(400, y + 3.5, 3.5, fill=G)
    y += 7 + 18
    c.text(400 + 1.5, y, foot, "lc400", 13, K, track=3, align="c")
    return c.finish()


# ================================================================== 10 Chalkboard
CHALK_BORDER = "M 18 22 Q 400 12 782 20 Q 790 240 780 460 Q 400 470 20 458 Q 10 240 18 22 Z"


def weather_chalk(ctx, w):
    c = Canvas("chalk", K)
    c.path(CHALK_BORDER, stroke=Wh, width=3)
    c.text(40, 36, w["wd"], "cb", 54, Wh, lh=1)
    c.path("M 30 112 Q 120 104 250 110", stroke=Y, width=3)
    c.text(40, 36 + 54 + 18, C.long_date(w["today"], ctx.lang, weekday=False, year=True), "ph", 28, Wh, lh=1.1)
    c.text(40, 36 + 54 + 18 + 28 * 1.1 + 2, f"{ctx.t('WK {n}', 'KW {n}', n=w['week'])} · {w['moon']}", "ph", 22, Y, lh=1.15)
    # temperature circled in red
    import math
    a = math.radians(-6)
    pts = [(420 + 104 * math.cos(t) * math.cos(a) - 78 * math.sin(t) * math.sin(a),
            140 + 104 * math.cos(t) * math.sin(a) + 78 * math.sin(t) * math.cos(a)) for t in
           [k / 60 * 2 * math.pi for k in range(61)]]
    c.stroke(pts, R, 3, cap=False)
    c.text(425, 72, f"{w['temp']}°", "cb", 104, Wh, lh=1, align="c")
    # doodle
    kind = w["kind"]
    sun = kind in ("sun", "part") or w["code"] in (1, 2, 51, 61, 80)
    if sun:
        c.circle(640, 100, 28, outline=Y, width=3)
        c.path("M 640 52 L 640 36 M 640 148 L 640 164 M 592 100 L 576 100 M 688 100 L 704 100 M 606 66 L 594 54 "
               "M 674 66 L 686 54 M 606 134 L 594 146 M 674 134 L 686 146", stroke=Y, width=3)
    if kind != "sun":
        c.path("M 610 168 q -30 0 -30 -24 q 0 -26 30 -24 q 6 -26 40 -24 q 30 0 34 26 q 26 2 26 24 q 0 22 -26 22 Z",
               fill=K, stroke=Wh, width=3)
    if kind in ("rain", "storm"):
        c.path("M 610 184 l -6 16 M 640 184 l -6 16 M 670 184 l -6 16", stroke=Wh if kind == "rain" else Y, width=3)
    elif kind == "snow":
        for x in (606, 636, 666):
            c.text(x, 180, "*", "ph", 30, Wh)
    # notes
    y = 200
    if w["maxp"] >= 50:
        tip = ctx.t("take an umbrella!", "Schirm mitnehmen!")
    elif w["hi"] >= 25:
        tip = ctx.t("sunglasses on!", "Sonnenbrille auf!")
    elif w["lo"] <= 0:
        tip = ctx.t("wrap up warm!", "warm anziehen!")
    else:
        tip = ctx.t("enjoy the day!", "genieß den Tag!")
    cond = f"• {lower_first(w['cond'])} – {tip}"
    size, lines, L, _ = c.fit(cond, "ph", 24, 560, 2 * 24 * 1.15, lh=1.15)
    for ln in lines:
        c.text(40, y, ln, "ph", size, Wh, lh=1.15)
        y += L + 4
    parts = [("• max. ", Wh), (f"{w['hi']}°", R), (", min. ", Wh), (f"{w['lo']}°", Y)]
    xx = 40
    for t, col in parts:
        c.text(xx, y, t, "ph", 24, col, lh=1.15)
        xx += c.tw(t, "ph", 24)
    y += 24 * 1.15 + 4
    c.text(40, y, "• " + ctx.t("Sun {a} to {b}", "Sonne {a} bis {b}", a=w["sr"], b=w["ss"]), "ph", 24, Wh, lh=1.15)
    c.text(60, 312, ctx.t("Rain today:", "Regen heute:"), "cb", 22, Y)
    pts = [(60 + i / 23 * 680 + (2 if i % 2 else -2), 430 - p * 0.9 + (i % 3 - 1) * 2) for i, p in enumerate(w["probs"])]
    c.stroke(pts, Wh, 3)
    nx, ny = pts[w["nowh"]]
    c.circle(nx, ny, 7, fill=R)
    c.dashed((60, 434, 740, 434), Wh, 2, 8, 6)
    fy = 480 - 16 - c.line_h("ph", 18)
    c.text(60, fy, "0:00", "ph", 18, Wh)
    c.text(400, fy, ctx.t("noon", "Mittag"), "ph", 18, Wh, align="c")
    c.text(740, fy, "24:00", "ph", 18, Wh, align="r")
    return c.finish()


def quote_chalk(ctx, kind, text, author):
    c = Canvas("chalk", K)
    c.path(CHALK_BORDER, stroke=Wh, width=3)
    c.path("M 270 112 Q 400 100 530 110", stroke=Y, width=3)
    c.path("M 270 120 Q 400 110 520 118", stroke=Y, width=2)
    c.path("M 690 360 q 10 -40 40 -36 q 30 6 14 34 q -10 16 -24 26 l 0 18", stroke=R, width=4)
    c.circle(720, 420, 4, fill=R)
    c.path("M 60 380 l 14 -10 l 12 14 l 14 -12 l 12 14 l 14 -12", stroke=G, width=3)
    c.path("M 80 70 l 6 -16 l 6 16 l 16 0 l -13 10 l 5 16 l -14 -10 l -14 10 l 5 -16 l -13 -10 Z", stroke=Y, width=2.5)
    c.text(400, 50, label(ctx, kind), "cb", 46, Wh, align="c")
    fy = 480 - 40 - c.line_h("ph", 22)
    size, lines, L, _ = c.fit(body(ctx, kind, text), "ph", 42, 580, fy - 20 - 150, lh=1.2)
    c.para(110, 150, 580, lines, "ph", size, L, Wh, align="c")
    left = f"— {author}" if author else ctx.t("Answers on the board, please :)", "Antworten bitte an die Tafel :)")
    c.text(110, fy, left, "ph", 22, Y)
    d = ctx.today
    c.text(690, fy, f"{C.weekday_short(d, ctx.lang)}, {numeric_date(d, ctx.lang, year=False)}", "ph", 22, Wh, align="r")
    return c.finish()
