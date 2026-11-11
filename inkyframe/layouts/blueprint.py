"""Blueprint ("Blaupause") signature layouts of the plugins – ports of mockups/Blaupause-*.dc.html.

White technical drawing on blueprint blue: faint grid, 2 px frame, "FIG. n – …" captions, outlined
light-weight numerals, dimension lines and the title block bottom right.
Positions: the mockups' inner box starts at (16, 16) (14 px padding + 2 px border).
"""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from ..designs import _bp_grid, numeric_date
from ..plugins import _calendar as C
from ..studio import B, G, K, R, Y, Canvas, Wh, W, H

OX, OY = 16, 16                    # inner box origin
RIGHT = 784                        # inner box right edge
COL = {"green": G, "yellow": Y, "red": R, "black": K, "blue": B, "white": Wh}


# ================================================================== helpers
def _page():
    c = Canvas("blueprint", B)
    _bp_grid(c)
    c.rect((14, 14, 786, 466), outline=Wh, width=2)
    return c


def _ell(c, text, role, size, width, track=0.0):
    """Cut text with an ellipsis so it fits width."""
    if c.tw(text, role, size, track) - track <= width:
        return text
    while text and c.tw(text + "…", role, size, track) - track > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _size(c, text, role, size, width, track=0.0, min_size=8):
    s = size
    while s > min_size and c.tw(text, role, s, track) - track > width:
        s -= 1
    return s


def _line(c, x, y, text, role, size, width, fill=Wh, track=0.0, min_size=None, align="l", lh=None):
    """One line that shrinks (to min_size) and then gets an ellipsis; keeps the line box of `size`.
    Returns (used size, drawn width)."""
    if min_size is None:
        min_size = max(8, int(size * 0.75))
    s = _size(c, text, role, size, width, track, min_size)
    t = _ell(c, text, role, s, width, track)
    L = c.line_h(role, size, lh)
    c.text(x, y, t, role, s, fill, track=track, lh=L / s, align=align)
    return s, c.tw(t, role, s, track) - track


def _fig(c, ctx, x, y, n, label, width=330, fill=Wh, align="l", tail="", track=2):
    """Caption 'FIG. n – LABEL' (12 px, letter-spacing 2); `tail` is appended without upper-casing."""
    txt = ctx.t("Fig. {n} – {s}", "Fig. {n} – {s}", n=n, s=label).upper() + tail
    return _line(c, x, y, txt, "pm400", 12, width, fill, track=track, min_size=9, align=align)


def _outline(c, items, fill=Wh, ring=2, outside=False):
    """-webkit-text-stroke with transparent fill for several texts at once.
    items: (x, top, text, role, size, lh, align). outside=True keeps thin glyphs hollow (small letters)."""
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    md.fontmode = "1"
    for x, top, text, role, size, lh, align in items:
        f = c.font(role, size)
        base = c._baseline(top, role, size, lh)
        w = md.textlength(text, font=f)
        x0 = x if align == "l" else x - w / 2 if align == "c" else x - w
        md.text((x0, base), text, font=f, fill=255, anchor="ls")
    k = 2 * (ring // 2) + 1
    outer = m.filter(ImageFilter.MaxFilter(k))
    inner = m if outside else m.filter(ImageFilter.MinFilter(k))
    ringm = ImageChops.subtract(outer, inner).point(lambda v: 255 if v > 127 else 0)
    c.img.paste(fill, (0, 0, W, H), ringm)


def _big(c, x, top, text, size, width, lh=0.9, fill=Wh, align="l", min_size=24, role="pm300"):
    """Outlined numeral/word that shrinks to width; keeps the line box. Returns (size, width)."""
    s = _size(c, text, role, size, width, 0, min_size)
    L = size * lh
    while s > min_size:                     # accents above capitals must stay inside the line box
        top_s = top + (L - s * lh) / 2
        gtop = c._baseline(top_s, role, s, lh) + c.font(role, s).getbbox(text, anchor="ls")[1]
        if gtop >= top - 2:
            break
        s -= 2
    t = _ell(c, text, role, s, width)
    _outline(c, [(x, top + (L - s * lh) / 2, t, role, s, lh, align)], fill)
    return s, c.tw(t, role, s)


def _dim(c, x0, x1, y, text="", fill=Wh):
    """Horizontal dimension line ◂ —— TEXT —— ▸ (11 px)."""
    L = c.line_h("pm400", 11)
    c.text(x0, y, "◂", "pm400", 11, fill)
    c.text(x1, y, "▸", "pm400", 11, fill, align="r")
    a0 = x0 + c.tw("◂", "pm400", 11) + 4
    a1 = x1 - c.tw("▸", "pm400", 11) - 4
    cy = y + L / 2
    if text:
        text = _ell(c, text, "pm400", _size(c, text, "pm400", 11, a1 - a0 - 24, 0, 8), a1 - a0 - 24)
        s = _size(c, text, "pm400", 11, a1 - a0 - 24, 0, 8)
        tw = c.tw(text, "pm400", s)
        mid = (a0 + a1) / 2
        c.text(mid, y, text, "pm400", s, fill, align="c", lh=L / s)
        c.hline(a0, mid - tw / 2 - 4, cy, fill, 1)
        c.hline(mid + tw / 2 + 4, a1, cy, fill, 1)
    else:
        c.hline(a0, a1, cy, fill, 1)


def _vdim(c, x, y0, y1, text, fill=Wh):
    """Vertical dimension line ▴ | TEXT | ▾ centred on x."""
    L = c.line_h("pm400", 11)
    c.text(x, y0, "▴", "pm400", 11, fill, align="c")
    c.text(x, y1 - L, "▾", "pm400", 11, fill, align="c")
    mid = (y0 + y1) / 2
    c.text(x, mid - L / 2, text, "pm400", 11, fill, align="c")
    c.vline(x, y0 + L + 4, mid - L / 2 - 4, fill, 1)
    c.vline(x, mid + L / 2 + 4, y1 - L - 4, fill, 1)


def _cell(c, text, width, maxlines=2):
    """Fit a title-block cell: wrap to ≤ maxlines at 11…7 px. Returns (size, lines)."""
    paras = text.split("\n")
    maxlines = max(maxlines, len(paras))
    for s in range(11, 8, -1):              # one line per paragraph first (as in the mockups)
        if all(c.tw(p, "pm400", s) <= width for p in paras):
            return s, paras
    for s in range(11, 6, -1):
        lines = []
        for p in paras:
            lines += c.wrap(p, "pm400", s, width)
        if len(lines) <= maxlines and all(c.tw(ln, "pm400", s) <= width for ln in lines):
            return s, lines
    lines = []
    for p in paras:
        lines += c.wrap(p, "pm400", 7, width)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        lines[-1] += "…"
    return 7, [_ell(c, ln, "pm400", 7, width) for ln in lines]


def _tb(c, title, rows):
    """Title block bottom right. rows: lists of 1 (spanning) or 2 cells; a cell is str or (str, colour)."""
    x0, x1 = 526, 786
    mid = x0 + 2 + (x1 - x0 - 4) / 2
    LH = c.line_h("pm400", 11)
    prep = []
    for row in rows:
        cells = []
        for cell in row:
            text, col = (cell, Wh) if isinstance(cell, str) else cell
            w = (x1 - x0 - 4 - 16) if len(row) == 1 else (mid - x0 - 2 - 16 - 1)
            s, lines = _cell(c, text.upper(), w)
            cells.append((s, lines, col, w))
        n = max(len(cl[1]) for cl in cells)
        prep.append((cells, 10 + n * LH))
    head = 12 + c.line_h("pm600", 13)
    total = 2 + head + 1 + sum(h for _, h in prep) + (len(prep) - 1) + 2
    y0 = 466 - total
    c.rect((x0, y0, x1, 466), fill=B)
    c.rect((x0, y0, x1, 466), outline=Wh, width=2)
    _line(c, x0 + 10, y0 + 8, title.upper(), "pm600", 13, x1 - x0 - 20, min_size=9)
    y = y0 + 2 + head
    c.hline(x0, x1, y, Wh, 1)
    y += 1
    for i, (cells, h) in enumerate(prep):
        if len(cells) == 2:
            c.vline(mid, y, y + h, Wh, 1)
        for j, (s, lines, col, w) in enumerate(cells):
            xx = (x0 + 2 if j == 0 else mid + 1) + 8
            yy = y + 5
            for ln in lines:
                c.text(xx, yy, ln, "pm400", s, col, lh=LH / s)
                yy += LH
        y += h
        if i < len(prep) - 1:
            c.hline(x0, x1, y, Wh, 1)
            y += 1
    return y0


def _sheet(ctx, name, today=None):
    d = today or ctx.today
    return ctx.t("{t} · sheet {n}", "{t} · Blatt {n}", t=name, n=d.timetuple().tm_yday)


def _date_cell(ctx, d=None):
    d = d or ctx.today
    s = numeric_date(d, ctx.lang)
    y = str(d.year)
    if s.endswith(y):
        s = s[:-4] + y[2:]
    elif s.startswith(y):
        s = y[2:] + s[4:]
    return ctx.t("Date {d}", "Datum {d}", d=s)


def _drawn(ctx):
    return ctx.t("Drawn: inkyframe", "Gez. inkyframe")


def _scale(ctx):
    return ctx.t("Scale 1:1", "Maßstab 1:1")


def _place_cell(ctx, place):
    return ctx.t("Location {p}", "Ort {p}", p=place) if place else _date_cell(ctx)


def _dashed_circle(c, cx, cy, r, fill=Wh, width=2, seg=None):
    """Circle with stroke-dasharray 4 4."""
    n = max(8, int(2 * math.pi * r / 8)) if seg is None else seg
    for k in range(n):
        a0 = k * 360 / n
        c.d.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 180 / n, fill=fill, width=width)


