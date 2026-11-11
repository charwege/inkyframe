"""Art déco signature layouts (ports of mockups/project/Deco-*.dc.html).

Frame: 14 px margin, 2 px gold rule, 6 px gap, 1 px gold rule – inner box 23…777 × 23…457.
Fonts: lime = Limelight (display numbers), poiret = Poiret One (texts), jos = Josefin Sans (labels).
"""
import math

from ..designs import _deco_frame, _ornament, _sunburst, roman
from ..studio import B, G, K, R, Y, Canvas, Wh

COL = {"green": G, "yellow": Y, "red": R, "blue": B, "black": K, "white": Wh}
X0, Y0, X1, Y1 = 23, 23, 777, 457


# ------------------------------------------------------------------ helpers
def _new():
    c = Canvas("deco", K)
    _deco_frame(c)
    return c


def _fit1(c, text, role, size, width, track=0.0, min_size=9):
    """Shrink letter-spacing first, then size, until one line fits; returns (size, track, text)."""
    tr = track
    while c.tw(text, role, size, tr) - tr > width:
        if tr > 1:
            tr = max(1, tr - 1)
        elif size > min_size:
            size -= 1
        else:
            break
    if c.tw(text, role, size, tr) - tr > width:
        text = _ellip(c, text, role, size, width, tr)
    return size, tr, text


def _ellip(c, text, role, size, width, tr=0.0):
    if c.tw(text, role, size, tr) - tr <= width:
        return text
    while text and c.tw(text + "…", role, size, tr) - tr > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _lab(c, x, top, text, size, track, width, col=Y, align="c", role="jos", upper=True):
    """A spaced caps label that never overflows `width`. Returns the line height."""
    if upper:
        text = text.upper()
    s, tr, text = _fit1(c, text, role, size, width, track)
    c.text(x, top, text, role, s, col, track=tr, align=align)
    return c.line_h(role, size)


