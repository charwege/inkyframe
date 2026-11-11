"""Zen – signature layouts of the 15 plugins (ports of mockups/project/Zen-*.dc.html).

Washi paper, Cormorant Garamond light/italic for the big words, Zen Kaku Gothic in wide-tracked
capitals for labels, an ensō brush circle and the red date seal (hanko).
"""
from ..designs import _seal, lower_first
from ..plugins import _calendar as C
from ..studio import B, G, K, R, Y, Canvas, Wh

COL = {"black": K, "white": Wh, "red": R, "yellow": Y, "green": G, "blue": B}


# ================================================================== helpers
def _fit_line(c, text, role, size, width, track=0.0, min_size=8):
    """Size and track (scaled) so that one line fits; text ellipsised if even min_size is too wide."""
    s, tr = size, track
    while s > min_size and c.tw(text, role, s, tr) - tr > width:
        s -= 1
        tr = track * s / size
    if c.tw(text, role, s, tr) - tr > width:
        while len(text) > 1 and c.tw(text + "…", role, s, tr) - tr > width:
            text = text[:-1]
        text = text.rstrip(" ·,–-") + "…"
    return text, s, tr


def _one(c, x, top, text, role, size, width, fill=K, track=0.0, align="l", upper=False, lh=None, min_size=8):
    """One line that never exceeds width: shrinks (centred in the original line box), then ellipsises.
    Returns the height of the original line box."""
    if upper:
        text = text.upper()
    L = c.line_h(role, size, lh)
    if not text:
        return L
    text, s, tr = _fit_line(c, text, role, size, width, track, min_size)
    Ls = s * lh if lh else c.line_h(role, s)
    c.text(x, top + (L - Ls) / 2, text, role, s, fill, track=tr, lh=(Ls / s), align=align)
    return L


def _lab(c, x, top, text, width, size=12, track=8, fill=K, align="l"):
    """Wide-tracked capital label (Zen Kaku Gothic 400)."""
    return _one(c, x + (track / 2 if align == "c" else 0), top, text, "zk400", size, width, fill, track,
                align, upper=True)


def _vert(c, right, top, text, size, track, maxlen, fill=K):
    """writing-mode: vertical-rl – Latin text turned clockwise, right edge at `right`."""
    text = text.upper()
    if not text:
        return
    tr, s = track, size
    while c.tw(text, "zk400", s, tr) - tr > maxlen and tr > 2:
        tr -= 1
    text, s, tr = _fit_line(c, text, "zk400", s, maxlen, tr, 8)
    h = c.line_h("zk400", s)
    lay, ld = c.layer(c.tw(text, "zk400", s, tr) + 4, h)
    c.text(0, 0, text, "zk400", s, fill, track=tr, draw=ld)
    rot = lay.rotate(-90, expand=True)
    c.img.paste(rot, (round(right - rot.width), round(top)), rot)


def _date_seal(c, ctx, x, y, d=None):
    d = d or ctx.today
    mon = C.month(d, ctx.lang)[:3].upper()
    _seal(c, x, y, 58, [(str(d.day), "zk700", 18, 0), (mon, "zk700", 11, 1)])


def _rule(c, x, y, w=60):
    c.hline(x, x + w, y, K, 1)


def _enso(c, x, y, size, col=K, w1=9, w2=4):
    """The small ensō of the mockups (viewBox 0 0 150 150) scaled into a size × size box."""
    s = size / 150
    c.path("M 118 38 A 56 56 0 1 0 128 92", stroke=col, width=w1, dx=x, dy=y, sx=s)
    c.path("M 116 36 A 58 58 0 0 1 124 52", stroke=col, width=w2, dx=x, dy=y, sx=s)