def _swatch(c, x, y, s, fill, border=1):
    c.rect((x, y, x + s, y + s), fill=fill)
    c.rect((x, y, x + s, y + s), outline=Wh, width=border)


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = _page()
    last = v.get("last")
    if last:
        n = v.get("move_number")
        if n:
            mv = f"{n}. {last[0]}–{last[1]}" if not v["white_to_move"] else f"{max(1, n - 1)}… {last[0]}–{last[1]}"
        else:
            mv = f"{last[0]}–{last[1]}"
        cap = ctx.t("Position after {m}", "Stellung nach {m}", m="\x00").upper()
        cap, tail = cap.split("\x00")[0], mv + cap.split("\x00")[1] if "\x00" in cap else ""
        if not tail:
            cap += " " + mv
    else:
        cap, tail = ctx.t("Position", "Stellung"), ""
    _fig(c, ctx, 46, 42, 1, cap.rstrip(), width=380, tail=(" " + tail) if tail else "")
    # board
    s = 38
    coords = v.get("show_coords", True)
    bx0, by0 = 61, 68                       # outer border of the board
    sx0, sy0 = bx0 + 2, by0 + 2
    hl = set(tuple(rc) for rc in v.get("last_cells") or [])
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            x, y = sx0 + col * s, sy0 + r * s
            if (r, col) in hl:
                bg, fg = Y, K
            elif (r + col) % 2 == 1:
                bg, fg = Wh, K
            else:
                bg, fg = B, Wh
            c.rect((x, y, x + s, y + s), fill=bg)
            chess_puzzle.draw_piece(c.d, p, x + s // 2, y + s // 2, s, ink=fg, paper=bg)
    c.rect((bx0, by0, sx0 + 8 * s + 2, sy0 + 8 * s + 2), outline=Wh, width=2)
    L11 = c.line_h("pm400", 11)
    if coords:
        for r, rk in enumerate(v["ranks"]):
            c.text(bx0 - 6, sy0 + r * s + (s - L11) / 2, rk, "pm400", 11, Wh, align="r")
        for col, fl in enumerate(v["files"]):
            c.text(sx0 + col * s + s / 2, sy0 + 8 * s + 2 + 4, fl, "pm400", 11, Wh, align="c")
    _dim(c, 65, 373, 408, ctx.t("8 × 8 squares", "8 × 8 Felder").upper())
    if last and v.get("last_cells"):
        tr = v["last_cells"][-1][0]
        c.text(382, sy0 + tr * s + (s - L11) / 2, f"← {last[1]}", "pm400", 11, Y)
    # right column
    x, x1 = 436, 754
    wd = x1 - x
    y = 42
    _fig(c, ctx, x, y, 2, ctx.t("Task", "Aufgabe"), width=wd)
    y += c.line_h("pm400", 12) + 6
    _line(c, x, y, v["title"], "pm600", 30, wd, lh=1.1, min_size=18)
    y += 33 + 6 + 6
    sq = K if not v["white_to_move"] else Wh
    L20 = c.line_h("pm400", 20)
    c.rect((x, y + (L20 - 18) / 2, x + 18, y + (L20 - 18) / 2 + 18), fill=sq)
    c.rect((x, y + (L20 - 18) / 2, x + 18, y + (L20 - 18) / 2 + 18), outline=Wh, width=2)
    _line(c, x + 28, y, v["to_move"].upper(), "pm400", 20, wd - 28, track=1, min_size=12)
    y += L20 + 6 + 8
    big = f"#{v['mate_in']}" if v.get("mate_in") else str(v.get("moves") or "")
    side = v["mate"] if v.get("mate_in") else v.get("solution_text", "")
    bs, bw = _big(c, x, y, big, 120, 170)
    bh = 120 * 0.9
    sx = x + bw + 14
    L13 = c.line_h("pm400", 13)
    by = y + bh - 6 - L13
    if v.get("rating_text"):
        _line(c, sx, by, v["rating_text"], "pm400", 13, x1 - sx)
        by -= 4 + c.line_h("pm600", 20)
    else:
        by = y + bh - 6 - c.line_h("pm600", 20)
    _line(c, sx, by, side, "pm600", 20, x1 - sx, fill=Y, min_size=11)
    y += bh + 6 + 6
    _dim(c, x, x1, y, ctx.t("Themes", "Motive").upper())
    y += L11 + 6
    themes = " · ".join(t for t in v.get("themes", []) if t != v.get("mate")) or v.get("themes_text", "")
    if themes:
        size, lines, L, _ = c.fit(themes, "pm400", 15, wd, 2 * 15 * 1.3, lh=1.3, min_size=11)
        lines = lines[:2]
        for ln in lines:
            _line(c, x, y, ln, "pm400", size, wd, lh=1.3)
            y += L
    sol = v.get("solution_text", "")
    if ": " in sol:
        sol = sol.replace(": ", ":\n", 1)
    _tb(c, _sheet(ctx, v["name"], v.get("today")), [
        [sol, (v.get("hint", ""), Y)],
        [ctx.t("Source {s}", "Quelle {s}", s=v.get("source", "Lichess")), _drawn(ctx)]])
    return c.finish()


# ================================================================== spotify
def _cover_placeholder(c, x, y):
    c.rect((x, y, x + 300, y + 300), fill=K)
    c.circle(x + 190, y + 120, 80, fill=Y)
    for yy in (170, 198, 226):
        c.rect((x + 30, y + yy, x + 270, y + yy + 14), fill=Wh)
    c.poly([(x + 30, y + 40), (x + 130, y + 40), (x + 30, y + 150)], fill=R)
    c.circle(x + 190, y + 120, 22, fill=K)
    c.rect((x + 30, y + 256, x + 140, y + 270), fill=B)


def spotify(ctx, v):
    c = _page()
    _fig(c, ctx, 46, 42, 1, ctx.t("Cover 1:1", "Cover 1:1"), width=300)
    x0, y0 = 46, 68
    if v.get("image") is not None:
        img = ctx.punch(ctx.cover_fit(v["image"].convert("RGB"), 296, 296))
        c.img.paste(img, (x0 + 2, y0 + 2))
    else:
        _cover_placeholder(c, x0, y0)
    c.rect((x0, y0, x0 + 300, y0 + 300), outline=Wh, width=2)
    _dim(c, 46, 346, 376, "300")
    _vdim(c, 356, 68, 368, "300")
    # right column
    x, x1 = 416, 754
    wd = x1 - x
    y = 42
    _fig(c, ctx, x, y, 2, v.get("label", ""), width=wd)
    y += c.line_h("pm400", 12) + 8 + 6
    rest = 8 + c.line_h("pm400", 18) + (8 + c.line_h("pm400", 13) if v.get("album") else 0)
    avail = 222 - y - rest
    size, lines, L, _ = c.fit(v["track"], "pm600", 28, wd, avail, lh=1.2, min_size=16)
    if len(lines) * L > avail:
        lines = lines[:max(1, int(avail // L))]
        lines[-1] = _ell(c, lines[-1] + "…", "pm600", size, wd)
    for ln in lines:
        _line(c, x, y, ln, "pm600", size, wd, lh=1.2)
        y += L
    y += 8
    if v.get("artist"):
        _line(c, x, y, v["artist"], "pm400", 18, wd)
    y += c.line_h("pm400", 18) + 8
    if v.get("album"):
        lab = ctx.t("Album", "Album").upper() + ": "
        lw = c.tw(lab, "pm400", 13, 1)
        c.text(x, y, lab, "pm400", 13, Wh, track=1)
        _line(c, x + lw, y, v["album"], "pm400", 13, wd - lw, fill=Y, track=1, min_size=10)
    # fig 3 – time axis (no playback position: total length only)
    y = 232
    _fig(c, ctx, x, y, 3, ctx.t("Timeline", "Zeitachse"), width=wd)
    y += c.line_h("pm400", 12) + 6
    dur = v.get("duration_text") or "–:––"
    bh = 56 * 0.9
    _big(c, x, y, dur, 56, wd - 140)
    L14 = c.line_h("pm400", 14)
    _line(c, x1, y + bh - L14, ctx.t("Length", "Länge").upper(), "pm400", 14, 130, align="r")
    y += bh + 6 + 4
    c.rect((x, y, x1, y + 12), outline=Wh, width=1)
    for k in range(1, 4):
        tx = x + (x1 - x) * k / 4
        c.vline(tx, y + 3, y + 9, Wh, 1)
    y += 12 + 6
    c.text(x, y, "0:00", "pm400", 11, Wh)
    c.text(x1, y, v.get("duration_text") or "", "pm400", 11, Wh, align="r")
    if not v.get("playing"):
        c.text((x + x1) / 2, y, "▴ " + v.get("label", "").upper(), "pm400", 11, Y, align="c")
    _tb(c, _sheet(ctx, ctx.t("Playback", "Wiedergabe"), v.get("today")), [
        [ctx.t("Source {s}", "Quelle {s}", s=v.get("source", "Spotify")), ctx.t("Updated {t}", "Stand {t}", t=v.get("time", ""))],
        [_scale(ctx), _drawn(ctx)]])
    return c.finish()


# ================================================================== grid (Stromampel)
def _advice(ctx, color):
    if color == "green":
        return ctx.t("Wash, charge, run the dishwasher now", "Jetzt waschen, laden, spülen")
    if color == "yellow":
        return ctx.t("Use electricity sparingly", "Strom sparsam nutzen")
    if color == "red":
        return ctx.t("Shift consumption to later", "Verbrauch verschieben")
    return ""


def grid(ctx, v):
    c = _page()
    _fig(c, ctx, 46, 42, 1, ctx.t("Signal", "Signal"), width=116, track=1)
    # traffic light 80 × 190
    lx, ly = 46, 42 + c.line_h("pm400", 12) + 8
    c.rrect((lx + 6, ly + 2, lx + 74, ly + 188), 6, outline=Wh, width=2)
    on_cy = None
    for i, light in enumerate(v.get("lights") or []):
        cy = ly + (36, 95, 154)[i]
        if light.get("on"):
            c.circle(lx + 40, cy, 22, fill=COL.get(light["color"], Wh), outline=Wh, width=2)
            on_cy = cy
        else:
            _dashed_circle(c, lx + 40, cy, 22)
    if on_cy is not None:
        c.hline(lx + 74, lx + 80, on_cy, Wh, 1)
    # fig 2
    x, x1 = 166, 754
    wd = x1 - x
    y = 42
    cap = ctx.t("Green power now", "Ökostrom jetzt") + (f" · {v['place']}" if v.get("place") else "")
    _fig(c, ctx, x, y, 2, cap, width=wd)
    y += c.line_h("pm400", 12) + 6
    name = (v.get("signal_name") or "–").split(" · ")[0]
    bh = 110 * 0.9
    s, bw = _big(c, x, y, name.upper(), 110, wd - 50)
    if v.get("color"):
        sx = x + bw + 18
        c.rect((sx, y + bh - 10 - 26, sx + 26, y + bh - 10), fill=COL.get(v["color"], Wh))
        c.rect((sx, y + bh - 10 - 26, sx + 26, y + bh - 10), outline=Wh, width=2)
    y += bh + 6 + 4
    if v.get("share") is not None:
        line = ctx.t("{s} renewable share", "{s} Ökostromanteil", s=v["share_text"])
    else:
        line = v.get("subtitle", "")
    if v.get("congestion") and " · " in (v.get("signal_name") or ""):
        line += " · " + v["signal_name"].split(" · ", 1)[1]
    _line(c, x, y, line, "pm400", 22, wd, min_size=13)
    y += c.line_h("pm400", 22) + 6
    _dim(c, x, x + min(480, wd), y, ctx.t("Advice", "Empfehlung").upper())
    y += c.line_h("pm400", 11) + 6
    adv = _advice(ctx, v.get("color"))
    if adv:
        _line(c, x, y, adv, "pm600", 20, wd, fill=Y, min_size=12)
    y += c.line_h("pm600", 20) + 2
    if v.get("best_text"):
        _line(c, x, y, v["best_text"], "pm400", 13, wd, min_size=10)
    # fig 3 – 24 h band
    y = 282
    fx0, fx1 = 46, 754
    _fig(c, ctx, fx0, y, 3, ctx.t("Today 00–24 h", "Heute 00–24 h"), width=300)
    by0 = y + c.line_h("pm400", 12) + 14
    by1 = by0 + 40
    ix0, ix1 = fx0 + 2, fx1 - 2
    cw = (ix1 - ix0) / 24
    hours = v.get("hours") or []
    for i in range(24):
        h = hours[i] if i < len(hours) else {}
        col = COL.get(h.get("color")) if h else None
        a, b = ix0 + i * cw, ix0 + (i + 1) * cw
        if col is not None:
            c.rect((a, by0 + 2, b, by1 - 2), fill=col)
        if i < 23:
            c.vline(b - 1, by0 + 2, by1 - 2, Wh, 1)
    c.rect((fx0, by0, fx1, by1), outline=Wh, width=2)
    nx = ix0 + (ix1 - ix0) * max(0.0, min(1.0, v.get("now_pos", 0)))
    c.rect((nx - 1, by0 - 14, nx + 2, by1 + 6), fill=Y)
    nl = f"{v.get('now_label', '')} {v.get('time', '')}".strip().upper()
    if nx + 8 + c.tw(nl, "pm400", 11) < fx1:
        c.text(nx + 8, by0 - 16, nl, "pm400", 11, Y)
    else:
        c.text(nx - 6, by0 - 16, nl, "pm400", 11, Y, align="r")
    ay = by1 + 4
    for i, t in enumerate(("00", "06", "12", "18", "24")):
        c.text(fx0 + (fx1 - fx0) * i / 4, ay, t, "pm400", 11, Wh, align="l" if i == 0 else "r" if i == 4 else "c")
    # legend: colours of today with their times
    y = 380
    L13 = c.line_h("pm400", 13)
    rows = []
    segs = v.get("segments") or []
    for colname in ("green", "yellow", "red"):
        ss = [s for s in segs if s.get("color") == colname]
        if not ss:
            continue
        nm = ss[0].get("name", colname).split(" · ")[0].upper()
        spans = ", ".join(f"{s['from']}–{s['to']}" for s in ss)
        rows.append((COL[colname], f"{nm} · {spans}"))
    for col, txt in rows[:3]:
        _swatch(c, 46, y + (L13 - 14) / 2, 14, col)
        _line(c, 46 + 24, y, txt, "pm400", 13, 526 - 12 - 70, min_size=10)
        y += L13 + 4
    _line(c, 46, max(y + 2, 444), v.get("source", ""), "pm400", 11, 526 - 12 - 46, min_size=8)   # CC BY credit
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [ctx.t("Updated {t}", "Stand {t}", t=v.get("time", "")), _date_cell(ctx, v.get("today"))],
        ["REV. A", _drawn(ctx)]])
    return c.finish()


# ================================================================== wordclock
def wordclock(ctx, v):
    c = _page()
    rows, cols = v.get("rows", len(v["grid"])), v.get("cols", len(v["grid"][0]))
    _fig(c, ctx, 46, 42, 1, ctx.t("Word grid {r} × {c}", "Wortraster {r} × {c}", r=rows, c=cols), width=370)
    gx, gy = 46, 68
    cw = min(32, 352 // cols)
    ch = min(34, 340 // rows)
    lit = set(tuple(p) for p in v.get("lit") or [])
    L21 = c.line_h("pm400", 21)
    outl = []
    for r, row in enumerate(v["grid"]):
        for k, letter in enumerate(row):
            cx = gx + 2 + k * cw + cw / 2
            top = gy + 2 + r * ch + (ch - L21) / 2
            if (r, k) in lit:
                c.text(cx, top, letter, "pm600", 21, Y, align="c")
            else:
                outl.append((cx, top, letter, "pm400", 21, None, "c"))
    _outline(c, outl, Wh, ring=2, outside=True)
    gw, gh = cols * cw + 4, rows * ch + 4
    c.rect((gx, gy, gx + gw, gy + gh), outline=Wh, width=2)
    _dim(c, 46, 46 + gw, min(gy + gh + 10, 446), v.get("phrase", "").upper())
    # fig 2 – date
    x, x1 = 446, 754
    wd = x1 - x
    y = 42
    _fig(c, ctx, x, y, 2, ctx.t("Date", "Datum"), width=wd)
    y += c.line_h("pm400", 12) + 6
    bh = 90 * 0.9
    s, bw = _big(c, x, y, str(v["day"]), 90, 120)
    tx = x + bw + 16
    tw_ = x1 - tx
    L20, L15, L12 = c.line_h("pm600", 20), c.line_h("pm400", 15), c.line_h("pm400", 12)
    th = L20 + L15 + L12 + 4
    ty = y + (bh - th) / 2
    _line(c, tx, ty, v["weekday"].upper(), "pm600", 20, tw_, fill=Y if v.get("special") else Wh, min_size=12)
    ty += L20 + 2
    _line(c, tx, ty, f"{v['month']} {v['year']}".upper(), "pm400", 15, tw_, track=1, min_size=10)
    ty += L15 + 2
    _line(c, tx, ty, (ctx.t("WK {n}", "KW {n}", n=v["week"]) + " · " +
                      ctx.t("Day {n}", "Tag {n}", n=v["day_of_year"])).upper(), "pm400", 12, tw_, min_size=9)
    # fig 3 – hands & minutes
    y = 166
    _fig(c, ctx, x, y, 3, ctx.t("Hands & minutes", "Zeiger & Minuten"), width=wd)
    y += c.line_h("pm400", 12) + 6
    sc = 100 / 110
    cx, cy = x + 55 * sc, y + 55 * sc
    c.circle(cx, cy, 50 * sc, outline=Wh, width=2)
    for a in range(4):
        ang = math.radians(a * 90)
        c.stroke([(cx + math.sin(ang) * 48 * sc, cy - math.cos(ang) * 48 * sc),
                  (cx + math.sin(ang) * 40 * sc, cy - math.cos(ang) * 40 * sc)], Wh, 2, cap=False)
    hh, mm = v["hour"], v["minute"]
    ha = math.radians((hh % 12 + mm / 60) * 30)
    ma = math.radians(mm * 6)
    c.stroke([(cx, cy), (cx + math.sin(ha) * 28 * sc, cy - math.cos(ha) * 28 * sc)], Wh, 4)
    c.stroke([(cx, cy), (cx + math.sin(ma) * 40 * sc, cy - math.cos(ma) * 40 * sc)], Y, 2, cap=False)
    c.circle(cx, cy, 4 * sc, fill=Wh)
    # minute squares derived from the exact render time
    now = v.get("now")
    extra = 0
    if now is not None:
        extra = max(0, min(4, (now.hour * 60 + now.minute) - (hh * 60 + mm)))
    tx = x + 100 + 22
    L13 = c.line_h("pm400", 13)
    colh = 20 + 8 + L13 + 8 + L20
    ty = cy - colh / 2
    for k in range(4):
        bx = tx + k * 28
        if k < extra:
            c.rect((bx, ty, bx + 20, ty + 20), fill=Y)
        c.rect((bx, ty, bx + 20, ty + 20), outline=Wh, width=2)
    ty += 20 + 8
    t0 = v.get("time", f"{hh:02d}:{mm:02d}")
    c.text(tx, ty, t0, "pm400", 13, Wh)
    if extra:
        _line(c, tx + c.tw(t0 + " ", "pm400", 13), ty, ctx.t("+ {n} min", "+ {n} Min", n=extra).upper(),
              "pm400", 13, x1 - tx - c.tw(t0 + " ", "pm400", 13), fill=Y)
    ty += L13 + 8
    exact = f"{now:%H:%M}" if now is not None else t0
    c.text(tx, ty, f"= {exact}", "pm600", 20, Wh)
    # fig 4 – moon
    y = 306
    _fig(c, ctx, x, y, 4, ctx.t("Moon", "Mond"), width=250)
    y += c.line_h("pm400", 12) + 6
    mx, my = x + 22, y + 22
    ph = v.get("phase", 0)
    if 0.03 < ph < 0.97:
        C.draw_moon(c.d, mx, my, 15, ph, Wh, B, B)
    _dashed_circle(c, mx, my, 17)
    c.vline(mx, y + 1, y + 43, Wh, 1)
    c.hline(x + 1, x + 43, my, Wh, 1)
    L14 = c.line_h("pm400", 14)
    _line(c, x + 58, my - L14 / 2, v.get("moon", "").upper(), "pm400", 14, x1 - x - 58, min_size=9)
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [ctx.t("Grid 5 min", "Raster 5 Min"), _place_cell(ctx, v.get("place"))],
        [_scale(ctx), _drawn(ctx)]])
    return c.finish()


# ================================================================== countdown
def _days(ctx, n):
    return ctx.t("{n} day", "{n} Tag", n=n) if n == 1 else ctx.t("{n} days", "{n} Tage", n=n)


def _weeks(ctx, n):
    return ctx.t("{n} week", "{n} Woche", n=n) if n == 1 else ctx.t("{n} weeks", "{n} Wochen", n=n)


def countdown(ctx, v):
    c = _page()
    state = v.get("state", "future")
    cap = ctx.t("Days left", "Resttage") if state == "future" else (v.get("small") or v.get("title", ""))
    _fig(c, ctx, 46, 42, 1, cap, width=310)
    y = 42 + c.line_h("pm400", 12) + 2
    _big(c, 46, y, v.get("big", str(v.get("count", ""))), 230, 314, min_size=40)
    dim = _days(ctx, v.get("count", 0))
    if v.get("weeks"):
        dim += " · " + _weeks(ctx, v["weeks"])
    _dim(c, 46, 326, 278, dim.upper())
    # fig 2 – target
    x, x1 = 376, 754
    wd = x1 - x
    y = 42
    _fig(c, ctx, x, y, 2, ctx.t("Target", "Zielmarke"), width=wd)
    y += c.line_h("pm400", 12) + 10 + 8
    title = v.get("event") or v.get("title", "")
    size, lines, L, _ = c.fit(title, "pm600", 30, wd, 2 * 36, lh=1.2, min_size=16)
    lines = lines[:2]
    for ln in lines:
        _line(c, x, y, ln, "pm600", size, wd, lh=1.2)
        y += L
    y += 10 + 6
    L12 = c.line_h("pm400", 12)
    for lab, val, vs, col in ((ctx.t("Target", "Ziel"), f"{v.get('target_weekday', '')}, {v.get('date', '')}", 20, Y),
                              (ctx.t("Start", "Start"), f"{v.get('today_weekday', '')}, {v.get('today_text', '')}", 16, Wh)):
        Lv = c.line_h("pm400", vs)
        h = L12 + 4 + Lv
        c.rect((x, y, x + 2, y + h), fill=col)
        _line(c, x + 14, y, lab.upper(), "pm400", 12, wd - 14, track=2)
        _line(c, x + 14, y + L12 + 4, val, "pm400", vs, wd - 14, fill=col, min_size=11)
        y += h + 10
    # fig 3 – day strip
    sx0, sx1 = 46, 496
    y = 316
    _fig(c, ctx, sx0, y, 3, ctx.t("Timeline WK {a}–{b}", "Zeitstrahl KW {a}–{b}",
                                  a=v.get("week_from", ""), b=v.get("week_to", "")), width=sx1 - sx0)
    y += c.line_h("pm400", 12) + 6
    strip = v.get("strip") or []
    cells = []
    if len(strip) > 92:                    # one cell per week
        wk = []
        for e in strip:
            if not wk or e["weekday"] == 0:
                wk.append([])
            wk[-1].append(e)
        for w_ in wk:
            fill = Y if any(e["today"] for e in w_) else R if any(e["target"] for e in w_) else None
            cells.append(fill)
    else:
        for e in strip:
            fill = Y if e["today"] else R if e["target"] else Wh if (e["weekend"] or e["special"]) else None
            cells.append(fill)
    if cells:
        n = len(cells)
        gap = 2 if n <= 60 else 1
        cw = (sx1 - sx0 - gap * (n - 1)) / n
        for i, fill in enumerate(cells):
            a = sx0 + i * (cw + gap)
            box = (round(a), y, max(round(a) + 2, round(a + cw)), y + 30)
            if fill is not None:
                c.rect(box, fill=fill)
            c.rect(box, outline=Wh, width=1)
        y += 30 + 6
        first, last = strip[0], strip[-1]
        mid = strip[len(strip) // 2]
        L11 = c.line_h("pm400", 11)
        lt = numeric_date(first["date"], ctx.lang, year=False)
        rt = numeric_date(last["date"], ctx.lang, year=False)
        c.text(sx0, y, f"▴ {lt}", "pm400", 11, Y if first["today"] else Wh)
        c.text((sx0 + sx1) / 2, y, numeric_date(mid["date"], ctx.lang, year=False), "pm400", 11, Wh, align="c")
        c.text(sx1, y, f"{rt} ▴", "pm400", 11, Y if last["today"] else Wh, align="r")
        y += L11 + 6 + 4
        lx = sx0
        legend = [(Y, ctx.t("Today", "Heute")), (Wh, ctx.t("Weekend", "Wochenende")), (R, v.get("event", ""))]
        for col, lab in legend:
            if not lab:
                continue
            _swatch(c, lx, y + (L11 - 10) / 2, 10, col)
            t = _ell(c, lab.upper(), "pm400", 11, sx1 - lx - 16)
            c.text(lx + 16, y, t, "pm400", 11, Wh)
            lx += 16 + c.tw(t, "pm400", 11) + 16
            if lx > sx1 - 40:
                break
    else:
        c.rect((sx0, y, sx1, y + 30), outline=Wh, width=1)
        c.rect((sx0, y, sx0 + 8, y + 30), fill=Y)
        c.rect((sx1 - 8, y, sx1, y + 30), fill=R)
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [_place_cell(ctx, v.get("place")) if v.get("place") else _scale(ctx), _date_cell(ctx, v.get("today"))],
        ["REV. A", _drawn(ctx)]])
    return c.finish()


# ================================================================== art
def _dims(text):
    """'73.2 × 92.1 cm (…)' -> ('73.2', '92.1') = (height, width) in cm, or None."""
    import re
    m = re.search(r"([\d.,]+)\s*[×xX]\s*([\d.,]+)\s*cm", text or "")
    return (m.group(1), m.group(2)) if m else None


def art(ctx, v):
    c = _page()
    _fig(c, ctx, 46, 42, 1, ctx.t("Picture field", "Bildfeld"), width=400)
    fx0, fy0, fw, fh = 46, 68, 400, 310
    c.rect((fx0, fy0, fx0 + fw, fy0 + fh), outline=Wh, width=2)
    bw, bh = fw - 20, fh - 20
    img = v["image"].convert("RGB")
    sc = min(bw / img.width, bh / img.height)
    iw, ih = max(1, round(img.width * sc)), max(1, round(img.height * sc))
    ix, iy = fx0 + 10 + (bw - iw) // 2, fy0 + 10 + (bh - ih) // 2
    if iw < bw - 4 or ih < bh - 4:        # construction lines in the free part of the field
        c.rect((fx0 + 10, fy0 + 10, fx0 + 10 + bw, fy0 + 10 + bh), outline=Wh, width=1)
    c.img.paste(img.resize((iw, ih), Image.LANCZOS), (ix, iy))
    c.rect((ix - 1, iy - 1, ix + iw + 1, iy + ih + 1), outline=Wh, width=1)
    dm = _dims(v.get("dimensions"))
    if dm:
        htxt, wtxt = dm[0], f"{dm[1]} CM"
    else:
        htxt, wtxt = str(v.get("height", "")), f"{v.get('width', '')} PX"
    _dim(c, 46, 446, 390, wtxt)
    _vdim(c, 456, 68, 378, htxt)
    if v.get("license"):
        _line(c, 46, 416, v["license"].upper(), "pm400", 11, 470, fill=Y)
    # fig 2 – caption
    x, x1 = 506, 754
    wd = x1 - x
    y = 42
    _fig(c, ctx, x, y, 2, ctx.t("Caption", "Beschriftung"), width=wd)
    y += c.line_h("pm400", 12) + 8 + 8
    if v.get("artist"):
        _line(c, x, y, v["artist"], "pm400", 16, wd, track=1, min_size=11)
        y += c.line_h("pm400", 16) + 8
    # space: work title, year numeral, dim + museum must end above the title block (~376)
    date = v.get("date", "")
    L15 = c.line_h("pm400", 15)
    tail = 6 + (72 + 8 if date else 0) + 4 + c.line_h("pm400", 11) + 8 + 2 * L15
    avail = max(34, 372 - y - tail)
    size, lines, L, _ = c.fit(v.get("work", ""), "pm600", 28, wd, avail, lh=1.15, min_size=14)
    if len(lines) * L > avail:
        lines = lines[:max(1, int(avail // L))]
        lines[-1] = _ell(c, lines[-1] + "…", "pm600", size, wd)
    for ln in lines:
        _line(c, x, y, ln, "pm600", size, wd, lh=1.15)
        y += L
    y += 8 + 6
    if date:
        if c.tw(date, "pm300", 40) <= wd:
            _big(c, x, y, date, 80, wd, min_size=40)
            y += 72 + 8
        else:
            _line(c, x, y, date, "pm400", 18, wd, min_size=11)
            y += c.line_h("pm400", 18) + 8
    y += 4
    _dim(c, x, x1, y, ctx.t("Location", "Standort").upper())
    y += c.line_h("pm400", 11) + 8
    _line(c, x, y, v.get("museum", ""), "pm400", 15, wd, min_size=10)
    y += L15
    if v.get("museum_city") and y + L15 < 380:
        _line(c, x, y, v["museum_city"], "pm400", 15, wd, min_size=10)
    dims_short = f"{dm[0]} × {dm[1]} cm" if dm else ""
    r1 = [v.get("medium") or v.get("origin") or _scale(ctx), dims_short or _date_cell(ctx, v.get("today"))]
    r2 = [_date_cell(ctx, v.get("today")) if dims_short else "REV. A", _drawn(ctx)]
    _tb(c, _sheet(ctx, ctx.t("Artwork", "Kunstwerk"), v.get("today")), [r1, r2])
    return c.finish()


# ================================================================== waste
def _bin(c, x, y, col, s=1.0):
    """Wheelie bin of the mockup (70 × 96 viewBox) scaled by s."""
    def P(px, py):
        return (x + px * s, y + py * s)
    rib = K if col in (Y, Wh) else Wh
    sw = max(1, round(2 * s))
    c.rect((*P(4, 6), *P(66, 16)), fill=col)
    c.rect((*P(4, 6), *P(66, 16)), outline=Wh, width=sw)
    c.rect((*P(26, 1), *P(44, 7)), outline=Wh, width=sw)
    c.poly([P(8, 16), P(62, 16), P(57, 84), P(13, 84)], fill=col, outline=Wh, width=sw)
    for a, b in ((24, 25), (35, 35), (46, 45)):
        c.stroke([P(a, 26), P(b, 74)], rib, sw, cap=False)
    for wx in (18, 52):
        cx, cy = P(wx, 88)
        c.circle(cx, cy, 6 * s, fill=B, outline=Wh, width=sw)


def _mini_bin(c, x, y, col):
    c.rect((x + 1, y + 2, x + 19, y + 6), fill=col, outline=Wh)
    c.poly([(x + 3, y + 6), (x + 17, y + 6), (x + 15, y + 23), (x + 5, y + 23)], fill=col, outline=Wh, width=1)


def waste(ctx, v):
    c = _page()
    soon = v.get("soon")
    rows = list(v.get("rows") or [])
    if soon:
        label, dtext, days = soon["label"], soon["date_text"], soon["days"]
        bins = soon["items"]
        names = soon["names_text"]
    else:
        first = rows[0]
        same = [r for r in rows if r["date"] == first["date"]]
        rows = [r for r in rows if r["date"] != first["date"]]
        label, dtext, days = first["in_text"], first["date_text"], first["days"]
        bins = same
        names = " + ".join(r["name"] for r in same)
    _fig(c, ctx, 46, 42, 1, ctx.t("Collection {w}", "Abfuhr {w}", w=label) + " · " + dtext, width=500)
    # big day count (right)
    unit = (ctx.t("day", "Tag") if days == 1 else ctx.t("days", "Tage")).upper()
    uw = c.tw(unit, "pm400", 14)
    bs, bw = _big(c, 754 - uw - 8, 56, str(days), 120, 200, align="r")
    c.text(754, 56 + 108 - 8 - c.line_h("pm400", 14), unit, "pm400", 14, Wh, align="r")
    big_x0 = 754 - uw - 8 - bw
    # bins
    nb = min(len(bins), 3)
    s = 1.0 if nb <= 2 else 0.68
    bx = 46
    for b in bins[:nb]:
        _bin(c, bx, 72, COL.get(b.get("color"), K), s)
        bx += 70 * s + 18 * s
    tx = 246 if nb <= 2 else max(246, bx + 6)
    tw_ = min(340, big_x0 - 16 - tx)
    y = 72
    _line(c, tx, y, label.upper(), "pm400", 14, tw_, fill=Y, track=3, min_size=10)
    y += c.line_h("pm400", 14) + 4
    size, lines, L, _ = c.fit(names, "pm600", 30, tw_, 2 * 36, lh=1.2, min_size=15)
    if len(lines) > 2:
        lines = lines[:2]
        lines[-1] = _ell(c, lines[-1] + "…", "pm600", size, tw_)
    for ln in lines:
        _line(c, tx, y, ln, "pm600", size, tw_, lh=1.2)
        y += L
    if soon and not soon.get("is_today"):
        _line(c, tx, y + 4, ctx.t("Put the bins out tonight", "Tonnen heute Abend rausstellen"), "pm400", 13, tw_, min_size=9)
    # fig 2 – further dates
    x0, x1 = 46, 754
    y = 206
    _fig(c, ctx, x0, y, 2, ctx.t("Further dates", "Weitere Termine"), width=400)
    y += c.line_h("pm400", 12) + 8
    L16 = c.line_h("pm400", 16)
    if not rows:
        c.hline(x0, x1, y, Wh, 1)
        _line(c, x0, y + (36 - L16) / 2, v.get("empty_text", ""), "pm400", 16, x1 - x0, min_size=11)
    for r in rows[:4]:
        c.hline(x0, x1, y, Wh, 1)
        ty = y + (36 - L16) / 2
        _line(c, x0, ty, r["date_text"], "pm600", 16, 110, min_size=11)
        _mini_bin(c, x0 + 124, y + 6, COL.get(r["color"], K))
        wtxt = r["in_text"]
        ws, ww = _line(c, x1, ty, wtxt, "pm400", 16, 150, align="r", min_size=11)
        nx = x0 + 124 + 20 + 14
        nmax = x1 - ww - 14 - 60 - nx
        ns, nw = _line(c, nx, ty, r["name"], "pm400", 16, nmax, min_size=11)
        d0 = max(nx + 150, nx + nw + 14)
        d1 = x1 - ww - 14
        if d1 - d0 > 30:
            _dim(c, d0, d1, y + (36 - c.line_h("pm400", 11)) / 2)
        y += 36
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [_place_cell(ctx, v.get("place")) if v.get("place") else _scale(ctx), _date_cell(ctx, v.get("today"))],
        ["REV. A", _drawn(ctx)]])
    return c.finish()


# ================================================================== warnings
def warnings(ctx, v):
    c = _page()
    x0, w0 = 46, 270
    y = 42
    _fig(c, ctx, x0, y, 1, ctx.t("Warning level", "Warnstufe"), width=w0)
    y += c.line_h("pm400", 12) + 8
    lvl, levels = v.get("level", 1), v.get("levels", 4)
    bh = 130 * 0.85
    ty = y + bh - 90
    tri = Y if v.get("color") == "yellow" or lvl <= 1 else Y
    c.poly([(x0 + 50, ty + 4), (x0 + 96, ty + 86), (x0 + 4, ty + 86)], outline=tri, width=3)
    c.rect((x0 + 46, ty + 32, x0 + 54, ty + 62), fill=tri)
    c.rect((x0 + 46, ty + 68, x0 + 54, ty + 76), fill=tri)
    s, bw = _big(c, x0 + 114, y, str(lvl), 130, 90, lh=0.85)
    L18 = c.line_h("pm400", 18)
    c.text(x0 + 114 + bw + 14, y + bh - 4 - L18, f"/ {levels}", "pm400", 18, Wh)
    y += bh + 14
    gap = 6
    cw = (w0 - gap * (levels - 1)) / levels
    for i in range(levels):
        a = x0 + i * (cw + gap)
        if i < lvl:
            c.rect((a, y, a + cw, y + 22), fill=Y)
        c.rect((a, y, a + cw, y + 22), outline=Wh, width=2)
        c.text(a + cw / 2, y + 25, str(i + 1), "pm400", 11, Wh, align="c")
    # fig 3 – period (onset → expires) with the now mark
    y = 306
    if v.get("onset_text") or v.get("expires_text"):
        _fig(c, ctx, x0, y, 3, ctx.t("Period", "Zeitraum"), width=w0)
        y += c.line_h("pm400", 12) + 8
        ax0, ax1 = x0 + 2, x0 + w0 - 30
        c.hline(ax0, ax1, y + 12, Wh, 2)
        pr = v.get("progress")
        if pr is not None:
            px = ax0 + (ax1 - ax0) * max(0.0, min(1.0, pr))
            c.dashed((ax0, y + 28, max(ax0 + 6, px), y + 28), Wh, 2, 6, 4)
            c.rect((px - 1, y + 4, px + 2, y + 36), fill=Y)
        c.poly([(ax1, y + 2), (ax1 + 28, y + 20), (ax1, y + 38)], fill=Y)
        y += 40 + 8
        span = " – ".join(t for t in (v.get("onset_text", ""), v.get("expires_text", "")) if t)
        _dim(c, x0, x0 + w0, y, span.upper())
        y += c.line_h("pm400", 11) + 8
    if v.get("more_text"):
        _line(c, x0, max(y, 420), v["more_text"], "pm400", 11, w0, fill=Y, min_size=8)
    c.vline(340, 42, 438, Wh, 1)
    # fig 2 – event
    x, x1 = 366, 754
    wd = x1 - x
    y = 42
    _fig(c, ctx, x, y, 2, ctx.t("Event", "Ereignis"), width=wd)
    y += c.line_h("pm400", 12) + 8 + 6
    size, lines, L, _ = c.fit(v.get("event", ""), "pm600", 46, wd, 2 * 46, lh=1.0, min_size=22)
    lines = lines[:2]
    for ln in lines:
        _line(c, x, y, ln, "pm600", size, wd, lh=1.0)
        y += L
    y += 8
    lv = f"{v.get('level_text', '')} · " + ctx.t("Level {n}", "Stufe {n}", n=lvl)
    _line(c, x, y, lv, "pm400", 18, wd, fill=Y, min_size=11)
    y += L18 + 8
    _line(c, x, y, v.get("place_span", ""), "pm400", 15, wd, track=1, min_size=10)
    y += c.line_h("pm400", 15) + 8 + 6
    _dim(c, x, x1, y, ctx.t("Description", "Beschreibung").upper())
    y += c.line_h("pm400", 11) + 8
    desc = v.get("description") or v.get("headline", "")
    if v.get("instruction"):
        desc = (desc + "\n" + v["instruction"]).strip()
    avail = 374 - y
    size, lines, L, _ = c.fit(desc, "pm400", 16, wd, avail, lh=1.45, min_size=11)
    if len(lines) * L > avail + 1:
        size, L = 11, 11 * 1.35
        lines = c.wrap(desc, "pm400", 11, wd)
        n = max(1, int(avail // L))
        if len(lines) > n:
            lines = lines[:n]
            lines[-1] = _ell(c, lines[-1] + "…", "pm400", 11, wd)
    for ln in lines:
        c.text(x, y, ln, "pm400", size, Wh, lh=L / size)
        y += L
    _tb(c, _sheet(ctx, ctx.t("Severe weather", "Unwetter"), v.get("today")), [
        [ctx.t("Source {s}", "Quelle {s}", s=v.get("source", ""))],
        [ctx.t("Updated {t}", "Stand {t}", t=v.get("updated", "")), _drawn(ctx)]])
    return c.finish()


# ================================================================== wifi
def wifi(ctx, v):
    from ..plugins import wifi as wifi_plugin
    c = _page()
    _fig(c, ctx, 46, 42, 1, ctx.t("QR code", "QR-Code"), width=300)
    n = v.get("size") or len(v["modules"])
    qx, qy, qs = 46, 68, 301
    c.rect((qx, qy, qx + qs, qy + qs), fill=Wh)
    inner = qs - 4
    m = max(1, inner // (n + 4))
    quiet = max(2, (inner - n * m) // (2 * m))
    wifi_plugin.draw_modules(c.d, v["modules"], qx + 2, qy + 2, inner, dark=K, light=Wh, quiet=quiet)
    c.rect((qx, qy, qx + qs, qy + qs), outline=Wh, width=2)
    _dim(c, 46, 347, 382, ctx.t("{n} × {n} modules", "{n} × {n} Module", n=n).upper())
    _line(c, 362, 206, "← " + v.get("hint", ""), "pm400", 16, 754 - 362, fill=Y, min_size=10)
    if v.get("note"):
        _line(c, 46, 408, v["note"], "pm400", 13, 470, min_size=10)
    # fig 2 – network
    x, x1 = 396, 754
    wd = x1 - x
    _fig(c, ctx, x, 42, 2, v.get("network_label", ""), width=wd)
    y = 42 + c.line_h("pm400", 12) + 6
    _big(c, x, y, v.get("ssid", ""), 96, wd, lh=0.95, min_size=24)
    # fig 3 – access
    y = 248
    _fig(c, ctx, x, y, 3, ctx.t("Access", "Zugang"), width=wd)
    y += c.line_h("pm400", 12) + 6
    L11 = c.line_h("pm400", 11)
    blocks = []
    if v.get("password"):
        blocks.append((v.get("password_label", ""), v["password"], "pm600", 28, Y))
    sec = v.get("security") or ""
    blocks.append((ctx.t("Encryption", "Verschlüsselung"), sec if sec else ctx.t("Open network", "Offenes Netz"),
                   "pm400", 18, Wh))
    for lab, val, role, size, col in blocks:
        Lv = c.line_h(role, size)
        h = L11 + 2 + Lv
        c.rect((x, y, x + 2, y + h), fill=col)
        _line(c, x + 14, y, lab.upper(), "pm400", 11, wd - 14, track=2)
        _line(c, x + 14, y + L11 + 2, val, role, size, min(wd - 14, 526 - 8 - x - 14) if y + h > 380 else wd - 14,
              fill=col, min_size=12)
        y += h + 6 + 4
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [ctx.t("SSID {s}", "SSID {s}", s=v.get("ssid", "")), ctx.t("Type {t}", "Typ {t}", t=sec or "–")],
        [_scale(ctx), _drawn(ctx)]])
    return c.finish()


# ================================================================== habits
def habits(ctx, v):
    c = _page()
    hs = v.get("habits") or []
    n = max(1, len(hs))
    ncol = max(4, n)
    gx0, gx1, gap = 46, 754, 16
    colw = (gx1 - gx0 - gap * (ncol - 1)) / ncol
    cell = min(18, int((colw - 5 * 4) / 6))
    best_streak = v.get("best_streak", 0)
    now = v.get("now") or [5, 0]
    for k, h in enumerate(hs):
        x = gx0 + k * (colw + gap)
        y = 42
        _fig(c, ctx, x, y, k + 1, ctx.t("Streak", "Serie"), width=colw, track=2 if ncol <= 4 else 1)
        y += c.line_h("pm400", 12) + 6
        size, lines, L, _ = c.fit(h["name"], "pm600", 16, colw, 42, lh=1.3, min_size=11)
        if len(lines) * L > 43:
            lines = lines[:2]
            lines[-1] = _ell(c, lines[-1] + "…", "pm600", size, colw)
        for i, ln in enumerate(lines):
            c.text(x, y + i * L, ln, "pm600", size, Wh, lh=1.3)
        y += 42 + 6
        g = h.get("grid") or []
        for ci, colv in enumerate(g[-6:]):
            for ri, done in enumerate(colv):
                if done is None:
                    continue
                bx, by = x + ci * (cell + 4), y + ri * (cell + 4)
                today = (ci == now[0] and ri == now[1])
                fill = Y if today else Wh if done else None
                if fill is not None:
                    c.rect((bx, by, bx + cell, by + cell), fill=fill)
                c.rect((bx, by, bx + cell, by + cell), outline=Wh, width=2)
        y += 7 * cell + 6 * 4 + 8
        col = Y if h["streak"] and h["streak"] == best_streak else Wh
        bs, bw = _big(c, x, y, str(h["streak"]), 66, colw * 0.55, fill=col, min_size=30)
        lab = [(ctx.t("day", "Tag") if h["streak"] == 1 else ctx.t("days", "Tage")).upper(),
               ctx.t("Streak", "Serie").upper()]
        L13 = 13 * 1.2
        ly = y + 66 * 0.9 - 4 - 2 * L13
        for i, t in enumerate(lab):
            _line(c, x + bw + 8, ly + i * L13, t, "pm400", 13, colw - bw - 8, lh=1.2, min_size=8)
    _dim(c, 46, 496, 352, (_weeks(ctx, v.get("weeks", 6)) + " · " + _days(ctx, v.get("days", 42))).upper())
    y = 382
    L12 = c.line_h("pm400", 12)
    lx = 46
    for fill, lab in ((Wh, ctx.t("Done", "Erledigt")), (None, ctx.t("Open", "Offen")), (Y, ctx.t("Today", "Heute"))):
        if fill is not None:
            c.rect((lx, y + (L12 - 12) / 2, lx + 12, y + (L12 - 12) / 2 + 12), fill=fill)
        c.rect((lx, y + (L12 - 12) / 2, lx + 12, y + (L12 - 12) / 2 + 12), outline=Wh, width=1)
        t = _ell(c, lab.upper(), "pm400", 12, 496 - lx - 18)
        c.text(lx + 18, y, t, "pm400", 12, Wh)
        lx += 18 + c.tw(t, "pm400", 12) + 18
    y += L12 + 6
    _line(c, 46, y, v.get("date_text", "") + " · " + ctx.t("Column = week", "Spalte = Woche"), "pm400", 12, 470, min_size=9)
    best = f"{v.get('best', 0)} {v.get('day_unit', '')}".strip()
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [ctx.t("Best streak {n}", "Beste Serie {n}", n=best), _date_cell(ctx, v.get("today"))],
        ["REV. A", _drawn(ctx)]])
    return c.finish()


# ================================================================== sudoku
def sudoku(ctx, v):
    c = _page()
    _fig(c, ctx, 46, 42, 1, ctx.t("Grid 9 × 9", "Raster 9 × 9"), width=340)
    s = 38
    gx, gy = 46, 66
    x0, y0 = gx + 3, gy + 3
    L22 = c.line_h("pm600", 22)
    for r, row in enumerate(v["grid"]):
        for k, val in enumerate(row):
            if val:
                c.text(x0 + k * s + s / 2, y0 + r * s + (s - L22) / 2, str(val), "pm600", 22, Wh, align="c")
    for i in range(1, 9):
        w = 3 if i % 3 == 0 else 1
        c.vline(x0 + i * s - w, y0, y0 + 9 * s, Wh, w)
        c.hline(x0, x0 + 9 * s, y0 + i * s - w, Wh, w)
    c.rect((gx, gy, x0 + 9 * s + 3, y0 + 9 * s + 3), outline=Wh, width=3)
    _dim(c, 46, 394, 426, ctx.t("3 × 3 blocks", "3 × 3 Blöcke").upper())
    # fig 2 – level
    x, x1 = 446, 754
    wd = x1 - x
    y = 42
    _fig(c, ctx, x, y, 2, v.get("name", ""), width=wd)
    y += c.line_h("pm400", 12) + 6 + 6
    mx = v.get("level_max", 3)
    dots_w = mx * 18 + (mx - 1) * 6
    L30 = c.line_h("pm600", 30)
    ls, lw = _line(c, x, y, v.get("level_name", ""), "pm600", 30, wd - dots_w - 14, min_size=16)
    dx = x + lw + 14
    for i in range(mx):
        cx = dx + i * 24 + 9
        cy = y + L30 / 2
        c.circle(cx, cy, 9, fill=Y if i < v.get("level_no", 1) else None, outline=Wh, width=2)
    y += L30 + 6
    _line(c, x, y, ctx.t("Difficulty {a} of {b}", "Schwierigkeit {a} von {b}", a=v.get("level_no", 1), b=mx).upper(),
          "pm400", 12, wd, track=1, min_size=9)
    # fig 3 – givens
    y = 166
    _fig(c, ctx, x, y, 3, ctx.t("Givens", "Vorgaben"), width=wd)
    y += c.line_h("pm400", 12) + 6
    bs, bw = _big(c, x, y, str(v.get("givens", "")), 110, 150)
    tx = x + bw + 12
    lab = ctx.t("digits given", "Zahlen vorgegeben").upper()
    size, lines, L, _ = c.fit(lab, "pm400", 14, x1 - tx, 3 * 14 * 1.3, lh=1.3, min_size=9)
    lines = lines[:3]
    ly = y + 99 - 6 - len(lines) * L
    for i, ln in enumerate(lines):
        _line(c, tx, ly + i * L, ln, "pm400", size, x1 - tx, lh=1.3)
    y += 99 + 6 + 4
    _dim(c, x, x1, y, ctx.t("{n} cells empty", "{n} Felder frei", n=v.get("empty", "")).upper())
    y += c.line_h("pm400", 11) + 6 + 6
    _line(c, x, y, v.get("hint", ""), "pm400", 16, wd, fill=Y, min_size=10)
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [ctx.t("Level {n}", "Stufe {n}", n=v.get("level_name", "")), _date_cell(ctx, v.get("today"))],
        ["REV. A", _drawn(ctx)]])
    return c.finish()