def _fitpara(c, text, role, max_size, width, height, lh=1.2, min_size=12, max_lines=None, track=0.0):
    """c.fit + ellipsis on the last line if it still does not fit."""
    size, lines, L, tr = c.fit(text, role, max_size, width, height, lh=lh, min_size=min_size, track=track)
    n = max(1, int((height + 0.5) // L))
    if max_lines:
        n = min(n, max_lines)
    if len(lines) > n:
        lines = lines[:n]
        lines[-1] = _ellip(c, lines[-1] + " …", role, size, width, tr) if not lines[-1].endswith("…") else lines[-1]
    lines = [_ellip(c, l, role, size, width, tr) for l in lines]
    return size, lines, L, tr


def _dia(c, cx, cy, s, fill=None, outline=None, width=1):
    """Square of side s rotated 45° (CSS rotate(45deg))."""
    h = s * math.sqrt(2) / 2
    pts = [(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)]
    if fill is not None:
        c.poly(pts, fill=fill)
    if outline is not None:
        for k in range(width):
            hh = h - k
            c.poly([(cx, cy - hh), (cx + hh, cy), (cx, cy + hh), (cx - hh, cy)], outline=outline)


def _orn(c, cx, cy, arm, gap, dcol=Y, ds=8):
    """Line – diamond – line ornament: arm = line length, gap = space between line and diamond box."""
    c.hline(cx - ds / 2 - gap - arm, cx - ds / 2 - gap, cy, Y, 1)
    c.hline(cx + ds / 2 + gap, cx + ds / 2 + gap + arm, cy, Y, 1)
    _dia(c, cx, cy + .5, ds, dcol)


def _dbox(c, box, pad=5):
    """Double gold box: 2 px outer border, `pad` gap, 1 px inner border. Returns the inner content box."""
    x0, y0, x1, y1 = box
    c.rect(box, outline=Y, width=2)
    c.rect((x0 + 2 + pad, y0 + 2 + pad, x1 - 2 - pad, y1 - 2 - pad), outline=Y, width=1)
    return (x0 + 3 + pad, y0 + 3 + pad, x1 - 3 - pad, y1 - 3 - pad)


def _rdate(d):
    return f"{roman(d.day)} · {roman(d.month)} · {roman(d.year)}"


def _rtime(h, m):
    return f"{roman(h) or 'N'}:{roman(m) or 'N'}"


def _bl(c, role, size):
    """Distance from the top of a 'normal' line box to its baseline."""
    return c._baseline(0, role, size, None)


def _lh(c, role, size):
    return c.line_h(role, size)


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = _new()
    S = 44
    bx, by = 61, 49                     # outer edge of the board's double border
    c.rect((bx, by, bx + 364, by + 364), outline=Y, width=2)
    c.rect((bx + 5, by + 5, bx + 359, by + 359), outline=Y, width=1)
    gx, gy = bx + 6, by + 6
    last = set(map(tuple, v.get("last_cells") or []))
    for r, row in enumerate(v["board"]):
        for k, p in enumerate(row):
            x, y = gx + k * S, gy + r * S
            bg = Y if (r + k) % 2 else Wh
            c.rect((x, y, x + S, y + S), fill=bg)
            if (r, k) in last:
                c.rect((x, y, x + S, y + S), outline=R, width=3)
            chess_puzzle.draw_piece(c.d, p, x + S // 2, y + S // 2, S - 6, ink=K, paper=Wh)
    if v.get("show_coords", True):
        for i, n in enumerate(v["ranks"]):
            c.text(48, gy + i * S + (S - _lh(c, "jos", 12)) / 2 + 1, n, "jos", 12, Y, align="c")
        for i, f in enumerate(v["files"]):
            c.text(gx + i * S + S / 2, by + 364 + 4, f, "jos", 12, Y, align="c")

    CX, W = 603, 300
    top, bot = 35, 445
    _sunburst(c, CX, top + 50, 100, 48, 10, 18)
    y = top + 50 + 9
    y += _lab(c, CX, y, v["title"], 14, 7, W) + 9
    _orn(c, CX, y + 4, 70, 10, R)
    y += 8 + 9 + 4
    side = v["to_move"]
    s, tr, side = _fit1(c, side, "poiret", 26, W - 30, 1, 14)
    sw = c.tw(side, "poiret", s, tr) - tr
    sx = CX - (sw + 24) / 2
    sh = _lh(c, "poiret", 26)
    _dia(c, sx + 6, y + sh / 2, 12, fill=Wh if v["white_to_move"] else K, outline=Wh, width=2)
    c.text(sx + 24, y + (sh - _lh(c, "poiret", s)) / 2, side, "poiret", s, Wh, track=tr)
    y += sh + 9
    big = v.get("mate") or (v["themes"][0] if v.get("themes") else v.get("source", ""))
    rest = [t for t in v.get("themes", []) if t != big]
    bs = 50
    while bs > 24 and c.tw(big, "lime", bs) > W:
        bs -= 1
    big = _ellip(c, big, "lime", bs, W)
    c.text(CX, y + (50 - bs) / 2, big, "lime", bs, Wh, lh=1, align="c")
    y += 50 + 9
    if rest:
        y += _lab(c, CX, y, " · ".join(rest), 19, 1, W, Y, role="poiret", upper=False)
    y += 9 + 6
    # rating | solution table
    cells = []
    if v.get("rating"):
        cells.append((ctx.t("Rating", "Wertung"), str(v["rating"])))
    cells.append((ctx.t("Solution", "Lösung"),
                  ctx.t("{n} moves", "{n} Züge", n=v["moves"]) if v["moves"] != 1 else ctx.t("{n} move", "{n} Zug", n=1)))
    th = 7 + _lh(c, "jos", 11) + 3 + _lh(c, "poiret", 24) + 7
    x0, x1 = CX - 152, CX + 152
    c.hline(x0, x1, y, Y)
    c.hline(x0, x1, y + th + 1, Y)
    cw = (x1 - x0) / len(cells)
    for i, (a, b) in enumerate(cells):
        cx = x0 + cw * i + cw / 2
        if i:
            c.vline(x0 + cw * i - 1, y, y + th + 1, Y)
        _lab(c, cx, y + 1 + 7, a, 11, 4, cw - 8)
        _lab(c, cx, y + 1 + 7 + _lh(c, "jos", 11) + 3, b, 24, 0, cw - 10, Wh, role="poiret", upper=False)
    fy = bot - _lh(c, "jos", 13)
    _lab(c, CX, fy, _rdate(v["today"]), 13, 8, W)
    _lab(c, CX, fy - 9 - _lh(c, "jos", 12), v["hint"], 12, 4, W)
    return c.finish()


# ================================================================== spotify
def _record_art(c, x, y):
    """The mockup's sunburst-and-record stand-in when there is no cover."""
    c.rect((x, y, x + 360, y + 360), fill=B)
    n = 16
    for i in range(0, n, 2):
        a1 = math.pi + i / n * math.pi
        a2 = math.pi + (i + 1) / n * math.pi
        c.poly([(x + 180, y + 250), (x + 180 + math.cos(a1) * 320, y + 250 + math.sin(a1) * 320),
                (x + 180 + math.cos(a2) * 320, y + 250 + math.sin(a2) * 320)], fill=Y)
    c.circle(x + 180, y + 250, 84, fill=K)
    c.circle(x + 180, y + 250, 78, fill=Wh)
    c.circle(x + 180, y + 250, 74, fill=R)
    c.circle(x + 180, y + 250, 54, outline=K, width=2)
    c.circle(x + 180, y + 250, 34, outline=K, width=2)
    c.rect((x, y + 250, x + 360, y + 360), fill=K)
    for k, (a, b) in enumerate(((0, 360), (40, 320), (80, 280), (120, 240), (160, 200))):
        c.rect((x + a, y + 249 + 22 * k, x + b, y + 252 + 22 * k), fill=Y)
    c.poly([(x + 180, y + 268), (x + 188, y + 276), (x + 180, y + 284), (x + 172, y + 276)], fill=Wh)


def spotify(ctx, v):
    c = _new()
    bx, by = 45, 52
    c.rect((bx, by, bx + 376, by + 376), outline=Y, width=2)
    c.rect((bx + 7, by + 7, bx + 369, by + 369), outline=Y, width=1)
    ix, iy = bx + 8, by + 8
    if v.get("image") is not None:
        c.img.paste(ctx.punch(ctx.cover_fit(v["image"], 360, 360)), (ix, iy))
    else:
        _record_art(c, ix, iy)

    x0, x1 = 451, 755
    W = x1 - x0
    y = 45
    y += _lab(c, x0, y, v["label"], 14, 8, W, align="l") + 10
    _dia(c, x0 + 4, y + 4, 8, R)
    c.hline(x0 + 14, x1, y + 4, Y)
    y += 8 + 10 + 8
    # bottom block first (rule, duration, footer) so the texts know their room
    fh = _lh(c, "jos", 13)
    fy = 435 - fh
    c.hline(x0, x1, fy - 11, Y)
    _lab(c, x0, fy, v.get("source") or "Spotify", 13, 8, W / 2, align="l")
    now = v["now"]
    _lab(c, x1, fy, _rtime(now.hour, now.minute), 13, 5, W / 2 - 10, align="r")
    dur_y = fy - 11 - 4 - 10 - _lh(c, "poiret", 22)
    if v.get("duration_text"):
        c.text(x1, dur_y + 2, v["duration_text"], "jos", 20, Wh, align="r")
    ry = dur_y - 10 - 18
    c.hline(x0, x1, ry + 8, Y)
    _dia(c, x0 + 6, ry + 8.5, 9, Wh, outline=K, width=2)
    _dia(c, x1 - 6, ry + 8.5, 9, Wh, outline=K, width=2)
    _dia(c, (x0 + x1) / 2, ry + 8.5, 9, Y)
    room = ry - 10 - y
    # track / artist / album
    art_h = _lh(c, "lime", 26) * 0 + 26 * 1.1
    alb = v.get("album", "")
    alb_h = _lh(c, "jos", 14) if alb else 0
    text_room = room - (4 + art_h + 10 if v.get("artist") else 0) - (alb_h + 10 if alb else 0)
    size, lines, L, tr = _fitpara(c, v["track"], "poiret", 31, W, max(40, text_room), lh=1.2, min_size=18, max_lines=4)
    c.para(x0, y, W, lines, "poiret", size, L, Wh)
    y += len(lines) * L
    if v.get("artist"):
        y += 4
        s, tr2, t = _fit1(c, v["artist"], "lime", 26, W, 0, 15)
        c.text(x0, y, t, "lime", s, Y, lh=1.1 * 26 / s)
        y += art_h + 10
    if alb:
        _lab(c, x0, y, alb, 14, 4, W, align="l")
    return c.finish()


# ================================================================== grid (Stromampel)
def grid(ctx, v):
    c = _new()
    L0, R0, T0, B0 = 51, 749, 41, 441
    W = R0 - L0
    # traffic light
    lx, ly = L0, T0
    _dbox(c, (lx, ly, lx + 86, ly + 206), 5)
    for i, li in enumerate(v["lights"]):
        cy = ly + 8 + 10 + 25 + i * 60
        col = COL.get(li["color"], Y)
        if li["on"]:
            c.circle(lx + 43, cy, 25, fill=col)
            c.circle(lx + 43, cy, 25, outline=Wh, width=3)
        else:
            c.circle(lx + 43, cy, 25, fill=K, outline=col, width=3)
    sig = v.get("color") or "yellow"
    sc = COL.get(sig, Y)
    # recommendation box
    bw = 210
    advice = {"green": ctx.t("Now is the time to wash, charge, run the dishwasher", "Jetzt waschen, laden, spülen"),
              "yellow": ctx.t("Use electricity with care", "Strom bewusst nutzen"),
              "red": ctx.t("Postpone consumption if you can", "Verbrauch möglichst verschieben")}.get(sig, "")
    size, lines, L, tr = _fitpara(c, advice, "poiret", 25, bw - 2 * 5 - 32, 130, lh=1.2, min_size=14)
    inner_h = 14 + _lh(c, "jos", 11) + 8 + 11 + 8 + len(lines) * L + 14
    bh = inner_h + 2 * 5 + 2
    bxx, byy = R0 - bw, ly + (206 - bh) / 2
    c.rect((bxx, byy, R0, byy + bh), outline=Y, width=2)
    c.rect((bxx + 6, byy + 6, R0 - 6, byy + bh - 6), outline=Y, width=1)
    yy = byy + 7 + 14
    yy += _lab(c, bxx + bw / 2, yy, ctx.t("Recommendation", "Empfehlung"), 11, 5, bw - 30) + 8
    _dia(c, bxx + bw / 2, yy + 5, 8, Y)
    yy += 11 + 8
    c.para(bxx + 21, yy, bw - 42, lines, "poiret", size, L, Wh, tr, align="c")
    # middle text column
    mx0, mx1 = lx + 86 + 30, bxx - 30
    MW = mx1 - mx0
    head = v["title"] + (f" · {v['place']}" if v.get("place") else "")
    name = v["signal_name"][:1].upper() + v["signal_name"][1:]
    bs = 92
    while bs > 34 and c.tw(name, "lime", bs) > MW:
        bs -= 1
    sub = ctx.t("{p} renewables", "{p} erneuerbar", p=v["share_text"]) if v.get("share") is not None else v["subtitle"]
    ss, str_, sub = _fit1(c, sub, "poiret", 30, MW, 0, 16)
    hh = _lh(c, "jos", 14) + 6 + bs + 6 + _lh(c, "poiret", ss) + 6 + 4 + 9
    yy = ly + (206 - hh) / 2
    yy += _lab(c, mx0, yy, head, 14, 5, MW, align="l") + 6
    c.text(mx0, yy, _ellip(c, name, "lime", bs, MW), "lime", bs, Wh, lh=1)
    yy += bs + 6
    c.text(mx0, yy, sub, "poiret", ss, Y)
    yy += _lh(c, "poiret", ss) + 6 + 4
    c.hline(mx0, mx0 + 60, yy + 4, Y)
    _dia(c, mx0 + 74, yy + 4.5, 10, Y)
    _dia(c, mx0 + 74, yy + 4.5, 8, sc)
    c.hline(mx0 + 88, mx0 + 148, yy + 4, Y)

    # bottom: legend, ticks, band, now label, caption (bottom-up)
    items = []
    if v.get("best_text"):
        items.append((G, v["best_text"]))
    items.append((Y, v["source"]))
    lgh = _lh(c, "jos", 12)
    gap = 34
    nat = [c.tw(t.upper(), "jos", 12, 2) - 2 + 18 for _, t in items]
    rows = [items] if sum(nat) + gap * (len(items) - 1) <= W else [[it] for it in items]
    lg_y = B0 - lgh * len(rows) - 6 * (len(rows) - 1)
    yy = lg_y
    for row in rows:
        widths = []
        for col, t in row:
            s, tr, tt = _fit1(c, t.upper(), "jos", 12, (W - gap * (len(row) - 1)) / len(row) - 18, 2)
            widths.append((col, tt, s, tr, c.tw(tt, "jos", s, tr) - tr + 18))
        tot = sum(w[4] for w in widths) + gap * (len(widths) - 1)
        x = L0 + (W - tot) / 2
        for col, tt, s, tr, w in widths:
            _dia(c, x + 5, yy + lgh / 2 - 1, 10, col)
            c.text(x + 18, yy + (lgh - _lh(c, "jos", s)) / 2, tt, "jos", s, Y, track=tr)
            x += w + gap
        yy += lgh + 6
    tk_y = lg_y - 4 - 10 - 16
    for k in range(9):
        c.text(L0 + W * k / 8, tk_y, f"{k * 3:02d}", "jos", 12, Y, align="c")
    band_b = tk_y - 10
    band_t = band_b - 42
    c.rect((L0, band_t, R0, band_b), outline=Y, width=1)
    cw = (W - 8 - 23 * 2) / 24
    for i, h in enumerate(v["hours"]):
        x = L0 + 4 + i * (cw + 2)
        col = COL.get(h.get("color"))
        if col is not None:
            c.rect((x, band_t + 4, x + cw, band_b - 4), fill=col)
        else:
            c.rect((x, band_t + 4, x + cw, band_b - 4), outline=Y)
    nx = L0 + W * v["now_pos"]
    c.rect((nx - 1, band_t - 6, nx + 2, band_b + 6), fill=Wh)
    c.rect((nx - 2, band_t - 6, nx - 1, band_b + 6), fill=K)
    c.rect((nx + 2, band_t - 6, nx + 3, band_b + 6), fill=K)
    tl_y = band_t - 10 - 18
    tx = min(max(nx, L0 + 24), R0 - 24)
    c.text(tx, tl_y, v["time"], "jos", 13, Wh, align="c")
    cap = ctx.t("Today · 0 – 24 h", "Heute · 0 – 24 Uhr")
    _lab(c, (L0 + R0) / 2, tl_y - 10 - _lh(c, "jos", 12), cap, 12, 6, W)
    return c.finish()


# ================================================================== wordclock
def wordclock(ctx, v):
    from ..designs import moon_disc
    c = _new()
    c.vline(192, Y0, Y1, Y)
    c.vline(607, Y0, Y1, Y)
    # left: date column
    LC = 108
    items = [("t", v["weekday"].upper(), "poiret", 20, 6, Y), ("o",), ("big", str(v["day"])), ("o",),
             ("t", v["month"].upper(), "poiret", 18, 4, Y), ("t", roman(v["year"]), "jos", 13, 6, Y),
             ("gap", 6), ("t", ctx.t("Wk {n}", "KW {n}", n=roman(v["week"])), "jos", 12, 5, Y)]
    hs = []
    for it in items:
        hs.append(20 if it[0] == "o" else 96 if it[0] == "big" else it[1] if it[0] == "gap" else _lh(c, it[2], it[3]))
    y = Y0 + (Y1 - Y0 - sum(hs) - 4 * (len(items) - 1)) / 2
    for it, h in zip(items, hs):
        if it[0] == "o":
            _orn(c, LC, y + 10, 30, 8)
        elif it[0] == "big":
            c.text(LC, y, it[1], "lime", 96, R if v.get("special") else Wh, lh=1, align="c")
        elif it[0] == "t":
            _lab(c, LC, y, it[1], it[3], it[4], 150, it[5], role=it[2], upper=False)
        y += h + 4
    # middle: letter grid
    rows, cols = v["rows"], v["cols"]
    cw, ch = min(33, 363 / cols), min(36, 360 / rows)
    gw, gh = cw * cols, ch * rows
    ow, oh = gw + 20 + 2 + 8 + 4, gh + 16 + 2 + 8 + 4
    ox, oy = 400 - ow / 2, 240 - oh / 2
    c.rect((ox, oy, ox + ow, oy + oh), outline=Y, width=2)
    c.rect((ox + 6, oy + 6, ox + ow - 6, oy + oh - 6), outline=Y, width=1)
    lit = set(map(tuple, v["lit"]))
    gx, gy = ox + 7 + 10, oy + 7 + 8
    off = B
    for r, line in enumerate(v["grid"]):
        for k, letter in enumerate(line):
            on = (r, k) in lit
            col = Y if on else off
            x = gx + k * cw + cw / 2
            c.text(x, gy + r * ch, letter, "jos", 22, col, lh=ch / 22, align="c",
                   stroke=1 if on else 0, stroke_fill=col if on else None)
    # right: dial, time, minute dots, moon
    RC = 692
    now = v["now"]
    extra = max(0, min(4, now.minute - v["minute"])) if now.hour == v["hour"] else 0
    th = _lh(c, "jos", 22)
    hs = [120, th, 14, _lh(c, "jos", 11), 1 + 8, 34, _lh(c, "jos", 11)]
    y = Y0 + (Y1 - Y0 - sum(hs) - 10 * (len(hs) - 1)) / 2
    cx, cy = RC, y + 60
    c.circle(cx, cy, 56, outline=Y, width=2)
    c.circle(cx, cy, 51, outline=Y, width=1)
    for i in range(12):
        a = i / 12 * math.pi * 2
        s = 5 if i % 3 == 0 else 3
        px, py = cx + math.sin(a) * 43, cy - math.cos(a) * 43
        c.poly([(px + math.sin(a) * s, py - math.cos(a) * s), (px + math.cos(a) * s * .6, py + math.sin(a) * s * .6),
                (px - math.sin(a) * s, py + math.cos(a) * s), (px - math.cos(a) * s * .6, py - math.sin(a) * s * .6)], fill=Y)
    ha = math.radians((v["hour"] % 12 + v["minute"] / 60) * 30)
    ma = math.radians(v["minute"] * 6)
    c.stroke([(cx, cy), (cx + math.sin(ha) * 25, cy - math.cos(ha) * 25)], Wh, 4)
    c.stroke([(cx, cy), (cx + math.sin(ma) * 40, cy - math.cos(ma) * 40)], Wh, 2)
    c.circle(cx, cy, 4, fill=R)
    y += 120 + 10
    c.text(RC, y, v["time"], "jos", 22, Wh, align="c")
    y += th + 10
    for i in range(4):
        dx = RC - 33 + i * 22
        if i < extra:
            _dia(c, dx, y + 7, 10, Wh)
        else:
            _dia(c, dx, y + 7, 10, outline=Y)
    y += 14 + 10
    _lab(c, RC, y, ctx.t("+ {n} min", "+ {n} Min.", n=roman(extra) or "0"), 11, 3, 150)
    y += _lh(c, "jos", 11) + 10 + 4
    c.hline(RC - 50, RC + 50, y, Y)
    y += 1 + 4 + 10
    moon_disc(c, RC, round(y + 17), 15, v["phase"], Y, K, Y)
    c.circle(RC, y + 17, 15, outline=Y, width=2)
    y += 34 + 10
    _lab(c, RC, y, v["moon"], 11, 4, 156)
    return c.finish()


# ================================================================== countdown
def countdown(ctx, v):
    c = _new()
    CX, L0, R0, T0, B0 = 400, 63, 737, 41, 441
    W = R0 - L0
    _sunburst(c, CX, T0 + 50, 110, 48, 10, 20)
    y = T0 + 50 + 8
    y += _lab(c, CX, y, v["title"], 14, 10, W) + 8
    big = v["big"]
    bs = 150
    while bs > 40 and c.tw(big, "lime", bs) > W - 2 * (110 + 18 + 26):
        bs -= 2
    arm = 110
    bw = c.tw(big, "lime", bs)
    if bw + 2 * (arm + 18 + 26) > W:
        arm = max(20, (W - bw) / 2 - 18 - 26)
    c.text(CX, y + (150 - bs) * .6, big, "lime", bs, Wh, lh=1, align="c")
    my = y + 75
    lx = CX - bw / 2 - 26
    _dia(c, lx - 5, my, 10, Y)
    c.hline(lx - 10 - 8 - arm, lx - 10 - 8, my, Y)
    rx = CX + bw / 2 + 26
    _dia(c, rx + 5, my, 10, Y)
    c.hline(rx + 18, rx + 18 + arm, my, Y)
    y += 150 + 8
    line = f"{v['small']} {v['event']}".strip() if v.get("small") else v["event"]
    s, tr, line = _fit1(c, line, "poiret", 36, W, 1, 18)
    c.text(CX, y, line, "poiret", s, Y, track=tr, align="c")
    y += _lh(c, "poiret", 36) + 8
    _lab(c, CX, y, f"{v['target_weekday']} · {v['date']}", 14, 6, W)
    # strip and labels at the bottom
    lh12 = _lh(c, "jos", 12)
    ly = B0 - lh12
    sy = ly - 8 - 26
    c.hline(L0, R0, sy + 12, Y)
    strip = v.get("strip") or []
    n = len(strip)

    def xpos(i):
        return L0 + 8 + (W - 16) * (i / (n - 1) if n > 1 else 0)

    mid = None
    for i, e in enumerate(strip):
        x = xpos(i)
        if e["today"] or e["target"]:
            continue
        if e["first_of_month"]:
            c.rect((x - 1, sy + 1, x + 1, sy + 25), fill=Y)
            if mid is None and 0.15 < i / max(1, n - 1) < 0.85:
                mid = (x, e["date"])
        elif n <= 120 or e["weekday"] == 0:
            c.rect((x, sy + 6, x + 1, sy + 18), fill=Y)
    a_today = v["state"] != "past"
    ends = [(L0 + 8, True), (R0 - 8, False)]
    for x, first in ends:
        is_today = first == a_today if v["state"] != "today" else first
        if is_today:
            _dia(c, x, sy + 12.5, 13, Wh)
        else:
            _dia(c, x, sy + 12.5, 15, R)
    td, tg = v["today"], v["target"]
    t_lab = f"{ctx.t('Today', 'Heute')} · {roman(td.day)}. {roman(td.month)}"
    e_lab = f"{v['event']} · {roman(tg.day)}. {roman(tg.month)}"
    left, right = (t_lab, Wh), (e_lab, R)
    if v["state"] == "past":
        left, right = (e_lab, R), (t_lab, Wh)
    if v["state"] == "today":
        _lab(c, CX, ly, t_lab, 12, 3, W, Wh)
    else:
        mw = 0
        if mid:
            mt = f"{roman(mid[1].day)}. {roman(mid[1].month)}"
            mw = c.tw(mt, "jos", 12, 3) + 20
        half = (W - mw) / 2 - 10
        _lab(c, L0, ly, left[0], 12, 3, half, left[1], align="l")
        _lab(c, R0, ly, right[0], 12, 3, half, right[1], align="r")
        if mid:
            lw = c.tw(left[0].upper(), "jos", 12, 3)
            rw = c.tw(right[0].upper(), "jos", 12, 3)
            mx = min(max(mid[0], L0 + min(lw, half) + mw / 2 + 4), R0 - min(rw, half) - mw / 2 - 4)
            c.text(mx, ly, mt, "jos", 12, Y, track=3, align="c")
    return c.finish()


# ================================================================== art
def art(ctx, v):
    c = _new()
    SW, SH = 476, 376
    img = v["image"]
    k = min(SW / img.width, SH / img.height)
    iw, ih = max(1, round(img.width * k)), max(1, round(img.height * k))
    ix, iy = 50 + (SW - iw) // 2, 52 + (SH - ih) // 2
    c.rect((ix - 9, iy - 9, ix + iw + 9, iy + ih + 9), outline=Y, width=2)
    c.rect((ix - 1, iy - 1, ix + iw + 1, iy + ih + 1), outline=Y, width=1)
    c.img.paste(img.convert("RGB").resize((iw, ih)), (ix, iy))

    CX, W, T0, B0 = 659, 200, 41, 439
    _sunburst(c, CX, T0 + 40, 80, 38, 8, 15)
    y = T0 + 40 + 8
    s, lines, L, tr = c.fit(v["title"].upper(), "jos", 13, W, 13 * 1.6 * 2, lh=1.6, track=6, min_size=10)
    lines = [_ellip(c, l, "jos", s, W, tr) for l in lines[:2]]
    c.para(CX - W / 2, y, W, lines, "jos", s, L, Y, tr, align="c")
    y += len(lines) * L + 8
    _orn(c, CX, y + 4, 50, 8, R)
    y += 8 + 8
    # bottom-up: city, museum, date table
    by = B0
    if v.get("museum_city"):
        by -= _lh(c, "jos", 12)
        _lab(c, CX, by, v["museum_city"], 12, 6, W)
        by -= 8
    if v.get("museum"):
        s2, l2, L2, _ = _fitpara(c, v["museum"], "poiret", 20, W, 2 * 20 * 1.15, lh=1.15, min_size=14)
        by -= len(l2) * L2
        c.para(CX - W / 2, by, W, l2, "poiret", s2, L2, Wh, align="c")
        by -= 8 + 2
    if v.get("date"):
        th = 7 + _lh(c, "jos", 11) + 3 + _lh(c, "poiret", 24) + 7
        by -= th + 2
        c.hline(CX - W / 2, CX + W / 2, by, Y)
        c.hline(CX - W / 2, CX + W / 2, by + th + 1, Y)
        d = v["date"].strip()
        lab = roman(int(d)) if d.isdigit() and 0 < int(d) < 4000 else ctx.t("Dated", "Datiert")
        _lab(c, CX, by + 1 + 7, lab, 11, 4, W)
        _lab(c, CX, by + 1 + 7 + _lh(c, "jos", 11) + 3, d, 24, 0, W, Wh, role="poiret", upper=False)
        by -= 8
    room = by - y
    extra = v.get("medium") or ""
    ah = 20 * 1.25 if v.get("artist") else 0
    eh = _lh(c, "jos", 11) + 6 if extra else 0
    s3, l3, L3, _ = _fitpara(c, v["work"], "poiret", 31, W, max(36, room - ah - 10 - eh - 10), lh=1.15, min_size=16)
    tot = len(l3) * L3 + (10 + ah if ah else 0) + (eh if extra else 0)
    yy = y + max(0, (room - tot) / 2)
    c.para(CX - W / 2, yy, W, l3, "poiret", s3, L3, Wh, align="c")
    yy += len(l3) * L3 + 10
    if v.get("artist"):
        s4, tr4, t4 = _fit1(c, v["artist"], "lime", 20, W, 0, 12)
        c.text(CX, yy, t4, "lime", s4, Y, lh=1.25 * 20 / s4, align="c")
        yy += ah + 6
    if extra:
        _lab(c, CX, yy, extra, 11, 2, W)
    return c.finish()


# ================================================================== waste
BIN = {"black": (K, Wh, Y), "yellow": (Y, Wh, K), "blue": (B, Y, K), "green": (G, Y, K), "red": (R, Wh, K)}


def _bin(c, x, y, s, color, ribs=3):
    """The mockup's 40×50 wheelie bin at scale s (top-left x, y)."""
    fill, st, rib = BIN.get(color, BIN["black"])
    w = max(1, round(s if s >= 1.5 else 1.5 * s))

    def P(px, py):
        return (x + px * s, y + py * s)

    c.rect((*P(2, 4), *P(38, 10)), fill=fill, outline=st, width=1 if s < 1.5 else 2)
    if ribs == 3:
        c.rect((*P(15, 1), *P(25, 4)), fill=st)
    c.poly([P(5, 11), P(35, 11), P(32, 44), P(8, 44)], fill=fill, outline=st, width=1 if s < 1.5 else 2)
    lines = ((14, 15), (20, 20), (26, 25)) if ribs == 3 else ((20, 20),)
    for a, b in lines:
        c.d.line((P(a, 16), P(b, 39)), fill=rib, width=max(1, round(1.2 * s if ribs == 3 else 2 * s)))
    for wx in (11, 29):
        c.circle(*P(wx, 46), 3 * s, fill=K, outline=st, width=1 if s < 1.5 else 2)


def waste(ctx, v):
    c = _new()
    L0, R0, T0, B0 = 53, 747, 41, 443
    W = R0 - L0
    soon, rows = v.get("soon"), list(v.get("rows") or [])
    if soon:
        hero = {"label": soon["label"], "date": soon["date_long"], "items": soon["items"],
                "names": soon["names_text"], "tonight": not soon["is_today"]}
    else:
        d0 = rows[0]["date"]
        first = [r for r in rows if r["date"] == d0]
        rows = [r for r in rows if r["date"] != d0]
        hero = {"label": rows and first[0]["in_text"] or first[0]["in_text"], "date": first[0]["date_long"],
                "items": [{"name": r["name"], "color": r["color"]} for r in first],
                "names": " + ".join(r["name"] for r in first), "tonight": False}
    bins = hero["items"][:3]
    bs = 2.0 if len(bins) <= 2 else 1.7
    bw, bh = 40 * bs, 50 * bs
    bx = L0
    for i, it in enumerate(bins):
        _bin(c, bx + i * (bw + 14), T0, bs, it["color"])
    tx = L0 + len(bins) * (bw + 14) - 14 + 28
    TW = R0 - tx
    lab = f"{hero['label']} · {hero['date']}"
    hint = ctx.t("Put the bins out tonight", "Heute Abend hinausstellen") if hero["tonight"] else ""
    s, lines, L, tr = _fitpara(c, hero["names"], "poiret", 40, TW, 2 * 44, lh=1.1, min_size=20)
    th = _lh(c, "jos", 13) + 6 + len(lines) * L + (6 + _lh(c, "jos", 12) if hint else 0)
    top_h = max(bh, th)
    yy = T0 + (top_h - th) / 2
    yy += _lab(c, tx, yy, lab, 13, 5, TW, align="l") + 6
    c.para(tx, yy, TW, lines, "poiret", s, L, Wh)
    yy += len(lines) * L + 6
    if hint:
        _lab(c, tx, yy, hint, 12, 4, TW, align="l")
    y = T0 + top_h + 10
    # divider
    c.hline(L0, 400 - 4 - 10 - 18 - 4, y + 4, Y)
    c.hline(400 + 4 + 10 + 18 + 4, R0, y + 4, Y)
    for k, col in ((-18, Y), (0, R), (18, Y)):
        _dia(c, 400 + k, y + 4.5, 8, col)
    y += 8 + 10
    area = B0 - y
    if not rows:
        s, lines, L, tr = _fitpara(c, v["empty_text"], "poiret", 26, W, area, min_size=16)
        c.para(L0, y + (area - len(lines) * L) / 2, W, lines, "poiret", s, L, Y, align="c")
        return c.finish()
    n = min(len(rows), 6, max(1, int(area // 44)))
    rh = area / n
    dw = max(c.tw(r["date_text"], "poiret", 26) for r in rows[:n]) + 20
    dw = max(130, min(dw, 190))
    for i, r in enumerate(rows[:n]):
        ry = y + i * rh
        cy = ry + rh / 2
        if i < n - 1:
            c.hline(L0, R0, ry + rh - 1, Y)
        _bin(c, L0, cy - 20, 0.8, r["color"], ribs=1)
        x = L0 + 32 + 20
        # right part: "in" N "days"
        it = r["in_text"]
        num = str(r["days"])
        if num in it:
            pre, post = it.split(num, 1)
            pre, post = pre.strip().upper(), post.strip().upper()
            pw = c.tw(pre, "jos", 12, 3) if pre else 0
            qw = c.tw(post, "jos", 12, 3) if post else 0
            nw = max(44, c.tw(num, "lime", 32) + 6)
            rx = R0 - qw
            base_top = cy - 16
            bl = c._baseline(base_top, "lime", 32, 1)
            jt = bl - _bl(c, "jos", 12)
            if post:
                c.text(rx, jt, post, "jos", 12, Y, track=3)
            c.text(rx - 8 - nw / 2, base_top, num, "lime", 32, Wh, lh=1, align="c")
            if pre:
                c.text(rx - 8 - nw - 8 - pw, jt, pre, "jos", 12, Y, track=3)
            right_w = qw + 8 + nw + (8 + pw if pre else 0)
        else:
            right_w = _fit1(c, it.upper(), "jos", 12, 200, 3)
            right_w = c.tw(right_w[2], "jos", right_w[0], right_w[1])
            _lab(c, R0, cy - _lh(c, "jos", 12) / 2, it, 12, 3, 200, align="r")
        ph = _lh(c, "poiret", 26)
        ds, dtr, dt = _fit1(c, r["date_text"], "poiret", 26, dw - 12, 0, 16)
        c.text(x, cy - ph / 2, dt, "poiret", ds, Wh)
        kx = x + dw
        ks, ktr, kt = _fit1(c, r["name"], "poiret", 26, R0 - right_w - 16 - kx, 0, 16)
        c.text(kx, cy - ph / 2, kt, "poiret", ks, Y)
    return c.finish()


# ================================================================== warnings
def warnings(ctx, v):
    from ..plugins import _calendar as C
    c = _new()
    c.vline(242, Y0, Y1, Y)
    col = Y if v.get("color") == "yellow" else R
    # left column: triangle, ornament, end of the warning
    LC = 132
    exp = v.get("expires")
    if exp is not None:
        lab, big, sub = ctx.t("Until", "Bis"), f"{exp:%H:%M}", C.weekday(exp.date(), ctx.lang)
    else:
        lab, big, sub = ctx.t("Level", "Stufe"), roman(v["level"]), v["level_text"]
    hs = [132, 20, _lh(c, "jos", 12), 64, _lh(c, "poiret", 22)]
    y = Y0 + (Y1 - Y0 - sum(hs) - 8 * 4) / 2
    tx, ty = LC - 75, y
    c.poly([(tx + 75, ty + 4), (tx + 146, ty + 128), (tx + 4, ty + 128)], fill=K, outline=Y, width=2)
    c.poly([(tx + 75, ty + 22), (tx + 130, ty + 118), (tx + 20, ty + 118)], fill=col, outline=Y)
    mark = K if col == Y else Wh
    c.rect((tx + 70, ty + 52, tx + 80, ty + 90), fill=mark)
    c.poly([(tx + 75, ty + 96), (tx + 81, ty + 102), (tx + 75, ty + 108), (tx + 69, ty + 102)], fill=mark)
    y += 132 + 8
    _orn(c, LC, y + 10, 40, 8)
    y += 20 + 8
    y += _lab(c, LC, y, lab, 12, 5, 190) + 8
    bs = 64
    while bs > 24 and c.tw(big, "lime", bs) > 190:
        bs -= 2
    c.text(LC, y + (64 - bs) / 2, big, "lime", bs, Wh, lh=1, align="c")
    y += 64 + 8
    _lab(c, LC, y, sub, 22, 0, 190, Y, role="poiret", upper=False)

    # right column
    x0, x1, T0, B0 = 273, 747, 45, 441
    W = x1 - x0
    y = T0
    head = v["title"] + (f" · {v['place']}" if v.get("place") else "")
    y += _lab(c, x0, y, head, 13, 6, W, align="l") + 10
    lv = v["level"]
    for i in range(4):
        cx = x0 + 3 + 6 + i * 22
        if i < lv:
            _dia(c, cx, y + 8, 12, col)
        else:
            _dia(c, cx, y + 8, 12, K, outline=Y)
    lx = x0 + 3 + 4 * 22 + 14
    lt = f"{ctx.t('Level', 'Stufe')} {roman(lv)} · {v['level_text']}"
    _lab(c, lx, y + 8 - _lh(c, "jos", 13) / 2, lt, 13, 3, x1 - lx, align="l")
    y += 16 + 10 + 6
    es = 76
    ev = v["event"]
    while es > 36 and c.tw(ev, "lime", es) > W:
        es -= 2
    c.text(x0, y + (76 - es) * .7, _ellip(c, ev, "lime", es, W), "lime", es, Wh, lh=1)
    y += 76 + 10
    span = v.get("place_span") or v.get("span") or ""
    if span:
        y += _lab(c, x0, y, span, 25, 0, W, Y, align="l", role="poiret", upper=False) + 10
    y += 4
    _dia(c, x0 + 4, y + 4, 8, R)
    c.hline(x0 + 16, x1, y + 4, Y)
    y += 8 + 4 + 10
    # footer bottom-up
    fh = _lh(c, "jos", 12)
    fy = B0 - fh
    c.hline(x0, x1, fy - 8 - 1, Y)
    _lab(c, x0, fy, v.get("footer") or v.get("source", ""), 12, 5, W, align="l")
    bottom = fy - 9 - 10
    if v.get("more_text"):
        mh = _lh(c, "poiret", 19)
        bottom -= mh
        _lab(c, x0, bottom, v["more_text"], 19, 0, W, Y, align="l", role="poiret", upper=False)
        bottom -= 8
    text = v.get("description") or v.get("headline") or ""
    if v.get("instruction"):
        text = (text + "\n" + v["instruction"]).strip()
    if text:
        s, lines, L, tr = _fitpara(c, text, "poiret", 23, W, bottom - y, lh=1.35, min_size=14)
        c.para(x0, y, W, lines, "poiret", s, L, Wh)
    return c.finish()


# ================================================================== wifi
def wifi(ctx, v):
    from ..plugins import wifi as wf
    c = _new()
    O = 367
    bx, by = 47, 57
    c.rect((bx, by, bx + O, by + O), outline=Y, width=2)
    c.rect((bx + 7, by + 7, bx + O - 7, by + O - 7), outline=Y, width=1)
    inner = O - 16
    wf.draw_modules(c.d, v["modules"], bx + 8, by + 8, inner, dark=K, light=Wh, quiet=2)

    CX, x0, x1, T0, B0 = 598, 448, 749, 43, 437
    W = x1 - x0
    _sunburst(c, CX, T0 + 50, 100, 48, 10, 18)
    y = T0 + 50 + 8
    y += _lab(c, CX, y, v["title"], 14, 10, W) + 8
    _orn(c, CX, y + 4, 70, 10, R)
    y += 8 + 8
    # bottom-up: hint, table
    hy = B0 - _lh(c, "jos", 12)
    _lab(c, CX, hy, v["hint"], 12, 5, W)
    cells = [(ctx.t("Security", "Sicherheit"), v["security"] or ctx.t("Open", "Offen"))]
    if v.get("place"):
        cells.append((ctx.t("Place", "Ort"), v["place"]))
    th = 6 + _lh(c, "jos", 11) + 2 + _lh(c, "poiret", 22) + 6
    ty = hy - 4 - 8 - th - 2
    c.hline(x0, x1, ty, Y)
    c.hline(x0, x1, ty + th + 1, Y)
    cw = W / len(cells)
    for i, (a, b) in enumerate(cells):
        cx = x0 + cw * i + cw / 2
        if i:
            c.vline(x0 + cw * i - 1, ty, ty + th + 1, Y)
        _lab(c, cx, ty + 1 + 6, a, 11, 4, cw - 8)
        _lab(c, cx, ty + 1 + 6 + _lh(c, "jos", 11) + 2, b, 22, 0, cw - 10, Wh, role="poiret", upper=False)
    room = ty - 8 - y
    blocks = []
    ss = 48
    while ss > 22 and c.tw(v["ssid"], "lime", ss) > W:
        ss -= 2
    blocks.append((v["network_label"], "lime", ss, _ellip(c, v["ssid"], "lime", ss, W), 1.0))
    if v.get("password"):
        ps, ptr, pt = _fit1(c, v["password"], "poiret", 34, W, 0, 16)
        blocks.append((v["password_label"], "poiret", ps, pt, 1.1))
    hs = [_lh(c, "jos", 11) + 4 + b[2] * b[4] for b in blocks]
    note = v.get("note", "")
    if note:
        nh = _lh(c, "poiret", 20)
        if sum(hs) + 14 * len(hs) + nh <= room:
            hs.append(nh)
        else:
            note = ""
    yy = y + (room - sum(hs) - 14 * (len(hs) - 1)) / 2
    for (lab, role, s, t, lh), h in zip(blocks, hs):
        _lab(c, CX, yy, lab, 11, 5, W)
        c.text(CX, yy + _lh(c, "jos", 11) + 4, t, role, s, Wh, lh=lh, align="c")
        yy += h + 14
    if note:
        _lab(c, CX, yy, note, 20, 0, W, Y, role="poiret", upper=False)
    return c.finish()


# ================================================================== habits
def habits(ctx, v):
    c = _new()
    L0, R0, T0, B0 = 47, 753, 39, 439
    W = R0 - L0
    d = v["today"]
    right = f"{v['weekday']} · {roman(d.day)} · {roman(d.month)} · {roman(d.year)}"
    rs, rtr, right = _fit1(c, right.upper(), "jos", 13, W * .5, 5)
    rw = c.tw(right, "jos", rs, rtr) - rtr
    ts, ttr, title = _fit1(c, v["title"].upper(), "poiret", 28, W - rw - 20, 8, 16)
    th = _lh(c, "poiret", 28)
    c.text(L0, T0, title, "poiret", ts, Y, track=ttr, lh=th / ts)
    base = c._baseline(T0, "poiret", ts, th / ts)
    c.text(R0, base - _bl(c, "jos", rs), right, "jos", rs, Y,
           track=rtr, align="r")
    y = T0 + th + 10
    c.hline(L0, 400 - 4 - 10, y + 4, Y)
    c.hline(400 + 4 + 10, R0, y + 4, Y)
    _dia(c, 400, y + 4.5, 8, R)
    y += 8 + 10
    hb = v["habits"][:6]
    nrow = (len(hb) + 1) // 2
    ncol = 2 if len(hb) > 1 else 1
    gap = 14
    cw = (W - gap * (ncol - 1)) / ncol
    ch = (B0 - y - gap * (nrow - 1)) / nrow
    for i, h in enumerate(hb):
        cx0 = L0 + (i % ncol) * (cw + gap)
        cy0 = y + (i // ncol) * (ch + gap)
        c.rect((cx0, cy0, cx0 + cw, cy0 + ch), outline=Y)
        c.rect((cx0 + 5, cy0 + 5, cx0 + cw - 5, cy0 + ch - 5), outline=Y)
        cell = min(20, (ch - 22) / 6)
        gx = cx0 + 6 + 14
        gy = cy0 + (ch - 6 * cell) / 2
        nowc, nowr = v["now"]
        ds = max(5, cell * 0.55)
        for w, week in enumerate(h["grid"][-6:]):
            for dd, val in enumerate(week):
                if val is None:
                    continue
                px, py = gx + dd * cell + cell / 2, gy + w * cell + cell / 2
                today = (w == nowc and dd == nowr)
                if today:
                    _dia(c, px, py, ds + 1, Y if val else K, outline=R, width=2)
                elif val:
                    _dia(c, px, py, ds, Y)
                else:
                    _dia(c, px, py, ds, K, outline=Y)
        tx = gx + 7 * cell + 18
        TW = cx0 + cw - 6 - 14 - tx
        best = h["streak"] > 0 and h["streak"] >= h["best"]
        note = ctx.t("Longest streak", "Längste Serie") if best else ctx.t("in a row", "in Folge")
        ns = 44 if ch > 120 else 34
        nl = 2 if ch > 120 else 1
        s, lines, L, tr = _fitpara(c, h["name"], "poiret", 22, TW, nl * 22 * 1.15, lh=1.15, min_size=14, max_lines=nl)
        hh = len(lines) * L + 4 + 4 + ns + 4 + _lh(c, "jos", 11)
        yy = cy0 + (ch - hh) / 2
        c.para(tx, yy, TW, lines, "poiret", s, L, Wh)
        yy += len(lines) * L + 8
        num = str(h["streak"])
        c.text(tx, yy, num, "lime", ns, R if best else Wh, lh=1)
        nw = c.tw(num, "lime", ns)
        unit = ctx.t("Days", "Tage") if h["streak"] != 1 else ctx.t("Day", "Tag")
        bl = c._baseline(yy, "lime", ns, 1)
        _lab(c, tx + nw + 8, bl - _bl(c, "jos", 11), unit, 11, 3, TW - nw - 8, align="l")
        yy += ns + 4
        _lab(c, tx, yy, note, 11, 3, TW, align="l")
    return c.finish()


# ================================================================== sudoku
def sudoku(ctx, v):
    c = _new()
    ox, oy = 43, 41
    c.rect((ox, oy, ox + 397, oy + 397), outline=Y, width=1)
    gx, gy = ox + 5, oy + 5
    c.rect((gx, gy, gx + 387, gy + 387), outline=Y, width=3)
    gx, gy = gx + 3, gy + 3

    def line(i):
        return 0 if i == 8 else (3 if i % 3 == 2 else 1)

    pos, p = [], 0
    for i in range(9):
        pos.append(p)
        p += 41 + line(i)
    for i in range(9):
        if line(i):
            c.rect((gx + pos[i] + 41, gy, gx + pos[i] + 41 + line(i), gy + 381), fill=Y)
            c.rect((gx, gy + pos[i] + 41, gx + 381, gy + pos[i] + 41 + line(i)), fill=Y)
    for r, row in enumerate(v["grid"]):
        for k, n in enumerate(row):
            if n:
                c.text(gx + pos[k] + 20.5, gy + pos[r] + 41 / 2 - 13 + 2, str(n), "lime", 26, Wh, lh=1, align="c")

    CX, x0, x1, T0, B0 = 610, 472, 749, 41, 439
    W = x1 - x0
    _sunburst(c, CX, T0 + 46, 90, 44, 10, 17)
    y = T0 + 46 + 9
    title = f"{v['title']} {v['subtitle']}".strip()
    y += _lab(c, CX, y, title, 13, 6, W) + 9
    _orn(c, CX, y + 4, 60, 10, R)
    y += 8 + 9
    # bottom-up
    fy = B0 - _lh(c, "jos", 13)
    _lab(c, CX, fy, _rdate(v["today"]), 13, 8, W)
    hy = fy - 9 - _lh(c, "jos", 12)
    _lab(c, CX, hy, v["hint"], 12, 4, W)
    # givens box
    num = str(v["givens"])
    rest = v["givens_text"].replace(num, "").strip()
    nw = c.tw(num, "lime", 34)
    s, lines, L, tr = c.fit(rest.upper(), "jos", 11, W - nw - 12 - 4, 11 * 1.5 * 2, lh=1.5, track=3, min_size=8)
    lines = [_ellip(c, l, "jos", s, W - nw - 16, tr) for l in lines[:2]]
    bh = 8 + max(34, len(lines) * L) + 8
    hh = _lh(c, "jos", 11) + 10 + 44 + 10 + 4 + 18
    spare = max(0, hy - 9 - y - hh - 9 - (bh + 2) - 9)
    dy = y + spare / 4
    by = dy + hh + spare / 4 + 9
    c.hline(x0, x1, by, Y)
    c.hline(x0, x1, by + bh + 1, Y)
    lw = max(c.tw(l, "jos", s, tr) - tr for l in lines) if lines else 0
    tot = nw + 12 + lw
    bx = CX - tot / 2
    c.text(bx, by + 1 + (bh - 34) / 2, num, "lime", 34, Wh, lh=1)
    ty = by + 1 + (bh - len(lines) * L) / 2
    c.para(bx + nw + 12, ty, lw, lines, "jos", s, L, Y, tr)
    # difficulty (centred in the free room)
    yy = dy
    yy += _lab(c, CX, yy, ctx.t("Difficulty", "Schwierigkeit"), 11, 5, W) + 10
    s2, tr2, t2 = _fit1(c, v["level_name"], "poiret", 44, W, 0, 20)
    c.text(CX, yy + (44 - s2) / 2, t2, "poiret", s2, Wh, lh=1, align="c")
    yy += 44 + 10 + 4
    n = v["level_max"]
    for i in range(n):
        dx = CX + (i - (n - 1) / 2) * 27
        if i < v["level_no"]:
            _dia(c, dx, yy + 9, 13, Y)
        else:
            _dia(c, dx, yy + 9, 13, outline=Y)
    return c.finish()


# ================================================================== solar
def solar(ctx, v):
    c = _new()
    L0, R0, T0, B0 = 51, 749, 39, 445
    W = R0 - L0
    # sun
    sx, sy = L0 + 75, T0 + 75
    for i in range(24):
        a = i / 24 * math.pi * 2
        lng = i % 2 == 0
        r2 = 72 if lng else 58
        c.d.line((sx + math.cos(a) * 44, sy + math.sin(a) * 44, sx + math.cos(a) * r2, sy + math.sin(a) * r2),
                 fill=Y, width=3 if lng else 2)
    c.circle(sx, sy, 38, fill=K, outline=Y, width=2)
    c.circle(sx, sy, 31, fill=Y)
    c.poly([(sx, sy - 13), (sx + 13, sy), (sx, sy + 13), (sx - 13, sy)], fill=K)
    # right column of figures
    rx0 = R0 - 200
    c.vline(rx0, T0 + 8, T0 + 142, Y)
    figs = [(v["subtitle"], v["today_text"]), (ctx.t("Saved", "Gespart"), v["saved_text"])]
    if v.get("total_text"):
        figs.append((ctx.t("Total", "Insgesamt"), v["total_text"]))
    fh = _lh(c, "jos", 11) + 2 + _lh(c, "poiret", 27)
    y = T0 + (150 - (len(figs) * fh + 9 * (len(figs) - 1))) / 2
    for a, b in figs:
        _lab(c, rx0 + 22, y, a, 11, 4, 178, align="l")
        _lab(c, rx0 + 22, y + _lh(c, "jos", 11) + 2, b, 27, 0, 178, Wh, align="l", role="poiret", upper=False)
        y += fh + 9
    # big power
    mx0 = L0 + 150 + 24
    MW = rx0 - 24 - mx0
    num = str(v["power_w"])
    bs = 104
    while bs > 40 and c.tw(num, "lime", bs) + 10 + c.tw("W", "lime", bs * 44 / 104) > MW:
        bs -= 2
    us = round(bs * 44 / 104)
    hh = _lh(c, "jos", 13) + 2 + bs
    y = T0 + (150 - hh) / 2
    y += _lab(c, mx0, y, v["power_label"], 13, 6, MW, align="l") + 2
    c.text(mx0, y, num, "lime", bs, Wh, lh=1)
    bl = c._baseline(y, "lime", bs, 1)
    c.text(mx0 + c.tw(num, "lime", bs) + 10, bl - c._baseline(0, "lime", us, 1), "W", "lime", us, Y, lh=1)
    y = T0 + 150 + 8
    c.hline(L0, 400 - 14, y + 4, Y)
    c.hline(400 + 14, R0, y + 4, Y)
    _dia(c, 400, y + 4.5, 8, R)
    y += 8 + 8
    # chart 698 × 170
    cy0 = y
    base = cy0 + 146
    peak = v["peak"] or 1
    t0, t1 = v["t0"], v["t1"]

    def X(h):
        return L0 + (h - t0) / (t1 - t0) * W

    def Yv(p):
        return base - min(p, peak) / (peak * 1.075) * 128

    for frac in (0.5, 1.0):
        yy = Yv(peak * frac)
        c.dashed((L0, yy, R0, yy), Y, 1, 2, 6)
        c.text(L0 + 4, yy - 4 - _lh(c, "jos", 11) + 2, f"{ctx.num(peak * frac, 0)} W", "jos", 11, Y)
    hs, ws = v["hours"], v["watts"]
    if len(hs) >= 2:
        pts = [(X(hs[0]), base)] + [(X(h), Yv(w)) for h, w in zip(hs, ws)] + [(X(hs[-1]), base)]
        c.poly(pts, fill=Y)
    c.rect((L0, base - 1, R0, base + 1), fill=Y)
    if v.get("now_visible"):
        nx = X(v["now"])
        c.rect((nx - 1, cy0 + 8, nx + 1, base), fill=Wh)
        ny = Yv(v["power"])
        c.poly([(nx, ny - 8), (nx + 8, ny), (nx, ny + 8), (nx - 8, ny)], fill=Wh)
        tw_ = c.tw(v["now_text"], "jos", 13)
        tx = nx + 8 if nx + 8 + tw_ < R0 else nx - 8 - tw_
        c.text(tx, cy0 + 16 - _bl(c, "jos", 13), v["now_text"], "jos", 13, Wh)
    for h, t in zip(v["ticks"], v["tick_labels"]):
        x = X(h)
        tw_ = c.tw(t, "jos", 12)
        x = min(max(x, L0 + tw_ / 2), R0 - tw_ / 2)
        c.text(x, cy0 + 166 - _bl(c, "jos", 12), t, "jos", 12, Y, align="c")
    y = cy0 + 170 + 8
    parts = [v["title"]]
    if v.get("max_text"):
        parts.append(f"{ctx.t('Peak', 'Spitze')} {v['max_text']}")
    parts.append(v["footer"])
    if v.get("place"):
        parts.append(v["place"])
    _lab(c, 400, min(y, B0 - _lh(c, "jos", 11)), " · ".join(parts), 11, 5, W)
    return c.finish()


def _in_days(c, rx, cy, text, n, nsize=32, nw_min=44):
    """'IN  4  TAGEN' – the number in Limelight between spaced caps, right-aligned at rx. Returns width."""
    num = str(n)
    if num not in text:
        s, tr, t = _fit1(c, text.upper(), "jos", 12, 220, 3)
        c.text(rx, cy - _lh(c, "jos", s) / 2, t, "jos", s, Y, track=tr, align="r")
        return c.tw(t, "jos", s, tr)
    pre, post = (p.strip().upper() for p in text.split(num, 1))
    pw = c.tw(pre, "jos", 12, 3) - 3 if pre else 0
    qw = c.tw(post, "jos", 12, 3) - 3 if post else 0
    nw = max(nw_min, c.tw(num, "lime", nsize) + 6)
    top = cy - nsize / 2
    jt = c._baseline(top, "lime", nsize, 1) - _bl(c, "jos", 12)
    x = rx
    if post:
        c.text(x, jt, post, "jos", 12, Y, track=3, align="r")
        x -= qw + 8
    c.text(x - nw / 2, top, num, "lime", nsize, Wh, lh=1, align="c")
    x -= nw
    if pre:
        c.text(x - 8, jt, pre, "jos", 12, Y, track=3, align="r")
        x -= 8 + pw
    return rx - x


# ================================================================== waterlevel
def _nice(x):
    for e in range(0, 6):
        for m in (1, 2, 2.5, 5):
            if m * 10 ** e >= x:
                return m * 10 ** e
    return x


def waterlevel(ctx, v):
    c = _new()
    c.vline(172, Y0, Y1, Y)
    # left: gauge staff
    gx, gy = 38, 40
    vals = [x for x in (v.get("hsw"), v.get("max"), v.get("mw"), v.get("value")) if x is not None]
    step = _nice(max(vals + [10]) * 1.08 / 4.5)
    M = step * 4.5

    def sy(cm):
        return gy + 380 - cm / M * 360

    for i in range(18):
        cm = (i + 1) * M / 18
        x = gx + (36 if i % 2 == 0 else 52)
        c.rect((x, sy(cm) + 5, x + 16, sy(cm) + 15), fill=Y)
    if v.get("value") is not None:
        wy = max(gy + 20, sy(v["value"]))
        c.rect((gx, wy, gx + 120, gy + 400), fill=B)
        c.stroke([(gx + k * 10, wy + (-2 if k % 2 == 0 else 2)) for k in range(13)], Wh, 2, cap=False)
    c.rect((gx + 36, gy + 20, gx + 68, gy + 380), outline=Y, width=2)
    for k in range(5):
        cm = k * step
        c.text(gx + 30, sy(cm) + 4 - _bl(c, "jos", 11), ctx.num(cm, 0), "jos", 11, Y, align="r")
    for key, col in (("mw", Wh), ("hsw", R)):
        if v.get(key) is not None:
            yy = sy(v[key])
            c.rect((gx + 72, yy - 1, gx + 86, yy + 1), fill=col)
            c.text(gx + 89, yy + 4 - _bl(c, "jos", 11), key.upper(), "jos", 11, col)

    x0, x1, T0, B0 = 199, 751, 41, 445
    W = x1 - x0
    y = T0
    head = " · ".join(t for t in (v["name"], v["station"], v["water"]) if t)
    y += _lab(c, x0, y, head, 13, 6, W, align="l") + 8
    # big value + status column
    num, unit = v["value_num"], v["unit"]
    bs = 108
    while bs > 50 and c.tw(num, "lime", bs) + 10 + c.tw(unit, "poiret", 30) > 300:
        bs -= 4
    c.text(x0, y + (108 - bs), num, "lime", bs, Wh, lh=1)
    bl = c._baseline(y + (108 - bs), "lime", bs, 1)
    nw = c.tw(num, "lime", bs)
    c.text(x0 + nw + 10, bl - _bl(c, "poiret", 30), unit, "poiret", 30, Y)
    sx = x0 + nw + 10 + c.tw(unit, "poiret", 30) + 28
    SW = x1 - sx - 22
    items = []
    if v.get("state_text"):
        items.append(("state", v["state_text"], 32, Wh))
    if v.get("trend_text"):
        items.append(("trend", v["trend_text"], 24, Y))
    if v.get("change_24h_text"):
        items.append(("chg", f"{v['change_24h_text']} / 24 h", 13, Y))
    if items:
        hs = [32 if k == "state" else 24 if k == "trend" else _lh(c, "jos", 13) for k, *_ in items]
        tot = sum(hs) + 8 * (len(hs) - 1)
        yy = y + (108 - tot) / 2
        c.vline(sx, yy - 4, yy + tot + 4, Y)
        tx = sx + 22
        for (k, t, s, col), h in zip(items, hs):
            if k == "chg":
                _lab(c, tx, yy, t, 13, 3, SW, align="l", upper=True)
            else:
                cy = yy + h / 2
                if k == "state":
                    sc = {"high": R, "low": B}.get(v.get("state"), G)
                    _dia(c, tx + 6, cy, 11, sc)
                    _dia(c, tx + 6, cy, 11, outline=Y)
                else:
                    tr_ = v.get("trend")
                    if tr_ == "rising":
                        c.poly([(tx + 6.5, cy - 6.5), (tx + 13, cy + 6.5), (tx, cy + 6.5)], fill=Y)
                    elif tr_ == "falling":
                        c.poly([(tx, cy - 6.5), (tx + 13, cy - 6.5), (tx + 6.5, cy + 6.5)], fill=Y)
                    else:
                        _dia(c, tx + 6.5, cy, 9, Y)
                ss, str_, tt = _fit1(c, t, "poiret", s, SW - 25, 0, 14)
                c.text(tx + 25, cy - ss / 2, tt, "poiret", ss, col, lh=1)
            yy += h + 8
    y += 108 + 8 + 2
    _dia(c, x0 + 4, y + 4, 8, Y)
    _dia(c, x1 - 4, y + 4, 8, Y)
    c.hline(x0 + 18, x1 - 18, y + 4, Y)
    y += 8 + 2 + 8
    # chart 551 × 190
    cx0, cy0 = x0, y
    fy = B0 - _lh(c, "jos", 11)
    ch = min(190, fy - 8 - cy0)
    base = cy0 + ch - 22
    lo_v = [x for x in (v.get("min"), v.get("mw")) if x is not None]
    hi_v = [x for x in (v.get("max"), v.get("hsw")) if x is not None]
    lo = min(lo_v) if lo_v else 0
    hi = max(hi_v) if hi_v else lo + 1
    pad = (hi - lo) * .12 or 10
    lo, hi = lo - pad * 1.5, hi + pad * .3
    top = cy0 + 8

    def cyv(val):
        return base - (val - lo) / (hi - lo) * (base - top)

    def cxv(f):
        return cx0 + 6 + f * 476

    labels = []
    for r in v.get("refs", []):
        yy = cyv(r["value"])
        col = R if r["key"] == "HSW" else Y
        if r["key"] == "HSW":
            c.dashed((cx0, yy, cx0 + 490, yy), col, 2, 8, 5)
        else:
            c.dashed((cx0, yy, cx0 + 490, yy), col, 1, 3, 5)
        labels.append((yy, f"{r['key']} {ctx.num(r['value'], 0)}", col))
    for yy, t, col in labels:
        s, tr, t = _fit1(c, t, "jos", 11, 551 - 496, 0, 8)
        c.text(cx0 + 496, yy + 4 - _bl(c, "jos", s), t, "jos", s, col)
    c.hline(cx0, cx0 + 490, base, Y)
    xs, vs = v.get("x") or [], v.get("values") or []
    if len(xs) >= 2:
        pts = [(cxv(f), cyv(val)) for f, val in zip(xs, vs)]
        c.stroke(pts, Wh, 3)
        ex, ey = pts[-1]
        c.poly([(ex, ey - 7), (ex + 7, ey), (ex, ey + 7), (ex - 7, ey)], fill=Wh)
    bounds = [0.0] + [t["x"] for t in v.get("day_ticks", [])] + [1.0]
    names = [None] + [t["weekday"] for t in v.get("day_ticks", [])]
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        if (b - a) * 476 < 26 or names[i] is None:
            continue
        c.text(cxv((a + b) / 2), base + 16 - _bl(c, "jos", 12) + 0, names[i], "jos", 12, Y, align="c")
    _lab(c, x0, fy, v["footer"], 11, 5, W, align="l")
    return c.finish()


# ================================================================== birthdays
def birthdays(ctx, v):
    c = _new()
    c.vline(322, Y0, Y1, Y)
    festive = v.get("festive")
    first = (v.get("celebrants") or [v["first"]])[0] if festive else v["first"]
    LC, LW = 173, 270
    lab = v["festive_title"] if festive else ctx.t("Next birthday", "Nächster Geburtstag")
    name = v["festive_names"] if festive else first["name"]
    sub = v["festive_line"] if festive else first["age_text"]
    ns = 84
    while ns > 30 and c.tw(name, "lime", ns) > LW:
        ns -= 2
    name = _ellip(c, name, "lime", ns, LW)
    when = first["when"]
    ws, wtr, when = _fit1(c, when, "poiret", 26, LW - 2 * 18 - 10, 0, 14)
    box_h = 6 + _lh(c, "poiret", 26) + 6 + 8
    hs = [50, _lh(c, "jos", 12), 8, 6 + ns, (_lh(c, "poiret", 30) if sub else None), _lh(c, "jos", 13), 8 + box_h]
    hs = [h for h in hs if h is not None]
    y = Y0 + (Y1 - Y0 - sum(hs) - 8 * (len(hs) - 1)) / 2
    _sunburst(c, LC, y + 50, 100, 48, 10, 18)
    y += 50 + 8
    y += _lab(c, LC, y, lab, 12, 5, LW) + 8
    _orn(c, LC, y + 4, 50, 8, R)
    y += 8 + 8 + 6
    c.text(LC, y, name, "lime", ns, R if festive else Wh, lh=1, align="c")
    y += ns + 8
    if sub:
        y += _lab(c, LC, y, sub, 30, 0, LW, Y, role="poiret", upper=False) + 8
    y += _lab(c, LC, y, first["date_long"], 13, 4, LW) + 8 + 8
    bw = c.tw(when, "poiret", ws) + 2 * 18 + 8
    c.rect((LC - bw / 2, y, LC + bw / 2, y + box_h), outline=Y, width=2)
    c.rect((LC - bw / 2 + 5, y + 5, LC + bw / 2 - 5, y + box_h - 5), outline=Y)
    c.text(LC, y + 4 + 6 + (_lh(c, "poiret", 26) - _lh(c, "poiret", ws)) / 2, when, "poiret", ws, Wh, align="c")

    x0, x1, T0, B0 = 351, 749, 45, 441
    W = x1 - x0
    d = v["today"]
    rd = _rdate(d)
    rw = c.tw(rd, "jos", 12, 4)
    hb = c._baseline(T0, "jos", 14, None)
    _lab(c, x0, T0, v["subtitle"], 14, 8, W - rw - 20, align="l")
    c.text(x1, hb - _bl(c, "jos", 12), rd, "jos", 12, Y, track=4, align="r")
    y = T0 + _lh(c, "jos", 14) + 8
    c.hline(x0, x1 - 16, y + 4, Y)
    _dia(c, x1 - 4, y + 4.5, 8, Y)
    y += 8 + 8
    if festive:
        names = {p["name"] for p in v.get("celebrants", [])}
        rest = [p for p in v["people"] if p.get("days", 1) != 0 or p["name"] not in names]
    else:
        rest = v["people"][1:]
    area = B0 - y
    n = min(len(rest), max(1, int(area // 62)), 6)
    if n == 0 or not rest:
        return c.finish()
    rh = area / n
    nwid = max(c.tw(p["name"], "poiret", 32) for p in rest[:n]) + 6
    nwid = max(96, min(nwid, 150))
    for i, p in enumerate(rest[:n]):
        ry = y + i * rh
        cy = ry + rh / 2
        if i < n - 1:
            c.hline(x0, x1, ry + rh - 1, Y)
        _dia(c, x0 + 5, cy, 9, Y)
        right = _in_days(c, x1, cy, p["when"], p["days"], 34, 46)
        nx = x0 + 9 + 16
        s, tr, t = _fit1(c, p["name"], "poiret", 32, nwid, 0, 18)
        c.text(nx, cy - _lh(c, "poiret", s) / 2, t, "poiret", s, Wh)
        dx = nx + nwid + 16
        DW = x1 - right - 16 - dx
        dh = _lh(c, "poiret", 22) + (3 + _lh(c, "jos", 12) if p.get("age_text") else 0)
        dy = cy - dh / 2
        _lab(c, dx, dy, p["date_short"], 22, 0, DW, Y, align="l", role="poiret", upper=False)
        if p.get("age_text"):
            _lab(c, dx, dy + _lh(c, "poiret", 22) + 3, p["age_text"], 12, 3, DW, align="l")
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    from ..plugins.watchlist import spark_points
    c = _new()
    L0, R0, T0, B0 = 51, 749, 39, 445
    W = R0 - L0
    sub = v["subtitle"]
    ts = 30
    th = _lh(c, "poiret", 30)
    s1, tr1, title = _fit1(c, v["title"].upper(), "poiret", 30, W * .45, 10, 18)
    tw_ = c.tw(title, "poiret", s1, tr1) - tr1
    c.text(L0, T0, title, "poiret", s1, Y, track=tr1, lh=th / s1)
    hb = c._baseline(T0, "poiret", s1, th / s1)
    s2, tr2, sub = _fit1(c, sub.upper(), "jos", 12, W - tw_ - 24, 4)
    c.text(R0, hb - _bl(c, "jos", s2), sub, "jos", s2, Y, track=tr2, align="r")
    y = T0 + th + 8
    c.hline(L0, 400 - 4 - 10 - 18 - 4, y + 4, Y)
    c.hline(400 + 4 + 10 + 18 + 4, R0, y + 4, Y)
    for k, col in ((-18, Y), (0, R), (18, Y)):
        _dia(c, 400 + k, y + 4.5, 8, col)
    y += 8 + 8
    # footer
    fh = _lh(c, "jos", 11)
    fy = B0 - fh
    c.hline(L0, R0, fy - 9, Y)
    rd = _rdate(v["today"])
    rw = c.tw(rd, "jos", 11, 4)
    c.text(R0, fy, rd, "jos", 11, Y, track=4, align="r")
    _lab(c, L0, fy, v["footer"], 11, 4, W - rw - 20, align="l")
    area = fy - 9 - 8 - y
    items = v["items"][:6]
    n = len(items)
    rh = area / max(1, n)
    big = rh >= 62
    for i, it in enumerate(items):
        ry = y + i * rh
        cy = ry + rh / 2
        if i < n - 1:
            c.hline(L0, R0, ry + rh - 1, Y)
        ns = 27 if big else 22
        k_line = ""
        if it.get("ok"):
            k_line = f"{ctx.t('{n} days', '{n} Tage', n=v['days'])} {it['period_text']}"
        elif it.get("error"):
            k_line = it["error"]
        hh = ns * 1.1 + (3 + _lh(c, "jos", 11) if k_line else 0)
        ny = cy - hh / 2
        s, tr, t = _fit1(c, it["label"], "poiret", ns, 186, 0, 14)
        c.text(L0, ny, t, "poiret", s, Wh, lh=1.1 * ns / s)
        if k_line:
            _lab(c, L0, ny + ns * 1.1 + 3, k_line, 11, 4, 186, R if not it.get("ok") else Y, align="l")
        vx = L0 + 186 + 18
        if not it.get("ok"):
            c.text(vx + 160, cy - 14, "–", "lime", 28, Wh, lh=1, align="r")
            continue
        vs = 28
        while vs > 14 and c.tw(it["last_text"], "lime", vs) > 160:
            vs -= 1
        c.text(vx + 160, cy - vs / 2, it["last_text"], "lime", vs, Wh, lh=1, align="r")
        col = COL.get(it.get("color"), K)
        bx = vx + 160 + 18
        chg = it["change_text"]
        cs, ctr, chg = _fit1(c, chg, "jos", 16, 104 - 12, 1, 10)
        cw_ = c.tw(chg, "jos", cs, ctr) - ctr + 20
        bh = _lh(c, "jos", cs) + 10
        bxc = bx + 52
        if col == K:
            c.rect((bxc - cw_ / 2, cy - bh / 2, bxc + cw_ / 2, cy + bh / 2), fill=K, outline=Y)
        else:
            c.rect((bxc - cw_ / 2, cy - bh / 2, bxc + cw_ / 2, cy + bh / 2), fill=col)
        c.text(bxc, cy - bh / 2 + 5 + 1, chg, "jos", cs, Wh, track=ctr, align="c", stroke=0)
        sx = bx + 104 + 18
        sw = R0 - sx
        sh = min(54, rh - 8)
        sy = cy - sh / 2
        vals = it["values"]
        if len(vals) >= 2:
            pts = spark_points(vals, sx + 2, sy + 6, sw - 10, sh - 12)
            mn, mx = min(vals), max(vals)
            fy0 = sy + 6 + (sh - 12) * (1 - (vals[0] - mn) / ((mx - mn) or 1))
            c.dashed((sx, fy0, R0, fy0), Y, 1, 2, 5)
            c.stroke(pts, col if col != K else Wh, 2.5)
            ex, ey = pts[-1]
            c.poly([(ex, ey - 5), (ex + 5, ey), (ex, ey + 5), (ex - 5, ey)], fill=Wh)
    return c.finish()