def _para(c, x, top, text, role, size, width, height, lh, fill=K, min_size=10, track=0.0, upper=False,
          max_lines=None):
    """Wrapped block that fits width × height (shrinks, then cuts with an ellipsis). Returns height used."""
    size_, lines, L, tr = c.fit(text, role, size, width, height, lh=lh, track=track, min_size=min_size,
                                upper=upper)
    cap = max(1, int((height + 0.5) // L))
    if max_lines:
        cap = min(cap, max_lines)
    if len(lines) > cap:
        lines = lines[:cap]
        lines[-1] = _fit_line(c, lines[-1] + " …", role, size_, width, tr, size_)[0]
    lines = [_fit_line(c, ln, role, size_, width, tr, size_)[0] for ln in lines]
    c.para(x, top, width, lines, role, size_, L, fill, track=tr)
    return len(lines) * L


def _cap(s):
    return s[:1].upper() + s[1:] if s else s


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = Canvas("zen", Wh)
    # rank digits (space-around over 336 px), board with 1 px frame, file letters below
    bx, by, s = 75, 64, 42
    for i, rk in enumerate(v["ranks"]):
        if v.get("show_coords", True):
            c.text(56 + 4, by + 21 + i * 42 - 9, rk, "zk400", 11, K, align="c")
    c.rect((bx, by, bx + 8 * s + 2, by + 8 * s + 2), outline=K)
    last = {tuple(rc) for rc in v.get("last_cells") or []}
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            x0, y0 = bx + 1 + col * s, by + 1 + r * s
            bg = Y if (r + col) % 2 == 1 else Wh
            c.rect((x0, y0, x0 + s, y0 + s), fill=bg)
            if (r, col) in last:
                c.rect((x0, y0, x0 + s, y0 + s), outline=R, width=3)
            chess_puzzle.draw_piece(c.d, p, x0 + s // 2, y0 + s // 2, 40, ink=K, paper=Wh)
    if v.get("show_coords", True):
        for i, f in enumerate(v["files"]):
            c.text(bx + 1 + 21 + i * 42 + 1, by + 8 * s + 2 + 8, f, "zk400", 11, K, align="c")

    # right column
    X, Wd = 470, 274
    y = 64
    y += _lab(c, X, y, v["title"], Wd) + 14
    mate = v.get("mate") or ""
    y += _one(c, X, y, v["to_move"], "cg400i", 34, Wd, lh=1.0) + 14
    big = mate or v["side"]
    y += _one(c, X, y, big, "cg300", 68, Wd, lh=0.95, min_size=30) + 14
    _rule(c, X, y)
    y += 1 + 14
    if v.get("themes"):
        themes = " · ".join(t for t in v["themes"] if t != mate) or v["themes_text"]
        y += _para(c, X, y, themes, "zk400", 12, Wd, 12 * 1.6 * 2, 1.6, track=3, upper=True, min_size=10) + 14
    y += 6
    stats = []
    if v.get("rating"):
        stats.append((ctx.t("Rating", "Wertung"), str(v["rating"])))
    if v.get("moves"):
        stats.append((ctx.t("Solution", "Lösung"),
                      ctx.t("{n} moves", "{n} Züge", n=v["moves"]) if v["moves"] != 1
                      else ctx.t("{n} move", "{n} Zug", n=v["moves"])))
    sx = X
    for i, (lab, val) in enumerate(stats):
        room = (X + Wd - sx) if i == len(stats) - 1 else 120
        val, vs, _ = _fit_line(c, val, "cg300", 36, room, 0, 20)
        lab, ls, ltr = _fit_line(c, lab.upper(), "zk400", 11, room, 4, 8)
        c.text(sx, y, lab, "zk400", ls, K, track=ltr)
        c.text(sx, y + c.line_h("zk400", 11) + 2, val, "cg300", vs, K, lh=1.0)
        sx += max(c.tw(lab, "zk400", ls, ltr) - ltr, c.tw(val, "cg300", vs)) + 40
    # hint, vertical source line, seal
    _one(c, X, 480 - 52 - c.line_h("cg400i", 20), v["hint"], "cg400i", 20, 686 - 14 - X)
    src = v["source"] + (f" · {v['last_text']}" if v.get("last_text") else "")
    _vert(c, 770, 64, src, 12, 8, 480 - 64 - 44)
    _date_seal(c, ctx, 686, 378)
    return c.finish()


# ================================================================== spotify
def spotify(ctx, v):
    c = Canvas("zen", Wh)
    if v.get("image") is not None:
        c.img.paste(ctx.punch(ctx.cover_fit(v["image"], 320, 320)), (64, 80))
    else:       # the mockup's abstract stand-in
        c.rect((64, 80, 384, 400), fill=K)
        c.circle(64 + 196, 80 + 128, 66, fill=R)
        c.path("M 102 236 A 46 46 0 1 0 84 196", stroke=Wh, width=7, dx=64, dy=80)
        for yy, x1 in ((268, 288), (282, 210), (296, 132)):
            c.hline(64 + 32, 64 + x1, 80 + yy - 1, Wh, 2)
    X, Wd = 428, 288
    y = 80
    y += _lab(c, X, y, v["label"], Wd) + 18
    room = 3 * 40 * 1.12
    y += _para(c, X, y, v["track"], "cg400i", 40, Wd, room, 1.12, min_size=22) + 18
    _rule(c, X, y)
    y += 1 + 18
    if v.get("artist"):
        y += _lab(c, X, y, v["artist"], Wd, size=14, track=5) + 18
    if v.get("album"):
        _one(c, X, y, v["album"], "cg400i", 22, Wd)
    # bottom: plain rule (no playback position) + total length
    by = 480 - 50 - 40
    c.hline(X, X + 200, by + 6, K, 1)
    c.circle(X, by + 6, 5, fill=R)
    if v.get("duration_text"):
        c.text(X + 200, by + 22, v["duration_text"], "zk400", 12, K, track=3, align="r")
    side = v["source"] + (f" · {v['place']}" if v.get("place") else "")
    _vert(c, 770, 80, side, 13, 8, 480 - 80 - 44)
    _date_seal(c, ctx, 800 - 84 - 58, 480 - 44 - 58)
    return c.finish()


# ================================================================== grid
GRID_ADVICE = {
    "green": ("Wash, charge, run the dishwasher now", "Jetzt waschen, laden, spülen"),
    "yellow": ("Save electricity", "Strom sparen"),
    "red": ("Shift your consumption", "Verbrauch verschieben"),
}


def grid(ctx, v):
    c = Canvas("zen", Wh)
    col = COL.get(v.get("color") or "", K)
    _enso(c, 50, 40, 230, col)
    centre = v.get("place") or v.get("share_text") or ""
    _lab(c, 165, 155 - 10, centre, 150, size=13, track=6, align="c")
    _date_seal(c, ctx, 686, 56)
    X = 330
    y = 58
    y += _lab(c, X, y, f"{v['title']} · {v['time']}", 686 - 14 - X) + 10
    name = _cap(v["signal_name"]) if v.get("signal") is not None else "–"
    size, lines, L, _ = c.fit(name, "cg300", 120, 686 - 14 - X, 108, lh=0.9, min_size=40)
    if len(lines) > 1:
        size, lines, L, _ = c.fit(name, "cg300", 64, 406, 2 * 64 * 0.9, lh=0.9, min_size=30)
    c.para(X, y, 406, lines[:2], "cg300", size, L)
    y += max(108, len(lines[:2]) * L) + 10
    if v.get("share_text"):
        y += _one(c, X, y, ctx.t("{p} renewables", "{p} erneuerbar", p=v["share_text"]), "cg400i", 30, 406) + 10
    y += 6
    _rule(c, X, y)
    y += 1 + 10
    adv = GRID_ADVICE.get(v.get("color") or "")
    if adv and not v.get("congestion"):
        _lab(c, X, y, ctx.t(*adv), 406, size=14, track=4)
    elif v.get("congestion"):
        _lab(c, X, y, ctx.t(*GRID_ADVICE["red"]), 406, size=14, track=4)

    # 24 h band
    X0, Wb, top = 56, 688, 480 - 40 - 104
    if v.get("best_text"):
        _lab(c, X0 + Wb, top, v["best_text"], Wb, size=12, track=3, align="r")
    sy = top + 18 + 8

    def hx(h):
        return X0 + round(h / 24 * Wb)
    for sg in v.get("segments") or []:
        if sg.get("color") in COL:
            c.rect((hx(sg["start"]), sy + 24, hx(sg["end"]), sy + 36), fill=COL[sg["color"]])
    b = v.get("best")
    if b and b.get("day") == "today":
        c.hline(hx(b["start"]), hx(min(24, b["end"])), sy + 17, K, 2)
    nx = X0 + v.get("now_pos", 0) * Wb
    c.vline(nx - 1, sy + 8, sy + 48, K, 2)
    c.circle(nx, sy + 8, 5, fill=K)
    ty = sy + 52 + 8
    for i, h in enumerate(("00", "06", "12", "18", "24")):
        al = "l" if i == 0 else "r" if i == 4 else "c"
        xx = X0 + i * Wb / 4 + (0 if al == "l" else 0)
        c.text(xx + (1.5 if al == "c" else 0), ty, h, "zk400", 12, K, track=3, align=al)
    return c.finish()


# ================================================================== wordclock
def wordclock(ctx, v):
    c = Canvas("zen", Wh)
    _date_seal(c, ctx, 56, 60, v["today"])
    vt = f"{v['weekday']} · {ctx.t('WK {n}', 'KW {n}', n=v['week'])}"
    vw = c.line_h("zk400", 13)
    _vert(c, 85 + vw / 2, 60 + 58 + 22, vt, 13, 8, 480 - 140 - 44)
    rows, cols = v.get("rows") or len(v["grid"]), v.get("cols") or len(v["grid"][0])
    cw, ch = min(34, 374 / cols), min(36, 360 / rows)
    gx, gy = 213 + (374 - cw * cols) / 2, 60
    lit = {tuple(rc) for rc in v["lit"]}
    for r, line in enumerate(v["grid"]):
        for col, letter in enumerate(line):
            cx, cy = gx + col * cw + cw / 2, gy + r * ch + ch / 2
            if (r, col) in lit:
                c.text(cx, cy - c.line_h("zk700", 24) / 2, letter, "zk700", 24, R, align="c")
            else:
                c.text(cx, cy - c.line_h("zk400", 15) / 2, letter, "zk400", 15, K, align="c")
    _one(c, 213 + 187, 432, v["phrase_time"], "cg400i", 18, 374, align="c")
    # right column (centre 682)
    cx = 682
    y = 60
    c.text(cx, y, v["time"], "cg300", 44, K, lh=1.0, align="c")
    y += 44 + 12
    extra = max(0, min(4, (v["now"].hour * 60 + v["now"].minute) - (v["hour"] * 60 + v["minute"])))
    for i in range(4):
        dx = cx - 33 + i * 22
        if i < extra:
            c.circle(dx, y + 6, 6, fill=R)
        else:
            c.circle(dx, y + 6, 5, outline=K)
    y += 12 + 12
    if extra:
        _lab(c, cx, y, ctx.t("+ {n} min.", "+ {n} Min.", n=extra), 124, size=11, track=4, align="c")
    y += c.line_h("zk400", 11) + 12 + 22
    c.hline(cx - 20, cx + 20, y, K, 1)
    y += 1 + 10 + 12
    _enso(c, cx - 48, y, 96)
    y += 96 + 12
    y += _one(c, cx, y, v["moon"], "cg400i", 20, 150, align="c") + 12
    if v.get("place"):
        _lab(c, cx, y, v["place"], 150, size=11, track=4, align="c")
    return c.finish()


# ================================================================== countdown
def countdown(ctx, v):
    c = Canvas("zen", Wh)
    _enso(c, -36, 36, 400, K, 8, 3)
    # the big number in the circle
    big = v["big"]
    bs = 200 if len(big) <= 2 else 160 if len(big) == 3 else 120
    big, bs, _ = _fit_line(c, big, "cg300", bs, 280, 0, 40)
    small = v["small"].upper()
    # old-style figures descend below the baseline: keep the label clear of the ink
    base = c._baseline(0, "cg300", bs, 0.85)
    ink_bottom = max(bs * 0.85, base + c.font("cg300", bs).getbbox(big, anchor="ls")[3])
    tot = ink_bottom + (10 + c.line_h("zk400", 13) if small else 0)
    y = 236 - tot / 2
    c.text(164, y, big, "cg300", bs, K, lh=0.85, align="c")
    if small:
        _lab(c, 164, y + ink_bottom + 10, small, 270, size=13, track=10, align="c")
    # right column, vertically centred
    X, Wd = 400, 336
    lab_h = c.line_h("zk400", 12)
    size, ev_lines, evL, _ = c.fit(v["event"], "cg400i", 42, Wd, 3 * 42 * 1.12, lh=1.12, min_size=22)
    ev_lines = ev_lines[:3]
    date = f"{v['target_weekday']}, {v['date']}".upper()
    dsize, d_lines, dL, dtr = c.fit(date, "zk400", 13, Wd, 2 * 13 * 1.7, lh=1.7, track=4, min_size=10)
    d_lines = d_lines[:2]
    strip_h = 30 + 6 + c.line_h("zk400", 11)
    tot = lab_h + 20 + len(ev_lines) * evL + 20 + 1 + 20 + len(d_lines) * dL + 20 + 8 + strip_h
    y = (480 - tot) / 2
    y += _lab(c, X, y, v["title"], Wd) + 20
    c.para(X, y, Wd, ev_lines, "cg400i", size, evL)
    y += len(ev_lines) * evL + 20
    _rule(c, X, y)
    y += 1 + 20
    c.para(X, y, Wd, d_lines, "zk400", dsize, dL, track=dtr)
    y += len(d_lines) * dL + 20 + 8
    strip = v.get("strip") or []
    n = len(strip)
    if n >= 2:
        step = 328 / (n - 1)
        for i, e in enumerate(strip):
            mark = e["weekday"] == 6 or e.get("special")
            if step < 2.5 and not (mark or e.get("first_of_month")):
                continue
            x = X + 4 + round(i * step)
            c.vline(x - (1 if mark else 0), y + (12 if mark else 18), y + 26, K, 2 if mark else 1)
    c.circle(X + 4, y + 8, 4, fill=R)
    c.rrect((X + 326, y, X + 336, y + 10), 2, fill=R)
    y += 30 + 6
    now_lab = f"{ctx.t('Today', 'Heute')} · {v['today_short']}"
    left, right = (now_lab, v["date_short"]) if v["state"] != "past" else (v["date_short"], now_lab)
    mid = f"{ctx.t('WK {n}', 'KW {n}', n=v['week_from'])} – {ctx.t('WK {n}', 'KW {n}', n=v['week_to'])}"
    wl = c.tw(left.upper(), "zk400", 11, 3) - 3
    wr = c.tw(right.upper(), "zk400", 11, 3) - 3
    _lab(c, X, y, left, Wd / 2, size=11, track=3)
    _lab(c, X + Wd, y, right, Wd / 2, size=11, track=3, align="r")
    wm = c.tw(mid.upper(), "zk400", 11, 3) - 3
    if v["week_from"] != v["week_to"] and wl + wr + wm + 24 < Wd:
        _lab(c, X + wl + (Wd - wl - wr) / 2, y, mid, Wd, size=11, track=3, align="c")
    doy = v["today"].timetuple().tm_yday
    vt = ((v["place"] + " · ") if v.get("place") else "") + ctx.t("Day {n}", "Tag {n}", n=doy)
    _vert(c, 770, 56, vt, 12, 8, 480 - 56 - 44)
    return c.finish()


# ================================================================== art
def art(ctx, v):
    c = Canvas("zen", Wh)
    img = v["image"]
    sw, sh = 414, 338
    k = min(sw / img.width, sh / img.height)
    iw, ih = max(1, round(img.width * k)), max(1, round(img.height * k))
    fw, fh = iw + 44 + 2, ih + 44 + 2
    fx, fy = 56 + (460 - fw) / 2, 48 + (384 - fh) / 2
    c.rect((fx, fy, fx + fw, fy + fh), outline=K)
    c.img.paste(img.convert("RGB").resize((iw, ih)), (round(fx + 23), round(fy + 23)))
    _date_seal(c, ctx, fx + fw - 29, fy + fh - 29, v["today"])
    X, Wd = 556, 188
    y = 48
    y += _para(c, X, y, v["title"].upper(), "zk400", 12, Wd, 2 * 12 * 1.7, 1.7, track=6, min_size=9) + 16
    if v.get("artist"):
        y += _para(c, X, y, v["artist"], "cg400i", 34, Wd, 2 * 34 * 1.08, 1.08, min_size=20) + 16
    _rule(c, X, y)
    y += 1 + 16
    y += _para(c, X, y, v["work"], "cg300", 30, Wd, 3 * 30 * 1.1, 1.1, min_size=18) + 16
    if v.get("date"):
        y += _one(c, X, y, v["date"], "cg300", 52 if len(v["date"]) <= 6 else 30, Wd, lh=1.0, min_size=16) + 16
    mus = " · ".join(s for s in (v.get("museum"), v.get("museum_city")) if s)
    _para(c, X, y, mus.upper(), "zk400", 12, Wd, min(2 * 12 * 1.7, 436 - y), 1.7, track=4, min_size=9)
    return c.finish()


# ================================================================== waste
def _bin(c, x, y, s, col, lid=True, sw=1.5):
    """Mockup bin (viewBox 0 0 40 52) at (x, y), scale s."""
    line = Wh if col == K else K
    if lid:
        c.rect((x + 14 * s, y + 1 * s, x + 26 * s, y + 5 * s), fill=K)
    c.rect((x + 2 * s, y + 6 * s, x + 38 * s, y + 11 * s), fill=col)
    body = [(x + 5 * s, y + 13 * s), (x + 35 * s, y + 13 * s), (x + 32 * s, y + 50 * s), (x + 8 * s, y + 50 * s)]
    c.poly(body, fill=col)
    if col != K:
        c.rect((x + 2 * s, y + 6 * s, x + 38 * s, y + 11 * s), outline=K, width=max(1, round(sw * s)))
        c.poly(body, outline=K, width=max(1, round(sw * s)))
    if lid:
        c.stroke([(x + 15 * s, y + 19 * s), (x + 16 * s, y + 44 * s)], line, max(1, round(sw * s)))
        c.stroke([(x + 25 * s, y + 19 * s), (x + 24 * s, y + 44 * s)], line, max(1, round(sw * s)))


def waste(ctx, v):
    c = Canvas("zen", Wh)
    soon, rows = v.get("soon"), list(v.get("rows") or [])
    if soon:
        big, items, sub = soon["label"], soon["items"], soon["date_long"]
        names = soon["names_text"]
    else:       # nothing today/tomorrow: the next pickup day takes the big slot
        d0 = rows[0]["date"]
        day = [r for r in rows if r["date"] == d0]
        rows = [r for r in rows if r["date"] != d0]
        big, items, sub = _cap(day[0]["in_text"]), day, day[0]["date_long"]
        names = " + ".join(r["name"] for r in day)
    X, Wd = 56, 360
    y = 56
    head = v["title"] + (f" · {v['place']}" if v.get("place") else "")
    y += _lab(c, X, y, head, Wd) + 10
    y += _one(c, X, y, big, "cg300", 112, Wd, lh=0.95, min_size=40) + 10
    y += _para(c, X, y, names, "cg400i", 32, Wd, 2 * 32 * 1.1, 1.1, min_size=18) + 10 + 4
    _lab(c, X, y, sub, Wd, size=12, track=4)
    bx = 56
    for it in items[:3]:
        _bin(c, bx, 480 - 44 - 96 + 0.5, 1.8, COL.get(it["color"], K))
        bx += 72 + 28
    _date_seal(c, ctx, bx + 20, 480 - 44 - 58, v["today"])
    c.vline(456, 56, 480 - 44, K, 1)
    X, Wd = 488, 256
    y = 56
    y += _lab(c, X, y, ctx.t("Later", "Danach"), Wd) + 18
    if not rows:
        _para(c, X, y + 12, v["empty_text"], "cg400i", 20, Wd, 80, 1.2, min_size=14)
    for it in rows[:4]:
        c.hline(X, X + Wd, y, K, 1)
        cy = y + 42
        _bin(c, X, cy - 17, 0.65, COL.get(it["color"], K), lid=False, sw=3)
        days = it["in_text"]
        dw = min(110, c.tw(days, "cg400i", 20))
        tx, tw_ = X + 26 + 14, Wd - 26 - 14 - dw - 14
        bh = 24 + 2 + c.line_h("zk400", 11)
        _one(c, tx, cy - bh / 2, it["name"], "cg300", 24, tw_, lh=1.0)
        _lab(c, tx, cy - bh / 2 + 26, f"{it['weekday_short']} {it['date_short']}", tw_, size=11, track=4)
        _one(c, X + Wd, cy - c.line_h("cg400i", 20) / 2, days, "cg400i", 20, dw, align="r")
        y += 84
    return c.finish()


# ================================================================== warnings
_WIND = ("wind", "sturm", "böe", "boe", "orkan", "storm", "gust", "gale", "hurricane", "tempête", "rafale")


def warnings(ctx, v):
    c = Canvas("zen", Wh)
    _date_seal(c, ctx, 56, 56, v["today"])
    vw = c.line_h("zk400", 13)
    _vert(c, 85 + vw / 2, 56 + 58 + 22, v["level_text"], 13, 8, 480 - 136 - 44)
    ev = v["event"].lower()
    ix, iy = 800 - 56 - 180, 56
    if any(w in ev for w in _WIND):     # the mockup's brushed gusts
        c.path("M 6 34 L 120 34 A 22 22 0 1 0 98 12", stroke=K, width=6, dx=ix, dy=iy)
        c.path("M 26 62 L 150 62 A 18 18 0 1 1 132 80", stroke=K, width=4, dx=ix, dy=iy)
        c.path("M 46 90 L 104 90", stroke=R, width=6, dx=ix, dy=iy)
    else:                               # other hazards: the ensō with a red stroke
        _enso(c, ix + 60, iy, 100)
        c.path("M 46 110 L 104 110", stroke=R, width=6, dx=ix + 40, dy=iy)
    X, Wd = 170, 566
    y = 60
    size, lines, L, _ = c.fit(v["event"], "cg300", 96, ix - 14 - X, 96 * 0.95, lh=0.95, min_size=48)
    if len(lines) > 1:
        size, lines, L, _ = c.fit(v["event"], "cg300", 56, ix - 14 - X, 2 * 56 * 0.95, lh=0.95, min_size=30)
        lines = lines[:2]
    c.para(X, y, Wd, lines, "cg300", size, L)
    y = max(y + len(lines) * L + 14, 162)
    # level dots · level name · "level n of 4"
    col = COL.get(v.get("color"), R)
    rh = c.line_h("cg400i", 24)
    for i in range(v.get("levels") or 4):
        cx = X + 8 + i * 24
        if i < v["level"]:
            c.circle(cx, y + rh / 2, 8, fill=col)
        c.circle(cx, y + rh / 2, 8, outline=K)
    x = X + 24 * (v.get("levels") or 4) - 8 + 16
    lv = ctx.t("Level {n} of {m}", "Stufe {n} von {m}", n=v["level"], m=v.get("levels") or 4).upper()
    lvw = c.tw(lv, "zk400", 11, 4) - 4
    name, ns, _ = _fit_line(c, v["level_text"], "cg400i", 24, X + Wd - x - 16 - lvw, 0, 16)
    c.text(x, y + (rh - c.line_h("cg400i", ns)) / 2, name, "cg400i", ns, K)
    x += c.tw(name, "cg400i", ns) + 16
    c.text(x, y + (rh - c.line_h("zk400", 11)) / 2, lv, "zk400", 11, K, track=4)
    y += rh + 14
    if v.get("place_span"):
        y += _lab(c, X, y, v["place_span"], Wd, size=13, track=4) + 14
    y += 4
    _rule(c, X, y)
    y += 1 + 14
    bottom = 480 - 44 - c.line_h("zk400", 12) - 14
    if v.get("more_text"):
        bottom -= c.line_h("cg400i", 20) + 6
        _one(c, X, bottom + 6 - 3, v["more_text"], "cg400i", 20, Wd)
    body = v["description"] + (("\n" + v["instruction"]) if v.get("instruction") else "")
    if bottom - y > 30:
        _para(c, X, y, body, "cg400i", 24, Wd, bottom - y - 8, 1.32, min_size=15)
    _lab(c, X, 480 - 44 - c.line_h("zk400", 12), f"{ctx.t('Source', 'Quelle')} · {v['source']}", Wd)
    return c.finish()


# ================================================================== wifi
def wifi(ctx, v):
    from ..plugins.wifi import draw_modules
    c = Canvas("zen", Wh)
    c.rect((64, 70, 64 + 321, 70 + 321), outline=K)
    draw_modules(c.d, v["modules"], 64 + 23, 70 + 23, 275, dark=K, light=Wh, quiet=0)
    _one(c, 64 + 160.5, 412, v["hint"], "cg400i", 20, 321, align="c")
    X, Wd = 440, 296
    y = 70
    y += _lab(c, X, y, v["title"], Wd) + 10
    size, lines, L, _ = c.fit(v["ssid"], "cg300", 104, Wd, 104 * 0.95, lh=0.95, min_size=40)
    if len(lines) > 1:
        size, lines, L, _ = c.fit(v["ssid"], "cg300", 52, Wd, 2 * 52 * 0.95, lh=0.95, min_size=24)
        lines = [_fit_line(c, ln, "cg300", size, Wd)[0] for ln in lines[:2]]
    c.para(X, y, Wd, lines, "cg300", size, L)
    y += max(99, len(lines) * L) + 10 + 10
    _rule(c, X, y)
    y += 1 + 10 + 10
    if v.get("password"):
        y += _lab(c, X, y, v["password_label"], Wd, size=11, track=6) + 10
        y += _one(c, X, y, v["password"], "cg400i", 40, Wd, lh=1.0, min_size=16) + 14
    y += _lab(c, X, y, ctx.t("Encryption", "Verschlüsselung"), 678 - 12 - X, size=11, track=6) + 10
    sec = v.get("security") or ctx.t("Open network", "Offenes Netz")
    _lab(c, X, y, sec, 678 - 12 - X, size=16, track=6)
    side = " · ".join(s for s in (v.get("note"), v.get("place")) if s)
    _vert(c, 770, 70, side, 12, 8, 480 - 70 - 44 - 58 - 16)
    _date_seal(c, ctx, 800 - 64 - 58, 480 - 44 - 58, v["today"])
    return c.finish()


# ================================================================== habits
def _at_base(c, x, base, text, role, size, fill=K, track=0.0, align="l"):
    c.text(x, base - c._baseline(0, role, size, None), text, role, size, fill, track=track, align=align)


def habits(ctx, v):
    c = Canvas("zen", Wh)
    _lab(c, 56, 50, v["title"], 600)
    _one(c, 56, 50 + c.line_h("zk400", 12) + 6, ctx.t("the last six weeks", "die letzten sechs Wochen"),
         "cg400i", 22, 600)
    _date_seal(c, ctx, 800 - 56 - 58, 50, v["today"])
    hs = v["habits"][:6]
    small = len(hs) > 4
    ns, ss, gap, cell, dgap, wgap, hgap = (22, 24, 5, 11, 2, 5, 9) if small else (26, 30, 8, 13, 3, 6, 22)
    y = 132
    unit = ctx.t("days in a row", "Tage in Folge").upper()
    for h in hs:
        base = y + ss * 0.8
        num = str(h["streak"])
        uw = c.tw(unit, "zk400", 11, 4) - 4
        _at_base(c, 744, base, unit, "zk400", 11, K, track=4, align="r")
        nw = c.tw(num, "cg300", ss)
        _at_base(c, 744 - uw - 8, base, num, "cg300", ss, R if h.get("hot") else K, align="r")
        name, nsz, _ = _fit_line(c, h["name"], "cg400i", ns, 688 - uw - nw - 8 - 24, 0, 14)
        _at_base(c, 56, base, name, "cg400i", nsz)
        y += ss + gap
        days = h["days"][-42:]
        x = 56
        for i, done in enumerate(days):
            if i and i % 7 == 0:
                x += wgap - dgap
            today = i == len(days) - 1
            if done:
                c.rect((x, y, x + cell, y + cell), fill=R if today else K)
            else:
                c.rect((x, y, x + cell, y + cell), outline=K)
            x += cell + dgap
        y += cell + hgap
    _lab(c, 744, 480 - 26 - c.line_h("zk400", 11),
         f"{ctx.t('Today', 'Heute')} · {v['weekday_short']} {v['date_short']}", 688, size=11, track=4, align="r")
    return c.finish()


# ================================================================== sudoku
def sudoku(ctx, v):
    c = Canvas("zen", Wh)
    x0, y0, s = 64, 50, 42
    c.rect((x0, y0, x0 + 384, y0 + 384), outline=K, width=3)
    for i in range(8):
        w = 3 if i % 3 == 2 else 1
        p = 67 + (i + 1) * s
        c.rect((p - w, y0 + 3, p, y0 + 381), fill=K)                 # vertical
        c.rect((x0 + 3, y0 + 3 + (i + 1) * s - w, x0 + 381, y0 + 3 + (i + 1) * s), fill=K)  # horizontal
    for r, row in enumerate(v["grid"]):
        for col, n in enumerate(row):
            if n:
                cx = x0 + 3 + col * s + (s - (1 if col % 3 != 2 else 3)) / 2
                cy = y0 + 3 + r * s + (s - (1 if r % 3 != 2 else 3)) / 2
                f = c.font("cg300", 30)
                l_, t_, r_, b_ = f.getbbox(str(n), anchor="ls")     # centre the ink (old-style figures)
                c.d.text((cx - (l_ + r_) / 2, cy - (t_ + b_) / 2), str(n), font=f, fill=K, anchor="ls")
    X, Wd = 500, 236
    y = 56
    y += _para(c, X, y, v["name"].upper(), "zk400", 12, Wd, 2 * 12 * 1.7, 1.7, track=8, min_size=9) + 14
    y += _one(c, X, y, v["level_name"], "cg300", 84, Wd, lh=0.95, min_size=30) + 14
    for i in range(v.get("level_max") or 3):
        cx = X + 7 + i * 24
        if i < v["level_no"]:
            c.circle(cx, y + 9, 7, fill=K)
        else:
            c.circle(cx, y + 9, 7, outline=K)
    lx = X + 24 * (v.get("level_max") or 3) - 10 + 6 + 10
    lv = ctx.t("Level {n} of {m}", "Stufe {n} von {m}", n=v["level_no"], m=v.get("level_max") or 3)
    _lab(c, lx, y + 9 - c.line_h("zk400", 11) / 2, lv, X + Wd - lx, size=11, track=4)
    y += 18 + 14 + 8
    _rule(c, X, y)
    y += 1 + 14
    _para(c, X, y, v["givens_text"].upper(), "zk400", 12, Wd, 2 * 12 * 1.7, 1.7, track=4, min_size=9)
    _one(c, X, 480 - 52 - c.line_h("cg400i", 20), v["hint"], "cg400i", 20, 678 - 12 - X)
    _date_seal(c, ctx, 800 - 64 - 58, 480 - 44 - 58, v["today"])
    doy = v["today"].timetuple().tm_yday
    wk = v["today"].isocalendar()[1]
    vt = f"{ctx.t('Day {n}', 'Tag {n}', n=doy)} · {ctx.t('WK {n}', 'KW {n}', n=wk)}"
    _vert(c, 770, 56, vt, 12, 8, 480 - 56 - 44 - 58 - 16)
    return c.finish()


# ================================================================== solar
def solar(ctx, v):
    c = Canvas("zen", Wh)
    sx, sy = 800 - 64 - 150, 40
    c.circle(sx + 75, sy + 75, 46, fill=R)
    _enso(c, sx, sy, 150, K, 4, 2)
    X = 56
    head = v["title"] + (f" · {v['place']}" if v.get("place") else "")
    y = 50 + _lab(c, X, 50, head, sx - 14 - X) + 4
    num = v["power_text"].rsplit(" ", 1)[0] if " " in v["power_text"] else str(v["power_w"])
    unit = ctx.t("Watt", "Watt")
    room = sx - 14 - X
    ns = 140
    while ns > 50 and c.tw(num, "cg300", ns) + 12 + c.tw(unit, "cg400i", ns * 40 / 140) > room:
        ns -= 2
    us = round(ns * 40 / 140)
    base = y + c._baseline(0, "cg300", ns, 0.95)
    c.text(X, y, num, "cg300", ns, K, lh=0.95)
    _at_base(c, X + c.tw(num, "cg300", ns) + 12, base, unit, "cg400i", us)
    ink_bottom = base + c.font("cg300", ns).getbbox(num, anchor="ls")[3]
    # three figures
    stats = [(ctx.t("Today", "Heute"), v["today_text"], "cg300"),
             (ctx.t("Saved", "Gespart"), f"≈ {v['saved_text']}", "cg400i")]
    if v.get("total_text"):
        stats.append((ctx.t("In total", "Insgesamt"), v["total_text"], "cg300"))
    elif v.get("max_text"):
        stats.append((ctx.t("Peak", "Spitze"), v["max_text"], "cg300"))
    x0, x1, n = 240, 736, len(stats)
    colw = (x1 - x0 - 24 * (n - 1)) / n
    widths = []
    fitted = []
    for lab, val, role in stats:
        lab_, ls, ltr = _fit_line(c, lab.upper(), "zk400", 11, colw, 4, 8)
        val_, vs, _ = _fit_line(c, val, role, 30, colw, 0, 16)
        fitted.append((lab_, ls, ltr, val_, vs, role))
        widths.append(max(c.tw(lab_, "zk400", ls, ltr) - ltr, c.tw(val_, role, vs)))
    gap = (x1 - x0 - sum(widths)) / (n - 1) if n > 1 else 0
    xx = x0
    for (lab_, ls, ltr, val_, vs, role), w in zip(fitted, widths):
        c.text(xx, 214, lab_, "zk400", ls, K, track=ltr)
        c.text(xx, 214 + c.line_h("zk400", 11) + 4, val_, role, vs, K, lh=1.0)
        xx += w + gap
    _date_seal(c, ctx, 56, min(230, max(210, ink_bottom + 8)), v["today"])
    # day curve
    CX, CW, CY = 56, 688, 480 - 40 - 146
    ticks = v.get("ticks") or [6, 9, 12, 15, 18, 21]
    t0, t1 = ticks[0], ticks[-1]
    peak = v.get("peak") or 1

    def px(h):
        return CX + (h - t0) / (t1 - t0) * CW

    def py(w):
        return CY + 118 - min(max(w, 0), peak) / peak * 100
    pts = [(px(h), py(w)) for h, w in zip(v.get("hours") or [], v.get("watts") or []) if t0 <= h <= t1]
    if len(pts) >= 2:
        c.poly([(pts[0][0], CY + 119)] + pts + [(pts[-1][0], CY + 119)], fill=Y)
        c.stroke(pts, K, 2, cap=False)
    c.hline(CX, CX + CW, CY + 119, K, 1)
    if v.get("now_visible") and len(pts) >= 2:
        nx, ny = pts[-1]
        c.vline(nx, ny, CY + 119, K, 1)
        c.circle(nx, ny, 6, fill=R)
    labels = v.get("tick_labels") or [f"{t:02d}" for t in ticks]
    for i, (t, lab) in enumerate(zip(ticks, labels)):
        al = "l" if i == 0 else "r" if i == len(ticks) - 1 else "c"
        c.text(px(t) + (2 if al == "c" else 0), CY + 128, lab, "zk400", 12, K, track=4, align=al)
    return c.finish()


# ================================================================== waterlevel
def waterlevel(ctx, v):
    c = Canvas("zen", Wh)
    _date_seal(c, ctx, 56, 56, v["today"])
    vt = " · ".join(s for s in (v.get("station"), v.get("water")) if s)
    vw = c.line_h("zk400", 14)
    _vert(c, 85 + vw / 2, 56 + 58 + 22, vt, 14, 8, 480 - 136 - 44)
    X, Wd = 156, 240
    y = 64
    y += _lab(c, X, y, v["name"], Wd) + 8
    num, unit = v["value_num"], v.get("unit") or ""
    ns = 128
    while ns > 48 and c.tw(num, "cg300", ns) + 10 + c.tw(unit, "cg400i", 32) > Wd:
        ns -= 2
    base = y + c._baseline(0, "cg300", ns, 0.95)
    col = R if v.get("high") else K
    c.text(X, y, num, "cg300", ns, col, lh=0.95)
    if unit and v.get("value") is not None:
        _at_base(c, X + c.tw(num, "cg300", ns) + 10, base, unit, "cg400i", 32)
    y += 128 * 0.95 + 8
    if v.get("state_text"):
        y += _one(c, X, y, v["state_text"], "cg400i", 34, Wd, fill=col, lh=1.0) + 8
    y += 12
    _rule(c, X, y)
    y += 1 + 4 + 8
    if v.get("trend"):
        ay = y + 11
        if v["trend"] == "rising":
            c.stroke([(X + 3, y + 19), (X + 17, y + 5)], K, 2)
            c.stroke([(X + 8, y + 4), (X + 18, y + 4), (X + 18, y + 14)], K, 2)
        elif v["trend"] == "falling":
            c.stroke([(X + 3, y + 3), (X + 17, y + 17)], K, 2)
            c.stroke([(X + 8, y + 18), (X + 18, y + 18), (X + 18, y + 8)], K, 2)
        else:
            c.stroke([(X + 2, ay), (X + 19, ay)], K, 2)
            c.stroke([(X + 13, ay - 6), (X + 19, ay), (X + 13, ay + 6)], K, 2)
        _lab(c, X + 32, ay - c.line_h("zk400", 13) / 2, v["trend_text"], Wd - 32, size=13, track=4)
        y += 22 + 8
    if v.get("change_24h_text"):
        _one(c, X, y, f"{v['change_24h_text']} / 24 h", "zk400", 13, Wd, track=4)
    # chart
    GX, GY, GW = 404, 64, 340
    vals = v.get("values") or []
    xs = v.get("x") or []
    refs = {r["key"]: r for r in v.get("refs") or []}
    if len(vals) >= 2 and len(xs) == len(vals):
        pool = vals + [r["value"] for r in refs.values()]
        lo, hi = min(pool), max(pool)
        span = (hi - lo) or 1
        vmin, vmax = lo - 0.18 * span, hi + 0.1 * span

        def gy(val):
            return GY + 290 - (val - vmin) / (vmax - vmin) * 280
        for key, colr, above in (("HSW", R, True), ("MW", B, False)):
            if key in refs:
                ly = gy(refs[key]["value"])
                c.dashed((GX, ly, GX + GW, ly), colr, 1, 6, 5)
                lt = GY + (ly - GY) - 22 if above else ly + 8
                lt = min(max(lt, GY - 18), GY + 300 - 20)
                _lab(c, GX, lt, f"{key} · {refs[key]['text'].split(' ', 1)[-1]}", GW, size=11, track=3, fill=colr)
        step = max(1, len(vals) // 340)
        pts = [(GX + xs[i] * 330, gy(vals[i])) for i in range(0, len(vals), step)]
        if pts[-1][0] != GX + xs[-1] * 330:
            pts.append((GX + xs[-1] * 330, gy(vals[-1])))
        c.stroke(pts, K, 2, cap=False)
        c.circle(pts[-1][0], pts[-1][1], 6, fill=R)
    c.hline(GX, GX + GW, GY + 299, K, 1)
    ticks = v.get("day_ticks") or []
    edges = [t["x"] for t in ticks] + [1.0]
    for i, t in enumerate(ticks):
        mid = (edges[i] + edges[i + 1]) / 2 * 330
        if edges[i + 1] - edges[i] < 0.06:
            continue
        _lab(c, GX + mid, GY + 308, t["weekday"], 60, size=11, track=3, align="c")
    _lab(c, X, 480 - 44 - c.line_h("zk400", 11), f"{ctx.t('Source', 'Quelle')} · {v['source']}",
         744 - X, size=11, track=4)
    return c.finish()


# ================================================================== birthdays
def birthdays(ctx, v):
    c = Canvas("zen", Wh)
    festive = bool(v.get("festive"))
    _enso(c, 20, 40, 300, R if festive else K, 8, 3)
    cx, cy = 170, 190
    first = v["first"]
    if festive:
        size, lines, L, tr = c.fit(v["festive_title"].upper(), "zk400", 13, 190, 4 * 13 * 1.7, lh=1.7, track=8,
                                   min_size=9)
        lines = lines[:4]
        y = cy - len(lines) * L / 2
        for ln in lines:
            c.text(cx + tr / 2, y, ln, "zk400", size, K, track=tr, lh=1.7, align="c")
            y += L
    elif first["days"] == 1:
        _one(c, cx, cy - c.line_h("cg400i", 44) / 2, first["when"], "cg400i", 44, 200, align="c")
    else:
        tpl = ctx.t("in {n} days", "in {n} Tagen")
        pre, post = tpl.split("{n}", 1) if "{n}" in tpl else ("", tpl)
        big = str(first["days"])
        bs = 130 if len(big) <= 2 else 100
        base = c._baseline(0, "cg300", bs, 0.85)
        ink_top = base + c.font("cg300", bs).getbbox(big, anchor="ls")[1]
        ink_bottom = base + c.font("cg300", bs).getbbox(big, anchor="ls")[3]
        lh = c.line_h("zk400", 12)
        tot = (lh + 8 if pre.strip() else 0) + ink_bottom - ink_top + (lh + 8 if post.strip() else 0)
        y = cy - tot / 2
        if pre.strip():
            _lab(c, cx, y, pre.strip(), 200, align="c")
            y += lh + 8
        c.text(cx, y - ink_top, big, "cg300", bs, K, lh=0.85, align="c")
        y += ink_bottom - ink_top + 8
        if post.strip():
            _lab(c, cx, y, post.strip(), 200, align="c")
    _date_seal(c, ctx, 56, 480 - 44 - 58, v["today"])
    side = [ctx.t("Today", "Heute")] + ([v["place"]] if v.get("place") else [])
    sy = 480 - 44 - 29 - len(side) * 11 * 1.7 / 2
    for s in side:
        _lab(c, 132, sy, s, 200, size=11, track=4)
        sy += 11 * 1.7
    X, Wd = 372, 372
    y = 56
    y += _lab(c, X, y, v["title"], Wd) + 10
    if festive:
        y += _one(c, X, y, v["festive_names"], "cg400i", 52, Wd, lh=1.0, min_size=24) + 10
        if v.get("festive_line"):
            _lab(c, X, y, v["festive_line"], Wd, size=13, track=4)
        rest = [p for p in v["people"] if p["days"] > 0][:4]
    else:
        head = f"{first['name']} {first['age_text']}".strip()
        y += _one(c, X, y, head, "cg400i", 52, Wd, lh=1.0, min_size=24) + 10
        _lab(c, X, y, first["date_long"], Wd, size=13, track=4)
        rest = v["others"][:4]
    _rule(c, X, 196)
    if not rest:
        return c.finish()
    dw = min(90, max(c.tw(p["date_short"], "zk400", 12, 3) - 3 for p in rest))
    ww = min(120, max(c.tw(p["when"], "cg400i", 20) for p in rest))
    aw = min(110, max([c.tw(p["age_text"].upper(), "zk400", 11, 3) - 3 for p in rest] + [0]))
    nw = Wd - dw - ww - aw - 14 * 3
    y = 220
    for p in rest:
        base = y + 28 * 0.8 + 4
        _at_base(c, X, base, _fit_line(c, p["date_short"], "zk400", 12, dw, 3, 12)[0], "zk400", 12, track=3)
        nm, ns, _ = _fit_line(c, p["name"], "cg300", 28, nw, 0, 16)
        _at_base(c, X + dw + 14, base, nm, "cg300", ns)
        if p["age_text"]:
            at, asz, atr = _fit_line(c, p["age_text"].upper(), "zk400", 11, aw, 3, 11)
            _at_base(c, X + dw + 14 + nw + 14, base, at, "zk400", asz, track=atr)
        wt, ws, _ = _fit_line(c, p["when"], "cg400i", 20, ww, 0, 20)
        _at_base(c, X + Wd, base, wt, "cg400i", ws, align="r")
        y += 52
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    from ..plugins.watchlist import spark_points
    c = Canvas("zen", Wh)
    _lab(c, 56, 50, v["title"], 600)
    _one(c, 56, 50 + c.line_h("zk400", 12) + 6, v["subtitle"], "cg400i", 22, 686 - 14 - 56)
    _date_seal(c, ctx, 800 - 56 - 58, 50, v["today"])
    items = v["items"][:6]
    rh = min(70, (420 - 132) / max(1, len(items)))
    k = min(1.0, (rh + 12) / 82)
    X, Wd = 56, 688
    y = 132
    for it in items:
        c.hline(X, X + Wd, y, K, 1)
        cy = y + rh / 2
        col = COL.get(it.get("color"), K) if it.get("ok") else K
        ns = round(28 * k)
        _one(c, X, cy - ns / 2, it["label"], "cg400i", ns, 190, lh=1.0, min_size=12)
        ps = round(32 * k)
        if it.get("ok"):
            _one(c, X + 190 + 16 + 150, cy - ps / 2 - 1, it["last_text"], "cg300", ps, 150, lh=1.0, align="r",
                 min_size=14)
            _one(c, X + 190 + 16 + 150 + 16 + 92, cy - c.line_h("zk400", 14) / 2, it["change_text"], "zk400",
                 14, 92, fill=col, track=2, align="r")
            pts = spark_points(it["values"], X + Wd - 192 + 4, cy - 22 + 4, 182, 36 * min(1, k + 0.1))
            if len(pts) >= 2:
                c.stroke(pts, col, 2, cap=False)
                c.circle(pts[-1][0], pts[-1][1], 4, fill=col)
        else:
            _one(c, X + 190 + 16 + 150, cy - ps / 2 - 1, "–", "cg300", ps, 150, lh=1.0, align="r")
        y += rh
    c.hline(X, X + Wd, y, K, 1)
    fy = 480 - 36 - c.line_h("zk400", 11)
    right = v.get("place") or ""
    rw = c.tw(right.upper(), "zk400", 11, 4) - 4 if right else 0
    _lab(c, X, fy, v["footer"], Wd - rw - 24, size=11, track=4)
    if right:
        _lab(c, X + Wd, fy, right, 200, size=11, track=4, align="r")
    return c.finish()
