"""Swiss (International Typographic Style) layouts for the plugins – ports of the Swiss-*.dc.html mockups.

Grid: 6 columns of (736 − 5·16) / 6 px between x = 32 and 768, header rule at y = 28, content from
`_head(...)` down to y = 452. Fonts: Inter Tight 900 / 700 / 500 (roles it900, it700, it500).
"""
from ..designs import _sx, numeric_date
from ..plugins import _calendar
from ..studio import B, G, K, R, Y, Canvas, Wh

X0, X1, BOT = 32, 768, 452
COLW = (736 - 80) / 6
COL = {"black": K, "white": Wh, "red": R, "yellow": Y, "green": G, "blue": B}


def _w(n):
    """Width of n grid columns incl. the gaps between them."""
    return n * COLW + (n - 1) * 16


def _ell(c, text, role, size, width, track=0.0):
    """Text cut with … so it fits width."""
    text = text or ""
    if c.tw(text, role, size, track) - track <= width:
        return text
    while text and c.tw(text + "…", role, size, track) - track > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _shrink(c, text, role, size, width, track=0.0, min_size=8):
    """Largest size ≤ size at which one line fits width (track scales with the size)."""
    s = size
    while s > min_size and c.tw(text, role, s, track * s / size) - track * s / size > width:
        s -= 1
    return s, track * s / size


def _fitline(c, text, role, size, width, min_size=11):
    """Shrink to min_size, then cut with … – returns (text, size)."""
    s, _ = _shrink(c, text, role, size, width, 0, min_size)
    return _ell(c, text, role, s, width), s


def _head(c, a, b, cc):
    """The black 6 px rule and the three header cells (columns 1–2, 3–4, 5–6). Returns the content top."""
    c.rect((X0, 28, X1, 34), fill=K)
    for col, t in ((1, a), (3, b), (5, cc)):
        if t:
            c.text(_sx(col), 42, _ell(c, t, "it500", 13, _w(2) - 6), "it500", 13, K)
    return 42 + c.line_h("it500", 13) + 14


def _foot(c, x, left, right="→", x1=X1):
    """Footer line at the bottom: 1 px rule, 13 px text left and right. Returns the rule's y."""
    fL = c.line_h("it500", 13)
    y = BOT - fL - 6 - 1
    c.hline(x, x1, y, K, 1)
    rw = c.tw(right, "it500", 13) if right else 0
    if left:
        c.text(x, y + 7, _ell(c, left, "it500", 13, x1 - x - rw - 12), "it500", 13, K)
    if right:
        c.text(x1, y + 7, right, "it500", 13, K, align="r")
    return y


def _kv(c, x, y, x1, rows, size=15, lab_w=96, gap=4, bottom=None):
    """Label/value table under a 1 px rule (labels it500, values it700). Returns the end y."""
    c.hline(x, x1, y, K, 1)
    y += 1 + 8
    L = c.line_h("it500", size)
    lw = max([lab_w] + [c.tw(a, "it500", size) for a, _ in rows])
    lw = min(lw, (x1 - x) * 0.45)
    for a, b in rows:
        if bottom is not None and y + L > bottom:
            break
        c.text(x, y, _ell(c, a, "it500", size, lw), "it500", size, K)
        c.text(x + lw + 16, y, _ell(c, b, "it700", size, x1 - x - lw - 16), "it700", size, K)
        y += L + gap
    return y


def _cap(s):
    return s[:1].upper() + s[1:] if s else s


def _today_line(ctx, d, time=None):
    s = f"{_calendar.weekday(d, ctx.lang)} {numeric_date(d, ctx.lang)}"
    return f"{s} · {time}" if time else s


