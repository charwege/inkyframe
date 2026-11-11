"""Bauhaus signature layouts of the plugins (ports of mockups/project/Bauhaus-*.dc.html).

Archivo Black ("black"), Archivo 800 ("x800") and 600 ("x600") on paper (Wh) with the three primary
shapes – red circle, blue square, yellow triangle – and heavy black bars.
"""
import math

from ..designs import numeric_date
from ..studio import B, G, K, R, Y, Canvas, Wh

COL = {"green": G, "yellow": Y, "red": R, "black": K, "blue": B, "white": Wh}


# ================================================================== helpers
def _w(c, text, role, size, track=0.0):
    """Visible width of one line (without the trailing letter-spacing)."""
    return c.tw(text, role, size, track) - (track if text and track else 0)


def _shrink(c, text, role, size, maxw, track=0.0, mn=9):
    """(size, track) – largest size ≤ size whose line fits maxw (track scales with the size)."""
    s = size
    while s > mn and _w(c, text, role, s, track * s / size) > maxw:
        s -= 1
    return s, track * s / size


def _ell(c, text, role, size, maxw, track=0.0):
    if _w(c, text, role, size, track) <= maxw:
        return text
    while text and _w(c, text + "…", role, size, track) > maxw:
        text = text[:-1]
    return text.rstrip(" ·,-–") + "…"


def _line(c, x, top, text, role, size, maxw, fill=K, track=0.0, lh=None, align="l", upper=False, mn=9):
    """One line that shrinks to maxw (down to mn px), then ellipsizes. Returns the line height."""
    if upper:
        text = text.upper()
    s, tr = _shrink(c, text, role, size, maxw, track, mn)
    text = _ell(c, text, role, s, maxw, tr)
    yy = top + (c.line_h(role, size, lh) - c.line_h(role, s, lh)) / 2
    c.text(x, yy, text, role, s, fill, track=tr, lh=lh, align=align)
    return c.line_h(role, size, lh)


def _tag(c, x, top, text, size=14, track=4, fill=K, ink=Wh, maxw=None, align="l", padx=12, pady=6, role="x800"):
    """Filled label box (the mockups' black / blue <p> with padding). Returns (width, height)."""
    text = text.upper()
    s, tr = size, track
    if maxw is not None:
        s, tr = _shrink(c, text, role, size, maxw - 2 * padx, track, 8)
        text = _ell(c, text, role, s, maxw - 2 * padx, tr)
    w = _w(c, text, role, s, tr) + 2 * padx
    h = c.line_h(role, size) + 2 * pady
    x0 = x if align == "l" else x - w
    c.rect((x0, top, x0 + w, top + h), fill=fill)
    c.text(x0 + padx, top + pady + (c.line_h(role, size) - c.line_h(role, s)) / 2, text, role, s, ink, track=tr)
    return w, h


def _label(c, x, top, text, maxw=None, size=11, track=2, fill=K, align="l"):
    """Small spaced capitals (11px / 800 / letter-spacing 2px)."""
    if maxw is None:
        c.text(x, top, text, "x800", size, fill, track=track, align=align, upper=True)
        return c.line_h("x800", size)
    return _line(c, x, top, text, "x800", size, maxw, fill, track, align=align, upper=True, mn=9)


def _shapes(c, x, top, s=14):
    """The three primary shapes in a row (circle, square, triangle) starting at x."""
    c.circle(x + s / 2, top + s / 2, s / 2, fill=R)
    c.rect((x + s + 6, top, x + 2 * s + 6, top + s), fill=B)
    tx = x + 2 * s + 12
    c.poly([(tx, top + s), (tx + s + 2, top + s), (tx + s / 2 + 1, top)], fill=Y)
    return 3 * s + 14


def _tri(c, x, top, w, h, fill, down=False):
    if down:
        c.poly([(x, top), (x + w, top), (x + w / 2, top + h)], fill=fill)
    else:
        c.poly([(x, top + h), (x + w, top + h), (x + w / 2, top)], fill=fill)


def _rich(c, x, top, words, role, size, L, track, maxw):
    """Wrapped words of (text, colour) pairs; returns the number of lines drawn."""
    sp = c.tw(" ", role, size, track)
    lines, cur, cw = [], [], 0
    for t, col in words:
        w = _w(c, t, role, size, track)
        if cur and cw + sp + w > maxw:
            lines.append(cur)
            cur, cw = [], 0
        cw += (sp if cur else 0) + w
        cur.append((t, col, w))
    if cur:
        lines.append(cur)
    y = top
    for ln in lines:
        xx = x
        for t, col, w in ln:
            c.text(xx, y, t, role, size, col, track=track, lh=L / size)
            xx += w + track + sp
        y += L
    return len(lines)


def _rich_fit(c, words, role, size, maxw, maxh, lh, track, mn=14):
    """Largest size whose wrapped (text, colour) words fit maxw × maxh. Returns (size, track, L, n lines)."""
    s = size
    while True:
        tr = track * s / size
        sp = c.tw(" ", role, s, tr)
        n, cw, ok = 1, 0, True
        for t, _ in words:
            w = _w(c, t, role, s, tr)
            if w > maxw:
                ok = False
            if cw and cw + sp + w > maxw:
                n += 1
                cw = w
            else:
                cw += (sp if cw else 0) + w
        L = s * lh
        if (ok and n * L <= maxh + 0.5) or s <= mn:
            return s, tr, L, n
        s -= 1


def _clip_words(c, words, role, size, track, maxw, maxlines):
    """Cut a (text, colour) word list so it wraps into at most maxlines lines (ellipsis on the last)."""
    sp = c.tw(" ", role, size, track)
    n, cw, out = 1, 0, []
    for t, col in words:
        w = _w(c, t, role, size, track)
        if cw and cw + sp + w > maxw:
            n += 1
            cw = 0
        if n > maxlines:
            if out:
                last, lc = out[-1]
                out[-1] = (last.rstrip(",.;:") + "…", lc)
            break
        if w > maxw:
            t = _ell(c, t, role, size, maxw, track)
            w = _w(c, t, role, size, track)
        cw += (sp if cw else 0) + w
        out.append((t, col))
    return out