# ================================================================== solar
def solar(ctx, v):
    c = _page()
    _fig(c, ctx, 46, 42, 1, ctx.t("Output now", "Leistung jetzt"), width=360)
    y = 42 + c.line_h("pm400", 12) + 2
    bh = 140 * 0.9
    L30 = c.line_h("pm400", 30)
    uw = c.tw("W", "pm400", 30)
    bs, bw = _big(c, 46, y, str(v.get("power_w", "")), 140, 360 - uw - 10)
    c.text(46 + bw + 10, y + bh - 10 - L30, "W", "pm400", 30, Wh)
    # fig 2 – balance
    x, x1 = 436, 736
    y = 42
    _fig(c, ctx, x, y, 2, ctx.t("Balance", "Bilanz"), width=x1 - x)
    y += c.line_h("pm400", 12) + 8
    rows = [(ctx.t("Today", "Heute"), v.get("today_text", ""), "pm600", 24, Wh),
            (ctx.t("Saved", "Gespart"), "≈ " + v.get("saved_text", ""), "pm600", 24, Y)]
    if v.get("total_text"):
        rows.append((ctx.t("Total", "Gesamt"), v["total_text"], "pm400", 16, Wh))
    for i, (lab, val, role, size, col) in enumerate(rows):
        Lv = c.line_h(role, size)
        base = c._baseline(y, role, size, None)
        lt = base - c._baseline(0, "pm400", 12, None)
        vs, vw = _line(c, x1, y, val, role, size, 200, fill=col, align="r", min_size=12)
        _line(c, x, lt, lab.upper(), "pm400", 12, x1 - x - vw - 10, track=1, min_size=8)
        y += Lv
        if i < len(rows) - 1:
            y += 4
            c.hline(x, x1, y, Wh, 1)
            y += 8
    # fig 3 – curve
    t0, t1 = v.get("t0", 5), v.get("t1", 22)
    y = 212
    _fig(c, ctx, 46, y, 3, ctx.t("Generation {a}–{b} h", "Erzeugung {a}–{b} h", a=f"{t0:02d}", b=f"{t1:02d}"), width=470)
    y += c.line_h("pm400", 12) + 6
    cx0, cy0, cw, ch = 82, y, 430, 150
    peak = v.get("peak") or 1

    def py(p):
        return cy0 + ch - 4 - max(0.0, min(p, peak)) / peak * (ch - 14)

    def px(t):
        return cx0 + (t - t0) / (t1 - t0) * cw
    L11 = c.line_h("pm400", 11)
    for val, yy in ((peak, cy0), (peak / 2, cy0 + ch / 2 - L11 / 2), (0, cy0 + ch - L11)):
        c.text(cx0 - 6, yy, f"{val:.0f}", "pm400", 11, Wh, align="r")
    c.dashed((cx0, py(peak), cx0 + cw, py(peak)), Wh, 1, 3, 5)
    c.dashed((cx0, py(peak / 2), cx0 + cw, py(peak / 2)), Wh, 1, 3, 5)
    c.hline(cx0, cx0 + cw, cy0 + ch - 2, Wh, 2)
    c.vline(cx0, cy0, cy0 + ch, Wh, 2)
    pts = [(px(h), py(w)) for h, w in zip(v.get("hours") or [], v.get("watts") or []) if t0 <= h <= t1]
    if len(pts) >= 2:
        c.stroke(pts, Wh, 3)
    if v.get("now_visible"):
        nx = px(v["now"])
        c.vline(nx - 1, cy0, cy0 + ch, Y, 2)
        c.circle(nx, py(v.get("power", 0)), 6, fill=Y, outline=Wh, width=2)
    for t, lab in zip(v.get("ticks") or [], v.get("tick_labels") or []):
        c.text(px(t), cy0 + ch + 6, lab, "pm400", 11, Wh, align="c")
    # fig 4 – sun
    sx = 651
    _fig(c, ctx, sx, 196, 4, ctx.t("Sun", "Sonne"), width=180, align="c")
    sy = 196 + c.line_h("pm400", 12) + 6
    scx, scy = sx, sy + 75
    _dashed_circle(c, scx, scy, 46, width=1, seg=24)
    c.circle(scx, scy, 34, fill=Y, outline=Wh, width=2)
    for a in range(8):
        ang = math.radians(a * 45)
        r0, r1 = (53, 71) if a % 2 == 0 else (54, 71)
        if a % 2:
            r0, r1 = 53, 70
        c.stroke([(scx + math.sin(ang) * r0, scy - math.cos(ang) * r0),
                  (scx + math.sin(ang) * r1, scy - math.cos(ang) * r1)], Wh, 3, cap=False)
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [_place_cell(ctx, v.get("place")) if v.get("place") else _scale(ctx),
         v.get("footer") or ctx.t("Updated {t}", "Stand {t}", t=v.get("now_text", ""))],
        [ctx.t("Peak {p}", "Peak {p}", p=v.get("peak_text", "")), _drawn(ctx)]])
    return c.finish()


