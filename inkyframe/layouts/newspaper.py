"""Newspaper ("Der Rahmen-Anzeiger") signature layouts – ports of /mockups/project/Zeitung-*.dc.html."""
import math

from ..designs import _double_rule, _dropcap_para, _rich_wrap, numeric_date
from ..plugins import _calendar as C
from ..studio import B, G, K, R, Y, Canvas, Wh

X0, X1 = 30, 770
COL = {"black": K, "white": Wh, "red": R, "yellow": Y, "green": G, "blue": B}
INK = {"black": K, "white": K, "red": R, "yellow": K, "green": G, "blue": B}     # readable text colour


# ================================================================== helpers
def _paper():
    return Canvas("newspaper", Wh)


def _ell(c, text, role, size, width, track=0.0):
    """Cut text with an ellipsis so it fits width."""
    if c.tw(text, role, size, track) - track <= width:
        return text
    while text and c.tw(text + "…", role, size, track) - track > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _one_line(c, text, role, max_size, width, min_size=10, track=0.0):
    """Largest size ≤ max_size at which text fits one line (ellipsis at min_size). -> (size, text)."""
    s = max_size
    while s > min_size and c.tw(text, role, s, track) - track > width:
        s -= 1
    return s, _ell(c, text, role, s, width, track)


def _title(ctx):
    return ctx.t("The Daily Frame", "Der Rahmen-Anzeiger")


def _long_date(ctx):
    return C.long_date(ctx.today, ctx.lang, weekday=True, year=True)


def _mast(c, ctx, section):
    """Small masthead (Feuilleton style): title left, date · section right, double rule. -> top of content."""
    hL = c.line_h("pf900", 24)
    t = _title(ctx)
    c.text(X0, 18, t, "pf900", 24, K)
    tw = c.tw(t, "pf900", 24)
    base_off = c._baseline(18, "pf900", 24, None) - c._baseline(0, "ss600", 12, None)
    rt = f"{_long_date(ctx)} · {section}" if section else _long_date(ctx)
    s, rt = _one_line(c, rt, "ss600", 12, X1 - X0 - tw - 20, 9)
    c.text(X1, base_off + (12 - s) * 0.8, rt, "ss600", s, K, align="r")
    y = 18 + hL + 6
    _double_rule(c, X0, X1, y)
    return y + 4


def _big_mast(c, ctx, left, right):
    """Large centred masthead with a three-part date line (as weather_newspaper). -> y below the double rule."""
    s, t = _one_line(c, _title(ctx), "pf900", 40, X1 - X0, 24, 1)
    c.text(400, 18 + (40 - s) / 2, t, "pf900", s, K, track=1, lh=40 / s, align="c")
    y = 18 + 40 + 6
    c.hline(X0, X1, y, K, 1)
    ty = y + 1 + 4
    mid = _long_date(ctx)
    mw = c.tw(mid, "ss600", 12)
    side = (X1 - X0 - mw) / 2 - 12
    c.text(X0, ty, _ell(c, left, "ss400", 12, side), "ss400", 12, K)
    c.text(400, ty, mid, "ss600", 12, K, align="c")
    c.text(X1, ty, _ell(c, right, "ss400", 12, side), "ss400", 12, K, align="r")
    y = ty + c.line_h("ss400", 12) + 6
    _double_rule(c, X0, X1, y)
    return y + 4


def _issue(ctx, place=""):
    s = ctx.t("No. {n}", "Nr. {n}", n=ctx.today.timetuple().tm_yday)
    return f"{s} · {place}" if place else s


def _week(ctx, section):
    wk = ctx.t("WK {n}", "KW {n}", n=ctx.today.isocalendar()[1])
    return f"{section} · {wk}" if section else wk


def _kicker(c, x, y, text, fill=R, size=13, width=None, track=4.0):
    """Spaced small caps label (font-weight 600, letter-spacing 4px, uppercase). -> drawn width."""
    text = text.upper()
    if width is not None:
        while size > 9 and c.tw(text, "ss600", size, track) - track > width:
            size -= 1
            track = max(1.5, track - 0.5)
        text = _ell(c, text, "ss600", size, width, track)
    c.text(x, y, text, "ss600", size, fill, track=track)
    return c.tw(text, "ss600", size, track) - track


def _head(c, x, y, text, width, size=15):
    """Column head: Playfair 700, uppercase, letter-spacing 1.5px."""
    text = text.upper()
    s = size
    while s > 10 and c.tw(text, "pf700", s, 1.5) - 1.5 > width:
        s -= 1
    c.text(x, y, _ell(c, text, "pf700", s, width, 1.5), "pf700", s, K, track=1.5)
    return c.line_h("pf700", size)


def _dots(c, x0, x1, y):
    for xx in range(int(x0), int(x1), 3):
        c.d.point((xx, round(y)), fill=K)