def _big(c, x, top, text, size, width, lh=0.78, track_per_px=-8 / 150, role="it900", fill=K, min_size=30):
    """Huge tight numeral/word (line-height < 1) shrunk to width. Returns (size, height, track)."""
    s, tr = _shrink(c, text, role, size, width, track_per_px * size, min_size)
    c.text(x, top, text, role, s, fill, track=tr, lh=lh)
    return s, s * lh, tr


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = Canvas("swiss", Wh)
    doy = v["today"].timetuple().tm_yday
    top = _head(c, v["title"], _today_line(ctx, v["today"]),
                f"{v['source']} · " + ctx.t("No. {n}", "Nr. {n}", n=doy))
    s = 42
    bx, by = X0 + 14 + 6 + 1, top + 1
    c.rect((bx - 1, by - 1, bx + 8 * s + 1, by + 8 * s + 1), outline=K)
    last = list(v.get("last_cells") or [])
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            x, y = bx + col * s, by + r * s
            fill = Y if (r + col) % 2 == 1 else Wh
            if len(last) == 2 and (r, col) == tuple(last[1]):
                fill = R
            c.rect((x, y, x + s, y + s), fill=fill)
            if len(last) == 2 and (r, col) == tuple(last[0]):
                c.rect((x, y, x + s, y + s), outline=K, width=3)
            chess_puzzle.draw_piece(c.d, p, x + s // 2, y + s // 2, s)
    if v.get("show_coords", True):
        for i, k in enumerate(v["ranks"]):
            c.text(X0, by + i * s, k, "it500", 11, K, lh=s / 11)
        for i, f in enumerate(v["files"]):
            c.text(bx + i * s + s / 2, by + 8 * s + 1 + 4, f, "it500", 11, K, align="c")
    # right column
    x = _sx(4)
    rw = X1 - x
    L22 = c.line_h("it700", 22)
    sq = (x, top + (L22 - 16) / 2, x + 16, top + (L22 + 16) / 2)
    if v["white_to_move"]:
        c.rect(sq, fill=Wh, outline=K, width=2)
    else:
        c.rect(sq, fill=K)
    s22, _ = _shrink(c, v["to_move"], "it700", 22, rw - 26)
    c.text(x + 26, top, v["to_move"], "it700", s22, K, lh=L22 / s22)
    y = top + L22 + 18
    if v.get("mate_in"):
        lab, n = ctx.t("Mate in", "Matt in"), str(v["mate_in"])
    else:
        lab, n = ctx.t("Moves", "Züge"), str(v["moves"])
    nh = 170 * 0.78
    nw = c.tw(n, "it900", 170, -8) + 8
    ls, _ = _shrink(c, lab, "it700", 34, rw - nw - 14, min_size=16)
    lw = c.tw(lab, "it700", ls)
    c.text(x, y + nh - 6 - ls, lab, "it700", ls, K, lh=1)
    c.text(x + lw + 14, y, n, "it900", 170, K, track=-8, lh=0.78)
    y += nh + 22
    rows = []
    if v.get("themes"):
        rows.append((ctx.t("Themes", "Themen"), " · ".join(t for t in v["themes"] if t != v.get("mate"))
                     or v["themes_text"]))
    if v.get("rating"):
        rows.append((ctx.t("Rating", "Wertung"), str(v["rating"])))
    mv = v["moves"]
    rows.append((ctx.t("Solution", "Lösung"),
                 ctx.t("{n} move", "{n} Zug", n=mv) if mv == 1 else ctx.t("{n} moves", "{n} Züge", n=mv)))
    if v.get("last"):
        rows.append((ctx.t("Last move", "Letzter Zug"), f"{v['last'][0]} → {v['last'][1]}"))
    fy = BOT - c.line_h("it500", 13) - 7
    _kv(c, x, y, X1, rows, 15, bottom=fy - 4)
    _foot(c, x, v["hint"])
    return c.finish()


# ================================================================== spotify
def _cover_placeholder(c, x, y):
    c.rect((x, y, x + 360, y + 360), fill=B)
    c.circle(x + 236, y + 138, 104, fill=Y)
    c.rect((x, y + 242, x + 360, y + 360), fill=K)
    c.rect((x, y, x + 120, y + 242), fill=Wh)
    c.rect((x + 24, y + 24, x + 96, y + 32), fill=K)
    c.rect((x + 24, y + 40, x + 72, y + 48), fill=K)
    for yy, ww in ((270, 200), (290, 150), (310, 100)):
        c.rect((x + 24, y + yy, x + 24 + ww, y + yy + 3), fill=Wh)
    c.rect((x + 288, y + 270, x + 336, y + 336), fill=Y)


def spotify(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"], v["time"]), v["place"])
    side = min(360, BOT - top)
    if v.get("image") is not None:
        c.img.paste(ctx.punch(ctx.cover_fit(v["image"], side, side)), (X0, round(top)))
    else:
        _cover_placeholder(c, X0, top)
    x = _sx(4)
    rw = X1 - x
    L13 = c.line_h("it500", 13)
    c.rect((x, top + (L13 - 16) / 2, x + 16, top + (L13 + 16) / 2), fill=R if v["playing"] else K)
    c.text(x + 26, top, _ell(c, v["label"], "it500", 13, rw - 26), "it500", 13, K)
    y = top + max(16, L13)
    # bottom block: big duration, rule, scale
    ly = BOT - c.line_h("it500", 11)
    ry = ly - 4 - 6
    dur = v.get("duration_text") or ""
    if dur:
        bt = ry - 14 - 88 * 0.8
        c.text(x, bt, dur, "it900", 88, K, track=-4, lh=0.8)
        c.text(x, ly, "0:00", "it500", 11, K)
        c.text(X1, ly, dur, "it500", 11, K, align="r")
    else:
        bt = ry - 8
    c.rect((x, ry, x + 6, ry + 6), fill=K)
    c.hline(x, X1, ry + 2.5, K, 1)
    # texts
    aL, alL = c.line_h("it700", 22, 1.1), c.line_h("it500", 16)
    rest = (14 + aL if v["artist"] else 0) + (2 + alL if v["album"] else 0)
    avail = bt - 12 - (y + 14) - rest
    size, lines, L, tr = c.fit(v["track"], "it700", 40, rw, avail, lh=1.02, track=-1, min_size=18)
    maxl = max(1, int(avail // L))
    if len(lines) > maxl:
        lines = lines[:maxl]
        lines[-1] = _ell(c, lines[-1] + "…", "it700", size, rw, tr)
    y += 14
    c.para(x, y, rw, lines, "it700", size, L, K, tr)
    y += len(lines) * L
    if v["artist"]:
        y += 14
        c.text(x, y, _ell(c, v["artist"], "it700", 22, rw), "it700", 22, K, lh=1.1)
        y += aL
    if v["album"]:
        y += 2
        c.text(x, y, _ell(c, v["album"], "it500", 16, rw), "it500", 16, K)
    return c.finish()


# ================================================================== grid (Stromampel)
def grid(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"], v["time"]), v["place"])
    # bottom band (row 3)
    axL = c.line_h("it500", 11)
    ay = BOT - axL
    band_b = ay - 4
    band_t = band_b - 58
    bar_t = band_b - 34
    for seg in v["segments"]:
        x0 = X0 + 736 * seg["start"] / 24
        x1 = X0 + 736 * seg["end"] / 24
        c.rect((x0, bar_t, x1, band_b - 2), fill=COL.get(seg["color"], Wh))
    c.rect((X0, band_b - 2, X1, band_b), fill=K)
    nx = X0 + 736 * v["now_pos"]
    c.rect((nx - 1, band_t + 14, nx + 1, band_b), fill=K)
    c.rect((nx - 7, band_t, nx + 7, band_t + 14), fill=R)
    tw = c.tw(v["time"], "it700", 11)
    if nx + 12 + tw <= X1:
        c.text(nx + 12, band_t, v["time"], "it700", 11, K, lh=14 / 11)
    else:
        c.text(nx - 12, band_t, v["time"], "it700", 11, K, lh=14 / 11, align="r")
    src_w = 736 * 0.45
    src = _ell(c, v["source"], "it500", 11, src_w)
    if v["now_pos"] > 0.5:
        c.text(X0, band_t, src, "it500", 11, K, lh=14 / 11)
    else:
        c.text(X1, band_t, src, "it500", 11, K, lh=14 / 11, align="r")
    for i, t in enumerate(("0", "6", "12", "18", "24 h")):
        c.text(X0 + 736 * i / 4, ay, t, "it500", 11, K, align="l" if i == 0 else "r" if i == 4 else "c")
    rb = band_t - 14
    # left: the signal word, colour bar, share line
    lw = _w(3)
    word = _cap((v["signal_name"] or "–").split(" · ")[0])
    _big(c, X0, top, word, 150, lw)
    line = ctx.t("{p} renewable", "{p} erneuerbar", p=v["share_text"]) if v.get("share") is not None else ""
    if v.get("congestion"):
        line = _cap(v["signal_name"].split(" · ", 1)[-1])
    s28, _ = _shrink(c, line, "it700", 28, lw, min_size=14)
    ly = rb - s28
    c.text(X0, ly, line, "it700", s28, K, lh=1)
    c.rect((X0, ly - 10 - 14, X0 + lw, ly - 10), fill=COL.get(v["color"] or "", Wh), outline=K if not v["color"] else None)
    # right: advice, best window, coming segments
    x = _sx(4)
    rw = X1 - x
    c.text(x, top, ctx.t("Recommendation", "Empfehlung"), "it500", 13, K)
    y = top + c.line_h("it500", 13) + 4
    advice = {"green": ctx.t("Wash, charge, run the dishwasher now.", "Jetzt waschen, laden, spülen."),
              "yellow": ctx.t("Use power with care.", "Strom bewusst nutzen."),
              "red": ctx.t("Shift consumption if you can.", "Verbrauch möglichst verschieben.")}.get(v["color"], "")
    upcoming = [s for s in v["segments"] if s["end"] > v["now_pos"] * 24 and not s["now"]][:3]
    rL = c.line_h("it500", 14)
    tab_h = (len(upcoming) * (rL + 6) - 6 + 9) if upcoming else 0
    tab_t = rb - tab_h
    best = v.get("best_text") or ""
    bL = c.line_h("it500", 15)
    blines = c.wrap(best, "it500", 15, rw)[:2] if best else []
    adv_h = tab_t - 12 - y - (10 + len(blines) * bL if blines else 0)
    if advice:
        size, lines, L, tr = c.fit(advice, "it700", 34, rw, adv_h, lh=1.02, track=-0.5, min_size=16)
        c.para(x, y, rw, lines, "it700", size, L, K, tr)
        y += len(lines) * L
    if blines:
        y += 10
        c.para(x, y, rw, blines, "it500", 15, bL, K)
    if upcoming:
        c.hline(x, X1, tab_t, K, 1)
        yy = tab_t + 9
        tcol = max(82, max(c.tw(f"{s['from']}–{s['to']}", "it700", 14) for s in upcoming))
        for s in upcoming:
            c.rect((x, yy + rL / 2 - 5, x + 24, yy + rL / 2 + 5), fill=COL.get(s["color"], Wh), outline=K)
            c.text(x + 34, yy, f"{s['from']}–{s['to']}", "it700", 14, K)
            nx0 = x + 34 + tcol + 10
            c.text(nx0, yy, _ell(c, _cap(s["name"]), "it500", 14, X1 - nx0), "it500", 14, K)
            yy += rL + 6
    return c.finish()


# ================================================================== wordclock
def wordclock(ctx, v):
    from ..plugins._calendar import draw_moon
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _cap(v["phrase"]), v["place"])
    rows, cols = v["rows"], v["cols"]
    cw, ch, gap = 33, 31, 3
    gw = cols * (cw + gap) - gap
    gh = rows * (ch + gap) - gap
    avail_w = _w(4)
    if gw > avail_w or gh > BOT - top:
        k = min(avail_w / gw, (BOT - top) / gh)
        cw, ch, gap = int(cw * k), int(ch * k), max(1, int(gap * k))
        gh = rows * (ch + gap) - gap
    gy = top + (BOT - top - gh) / 2
    lit = {tuple(p) for p in v["lit"]}
    for r, line in enumerate(v["grid"]):
        for col, letter in enumerate(line):
            x, y = X0 + col * (cw + gap), gy + r * (ch + gap)
            on = (r, col) in lit
            if on:
                c.rect((x, y, x + cw, y + ch), fill=K)
            c.text(x + cw / 2, y, letter, "it900" if on else "it500", 20, Wh if on else K, lh=ch / 20, align="c")
    x = _sx(5)
    rw = X1 - x
    c.text(x, top, _ell(c, v["weekday"], "it700", 22, rw), "it700", 22, K)
    y = top + c.line_h("it700", 22) + 10
    day = str(v["day"])
    c.text(x, y, day, "it900", 140, K, track=-8, lh=0.78)
    dx = x + c.tw(day, "it900", 140, -8) + 8 + 12
    c.rect((dx, y + 4, dx + 18, y + 22), fill=R)
    y += 140 * 0.78 + 10
    my = f"{v['month']} {v['year']}"
    c.text(x, y, _ell(c, my, "it700", 22, rw), "it700", 22, K)
    # table at the bottom
    L = c.line_h("it500", 14)
    ty = BOT - 3 * L - 2 * 8 - 9
    c.hline(x, X1, ty, K, 1)
    labs = (ctx.t("Minutes", "Minuten"), ctx.t("Time", "Uhrzeit"), ctx.t("Moon", "Mond"))
    lw = min(rw / 2 - 8, max(c.tw(t, "it500", 14) for t in labs))
    vx = x + lw + 16
    y = ty + 9
    extra = max(0, min(4, v["now"].minute - v["minute"]))
    c.text(x, y, _ell(c, ctx.t("Minutes", "Minuten"), "it500", 14, lw), "it500", 14, K)
    for i in range(4):
        bx = vx + i * 20
        by = y + L / 2 - 7
        if i < extra:
            c.rect((bx, by, bx + 14, by + 14), fill=K)
        else:
            c.rect((bx + 1, by + 1, bx + 13, by + 13), outline=K)
    y += L + 8
    c.text(x, y, _ell(c, ctx.t("Time", "Uhrzeit"), "it500", 14, lw), "it500", 14, K)
    c.text(vx, y, f"{v['now']:%H:%M}", "it700", 14, K)
    y += L + 8
    c.text(x, y, _ell(c, ctx.t("Moon", "Mond"), "it500", 14, lw), "it500", 14, K)
    draw_moon(c.d, vx + 8, y + L / 2, 7, v["phase"], Wh, K, K)
    mt, ms = _fitline(c, v["moon"], "it700", 14, X1 - vx - 22)
    c.text(vx + 22, y, mt, "it700", ms, K, lh=L / ms)
    return c.finish()


# ================================================================== countdown
def countdown(ctx, v):
    c = Canvas("swiss", Wh)
    t = v["today"]
    top = _head(c, v["title"], _today_line(ctx, t),
                ctx.t("Day {n}", "Tag {n}", n=t.timetuple().tm_yday) + " · "
                + ctx.t("WK {n}", "KW {n}", n=t.isocalendar()[1]))
    strip = v.get("strip") or []
    rb = BOT
    if strip:
        lL = c.line_h("it500", 11)
        ly = BOT - lL
        sb = ly - 5
        st = sb - 22
        rb = st - 14
        n = len(strip)
        gap = 3 if n <= 80 else 1 if n <= 160 else 0
        cw = (736 - gap * (n - 1)) / n
        for i, e in enumerate(strip):
            x0 = X0 + i * (cw + gap)
            x1 = x0 + cw
            if e["today"]:
                c.rect((x0, st, x1, sb), fill=R)
            elif e["target"]:
                c.rect((x0, st, x1, sb), fill=K)
            else:
                fill = Y if (e["weekend"] or e["special"]) else Wh
                c.rect((x0, st, x1, sb), fill=fill, outline=K if cw >= 5 else None)
        if cw < 5:
            c.rect((X0, st, X1, sb), outline=K)
        wd = lambda d: _calendar.weekday_short(d, ctx.lang)  # noqa: E731
        now_lab = f"{ctx.t('Today', 'Heute')} · {wd(t)} {v['today_short']}"
        ev_lab = f"{v['event']} · {wd(v['target'])} {v['date_short']}"
        left, right = (now_lab, ev_lab) if v["state"] != "past" else (ev_lab, now_lab)
        firsts = [e for e in strip[1:] if e["first_of_month"]]
        mid = f"{_calendar.month(firsts[0]['date'], ctx.lang)} →" if firsts else ""
        mw = c.tw(mid, "it500", 11) if mid else 0
        side = (736 - mw - 40) / 2
        c.text(X0, ly, _ell(c, left, "it500", 11, side), "it500", 11, K)
        c.text(X1, ly, _ell(c, right, "it500", 11, side), "it500", 11, K, align="r")
        if mid:
            c.text(X0 + 368, ly, mid, "it500", 11, K, align="c")
    # left: the big figure, bottom-aligned
    big = v["big"]
    lw = _w(3)
    s, tr = _shrink(c, big, "it900", 290, lw, -18, 40)
    h = s * 0.76
    if big.isdigit() or s >= 120:
        c.text(X0, rb - h, big, "it900", s, K, track=tr, lh=0.76)
    else:          # "Today!" in a long language: wrap into the column
        size, lines, L, tr2 = c.fit(big, "it900", 120, lw, rb - top, lh=0.9, track=-6, min_size=40)
        c.para(X0, rb - len(lines) * L, lw, lines, "it900", size, L, K, tr2)
    # right: small line, event, facts
    x = _sx(4)
    rw = X1 - x
    rows = [(ctx.t("Target", "Ziel"), f"{v['target_weekday']}, {v['date']}")]
    if v["count"] >= 7:
        wk = str(v["weeks"]) + (f" + {v['rest_days']} {ctx.t('d', 'T')}" if v["rest_days"] else "")
        rows.append((ctx.t("Weeks", "Wochen"), wk))
    if v["weekends"]:
        rows.append((ctx.t("Weekends", "Wochenenden"), str(v["weekends"])))
    L14 = c.line_h("it500", 14)
    ty = rb - (1 + 6 + len(rows) * (L14 + 2) - 2)
    y = top
    if v["small"]:
        st_, ss = _fitline(c, v["small"], "it700", 22, rw)
        c.text(x, y, st_, "it700", ss, K)
        y += c.line_h("it700", ss) + 6
    size, lines, L, tr = c.fit(v["event"], "it700", 46, rw, ty - 12 - y, lh=1.0, track=-1.5, min_size=16)
    maxl = max(1, int((ty - 12 - y) // L))
    if len(lines) > maxl:
        lines = lines[:maxl]
        lines[-1] = _ell(c, lines[-1] + "…", "it700", size, rw, tr)
    c.para(x, y, rw, lines, "it700", size, L, K, tr)
    c.hline(x, X1, ty, K, 1)
    yy = ty + 7
    lab_w = min(max([80] + [c.tw(a, "it500", 14) for a, _ in rows]), rw * 0.45)
    for a, b in rows:
        c.text(x, yy, _ell(c, a, "it500", 14, lab_w), "it500", 14, K)
        bt, bs = _fitline(c, b, "it700", 14, rw - lab_w - 16)
        c.text(x + lab_w + 16, yy, bt, "it700", bs, K, lh=L14 / bs)
        yy += L14 + 2
    return c.finish()


# ================================================================== art
def art(ctx, v):
    c = Canvas("swiss", Wh)
    t = v["today"]
    top = _head(c, v["title"], _today_line(ctx, t), ctx.t("No. {n}", "Nr. {n}", n=v["doy"]))
    fL = c.line_h("it500", 13)
    fy = BOT - fL - 6 - 1
    # picture: fit inside the slot (columns 1–4), 1 px frame with 10 px padding
    sw, sh = _w(4), fy - 12 - top
    img = v["image"]
    k = min((sw - 22) / img.width, (sh - 22) / img.height)
    iw, ih = max(1, round(img.width * k)), max(1, round(img.height * k))
    fx = X0 + (sw - iw - 22) / 2
    fyy = top + (sh - ih - 22) / 2
    c.rect((fx, fyy, fx + iw + 22, fyy + ih + 22), outline=K)
    c.img.paste(img.convert("RGB").resize((iw, ih)), (round(fx + 11), round(fyy + 11)))
    # right column
    x = _sx(5)
    rw = X1 - x
    c.rect((x, top, x + 18, top + 18), fill=R)
    rows = [(a, b) for a, b in ((ctx.t("Technique", "Technik"), v["medium"]),
                                (ctx.t("Size", "Maße"), v["dimensions"]),
                                (ctx.t("Origin", "Herkunft"), v["origin"])) if b]
    L14 = c.line_h("it500", 14)
    bottom = fy - 12
    if rows:
        ty = bottom - (1 + 6 + len(rows) * (L14 + 2) - 2)
        c.hline(x, X1, ty, K, 1)
        yy = ty + 7
        lw = min(max([70] + [c.tw(a, "it500", 14) for a, _ in rows]), rw * 0.42)
        for a, b in rows:
            c.text(x, yy, _ell(c, a, "it500", 14, lw), "it500", 14, K)
            bt, bs = _fitline(c, b, "it700", 14, rw - lw - 12)
            c.text(x + lw + 12, yy, bt, "it700", bs, K, lh=L14 / bs)
            yy += L14 + 2
        bottom = ty - 14
    if v["date"]:
        ds, dtr = _shrink(c, v["date"], "it900", 92, rw, -5, 24)
        if c.tw(v["date"], "it900", ds, dtr) - dtr <= rw:
            c.text(x, bottom - ds * 0.78, v["date"], "it900", ds, K, track=dtr, lh=0.78)
            bottom -= ds * 0.78
        else:
            dt, dss = _fitline(c, v["date"], "it700", 19, rw)
            c.text(x, bottom - dss * 1.1, dt, "it700", dss, K, lh=1.1)
            bottom -= dss * 1.1
    y = top + 18 + 14
    aL = c.line_h("it700", 19, 1.1)
    alines = c.wrap(v["artist"], "it700", 19, rw)[:2] if v["artist"] else []
    avail = bottom - 12 - y - (10 + len(alines) * aL if alines else 0)
    size, lines, L, tr = c.fit(v["work"], "it900", 36, rw, avail, lh=0.98, track=-1, min_size=16)
    maxl = max(1, int(avail // L))
    if len(lines) > maxl:
        lines = lines[:maxl]
        lines[-1] = _ell(c, lines[-1] + "…", "it900", size, rw, tr)
    c.para(x, y, rw, lines, "it900", size, L, K, tr)
    y += len(lines) * L
    if alines:
        y += 10
        if len(c.wrap(v["artist"], "it700", 19, rw)) > 2:
            alines[-1] = _ell(c, alines[-1] + "…", "it700", 19, rw)
        c.para(x, y, rw, alines, "it700", 19, aL, K)
    # footer
    left = " · ".join(p for p in (v["artist"], v["work"], v["date"], v["museum"]) if p)
    _foot(c, X0, left, v["license"])
    return c.finish()


# ================================================================== waste
def _bin(c, x, y, w, col, small=False):
    """The mockup's bin (viewBox 40 × 48) at (x, y), w px wide."""
    k = w / 40
    sw = max(1, round(k * (2 if small else 1)))
    if not small:
        c.rect((x + 15 * k, y + 1 * k, x + 25 * k, y + 5 * k), fill=K)
        c.rect((x + 2 * k, y + 5 * k, x + 38 * k, y + 10 * k), fill=col, outline=K, width=sw)
    else:
        c.rect((x + 2 * k, y + 4 * k, x + 38 * k, y + 10 * k), fill=col, outline=K, width=sw)
    c.poly([(x + 5 * k, y + 12 * k), (x + 35 * k, y + 12 * k), (x + 32 * k, y + 46 * k), (x + 8 * k, y + 46 * k)],
           fill=col, outline=K, width=sw)
    if not small:
        c.rect((x + 12 * k, y + 18 * k, x + 28 * k, y + 20 * k), fill=Wh if col == K else K)


def waste(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"]), v["place"])
    soon, rows = v["soon"], list(v["rows"])
    if soon:
        hero = {"label": soon["label"], "items": soon["items"], "names": soon["names_text"],
                "sub": f"{soon['weekday']} {soon['date_short']}"}
        if not soon["is_today"]:
            hero["sub"] += " · " + ctx.t("put the bins out tonight", "heute Abend an die Straße")
    else:
        d0 = rows[0]["date"]
        same = [r for r in rows if r["date"] == d0]
        rows = [r for r in rows if r["date"] != d0]
        hero = {"label": same[0]["weekday"], "items": same, "names": " + ".join(r["name"] for r in same),
                "sub": f"{same[0]['date_short']} · {same[0]['in_text']}"}
    # rows at the bottom
    L19 = c.line_h("it500", 19)
    rh = 1 + 6 + L19 + 6
    show = rows[:4]
    texts = []
    if not show and soon:
        texts = [v["empty_text"]]
    nrows = len(show) or len(texts)
    rt = BOT - nrows * rh
    y = rt
    dcol = max([_w(1) + 16 - 28] + [c.tw(r["date_text"], "it700", 19) + 12 for r in show])
    dcol = min(dcol, _w(2) - 28)
    nx = max(_sx(2), X0 + 28 + dcol)
    for r in show:
        c.hline(X0, X1, y, K, 1)
        ty = y + 7
        _bin(c, X0, ty + (L19 - 22) / 2, 18, COL.get(r["color"], Wh), small=True)
        c.text(X0 + 28, ty, _ell(c, r["date_text"], "it700", 19, nx - X0 - 28 - 10), "it700", 19, K)
        # "in 4 Tagen" with the number in 900
        it = r["in_text"]
        n = str(r["days"])
        i = it.find(n)
        right_w = _w(2)
        if i >= 0:
            parts = [(it[:i], "it500"), (n, "it900"), (it[i + len(n):], "it500")]
            tot = sum(c.tw(p, f, 19) for p, f in parts)
            xx = X1 - tot
            for p, f in parts:
                c.text(xx, ty, p, f, 19, K)
                xx += c.tw(p, f, 19)
        else:
            tot = c.tw(it, "it500", 19)
            c.text(X1, ty, _ell(c, it, "it500", 19, right_w), "it500", 19, K, align="r")
        c.text(nx, ty, _ell(c, r["name"], "it500", 19, X1 - min(tot, right_w) - 16 - nx), "it500", 19, K)
        y += rh
    for tx in texts:
        c.hline(X0, X1, y, K, 1)
        c.text(X0, y + 7, _ell(c, tx, "it500", 19, 736), "it500", 19, K)
        y += rh
    rb = rt - 14
    # right: bins of the hero day, bottom-right
    items = hero["items"][:4]
    n = len(items)
    bw = min(92, (_w(2) - 16 * (n - 1)) / max(1, n))
    bh = bw * 48 / 40
    for i, it in enumerate(reversed(items)):
        bx = X1 - (i + 1) * bw - i * 16
        _bin(c, bx, rb - bh, bw, COL.get(it["color"], Wh))
    # left: big day word, names, sub line
    lw = _w(4)
    sq = 20 + 14
    s, tr = _shrink(c, hero["label"], "it900", 128, lw - sq, -7, 40)
    c.text(X0, top, hero["label"], "it900", s, K, track=tr, lh=0.78)
    qx = X0 + c.tw(hero["label"], "it900", s, tr) - tr + 14
    c.rect((qx, top + 4, qx + 20, top + 24), fill=R)
    sub_t, sub_s = _fitline(c, hero["sub"], "it500", 15, lw)
    sy = rb - c.line_h("it500", sub_s)
    c.text(X0, sy, sub_t, "it500", sub_s, K)
    avail = sy - 4 - (top + s * 0.78 + 16)
    size, lines, L, tr2 = c.fit(hero["names"], "it700", 34, lw, avail, lh=1.05, track=-0.5, min_size=16)
    maxl = max(1, int(avail // L))
    if len(lines) > maxl:
        lines = lines[:maxl]
        lines[-1] = _ell(c, lines[-1] + "…", "it700", size, lw, tr2)
    c.para(X0, sy - 4 - len(lines) * L, lw, lines, "it700", size, L, K, tr2)
    return c.finish()


# ================================================================== warnings
def warnings(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"], v["updated"]), v["source"])
    # bottom: the four levels
    n = v["levels"]
    L12 = c.line_h("it500", 12)
    lt = BOT - L12 - 5 - 10
    cw = (736 - 16 * (n - 1)) / n
    for i in range(n):
        x0 = X0 + i * (cw + 16)
        if i < v["level"]:
            c.rect((x0, lt, x0 + cw, lt + 10), fill=K)
        else:
            c.rect((x0, lt, x0 + cw, lt + 10), outline=K)
        role = "it700" if i + 1 == v["level"] else "it500"
        t, s = _fitline(c, f"{i + 1} · {v['level_names'][i]}", role, 12, cw, 9)
        c.text(x0, lt + 15, t, role, s, K, lh=L12 / s)
    rb = lt - 14
    # left: level number
    lw = _w(2)
    c.text(X0, top, _ell(c, ctx.t("Warning level", "Warnstufe"), "it500", 13, lw), "it500", 13, K)
    y = top + c.line_h("it500", 13) + 10
    big = 250
    of_h = 12 + c.line_h("it700", 22)
    big = min(big, int((rb - y - of_h) / 0.76))
    c.text(X0, y, str(v["level"]), "it900", big, K, track=-12 * big / 250, lh=0.76)
    y += big * 0.76 + 12
    c.text(X0, y, _ell(c, ctx.t("of {n}", "von {n}", n=n), "it700", 22, lw), "it700", 22, K)
    # right: level name, event, place/time, description
    x = _sx(3)
    rw = X1 - x
    L22 = c.line_h("it700", 22)
    c.rect((x, top + (L22 - 18) / 2, x + 18, top + (L22 + 18) / 2), fill=COL.get(v["color"], R))
    t, s = _fitline(c, v["level_text"], "it700", 22, rw - 28, 14)
    c.text(x + 28, top, t, "it700", s, K, lh=L22 / s)
    y = top + L22 + 10
    size, lines, L, tr = c.fit(v["event"], "it900", 82, rw, 2 * 82 * 0.9, lh=0.9, track=-3.5, min_size=30)
    if len(lines) > 2:
        lines = lines[:2]
        lines[-1] = _ell(c, lines[-1] + "…", "it900", size, rw, tr)
    c.para(x, y, rw, lines, "it900", size, L, K, tr)
    y += len(lines) * L + 14
    c.hline(x, X1, y, K, 1)
    y += 1 + 8
    ps = v["place_span"] or v["place"]
    if ps:
        t, s = _fitline(c, ps, "it700", 20, rw, 13)
        c.text(x, y, t, "it700", s, K, lh=c.line_h("it700", 20) / s)
        y += c.line_h("it700", 20) + 8
    more = v.get("more_text") or ""
    mb = rb
    if more:
        mL = c.line_h("it700", 15)
        mb = rb - mL
        c.text(x, mb, _ell(c, more, "it700", 15, rw), "it700", 15, K)
        mb -= 8
    desc = v["description"] or v["headline"] or v["instruction"]
    if desc and mb - y > 16:
        size, lines, L, tr = c.fit(desc, "it500", 19, rw, mb - y, lh=1.3, min_size=13)
        maxl = max(0, int((mb - y + 0.5) // L))
        if len(lines) > maxl:
            lines = lines[:maxl]
            if lines:
                lines[-1] = _ell(c, lines[-1] + "…", "it500", size, rw)
        c.para(x, y, rw, lines, "it500", size, L, K)
    return c.finish()


# ================================================================== wifi
def wifi(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"]), v["place"])
    mods = v["modules"]
    n = len(mods)
    side = min(_w(3), BOT - top)
    s = max(1, int(side // (n + 4)))
    qs = s * n
    qx, qy = X0 + 2 * s, round(top + (BOT - top - qs) / 2)
    for r, row in enumerate(mods):
        for col, on in enumerate(row):
            if on:
                c.d.rectangle((qx + col * s, qy + r * s, qx + col * s + s - 1, qy + r * s + s - 1), fill=K)
    x = _sx(4)
    rw = X1 - x
    c.text(x, top, _ell(c, v["network_label"], "it500", 13, rw), "it500", 13, K)
    y = top + c.line_h("it500", 13) + 10
    ssid = v["ssid"]
    sz, tr = _shrink(c, ssid, "it900", 118, rw - 32, -6, 30)
    if c.tw(ssid, "it900", sz, tr) - tr > rw - 32:
        ssid = _ell(c, ssid, "it900", sz, rw - 32, tr)
    c.text(x, y, ssid, "it900", sz, K, track=tr, lh=0.78)
    qx2 = x + c.tw(ssid, "it900", sz, tr) - tr + 14
    c.rect((qx2, y + 2, qx2 + 18, y + 20), fill=R)
    y += sz * 0.78 + 26
    L13 = c.line_h("it500", 13)
    if v["password"]:
        c.hline(x, X1, y, K, 1)
        y += 1 + 8
        c.text(x, y, _ell(c, v["password_label"], "it500", 13, rw), "it500", 13, K)
        y += L13
        t, ps = _fitline(c, v["password"], "it700", 32, rw, 14)
        c.text(x, y, t, "it700", ps, K, track=-0.5 * ps / 32, lh=c.line_h("it700", 32) / ps)
        y += c.line_h("it700", 32) + 10
    c.hline(x, X1, y, K, 1)
    y += 1 + 6
    L14 = c.line_h("it500", 14)
    lab = ctx.t("Encryption", "Verschlüsselung")
    lw = min(rw / 2 - 8, max(c.tw(lab, "it500", 14), (rw - 16) / 2))
    c.text(x, y, _ell(c, lab, "it500", 14, lw), "it500", 14, K)
    sec = v["security"] if not v["open"] and v["security"] else ctx.t("open", "offen")
    c.text(x + lw + 16, y, _ell(c, sec, "it700", 14, rw - lw - 16), "it700", 14, K)
    y += L14
    # footer: arrow + hint
    L20 = c.line_h("it700", 20)
    fy = BOT - L20 - 6 - 1
    if v["note"] and fy - 12 - y > 18:
        nL = c.line_h("it500", 15)
        lines = c.wrap(v["note"], "it500", 15, rw)
        maxl = int((fy - 12 - y - 10) // nL)
        if len(lines) > maxl:
            lines = lines[:maxl]
            if lines:
                lines[-1] = _ell(c, lines[-1] + "…", "it500", 15, rw)
        c.para(x, y + 10, rw, lines, "it500", 15, nL, K)
    c.hline(x, X1, fy, K, 1)
    c.text(x, fy + 7, "←", "it700", 20, K)
    aw = c.tw("←", "it700", 20) + 10
    t, hs = _fitline(c, v["hint"], "it700", 20, rw - aw, 13)
    c.text(x + aw, fy + 7, t, "it700", hs, K, lh=L20 / hs)
    return c.finish()


# ================================================================== habits
def habits(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"]),
                ctx.t("Last {n} weeks", "Letzte {n} Wochen", n=v["weeks"]))
    hs = v["habits"][:6]
    n = len(hs)
    ncol = 2 if n <= 4 else 3
    nrow = 1 if n <= 2 else 2
    gap = 16
    cw = (736 - gap * (ncol - 1)) / ncol
    ch = (BOT - top - gap * (nrow - 1)) / nrow
    best_i = next((i for i, h in enumerate(hs) if h["streak"] and h["streak"] == v["best_streak"]), None)
    letters = v["weekday_letters"]
    today_row = v["now"][1]
    for i, h in enumerate(hs):
        x0 = X0 + (i % ncol) * (cw + gap)
        y0 = top + (i // ncol) * (ch + gap)
        c.hline(x0, x0 + cw, y0, K, 1)
        y = y0 + 1 + 6
        L18 = c.line_h("it700", 18)
        mark = ""
        mw = 0
        if i == best_i:
            mark = ctx.t("longest streak", "längste Serie")
            mw = 8 + 12 + 8 + min(c.tw(mark, "it500", 12), cw * 0.4)
        name = _ell(c, h["name"], "it700", 18, cw - mw)
        c.text(x0, y, name, "it700", 18, K)
        if mark:
            mx = x0 + c.tw(name, "it700", 18) + 8
            c.rect((mx, y + L18 / 2 - 6, mx + 12, y + L18 / 2 + 6), fill=R)
            c.text(mx + 20, y + (L18 - c.line_h("it500", 12)) / 2, _ell(c, mark, "it500", 12, cw * 0.4), "it500", 12, K)
        y += L18 + 8
        # calendar: 7 columns (weekdays) × 6 rows (weeks)
        cell, g = 17, 3
        L11 = c.line_h("it500", 11)
        avail_h = y0 + ch - y
        if L11 + 3 + 6 * (cell + g) - g > avail_h:
            cell = max(8, int((avail_h - L11 - 3 + g) / 6 - g))
        for d, t in enumerate(letters):
            role = "it900" if d == today_row else "it500"
            c.text(x0 + d * (cell + g) + cell / 2, y, t, role, 11, K, align="c")
        gy = y + L11 + 3
        for w, week in enumerate(h["grid"]):
            for d, done in enumerate(week):
                if done is None:
                    continue
                bx, by = x0 + d * (cell + g), gy + w * (cell + g)
                c.rect((bx, by, bx + cell, by + cell), fill=K if done else Wh, outline=K)
        gb = gy + 6 * (cell + g) - g
        gw = 7 * (cell + g) - g
        # streak number, bottom-right
        lab = ctx.t("day in a row", "Tag in Folge") if h["streak"] == 1 else ctx.t("days in a row", "Tage in Folge")
        lt, ls = _fitline(c, lab, "it500", 14, cw - gw - 12, 9)
        Ll = c.line_h("it500", 14)
        num = str(h["streak"])
        ns, ntr = _shrink(c, num, "it900", 104, cw - gw - 12, -5, 30)
        ns = min(ns, int((gb - y - Ll - 6) / 0.78))
        ntr = -5 * ns / 104
        c.text(x0 + cw, gb - Ll, lt, "it500", ls, K, align="r", lh=Ll / ls)
        c.text(x0 + cw + ntr, gb - Ll - 6 - ns * 0.78, num, "it900", ns, R if h["hot"] else K, track=ntr,
               lh=0.78, align="r")
    return c.finish()


# ================================================================== sudoku
def sudoku(ctx, v):
    c = Canvas("swiss", Wh)
    t = v["today"]
    top = _head(c, v["name"], _today_line(ctx, t), ctx.t("No. {n}", "Nr. {n}", n=t.timetuple().tm_yday))
    cs = 38
    # positions of the cell starts: 3 px frame, 1 px lines, 3 px block lines
    pos, p = [], 3
    for i in range(9):
        pos.append(p)
        p += cs + (3 if i in (2, 5) else 1 if i < 8 else 0)
    total = p + 3
    gx, gy = X0, top
    c.rect((gx, gy, gx + total, gy + total), fill=K)
    for r in range(9):
        for col in range(9):
            x, y = gx + pos[col], gy + pos[r]
            c.rect((x, y, x + cs, y + cs), fill=Wh)
            n = v["grid"][r][col]
            if n:
                c.text(x + cs / 2, y, str(n), "it700", 22, K, lh=cs / 22, align="c")
    x = _sx(4)
    rw = X1 - x
    c.text(x, top, _ell(c, ctx.t("Difficulty", "Schwierigkeit"), "it500", 13, rw), "it500", 13, K)
    y = top + c.line_h("it500", 13) + 6
    dots_w = v["level_max"] * 22 - 6
    s, tr = _shrink(c, v["level_name"], "it900", 64, rw - dots_w - 16, -2.5, 24)
    c.text(x, y + (64 - s) * 0.9, v["level_name"], "it900", s, K, track=tr, lh=0.9)
    dx = x + c.tw(v["level_name"], "it900", s, tr) - tr + 16
    cy = y + 64 * 0.9 / 2
    for i in range(v["level_max"]):
        bx = dx + i * 22
        if i < v["level_no"]:
            c.rect((bx, cy - 8, bx + 16, cy + 8), fill=K)
        else:
            c.rect((bx + 1, cy - 7, bx + 15, cy + 7), outline=K)
    y += 64 * 0.9 + 22
    c.hline(x, X1, y, K, 1)
    y += 1 + 14
    g = str(v["givens"])
    c.text(x, y, g, "it900", 150, K, track=-8, lh=0.78)
    qx = x + c.tw(g, "it900", 150, -8) + 8 + 14
    c.rect((qx, y, qx + 18, y + 18), fill=R)
    y += 150 * 0.78 + 10
    t2, s2 = _fitline(c, ctx.t("numbers given", "Zahlen vorgegeben"), "it700", 22, rw, 13)
    c.text(x, y, t2, "it700", s2, K, lh=c.line_h("it700", 22) / s2)
    _foot(c, x, v["hint"])
    return c.finish()


# ================================================================== solar
def _sun(c, x, y):
    cx, cy = x + 36, y + 36
    for a in range(0, 360, 45):
        import math
        r = math.radians(a)
        ux, uy = math.sin(r), -math.cos(r)
        px, py = -uy, ux
        pts = []
        for d0, d1 in ((24, 36),):
            for s_, d in ((-2, d0), (2, d0), (2, d1), (-2, d1)):
                pts.append((cx + ux * d + px * s_, cy + uy * d + py * s_))
        c.poly(pts, fill=K)
    c.circle(cx, cy, 17, fill=Y, outline=K, width=2)


def solar(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"], v["now_text"]), v["place"])
    # chart row
    L11 = c.line_h("it500", 11)
    ly = BOT - L11
    cb = ly - 4          # bottom of the 118 px chart box
    ct = cb - 118
    t0, t1 = v["t0"], v["t1"]
    X = lambda h: X0 + 736 * (h - t0) / (t1 - t0)  # noqa: E731
    peak = v["peak"] or 1
    Yv = lambda w: cb - 2 - 106 * min(max(w, 0), peak) / peak  # noqa: E731
    pts = [(X(h), Yv(w)) for h, w in zip(v["hours"], v["watts"]) if t0 <= h <= t1]
    if len(pts) >= 2:
        c.poly([(pts[0][0], cb - 2)] + pts + [(pts[-1][0], cb - 2)], fill=Y)
        c.stroke(pts, K, 2)
    c.rect((X0, cb - 2, X1, cb), fill=K)
    if v["now_visible"]:
        nx = X(v["now"])
        c.rect((nx - 1, ct, nx + 1, cb - 2), fill=K)
        lab = f"{v['now_text']} · {v['power_text']}"
        lw_ = c.tw(lab, "it700", 11)
        if nx + 8 + lw_ <= X1:
            c.text(nx + 8, ct, lab, "it700", 11, K)
        else:
            c.text(nx - 8, ct, lab, "it700", 11, K, align="r")
    ticks = list(zip(v["ticks"], v["tick_labels"]))
    for i, (h, t) in enumerate(ticks):
        tx = X(h)
        if i == len(ticks) - 1:
            t += " h"
        w_ = c.tw(t, "it500", 11)
        tx = min(max(tx - w_ / 2, X0), X1 - w_)
        c.text(tx, ly, t, "it500", 11, K)
    rb = ct - 14
    # left: power now
    c.text(X0, top, _ell(c, ctx.t("Power now", "Leistung jetzt"), "it500", 13, _w(3)), "it500", 13, K)
    num = str(v["power_w"])
    uw = max(20, c.tw("W", "it700", 40))
    s, tr = _shrink(c, num, "it900", 168, _w(3) - uw - 10, -9, 40)
    nh = s * 0.78
    c.text(X0, rb - nh, num, "it900", s, K, track=tr, lh=0.78)
    ux = X0 + c.tw(num, "it900", s, tr) - tr + 10
    c.rect((ux, rb - nh, ux + 20, rb - nh + 20), fill=R)
    c.text(ux, rb - 32, "W", "it700", 40, K, lh=0.8)
    # right: figures + sun
    x = _sx(4)
    _sun(c, X1 - 72, top)
    tw_ = X1 - 72 - 16 - x
    rows = [(ctx.t("Today", "Heute"), v["today_text"]), (ctx.t("Savings", "Ersparnis"), f"≈ {v['saved_text']}")]
    if v.get("total_text"):
        rows.append((ctx.t("Total", "Gesamt"), v["total_text"]))
    elif v.get("max_text"):
        rows.append((ctx.t("Peak", "Spitze"), v["max_text"]))
    note = v["footer"]
    if v.get("max_text") and v.get("total_text"):
        note = ctx.t("Peak {w} at {t}", "Spitze {w} um {t}", w=v["max_text"], t=v["max_time"]) + " · " + note
    L12 = c.line_h("it500", 12)
    ny = rb - L12
    c.hline(x, X1 - 72 - 16, ny - 4 - 1, K, 1)
    c.text(x, ny, _ell(c, note, "it500", 12, tw_), "it500", 12, K)
    lab_w = min(max([82] + [c.tw(a, "it500", 14) for a, _ in rows]), tw_ * 0.45)
    y = ny - 5 - 6
    for a, b in reversed(rows):
        y -= 28
        c.text(x, y + 28 - c.line_h("it500", 14) + 2, _ell(c, a, "it500", 14, lab_w), "it500", 14, K)
        bs, btr = _shrink(c, b, "it900", 28, tw_ - lab_w - 12, -0.5, 12)
        c.text(x + lab_w + 12, y + 28 - bs, b, "it900", bs, K, track=btr, lh=1)
        y -= 6
    return c.finish()


# ================================================================== waterlevel
def waterlevel(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, f"{v['name']} {v['station']} · {v['water']}",
                _today_line(ctx, v["today"], v["now_text"]), v["source"])
    unit = v["unit"]
    # bottom facts row
    pairs = []
    if v.get("mw") is not None:
        pairs.append((ctx.t("Mean water", "Mittelwasser"), v["mw_text"]))
    if v.get("hsw") is not None:
        pairs.append((ctx.t("Highest navigable", "Höchster SW"), v["hsw_text"]))
    if v.get("change_24h") is not None and v.get("value") is not None:
        pairs.append((ctx.t("Previous day", "Vortag"), f"{ctx.num(v['value'] - v['change_24h'], 0)} {unit}"))
    L13 = c.line_h("it500", 13)
    rb = BOT
    if pairs:
        fy = BOT - L13 - 6 - 1
        c.hline(X0, X1, fy, K, 1)
        for i, (a, b) in enumerate(pairs):
            c.text(_sx(2 * i + 1), fy + 7, _ell(c, a, "it500", 13, _w(1)), "it500", 13, K)
            c.text(_sx(2 * i + 2), fy + 7, _ell(c, b, "it700", 13, _w(1)), "it700", 13, K)
        rb = fy - 14
    # left column
    lw = _w(2)
    c.text(X0, top, _ell(c, ctx.t("Water level", "Wasserstand"), "it500", 13, lw), "it500", 13, K)
    y = top + c.line_h("it500", 13) + 10
    num = v["value_num"]
    s, tr = _shrink(c, num, "it900", 116, lw - 26, -6, 40)
    c.text(X0, y, num, "it900", s, R if v["high"] else K, track=tr, lh=0.78)
    qx = X0 + c.tw(num, "it900", s, tr) - tr + 10
    c.rect((qx, y, qx + 16, y + 16), fill=R)
    y += s * 0.78 + 8
    st = unit + (f" · {v['state_text']}" if v["state_text"] else "")
    t, ss = _fitline(c, st, "it700", 26, lw, 14)
    c.text(X0, y, t, "it700", ss, K, lh=c.line_h("it700", 26) / ss)
    arrow = v["trend_arrow"]
    if v.get("change_24h") is not None:
        big = f"{arrow} {v['change_24h_text']}".strip()
        small = f"{v['trend_text']} {v['change_24h_text']}/24 h".strip()
    else:
        big, small = f"{arrow} {v['trend_text']}".strip(), ""
    if big:
        sL = c.line_h("it500", 15) if small else 0
        bt = rb - sL - (4 if small else 0) - 44
        c.hline(X0, X0 + lw, bt - 8 - 1, K, 1)
        bs, btr = _shrink(c, big, "it900", 44, lw, -1.5, 18)
        c.text(X0, bt + 44 - bs, big, "it900", bs, K, track=btr, lh=1)
        if small:
            t, ss = _fitline(c, small, "it500", 15, lw)
            c.text(X0, rb - sL, t, "it500", ss, K, lh=sL / ss)
    # chart (columns 3–6)
    x0 = _sx(3)
    cw = X1 - x0
    L11 = c.line_h("it500", 11)
    ly = rb - L11
    cb = ly - 4
    ch = min(290, cb - top)
    ct = cb - ch
    vals = v["values"]
    lo = min([v["min"]] + ([v["mw"]] if v.get("mw") is not None else []))
    hi = v["hsw"] if v.get("hsw") is not None else v["axis_hi"]
    hi = max(hi, v["max"])
    pad = (hi - lo) * 0.08 or 10
    lo -= pad
    Yv = lambda val: cb - 2 - (val - lo) / (hi - lo) * (ch - 28)  # noqa: E731
    if v.get("hsw") is not None:
        hy = Yv(v["hsw"]) - 1
        c.rect((x0, hy, X1, hy + 2), fill=K)
        lab = f"HSW {v['hsw_text']} · " + ctx.t("highest navigable water level", "höchster Schifffahrtswasserstand")
        c.text(x0, hy - 18, _ell(c, lab, "it700", 12, cw), "it700", 12, K)
    if v.get("mw") is not None:
        my = Yv(v["mw"])
        c.dashed((x0, my, X1, my), K, 1, 5, 4)
        c.text(x0, my + 6, _ell(c, f"MW {v['mw_text']} · {v['mw_label']}", "it700", 12, cw), "it700", 12, K)
    if len(v["x"]) >= 2:
        pts = [(x0 + cw * xx, Yv(val)) for xx, val in zip(v["x"], vals)]
        c.stroke(pts, K, 3)
    c.rect((x0, cb - 2, X1, cb), fill=K)
    for tk in v["day_ticks"]:
        tx = x0 + cw * tk["x"]
        c.vline(tx, cb, cb + 3, K, 1)
        w_ = c.tw(tk["weekday"], "it500", 11)
        c.text(min(max(tx - w_ / 2 + cw / max(1, v["days"]) / 2, x0), X1 - w_), ly, tk["weekday"], "it500", 11, K)
    return c.finish()


# ================================================================== birthdays
def _in_days(c, x1, y, text, n, size):
    """Right-aligned 'in 4 days' with the number in it900. Returns the width used."""
    i = text.find(n) if n else -1
    if i < 0:
        c.text(x1, y, text, "it500", size, K, align="r")
        return c.tw(text, "it500", size)
    parts = [(text[:i], "it500"), (n, "it900"), (text[i + len(n):], "it500")]
    tot = sum(c.tw(p, f, size) for p, f in parts)
    xx = x1 - tot
    for p, f in parts:
        c.text(xx, y, p, f, size, K)
        xx += c.tw(p, f, size)
    return tot


def birthdays(ctx, v):
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"]), v["subtitle"])
    festive = v["festive"]
    others = [p for p in v["people"] if p["days"] > 0] if festive else v["others"]
    # rows at the bottom
    L18 = c.line_h("it500", 18)
    rh = 1 + 5 + L18 + 5
    show = others[:4] if not festive else others[:3]
    rt = BOT - len(show) * rh
    y = rt
    for p in show:
        c.hline(X0, X1, y, K, 1)
        ty = y + 6
        tot = _in_days(c, X1, ty, p["when"], str(p["days"]), 18)
        c.text(X0, ty, _ell(c, p["name"], "it700", 18, _w(2)), "it700", 18, K)
        c.text(_sx(3), ty, _ell(c, p["date_short"], "it500", 18, _w(1)), "it500", 18, K)
        c.text(_sx(4), ty, _ell(c, p["age_text"] or "–", "it500", 18, min(_w(1), X1 - tot - 16 - _sx(4))), "it500",
               18, K)
        y += rh
    rb = rt - 14
    lw = _w(2)
    x = _sx(3)
    rw = X1 - x
    if festive:
        cel = v["celebrants"]
        top_lab = ctx.t("Today", "Heute")
        age = cel[0]["age"] if len(cel) == 1 and cel[0]["age"] else None
        big = str(age) if age else ""
        bottom_lab = ctx.t("years", "Jahre") if age else ""
        name = v["festive_names"]
        line = v["festive_line"] if not age else ""
        sub = v["festive_title"]
    else:
        p = v["first"]
        n = str(p["days"])
        i = p["when"].find(n)
        if i >= 0:
            top_lab, big, bottom_lab = p["when"][:i].strip(), n, p["when"][i + len(n):].strip()
        else:
            top_lab, big, bottom_lab = "", p["when"], ""
        name, line, sub = p["name"], p["age_text"], p["date_long"]
    # left column: "in" / big / "days"
    if top_lab:
        t, s = _fitline(c, top_lab, "it700", 22, lw, 12)
        c.text(X0, top, t, "it700", s, K)
    L30 = c.line_h("it700", 30, 1)
    if bottom_lab:
        t, s = _fitline(c, bottom_lab, "it700", 30, lw, 14)
        c.text(X0, rb - L30, t, "it700", s, K, lh=L30 / s)
    if big:
        s, tr = _shrink(c, big, "it900", 190, lw, -10, 30)
        if big.isdigit() or s >= 80:
            bh = s * 0.76
            c.text(X0, top + (rb - top - bh) / 2, big, "it900", s, R if festive else K, track=tr, lh=0.76)
        else:
            size, lines, L, tr2 = c.fit(big, "it900", 80, lw, rb - top - 80, lh=0.9, track=-4, min_size=24)
            c.para(X0, top + (rb - top - len(lines) * L) / 2, lw, lines, "it900", size, L, K, tr2)
    elif festive:
        c.rect((X0, top + 40, X0 + 120, top + 160), fill=R)
    # right column: name + square, rule, age line, date
    L20 = c.line_h("it500", 20)
    bot_h = (c.line_h("it700", 40, 1.05) if line else 0) + 2 + L20
    rule_y = rb - bot_h - 6 - 1
    c.hline(x, X1, rule_y, K, 1)
    yy = rule_y + 7
    if line:
        t, s = _fitline(c, line, "it700", 40, rw, 16)
        L40 = c.line_h("it700", 40, 1.05)
        c.text(x, yy, t, "it700", s, K, track=-1 * s / 40, lh=L40 / s)
        yy += L40 + 2
    t, s = _fitline(c, sub, "it500", 20, rw, 12)
    c.text(x, yy, t, "it500", s, K, lh=L20 / s)
    avail = rule_y - 12 - top
    s, tr = _shrink(c, name, "it900", 120, rw - 34, -6, 40)
    if c.tw(name, "it900", s, tr) - tr <= rw - 34:
        c.text(x, top, name, "it900", s, K, track=tr, lh=0.78)
        qx = x + c.tw(name, "it900", s, tr) - tr + 14
    else:
        size, lines, L, tr2 = c.fit(name, "it900", 60, rw - 34, avail, lh=0.9, track=-3, min_size=20)
        maxl = max(1, int(avail // L))
        if len(lines) > maxl:
            lines = lines[:maxl]
            lines[-1] = _ell(c, lines[-1] + "…", "it900", size, rw - 34, tr2)
        c.para(x, top, rw - 34, lines, "it900", size, L, K, tr2)
        qx = x + max(c.tw(l_, "it900", size, tr2) - tr2 for l_ in lines) + 14
    c.rect((qx, top + 4, qx + 20, top + 24), fill=R)
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    from ..plugins.watchlist import spark_points
    c = Canvas("swiss", Wh)
    top = _head(c, v["title"], _today_line(ctx, v["today"], v["now_text"]),
                ctx.t("{n} days", "{n} Tage", n=v["days"]))
    top -= 4           # row-gap 10 instead of 14
    # footer: 2 px rule, legend left, source right
    L13 = c.line_h("it500", 13)
    fy = BOT - L13 - 6 - 2
    c.rect((X0, fy, X1, fy + 2), fill=K)
    src = v["footer"]
    sw = min(c.tw(src, "it500", 13), 736 * 0.5)
    c.text(X1, fy + 8, _ell(c, src, "it500", 13, sw), "it500", 13, K, align="r")
    c.rect((X0, fy + 8 + L13 / 2 - 6, X0 + 12, fy + 8 + L13 / 2 + 6), fill=R)
    leg = ctx.t("Last close · line = {n} days, tick = start value",
                "Letzter Schlusskurs · Linie = {n} Tage, Strich = Startwert", n=v["days"])
    c.text(X0 + 20, fy + 8, _ell(c, leg, "it500", 13, 736 - 20 - sw - 16), "it500", 13, K)
    items = v["items"][:6]
    n = max(1, len(items))
    rb = fy - 10
    rh = (rb - top) / n
    k = min(1.0, rh / 86)
    s_name, s_chg, s_val = max(12, round(24 * k)), max(11, round(17 * k)), max(20, round(46 * k))
    for i, it in enumerate(items):
        y0 = top + i * rh
        c.hline(X0, X1, y0, K, 1)
        cy = y0 + 1 + (rh - 1) / 2
        col = COL.get(it.get("color", "black"), K)
        Ln = c.line_h("it700", s_name, 1.05)
        Lc = c.line_h("it700", s_chg)
        ty = cy - (Ln + 2 + Lc) / 2
        c.text(X0, ty, _ell(c, it["label"], "it700", s_name, _w(2)), "it700", s_name, K, lh=1.05)
        if it["ok"]:
            arrow = "▲" if it["direction"] == "up" else "▼" if it["direction"] == "down" else "■"
            c.text(X0, ty + Ln + 2, _ell(c, f"{arrow} {it['change_text']}", "it700", s_chg, _w(2)), "it700", s_chg,
                   col)
            val = it["last_text"]
            vs, vtr = _shrink(c, val, "it900", s_val, _w(2), -2 * s_val / 46, 14)
            c.text(_sx(5) - 16, cy - vs / 2, val, "it900", vs, K, track=vtr, lh=1, align="r")
            # sparkline (234 × 56, scaled with the row)
            sh = min(56, rh - 10)
            sx0, sy0 = _sx(5), cy - sh / 2
            pts = spark_points(it["values"], sx0, sy0 + 6 * sh / 56, 226, sh - 12 * sh / 56)
            if pts:
                lo, hi = it["min"], it["max"]
                by = pts[0][1]
                c.hline(sx0, sx0 + 234, by, K, 1)
                c.stroke(pts, col, 2.5)
                ex, ey = pts[-1]
                c.rect((ex + 2, ey - 3, ex + 8, ey + 3), fill=col)
        else:
            err = it.get("error") or "–"
            c.text(X0, ty + Ln + 2, _ell(c, err, "it500", s_chg, _w(2)), "it500", s_chg, K)
            c.text(_sx(5) - 16, cy - s_val / 2, "–", "it900", s_val, K, lh=1, align="r")
    return c.finish()