# ================================================================== waterlevel
def _nice_range(lo0, hi0):
    span = max(hi0 - lo0, 1.0)
    mag = 10 ** math.floor(math.log10(span / 3))
    step = mag
    for f in (1, 2, 2.5, 5, 10):
        if span / (f * mag) <= 4:
            step = f * mag
            break
    return math.floor(lo0 / step) * step, math.ceil(hi0 / step) * step, step


def waterlevel(ctx, v):
    c = _page()
    x0, w0 = 46, 270
    y = 42
    cap = " · ".join(t for t in (v.get("station", ""), v.get("water", "")) if t)
    _fig(c, ctx, x0, y, 1, cap, width=w0 + 10)
    y += c.line_h("pm400", 12) + 4
    unit = v.get("unit", "cm")
    L22 = c.line_h("pm400", 22)
    uw = c.tw(unit, "pm400", 22)
    bh = 120 * 0.9
    bs, bw = _big(c, x0, y, v.get("value_num", "–"), 120, w0 - uw - 8)
    c.text(x0 + bw + 8, y + bh - 8 - L22, unit, "pm400", 22, Wh)
    y += bh + 4 + 6
    if v.get("state_text"):
        _line(c, x0, y, v["state_text"], "pm600", 22, w0, fill=R if v.get("high") else Wh, min_size=12)
        y += c.line_h("pm600", 22) + 4
    tr = " ".join(t for t in (v.get("trend_arrow", ""), v.get("trend_text", "")) if t)
    if v.get("change_24h_text"):
        tr = (tr + " " if tr else "") + f"{v['change_24h_text']}/24 h"
    if tr:
        _line(c, x0, y, tr, "pm400", 15, w0, fill=Y, min_size=10)
    # fig 3 – key values
    y = 268
    refs = list(v.get("refs") or [])
    _fig(c, ctx, x0, y, 3, ctx.t("Key values", "Kennwerte"), width=w0)
    y += c.line_h("pm400", 12) + 8
    rows = [(r["key"], r["text"][len(r["key"]):].strip() or str(r["value"]), Wh) for r in refs]
    if v.get("to_hsw_text"):
        rows.append((ctx.t("To HSW", "Bis HSW").upper(), v["to_hsw_text"], Y))
    L14 = c.line_h("pm400", 14)
    for k, val, col in rows[:4]:
        c.hline(x0, x0 + w0, y, Wh, 1)
        vs, vw = _line(c, x0 + w0, y + 5, val, "pm400", 14, 120, fill=col, align="r")
        _line(c, x0, y + 5, k, "pm400", 14, w0 - vw - 10, min_size=9)
        y += 10 + L14
    if rows:
        c.hline(x0, x0 + w0, y, Wh, 1)
    # fig 2 – hydrograph
    gx0 = 356
    y = 42
    _fig(c, ctx, gx0, y, 2, ctx.t("Hydrograph {n} days", "Ganglinie {n} Tage", n=v.get("days", 7)), width=754 - gx0)
    cx0, cy0, cw, ch = 396, y + c.line_h("pm400", 12) + 6, 356, 250
    vals = v.get("values") or []
    xs = v.get("x") or []
    mw, hsw = v.get("mw"), v.get("hsw")
    lo0 = min(vals + ([mw] if mw is not None else [])) if vals else (mw or 0)
    hi0 = max(vals + [r for r in (mw, hsw) if r is not None]) if vals else (hsw or mw or 100)
    lo, hi, step = _nice_range(lo0, hi0)
    if hi <= lo:
        hi = lo + step

    def py(val):
        return cy0 + ch - (val - lo) / (hi - lo) * ch

    def px(f):
        return cx0 + 4 + f * (cw - 12)
    L11 = c.line_h("pm400", 11)
    t = lo
    while t <= hi + 1e-6:
        yy = min(max(cy0, py(t) - L11 / 2), cy0 + ch - L11)
        c.text(cx0 - 6, yy, f"{t:g}", "pm400", 11, Wh, align="r")
        t += step
    c.vline(cx0, cy0, cy0 + ch, Wh, 2)
    c.hline(cx0, cx0 + cw, cy0 + ch - 2, Wh, 2)
    L12 = c.line_h("pm400", 12)
    if hsw is not None and lo <= hsw <= hi:
        c.hline(cx0, cx0 + cw, py(hsw) - 1, R, 3)
        c.text(cx0 + cw - 6, max(cy0, py(hsw) - 8 - L12), v.get("hsw_text") and f"HSW {v['hsw_text']}" or "HSW",
               "pm400", 12, Wh, align="r")
    if mw is not None and lo <= mw <= hi:
        c.dashed((cx0, py(mw), cx0 + cw, py(mw)), Wh, 1, 6, 4)
        c.text(cx0 + cw - 6, min(py(mw) + 5, cy0 + ch - L12 - 3), f"MW {v.get('mw_text', '')}".strip(), "pm400", 12, Wh,
               align="r")
    if len(vals) >= 2 and len(xs) == len(vals):
        pts = [(px(f), py(val)) for f, val in zip(xs, vals)]
        c.stroke(pts, Wh, 3)
        c.circle(pts[-1][0], pts[-1][1], 6, fill=Y, outline=Wh, width=2)
    hours = max(1, v.get("hours") or 24 * v.get("days", 7))
    dayf = 24 / hours
    for tk in v.get("day_ticks") or []:
        cxm = tk["x"] + dayf / 2
        if cxm <= 1:
            c.text(px(cxm), cy0 + ch + 6, tk.get("weekday", ""), "pm400", 11, Wh, align="c")
    _dim(c, 396, 736, 346, f"{v.get('hours', '')} H")
    _tb(c, _sheet(ctx, v.get("name", ""), v.get("today")), [
        [ctx.t("Source {s}", "Quelle {s}", s=v.get("source", ""))],
        [ctx.t("Updated {t}", "Stand {t}", t=v.get("now_text", "")), _drawn(ctx)]])
    return c.finish()