def _rows(c, x0, x1, y, rows, size=14, bottom=None, vfill=None):
    """Label … value rows with dotted rules between them (the mockups' fact boxes). -> y below."""
    rL = c.line_h("ss400", size)
    n = len(rows)
    if bottom is not None:
        n = max(0, min(n, int((bottom - y + 4) // (rL + 8))))
    rows = rows[:n]
    for i, row in enumerate(rows):
        a, b = row[0], row[1]
        fill = row[2] if len(row) > 2 else K
        wb = min(c.tw(b, "ss600", size), (x1 - x0) * 0.62)
        b = _ell(c, b, "ss600", size, wb)
        a = _ell(c, a, "ss400", size, x1 - x0 - wb - 10)
        c.text(x0, y, a, "ss400", size, K)
        c.text(x1, y, b, "ss600", size, fill, align="r")
        if i < len(rows) - 1:
            _dots(c, x0, x1, y + rL + 2)
        y += rL + 4 + 4
    return y - 4


def _hatch(c, x, y, w, h, step=6, fill=K):
    """Diagonal hatching (SVG M0 k L k 0) clipped to the box."""
    k = step
    while k < w + h:
        ax, ay = max(0, k - h), min(k, h)
        bx, by = min(k, w), max(0, k - w)
        c.d.line((x + ax, y + ay - 1, x + bx, y + by), fill=fill, width=1)
        k += step


def _hour_label(h, lang):
    return f"{h} Uhr" if lang == "de" else f"{h:02d}:00"


def _clock(t, lang):
    return f"{t} Uhr" if lang == "de" else t


def _cap(s):
    return s[:1].upper() + s[1:] if s else s


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = _paper()
    top = _mast(c, ctx, ctx.t("Brain teasers", "Denksport")) + 12
    S = 44
    bx, by = 46, top
    # board
    c.rect((bx, by, bx + 8 * S + 4, by + 8 * S + 4), outline=K, width=2)
    last = set(tuple(rc) for rc in (v.get("last_cells") or []))
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            x, y = bx + 2 + col * S, by + 2 + r * S
            if (r + col) % 2 == 1:
                _hatch(c, x, y, S, S)
            if (r, col) in last:
                c.rect((x, y, x + S, y + S), outline=R, width=3)
            chess_puzzle.draw_piece(c.d, p, x + S // 2, y + S // 2, S, ink=K, paper=Wh)
    if v.get("show_coords", True):
        for i, rk in enumerate(v["ranks"]):
            c.text(30, by + 2 + i * S + S / 2 - 8, rk, "ss400i", 11, K, lh=16 / 11)
        for i, f in enumerate(v["files"]):
            c.text(bx + 2 + i * S + S / 2, by + 8 * S + 4 + 3, f, "ss400i", 11, K, align="c")
    # right column
    x0 = bx + 8 * S + 4 + 26
    w = X1 - x0
    y = top
    _kicker(c, x0, y, ctx.t("The puzzle", "Die Aufgabe"), width=w)
    y += c.line_h("ss600", 13) + 10
    size, lines, L, _ = c.fit(v["title"], "pf900", 40, w, 84, lh=1.0, min_size=24)
    lines = lines[:2]
    c.para(x0, y, w, lines, "pf900", size, L, K)
    y += len(lines) * L + 10
    # side to move
    c.hline(x0, X1, y, K, 1)
    tm = v["to_move"]
    s, tm = _one_line(c, tm, "pf700", 24, w - 30, 14)
    bh = c.line_h("pf700", 24)
    sq = y + 1 + 8 + (bh - 20) / 2
    if v.get("white_to_move"):
        c.rect((x0, sq, x0 + 20, sq + 20), fill=Wh, outline=K, width=2)
    else:
        c.rect((x0, sq, x0 + 20, sq + 20), fill=K)
    c.text(x0 + 30, y + 1 + 8 + (24 - s) / 2, tm, "pf700", s, K, lh=bh / s)
    y += 1 + 8 + bh + 8
    c.hline(x0, X1, y, K, 1)
    y += 1 + 10
    # footer (bottom)
    fL = c.line_h("ss400", 13)
    fy = 460 - fL
    c.hline(x0, X1, fy - 7, K, 1)
    src = v.get("source", "")
    sw = c.tw(src, "ss600", 13)
    c.text(X1, fy, src, "ss600", 13, K, align="r")
    c.text(x0, fy, _ell(c, v.get("hint", ""), "ss400i", 13, w - sw - 12), "ss400i", 13, K)
    bottom = fy - 7 - 8
    if v.get("mate"):
        s, mt = _one_line(c, v["mate"], "pf700i", 36, w, 20)
        c.text(x0, y, mt, "pf700i", s, R, lh=36 / s)
        y += 36 + 10
    rows = []
    if v.get("rating"):
        rows.append((ctx.t("Rating", "Wertung"), str(v["rating"])))
    if v.get("moves"):
        rows.append((ctx.t("Solution", "Lösung"),
                     ctx.t("{n} move", "{n} Zug", n=v["moves"]) if v["moves"] == 1
                     else ctx.t("{n} moves", "{n} Züge", n=v["moves"])))
    if v.get("last_text"):
        lt = v["last_text"]
        if v.get("move_number") and v.get("last"):
            n = v["move_number"] if not v.get("white_to_move") else v["move_number"] - 1
            if n >= 1:
                lt = f"{n}.{'' if not v.get('white_to_move') else '..'} {lt}"
        rows.append((ctx.t("Last move", "Letzter Zug"), lt))
    rL = c.line_h("ss400", 14)
    rows_h = len(rows) * (rL + 8) - 4
    if v.get("themes_text"):
        tL = c.line_h("ss400i", 15)
        room = bottom - y - rows_h - 10
        if room >= tL:
            tl = c.wrap(v["themes_text"], "ss400i", 15, w)
            nmax = int(room // tL)
            if len(tl) > nmax:
                tl = tl[:nmax]
                tl[-1] = _ell(c, tl[-1] + " …", "ss400i", 15, w)
            for ln in tl:
                c.text(x0, y, ln, "ss400i", 15, K)
                y += tL
            y += 10
    _rows(c, x0, X1, y, rows, 14, bottom=bottom)
    return c.finish()


# ================================================================== spotify
def _sleeve_art(c, x, y, s=318):
    k = s / 318
    c.rect((x, y, x + s, y + s), fill=B)
    c.rect((x, y + 212 * k, x + s, y + s), fill=K)
    c.circle(x + 200 * k, y + 140 * k, 92 * k, fill=Y)
    c.rect((x + 34 * k, y + 40 * k, x + 56 * k, y + 278 * k), fill=Wh)
    c.rect((x + 70 * k, y + 40 * k, x + 80 * k, y + 278 * k), fill=Wh)
    c.poly([(x + 110 * k, y + 278 * k), (x + 200 * k, y + 150 * k), (x + 290 * k, y + 278 * k)], fill=R)
    c.rect((x, y + 278 * k, x + s, y + 290 * k), fill=Wh)
    c.circle(x + 200 * k, y + 140 * k, 16 * k, fill=K)


def _split_title(t):
    """'Song (Remastered)' / 'Song - Live' -> ('Song', '(Remastered)')."""
    for sep in (" (", " - ", " – "):
        i = t.rfind(sep)
        if i > 0:
            return t[:i], t[i + 1:] if sep == " (" else t[i + 1:]
    return t, ""


def spotify(ctx, v):
    c = _paper()
    top = _mast(c, ctx, ctx.t("Features", "Feuilleton")) + 12
    # sleeve
    c.rect((X0, top, X0 + 330, top + 330), outline=K, width=1)
    ix, iy = X0 + 6, top + 6
    if v.get("image") is not None:
        c.img.paste(ctx.punch(ctx.cover_fit(v["image"], 318, 318)), (ix, iy))
    else:
        _sleeve_art(c, ix, iy)
    cap = ctx.t("Fig.: record sleeve", "Abb.: Plattenhülle")
    q = __import__("inkyframe.i18n", fromlist=["get"]).get(ctx.lang, "QUOTE_MARKS")
    if v.get("album"):
        cap = f"{cap} {q[0]}{v['album']}{q[1]}"
    c.text(X0, top + 330 + 5, _ell(c, cap, "ss400i", 11, 330), "ss400i", 11, K)
    # text column
    x0 = X0 + 330 + 28
    w = X1 - x0
    y = top
    kw = _kicker(c, x0, y, v.get("label", ""), width=w - 30)
    lL = c.line_h("ss600", 13)
    c.hline(x0 + kw + 10, X1, y + lL / 2, K, 1)
    y += lL + 10
    # footer + duration block from the bottom up
    fL = c.line_h("ss400", 13)
    fy = 460 - fL
    c.hline(x0, X1, fy - 7, K, 1)
    tm = _clock(v["now"].strftime("%H:%M") if v.get("now") else v.get("time", ""), ctx.lang)
    tw = c.tw(tm, "ss600", 13)
    c.text(X1, fy, tm, "ss600", 13, K, align="r")
    left = ctx.t("Played in {p}", "Gespielt in {p}", p=v["place"]) if v.get("place") else v.get("date", "")
    c.text(x0, fy, _ell(c, left, "ss400i", 13, w - tw - 12), "ss400i", 13, K)
    dy = fy - 7 - 10 - fL
    bar = dy - 5 - 10
    if v.get("duration_text"):
        c.rect((x0, bar, X1, bar + 10), outline=K, width=1)
        _hatch(c, x0 + 1, bar + 1, w - 2, 8, step=4)
        c.text(x0, dy, ctx.t("Running time", "Spieldauer"), "ss400i", 13, K)
        c.text(X1, dy, v["duration_text"], "ss600", 13, K, align="r")
        bottom = bar - 12
    else:
        c.hline(x0, X1, bar + 4, K, 1)
        c.hline(x0, X1, bar + 7, K, 1)
        bottom = bar - 10
    # facts
    rows = []
    if v.get("album"):
        rows.append((ctx.t("Album", "Album"), v["album"]))
    rows.append((ctx.t("Service", "Dienst"), v.get("source", "Spotify")))
    rL = c.line_h("ss400", 14)
    rows_h = 1 + 8 + len(rows) * (rL + 8) - 4
    by_h = c.line_h("pf400i", 24)
    artist = ctx.t("by {a}", "von {a}", a=v["artist"]) if v.get("artist") else ""
    room = bottom - rows_h - 10 - (by_h + 10 if artist else 0) - y
    main, extra = _split_title(v["track"])
    size = 40
    while True:
        segs = [(main, "pf900", size, K)] + ([(extra, "pf700i", size, R)] if extra else [])
        lines = _rich_wrap(c, segs, w)
        L = size * 1.04
        if len(lines) * L <= room or size <= 18:
            break
        size -= 2
    nmax = max(1, int(room // L))
    if len(lines) > nmax:
        lines = lines[:nmax]
        wd, role, sz, fill = lines[-1][-1]
        lines[-1][-1] = (wd + "…", role, sz, fill)
    for ln in lines:
        x = x0
        for wd, role, sz, fill in ln:
            wd = _ell(c, wd, role, sz, X1 - x, -0.3)
            c.text(x, y, wd, role, sz, fill, track=-0.3, lh=1.04)
            x += c.tw(wd, role, sz, -0.3) + c.tw(" ", role, sz)
        y += L
    y += 10
    if artist:
        s, artist = _one_line(c, artist, "pf400i", 24, w, 14)
        c.text(x0, y, artist, "pf400i", s, K, lh=by_h / s)
        y += by_h + 10
    c.hline(x0, X1, y, K, 1)
    _rows(c, x0, X1, y + 1 + 8, rows, 14)
    return c.finish()


# ================================================================== grid
def _grid_advice(ctx, color):
    if color == "green":
        return ctx.t("Plenty of green power – a good time to wash, charge and run the dishwasher.",
                     "Viel Ökostrom im Netz – jetzt waschen, laden, spülen.")
    if color == "yellow":
        return ctx.t("Mixed power – shift big loads if you can.",
                     "Gemischter Strom – große Verbraucher besser verschieben.")
    return ctx.t("Lots of fossil power – better wait with big loads.",
                 "Viel fossiler Strom – große Verbraucher besser später.")


def grid(ctx, v):
    c = _paper()
    y = _big_mast(c, ctx, _issue(ctx, v.get("place", "")), _week(ctx, ctx.t("Energy", "Energie"))) + 10
    color = v.get("color") or "red"
    # hero: the light + headline
    kL = c.line_h("ss600", 13)
    name = _cap(v.get("signal_name") or "–")
    tail = ctx.t("{p} green power", "{p} Ökostrom", p=v["share_text"]) if v.get("share_text") else ""
    hx = X0 + 62 + 22
    hw = X1 - hx
    size = 46
    while True:
        segs = [(name, "pf900", size, INK.get(color, K))]
        if tail:
            segs += [("–", "pf900", size, K), (tail, "pf700i", size, K)]
        lines = _rich_wrap(c, segs, hw)
        if len(lines) <= 1 or size <= 26:
            break
        size -= 2
    lines = lines[:2]
    hL = size * 1.02
    adv = _grid_advice(ctx, color)
    aL = c.line_h("ss400i", 15)
    asz, alines, aL, _ = c.fit(adv, "ss400i", 15, hw, aL * 2, lh=None, min_size=12)
    aL = c.line_h("ss400i", asz)
    alines = alines[:2]
    text_h = kL + 6 + len(lines) * hL + 6 + len(alines) * aL
    box_h = max(8 + 3 * 40 + 2 * 7 + 8, text_h)
    c.rect((X0, y, X0 + 62, y + box_h), fill=K)
    cy0 = y + (box_h - (3 * 40 + 14)) / 2
    for i, lt in enumerate(v.get("lights") or []):
        cx, cy = X0 + 31, cy0 + 20 + i * 47
        if lt.get("on"):
            c.circle(cx, cy, 20, fill=COL.get(lt.get("color"), Wh))
        c.circle(cx, cy, 20, outline=Wh, width=2)
    ty = y + (box_h - text_h) / 2
    _kicker(c, hx, ty, ctx.t("The grid light", "Die Netz-Ampel"), width=hw)
    ty += kL + 6
    for ln in lines:
        x = hx
        for wd, role, sz, fill in ln:
            c.text(x, ty, wd, role, sz, fill, track=-0.5, lh=1.02)
            x += c.tw(wd, role, sz, -0.5) + c.tw(" ", role, sz)
        ty += hL
    ty += 6
    for ln in alines:
        c.text(hx, ty, ln, "ss400i", asz, K)
        ty += aL
    y += box_h + 10
    # two columns
    c.hline(X0, X1, y, K, 1)
    gtop = y + 1
    fL = c.line_h("ss400i", 11)
    gbot = 460 - fL - 4
    cw = (X1 - X0) / 3
    c.vline(X0 + cw - 1, gtop, gbot, K, 1)
    # column 1: timetable of the colour runs from now on
    x0, x1 = X0, X0 + cw - 1 - 16
    hh = _head(c, x0, gtop + 10, ctx.t("Timetable", "Fahrplan"), x1 - x0)
    yy = gtop + 10 + hh + 4
    segs = v.get("segments") or []
    k0 = next((i for i, s in enumerate(segs) if s.get("now")), 0)
    segs = segs[k0:]
    rows = []
    for i, s in enumerate(segs):
        if i == 0:
            lab = ctx.t("until {t}", "bis {t}", t=_clock(s["to"], ctx.lang))
        elif s["to"] in ("24:00", "00:00") or s["end"] >= 24:
            lab = ctx.t("from {t}", "ab {t}", t=_clock(s["from"], ctx.lang))
        else:
            lab = f"{s['from']} – {s['to']}"
        rows.append((lab, _cap(s.get("name", "")), INK.get(s.get("color"), K)))
    _rows(c, x0, x1, yy, rows, 14, bottom=gbot - 4)
    # column 2: the day as a 24-hour band
    x0, x1 = X0 + cw + 16, X1
    hh = _head(c, x0, gtop + 10, ctx.t("The day on the grid", "Der Tag im Netz"), x1 - x0)
    legL = c.line_h("ss400", 12)
    leg_y = gbot - legL
    c.hline(x0, x1, leg_y - 5, K, 1)
    axL = c.line_h("ss400i", 11)
    ax_y = leg_y - 5 - 5 - axL
    band_b = ax_y - 5
    band_t = band_b - 34
    c.rect((x0, band_t, x1, band_b), outline=K, width=1)
    bw = (x1 - x0 - 6 - 23) / 24
    for i, hr in enumerate((v.get("hours") or [])[:24]):
        col = COL.get(hr.get("color"))
        if col is not None:
            xx = x0 + 3 + i * (bw + 1)
            c.rect((xx, band_t + 3, xx + bw, band_b - 3), fill=col)
    nx = x0 + (x1 - x0) * v.get("now_pos", 0)
    lab_top = gtop + 10 + hh + 6
    if v.get("best_text"):
        bs, bl, bL, _ = c.fit(v["best_text"], "ss400i", 14, x1 - x0, band_t - 22 - lab_top, lh=1.25, min_size=11)
        c.para(x0, lab_top, x1 - x0, bl[:2], "ss400i", bs, bL, K)
    c.rect((nx - 1, band_t - 20, nx + 1, band_b), fill=K)
    nl = f"{ctx.t('Now', 'Jetzt')} {v.get('time', '')}"
    nw = c.tw(nl, "ss600", 12)
    if nx + 6 + nw <= x1:
        c.text(nx + 6, band_t - 20, nl, "ss600", 12, K)
    else:
        c.text(nx - 6, band_t - 20, nl, "ss600", 12, K, align="r")
    for k, h in enumerate((0, 6, 12, 18, 24)):
        t = _hour_label(0, ctx.lang) if h == 0 else str(h)
        al = "l" if k == 0 else "r" if k == 4 else "c"
        c.text(x0 + (x1 - x0) * h / 24, ax_y, t, "ss400i", 11, K, align=al)
    xx = x0
    for key in ("green", "yellow", "red"):
        nm = _cap(ctx.t(key, {"green": "grün", "yellow": "gelb", "red": "rot"}[key]))
        c.rect((xx, leg_y + (legL - 11) / 2, xx + 11, leg_y + (legL - 11) / 2 + 11), fill=COL[key])
        c.text(xx + 16, leg_y, nm, "ss400", 12, K)
        xx += 16 + c.tw(nm, "ss400", 12) + 14
    # credit (CC BY 4.0)
    c.text(X1, 460 - fL, _ell(c, v.get("source", ""), "ss400i", 11, X1 - X0), "ss400i", 11, K, align="r")
    return c.finish()


# ================================================================== wordclock
def wordclock(ctx, v):
    c = _paper()
    top = _mast(c, ctx, ctx.t("The time", "Die Uhrzeit")) + 12
    bottom = 460
    # centre: the letter grid in a double-ruled box
    bx0, bx1 = 210, 590
    by0 = top
    by1 = min(bottom, top + 380)
    c.rect((bx0, by0, bx1, by1), outline=K, width=1)
    c.rect((bx0 + 3, by0 + 3, bx1 - 3, by1 - 3), outline=K, width=1)
    rows, cols = v.get("rows") or len(v["grid"]), v.get("cols") or len(v["grid"][0])
    iw, ih = bx1 - bx0 - 28, by1 - by0 - 28
    cw = iw / cols
    ch = min(34.0, ih / rows)
    gy = by0 + 14 + (ih - ch * rows) / 2
    lit = set(tuple(x) for x in v.get("lit") or [])
    big = min(25, round(ch * 0.74))
    small = min(15, round(ch * 0.44))
    for r, line in enumerate(v["grid"]):
        for k, chh in enumerate(line):
            cx = bx0 + 14 + k * cw + cw / 2
            on = (r, k) in lit
            role, size, fill = ("pf900", big, R) if on else ("ss400", small, K)
            Lh = c.line_h(role, size)
            c.text(cx, gy + r * ch + (ch - Lh) / 2, chh, role, size, fill, align="c")
    # left column
    x0, x1 = X0, X0 + 158 - 1 - 16
    c.vline(X0 + 158 - 1, top, bottom, K, 1)
    w = x1 - x0
    y = top
    _kicker(c, x0, y, ctx.t("Today", "Heute"), width=w, track=3)
    y += c.line_h("ss600", 13) + 8
    s, wd = _one_line(c, v["weekday"], "pf900", 28, w, 16)
    c.text(x0, y + (28 - s) * 0.7, wd, "pf900", s, K, lh=28 / s)
    y += 28 + 8
    ds = C.long_date(v["today"], ctx.lang, weekday=False, year=True)
    dsz, dl, dL, _ = c.fit(ds, "pf400i", 20, w, 2 * 20 * 1.15, lh=1.15, min_size=13)
    c.para(x0, y, w, dl[:2], "pf400i", dsz, dL, K)
    y += len(dl[:2]) * dL + 8
    c.hline(x0, x1, y, K, 1)
    y = _rows(c, x0, x1, y + 1 + 8, [(ctx.t("Week", "Woche"), ctx.t("WK {n}", "KW {n}", n=v["week"])),
                                     (ctx.t("Day", "Tag"), str(v["day_of_year"]))], 14)
    ph = v.get("phrase", "")
    if ph:
        ph = ph[:1].upper() + ph[1:] + "."
        room = bottom - y - 12
        psz, pl, pL, _ = c.fit(ph, "ss400i", 13, w, room, lh=1.35, min_size=10)
        nmax = max(0, int(room // pL))
        pl = pl[:nmax]
        c.para(x0, bottom - len(pl) * pL, w, pl, "ss400i", psz, pL, K)
    # right column
    x0 = 612 + 1 + 16
    c.vline(612, top, bottom, K, 1)
    w = X1 - x0
    y = top
    _kicker(c, x0, y, ctx.t("The hour", "Die Stunde"), width=w, track=3)
    y += c.line_h("ss600", 13) + 10
    q = v["minute"] // 15
    for i in range(4):
        cx = x0 + 8 + i * 26
        if i < q:
            c.circle(cx, y + 8, 8, fill=R)
        else:
            c.circle(cx, y + 8, 8, outline=K, width=1)
    y += 16 + 10
    c.text(x0, y, v["time"], "pf700", 28, K, lh=1)
    y += 28 + 10
    c.hline(x0, X1, y, K, 1)
    y += 1 + 10
    hh = _head(c, x0, y, ctx.t("The moon", "Der Mond"), w)
    y += hh + 8
    C.draw_moon(c.d, int(x0 + 31), int(y + 31), 29, v["phase"], Wh, K, K)
    c.circle(x0 + 31, y + 31, 29, outline=K, width=2)
    y += 62 + 8
    nm = v.get("moon", "")
    nsz, nl, nL, _ = c.fit(nm, "ss600", 14, w, 2 * 20, lh=1.4, min_size=11)
    c.para(x0, y, w, nl[:2], "ss600", nsz, nL, K)
    y += len(nl[:2]) * nL
    pct = round((1 - math.cos(2 * math.pi * v["phase"])) / 2 * 100)
    if y + 20 <= bottom:
        c.text(x0, y, _ell(c, ctx.t("{n} % lit", "{n} % beleuchtet", n=pct), "ss400i", 14, w), "ss400i", 14, K, lh=1.4)
    return c.finish()


# ================================================================== countdown
def _plural(ctx, n, one, many, one_de, many_de):
    return ctx.t(one, one_de, n=n) if n == 1 else ctx.t(many, many_de, n=n)


def countdown(ctx, v):
    c = _paper()
    y = _big_mast(c, ctx, _issue(ctx, v.get("place", "")), _week(ctx, ctx.t("Special edition", "Sonderausgabe"))) + 10
    strip = v.get("strip") or []
    acc = COL.get(v.get("color") or "", R)
    if acc in (Wh, Y):
        acc = R
    # bottom: the strip of days
    bottom = 460
    if strip:
        lgL = c.line_h("ss400i", 11)
        mL = c.line_h("pf700", 12)
        cell_t = bottom - lgL - 3 - 26
        m_t = cell_t - 3 - mL
        rule = m_t - 8 - 1
        c.hline(X0, X1, rule, K, 1)
        n = len(strip)
        gap = 1 if n <= 62 else 0
        cw = (X1 - X0 - gap * (n - 1)) / n
        xs = [X0 + i * (cw + gap) for i in range(n)]
        for i, e in enumerate(strip):
            x = xs[i]
            bg, fg, role = (Y if e["weekend"] else Wh), K, "ss400"
            if e["today"]:
                bg, fg, role = acc, Wh, "ss600"
            elif e["target"]:
                bg, fg, role = K, Wh, "ss600"
            if gap:
                c.rect((x, cell_t, x + cw, cell_t + 26), fill=bg, outline=K, width=1)
            else:
                c.rect((x, cell_t, x + cw, cell_t + 26), fill=bg)
            if cw >= 13:
                c.text(x + cw / 2, cell_t + (26 - c.line_h(role, 11)) / 2, str(e["day"]), role, 11, fg, align="c")
        if not gap:
            c.rect((X0, cell_t, X1, cell_t + 26), outline=K, width=1)
        # month labels
        starts = [i for i, e in enumerate(strip) if i == 0 or e["first_of_month"]]
        for k, i in enumerate(starts):
            j = starts[k + 1] if k + 1 < len(starts) else n
            x, xe = xs[i], xs[j - 1] + cw
            if k:
                c.vline(x - gap, m_t, m_t + mL, K, 1)
            name = C.month(strip[i]["date"], ctx.lang).upper()
            room = xe - x - (4 if k else 0) - 2
            if room > 24:
                c.text(x + (4 if k else 0), m_t, _ell(c, name, "pf700", 12, room, 1.5), "pf700", 12, K, track=1.5)
        a = ctx.t("today", "heute")
        b = v.get("event", "")
        if v.get("state") == "past":
            a, b = b, a
        mid = ctx.t("weekends in yellow", "Wochenenden gelb")
        mw = c.tw(mid, "ss400i", 11)
        side = (X1 - X0 - mw) / 2 - 10
        ly = bottom - lgL
        c.text(X0, ly, _ell(c, a, "ss400i", 11, side), "ss400i", 11, K)
        c.text(400, ly, mid, "ss400i", 11, K, align="c")
        c.text(X1, ly, _ell(c, b, "ss400i", 11, side), "ss400i", 11, K, align="r")
        bottom = rule - 10
    # middle: big figure + text block
    big = v.get("big", "")
    numeric = big.isdigit()
    bsz = 210 if numeric else 90
    maxw = 330
    while bsz > 40 and c.tw(big, "pf900", bsz, -6 * bsz / 210) > maxw:
        bsz -= 4
    tr = -6 * bsz / 210
    bw = c.tw(big, "pf900", bsz, tr) - tr
    tx = X0 + bw + 26
    tw = X1 - tx - 24 - 1
    # text block
    kL = c.line_h("ss600", 13)
    state = v.get("state")
    kick = {"future": ctx.t("Still to wait", "Noch zu warten"), "past": ctx.t("Already behind us", "Schon vorbei"),
            "today": ctx.t("The day has come", "Der Tag ist da")}.get(state, "")
    small, ev = v.get("small", ""), v.get("event", "")
    room_h = bottom - y
    line2 = f"{v.get('target_weekday', '')}, {v.get('date', '')}"
    lab2 = ctx.t("Date:", "Datum:")
    l2 = c.line_h("ss400", 16)
    extra = ""
    if state != "today" and strip:
        work = sum(1 for e in strip[1:] if not e["weekend"] and not e["special"]) if state == "future" else \
            sum(1 for e in strip[:-1] if not e["weekend"] and not e["special"])
        parts = []
        if v.get("weeks"):
            parts.append(_plural(ctx, v["weeks"], "{n} week", "{n} weeks", "{n} Woche", "{n} Wochen"))
        if v.get("rest_days") or not parts:
            parts.append(_plural(ctx, v.get("rest_days") or v["count"], "{n} day", "{n} days", "{n} Tag", "{n} Tage"))
        a = parts[0] if len(parts) == 1 else ctx.t("{a} and {b}", "{a} und {b}", a=parts[0], b=parts[1])
        extra = ctx.t("That makes {a} – or {n} working days.", "Das sind {a} – oder {n} Werktage.", a=a, n=work)
    eL = c.line_h("ss400i", 14)
    fixed = kL + 10 + 10 + 1 + 8 + l2 + (10 + eL * 2 if extra else 0)
    size = 44
    while True:
        segs = ([(small, "pf900", size, K)] if small else []) + ([(ev, "pf700i", size, K)] if ev else [])
        lines = _rich_wrap(c, segs, tw) if segs else []
        if fixed + len(lines) * size * 1.02 <= room_h or size <= 22:
            break
        size -= 2
    hL = size * 1.02
    nmax = max(1, int((room_h - fixed) // hL))
    if len(lines) > nmax:
        lines = lines[:nmax]
        wd, role, sz, fill = lines[-1][-1]
        lines[-1][-1] = (wd + "…", role, sz, fill)
    ex_lines = c.wrap(extra, "ss400i", 14, tw)[:2] if extra else []
    block = kL + 10 + len(lines) * hL + 10 + 1 + 8 + l2 + ((10 + eL * len(ex_lines)) if ex_lines else 0)
    by = y + (room_h - block) / 2
    # big figure, vertically centred
    if numeric:
        bh = bsz * 0.82
        c.text(X0, y + (room_h - bh) / 2, big, "pf900", bsz, acc, track=tr, lh=0.82)
    else:
        bl = c.wrap(big, "pf900", bsz, maxw)
        c.para(X0, y + (room_h - len(bl) * bsz) / 2, maxw, bl, "pf900", bsz, bsz, acc)
    c.vline(tx - 1, by, by + block, K, 1)
    x0 = tx + 24
    yy = by
    _kicker(c, x0, yy, kick, width=tw)
    yy += kL + 10
    for ln in lines:
        x = x0
        for wd, role, sz, fill in ln:
            wd = _ell(c, wd, role, sz, x0 + tw - x, -0.5)
            c.text(x, yy, wd, role, sz, fill, track=-0.5, lh=1.02)
            x += c.tw(wd, role, sz, -0.5) + c.tw(" ", role, sz)
        yy += hL
    yy += 10
    c.hline(x0, x0 + tw, yy, K, 1)
    yy += 1 + 8
    lw = c.tw(lab2 + " ", "ss400", 16)
    c.text(x0, yy, lab2, "ss400", 16, K)
    c.text(x0 + lw, yy, _ell(c, line2, "ss600", 16, tw - lw), "ss600", 16, K)
    yy += l2
    if ex_lines:
        yy += 10
        c.para(x0, yy, tw, ex_lines, "ss400i", 14, eL, K)
    return c.finish()


# ================================================================== art
def art(ctx, v):
    c = _paper()
    top = _mast(c, ctx, ctx.t("Arts & culture", "Kunst & Kultur")) + 12
    img = v["image"]
    capL = c.line_h("ss400i", 12)
    max_w, max_h = 478, 318
    k = min(max_w / img.width, max_h / img.height)
    iw, ih = max(1, round(img.width * k)), max(1, round(img.height * k))
    fw, fh = iw + 20, ih + 20
    fx, fy = X0, top
    c.rect((fx, fy, fx + fw, fy + fh), outline=K, width=1)
    c.rect((fx + 3, fy + 3, fx + fw - 3, fy + fh - 3), outline=K, width=1)
    c.img.paste(img.convert("RGB").resize((iw, ih)), (fx + 10, fy + 10))
    fig = ctx.t("Fig. 1", "Abb. 1")
    lw = c.tw(fig, "ss400i", 12) + 16
    if iw > lw + 40 and ih > 60:
        c.rect((fx + 10 + 22, fy + 10 + 20, fx + 10 + 22 + lw, fy + 10 + 40), fill=Wh)
        c.text(fx + 10 + 22 + lw / 2, fy + 10 + 20 + (20 - capL) / 2, fig, "ss400i", 12, K, align="c")
    cap = " · ".join(x for x in (v.get("artist"), v.get("work"), v.get("date"), v.get("museum")) if x)
    cw = max(fw, 200)
    cl = c.wrap(cap, "ss400i", 12, cw)
    room = int((460 - (fy + fh + 6)) // capL)
    if len(cl) > room:
        cl = cl[:max(1, room)]
        cl[-1] = _ell(c, cl[-1] + " …", "ss400i", 12, cw)
    c.para(fx, fy + fh + 6, cw, cl, "ss400i", 12, capL, K)
    # text column
    x0 = fx + max(fw, 200) + 24
    w = X1 - x0
    y = top
    _kicker(c, x0, y, v.get("title", ""), width=w, track=3)
    y += c.line_h("ss600", 13) + 10
    # footer note from the bottom
    note = ", ".join(x for x in (v.get("museum"), v.get("museum_city")) if x)
    if v.get("license"):
        note = f"{note} · {v['license']}" if note else v["license"]
    nL = 13 * 1.4
    nl = c.wrap(note, "ss400i", 13, w)[:3] if note else []
    fy0 = 460 - len(nl) * nL
    if nl:
        c.hline(x0, X1, fy0 - 6 - 1, K, 1)
        c.para(x0, fy0, w, nl, "ss400i", 13, nL, K)
    bottom = fy0 - 6 - 1 - 10
    rows = []
    for key, en, de in (("date", "Created", "Entstanden"), ("medium", "Medium", "Technik"),
                        ("dimensions", "Size", "Maße"), ("origin", "Origin", "Herkunft")):
        val = (v.get(key) or "").strip()
        if key == "dimensions" and " (" in val:
            val = val[:val.index(" (")]
        if val:
            rows.append((ctx.t(en, de), val))
    rL = c.line_h("ss400", 14)
    rows_h = len(rows) * (rL + 8) - 4 if rows else 0
    artist = (v.get("artist") or "").upper()
    aL = c.line_h("pf700", 16)
    al = c.wrap(artist, "pf700", 16, w, 1.5)[:2] if artist else []
    a_h = (1 + 8 + len(al) * aL + 10) if al else 0
    room = bottom - y - a_h - rows_h
    size, tl, L, _ = c.fit(v.get("work", ""), "pf700i", 32, w, max(room - 10, 40), lh=1.05, min_size=18)
    nmax = max(1, int((room - 10) // L))
    if len(tl) > nmax:
        tl = tl[:nmax]
        tl[-1] = _ell(c, tl[-1] + " …", "pf700i", size, w)
    c.para(x0, y, w, tl, "pf700i", size, L, K)
    y += len(tl) * L + 10
    if al:
        c.hline(x0, X1, y, K, 1)
        y += 1 + 8
        for ln in al:
            c.text(x0, y, _ell(c, ln, "pf700", 16, w, 1.5), "pf700", 16, K, track=1.5)
            y += aL
        y += 10
    _rows(c, x0, X1, y, rows, 14, bottom=bottom)
    return c.finish()


# ================================================================== waste
def _bin(c, x, y, w, fill, sw=2, line=None, lid=True):
    """The mockup's bin (viewBox 70×92) scaled to width w at (x, y)."""
    k = w / 70
    edge = K
    line = line if line is not None else (K if fill in (Y, Wh) else Wh)
    c.rect((x + 2 * k, y + 6 * k, x + 68 * k, y + 16 * k), fill=fill, outline=edge, width=max(1, round(sw)))
    if lid:
        c.rect((x + 26 * k, y + 1 * k, x + 44 * k, y + 7 * k), fill=K)
    pts = [(x + 7 * k, y + 18 * k), (x + 63 * k, y + 18 * k), (x + 58 * k, y + 88 * k), (x + 12 * k, y + 88 * k)]
    c.poly(pts, fill=fill)
    c.d.polygon([(round(a), round(b)) for a, b in pts], outline=edge, width=max(1, round(sw)))
    xs = (21, 34, 47) if lid else (22, 42)
    lw = 3 if lid else 6
    for lx in xs:
        c.rect((x + lx * k, y + (28 if lid else 30) * k, x + (lx + lw) * k, y + (78 if lid else 76) * k), fill=line)


def waste(ctx, v):
    c = _paper()
    y = _mast(c, ctx, ctx.t("Local news", "Aus der Stadt")) + 12
    # centred kicker between rules
    kL = c.line_h("ss600", 13)
    kt = f"{ctx.t('Official notice', 'Amtliche Bekanntmachung')} · {v['title']}".upper()
    ks, ktr = 13, 4.0
    while ks > 9 and c.tw(kt, "ss600", ks, ktr) - ktr > X1 - X0 - 80:
        ks -= 1
        ktr = max(1.5, ktr - 0.5)
    kt = _ell(c, kt, "ss600", ks, X1 - X0 - 80, ktr)
    kw = c.tw(kt, "ss600", ks, ktr) - ktr
    c.text(400, y + (kL - c.line_h("ss600", ks)) / 2, kt, "ss600", ks, R, track=ktr, align="c")
    c.hline(X0, 400 - kw / 2 - 12, y + kL / 2, K, 1)
    c.hline(400 + kw / 2 + 12, X1, y + kL / 2, K, 1)
    y += kL + 12
    soon = v.get("soon")
    rows = list(v.get("rows") or [])
    if soon:
        bins = [COL.get(it["color"], K) for it in soon["items"]]
        lead, names = soon["label"] + ":", soon["names_text"]
        sub = soon["date_long"]
        if not soon.get("is_today"):
            sub += " – " + ctx.t("Please put the bins out tonight.", "Tonnen bitte heute Abend an die Straße stellen.")
    else:
        first = rows.pop(0)
        same = [first] + [r for r in rows if r["date"] == first["date"]]
        rows = [r for r in rows if r["date"] != first["date"]]
        bins = [COL.get(it["color"], K) for it in same]
        lead = _cap(first["in_text"]) + ":"
        names = " + ".join(it["name"] for it in same)
        sub = first["date_long"]
    nb = min(3, len(bins))
    bx = X0
    hx = X0 + nb * 70 + (nb - 1) * 10 + 24
    hw = X1 - hx
    size = 44
    while True:
        lines = _rich_wrap(c, [(lead, "pf700i", size, R), (names, "pf900", size, K)], hw)
        if len(lines) <= 2 or size <= 24:
            break
        size -= 2
    lines = lines[:2]
    hL = size * 1.02
    sL = c.line_h("ss400i", 14)
    sub_l = c.wrap(sub, "ss400i", 14, hw)[:2]
    th = len(lines) * hL + 4 + len(sub_l) * sL
    hh = max(92, th)
    for i in range(nb):
        _bin(c, bx + i * 80, y + (hh - 92) / 2, 70, bins[i])
    ty = y + (hh - th) / 2
    for ln in lines:
        x = hx
        for wd, role, sz, fill in ln:
            wd = _ell(c, wd, role, sz, X1 - x, -0.5)
            c.text(x, ty, wd, role, sz, fill, track=-0.5, lh=1.02)
            x += c.tw(wd, role, sz, -0.5) + c.tw(" ", role, sz)
        ty += hL
    ty += 4
    for ln in sub_l:
        c.text(hx, ty, ln, "ss400i", 14, K)
        ty += sL
    y += hh + 12
    # table
    c.hline(X0, X1, y, K, 1)
    y += 1 + 6
    thL = c.line_h("pf700", 13)
    wdate, win = 130, 130
    for w0 in (r["date_text"] for r in rows):
        wdate = max(wdate, c.tw(w0, "ss600", 18) + 12)
    wdate = min(wdate, 170)
    cols = (X0 + 48, X0 + 48 + wdate, X1)
    _head(c, cols[0], y, ctx.t("Date", "Termin"), wdate - 8, 13)
    _head(c, cols[1], y, ctx.t("Type of waste", "Abfallart"), X1 - cols[1] - win - 8, 13)
    nt = ctx.t("Due", "Noch").upper()
    c.text(X1, y, _ell(c, nt, "pf700", 13, win, 1.5), "pf700", 13, K, track=1.5, align="r")
    y += thL + 4
    c.hline(X0, X1, y, K, 1)
    y += 1
    room = 460 - y
    if not rows:
        c.text(400, y + (room - c.line_h("ss400i", 16)) / 2, _ell(c, v.get("empty_text", ""), "ss400i", 16, X1 - X0),
               "ss400i", 16, K, align="c")
        return c.finish()
    n = min(len(rows), max(1, int(room // 38)))
    rows = rows[:n]
    rh = min(room / n, 64)
    for i, r in enumerate(rows):
        ry = y + i * rh
        fill = COL.get(r["color"], K)
        _bin(c, X0, ry + (rh - 34) / 2, 26, fill, sw=2, lid=False)
        c.text(cols[0], ry + (rh - c.line_h("ss600", 18)) / 2, _ell(c, r["date_text"], "ss600", 18, wdate - 8),
               "ss600", 18, K)
        when = ctx.t("Tomorrow", "Morgen") if r["days"] == 1 else ctx.t("Today", "Heute") if r["days"] == 0 \
            else r["in_text"]
        ww = c.tw(when, "ss400i", 18)
        c.text(X1, ry + (rh - c.line_h("ss400i", 18)) / 2, when, "ss400i", 18, K, align="r")
        ks, nm = _one_line(c, r["name"], "pf700", 22, X1 - cols[1] - ww - 12, 15)
        c.text(cols[1], ry + (rh - c.line_h("pf700", ks)) / 2, nm, "pf700", ks, K)
        if i < n - 1:
            _dots(c, X0, X1, ry + rh - 1)
    return c.finish()


# ================================================================== warnings
def _justified_dropcap(c, x, top, width, bottom, text, size=17, lh=1.42, cap_size=44):
    """Justified paragraph with a Playfair drop cap over two lines; shrinks until it fits. -> bool fits."""
    text = " ".join(text.split())
    if not text:
        return
    for sz in range(size, 10, -1):
        L = sz * lh
        cs = round(cap_size * sz / size)
        cap, rest = text[0], text[1:]
        capw = c.tw(cap, "pf900", cs) + 7
        words = rest.split(" ")
        lines, cur = [], []
        while words:
            avail = width - (capw if len(lines) < 2 else 0)
            t = " ".join(cur + [words[0]]) if cur else words[0]
            if cur and c.tw(t, "ss400", sz) > avail:
                lines.append(cur)
                cur = []
                continue
            cur.append(words.pop(0))
        if cur:
            lines.append(cur)
        if len(lines) * L <= bottom - top or sz == 11:
            break
    nmax = max(2, int((bottom - top) // L))
    cut = len(lines) > nmax
    lines = lines[:nmax]
    if rest[:1] == " ":
        lines[0] = [""] + lines[0] if lines else lines
    c.text(x, top + 3 + (L - sz) / 2 - cs * 0.1, cap, "pf900", cs, K, lh=0.9)
    y = top
    for i, ln in enumerate(lines):
        ln = [w for w in ln if w != ""]
        x0 = x + (capw if i < 2 else 0)
        avail = width - (capw if i < 2 else 0)
        last = i == len(lines) - 1
        if last and cut:
            s = _ell(c, " ".join(ln) + " …", "ss400", sz, avail)
            c.text(x0, y, s, "ss400", sz, K, lh=lh)
        elif last or len(ln) == 1:
            c.text(x0, y, " ".join(ln), "ss400", sz, K, lh=lh)
        else:
            wsum = sum(c.tw(wd, "ss400", sz) for wd in ln)
            gap = (avail - wsum) / (len(ln) - 1)
            xx = x0
            for wd in ln:
                c.text(xx, y, wd, "ss400", sz, K, lh=lh)
                xx += c.tw(wd, "ss400", sz) + gap
        y += L


def _triangle(c, x, y, w, fill=Y):
    k = w / 96
    pts = [(x + 48 * k, y + 4 * k), (x + 92 * k, y + 82 * k), (x + 4 * k, y + 82 * k)]
    c.poly(pts, fill=fill)
    c.d.line([(round(a), round(b)) for a, b in pts + [pts[0]]], fill=K, width=max(2, round(4 * k)), joint="curve")
    c.rect((x + 44 * k, y + 28 * k, x + 52 * k, y + 60 * k), fill=K)
    c.rect((x + 44 * k, y + 66 * k, x + 52 * k, y + 74 * k), fill=K)


def warnings(ctx, v):
    c = _paper()
    upd = _clock(v.get("updated", ""), ctx.lang)
    y = _big_mast(c, ctx, _issue(ctx, v.get("place", "")),
                  f"{ctx.t('Extra edition', 'Extrablatt')} · {upd}" if upd else ctx.t("Extra edition", "Extrablatt")) + 10
    lvl, nlv = v.get("level", 1), v.get("levels", 4)
    # breaking-news bar
    yellow = v.get("color") == "yellow"
    bg, fg = (Y, K) if yellow else (R, Wh)
    bL = c.line_h("ss600", 14)
    c.rect((X0, y, X1, y + 5 + bL + 5), fill=bg)
    right = ctx.t("Warning level {n} of {m}", "Warnstufe {n} von {m}", n=lvl, m=nlv)
    rw = c.tw(right, "ss400i", 13)
    c.text(X1 - 12, y + 5 + (bL - c.line_h("ss400i", 13)) / 2, right, "ss400i", 13, fg, align="r")
    _kicker(c, X0 + 12, y + 5, f"{ctx.t('Breaking news', 'Eilmeldung')} · {v['title']}", fill=fg, size=14,
            width=X1 - X0 - 36 - rw, track=5)
    y += 5 + bL + 5 + 10
    # headline row
    lv_w = nlv * 30 + (nlv - 1) * 3
    lab = ctx.t("Level {n} of {m}", "Stufe {n} von {m}", n=lvl, m=nlv)
    lv_w = max(lv_w, c.tw(lab, "ss400i", 12))
    hx = X0 + 96 + 20
    hw = X1 - lv_w - 20 - hx
    s, ev = _one_line(c, v.get("event", ""), "pf900", 64, hw, 30, -1)
    if c.tw(ev, "pf900", s, -1) > hw:
        ev = _ell(c, ev, "pf900", s, hw, -1)
    lt_s, lt = _one_line(c, v.get("level_text", ""), "pf700i", 22, hw, 14)
    ltL = c.line_h("pf700i", 22)
    th = s * 0.95 + 4 + ltL
    rh = max(86, th)
    _triangle(c, X0, y + (rh - 86) / 2, 96)
    ty = y + (rh - th) / 2
    c.text(hx, ty, ev, "pf900", s, K, track=-1, lh=0.95)
    c.text(hx, ty + s * 0.95 + 4, lt, "pf700i", lt_s, R, lh=ltL / lt_s)
    lx = X1 - (nlv * 30 + (nlv - 1) * 3)
    ly = y + rh / 2 - (16 + 4 + 16) / 2
    for i in range(nlv):
        bx = lx + i * 33
        c.rect((bx, ly, bx + 30, ly + 16), fill=(Y if lvl <= 2 else R) if i < lvl else None, outline=K, width=1)
    c.text(X1, ly + 20, lab, "ss400i", 12, K, align="r")
    y += rh + 10
    # two columns
    c.hline(X0, X1, y, K, 1)
    gtop = y + 1
    cw = (X1 - X0) * 2 / 3
    c.vline(X0 + cw - 1, gtop, 460, K, 1)
    x0, x1 = X0, X0 + cw - 1 - 18
    hh = _head(c, x0, gtop + 10, ctx.t("The report", "Die Meldung"), x1 - x0)
    text = v.get("description", "") or v.get("headline", "")
    if v.get("instruction"):
        text = f"{text} {v['instruction']}"
    _justified_dropcap(c, x0, gtop + 10 + hh + 6, x1 - x0, 460, text)
    x0, x1 = X0 + cw + 18, X1
    hh = _head(c, x0, gtop + 10, ctx.t("Valid", "Gültig"), x1 - x0)
    sL = c.line_h("ss400i", 12)
    src = ctx.t("Source: {s}", "Quelle: {s}", s=v.get("source", ""))
    sl = c.wrap(src, "ss400i", 12, x1 - x0)[:2]
    sy = 460 - len(sl) * sL
    c.hline(x0, x1, sy - 5 - 1, K, 1)
    c.para(x0, sy, x1 - x0, sl, "ss400i", 12, sL, K)
    rows = []
    if v.get("place"):
        rows.append((ctx.t("Place", "Ort"), v["place"]))
    if v.get("onset_text"):
        rows.append((ctx.t("From", "Ab"), v["onset_text"]))
    if v.get("expires_text"):
        rows.append((ctx.t("Until", "Bis"), v["expires_text"]))
    yy = _rows(c, x0, x1, gtop + 10 + hh + 8, rows, 14, bottom=sy - 12)
    if v.get("more_text"):
        mL = c.line_h("ss400i", 13)
        room = sy - 12 - (yy + 8)
        ml = c.wrap(v["more_text"], "ss400i", 13, x1 - x0)
        n = int(room // mL)
        if n > 0:
            if len(ml) > n:
                ml = ml[:n]
                ml[-1] = _ell(c, ml[-1] + " …", "ss400i", 13, x1 - x0)
            c.para(x0, yy + 8, x1 - x0, ml, "ss400i", 13, mL, R)
    return c.finish()


# ================================================================== wifi
def wifi(ctx, v):
    from ..plugins import wifi as W
    c = _paper()
    top = _mast(c, ctx, ctx.t("Service", "Service")) + 12
    # QR code on the right
    box = 336
    qx = X1 - box
    c.rect((qx, top, qx + box, top + box), outline=K, width=1)
    c.rect((qx + 3, top + 3, qx + box - 3, top + box - 3), outline=K, width=1)
    q0 = qx + 4 + 14
    n = len(v["modules"])
    quiet = 2 if 300 // (n + 4) >= 6 and 300 // (n + 8) < 6 else 4
    W.draw_modules(c.d, v["modules"], q0, top + 18, 300, dark=K, light=Wh, quiet=quiet)
    s, hint = _one_line(c, v.get("hint", ""), "pf400i", 17, box + 20, 11)
    c.text(qx + box / 2, top + box + 6, hint, "pf400i", s, K, align="c")
    # left column
    x0, x1 = X0, qx - 30
    w = x1 - x0
    y = top
    _kicker(c, x0, y, ctx.t("For our guests", "Für unsere Gäste"), width=w)
    y += c.line_h("ss600", 13) + 12
    # bottom note
    note = v.get("note") or (ctx.t("Please do not pass the password on – thank you!",
                                   "Bitte das Passwort nicht weitergeben – danke!") if v.get("password") else "")
    nL = c.line_h("ss400i", 13)
    nl = c.wrap(note, "ss400i", 13, w)[:2] if note else []
    bottom = 460 - len(nl) * nL
    c.para(x0, bottom, w, nl, "ss400i", 13, nL, K)
    rows = [(v.get("network_label", ""), v.get("ssid", ""), "pf700", 28)]
    if v.get("password"):
        rows.append((v.get("password_label", ""), v["password"], "pf700", 28))
    sec = v.get("security") or ""
    rows.append((ctx.t("Encryption", "Verschlüsselung"), sec if sec else ctx.t("open network", "offenes Netz"), "ss600", 18))
    row_h = [8 + c.line_h(r, z) + 8 for _, _, r, z in rows]
    table_h = 1 + sum(row_h) + len(rows)
    room = bottom - 12 - table_h - y
    size = 46
    head = ctx.t("Welcome to the", "Willkommen im")
    while True:
        lines = _rich_wrap(c, [(head, "pf900", size, K), (v.get("title", ""), "pf700i", size, R)], w)
        if len(lines) * size * 1.02 <= room or size <= 22:
            break
        size -= 2
    hL = size * 1.02
    for ln in lines[:max(1, int(room // hL))]:
        x = x0
        for wd, role, sz, fill in ln:
            wd = _ell(c, wd, role, sz, x1 - x, -0.5)
            c.text(x, y, wd, role, sz, fill, track=-0.5, lh=1.02)
            x += c.tw(wd, role, sz, -0.5) + c.tw(" ", role, sz)
        y += hL
    y += 12
    c.hline(x0, x1, y, K, 1)
    y += 1
    for i, (lab, val, role, z) in enumerate(rows):
        rh = row_h[i]
        base = y + 8 + c._baseline(0, role, z, None)
        lw = min(c.tw(lab, "ss400i", 14), w * 0.45)
        sz, val = _one_line(c, val, role, z, w - lw - 12, 12)
        lab = _ell(c, lab, "ss400i", 14, w - c.tw(val, role, sz) - 12)
        c.text(x0, base - c._baseline(0, "ss400i", 14, None), lab, "ss400i", 14, K)
        c.text(x1, base - c._baseline(0, role, sz, None), val, role, sz, K, align="r")
        y += rh
        if i < len(rows) - 1:
            _dots(c, x0, x1, y)
        y += 1
    c.hline(x0, x1, y - 1, K, 1)
    return c.finish()


# ================================================================== habits
def _centre_kicker(c, y, text, fill=R):
    kL = c.line_h("ss600", 13)
    kt = text.upper()
    ks, ktr = 13, 4.0
    while ks > 9 and c.tw(kt, "ss600", ks, ktr) - ktr > X1 - X0 - 80:
        ks -= 1
        ktr = max(1.5, ktr - 0.5)
    kt = _ell(c, kt, "ss600", ks, X1 - X0 - 80, ktr)
    kw = c.tw(kt, "ss600", ks, ktr) - ktr
    c.text(400, y + (kL - c.line_h("ss600", ks)) / 2, kt, "ss600", ks, fill, track=ktr, align="c")
    c.hline(X0, 400 - kw / 2 - 12, y + kL / 2, K, 1)
    c.hline(400 + kw / 2 + 12, X1, y + kL / 2, K, 1)
    return kL


def _dotted_box(c, x, y, s):
    for xx in range(int(x), int(x + s), 2):
        c.d.point((xx, round(y)), fill=K)
        c.d.point((xx, round(y + s - 1)), fill=K)
    for yy in range(int(y), int(y + s), 2):
        c.d.point((round(x), yy), fill=K)
        c.d.point((round(x + s - 1), yy), fill=K)


def habits(ctx, v):
    c = _paper()
    y = _mast(c, ctx, ctx.t("Lifestyle", "Lebensart")) + 12
    y += _centre_kicker(c, y, f"{v['title']} · {ctx.t('the last six weeks', 'die letzten sechs Wochen')}") + 12
    hs = v["habits"][:6]
    n = len(hs)
    ncol = 1 if n == 1 else 2
    nrow = math.ceil(n / ncol)
    gw = (X1 - X0) / ncol
    gh = (460 - y) / nrow
    letters = v.get("weekday_letters") or list("MTWTFSS")
    lab_L = c.line_h("ss400i", 11)
    for i, h in enumerate(hs):
        col, row = i % ncol, i // ncol
        x0 = X0 + col * gw
        y0 = y + row * gh
        if col < ncol - 1:
            c.vline(x0 + gw - 1, y0, y0 + gh, K, 1)
        if row < nrow - 1:
            c.hline(x0, x0 + gw, y0 + gh - 1, K, 1)
        padl = 0 if col == 0 else 18
        padr = 18 if col < ncol - 1 else 0
        inner_h = gh - 20
        s = int(min(17, (inner_h - lab_L - 3 - 5 * 3) / 6))
        s = max(7, s)
        calw = 7 * s + 6 * 3
        calh = 6 * s + 5 * 3 + 3 + lab_L
        cx0 = x0 + padl
        cy0 = y0 + (gh - calh) / 2
        for w, week in enumerate(h["grid"][:6]):
            for d, val in enumerate(week[:7]):
                bx, by = cx0 + d * (s + 3), cy0 + w * (s + 3)
                today = v.get("now") and w == v["now"][0] and d == v["now"][1]
                if val is None:
                    _dotted_box(c, bx, by, s)
                elif today:
                    c.rect((bx, by, bx + s, by + s), fill=R if val else None, outline=R, width=1)
                elif val:
                    c.rect((bx, by, bx + s, by + s), fill=K)
                else:
                    c.rect((bx, by, bx + s, by + s), outline=K, width=1)
        if s >= 9:
            for d, ltr in enumerate(letters[:7]):
                c.text(cx0 + d * (s + 3) + s / 2, cy0 + 6 * (s + 3), ltr, "ss400i", 11, K, align="c")
        # text block
        tx = cx0 + calw + 16
        tw = x0 + gw - padr - tx
        nsz = 20
        nl = c.wrap(h["name"], "pf700", nsz, tw)
        while len(nl) > 2 and nsz > 14:
            nsz -= 1
            nl = c.wrap(h["name"], "pf700", nsz, tw)
        if len(nl) > 2:
            nl = nl[:2]
            nl[-1] = _ell(c, nl[-1] + " …", "pf700", nsz, tw)
        nL = nsz * 1.1
        big = min(50, max(26, int(gh * 0.32)))
        unit = ctx.t("day in a row", "Tag in Folge") if h["streak"] == 1 else ctx.t("days in a row", "Tage in Folge")
        rate = ctx.t("{n} of {m} days done", "{n} von {m} Tagen geschafft", n=h["done_count"], m=v.get("days", 42))
        rL = c.line_h("ss400", 12)
        th = len(nl) * nL + 4 + 1 + 2 + big + 2 + rL
        ty = y0 + (gh - th) / 2
        for ln in nl:
            c.text(tx, ty, ln, "pf700", nsz, K, lh=1.1)
            ty += nL
        ty += 4
        c.hline(tx, tx + tw, ty, K, 1)
        ty += 1 + 2
        st = str(h["streak"])
        c.text(tx, ty, st, "pf900", big, R if h.get("hot") or True else K, lh=1)
        sw = c.tw(st, "pf900", big) + 6
        ub = c._baseline(ty, "pf900", big, 1) - c._baseline(0, "ss400i", 14, None)
        us, ut = _one_line(c, unit, "ss400i", 14, tw - sw, 10)
        c.text(tx + sw, ub, ut, "ss400i", us, K)
        ty += big + 2
        c.text(tx, ty, _ell(c, rate, "ss400", 12, tw), "ss400", 12, K)
    return c.finish()


# ================================================================== sudoku
def sudoku(ctx, v):
    c = _paper()
    top = _mast(c, ctx, ctx.t("Puzzle corner", "Rätselecke")) + 12
    # grid
    S = 384
    gx, gy = X1 - S, top
    if gy + S > 460:
        S = 460 - gy
        gx = X1 - S
    c.rect((gx, gy, gx + S, gy + S), fill=K)
    inner = S - 6
    edges = [0]
    for i in range(1, 9):
        edges.append(inner * i / 9)
    edges.append(inner)
    cw = inner / 9
    for r in range(9):
        for k in range(9):
            x0 = gx + 3 + edges[k] + (0 if k == 0 else (1.5 if k % 3 == 0 else 0.5))
            x1 = gx + 3 + edges[k + 1] - (0 if k == 8 else (1.5 if (k + 1) % 3 == 0 else 0.5))
            y0 = gy + 3 + edges[r] + (0 if r == 0 else (1.5 if r % 3 == 0 else 0.5))
            y1 = gy + 3 + edges[r + 1] - (0 if r == 8 else (1.5 if (r + 1) % 3 == 0 else 0.5))
            c.rect((x0, y0, x1, y1), fill=Wh)
            d = v["grid"][r][k]
            if d:
                fs = round(26 * cw / 42)
                c.text((x0 + x1) / 2, (y0 + y1) / 2 - c.line_h("pf700", fs) / 2, str(d), "pf700", fs, K, align="c")
    # text column
    x0, x1 = X0, gx - 28
    w = x1 - x0
    y = top
    _kicker(c, x0, y, ctx.t("The riddle", "Das Rätsel"), width=w)
    y += c.line_h("ss600", 13) + 10
    size = 44
    while True:
        lines = _rich_wrap(c, [(v["title"], "pf900", size, K), (v.get("subtitle", ""), "pf700i", size, K)], w)
        if len(lines) <= 2 or size <= 24:
            break
        size -= 2
    for ln in lines[:2]:
        x = x0
        for wd, role, sz, fill in ln:
            wd = _ell(c, wd, role, sz, x1 - x)
            c.text(x, y, wd, role, sz, fill, lh=1)
            x += c.tw(wd, role, sz) + c.tw(" ", role, sz)
        y += size
    y += 10
    # footer
    fL = c.line_h("ss400", 13)
    fy = 460 - fL
    c.hline(x0, x1, fy - 7, K, 1)
    no = ctx.t("No. {n}", "Nr. {n}", n=v["today"].timetuple().tm_yday)
    nw = c.tw(no, "ss600", 13)
    c.text(x1, fy, no, "ss600", 13, K, align="r")
    c.text(x0, fy, _ell(c, v.get("hint", ""), "ss400i", 13, w - nw - 12), "ss400i", 13, K)
    # rows (from the bottom)
    rL = c.line_h("ss400", 14)
    rows_top = fy - 7 - 10 - (2 * (rL + 8) - 4)
    c.hline(x0, x1, y, K, 1)
    rule = ctx.t("Every row, every column and each of the nine boxes contains the digits 1 to 9 exactly once.",
                 "Jede Zeile, jede Spalte und jedes der neun Kästchen enthält die Ziffern 1 bis 9 genau einmal.")
    _justified_dropcap(c, x0, y + 1 + 8, w, rows_top - 10, rule, size=15, cap_size=40)
    # difficulty row with dots
    yy = rows_top
    lab = ctx.t("Difficulty", "Schwierigkeit")
    name = v.get("level_name", "")
    nwid = c.tw(name, "ss600", 14)
    c.text(x0, yy, _ell(c, lab, "ss400", 14, w - nwid - 60), "ss400", 14, K)
    c.text(x1, yy, name, "ss600", 14, K, align="r")
    dx = x1 - nwid - 4 - 3 * 16
    for i in range(v.get("level_max", 3)):
        cx, cy = dx + i * 16 + 5.5, yy + rL / 2
        if i < v.get("level_no", 1):
            c.circle(cx, cy, 5.5, fill=R)
        else:
            c.circle(cx, cy, 5.5, outline=K, width=1)
    _dots(c, x0, x1, yy + rL + 2)
    yy += rL + 8
    _rows(c, x0, x1, yy, [(ctx.t("Given", "Vorgegeben"), ctx.t("{n} digits", "{n} Zahlen", n=v["givens"]))], 14)
    return c.finish()


# ================================================================== solar
def _sun(c, x, y, s=64):
    k = s / 64
    for x1, y1, x2, y2 in ((32, 2, 32, 12), (32, 52, 32, 62), (2, 32, 12, 32), (52, 32, 62, 32),
                           (11, 11, 18, 18), (46, 46, 53, 53), (11, 53, 18, 46), (46, 18, 53, 11)):
        c.d.line((x + x1 * k, y + y1 * k, x + x2 * k, y + y2 * k), fill=K, width=max(2, round(3 * k)))
    c.circle(x + 32 * k, y + 32 * k, 14 * k, fill=Y, outline=K, width=2)


def solar(ctx, v):
    c = _paper()
    y = _big_mast(c, ctx, _issue(ctx, v.get("place", "")),
                  f"{ctx.t('Energy', 'Energie')} · {_clock(v.get('now_text', ''), ctx.lang)}") + 10
    # headline
    fr = v.get("power_frac") or 0
    if fr >= 0.6:
        tail = ctx.t("the sun is riding high", "die Sonne steht hoch")
    elif fr >= 0.25:
        tail = ctx.t("the sun is at work", "die Sonne arbeitet")
    elif v.get("power_w", 0) > 0:
        tail = ctx.t("a modest sun", "die Sonne zeigt sich zaghaft")
    else:
        tail = ctx.t("the panels are resting", "die Module ruhen")
    head = f"{v['power_text']} {v.get('power_label', '')},"
    hx = X0 + 64 + 18
    hw = X1 - hx
    size = 46
    while True:
        lines = _rich_wrap(c, [(head, "pf900", size, K), (tail, "pf700i", size, R)], hw)
        if len(lines) <= 2 or size <= 26:
            break
        size -= 2
    lines = lines[:2]
    hL = size * 1.02
    hh = max(64, len(lines) * hL)
    _sun(c, X0, y + (hh - 64) / 2)
    ty = y + (hh - len(lines) * hL) / 2
    for ln in lines:
        x = hx
        for wd, role, sz, fill in ln:
            wd = _ell(c, wd, role, sz, X1 - x, -0.5)
            c.text(x, ty, wd, role, sz, fill, track=-0.5, lh=1.02)
            x += c.tw(wd, role, sz, -0.5) + c.tw(" ", role, sz)
        ty += hL
    y += hh + 10
    c.hline(X0, X1, y, K, 1)
    gtop = y + 1
    cw = (X1 - X0) / 3
    c.vline(X0 + cw - 1, gtop, 460, K, 1)
    # column 1: figures
    x0, x1 = X0, X0 + cw - 1 - 16
    hh = _head(c, x0, gtop + 10, ctx.t("In numbers", "In Zahlen"), x1 - x0)
    note = f"{ctx.t('System {p}', 'Anlage {p}', p=v.get('peak_text', ''))} · {v.get('footer', '')}"
    sL = c.line_h("ss400i", 12)
    nl = c.wrap(note, "ss400i", 12, x1 - x0)[:2]
    ny = 460 - len(nl) * sL
    c.hline(x0, x1, ny - 6, K, 1)
    c.para(x0, ny, x1 - x0, nl, "ss400i", 12, sL, K)
    rows = [(ctx.t("Now", "Jetzt"), v["power_text"]), (ctx.t("Today", "Heute"), v["today_text"]),
            (ctx.t("Saved", "Gespart"), f"≈ {v['saved_text']}", R)]
    if v.get("total_text"):
        rows.append((ctx.t("In total", "Insgesamt"), v["total_text"]))
    _rows(c, x0, x1, gtop + 10 + hh + 8, rows, 14, bottom=ny - 12)
    # column 2: curve
    x0, x1 = X0 + cw + 16, X1
    hh = _head(c, x0, gtop + 10, ctx.t("Power over the day", "Leistung im Tagesverlauf"), x1 - x0)
    capL = c.line_h("ss400", 12)
    axL = c.line_h("ss400i", 11)
    cap_y = 460 - capL
    ax_y = cap_y - 4 - axL
    ch_b = ax_y - 4
    ch_t = gtop + 10 + hh + 6
    W_, H_ = x1 - x0, ch_b - ch_t
    t0, t1 = v.get("t0", 5), v.get("t1", 22)
    peak = v.get("peak") or 1
    top_w = peak * 1.12

    def px(t):
        return x0 + (t - t0) / (t1 - t0) * W_

    def py(w):
        return ch_b - 2 - min(w, peak) / top_w * (H_ - 2)

    for lv in (peak / 2, peak):
        yy = py(lv)
        for xx in range(int(x0), int(x1), 4):
            c.d.point((xx, round(yy)), fill=K)
        c.text(x0 + 2, yy - 4 - c.line_h("ss400i", 11), f"{ctx.num(lv, 0)} W", "ss400i", 11, K)
    hrs, wts = v.get("hours") or [], v.get("watts") or []
    pts = [(px(h), py(w)) for h, w in zip(hrs, wts) if t0 <= h <= t1]
    if len(pts) >= 2:
        c.poly(pts + [(pts[-1][0], ch_b - 2), (pts[0][0], ch_b - 2)], fill=Y)
        c.stroke(pts, K, 2.5)
    c.rect((x0, ch_b - 2, x1, ch_b), fill=K)
    if v.get("now_visible", True):
        nx = px(v["now"])
        c.rect((nx - 1, ch_t, nx + 1, ch_b - 2), fill=R)
        if pts:
            c.circle(pts[-1][0], pts[-1][1], 5, fill=R)
    for k, (t, lab) in enumerate(zip(v.get("ticks") or [], v.get("tick_labels") or [])):
        if k == 0 and ctx.lang == "de":
            lab = f"{int(t)} Uhr"
        c.text(px(t), ax_y, lab, "ss400i", 11, K, align="c")
    a = f"{ctx.t('Now', 'Jetzt')} {v.get('now_text', '')}"
    aw = c.tw(a, "ss600", 12)
    c.text(x0, cap_y, a, "ss600", 12, R)
    if v.get("max_text"):
        b = " · " + ctx.t("peak today {p} at {t}", "Spitze heute {p} um {t}", p=v["max_text"],
                         t=_clock(v.get("max_time", ""), ctx.lang))
        c.text(x0 + aw, cap_y, _ell(c, b, "ss400", 12, W_ - aw), "ss400", 12, K)
    return c.finish()


# ================================================================== waterlevel
def _trend_arrow(c, x, y, trend, col):
    """The mockup's 30×30 arrow (rising); falling / steady are turned."""
    if trend == "rising":
        line, head = (4, 26, 24, 6), [(12, 4), (27, 3), (26, 18)]
    elif trend == "falling":
        line, head = (4, 4, 24, 24), [(12, 26), (27, 27), (26, 12)]
    else:
        line, head = (2, 15, 22, 15), [(18, 7), (29, 15), (18, 23)]
    c.d.line((x + line[0], y + line[1], x + line[2], y + line[3]), fill=col, width=4)
    c.poly([(x + a, y + b) for a, b in head], fill=col)


def waterlevel(ctx, v):
    c = _paper()
    top = _mast(c, ctx, ctx.t("From the river", "Vom Fluss")) + 12
    bottom = 460
    # left column
    x0, x1 = X0, X0 + 230
    c.vline(X0 + 250 - 1, top, bottom, K, 1)
    w = x1 - x0
    y = top
    _kicker(c, x0, y, v.get("name", ""), width=w)
    y += c.line_h("ss600", 13) + 8
    segs = [(v.get("station", ""), "pf700", 22, K)]
    if v.get("water"):
        segs.append(("· " + v["water"], "pf700i", 22, K))
    sz = 22
    while True:
        segs = [(t, r, sz, f) for t, r, _, f in segs]
        lines = _rich_wrap(c, segs, w)
        if len(lines) <= 2 or sz <= 14:
            break
        sz -= 1
    for ln in lines[:2]:
        x = x0
        for wd, role, s, fill in ln:
            wd = _ell(c, wd, role, s, x1 - x)
            c.text(x, y, wd, role, s, fill, lh=1.1)
            x += c.tw(wd, role, s) + c.tw(" ", role, s)
        y += sz * 1.1
    y += 8
    num, unit = v.get("value_num", "–"), " " + v.get("unit", "")
    bs = 84
    while bs > 40 and c.tw(num, "pf900", bs, -2) + c.tw(unit, "pf900", 30 * bs / 84) > w:
        bs -= 4
    us = round(30 * bs / 84)
    c.text(x0, y, num, "pf900", bs, K, track=-2, lh=0.9)
    nb = c._baseline(y, "pf900", bs, 0.9)
    c.text(x0 + c.tw(num, "pf900", bs, -2) + 2, nb - c._baseline(0, "pf900", us, None), unit, "pf900", us, K)
    y += bs * 0.9 + 8
    if v.get("state_text"):
        s, st = _one_line(c, v["state_text"], "pf700i", 26, w, 14)
        c.text(x0, y, st, "pf700i", s, R if v.get("high") else B)
        y += c.line_h("pf700i", 26) + 8
    if v.get("trend"):
        tL = c.line_h("ss400", 15)
        sub = f"{v['change_24h_text']} / 24 h" if v.get("change_24h_text") else \
            (f"{v['trend_diff']:+.0f} {v.get('unit', '')} / 3 h" if v.get("trend_diff") is not None else "")
        bh = max(30, tL * (2 if sub else 1))
        c.hline(x0, x1, y, K, 1)
        col = R if v["trend"] == "rising" else B if v["trend"] == "falling" else K
        _trend_arrow(c, x0, y + 1 + 8 + (bh - 30) / 2, v["trend"], col)
        ty = y + 1 + 8 + (bh - tL * (2 if sub else 1)) / 2
        c.text(x0 + 40, ty, _ell(c, v.get("trend_text", ""), "ss600", 15, w - 40), "ss600", 15, K)
        if sub:
            c.text(x0 + 40, ty + tL, _ell(c, sub, "ss400", 15, w - 40), "ss400", 15, K)
        y += 1 + 8 + bh + 8
        c.hline(x0, x1, y, K, 1)
        y += 1 + 8
    rows = []
    for r in v.get("refs") or []:
        lab = v.get("mw_label") if r["key"] == "MW" else \
            ctx.t("Navigation limit (HSW)", "Schifffahrtsgrenze (HSW)") if r["key"] == "HSW" else r["key"]
        rows.append((lab, r["text"].split(" ", 1)[1] if " " in r["text"] else r["text"]))
    _rows(c, x0, x1, y, rows, 14, bottom=bottom)
    # right column: the chart
    x0, x1 = X0 + 250 + 20, X1
    hh = _head(c, x0, top, ctx.t("The last {n} days", "Die letzten {n} Tage", n=v.get("days", 7)), x1 - x0)
    fL = c.line_h("ss400i", 12)
    fy = bottom - fL
    c.hline(x0, x1, fy - 6, K, 1)
    c.text(x0, fy, _ell(c, v.get("footer", ""), "ss400i", 12, x1 - x0), "ss400i", 12, K)
    axL = c.line_h("ss400i", 11)
    ax_y = fy - 6 - 8 - axL
    ch_b = ax_y - 4
    ch_t = top + hh + 6
    vals, xs = v.get("values") or [], v.get("x") or []
    mw, hsw = v.get("mw"), v.get("hsw")
    lo_d = min([x for x in (v.get("min"), mw) if x is not None] or [0])
    hi_d = max([x for x in (v.get("max"), hsw, mw) if x is not None] or [1])
    span = max(1.0, hi_d - lo_d)
    lo, hi = lo_d - span * 0.25, hi_d + span * 0.08
    W_ = x1 - x0

    def py(val):
        return ch_b - 2 - (val - lo) / (hi - lo) * (ch_b - 2 - ch_t)

    pts = [(x0 + xx * W_, py(val)) for xx, val in zip(xs, vals)]
    if len(pts) >= 2:
        c.poly(pts + [(pts[-1][0], ch_b - 2), (pts[0][0], ch_b - 2)], fill=B)
        c.stroke(pts, K, 2.5)
    if hsw is not None:
        yy = py(hsw)
        c.dashed((x0, yy, x1, yy), R, 2, 8, 5)
        c.text(x1 - 2, yy - 6 - c.line_h("ss400i", 12) + 3, f"HSW {v.get('hsw_text', '')}", "ss400i", 12, R, align="r")
    if mw is not None:
        yy = py(mw)
        c.dashed((x0, yy, x1, yy), K, 1, 2, 3)
        lab = f"MW {v.get('mw_text', '')}"
        lL = c.line_h("ss400i", 12)
        lw = c.tw(lab, "ss400i", 12)
        ly = yy - 6 - lL + 3
        c.rect((x1 - lw - 8, ly + 2, x1 - 10, ly + lL), fill=Wh)
        c.text(x1 - 12, ly, lab, "ss400i", 12, K, align="r")
    if pts:
        c.circle(pts[-1][0] - 3, pts[-1][1], 5, fill=R)
    c.rect((x0, ch_b - 2, x1, ch_b), fill=K)
    hours = max(1, v.get("hours") or 24 * v.get("days", 7))
    for t in v.get("day_ticks") or []:
        cx = t["x"] + 12 / hours
        if 0 <= cx <= 1:
            c.text(x0 + cx * W_, ax_y, t.get("weekday", ""), "ss400i", 11, K, align="c")
    return c.finish()


# ================================================================== birthdays
def birthdays(ctx, v):
    c = _paper()
    y = _mast(c, ctx, ctx.t("Family notices", "Familienanzeigen")) + 12
    y += _centre_kicker(c, y, v.get("festive_title") if v.get("festive") else v["title"]) + 12
    festive = v.get("festive")
    first = v["first"]
    others = [p for p in v["people"] if p["days"] > 0][:4] if festive else v.get("others", [])[:4]
    # feature box
    bh = 150 if others else 460 - y
    c.rect((X0, y, X1, y + bh), outline=K, width=1)
    c.rect((X0 + 3, y + 3, X1 - 3, y + bh - 3), outline=K, width=1)
    lx = X0 + 4 + 24
    c.vline(lx + 120 + 20, y + 18, y + bh - 18, K, 1)
    iL = c.line_h("ss400i", 13)
    if festive:
        s, word = _one_line(c, ctx.t("Today", "Heute"), "pf900", 40, 120, 18)
        c.text(lx + 60, y + (bh - c.line_h("pf900", s)) / 2, word, "pf900", s, R, align="c")
    else:
        d = first["days"]
        top_w = ctx.t("in", "in")
        bot_w = ctx.t("day", "Tag") if d == 1 else ctx.t("days", "Tagen")
        ns = 76
        while ns > 30 and c.tw(str(d), "pf900", ns) > 120:
            ns -= 4
        th = iL + 2 + ns * 0.9 + 2 + iL
        ty = y + (bh - th) / 2
        c.text(lx + 60, ty, _ell(c, top_w, "ss400i", 13, 120), "ss400i", 13, K, align="c")
        c.text(lx + 60, ty + iL + 2, str(d), "pf900", ns, R, lh=0.9, align="c")
        c.text(lx + 60, ty + iL + 2 + ns * 0.9 + 2, _ell(c, bot_w, "ss400i", 13, 120), "ss400i", 13, K, align="c")
    rx0 = lx + 120 + 20 + 1 + 24
    rx1 = X1 - 4 - 24
    rw = rx1 - rx0
    rc = (rx0 + rx1) / 2
    if festive:
        main = [(v.get("festive_names", ""), "pf900", 54, K)]
        sub = v.get("festive_line") or C.long_date(v["today"], ctx.lang)
    else:
        main = [(first["name"], "pf900", 54, K)] + ([(first["age_text"], "pf400i", 54, K)] if first.get("age_text") else [])
        sub = first.get("date_long", "")
    size = 54
    maxl = 2 if bh > 140 else 1
    while True:
        segs = [(t, r, size, f) for t, r, _, f in main]
        lines = _rich_wrap(c, segs, rw)
        if len(lines) <= maxl or size <= 24:
            break
        size -= 2
    lines = lines[:maxl]
    sL = c.line_h("pf400i", 24)
    th = len(lines) * size + 6 + 10 + 6 + sL
    ty = y + (bh - th) / 2
    for ln in lines:
        lw = sum(c.tw(wd, role, sz) for wd, role, sz, _ in ln) + sum(c.tw(" ", role, sz) for _, role, sz, _ in ln[:-1])
        x = max(rx0, rc - lw / 2)
        for wd, role, sz, fill in ln:
            wd = _ell(c, wd, role, sz, rx1 - x)
            c.text(x, ty, wd, role, sz, fill, lh=1)
            x += c.tw(wd, role, sz) + c.tw(" ", role, sz)
        ty += size
    ty += 6
    c.hline(rc - 70, rc - 12, ty + 5, K, 1)
    c.hline(rc + 12, rc + 70, ty + 5, K, 1)
    c.poly([(rc, ty), (rc + 5, ty + 5), (rc, ty + 10), (rc - 5, ty + 5)], fill=R)
    ty += 10 + 6
    s, sub = _one_line(c, sub, "pf400i", 24, rw, 14)
    c.text(rc, ty, sub, "pf400i", s, K, lh=sL / s, align="c")
    y += bh + 12
    # the next ones
    if others:
        n = len(others)
        gw = (X1 - X0 - 12 * (n - 1)) / n if n == 4 else (X1 - X0 - 12 * 3) / 4
        gh = 460 - y
        for i, p in enumerate(others):
            bx = X0 + i * (gw + 12)
            c.rect((bx, y, bx + gw, y + gh), outline=K, width=1)
            iw = gw - 24
            cx = bx + gw / 2
            parts = [("pf700", 26, p["name"], K), ("ss600", 15, p["date_short"], K),
                     ("ss400i", 14, p.get("age_text", ""), K), ("rule", 0, "", K), ("ss600", 13, p["when"], R)]
            hs = [1 if r == "rule" else (26 if r == "pf700" else c.line_h(r, z)) for r, z, _, _ in parts]
            th = sum(hs) + 4 * (len(parts) - 1)
            yy = y + (gh - th) / 2
            for (r, z, t, f), h in zip(parts, hs):
                if r == "rule":
                    c.hline(cx - 20, cx + 20, yy, K, 1)
                elif t:
                    s, t = _one_line(c, t, r, z, iw, 10)
                    c.text(cx, yy + (h - c.line_h(r, s)) / 2 if r != "pf700" else yy + (26 - s) / 2, t, r, s, f,
                           align="c", lh=1 if r == "pf700" else None)
                yy += h + 4
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    from ..plugins import watchlist as WL
    c = _paper()
    y = _big_mast(c, ctx, _issue(ctx, v.get("place", "")), _week(ctx, ctx.t("Business", "Wirtschaft"))) + 10
    # headline + kicker on one baseline
    hs = 30
    a, b = ctx.t("The markets", "Die Börse"), ctx.t("at the close", "zum Schluss")
    sub = v.get("subtitle", "")
    while True:
        hw = c.tw(a + " ", "pf900", hs) + c.tw(b, "pf700i", hs)
        if hw <= (X1 - X0) * 0.55 or hs <= 18:
            break
        hs -= 1
    c.text(X0, y, a, "pf900", hs, K, lh=1)
    c.text(X0 + c.tw(a + " ", "pf900", hs), y, b, "pf700i", hs, R, lh=1)
    base = c._baseline(y, "pf900", hs, 1)
    room = X1 - X0 - hw - 20
    ks, ktr = 13, 4.0
    st = sub.upper()
    while ks > 9 and c.tw(st, "ss600", ks, ktr) - ktr > room:
        ks -= 1
        ktr = max(1.0, ktr - 0.5)
    st = _ell(c, st, "ss600", ks, room, ktr)
    c.text(X1, base - c._baseline(0, "ss600", ks, None), st, "ss600", ks, R, track=ktr, align="r")
    y += hs + 10
    # footer
    fL = c.line_h("ss400i", 12)
    fy = 460 - fL
    c.hline(X0, X1, fy - 6, K, 1)
    right = ctx.t("Dotted: level {n} days ago", "Gepunktet: Stand vor {n} Tagen", n=v.get("days", 30))
    rw = c.tw(right, "ss400i", 12)
    c.text(X1, fy, right, "ss400i", 12, K, align="r")
    c.text(X0, fy, _ell(c, v.get("footer", ""), "ss400i", 12, X1 - X0 - rw - 16), "ss400i", 12, K)
    # table
    c.hline(X0, X1, y, K, 1)
    y += 1 + 5
    PW, CW, SW = 130, 110, 220
    xc = X1 - CW
    xp = xc - 16 - PW
    xs = xp - 16 - SW
    _head(c, X0, y, ctx.t("Security", "Wert"), xs - 16 - X0, 13)
    _head(c, xs, y, ctx.t("Trend", "Verlauf"), SW, 13)
    for x_r, txt, wd in ((xp + PW, ctx.t("Price", "Kurs"), PW), (X1, ctx.t("Day", "Tag"), CW)):
        t = _ell(c, txt.upper(), "pf700", 13, wd, 1.5)
        c.text(x_r, y, t, "pf700", 13, K, track=1.5, align="r")
    y += c.line_h("pf700", 13) + 4
    c.hline(X0, X1, y, K, 1)
    y += 1
    items = v.get("items") or []
    room = fy - 6 - y
    n = min(len(items), max(1, int(room // 46)))
    items = items[:n]
    rh = room / max(1, n)
    for i, it in enumerate(items):
        ry = y + i * rh
        mid = ry + rh / 2
        col = INK.get(it.get("color", "black"), K) if it.get("ok") else K
        nsz = 24
        nl = c.wrap(it["label"], "pf700", nsz, xs - 16 - X0)
        while len(nl) > (2 if rh > 60 else 1) and nsz > 14:
            nsz -= 1
            nl = c.wrap(it["label"], "pf700", nsz, xs - 16 - X0)
        nl = nl[:2 if rh > 60 else 1]
        nl[-1] = _ell(c, nl[-1], "pf700", nsz, xs - 16 - X0)
        nL = nsz * 1.05
        c.para(X0, mid - len(nl) * nL / 2, xs - 16 - X0, nl, "pf700", nsz, nL, K)
        sh = min(44, rh - 8)
        if it.get("ok"):
            pts = WL.spark_points(it["values"], xs + 2, mid - sh / 2 + 4, SW - 4, sh - 8)
            fy0 = pts[0][1]
            for xx in range(int(xs), int(xs + SW), 4):
                c.d.point((xx, round(fy0)), fill=K)
            c.stroke(pts, col, 2.5)
            c.circle(pts[-1][0], pts[-1][1], 3, fill=col)
            pr = it["last_text"]
            ch = it["change_text"]
        else:
            et = it.get("error") or "–"
            c.text(xs, mid - c.line_h("ss400i", 13) / 2, _ell(c, et, "ss400i", 13, SW), "ss400i", 13, R)
            pr, ch = "–", "–"
        ps, pr = _one_line(c, pr, "ss600", 20, PW, 12)
        c.text(xp + PW, mid - c.line_h("ss600", ps) / 2, pr, "ss600", ps, K, align="r")
        cs, ch = _one_line(c, ch, "ss600", 18, CW - 18, 11)
        c.text(X1, mid - c.line_h("ss600", cs) / 2, ch, "ss600", cs, col, align="r")
        if it.get("ok") and it.get("direction") in ("up", "down"):
            tx = X1 - c.tw(ch, "ss600", cs) - 6 - 12
            if it["direction"] == "up":
                c.poly([(tx + 6, mid - 5), (tx + 12, mid + 5), (tx, mid + 5)], fill=col)
            else:
                c.poly([(tx, mid - 5), (tx + 12, mid - 5), (tx + 6, mid + 5)], fill=col)
        if i < n - 1:
            _dots(c, X0, X1, ry + rh - 1)
    return c.finish()