def _ctext(c, cx, cy, text, role, size, fill=K, track=0.0):
    """Text whose line box is centred on (cx, cy)."""
    c.text(cx, cy - c.line_h(role, size) / 2, text, role, size, fill, track=track, align="c")


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = Canvas("bauhaus", Wh)
    c.circle(780, 20, 75, fill=R)
    _tri(c, 704, 196, 68, 58, Y)

    # board: left 20 / top 16, rank column 12 + gap 6, border 6, squares 52
    S, bx, by = 52, 44, 22
    c.rect((38, 16, 38 + 8 * S + 12, 16 + 8 * S + 12), fill=K)
    last = {tuple(rc) for rc in (v.get("last_cells") or [])}
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            x, y = bx + col * S, by + r * S
            fill = R if (r, col) in last else (Y if (r + col) % 2 else Wh)
            c.rect((x, y, x + S, y + S), fill=fill)
            chess_puzzle.draw_piece(c.d, p, x + S // 2, y + S // 2, S, ink=K, paper=Wh)
    if v.get("show_coords", True):
        for i, rk in enumerate(v["ranks"]):
            c.text(20, by + i * S + S / 2 - c.line_h("x800", 11) / 2, rk, "x800", 11)
        for i, f in enumerate(v["files"]):
            c.text(bx + i * S + S / 2, 460, f.upper(), "x800", 11, align="c")

    # right column: left 488, top 30, width 290, height 420, gap 16
    X, Wd, y = 488, 290, 30
    _, h = _tag(c, X, y, v["title"], maxw=Wd)
    y += h + 16
    black = not v.get("white_to_move", False)
    c.circle(X + 13, y + 15, 13, fill=K if black else Wh, outline=K, width=3)
    L = _line(c, X + 38, y, v["to_move"], "black", 30, Wd - 38, K, -0.5, lh=1, upper=True, mn=14)
    y += max(L, 26) + 16
    big = v.get("mate") or (v["themes"][0] if v.get("themes") else "") or v.get("title_b", "")
    size, lines, L, tr = c.fit(big, "black", 66, Wd, 2 * 66 * 0.9, lh=0.9, track=-2, min_size=26, upper=True)
    lines = lines[:2]
    c.para(X, y, Wd, lines, "black", size, L, R, tr)
    y += len(lines) * L + 16
    rest = [t for t in v.get("themes", []) if t != v.get("mate")]
    if rest:
        y += _line(c, X, y, " · ".join(rest), "x800", 12, Wd, K, 1, upper=True, mn=9) + 16
    # two-cell grid with a 4px top rule
    c.rect((X, y, X + Wd, y + 4), fill=K)
    top = y + 4
    lab_h, val_h = c.line_h("x800", 11), c.line_h("black", 24)
    cell_h = 10 + lab_h + 2 + val_h
    c.vline(X + Wd / 2 - 2, top, top + cell_h, K, 2)
    cells = ((ctx.t("Rating", "Wertung"), str(v["rating"]) if v.get("rating") else "–"),
             (ctx.t("Solution", "Lösung"),
              ctx.t("{n} moves", "{n} Züge", n=v["moves"]) if v.get("moves", 0) != 1 else ctx.t("1 move", "1 Zug")))
    for i, (lab, val) in enumerate(cells):
        x = X + (Wd / 2 + 12 if i else 0)
        cw = Wd / 2 - 14
        _label(c, x, top + 10, lab, maxw=cw)
        _line(c, x, top + 10 + lab_h + 2, val, "black", 24, cw, upper=True, mn=12)
    y = top + cell_h + 16
    if v.get("last_text"):
        lh = c.line_h("x800", 13)
        c.rect((X, y + lh / 2 - 8, X + 16, y + lh / 2 + 8), fill=R)
        _line(c, X + 26, y, ctx.t("Last move", "Letzter Zug") + " " + v["last_text"], "x800", 13, Wd - 26, K, 2,
              upper=True)
    hint_h = c.line_h("x800", 14) + 12
    _tag(c, X, 450 - hint_h, v["hint"], track=2, fill=B, maxw=Wd)
    return c.finish()


# ================================================================== spotify
def _cover_placeholder(c, x, y):
    c.rect((x, y, x + 420, y + 420), fill=Y)
    c.rect((x, y, x + 210, y + 210), fill=B)
    c.circle(x + 190, y + 190, 130, fill=R)
    c.rect((x + 210, y + 210, x + 420, y + 420), fill=K)
    c.poly([(x + 230, y + 380), (x + 400, y + 380), (x + 315, y + 230)], fill=Wh)
    c.circle(x + 44, y + 376, 20, fill=K)
    c.rect((x + 406, y, x + 420, y + 210), fill=K)


def spotify(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 480, 480), fill=K)
    if v.get("image") is not None:
        c.img.paste(ctx.punch(ctx.cover_fit(v["image"], 420, 420)), (30, 30))
    else:
        _cover_placeholder(c, 30, 30)

    X0, X1, top, bot = 510, 770, 32, 452
    Wd = X1 - X0
    sw = 3 * 14 + 14
    _, th = _tag(c, X0, top, v["label"], maxw=Wd - sw - 10)
    _shapes(c, X1 - sw, top + 6)
    y = top + th + 16

    # bottom block first (footer + bar), then fit the title into what is left
    foot_h = c.line_h("x800", 13)
    foot_top = bot - foot_h - 10 - 4
    c.rect((X0, foot_top, X1, foot_top + 4), fill=K)
    _label(c, X0, foot_top + 14, v.get("source") or "Spotify", maxw=Wd / 2, size=13, track=4)
    c.text(X1, foot_top + 14, v.get("time", ""), "x800", 13, track=2, align="r")
    dur_h = c.line_h("black", 16)
    bar_top = foot_top - 16 - dur_h - 6 - 12
    c.rect((X0, bar_top, X1, bar_top + 12), fill=K)
    c.rect((X1 - 15, bar_top + 3, X1 - 3, bar_top + 9), fill=R)
    if v.get("duration_text"):
        c.text(X1, bar_top + 18, v["duration_text"], "black", 16, align="r")
    if v.get("playing"):
        _tri_play = [(X0, bar_top + 20), (X0, bar_top + 34), (X0 + 12, bar_top + 27)]
        c.poly(_tri_play, fill=R)

    blocks = [(ctx.t("Artist", "Interpret"), v.get("artist", ""), "x800", 20),
              (ctx.t("Album", "Album"), v.get("album", ""), "x600", 18)]
    blocks = [b for b in blocks if b[1]]
    lab_h = c.line_h("x800", 11)
    blocks_h = sum(lab_h + 4 + c.line_h(r, s) + 16 for _, _, r, s in blocks)
    room = bar_top - 16 - blocks_h - y
    words = v["track"].upper().split()
    cut = next((i for i, w in enumerate(words) if i and w[:1] in "([-–"), None)
    words = [(w, R if cut is not None and i >= cut and w not in ("-", "–") else K) for i, w in enumerate(words)]
    size, tr, L, n = _rich_fit(c, words, "black", 30, Wd, room, 1.05, -0.5, mn=16)
    maxl = max(1, int((room + 0.5) // L))
    words = _clip_words(c, words, "black", size, tr, Wd, maxl)
    n = _rich(c, X0, y, words, "black", size, L, tr, Wd)
    y += n * L + 16
    for lab, val, role, s in blocks:
        _label(c, X0, y, lab, maxw=Wd)
        y += lab_h + 4
        y += _line(c, X0, y, val, role, s, Wd, mn=12) + 16
    return c.finish()


# ================================================================== grid (Stromampel)
def grid(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 18, 480), fill=K)
    c.rect((50, 30, 170, 310), fill=K)
    for (cy, lamp) in zip((75, 165, 260), v["lights"]):
        col = COL.get(lamp["color"], Wh)
        if lamp["on"]:
            c.circle(110, cy, 37, fill=col)
        else:
            c.circle(110, cy, 32, outline=col, width=5)

    X, Wd = 204, 560
    y = 30
    tw_, th = _tag(c, X, y, v["title"], maxw=Wd * 0.55)
    where = " · ".join(t for t in (v.get("place") or v.get("country", ""), v.get("time", "")) if t)
    _line(c, X + Wd, y + 6, where, "x800", 14, Wd - tw_ - 16, K, 4, align="r", upper=True)
    y += th + 12
    name = v.get("signal_name") or "–"
    head, _, extra = name.partition(" · ")
    col = COL.get(v.get("color") or "", K)
    s, tr = _shrink(c, head.upper(), "black", 120, Wd, -4, 40)
    big_L = 120 * 0.9
    c.text(X, y + (big_L - s * 0.9), head, "black", s, col, track=tr, lh=0.9, upper=True)
    y += big_L + 12
    if v.get("share_text"):
        y += _line(c, X, y, ctx.t("{p} renewable energy", "{p} Ökostrom", p=v["share_text"]), "black", 28, Wd,
                   upper=True, mn=14) + 12
    sig = v.get("signal")
    if extra:
        adv = extra
    elif sig == 2:
        adv = ctx.t("Now: wash, charge, run the dishwasher", "Jetzt waschen, laden, spülen")
    elif sig == 1:
        adv = ctx.t("Use power sparingly", "Strom sparsam nutzen")
    elif sig is not None:
        adv = ctx.t("Shift your consumption", "Verbrauch verschieben")
    else:
        adv = ""
    if adv:
        _tag(c, X, y, adv, size=17, track=2, fill=B, maxw=Wd)

    # 24 h band
    X0, X1 = 50, 770
    top = 334
    lab = ctx.t("Today · 24 hours", "Heute · 24 Stunden")
    lw = _w(c, lab.upper(), "x800", 11, 2)
    _label(c, X0, top, lab, maxw=300)
    best = v.get("best")
    if v.get("best_text"):
        bc = K
        if best:
            hrs = v.get("hours") or []
            hi = int(best["start"]) % 24
            if best.get("day") == "today" and hi < len(hrs) and hrs[hi].get("color"):
                bc = COL.get(hrs[hi]["color"], K)
        room = X1 - X0 - min(lw, 300) - 30
        tw2 = min(room - 18, _w(c, v["best_text"].upper(), "x800", 11, 1))
        _line(c, X1, top, v["best_text"], "x800", 11, room - 18, K, 1, align="r", upper=True, mn=8)
        lhh = c.line_h("x800", 11)
        c.rect((X1 - tw2 - 18, top + lhh / 2 - 6, X1 - tw2 - 6, top + lhh / 2 + 6), fill=bc, outline=K)
    btop = top + c.line_h("x800", 11) + 6
    c.rect((X0, btop + 14, X1, btop + 54), fill=K)
    ix0, ix1 = X0 + 4, X1 - 4
    cw = (ix1 - ix0) / 24
    for i, hr in enumerate(v["hours"][:24]):
        x0 = ix0 + i * cw
        x1 = ix0 + (i + 1) * cw - (2 if i < 23 else 0)
        c.rect((x0, btop + 18, x1, btop + 50), fill=COL.get(hr.get("color") or "", Wh))
        if i < 23:
            c.rect((x1, btop + 18, x1 + 2, btop + 50), fill=Wh)
    nx = ix0 + v.get("now_pos", 0) * (ix1 - ix0)
    _tri(c, nx - 9, btop, 18, 14, K, down=True)
    c.rect((nx - 2, btop + 14, nx + 2, btop + 62), fill=K)
    nl = v.get("now_label", "").upper()
    if nx + 12 + _w(c, nl, "x800", 11, 1) < X1:
        c.text(nx + 12, btop, nl, "x800", 11, track=1)
    else:
        c.text(nx - 12, btop, nl, "x800", 11, track=1, align="r")
    ty = btop + 70 + 6
    for i, t in enumerate(("00", "06", "12", "18", "24")):
        x = X0 + (X1 - X0) * i / 4
        c.text(x, ty, t, "x800", 11, align="l" if i == 0 else "r" if i == 4 else "c")
    if v.get("source"):
        _line(c, (X0 + X1) / 2, 462, v["source"], "x600", 10, 400, K, 0.5, align="c")
    return c.finish()


# ================================================================== wordclock
def wordclock(ctx, v):
    from ..designs import moon_disc
    c = Canvas("bauhaus", Wh)
    # left column 24…166
    LX, LW = 24, 142
    c.circle(24, 400, 60, fill=Y)
    y = 20
    _, h = _tag(c, LX, y, v["weekday"], padx=10, maxw=LW, fill=R if v.get("special") else K)
    y += h + 10
    c.text(LX, y, str(v["day"]), "black", 96, K, track=-4, lh=0.9)
    y += 96 * 0.9 + 10
    y += _line(c, LX, y, v["month"], "black", 20, LW, K, 1, upper=True, mn=10) + 10
    c.text(LX, y, str(v["year"]), "x600", 14, K, track=4)

    # letter grid on black 190…610 × 20…460
    c.rect((190, 20, 610, 460), fill=K)
    rows, cols = v.get("rows") or len(v["grid"]), v.get("cols") or len(v["grid"][0])
    cw, ch = min(36, 396 / cols), min(40, 400 / rows)
    gx, gy = 400 - cw * cols / 2, 240 - ch * rows / 2
    lit = {tuple(rc) for rc in v.get("lit", [])}
    fs = round(25 * min(cw / 36, ch / 40))
    for r, line in enumerate(v["grid"]):
        for col, ch_ in enumerate(line):
            on = (r, col) in lit
            _ctext(c, gx + col * cw + cw / 2, gy + r * ch + ch / 2, ch_, "black", fs, Y if on else B)

    # right column 634…776, centred at 705
    cx = 705
    dy = 26 + 55
    c.circle(cx, dy, 54, fill=K)
    c.circle(cx, dy, 48, fill=Wh)
    c.rect((cx - 3, dy - 47, cx + 3, dy - 35), fill=K)
    c.rect((cx + 35, dy - 3, cx + 47, dy + 3), fill=K)
    c.rect((cx - 3, dy + 35, cx + 3, dy + 47), fill=K)
    c.rect((cx - 47, dy - 3, cx - 35, dy + 3), fill=K)
    hh, mm = v["hour"] % 12, v["minute"]
    ha = math.radians((hh + mm / 60) * 30)
    ma = math.radians(mm * 6)
    c.d.line((cx, dy, cx + 25 * math.sin(ha), dy - 25 * math.cos(ha)), fill=K, width=7)
    c.d.line((cx, dy, cx + 40 * math.sin(ma), dy - 40 * math.cos(ma)), fill=R, width=4)
    c.circle(cx, dy, 6, fill=R)
    y = 26 + 110 + 12
    extra = v["now"].minute % 5 if v.get("now") else 0
    for i in range(4):
        x = cx - 39 + i * 20
        if i < extra:
            c.rect((x, y, x + 14, y + 14), fill=R)
        else:
            c.rect((x, y, x + 14, y + 14), outline=K, width=3)
    y += 20
    if extra == 1:
        lab = ctx.t("+1 minute", "+1 Minute")
    elif extra:
        lab = ctx.t("+{n} minutes", "+{n} Minuten", n=extra)
    else:
        lab = v.get("time", "")
    _label(c, cx, y, lab, maxw=142, align="c")
    # bottom up: triangle, moon text, moon disc
    _tri(c, cx - 14, 436, 28, 24, B)
    mL = c.line_h("x800", 16)
    ty = 436 - 12 - mL - 2 - c.line_h("x800", 11)
    _label(c, cx, ty, ctx.t("Moon", "Mond"), maxw=142, align="c")
    _line(c, cx, ty + c.line_h("x800", 11) + 2, v.get("moon", ""), "x800", 16, 142, align="c", mn=9)
    moon_disc(c, cx, ty - 12 - 27, 25, v.get("phase", 0), Wh, K, K)
    c.circle(cx, ty - 12 - 27, 27, outline=K, width=3)
    return c.finish()


# ================================================================== countdown
def countdown(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.circle(200, 210, 170, fill=Y)
    c.rect((690, 0, 800, 110), fill=B)
    c.rect((0, 0, 18, 480), fill=K)
    tw_, th = _tag(c, 50, 30, v["title"], maxw=300)
    today = numeric_date(v["today"], ctx.lang).replace(".", " · ").replace("/", " · ").replace("-", " · ")
    c.text(50 + tw_ + 14, 30 + 6, today, "x800", 14, K, track=4)

    accent = COL.get(v.get("color") or "", R)
    big = v["big"].upper()
    s, tr = _shrink(c, big, "black", 250, 340, -12, 40)
    L = c.line_h("black", s, 1)
    c.text(44, 70 + (250 - L) / 2, big, "black", s, K, track=tr, lh=1)

    X, Wd = 400, 360
    y = 136
    if v.get("small"):
        size, lines, L, tr = c.fit(v["small"], "black", 64, Wd, 2 * 64 * 0.9, lh=0.9, track=-2, min_size=28,
                                   upper=True)
        lines = lines[:2]
        c.para(X, y, Wd, lines, "black", size, L, accent, tr)
        y += len(lines) * L + 14
    if v.get("event"):
        room = 384 - 20 - 14 - (c.line_h("x800", 15) + 12) - y
        size, lines, L, tr = c.fit(v["event"], "black", 25, Wd, max(room, 30), lh=1.05, min_size=14, upper=True)
        maxl = max(1, int(room // L))
        if len(lines) > maxl:
            lines = lines[:maxl]
            lines[-1] = _ell(c, lines[-1] + "…", "black", size, Wd, tr)
        c.para(X, y, Wd, lines, "black", size, L, K, tr)
        y += len(lines) * L + 14
    when = f"{v['target_weekday']}, {v['date']}" if v.get("target_weekday") else v["date"]
    _tag(c, X, y, when, size=15, track=2, fill=B, maxw=Wd)

    # day strip 50…770 at 384
    X0, X1, top = 50, 770, 384
    strip = v.get("strip") or []
    n = len(strip)
    if n:
        gap = 2 if n <= 120 else 0
        cw = (X1 - X0 - gap * (n - 1)) / n
        for i, d in enumerate(strip):
            x0 = X0 + i * (cw + gap)
            x1 = x0 + cw
            box = (round(x0), top, max(round(x0) + 1, round(x1)), top + 26)
            if d["today"]:
                c.rect(box, fill=R)
            elif d["target"]:
                c.rect(box, fill=B)
            elif d["weekend"] or d["special"]:
                c.rect(box, fill=Y)
            elif cw >= 6:
                c.rect(box, fill=Wh, outline=K, width=2)
            else:
                c.rect(box, fill=K)
    c.rect((X0, top + 30, X1, top + 34), fill=K)
    ly = top + 40
    t_lab = ctx.t("Today", "Heute") + " " + v.get("today_short", "")
    e_lab = (v.get("event") or ctx.t("Target", "Ziel"))
    e_short = v.get("date_short", "")
    if v.get("state") == "past":
        left, right, lcol, rcol = (e_lab, e_short), (t_lab, ""), B, R
    else:
        left, right, lcol, rcol = (t_lab, ""), (e_lab, e_short), R, B
    half = (X1 - X0) * 0.4
    for (txt, tail), col, al, x in ((left, lcol, "l", X0), (right, rcol, "r", X1)):
        full = f"{txt} {tail}".strip().upper()
        if _w(c, full, "x800", 11, 2) > half and tail:
            full = _ell(c, txt.upper(), "x800", 11, half - _w(c, " " + tail, "x800", 11, 2), 2) + " " + tail
        _line(c, x, ly, full, "x800", 11, half, col, 2, align=al, mn=8)
    if v.get("target") and v["target"].month != v["today"].month or v.get("target") and v["target"].year != v["today"].year:
        from ..plugins import _calendar
        mid = _calendar.month(max(v["target"], v["today"]), ctx.lang)
        _line(c, (X0 + X1) / 2, ly, mid, "x800", 11, (X1 - X0) * 0.18, K, 2, align="c", upper=True, mn=8)
    return c.finish()


# ================================================================== art
def art(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 510, 480), fill=K)
    img = v["image"]
    sc = min(458 / img.width, 428 / img.height)
    w, h = max(1, round(img.width * sc)), max(1, round(img.height * sc))
    fx, fy = 255 - w // 2 - 6, 240 - h // 2 - 6
    c.rect((fx, fy, fx + w + 12, fy + h + 12), fill=Wh)
    c.img.paste(img.convert("RGB").resize((w, h)), (fx + 6, fy + 6))
    if v.get("license"):
        lab = v["license"].upper()
        s, tr = _shrink(c, lab, "x800", 11, w - 20, 2, 8)
        lw = _w(c, lab, "x800", s, tr) + 16
        lh = c.line_h("x800", 11) + 8
        bx, by = fx + 6 + w - lw, fy + 6 + h - lh
        c.rect((bx, by, bx + lw, by + lh), fill=Wh)
        c.text(bx + 8, by + 4, _ell(c, lab, "x800", s, w - 20, tr), "x800", s, K, track=tr)

    X0, X1, top, bot = 536, 774, 30, 454
    Wd = X1 - X0
    y = top
    _, th = _tag(c, X0, y, v["title"], size=12, track=2, padx=10, maxw=Wd)
    y += th + 18
    # bottom row first
    sh = 22
    c.circle(X1 - 74 + 11, bot - 11, 11, fill=R)
    c.rect((X1 - 46, bot - 22, X1 - 24, bot), fill=B)
    c.poly([(X1 - 24 + 0, bot), (X1, bot), (X1 - 12, bot - 22)], fill=Y)
    if v.get("museum_city"):
        _line(c, X0, bot - c.line_h("x800", 13), v["museum_city"], "x800", 13, Wd - 84, K, 4, upper=True)
    lab_h = c.line_h("x800", 11)
    # info grid height (year | museum)
    mus_lines = c.wrap(v.get("museum", ""), "x800", 15, Wd - 92 if v.get("date") else Wd)[:3]
    grid_h = 4 + 10 + lab_h + 2 + max(c.line_h("black", 22) if v.get("date") else 0, len(mus_lines) * 15 * 1.15)
    art_h = (lab_h + 4 + 19 * 1.15 + 18) if v.get("artist") else 0
    room = bot - sh - 18 - grid_h - 18 - art_h - y
    words = v["work"].upper().split()
    words = [(wd, R if i == len(words) - 1 and len(words) > 1 else K) for i, wd in enumerate(words)]
    size, tr, L, n = _rich_fit(c, words, "black", 34, Wd, room, 1.0, -0.5, mn=16)
    words = _clip_words(c, words, "black", size, tr, Wd, max(1, int((room + 0.5) // L)))
    n = _rich(c, X0, y, words, "black", size, L, tr, Wd)
    y += n * L + 18
    if v.get("artist"):
        _label(c, X0, y, ctx.t("Artist", "Künstler"), maxw=Wd)
        y += lab_h + 4
        y += _line(c, X0, y, v["artist"], "x800", 19, Wd, lh=1.15, mn=11) + 18
    c.rect((X0, y, X1, y + 4), fill=K)
    gt = y + 4
    mx = X0
    if v.get("date"):
        c.vline(X0 + 78, gt, gt + grid_h - 4, K, 2)
        _label(c, X0, gt + 10, ctx.t("Year", "Jahr"), maxw=68)
        _line(c, X0, gt + 10 + lab_h + 2, v["date"], "black", 22, 68, mn=10)
        mx = X0 + 92
    _label(c, mx, gt + 10, ctx.t("Museum", "Museum"), maxw=X1 - mx)
    my = gt + 10 + lab_h + 2
    for ln in mus_lines:
        _line(c, mx, my, ln, "x800", 15, X1 - mx, lh=1.15, mn=9)
        my += 15 * 1.15
    y = gt + grid_h + 10
    extra = " · ".join(t for t in (v.get("medium", ""), v.get("dimensions", "")) if t)
    if extra and y + 30 < bot - sh - 8:
        for ln in c.wrap(extra, "x600", 12, Wd)[:max(0, int((bot - sh - 8 - y) // 15))][:2]:
            _line(c, X0, y, ln, "x600", 12, Wd, lh=1.2)
            y += 14.4
    return c.finish()


# ================================================================== waste
def _big_bin(c, x, y, s, color, bg=K):
    """The mockup's 110×150 bin (lid handle, lid, tapered body, two slots), scaled by s."""
    def P(px, py):
        return x + px * s, y + py * s
    col = COL.get(color, Wh)
    if col == bg:       # a black bin on the black panel: paper outline, black inside
        c.rect((*P(40, 0), *P(70, 10)), fill=Wh)
        c.rect((*P(4, 12), *P(106, 28)), fill=Wh)
        c.poly([P(12, 34), P(98, 34), P(90, 150), P(20, 150)], fill=Wh)
        c.poly([P(20, 42), P(90, 42), P(83, 142), P(27, 142)], fill=K)
        slot = Wh
        c.rect((*P(34, 56), *P(42, 126)), fill=slot)
        c.rect((*P(68, 56), *P(76, 126)), fill=slot)
        return
    c.rect((*P(40, 0), *P(70, 10)), fill=col)
    c.rect((*P(4, 12), *P(106, 28)), fill=col)
    c.poly([P(12, 34), P(98, 34), P(90, 150), P(20, 150)], fill=col)
    slot = K if col in (Y, Wh) else Wh
    c.rect((*P(34, 52), *P(42, 130)), fill=slot)
    c.rect((*P(68, 52), *P(76, 130)), fill=slot)


def waste(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 330, 480), fill=K)
    c.rect((246, 0, 330, 84), fill=R)
    _line(c, 28, 30, v["title"], "x800", 14, 210, Wh, 4, upper=True)
    soon = v.get("soon")
    rows = list(v.get("rows") or [])
    if soon:
        big, wd, ds, bins = soon["label"], soon["weekday"], soon["date_short"], soon["items"]
    else:
        first = rows[0]
        big, wd, ds = first["in_text"], first["weekday"], first["date_short"]
        bins = [r for r in rows if r["date"] == first["date"]]
        rows = [r for r in rows if r["date"] != first["date"]]
    _line(c, 26, 96, big, "black", 62, 290, Wh, -2, lh=1, upper=True, mn=24)
    _line(c, 28, 166, f"{wd} · {ds}", "x600", 16, 290, Wh, 4, upper=True)
    bins = bins[:4]
    n = len(bins)
    s = min(1.0, (274 - (n - 1) * 16) / (n * 110)) if n else 1
    gap = 28 if n <= 2 else 16
    x = 28
    for b in bins:
        bw = 110 * s
        _big_bin(c, x, 212, s, b.get("color", "black"))
        L = c.line_h("x800", 13)
        ny = 212 + 150 * s + 10
        lines = c.wrap(b["name"].upper(), "x800", 13, bw + gap - 4, 2)
        if len(lines) > 2:
            lines = lines[:2]
            lines[1] = _ell(c, lines[1] + "…", "x800", 13, bw + gap - 4, 2)
        for ln in lines:
            _line(c, x + bw / 2, ny, ln, "x800", 13, bw + gap - 4, Wh, 2, align="c", mn=8)
            ny += L
        x += bw + gap
    if soon and not soon.get("is_today"):
        _line(c, 28, 440, ctx.t("Put the bins out tonight", "Heute Abend rausstellen"), "x800", 12, 274, Y, 2,
              upper=True, mn=8)

    X0, X1, top, bot = 362, 768, 30, 454
    Wd = X1 - X0
    sx = X1 - (3 * 18 + 14 + 2)
    _shapes(c, sx, top, 18)
    _line(c, X0, top, v.get("place") or v.get("date_text", ""), "x800", 16, sx - X0 - 12, K, 5, upper=True)
    y = top + max(c.line_h("x800", 16), 18) + 14
    _label(c, X0, y, ctx.t("After that", "Danach"), maxw=Wd)
    y += c.line_h("x800", 11) + 8
    c.rect((X0, y, X1, y + 4), fill=K)
    y += 4
    if not rows:
        size, lines, L, tr = c.fit(v.get("empty_text", ""), "x800", 19, Wd, bot - y - 20, min_size=11)
        c.para(X0, y + 20, Wd, lines, "x800", size, L)
        return c.finish()
    nmax = 5
    rows = rows[:nmax]
    rh = min(100, (bot - y) / max(4, len(rows)))
    for r in rows:
        col = COL.get(r.get("color"), K)
        cy = y + rh / 2
        c.rect((X0, cy - 22, X0 + 34, cy - 15), fill=col, outline=K if col == Wh else None)
        c.rect((X0 + 3, cy - 12, X0 + 31, cy + 22), fill=col, outline=K if col == Wh else None)
        tx = X0 + 50
        lab_h, val_h = c.line_h("x800", 11), c.line_h("black", 20)
        ty = cy - (lab_h + val_h) / 2
        _label(c, tx, ty, r["weekday_short"], maxw=74)
        _line(c, tx, ty + lab_h, r["date_short"], "black", 20, 74, mn=11)
        inn = r["in_text"].upper()
        is_, itr = _shrink(c, inn, "x800", 14, 150, 1, 9)
        iw = _w(c, inn, "x800", is_, itr)
        c.text(X1, cy - c.line_h("x800", 14) / 2, inn, "x800", is_, K, track=itr, align="r")
        nx = tx + 74 + 16
        _line(c, nx, cy - c.line_h("x800", 19) / 2, r["name"], "x800", 19, X1 - iw - 16 - nx, mn=11)
        y += rh
        c.rect((X0, y - 2, X1, y), fill=K)
    return c.finish()


# ================================================================== warnings
def warnings(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 800, 64), fill=K)
    place = (v.get("place") or "").upper()
    pw = min(220, _w(c, place, "x800", 14, 4)) if place else 0
    if place:
        _line(c, 770, 32 - c.line_h("x800", 14) / 2, place, "x800", 14, 220, Wh, 4, align="r")
    _line(c, 30, 32 - c.line_h("black", 26) / 2, v["title"], "black", 26, 740 - pw - 20 - 30, Wh, 2, upper=True,
          mn=12)
    # triangle 260×230 at (30, 96)
    def T(px, py):
        return 30 + px, 96 + py
    c.poly([T(130, 0), T(260, 230), T(0, 230)], fill=Y)
    c.poly([T(130, 40), T(226, 210), T(34, 210)], fill=K)
    c.poly([T(130, 70), T(202, 196), T(58, 196)], fill=Y)
    c.rect((*T(119, 104), *T(141, 160)), fill=K)
    c.rect((*T(119, 168), *T(141, 188)), fill=K)
    y = 350
    lv, n = v.get("level", 1), v.get("levels", 4)
    y += _label(c, 30, y, ctx.t("Warning level {n} of {m}", "Warnstufe {n} von {m}", n=lv, m=n), maxw=260) + 8
    bw = (260 - 6 * (n - 1)) / n
    cols = [Y, R, R, K]
    for i in range(n):
        x = 30 + i * (bw + 6)
        if i < lv:
            c.rect((x, y, x + bw, y + 22), fill=cols[min(i, 3)])
        else:
            c.rect((x, y, x + bw, y + 22), outline=K, width=3)
    y += 22 + 8
    lines = c.wrap(v.get("level_text", ""), "x800", 17, 260)[:2]
    for ln in lines:
        y += _line(c, 30, y, ln, "x800", 17, 260, mn=10)

    X, Wd = 330, 440
    foot_top = 480 - 26 - 10 - c.line_h("x800", 11) - 2
    c.rect((X, foot_top, 770, foot_top + 2), fill=K)
    _label(c, X, foot_top + 12, v.get("footer") or v.get("source", ""), maxw=Wd - 70)
    _shapes(c, 770 - 56, foot_top + 12)
    y = 92
    size, lines, L, tr = c.fit(v["event"], "black", 60, Wd, 2 * 60 * 0.9, lh=0.9, track=-2, min_size=24, upper=True)
    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = _ell(c, lines[1] + "…", "black", size, Wd, tr)
    c.para(X, y, Wd, lines, "black", size, L, R, tr)
    y += len(lines) * L + 16
    span = " – ".join(t for t in (v.get("onset_text"), v.get("expires_text")) if t) or v.get("span", "")
    if span:
        _, th = _tag(c, X, y, span, size=17, track=2, fill=B, maxw=Wd)
        y += th + 16
    more = v.get("more_text", "")
    bottom = foot_top - 14 - (c.line_h("x800", 13) + 6 if more else 0)
    if more:
        _line(c, X, bottom + 2, more, "x800", 13, Wd, R, 1, upper=True, mn=9)
    c.rect((X, y, X + Wd, y + 4), fill=K)
    y += 4 + 14
    txt = v.get("description") or v.get("headline", "")
    if v.get("instruction"):
        txt = (txt + "\n" + v["instruction"]).strip()
    if txt and bottom - y > 14:
        size, lines, L, tr = c.fit(txt, "x600", 19, Wd, bottom - y, lh=1.35, min_size=12)
        maxl = max(1, int((bottom - y + 0.5) // L))
        if len(lines) > maxl:
            lines = lines[:maxl]
            lines[-1] = _ell(c, lines[-1] + "…", "x600", size, Wd)
        c.para(X, y, Wd, lines, "x600", size, L)
    return c.finish()


# ================================================================== wifi
def wifi(ctx, v):
    from ..plugins import wifi as wifi_plugin
    c = Canvas("bauhaus", Wh)
    c.circle(30, 460, 110, fill=Y)
    c.rect((0, 0, 18, 480), fill=K)
    X, Wd = 60, 330
    y = 40
    sec = v.get("security") or ctx.t("Open", "Offen")
    sw = min(110, _w(c, sec.upper(), "x800", 14, 4))
    tw_, th = _tag(c, X, y, v["title"], maxw=Wd - sw - 14)
    _line(c, X + tw_ + 14, y + 6, sec, "x800", 14, Wd - tw_ - 14, K, 4, upper=True, mn=8)
    y += th + 18
    y += _label(c, X, y, v["network_label"], maxw=Wd) + 2
    y += _line(c, X, y, v["ssid"], "black", 64, Wd, K, -2, lh=1, mn=18) + 18
    pw = v.get("password", "")
    if pw:
        c.rect((X, y, X + Wd, y + 4), fill=K)
        y += 4 + 12
        y += _label(c, X, y, v["password_label"], maxw=Wd) + 6
        s, tr = _shrink(c, pw, "black", 34, Wd, 0, 18)
        if _w(c, pw, "black", s, tr) <= Wd:
            c.text(X, y, pw, "black", s, R, lh=1)
            y += 34
        else:
            lines, cur = [], ""
            for ch in pw:
                if cur and _w(c, cur + ch, "black", 18) > Wd:
                    lines.append(cur)
                    cur = ""
                cur += ch
            lines.append(cur)
            for ln in lines[:4]:
                c.text(X, y, ln, "black", 18, R, lh=1.1)
                y += 19.8
        y += 18
    if v.get("note") and y < 390:
        size, lines, L, tr = c.fit(v["note"], "x600", 17, Wd, 400 - y, lh=1.25, min_size=11)
        lines = lines[:max(1, int((400 - y) // L))]
        c.para(X, y, Wd, lines, "x600", size, L)
    # QR in a 349 px frame at right 30 / top 40
    QX, QY, QS = 421, 40, 349
    c.rect((QX, QY, QX + QS, QY + QS), fill=K)
    wifi_plugin.draw_modules(c.d, v["modules"], QX + 6, QY + 6, QS - 12, dark=K, light=Wh, quiet=2)
    # hint: triangle + blue tag, centred under the code
    hint = v.get("hint", "")
    hs, htr = _shrink(c, hint.upper(), "x800", 15, QS - 38 - 24, 2, 8)
    hw = _w(c, _ell(c, hint.upper(), "x800", hs, QS - 38 - 24, htr), "x800", hs, htr) + 24
    hx = QX + (QS - (26 + 12 + hw)) / 2
    hh = c.line_h("x800", 15) + 12
    _tri(c, hx, 400 + (hh - 22) / 2, 26, 22, B)
    _tag(c, hx + 38, 400, hint, size=15, track=2, fill=B, maxw=QS - 38)
    c.circle(181, 421, 11, fill=R)
    c.rect((198, 410, 220, 432), fill=B)
    c.poly([(226, 432), (250, 432), (238, 410)], fill=Y)
    return c.finish()


# ================================================================== habits
def _mark(c, i, x, y, s, col):
    """Habit marker: circle, square, triangle in turn."""
    k = i % 3
    if k == 0:
        c.circle(x + s / 2, y + s / 2, s / 2, fill=col)
    elif k == 1:
        c.rect((x, y, x + s, y + s), fill=col)
    else:
        c.poly([(x, y + s), (x + s + 2, y + s), (x + s / 2 + 1, y)], fill=col)


def habits(ctx, v):
    c = Canvas("bauhaus", Wh)
    X0, X1, top = 24, 776, 26
    sx = X1 - (3 * 18 + 14 + 2)
    _shapes(c, sx, top + 5, 18)
    tw_, th = _tag(c, X0, top, v["title"], maxw=300)
    sub = ctx.t("Last 6 weeks", "Letzte 6 Wochen") + f" · {v['weekday_short']} {v['date_short']}"
    _line(c, X0 + tw_ + 14, top + 6, sub, "x800", 14, sx - 16 - X0 - tw_ - 14, K, 4, upper=True)
    y = top + th + 18
    c.rect((X0, y, X1, y + 4), fill=K)
    y += 4
    foot_h = c.line_h("x800", 11)
    foot_top = 480 - 22 - foot_h
    hs = v["habits"][:6]
    n = len(hs)
    ncol = max(4, n) if n > 1 else 4
    colw = (X1 - X0) / ncol
    cell = min(20, math.floor((colw - 28 - 5 * 4) / 6))
    nowc, nowr = v.get("now", [5, 0])
    for i, h in enumerate(hs):
        x = X0 + i * colw
        if i < n - 1:
            c.rect((x + colw - 2, y, x + colw, foot_top - 18), fill=K)
        ix, iy = x + 14, y + 12
        col = COL.get(h.get("color"), K)
        _mark(c, i, ix, iy + 2, 18, col)
        nw = colw - 28 - 28
        size, lines, L, tr = c.fit(h["name"], "x800", 15, nw, 44, lh=1.2, track=1, min_size=10, upper=True)
        if len(lines) > 2 or len(lines) * L > 44.5:
            lines = lines[:2]
            lines[-1] = _ell(c, lines[-1] + "…", "x800", size, nw, tr)
        c.para(ix + 28, iy, nw, lines, "x800", size, L, K, tr)
        gy = iy + 44 + 10
        for wk, days in enumerate(h["grid"][:6]):
            for d, val in enumerate(days[:7]):
                cx_, cy_ = ix + wk * (cell + 4), gy + d * (cell + 4)
                box = (cx_, cy_, cx_ + cell, cy_ + cell)
                if val is None:
                    continue
                if val:
                    c.rect(box, fill=col)
                else:
                    c.rect(box, fill=Wh, outline=K, width=2)
                if [wk, d] == [nowc, nowr]:
                    c.rect(box, outline=Y, width=4)
        sy = gy + 7 * (cell + 4) - 4 + 14
        num = str(h["streak"])
        c.text(ix, sy, num, "black", 54, R if h.get("hot") else K, lh=0.9)
        nw2 = _w(c, num, "black", 54) + 8
        lab = ctx.t("days in a row", "Tage in Folge").upper()
        lw = colw - 28 - nw2
        ls, llines, LL, ltr = c.fit(lab, "x800", 11, lw, 2 * c.line_h("x800", 11), track=2, lh=None,
                                    min_size=8)
        if c.line_h("x800", 11) * 0 == 0:
            LL = c.line_h("x800", ls)
        llines = llines[:2]
        ly = sy + 54 * 0.9 - 4 - len(llines) * LL + 6
        for ln in llines:
            c.text(ix + nw2, ly, ln, "x800", ls, K, track=ltr)
            ly += LL
    leg = ctx.t("Today", "Heute").upper()
    lgw = _w(c, leg, "x800", 11, 2)
    c.text(X1, foot_top, leg, "x800", 11, K, track=2, align="r")
    bx = X1 - lgw - 18
    c.rect((bx, foot_top + foot_h / 2 - 6, bx + 12, foot_top + foot_h / 2 + 6), fill=K, outline=Y, width=3)
    wl = v.get("weekday_letters") or ["M", "", "", "", "", "", "S"]
    _label(c, X0, foot_top, ctx.t("Columns = weeks · rows = {a} – {b}", "Spalten = Wochen · Zeilen = {a} – {b}",
                                  a=wl[0], b=wl[6]), maxw=bx - X0 - 20)
    return c.finish()


# ================================================================== sudoku
def sudoku(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.circle(770, 470, 100, fill=B)
    c.rect((730, 0, 800, 70), fill=R)
    c.rect((30, 31, 448, 449), fill=K)
    for r in range(9):
        for col in range(9):
            x = 34 + (col // 3) * 138 + (col % 3) * 45
            y = 35 + (r // 3) * 138 + (r % 3) * 45
            c.rect((x, y, x + 44, y + 44), fill=Wh)
            d = v["grid"][r][col]
            if d:
                _ctext(c, x + 22, y + 22, str(d), "black", 26)
    X, Wd = 488, 250
    y = 34
    _, th = _tag(c, X, y, v["title"], maxw=Wd)
    y += th + 18
    size, lines, L, tr = c.fit(v.get("subtitle", ""), "black", 44, Wd, 3 * 44 * 0.95, lh=0.95, track=-1,
                               min_size=20, upper=True)
    c.para(X, y, Wd, lines[:3], "black", size, L, K, tr)
    y += len(lines[:3]) * L + 18
    c.rect((X, y, X + Wd, y + 4), fill=K)
    y += 4 + 12
    y += _label(c, X, y, ctx.t("Difficulty", "Schwierigkeit"), maxw=Wd) + 8
    for i in range(v.get("level_max", 3)):
        if i < v.get("level_no", 1):
            c.circle(X + 10 + i * 26, y + 15, 10, fill=R)
        else:
            c.circle(X + 10 + i * 26, y + 15, 10, outline=K, width=3)
    lx = X + v.get("level_max", 3) * 26 + 6
    _line(c, lx, y + 15 - c.line_h("black", 24) / 2, v["level_name"], "black", 24, X + Wd - lx, upper=True, mn=11)
    y += 30 + 18
    c.rect((X, y, X + Wd, y + 2), fill=K)
    y += 2 + 10
    y += _label(c, X, y, ctx.t("Givens", "Vorgegeben"), maxw=Wd) + 2
    y += _line(c, X, y, v["givens_text"], "x800", 18, Wd, mn=10) + 18
    _tag(c, X, y, v["hint"], track=2, fill=Y, ink=K, maxw=Wd)
    return c.finish()


# ================================================================== solar
def solar(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 300, 480), fill=K)
    cx, cy = 110, 210
    for k in range(12):
        a = k * math.pi / 6
        pts = [(cx + 130 * math.cos(a - .14), cy + 130 * math.sin(a - .14)),
               (cx + 154 * math.cos(a), cy + 154 * math.sin(a)),
               (cx + 130 * math.cos(a + .14), cy + 130 * math.sin(a + .14))]
        c.poly(pts, fill=Y)
    c.circle(cx, cy, 120, fill=Y)
    c.rect((216, 0, 300, 84), fill=R)
    ps, plines, pL, ptr = c.fit(v.get("power_label", ""), "x800", 13, 72, 2 * c.line_h("x800", 13), lh=None,
                                track=1, min_size=8, upper=True)
    py = 32
    for ln in plines[:2]:
        _line(c, 288, py, ln, "x800", ps, 72, Wh, ptr, align="r", mn=7)
        py += c.line_h("x800", ps)
    num = str(v["power_w"])
    s, tr = _shrink(c, num, "black", 100, 250, -5, 30)
    c.text(24, 156 + (100 - s) / 2, num, "black", s, K, track=tr, lh=1)
    c.text(28, 480 - 74 - c.line_h("black", 34), "WATT", "black", 34, Wh, track=2)
    meta = " · ".join(t for t in (v.get("now_text", ""), v.get("place", "")) if t)
    _line(c, 28, 480 - 40 - c.line_h("x600", 16), meta, "x600", 16, 260, Wh, 5, upper=True)

    X0, X1, top, bot = 334, 766, 30, 454
    Wd = X1 - X0
    tag = ctx.t("System {p}", "Anlage {p}", p=v.get("peak_text", ""))
    tw_, th = _tag(c, X1, top, tag, size=12, track=2, padx=10, pady=5, maxw=Wd / 2, align="r")
    _line(c, X0, top, v["title"], "x800", 16, Wd - tw_ - 14, K, 5, upper=True)
    y = top + max(th, c.line_h("x800", 16)) + 18
    big = v["today_num"]
    bs, btr = _shrink(c, big, "black", 84, Wd * 0.55, -3, 40)
    bL = 84 * 0.85
    c.text(X0, y + (bL - bs * 0.85), big, "black", bs, K, track=btr, lh=0.85)
    rx = X0 + _w(c, big, "black", bs, btr) + 18
    rw = X1 - rx
    t1h = c.line_h("black", 22)
    gh = c.line_h("x800", 15) + 10
    by = y + bL - 2 - gh - 8 - t1h
    _line(c, rx, by, ctx.t("kWh today", "kWh heute"), "black", 22, rw, upper=False, mn=11)
    _tag(c, rx, by + t1h + 8, ctx.t("≈ {e} saved", "≈ {e} gespart", e=v.get("saved_text", "")), size=15, track=1,
         fill=G, padx=10, pady=5, maxw=rw)
    y += bL + 18
    # two cells
    c.rect((X0, y, X1, y + 4), fill=K)
    gt = y + 4
    lab_h, val_h = c.line_h("x800", 11), c.line_h("black", 22)
    ch = 10 + lab_h + 2 + val_h
    c.vline(X0 + Wd / 2 - 2, gt, gt + ch, K, 2)
    first = (ctx.t("Total", "Insgesamt"), v["total_text"]) if v.get("total_text") else \
        (ctx.t("Peak at", "Spitze um"), v.get("max_time") or "–")
    cells = (first, (ctx.t("Peak today", "Spitze heute"), v.get("max_text") or "–"))
    for i, (lab, val) in enumerate(cells):
        x = X0 + (Wd / 2 + 12 if i else 0)
        cw = Wd / 2 - 14
        _label(c, x, gt + 10, lab, maxw=cw)
        _line(c, x, gt + 10 + lab_h + 2, val, "black", 22, cw, mn=11)
    y = gt + ch + 18
    # chart
    tl = v.get("tick_labels") or ["06", "21"]
    ticks = v.get("ticks") or [6, 21]
    a, b = ticks[0], ticks[-1]
    lab = ctx.t("Power {a} – {b} h", "Leistung {a} – {b} Uhr", a=tl[0], b=tl[-1])
    fw = min(Wd / 2, _w(c, v.get("footer", "").upper(), "x800", 11, 2))
    _label(c, X1, y, v.get("footer", ""), maxw=Wd / 2, align="r")
    _label(c, X0, y, lab, maxw=Wd - fw - 16)
    ctop = y + lab_h + 6
    tick_h = c.line_h("x800", 11)
    cbot = bot - tick_h - 6
    c.rect((X0, cbot - 4, X1, cbot), fill=K)
    nb = max(1, int((b - a) * 2))
    gap = 3
    bw = (Wd - gap * (nb - 1)) / nb
    peak = v.get("peak") or 1
    hmax = cbot - 4 - ctop
    hrs, ws = v.get("hours") or [], v.get("watts") or []
    nowh = v.get("now", 0)
    for i in range(nb):
        h0, h1 = a + i * 0.5, a + (i + 1) * 0.5
        vals = [min(w, peak) for t, w in zip(hrs, ws) if h0 <= t < h1]
        if not vals:
            continue
        p = sum(vals) / len(vals)
        hh = round(p / peak * hmax) + 3
        x = X0 + i * (bw + gap)
        c.rect((x, cbot - 4 - hh, x + bw, cbot - 4), fill=R if h0 <= nowh < h1 else K)
    for i, t in enumerate(tl):
        x = X0 + Wd * (ticks[i] - a) / max(1, b - a)
        c.text(x, cbot + 6, t, "x800", 11, align="l" if i == 0 else "r" if i == len(tl) - 1 else "c")
    return c.finish()


# ================================================================== waterlevel
def waterlevel(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 300, 480), fill=B)
    c.rect((0, 330, 300, 480), fill=K)
    c.circle(278, 22, 42, fill=Y)
    _line(c, 28, 30, ctx.t("Level now", "Pegel jetzt"), "x800", 14, 210, Wh, 4, upper=True)
    num = v.get("value_num") or "–"
    s, tr = _shrink(c, num, "black", 118, 262, -5, 40)
    c.text(22, 92 + (118 - s) * 0.6, num, "black", s, Wh, track=tr, lh=1)
    _line(c, 28, 228, v.get("unit", ""), "black", 34, 250, Wh, 2, upper=True)
    if v.get("state_text"):
        _tag(c, 28, 284, v["state_text"], size=15, track=3, fill=Wh, ink=R if v.get("high") else K, pady=5,
             maxw=250)
    by = 480 - 34
    if v.get("change_24h_text"):
        L = c.line_h("x600", 16)
        _line(c, 28, by - L, f"{v['change_24h_text']} / 24 h", "x600", 16, 250, Wh, 3, upper=True)
        by -= L + 6
    if v.get("trend"):
        L = max(20, c.line_h("black", 22))
        tr_ = v["trend"]
        if tr_ == "rising":
            _tri(c, 28, by - L / 2 - 10, 24, 20, R)
        elif tr_ == "falling":
            _tri(c, 28, by - L / 2 - 10, 24, 20, Y, down=True)
        else:
            c.rect((28, by - L / 2 - 4, 52, by - L / 2 + 4), fill=Wh)
        _line(c, 62, by - L, v.get("trend_text", ""), "black", 22, 220, Wh, upper=True, mn=11)

    X0, X1, top = 334, 766, 30
    Wd = X1 - X0
    sx = X1 - (3 * 18 + 14 + 2)
    _shapes(c, sx, top, 18)
    y = top
    y += _line(c, X0, y, v.get("station", ""), "black", 40, sx - X0 - 12, K, lh=1, upper=True, mn=16) + 4
    if v.get("water"):
        y += _line(c, X0, y, v["water"], "x800", 16, Wd, K, 5, upper=True)
    y += 14
    c.rect((X0, y, X1, y + 4), fill=K)
    y += 4 + 8
    refs = [r for r in v.get("refs", []) if r.get("key") in ("HSW", "MW")]
    lx = X1
    for r in reversed(refs):
        t = f"{r['key']} {r['value']}".upper()
        tw_ = _w(c, t, "x800", 11, 1)
        c.text(lx, y, t, "x800", 11, K, track=1, align="r")
        lh = c.line_h("x800", 11)
        c.rect((lx - tw_ - 22, y + lh / 2 - 2, lx - tw_ - 6, y + lh / 2 + 2), fill=R if r["key"] == "HSW" else K)
        lx -= tw_ + 22 + 14
    _label(c, X0, y, ctx.t("Last {n} days · {u}", "Letzte {n} Tage · {u}", n=v.get("days", 7), u=v.get("unit", "")),
           maxw=lx - X0)
    y += c.line_h("x800", 11) + 14
    # chart 432 × 220
    ct, cb = y, y + 216
    vals, xs = v.get("values") or [], v.get("x") or []
    mw, hsw = v.get("mw"), v.get("hsw")
    lo_c = [x for x in (v.get("min"), mw) if x is not None]
    hi_c = [x for x in (v.get("max"), hsw, mw) if x is not None]
    if lo_c and hi_c:
        lo, hi = min(lo_c), max(hi_c)
        rng = (hi - lo) or 1
        lo -= rng * 0.15
        rng = hi - lo

        def Y_(val):
            return cb - (val - lo) / rng * (216 - 37)
        if hsw is not None:
            c.rect((X0, Y_(hsw) - 2, X1, Y_(hsw) + 2), fill=R)
        if len(vals) >= 2 and len(xs) == len(vals):
            step = max(1, len(vals) // 216)
            pts = [(X0 + 4 + xs[i] * (Wd - 14), Y_(vals[i])) for i in range(0, len(vals), step)]
            last = (X0 + 4 + xs[-1] * (Wd - 14), Y_(vals[-1]))
            if pts[-1] != last:
                pts.append(last)
            c.poly([(pts[0][0], cb)] + pts + [(pts[-1][0], cb)], fill=B)
            if mw is not None:
                c.rect((X0, Y_(mw) - 1.5, X1, Y_(mw) + 1.5), fill=K)
            c.stroke(pts, K, 4)
            c.circle(last[0], last[1], 8, fill=R)
        elif mw is not None:
            c.rect((X0, Y_(mw) - 1.5, X1, Y_(mw) + 1.5), fill=K)
    c.rect((X0, cb, X1, cb + 4), fill=K)
    ty = cb + 10
    ticks = v.get("day_ticks") or []
    minsp = max([_w(c, t["weekday"].upper(), "x800", 11) for t in ticks] + [0]) + 6
    lastx = -999
    for t in ticks:
        x = X0 + 4 + t["x"] * (Wd - 14)
        c.rect((x - 1, cb - 6, x + 1, cb), fill=K)
        lab = t["weekday"].upper()
        tx = min(max(x, X0 + _w(c, lab, "x800", 11) / 2), X1 - _w(c, lab, "x800", 11) / 2)
        if tx - lastx >= minsp:
            c.text(tx, ty, lab, "x800", 11, align="c")
            lastx = tx
    _label(c, X0, 480 - 22 - c.line_h("x800", 11), v.get("footer", ""), maxw=Wd)
    return c.finish()


# ================================================================== birthdays
def birthdays(ctx, v):
    c = Canvas("bauhaus", Wh)
    c.circle(310, 40, 150, fill=R)
    c.rect((0, 0, 18, 480), fill=K)
    festive = v.get("festive") and v.get("celebrants")
    _tag(c, 50, 30, v["festive_title"] if festive else v["title"], maxw=400)
    X, Wd = 50, 400
    y = 92
    if festive:
        cel = v["celebrants"]
        when = ctx.t("Today", "Heute")
        name = v.get("festive_names") or " & ".join(p["name"] for p in cel)
        age = cel[0].get("age") if len(cel) == 1 else None
        date_tag = cel[0]["date_long"]
        rest = [p for p in v["people"] if p["days"] > 0][:4]
    else:
        f = v["first"]
        when, name, age, date_tag = f["when"], f["name"], f.get("age"), f["date_long"]
        rest = v.get("others", [])[:4]
    y += _line(c, X, y, when, "x800", 18, Wd, K, 4, upper=True) + 12
    # name: one line (shrinks), else two lines
    nm = name.upper()
    s, tr = _shrink(c, nm, "black", 120, Wd, -5, 56)
    if _w(c, nm, "black", s, tr) <= Wd:
        c.text(X, y + (120 - s) * 0.85, nm, "black", s, K, track=tr, lh=0.85)
        y += 120 * 0.85 + 12
    else:
        size, lines, L, tr = c.fit(nm, "black", 60, Wd, 2 * 60 * 0.9, lh=0.9, track=-2, min_size=22)
        if len(lines) > 2:
            lines = lines[:2]
            lines[1] = _ell(c, lines[1] + "…", "black", size, Wd, tr)
        c.para(X, y, Wd, lines, "black", size, L, K, tr)
        y += len(lines) * L + 12
    if age is not None:
        verb = ctx.t("turns", "wird").upper()
        vs, vtr = _shrink(c, verb, "black", 34, Wd - 92 - 16, 0, 14)
        c.text(X, y + 46 - c.line_h("black", vs) / 2, verb, "black", vs, K)
        bx = X + _w(c, verb, "black", vs) + 16
        c.rect((bx, y, bx + 92, y + 92), fill=B)
        a = str(age)
        as_, atr = _shrink(c, a, "black", 50, 80, -2, 20)
        _ctext(c, bx + 46, y + 46, a, "black", as_, Wh, atr)
        y += 92 + 12
    _tag(c, X, y, date_tag, size=16, track=2, fill=Y, ink=K, maxw=Wd)
    if festive:
        for (x, yy, k, col) in ((60, 420, 0, B), (110, 430, 1, Y), (160, 418, 2, R), (420, 300, 0, Y), (380, 430, 1, R)):
            _mark(c, k, x, yy, 20, col)

    X0, Wd2 = 478, 292
    yy = 30
    _label(c, X0, yy, ctx.t("After that", "Danach"), maxw=Wd2)
    yy += c.line_h("x800", 11) + 8
    c.rect((X0, yy, X0 + Wd2, yy + 4), fill=K)
    yy += 4
    if not rest:
        return c.finish()
    rh = (454 - yy) / 4
    cols = (R, B, Y, G)
    for i, p in enumerate(rest):
        cy = yy + rh / 2
        _mark(c, i % 2, X0, cy - 11, 22, cols[i % 4])
        # right block: number + unit
        num = str(p["days"])
        unit = (ctx.t("day", "Tag") if p["days"] == 1 else ctx.t("days", "Tage")).upper()
        nw = _w(c, num, "black", 26)
        uw = min(90, _w(c, unit, "x800", 11, 2))
        bw = max(nw, uw)
        nL, uL = 26, c.line_h("x800", 11)
        bt = cy - (nL + 2 + uL) / 2
        c.text(X0 + Wd2, bt, num, "black", 26, K, lh=1, align="r")
        _line(c, X0 + Wd2, bt + nL + 2, unit, "x800", 11, 90, K, 2, align="r", mn=8)
        tx = X0 + 36
        tw_ = X0 + Wd2 - bw - 14 - tx
        L1, L2 = 24 * 1.1, c.line_h("x600", 14)
        ty = cy - (L1 + 2 + L2) / 2
        _line(c, tx, ty, p["name"], "black", 24, tw_, lh=1.1, mn=12)
        det = p["date_short"] + (f" · {p['age_text']}" if p.get("age_text") else "")
        _line(c, tx, ty + L1 + 2, det, "x600", 14, tw_, K, 1, mn=9)
        yy += rh
        c.rect((X0, yy - 2, X0 + Wd2, yy), fill=K)
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    from ..plugins.watchlist import spark_points
    c = Canvas("bauhaus", Wh)
    c.rect((0, 0, 800, 64), fill=K)
    sw = 3 * 16 + 14
    _shapes(c, 770 - sw, 24, 16)
    tw_ = min(300, _w(c, v["title"].upper(), "black", 28, 2))
    _line(c, 30, 32 - c.line_h("black", 28) / 2, v["title"], "black", 28, 300, Wh, 2, upper=True, mn=14)
    _line(c, 770 - sw - 16, 32 - c.line_h("x800", 13) / 2, v.get("subtitle", ""), "x800", 13,
          770 - sw - 16 - 30 - tw_ - 24, Wh, 3, align="r", upper=True, mn=8)
    items = v["items"][:6]
    n = len(items)
    nrows = max(1, math.ceil(n / 2))
    if n == 1:
        nrows = 1
    ncols = 1 if n == 1 else 2
    foot_h = c.line_h("x800", 11)
    gt, gb = 64, 480 - 18 - foot_h - 6
    X0, X1 = 30, 770
    cw = (X1 - X0) / ncols
    rh = (gb - gt) / max(2, nrows) if nrows <= 2 else (gb - gt) / nrows
    for i, it in enumerate(items):
        r, col = divmod(i, ncols)
        x0 = X0 + col * cw
        y0 = gt + r * rh
        if col == 0 and ncols == 2:
            c.rect((x0 + cw - 2, y0, x0 + cw, y0 + rh), fill=K)
        if r < nrows - 1:
            c.rect((x0, y0 + rh - 2, x0 + cw, y0 + rh), fill=K)
        pl = 0 if col == 0 else 24
        pr = 24 if (col == 0 and ncols == 2) else 0
        ix0, ix1 = x0 + pl, x0 + cw - pr
        y = y0 + (16 if nrows <= 2 else 10)
        colr = COL.get(it.get("color", "black"), K) if it.get("ok") else K
        lh15 = c.line_h("x800", 15)
        badge_w = 0
        if it.get("ok"):
            ch = it["change_text"]
            badge_w = _w(c, ch, "x800", 15) + 16
            c.rect((ix1 - badge_w, y, ix1, y + lh15 + 6), fill=colr)
            c.text(ix1 - 8, y + 3, ch, "x800", 15, Wh, align="r")
            d = it.get("direction")
            if d == "up":
                _tri(c, ix0, y + (lh15 + 6) / 2 - 7, 16, 14, colr)
            elif d == "down":
                _tri(c, ix0, y + (lh15 + 6) / 2 - 7, 16, 14, colr, down=True)
            else:
                c.rect((ix0 + 2, y + (lh15 + 6) / 2 - 6, ix0 + 14, y + (lh15 + 6) / 2 + 6), fill=K)
        else:
            c.rect((ix0 + 2, y + (lh15 + 6) / 2 - 6, ix0 + 14, y + (lh15 + 6) / 2 + 6), outline=K, width=3)
        _line(c, ix0 + 24, y + 3, it["label"], "x800", 15, ix1 - badge_w - 8 - ix0 - 24, K, 2, upper=True, mn=10)
        y += lh15 + 6 + 6
        if not it.get("ok"):
            c.text(ix0, y, "–", "black", 34, K, lh=1)
            if it.get("error"):
                _line(c, ix0, y + 40, it["error"], "x600", 13, ix1 - ix0, R, mn=9)
            continue
        vs = 34 if nrows <= 2 else 26
        _line(c, ix0, y, it["last_text"], "black", vs, ix1 - ix0, K, -1, lh=1, mn=14)
        y += vs + 6
        sh = y0 + rh - 10 - y
        if sh > 16:
            c.rect((ix0, y + sh - 3, ix1, y + sh), fill=K)
            pts = spark_points(it["values"], ix0 + 6, y + 8, ix1 - ix0 - 18, sh - 18)
            if len(pts) >= 2:
                c.stroke(pts, colr, 4)
                c.circle(pts[-1][0], pts[-1][1], 6, fill=colr)
    _label(c, 30, 480 - 18 - foot_h, v.get("footer") or v.get("source", ""), maxw=740)
    return c.finish()