# ================================================================== birthdays
def birthdays(ctx, v):
    if v.get("festive"):
        return None                         # the plugin's own festive screen
    c = _page()
    p = v["first"]
    x0 = 46
    y = 42
    _fig(c, ctx, x0, y, 1, ctx.t("Next birthday", "Nächster Geburtstag"), width=400)
    y += c.line_h("pm400", 12) + 4
    when = p.get("when", "").upper()
    ww = c.tw(when, "pm400", 13, 2) - 2
    bs, bw = _big(c, x0, y, str(p["days"]), 190, 170, fill=Y, min_size=60)
    colw = max(bw, min(ww, 200))
    _line(c, x0 + colw / 2, y + 171, when, "pm400", 13, 200, track=2, align="c", min_size=9)
    tx = x0 + colw + 20
    tw_ = 436 - tx
    ty = y + 22
    size, lines, L, _ = c.fit(p["name"], "pm600", 46, tw_, 2 * 46, lh=1.0, min_size=18)
    lines = lines[:2]
    for ln in lines:
        _line(c, tx, ty, ln, "pm600", size, tw_, lh=1.0)
        ty += L
    ty += 6
    if p.get("age_text"):
        _line(c, tx, ty, p["age_text"], "pm400", 24, tw_, fill=Y, min_size=12)
        ty += c.line_h("pm400", 24) + 6
    ty += 6
    _dim(c, tx, tx + min(210, tw_), ty, ctx.t("Date", "Datum").upper())
    ty += c.line_h("pm400", 11) + 2 + 6
    _line(c, tx, ty, p.get("date_long", ""), "pm400", 16, tw_, min_size=10)
    # fig 2 – preview
    x, x1 = 476, 754
    wd = x1 - x
    y = 42
    _fig(c, ctx, x, y, 2, ctx.t("Preview", "Vorschau"), width=wd)
    y += c.line_h("pm400", 12) + 8
    L18, L13 = c.line_h("pm600", 18), c.line_h("pm400", 13)
    for o in (v.get("others") or [])[:4]:
        c.hline(x, x1, y, Wh, 1)
        yy = y + 7
        ds, dw = _line(c, x1, yy + (L18 - c.line_h("pm400", 14)), o.get("date_short", ""), "pm400", 14, 110, align="r")
        _line(c, x, yy, o["name"], "pm600", 18, wd - dw - 10, min_size=11)
        yy += L18 + 2
        ws, wdw = _line(c, x1, yy, o.get("when", ""), "pm400", 13, 140, fill=Y, align="r")
        _line(c, x, yy, o.get("age_text") or "–", "pm400", 13, wd - wdw - 10, min_size=9)
        y = yy + L13 + 7
    # fig 3 – 60 day axis
    ax0, ax1 = 46, 496
    y = 316
    _fig(c, ctx, ax0, y, 3, ctx.t("Timeline {n} days", "Zeitachse {n} Tage", n=60), width=ax1 - ax0)
    y += c.line_h("pm400", 12) + 6
    c.hline(ax0, ax1, y + 26, Wh, 2)
    c.vline(ax0, y + 16, y + 38, Wh, 2)
    c.vline(ax1 - 2, y + 16, y + 38, Wh, 2)
    L11 = c.line_h("pm400", 11)
    last_lab = -999
    marks = [q for q in v.get("people") or [] if q["days"] <= 60]
    for i, q in enumerate(marks):
        mx = ax0 + 1 + (ax1 - ax0 - 2) * q["days"] / 60
        mx = min(max(mx, ax0 + 8), ax1 - 8)
        c.diamond(mx, y + 27, 12, Wh)
        c.diamond(mx, y + 27, 7, Y if i == 0 else B)
        if mx - last_lab >= 62:
            nm = _ell(c, q["name"], "pm400", 11, 60)
            lx = min(max(mx, ax0 + c.tw(nm, "pm400", 11) / 2), ax1 - c.tw(nm, "pm400", 11) / 2)
            c.text(lx, y, nm, "pm400", 11, Wh, align="c")
            ds = q.get("date_short", "")
            lx = min(max(mx, ax0 + c.tw(ds, "pm400", 11) / 2), ax1 - c.tw(ds, "pm400", 11) / 2)
            c.text(lx, y + 40, ds, "pm400", 11, Wh, align="c")
            last_lab = mx
    y += 70 + 6
    c.text(ax0, y, ctx.t("Today {d}", "Heute {d}", d=v.get("date_short", "")).upper(), "pm400", 11, Wh)
    c.text(ax1, y, ctx.t("+{n} d", "+{n} T", n=60).upper(), "pm400", 11, Wh, align="r")
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [ctx.t("{n} dates", "{n} Termine", n=v.get("count", 0)), _date_cell(ctx, v.get("today"))],
        ["REV. A", _drawn(ctx)]])
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    from ..plugins import watchlist as wl
    c = _page()
    days = v.get("days", 30)
    _, rw = _fig(c, ctx, 754, 42, 2, ctx.t("Trend {n} days", "Verlauf {n} Tage", n=days), width=300, align="r")
    _fig(c, ctx, 46, 42, 1, ctx.t("Exchange · last close", "Börse · letzter Schlusskurs"), width=708 - rw - 20)
    items = (v.get("items") or [])[:6]
    n = max(1, len(items))
    rh = min(72, (356 - 68) / n)
    sh = min(52, rh - 14)
    y = 68
    for it in items:
        c.hline(46, 754, y, Wh, 1)
        cy = y + rh / 2
        ok = it.get("ok")
        col = COL.get(it.get("color"), K) if ok else K
        L18, L11 = c.line_h("pm600", 18), c.line_h("pm400", 11)
        sub = (_days(ctx, days) + " " + it.get("period_text", "")) if ok else (it.get("error") or "")
        hh = L18 + (2 + L11 if sub and rh >= 44 else 0)
        _line(c, 46, cy - hh / 2, it["label"], "pm600", 18 if rh >= 44 else 15, 190, min_size=10)
        if sub and rh >= 44:
            _line(c, 46, cy - hh / 2 + L18 + 2, sub.upper(), "pm400", 11, 190, track=2 if ok else 0, min_size=7,
                  fill=Wh if ok else R)
        L24 = c.line_h("pm400", 24)
        _line(c, 402, cy - L24 / 2, it.get("last_text", "–") if ok else "–", "pm400", 24 if rh >= 44 else 18, 150,
              align="r", min_size=10)
        if ok:
            bh = min(30, rh - 10)
            c.rect((418, cy - bh / 2, 518, cy + bh / 2), fill=col)
            c.rect((418, cy - bh / 2, 518, cy + bh / 2), outline=Wh, width=2)
            L15 = c.line_h("pm600", 15)
            _line(c, 468, cy - L15 / 2, it.get("change_text", ""), "pm600", 15, 92, align="c", min_size=9)
            sx, sy = 534, cy - sh / 2
            c.rect((sx, sy, sx + 220, sy + sh), fill=Wh)
            pts = wl.spark_points(it.get("values") or [], sx + 7, sy + 7, 220 - 14, sh - 14)
            if len(pts) >= 2:
                c.stroke(pts, col, 3)
                c.circle(pts[-1][0], pts[-1][1], 4, fill=col)
        y += rh
    c.hline(46, 754, y, Wh, 1)
    _dim(c, 534, 754, max(y + 8, 364) if y + 8 + 14 < 382 else y + 4, _days(ctx, days).upper())
    yb = 388
    _line(c, 46, yb, v.get("footer", ""), "pm400", 13, 470, min_size=9)
    yb += c.line_h("pm400", 13) + 4
    lx = 46
    for tri, lab in (("▲", ctx.t("green rising", "grün steigend")), ("▼", ctx.t("red falling", "rot fallend"))):
        c.text(lx, yb, tri, "pm400", 11, Y)
        lx += c.tw(tri + " ", "pm400", 11)
        t = _ell(c, lab.upper(), "pm400", 11, 230)
        c.text(lx, yb, t, "pm400", 11, Wh, track=1)
        lx += c.tw(t, "pm400", 11, 1) + 16
    _tb(c, _sheet(ctx, v.get("title", ""), v.get("today")), [
        [ctx.t("{n} values", "{n} Werte", n=v.get("count", len(items))), _date_cell(ctx, v.get("today"))],
        ["REV. A", _drawn(ctx)]])
    return c.finish()
