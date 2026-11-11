"""Botanical design – signature layouts of the plugins (ports of Botanisch-*.dc.html).

Herbarium look: warm paper, Libre Caslon (lc400 / lc400i), Caveat notes (cav) in green,
hand-drawn leaves and sprigs, berries (small red/yellow circles) and thin specimen-label boxes.
"""
import math

from ..designs import lower_first
from ..plugins import _calendar as C
from ..studio import B, G, K, R, Y, Canvas, Wh

COL = {"black": K, "white": Wh, "red": R, "yellow": Y, "green": G, "blue": B}
T = "botanical"


# ================================================================== helpers
def _canvas():
    return Canvas(T, Wh)


def tb(c, x, base, text, role, size, fill=K, align="l", track=0.0):
    """Text placed by its baseline (SVG <text y=…>)."""
    top = base - c._baseline(0, role, size, None)
    c.text(x, top, text, role, size, fill, track=track, align=align)


def ell(c, text, role, size, width, track=0.0):
    """Cut text with an ellipsis so it fits width."""
    text = text or ""
    if c.tw(text, role, size, track) - track <= width:
        return text
    while text and c.tw(text + "…", role, size, track) - track > width:
        text = text[:-1]
    return text.rstrip(" ·,–-") + "…"


def shrink(c, text, role, size, width, track=0.0, min_size=9):
    """Largest size ≤ size at which text fits width on one line (then ellipsis)."""
    s = size
    while s > min_size and c.tw(text, role, s, track * s / size) - track > width:
        s -= 1
    tr = track * s / size
    return s, ell(c, text, role, s, width, tr), tr


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def leaf_d(x, y, s, up, length, k=0.36, back=8):
    """The mockups' leaf: two quadratic curves from the stem point."""
    tx, ty = x + s * length, y - up
    mx = x + s * length / 2
    return f"M {x} {y} Q {mx} {y - up - length * k} {tx} {ty} Q {mx + s * 5} {y + back} {x} {y} Z"


def leaf(c, x, y, s, up, length, stroke=G, width=2.5, fill=None, dx=0, dy=0, k=0.36, back=8):
    c.path(leaf_d(x, y, s, up, length, k, back), stroke=stroke, width=width, fill=fill, dx=dx, dy=dy)


def berry(c, cx, cy, r, fill=R, width=1.5):
    c.circle(cx, cy, r, fill=fill, outline=K, width=max(1, round(width)))


def label_box(c, x0, y0, x1, y1):
    c.rect((x0, y0, x1, y1), outline=K, width=2)


def dot_rule(c, x0, x1, y, dot=G, r=3.5, gap=10):
    """—— ● —— divider."""
    cx = (x0 + x1) / 2
    c.hline(x0, cx - r - gap, y, K, 1)
    c.hline(cx + r + gap, x1, y, K, 1)
    c.circle(cx, y + 0.5, r, fill=dot)


def small_caps(c, x, top, text, size=11, track=2, fill=K, width=None, align="l"):
    text = text.upper()
    if width:
        size, text, track = shrink(c, text, "lc400", size, width, track, 8)
    c.text(x, top, text, "lc400", size, fill, track=track, align=align)
    return c.line_h("lc400", size)


def sprig(c, dx, dy, stem, leaves, bud=None, width=3, lw=2.5):
    """Stem path + outline leaves + optional berry (x, y, r, colour)."""
    c.path(stem, stroke=G, width=width, dx=dx, dy=dy)
    for lf in leaves:
        leaf(c, *lf, width=lw, dx=dx, dy=dy)
    if bud:
        berry(c, dx + bud[0], dy + bud[1], bud[2], bud[3])


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = _canvas()
    x0, y0, s = 44, 30, 52
    last = {tuple(rc) for rc in v.get("last_cells") or []}
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            bg = Y if (r, col) in last else G if (r + col) % 2 == 1 else Wh
            c.rect((x0 + col * s, y0 + r * s, x0 + col * s + s, y0 + r * s + s), fill=bg)
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            chess_puzzle.draw_piece(c.d, p, x0 + col * s + s // 2, y0 + r * s + s // 2, s)
    c.rect((x0 - 1, y0 - 1, x0 + 8 * s + 1, y0 + 8 * s + 1), outline=K, width=2)
    if v.get("show_coords", True):
        for i, rk in enumerate(v["ranks"]):
            tb(c, 30, y0 + i * s + 31, rk, "lc400i", 13, align="c")
        for i, f in enumerate(v["files"]):
            tb(c, x0 + i * s + 26, 463, f, "lc400i", 13, align="c")

    X, Wd = 494, 276
    y = 34
    sz, t, _ = shrink(c, v["title"], "cav", 30, Wd, min_size=18)
    c.text(X, y, t, "cav", sz, G)
    y += c.line_h("cav", 30) + 6
    L = 32 * 1.1
    white = v.get("white_to_move")
    c.circle(X + 8, y + L / 2, 8, fill=Wh if white else K, outline=K, width=2)
    sz, t, _ = shrink(c, v["to_move"], "lc400i", 32, Wd - 28, min_size=16)
    c.text(X + 28, y, t, "lc400i", sz, K, lh=L / sz)
    y += L + 6
    if v.get("mate"):
        y += 8
        sz, t, _ = shrink(c, v["mate"], "lc400", 40, Wd, min_size=20)
        c.text(X, y, t, "lc400", sz, R, lh=1)
        y += 40 + 6
    if v.get("themes_text"):
        y += 4
        th = " · ".join(t for t in v["themes"] if t != v.get("mate"))
        size, lines, Lh, _ = c.fit(th, "lc400i", 17, Wd, 2 * c.line_h("lc400i", 17), lh=None, min_size=12)
        c.para(X, y, Wd, lines[:2], "lc400i", size, c.line_h("lc400i", size))
        y += min(2, len(lines)) * c.line_h("lc400i", size) + 6
    # twig
    ty = min(y + 6, 236)
    c.path("M 4 26 C 70 20 150 30 250 22", stroke=G, width=2.5, dx=X, dy=ty)
    for x, yy, sg in ((40, 24, -1), (80, 23, 1), (120, 25, -1), (160, 25, 1), (200, 24, -1), (228, 23, 1)):
        tx, tyy = x + 26, yy + sg * 16
        c.path(f"M {x} {yy} Q {x + 8} {yy + sg * 18} {tx} {tyy} Q {x + 20} {yy + sg * 2} {x} {yy} Z",
               stroke=G, width=2, dx=X, dy=ty)
    berry(c, X + 256, ty + 22, 7)

    # determination label (bottom box)
    inner = Wd - 28 - 3
    rows = []
    stats = [t for t in (v.get("rating_text"), v.get("solution_text")) if t]
    hint = v.get("hint", "")
    foot = " · ".join(p for p in (v.get("source", ""), f"No. {v['today'].timetuple().tm_yday}", v.get("place", "")) if p)
    h = 10 + c.line_h("lc400", 11) + (6 + c.line_h("lc400", 17) if stats else 0) + \
        (6 + c.line_h("cav", 21) if hint else 0) + 2 + c.line_h("lc400", 11) + 10 + 3
    by1 = 480 - 34
    by0 = by1 - h
    label_box(c, X, by0, 800 - 30, by1)
    xx, yy = X + 16, by0 + 11.5
    yy += small_caps(c, xx, yy, ctx.t("Determination", "Bestimmung"), width=inner)
    if stats:
        yy += 6
        if len(stats) == 2:
            a, b = stats
            sa = 17
            while sa > 11 and c.tw(a, "lc400", sa) + c.tw(b, "lc400i", sa) + 10 > inner:
                sa -= 1
            c.text(xx, yy + (17 - sa) / 2, a, "lc400", sa)
            c.text(xx + inner, yy + (17 - sa) / 2, b, "lc400i", sa, align="r")
        else:
            sz, t, _ = shrink(c, stats[0], "lc400", 17, inner, min_size=11)
            c.text(xx, yy, t, "lc400", sz)
        yy += c.line_h("lc400", 17)
    if hint:
        yy += 6
        sz, t, _ = shrink(c, hint, "cav", 21, inner, min_size=14)
        c.text(xx, yy, t, "cav", sz, G)
        yy += c.line_h("cav", 21)
    yy += 2
    small_caps(c, xx, yy, foot, width=inner)
    return c.finish()


# ================================================================== spotify
def spotify(ctx, v):
    c = _canvas()
    c.rect((40, 40, 440, 440), outline=K, width=2)
    if v.get("image") is not None:
        c.img.paste(ctx.punch(ctx.cover_fit(v["image"], 377, 377)), (52, 52))
    else:
        ox, oy = 52, 52
        c.rect((ox, oy, ox + 377, oy + 377), fill=B)
        c.rect((ox, oy + 250, ox + 377, oy + 377), fill=K)
        c.circle(ox + 250, oy + 130, 82, fill=Y)
        c.circle(ox + 250, oy + 130, 34, fill=R)
        c.path("M 110 377 C 104 300 128 220 112 120", stroke=Wh, width=5, dx=ox, dy=oy)
        for lf in ((108, 330, 1, 30, 90), (110, 280, -1, 24, 80), (116, 220, 1, 34, 84), (114, 168, -1, 22, 70)):
            c.path(leaf_d(*lf), fill=G, dx=ox, dy=oy)
            c.path(leaf_d(*lf), stroke=Wh, width=3, dx=ox, dy=oy)
        c.circle(ox + 112, oy + 112, 16, fill=Wh)
        c.rect((ox + 196, oy + 290, ox + 346, oy + 300), fill=Wh)
        c.rect((ox + 196, oy + 314, ox + 292, oy + 324), fill=Y)
    # corner sprig (100 × 110 at the bottom right)
    sprig(c, 700, 370, "M 84 110 C 80 80 86 60 64 24",
          [(82, 92, -1, 14, 40), (82, 70, 1, 18, 14), (74, 46, -1, 16, 30)], (62, 20, 9, Y))

    X, Wd = 474, 296
    y = 48
    lab = v.get("label") or ""
    lab = (lower_first(lab) if ctx.lang in ("de", "en") else lab) + " …"
    sz, t, _ = shrink(c, lab, "cav", 30, Wd, min_size=18)
    c.text(X, y, t, "cav", sz, G)
    y += c.line_h("cav", 30) + 10
    tail = 0
    artist, album = v.get("artist", ""), v.get("album", "")
    if artist:
        tail += 10 + 4 + c.line_h("lc400", 22)
    if album:
        tail += 10 + c.line_h("lc400i", 17)
    room = 318 - y - tail
    size, lines, L, _ = c.fit(v.get("track", ""), "lc400i", 34, Wd, room, lh=1.18, min_size=18)
    maxl = max(1, int((room + 0.5) // L))
    if len(lines) > maxl:
        lines = lines[:maxl]
        lines[-1] = ell(c, lines[-1] + " …", "lc400i", size, Wd)
    c.para(X, y, Wd, lines, "lc400i", size, L)
    y += len(lines) * L
    if artist:
        y += 14
        sz, t, _ = shrink(c, artist, "lc400", 22, Wd, min_size=15)
        c.text(X, y, t, "lc400", sz)
        y += c.line_h("lc400", 22)
    if album:
        y += 10
        sz, t, _ = shrink(c, ctx.t("from “{a}”", "aus „{a}“", a=album), "lc400i", 17, Wd, min_size=12)
        c.text(X, y, t, "lc400i", sz)
    # length – a quiet rule (no playback position on e-ink)
    c.hline(X + 2, X + 294 - 9, 342, K, 1)
    c.stroke([(X + 2, 342), (X + 40, 342)], G, 4)
    berry(c, X + 294 - 7, 342, 7)
    if v.get("duration_text"):
        c.text(X + 294, 360, v["duration_text"], "lc400i", 15, align="r")
        c.text(X, 360, ctx.t("Length", "Länge"), "lc400", 15)
    # source label
    foot = " · ".join(p for p in (v.get("source", "Spotify"), v.get("place", "")) if p).upper()
    s, foot, tr = shrink(c, foot, "lc400", 11, 196, 2, 8)
    w = c.tw(foot, "lc400", s, tr) - tr
    h = 6 + c.line_h("lc400", 11) + 6 + 3
    label_box(c, X, 446 - h, X + w + 31, 446)
    c.text(X + 15.5, 446 - h + 7.5, foot, "lc400", s, track=tr)
    return c.finish()


# ================================================================== grid
def _grid_advice(ctx, col):
    if col == "green":
        return ctx.t("Wash, charge, run the dishwasher now", "Jetzt waschen, laden, spülen")
    if col == "yellow":
        return ctx.t("Better wait a little", "Lieber noch etwas warten")
    if col == "red":
        return ctx.t("Postpone big loads if you can", "Große Verbraucher möglichst verschieben")
    return ""


def grid(ctx, v):
    c = _canvas()
    col = v.get("color")
    head = " · ".join(p for p in (v["title"], v.get("place", "")) if p)
    sz, t, _ = shrink(c, head, "cav", 30, 420, min_size=18)
    c.text(40, 34, t, "cav", sz, G)
    y = 34 + c.line_h("cav", 30) + 4 + 6
    # signal disc with a leaf
    cx, cy = 40 + 48, y + 48
    c.circle(cx, cy, 40, fill=COL.get(col, Wh), outline=K, width=2)
    ink = K if col in ("yellow", None) else Wh
    c.path("M 48 20 Q 66 40 48 76 Q 30 40 48 20 Z", stroke=ink, width=2.5, dx=40, dy=y)
    c.vline(87.5, y + 28, y + 70, ink, 2)
    # name + share
    tx, tw_ = 40 + 96 + 22, 455 - 158
    name = cap(v.get("signal_name") or "–")
    s = 84
    while s > 30 and c.tw(name, "lc400", s) > tw_:
        s -= 2
    sub = ctx.t("{p} renewables", "{p} Erneuerbare", p=v["share_text"]) if v.get("share_text") else ""
    hb = s + (2 + c.line_h("lc400i", 26) if sub else 0)
    top = cy - hb / 2
    c.text(tx, top + (84 - s) * 0 , ell(c, name, "lc400", s, tw_), "lc400", s, lh=1)
    if sub:
        s2, t2, _ = shrink(c, sub, "lc400i", 26, tw_, min_size=14)
        c.text(tx, top + s + 2, t2, "lc400i", s2)

    # advice box (right)
    bx0, bx1 = 800 - 40 - 281, 800 - 40
    inner = 250
    adv = _grid_advice(ctx, col)
    asz, alines, AL, _ = c.fit(adv, "cav", 30, inner, 2 * 33, lh=1.1, min_size=18) if adv else (30, [], 0, 0)
    best = v.get("best_text", "")
    bsz, blines, BL, _ = c.fit(best, "lc400i", 15, inner, 3 * c.line_h("lc400i", 15), lh=None, min_size=11) \
        if best else (15, [], 0, 0)
    blines = blines[:3]
    h = 10 + c.line_h("lc400", 11) + (6 + len(alines) * AL if alines else 0) + \
        (8 + len(blines) * BL if blines else 0) + 10 + 3
    by0 = 52
    label_box(c, bx0, by0, bx1, by0 + h)
    yy = by0 + 11.5
    yy += small_caps(c, bx0 + 16, yy, ctx.t("Advice for now", "Empfehlung für jetzt"), width=inner)
    if alines:
        yy += 6
        c.para(bx0 + 16, yy, inner, alines, "cav", asz, AL, G)
        yy += len(alines) * AL
    if blines:
        yy += 8
        c.para(bx0 + 16, yy, inner, blines, "lc400i", bsz, BL)

    dot_rule(c, 40, 760, 225, G, 3.5, 10)
    small_caps(c, 40, 244, ctx.t("Green power through the day · 00 – 24 h", "Der Tag im Stromnetz · 00 – 24 Uhr"),
               size=13, track=3, width=720)

    # 24 leaves
    ox, oy = 30, 290
    base = oy + 100
    c.stroke([(ox + 20, base), (ox + 700, base)], G, 3)
    for hd in v["hours"]:
        h_ = hd["hour"]
        x = ox + 20 + h_ * 28
        fill = COL.get(hd.get("color"), Wh)
        d = f"M {x + 3} {base} Q {x + 2} {base - 26} {x + 25} {base - 34} Q {x + 28} {base - 8} {x + 3} {base} Z"
        c.path(d, fill=fill)
        c.path(d, stroke=K, width=1.2)
    for h_ in range(0, 25, 3):
        x = ox + 20 + h_ * 28
        c.vline(x - 0.5, base, base + 8, K, 1)
        tb(c, x, oy + 126, f"{h_:02d}", "lc400", 14, align="c")
    nx = ox + 20 + v.get("now_pos", 0) * 672
    c.rect((nx - 1, oy + 54, nx + 1, oy + 112), fill=K)
    berry(c, nx, oy + 50, 7)
    nl = f"{v.get('now_label', '')} {v.get('time', '')}".strip()
    nw = c.tw(nl, "cav", 24)
    ncx = min(max(nx, 40 + nw / 2), 760 - nw / 2)
    tb(c, ncx, oy + 30, nl, "cav", 24, G, align="c")
    # names of the non-green runs above the band
    taken = [(ncx - nw / 2 - 8, ncx + nw / 2 + 8)]
    for sg in v.get("segments", []):
        if sg.get("color") in (None, "green") or sg["end"] - sg["start"] < 1:
            continue
        name = sg.get("name", "")
        w = c.tw(name, "lc400i", 16)
        mx = ox + 20 + (sg["start"] + sg["end"]) / 2 * 28
        a, b = max(40, mx - w / 2), min(760, max(40, mx - w / 2) + w)
        if b - a < w - 0.5 or any(a < q and b > p for p, q in taken):
            continue
        tb(c, a, oy + 46, name, "lc400i", 16, R if sg["color"] == "red" else K)
        taken.append((a - 8, b + 8))
    return c.finish()


# ================================================================== wordclock
def wordclock(ctx, v):
    c = _canvas()
    rows, cols = v["rows"], v["cols"]
    cw, ch = 396 / cols, 380 / rows
    c.rect((36, 36, 36 + 3 + 24 + 396, 36 + 3 + 24 + 380), outline=K, width=2)
    gx, gy = 36 + 13.5, 36 + 13.5
    lit = {tuple(p) for p in v["lit"]}
    big = min(27, round(ch * 0.71))
    small = min(18, round(ch * 0.47))
    for r, line in enumerate(v["grid"]):
        for col, letter in enumerate(line):
            on = (r, col) in lit
            sz = big if on else small
            cx, cy = gx + col * cw + cw / 2, gy + r * ch + ch / 2
            f = c.font("lc400", sz)
            c.d.text((cx, cy), letter, font=f, fill=R if on else G, anchor="mm",
                     **({"stroke_width": 1, "stroke_fill": R} if on else {}))

    X, Wd = 500, 270
    y = 36
    s, t, _ = shrink(c, v["weekday"], "lc400i", 38, Wd, min_size=20)
    c.text(X, y, t, "lc400i", s, lh=41.8 / s)
    y += 41.8 + 2
    s, t, _ = shrink(c, ctx.date(v["today"], weekday=False, year=True), "lc400", 20, Wd, min_size=12)
    c.text(X, y, t, "lc400", s)
    y += c.line_h("lc400", 20) + 2 + 6
    size, lines, L, _ = c.fit(v["phrase_time"], "cav", 26, Wd, 180 - y, lh=None, min_size=16)
    c.para(X, y, Wd, lines[:2], "cav", size, L, G)

    # dial
    ox, oy = 500, 186
    c.circle(ox + 65, oy + 65, 60, fill=Wh, outline=K, width=2)
    for i in range(12):
        a = i * math.pi / 6
        bigt = i % 3 == 0
        r1, r2 = (46 if bigt else 51), 56
        c.stroke([(ox + 65 + r1 * math.sin(a), oy + 65 - r1 * math.cos(a)),
                  (ox + 65 + r2 * math.sin(a), oy + 65 - r2 * math.cos(a))], K, 2.5 if bigt else 1.2, cap=False)
    ha = math.radians((v["hour"] % 12 + v["minute"] / 60) * 30)
    ma = math.radians(v["minute"] * 6)
    c.stroke([(ox + 65, oy + 65), (ox + 65 + 32 * math.sin(ha), oy + 65 - 32 * math.cos(ha))], K, 4)
    c.stroke([(ox + 65, oy + 65), (ox + 65 + 50 * math.sin(ma), oy + 65 - 50 * math.cos(ma))], G, 2.5)
    berry(c, ox + 65, oy + 65, 6)
    # minutes + moon
    mx, mw = ox + 130 + 22, 800 - 30 - (ox + 152)
    extra = max(0, min(4, v["now"].minute - v["minute"])) if v.get("now") else 0
    lh11 = c.line_h("lc400", 11)
    msz, mlines, ML, _ = c.fit(v.get("moon", ""), "lc400i", 17, mw - 30, 2 * c.line_h("lc400i", 17), lh=None,
                               min_size=11)
    mlines = mlines[:2]
    mh = max(22, len(mlines) * ML)
    total = lh11 + 6 + 14 + 14 + lh11 + 6 + mh
    yy = oy + 65 - total / 2
    small_caps(c, mx, yy, ctx.t("Minutes", "Minuten"), width=mw)
    yy += lh11 + 6
    for i in range(4):
        c.circle(mx + 7 + i * 22, yy + 7, 7, fill=R if i < extra else Wh, outline=K, width=2)
    yy += 14 + 14
    small_caps(c, mx, yy, ctx.t("Moon", "Mond"), width=mw)
    yy += lh11 + 6
    C.draw_moon(c.d, mx + 11, yy + mh / 2, 10, v["phase"], Wh, K, K)
    c.para(mx + 30, yy + (mh - len(mlines) * ML) / 2, mw - 30, mlines, "lc400i", msz, ML)

    sprig(c, 650, 340, "M 140 140 C 128 104 120 70 84 40",
          [(130, 110, -1, 20, 50), (124, 88, 1, 16, 22), (108, 64, -1, 18, 44)], (80, 36, 9, Y))
    # label
    l1 = ctx.t("Wk {w} · Day {d}", "KW {w} · Tag {d}", w=v["week"], d=v["day_of_year"]).upper()
    l2 = " · ".join(p for p in (v.get("place", ""), v["time"]) if p)
    s2, l2, _ = shrink(c, l2, "cav", 20, 170, min_size=13)
    h = 8 + lh11 + 4 + c.line_h("cav", 20) + 8 + 3
    label_box(c, 500, 444 - h, 701, 444)
    small_caps(c, 513.5, 444 - h + 9.5, l1, width=170)
    c.text(513.5, 444 - h + 9.5 + lh11 + 4, l2, "cav", s2)
    return c.finish()


# ================================================================== countdown
def _weeks(ctx, n):
    return ctx.t("1 week", "1 Woche") if n == 1 else ctx.t("{n} weeks", "{n} Wochen", n=n)


def _days(ctx, n):
    return ctx.t("1 day", "1 Tag") if n == 1 else ctx.t("{n} days", "{n} Tage", n=n)


def _weekends(ctx, n):
    return ctx.t("1 weekend", "1 Wochenende") if n == 1 else ctx.t("{n} weekends", "{n} Wochenenden", n=n)


def _in_a_row(ctx, n):
    return ctx.t("day in a row", "Tag in Folge") if n == 1 else ctx.t("days in a row", "Tage in Folge")


def countdown(ctx, v):
    c = _canvas()
    state = v["state"]
    pre = {"future": ctx.t("only", "nur noch"), "past": ctx.t("already", "schon")}.get(state, "")
    if pre:
        c.text(48, 30, pre, "cav", 30, G)
    big = v["big"]
    s, tr = 210, -4
    while s > 60 and c.tw(big, "lc400", s, tr * s / 210) > 290:
        s -= 4
    btop = 58 + (210 - s) * 0.45
    c.text(40, btop, big, "lc400", s, track=tr * s / 210, lh=1)

    X, Wd = 340, 420
    head = " ".join(p for p in (v.get("small", ""), v.get("event", "")) if p)
    y = 86
    size, lines, L, _ = c.fit(head, "lc400i", 38, Wd, 3 * 38 * 1.2, lh=1.2, min_size=18)
    if len(lines) * L > 3 * 38 * 1.2 + 1:
        lines = lines[:max(1, int(3 * 38 * 1.2 // L))]
        lines[-1] = ell(c, lines[-1] + " …", "lc400i", size, Wd)
    c.para(X, y, Wd, lines, "lc400i", size, L)
    y += len(lines) * L + 10
    c.hline(X, X + 60, y + 3, K, 1)
    c.circle(X + 73.5, y + 3.5, 3.5, fill=G)
    c.hline(X + 87, X + 147, y + 3, K, 1)
    y += 7 + 10
    s2, t2, _ = shrink(c, f"{v['target_weekday']}, {v['date']}", "cav", 28, Wd, min_size=16)
    c.text(X, y, t2, "cav", s2, G)
    y += c.line_h("cav", 28) + 10
    if state != "today":
        wk = _weeks(ctx, v["weeks"])
        if v["rest_days"]:
            wk += ", " + _days(ctx, v["rest_days"])
        parts = [wk] if v["weeks"] else []
        if v["weekends"]:
            parts.append(_weekends(ctx, v["weekends"]))
        if parts:
            small_caps(c, X, min(y, 290), " · ".join(parts), size=13, track=3, width=Wd)

    # strip of days
    oy = 316
    by = oy + 70
    strip = v.get("strip") or []
    n = len(strip)
    x0, x1 = 60, 716
    c.stroke([(x0, by), (x1, by)], G, 3)
    xs = (lambda i: x0 + i * (x1 - x0) / (n - 1)) if n > 1 else (lambda i: x0)
    dense = n > 64
    if n > 1:
        for i, e in enumerate(strip):
            if (e["weekday"] == 0 and not dense) or (dense and e["first_of_month"]):
                x = xs(i)
                for sg in (-1, 1):
                    c.path(f"M {x} {by} Q {x + 4} {by + sg * 26} {x + 20} {by + sg * 30} Q {x + 18} {by + sg * 8} {x} {by} Z",
                           stroke=G, width=2)
            if not dense and 0 < i < n - 1:
                c.circle(xs(i), by, 2.5, fill=K)
        step = (x1 - x0) / (n - 1)
        used = []
        for i, e in enumerate(strip):
            if e["first_of_month"] and 0 < i < n - 1:
                x = xs(i)
                c.vline(x - 0.5, by - 12, by + 28, K, 1)
                m = C.month(e["date"], ctx.lang)
                w = c.tw(m, "lc400i", 14)
                if x + 6 + w < 790:
                    tb(c, x + 6, oy + 96, m, "lc400i", 14)
                    used.append((x - 2, x + 8 + w))
        if not dense and step * 7 >= 46:
            for i, e in enumerate(strip):
                if e["weekday"] == 0 and i + 3.5 <= n - 1:
                    x = xs(i + 3.5)
                    lab = ctx.t("Wk {n}", "KW {n}", n=e["date"].isocalendar()[1])
                    tb(c, x, oy + 114, lab, "lc400", 13, align="c")
    # ends: today = berry, event = flower
    ti = next((i for i, e in enumerate(strip) if e["today"]), 0 if state != "past" else n - 1)
    ei = next((i for i, e in enumerate(strip) if e["target"]), n - 1 if state != "past" else 0)
    tx, ex = (xs(ti), xs(ei)) if n > 1 else ((x0, x1) if state != "past" else (x1, x0))
    if state == "today":
        tx, ex = x0, x1
    for k in range(6):
        a = k * math.pi / 3
        berry(c, ex + 13 * math.cos(a), by + 13 * math.sin(a), 8, Y)
    berry(c, ex, by, 7, R)
    berry(c, tx, by, 9, R)
    tlab = ctx.t("today, {d}", "heute, {d}", d=v["today_short"])
    elab = v["date_short"]
    for x, lab in ((tx, tlab), (ex, elab)):
        if x < 400:
            tb(c, x - 8, oy + 28, lab, "cav", 22, G)
        else:
            tb(c, 760, oy + 28, lab, "cav", 22, G, align="r")
    return c.finish()


# ================================================================== art
def art(ctx, v):
    c = _canvas()
    img = v["image"]
    sc = min(453 / img.width, 373 / img.height)
    iw, ih = max(1, round(img.width * sc)), max(1, round(img.height * sc))
    fx0 = 36 + (488 - (iw + 35)) / 2
    fy0 = 36 + (408 - (ih + 35)) / 2
    c.rect((fx0, fy0, fx0 + iw + 35, fy0 + ih + 35), outline=K, width=2)
    ix, iy = round(fx0 + 17.5), round(fy0 + 17.5)
    c.img.paste(img.convert("RGB").resize((iw, ih)), (ix, iy))
    k = max(18, min(52, round(min(iw, ih) * 0.13)))
    for px, py, sx, sy in ((ix, iy, 1, 1), (ix + iw - 1, iy, -1, 1), (ix, iy + ih - 1, 1, -1), (ix + iw - 1, iy + ih - 1, -1, -1)):
        c.poly([(px, py), (px + sx * k, py), (px, py + sy * k)], fill=Wh, outline=K, width=2)
    sprig(c, 580, 0, "M 220 26 C 170 30 120 20 70 56",
          [(180, 26, -1, 26, 40), (150, 26, 1, -30, 34), (118, 30, -1, 22, 42), (96, 42, 1, -34, 24)], (66, 60, 9, R))

    X, Wd = 556, 210
    # bottom label first (its height limits the column)
    inner = Wd - 31
    msz, mlines, ML, _ = c.fit(v["museum"], "lc400i", 17, inner, 2 * c.line_h("lc400i", 17), lh=None, min_size=12)
    mlines = mlines[:2]
    foot = " · ".join(p for p in (f"No. {v['doy']}", v.get("museum_city", ""), v.get("date_short", "")) if p)
    fs, foot, _ = shrink(c, foot, "cav", 20, inner, min_size=13)
    lh11 = c.line_h("lc400", 11)
    h = 10 + lh11 + 4 + len(mlines) * ML + 6 + c.line_h("cav", 20) + 10 + 3
    by1 = 444
    by0 = by1 - h
    label_box(c, X, by0, 800 - 34, by1)
    yy = by0 + 11.5
    yy += small_caps(c, X + 15.5, yy, ctx.t("Collection", "Sammlung"), width=inner) + 4
    c.para(X + 15.5, yy, inner, mlines, "lc400i", msz, ML)
    yy += len(mlines) * ML + 6
    c.text(X + 15.5, yy, foot, "cav", fs)

    y = 120
    bottom = by0 - 14
    s, t, _ = shrink(c, v["title"], "cav", 30, Wd, min_size=18)
    c.text(X, y, t, "cav", s, G)
    y += c.line_h("cav", 30) + 8
    rest = [(x, "lc400", 18) for x in (v.get("artist"), v.get("date")) if x]
    if v.get("medium"):
        rest.append((v["medium"], "lc400i", 15))
    rh = sum(c.line_h(r, z) + 8 for _, r, z in rest)
    room = max(40, bottom - y - rh)
    size, lines, L, _ = c.fit(v["work"], "lc400i", 30, Wd, room, lh=1.15, min_size=15)
    maxl = max(1, int((room + 0.5) // L))
    if len(lines) > maxl:
        lines = lines[:maxl]
        lines[-1] = ell(c, lines[-1] + " …", "lc400i", size, Wd)
    c.para(X, y, Wd, lines, "lc400i", size, L)
    y += len(lines) * L + 8
    for txt, r, z in rest:
        if y + c.line_h(r, z) > bottom:
            break
        sz, t, _ = shrink(c, txt, r, z, Wd, min_size=11)
        c.text(X, y, t, r, sz)
        y += c.line_h(r, z) + 8
    return c.finish()


# ================================================================== waste
def _bin(c, x, y, w, fill, stripes=False, lw=1.2):
    """The mockup's bin icon (viewBox 44 × 52) scaled to width w at (x, y)."""
    s = w / 44
    sw = max(1, round(lw * s))
    c.rect((x + 2 * s, y + 4 * s, x + 42 * s, y + 11 * s), fill=fill, outline=K, width=sw)
    c.poly([(x + 6 * s, y + 12 * s), (x + 38 * s, y + 12 * s), (x + 35 * s, y + 45 * s), (x + 9 * s, y + 45 * s)],
           fill=fill, outline=K, width=sw)
    if stripes:
        ink = Wh if fill == K else K
        c.stroke([(x + 16 * s, y + 18 * s), (x + 17 * s, y + 40 * s)], ink, max(1, round(s)), cap=False)
        c.stroke([(x + 28 * s, y + 18 * s), (x + 27 * s, y + 40 * s)], ink, max(1, round(s)), cap=False)
    for wx in (12, 32):
        c.circle(x + wx * s, y + 48 * s, 3 * s, fill=Wh, outline=K, width=sw)


def waste(ctx, v):
    c = _canvas()
    sprig(c, 670, 0, "M 118 0 C 104 50 112 100 76 150",
          [(112, 40, -1, -16, 44), (110, 80, 1, -4, 16), (100, 108, -1, -16, 46)], (73, 155, 9, Y))
    soon, rows = v.get("soon"), list(v.get("rows") or [])
    if soon:
        head = f"{soon['label']}, {soon['weekday']} {soon['date_short']}"
        items = soon["items"]
        tonight = not soon["is_today"]
    else:
        d0 = rows[0]["date"]
        items = [{"name": r["name"], "color": r["color"]} for r in rows if r["date"] == d0]
        head = f"{rows[0]['in_text']}, {rows[0]['weekday']} {rows[0]['date_short']}"
        rows = [r for r in rows if r["date"] != d0]
        tonight = False
    s, t, _ = shrink(c, cap(head), "cav", 30, 390, min_size=18)
    c.text(40, 32, t, "cav", s, G)
    y = 32 + c.line_h("cav", 30) + 2
    names = [it["name"] for it in items]
    lines = [names[0]] + ["+ " + n for n in names[1:]]
    if len(lines) > 3:
        lines = lines[:2] + [ell(c, "+ " + ", ".join(names[2:]), "lc400i", 30, 390)]
    sz = 44
    while sz > 24 and (max(c.tw(l, "lc400i", sz) for l in lines) > 390 or len(lines) * sz * 1.1 > 3 * 44 * 1.1 - 10):
        sz -= 2
    for l in lines:
        c.text(40, y, ell(c, l, "lc400i", sz, 390), "lc400i", sz, lh=1.1)
        y += sz * 1.1
    if tonight:
        small_caps(c, 40, y + 6, ctx.t("Put out tonight", "Heute Abend rausstellen"), size=13, track=3, width=390)
    # big bins
    n = min(3, len(items))
    bw = min(84, (220 - 26 * (n - 1)) / n)
    for i, it in enumerate(items[:n]):
        bh = bw * 52 / 44
        _bin(c, 440 + i * (bw + 26), 150 - bh, bw, COL.get(it["color"], K), stripes=True)

    # list
    y = 214
    c.hline(40, 100, y + 3, K, 1)
    c.circle(113.5, y + 3.5, 3.5, fill=G)
    c.hline(127, 187, y + 3, K, 1)
    y += 7 + 6
    if not rows:
        size, ls, L, _ = c.fit(v.get("empty_text", ""), "lc400i", 22, 640, 80, lh=None, min_size=14)
        c.para(40, y + 14, 640, ls, "lc400i", size, L)
    for r in rows[:4]:
        cy = y + 25
        _bin(c, 40, cy - 18, 30, COL.get(r["color"], K), lw=1.5)
        ds, dt_, _ = shrink(c, r["date_text"], "lc400", 20, 110, min_size=12)
        c.text(88, cy - c.line_h("lc400", ds) / 2, dt_, "lc400", ds)
        iw = c.tw(r["in_text"], "cav", 26)
        c.text(760, cy - c.line_h("cav", 26) / 2, r["in_text"], "cav", 26, G, align="r")
        ns, nt, _ = shrink(c, r["name"], "lc400i", 24, 760 - iw - 18 - 216, min_size=14)
        c.text(216, cy - c.line_h("lc400i", ns) / 2, nt, "lc400i", ns)
        c.hline(40, 760, y + 50, K, 1)
        y += 51
    foot = " · ".join(p for p in (v["title"], v.get("place", ""), ctx.t("Wk {n}", "KW {n}", n=v["week"])) if p)
    small_caps(c, 40, 480 - 22 - c.line_h("lc400", 11), foot, width=620)
    return c.finish()


# ================================================================== warnings
def warnings(ctx, v):
    c = _canvas()
    for d, w in (("M 60 480 C 62 380 80 300 200 230", 3), ("M 110 480 C 110 410 130 360 226 318", 2.5),
                 ("M 26 480 C 26 400 40 330 130 260", 2.5)):
        c.path(d, stroke=G, width=w)
    for x, y, ln, up in ((64, 400, 60, 14), (70, 340, 64, 20), (96, 290, 62, 22), (140, 256, 50, 16),
                         (112, 440, 56, 10), (124, 390, 60, 14), (160, 350, 48, 12), (30, 420, 50, 12), (44, 350, 52, 16)):
        c.path(f"M {x} {y} Q {x + ln * 0.5} {y - up - 14} {x + ln} {y - up} Q {x + ln * 0.5} {y - up + 10} {x} {y} Z",
               stroke=G, width=2.2)
    for d in ("M 150 120 C 190 110 220 120 240 112", "M 120 150 C 170 140 200 154 236 144",
              "M 170 180 C 196 174 216 180 238 176", "M 70 96 C 110 88 150 98 180 90"):
        c.path(d, stroke=K, width=1.5)
    berry(c, 204, 228, 9, R)
    berry(c, 230, 316, 7, Y)

    X, Wd = 270, 490
    y = 34
    head = ctx.t("Warning for {p}", "Warnung für {p}", p=v["place"]) if v.get("place") else v["title"]
    s, t, _ = shrink(c, head, "cav", 30, Wd, min_size=18)
    c.text(X, y, t, "cav", s, G)
    y += c.line_h("cav", 30) + 6
    acc = Y if v.get("color") == "yellow" else R
    for i in range(v.get("levels", 4)):
        c.circle(X + 8 + i * 24, y + 8, 8, fill=acc if i < v["level"] else Wh, outline=K, width=2)
    lx = X + v.get("levels", 4) * 24 + 8
    lab = ctx.t("Level {n} of {m}", "Stufe {n} von {m}", n=v["level"], m=v.get("levels", 4)) + " · " + v["level_text"]
    lh13 = c.line_h("lc400", 13)
    small_caps(c, lx, y + 8 - lh13 / 2, lab, size=13, track=3, width=X + Wd - lx)
    y += 16 + 6 + 6
    s = 70
    while s > 30 and c.tw(v["event"], "lc400i", s) > Wd:
        s -= 2
    c.text(X, y, ell(c, v["event"], "lc400i", s, Wd), "lc400i", s, lh=1)
    y += s + 4
    if v.get("place_span"):
        s2, t2, _ = shrink(c, v["place_span"], "lc400", 20, Wd, min_size=13)
        c.text(X, y, t2, "lc400", s2)
        y += c.line_h("lc400", 20)
    y += 10
    c.hline(X, X + Wd, y, K, 1)
    y += 13

    # source box
    inner = 250
    flav = ctx.t("Close the windows, bring the plants in", "Fenster zu, Topfpflanzen rein")
    fs, flav, _ = shrink(c, flav, "cav", 20, inner, min_size=13)
    h = 8 + c.line_h("lc400", 11) + 3 + c.line_h("lc400i", 17) + 3 + c.line_h("cav", 20) + 8 + 3
    bx0, by1 = 760 - 281, 450
    by0 = by1 - h
    label_box(c, bx0, by0, 760, by1)
    yy = by0 + 9.5
    yy += small_caps(c, bx0 + 15.5, yy, ctx.t("Source", "Quelle"), width=inner) + 3
    s3, t3, _ = shrink(c, v.get("source", ""), "lc400i", 17, inner, min_size=11)
    c.text(bx0 + 15.5, yy, t3, "lc400i", s3)
    yy += c.line_h("lc400i", 17) + 3
    c.text(bx0 + 15.5, yy, flav, "cav", fs, G)

    # description (+ instruction, more alerts)
    more = v.get("more_text", "")
    room = by0 - 12 - y - (c.line_h("lc400i", 17) + 4 if more else 0)
    text = v.get("description", "")
    if v.get("instruction"):
        text = (text + "\n" + v["instruction"]).strip()
    size, lines, L, _ = c.fit(text, "lc400i", 20, Wd, room, lh=1.35, min_size=12)
    maxl = max(0, int((room + 0.5) // L))
    if len(lines) > maxl:
        lines = lines[:maxl]
        if lines:
            lines[-1] = ell(c, lines[-1] + " …", "lc400i", size, Wd)
    c.para(X, y, Wd, lines, "lc400i", size, L)
    y += len(lines) * L + 4
    if more:
        s4, t4, _ = shrink(c, more, "lc400i", 17, Wd, min_size=11)
        c.text(X, y, t4, "lc400i", s4, R)
    return c.finish()


# ================================================================== wifi
def wifi(ctx, v):
    from ..plugins import wifi as wifi_plugin
    c = _canvas()
    cap_t = " · ".join(p for p in (v.get("security") or ctx.t("open network", "offenes Netz"), v["ssid"]) if p).upper()
    lh11 = c.line_h("lc400", 11)
    bx0, by0 = 40, 44
    bx1 = bx0 + 3 + 36 + 325
    by1 = by0 + 3 + 36 + 325 + 10 + lh11
    c.rect((bx0, by0, bx1, by1), outline=K, width=2)
    qx, qy = bx0 + 19.5, by0 + 19.5
    wifi_plugin.draw_modules(c.d, v["modules"], round(qx), round(qy), 325, dark=K, light=Wh, quiet=2)
    small_caps(c, (bx0 + bx1) / 2, qy + 325 + 10, cap_t, width=325, align="c")

    # sunflower
    ox = 660
    c.path("M 84 390 C 80 300 92 200 78 96", stroke=G, width=3, dx=ox)
    for lf in ((84, 300, -1, 30, 60), (86, 230, 1, 26, 40), (82, 170, -1, 24, 52)):
        leaf(c, *lf, dx=ox)
    for k in range(12):
        a = k * math.pi / 6
        co, si = math.cos(a), math.sin(a)
        bx, by_, tx, ty = 78 + 18 * co, 80 + 18 * si, 78 + 44 * co, 80 + 44 * si
        px, py = -si * 8, co * 8
        mx, my = 78 + 31 * co, 80 + 31 * si
        d = f"M {bx} {by_} Q {mx + px} {my + py} {tx} {ty} Q {mx - px} {my - py} {bx} {by_} Z"
        c.path(d, fill=Y, dx=ox)
        c.path(d, stroke=K, width=1.2, dx=ox)
    c.circle(ox + 78, 80, 18, fill=K)
    for x, y in ((72, 75), (84, 78), (76, 87)):
        c.circle(ox + x, y, 2, fill=R)

    X, Wd = 440, 230
    y = 44
    s, t, _ = shrink(c, v["title"], "cav", 32, Wd, min_size=18)
    c.text(X, y, t, "cav", s, G)
    y += c.line_h("cav", 32) + 4 + 14
    y += small_caps(c, X, y, v["network_label"], width=Wd) + 4
    s, t, _ = shrink(c, v["ssid"], "lc400i", 46, Wd, min_size=16)
    c.text(X, y, t, "lc400i", s, lh=46 * 1.1 / s)
    y += 46 * 1.1 + 4
    if v.get("password"):
        y += 16
        y += small_caps(c, X, y, v["password_label"], width=Wd) + 4
        s, t, _ = shrink(c, v["password"], "lc400", 30, Wd, min_size=12)
        c.text(X, y, t, "lc400", s, lh=36 / s)
        y += 36 + 4
    y += 16
    y += small_caps(c, X, y, ctx.t("Encryption", "Verschlüsselung"), width=Wd) + 4
    sec = {"WPA": "WPA/WPA2", "WEP": "WEP"}.get(v.get("security", ""), ctx.t("open network", "offenes Netz"))
    c.text(X, y, sec, "lc400i", 22)
    y += c.line_h("lc400i", 22) + 10
    if v.get("note"):
        size, lines, L, _ = c.fit(v["note"], "cav", 24, Wd, 380 - y, lh=None, min_size=15)
        lines = lines[:max(0, int((380 - y) // L))]
        c.para(X, y, Wd, lines, "cav", size, L)
    # hint with arrow
    c.path("M 74 10 C 50 4 24 10 8 24", stroke=K, width=1.5, dx=400, dy=400)
    c.path("M 8 24 L 18 22 M 8 24 L 12 14", stroke=K, width=1.5, dx=400, dy=400)
    s, t, _ = shrink(c, v.get("hint", ""), "cav", 26, 290, min_size=15)
    c.text(480, 396, t, "cav", s, G)
    return c.finish()


# ================================================================== habits
def habits(ctx, v):
    c = _canvas()
    sprig(c, 560, 0, "M 240 30 C 190 34 140 24 80 52",
          [(190, 30, -1, 24, 38), (160, 30, 1, -30, 30), (126, 36, -1, 22, 40), (104, 44, 1, -32, 22)], (76, 55, 9, Y))
    ts = 40
    while ts > 24 and c.tw(v["title"], "lc400i", ts) > 330:
        ts -= 2
    base = 26 + c._baseline(0, "lc400i", 40, None)
    tb(c, 40, base, ell(c, v["title"], "lc400i", ts, 330), "lc400i", ts)
    sub = f"{ctx.date(v['today'], weekday=False)} · {ctx.t('six weeks', 'sechs Wochen')}"
    x2 = 40 + min(330, c.tw(v["title"], "lc400i", ts)) + 18
    s2, t2, _ = shrink(c, sub, "cav", 24, 600 - x2, min_size=14)
    tb(c, x2, base, t2, "cav", s2, G)

    hs = v["habits"][:6]
    nrows = (len(hs) + 1) // 2
    cellh = 166 if nrows <= 2 else 112
    gap = 14 if nrows <= 2 else 4
    step = 20 if nrows <= 2 else 14.5
    rr = 6.5 * step / 20
    wd_ = v["now"][1] if v.get("now") else None
    for k, h in enumerate(hs):
        x0 = 40 + (k % 2) * 370
        y0 = 96 + (k // 2) * (cellh + gap)
        c.hline(x0, x0 + 350, y0, K, 1)
        gy = y0 + 15
        for wk, col in enumerate(h["grid"]):
            for wd, done in enumerate(col):
                if done is None:
                    continue
                cx, cy = x0 + step / 2 + wd * step, gy + step / 2 + wk * step
                today = (wk == len(h["grid"]) - 1 and wd == wd_)
                if today:
                    c.circle(cx, cy, rr + 0.5, fill=G if done else Wh, outline=R, width=3 if step == 20 else 2)
                else:
                    c.circle(cx, cy, rr, fill=G if done else Wh, outline=G if done else K, width=1)
        tx = x0 + 7 * step + 18
        tw_ = x0 + 350 - tx
        size, lines, L, _ = c.fit(h["name"], "lc400i", 22, tw_, 2 * 22 * 1.15 if nrows <= 2 else 22 * 1.15, lh=1.15,
                                  min_size=14)
        lines = lines[:2 if nrows <= 2 else 1]
        if lines:
            lines[-1] = ell(c, lines[-1], "lc400i", size, tw_)
        c.para(tx, gy, tw_, lines, "lc400i", size, L)
        yy = gy + len(lines) * L + 2 + 4
        big = 48 if nrows <= 2 else 38
        num = str(h["streak"])
        nb = yy + c._baseline(0, "lc400", big, 1)
        tb(c, tx, nb, num, "lc400", big, R if h.get("hot") else K)
        nx = tx + c.tw(num, "lc400", big) + 8
        unit = _in_a_row(ctx, h["streak"])
        s3, t3, _ = shrink(c, unit, "cav", 22, x0 + 350 - nx, min_size=13)
        tb(c, nx, nb, t3, "cav", s3, G)
    # legend
    y = 480 - 16 - 16
    x = 40
    for kind, txt in (("done", ctx.t("done", "erledigt")), ("missed", ctx.t("missed", "ausgelassen")),
                      ("today", ctx.t("today", "heute"))):
        cy = y + 8
        if kind == "done":
            c.circle(x + 6, cy, 6, fill=G)
            x += 12
        elif kind == "missed":
            c.circle(x + 5.5, cy, 5.5, fill=Wh, outline=K, width=1)
            x += 11
        else:
            c.circle(x + 7, cy, 7, fill=Wh, outline=R, width=2)
            x += 14
        x += 6
        c.text(x, cy - c.line_h("lc400", 13) / 2, txt, "lc400", 13)
        x += c.tw(txt, "lc400", 13) + 16
    return c.finish()


# ================================================================== sudoku
def sudoku(ctx, v):
    c = _canvas()
    x0, y0, s = 40, 33, 46
    for r, row in enumerate(v["grid"]):
        for col, n in enumerate(row):
            if n:
                f = c.font("lc400", 27)
                c.d.text((x0 + col * s + s / 2, y0 + r * s + s / 2), str(n), font=f, fill=K, anchor="mm")
    for i in range(10):
        p = x0 + i * s
        if i % 3 == 0:
            q = min(max(p, x0 + 1), x0 + 414 - 2)
            c.rect((q - 1, y0, q + 2, y0 + 414), fill=K)
            c.rect((x0, y0 + (q - x0) - 1, x0 + 414, y0 + (q - x0) + 2), fill=K)
        else:
            c.vline(p, y0, y0 + 414, K, 1)
            c.hline(x0, x0 + 414, y0 + i * s, K, 1)

    X, Wd = 494, 276
    y = 36
    sz, t, _ = shrink(c, v.get("name") or v["title"], "cav", 32, Wd, min_size=18)
    c.text(X, y, t, "cav", sz, G)
    y += c.line_h("cav", 32) + 8
    dots_w = v["level_max"] * 20 - 6
    sz, t, _ = shrink(c, v["level_name"], "lc400i", 40, Wd - dots_w - 14, min_size=18)
    c.text(X, y, t, "lc400i", sz, lh=44 / sz)
    dx = X + c.tw(t, "lc400i", sz) + 14
    for i in range(v["level_max"]):
        c.circle(dx + 7 + i * 20, y + 22, 7, fill=R if i < v["level_no"] else Wh, outline=K, width=2)
    y += 44 + 8
    sz, t, _ = shrink(c, v["givens_text"], "lc400", 19, Wd, min_size=12)
    c.text(X, y, t, "lc400", sz)
    y += c.line_h("lc400", 19) + 8
    size, lines, L, _ = c.fit(ctx.t("{n} squares are waiting for you", "{n} Felder warten auf dich", n=v["empty"]),
                              "lc400i", 17, Wd, 2 * c.line_h("lc400i", 17), lh=None, min_size=12)
    c.para(X, y, Wd, lines[:2], "lc400i", size, L)

    sprig(c, 660, 214, "M 140 150 C 110 130 70 110 40 60",
          [(112, 134, 1, 40, 22), (96, 124, -1, -18, 40), (70, 100, 1, 34, 34), (54, 84, -1, -10, 30)], (37, 55, 9, R))
    inner = 220
    lh11 = c.line_h("lc400", 11)
    h = 10 + lh11 + 4 + c.line_h("cav", 22) + 2 + lh11 + 10 + 3
    by1 = 480 - 33
    by0 = by1 - h
    label_box(c, X, by0, X + 251, by1)
    yy = by0 + 11.5
    yy += small_caps(c, X + 15.5, yy, ctx.t("Solution", "Auflösung"), width=inner) + 4
    sz, t, _ = shrink(c, v.get("hint", ""), "cav", 22, inner, min_size=13)
    c.text(X + 15.5, yy, t, "cav", sz, G)
    yy += c.line_h("cav", 22) + 2
    foot = " · ".join(p for p in (f"No. {v['today'].timetuple().tm_yday}", v.get("place", "")) if p)
    small_caps(c, X + 15.5, yy, foot, width=inner)
    return c.finish()


# ================================================================== solar
def solar(ctx, v):
    c = _canvas()
    for k in range(12):
        a = k * math.pi / 6
        c.stroke([(90 + 40 * math.cos(a), 90 + 40 * math.sin(a)), (90 + 54 * math.cos(a), 90 + 54 * math.sin(a))], K, 2)
    c.circle(90, 90, 32, fill=Y, outline=K, width=2)

    head = " · ".join(p for p in (v["title"], v.get("power_label", "")) if p)
    s, t, _ = shrink(c, head, "cav", 28, 325, min_size=16)
    c.text(170, 26, t, "cav", s, G)
    num, _, unit = v["power_text"].rpartition(" ")
    if not num:
        num, unit = unit, ""
    ns = 92
    while ns > 40 and c.tw(num, "lc400", ns) + 12 + c.tw(unit, "lc400i", ns * 48 / 92) > 325:
        ns -= 4
    top = 26 + c.line_h("cav", 28)
    base = top + c._baseline(0, "lc400", 92, 1)
    tb(c, 170, base, num, "lc400", ns)
    if unit:
        tb(c, 170 + c.tw(num, "lc400", ns) + 12, base, unit, "lc400i", round(ns * 48 / 92))

    # harvest label
    inner = 220
    rows = [(ctx.t("Today's harvest", "Ernte heute").upper(), "lc400", 11, 2, 0, K),
            (v["today_text"], "lc400", 30, 0, 4, K),
            (ctx.t("≈ {e} saved", "≈ {e} gespart", e=v["saved_text"]), "cav", 24, 0, 4, G)]
    if v.get("total_line"):
        rows.append((v["total_line"], "lc400i", 15, 0, 6, K))
    h = 10 + sum(m + (33 if sz == 30 else c.line_h(r, sz)) for _, r, sz, _, m, _ in rows) + 10 + 3
    bx0 = 760 - 251
    label_box(c, bx0, 36, 760, 36 + h)
    yy = 36 + 11.5
    for txt, r, sz, tr, m, col in rows:
        yy += m
        s2, t2, tr2 = shrink(c, txt, r, sz, inner, tr, min_size=9)
        c.text(bx0 + 15.5, yy + ((33 - c.line_h(r, s2)) / 2 if sz == 30 else 0), t2, r, s2, col, track=tr2)
        yy += 33 if sz == 30 else c.line_h(r, sz)

    # chart
    ox, oy = 30, 210
    t0, t1 = v["t0"], v["t1"]
    peak = v["peak"] or 1
    X = lambda hh: ox + 40 + (hh - t0) / (t1 - t0) * 660
    Yf = lambda w: oy + 200 - min(max(w, 0), peak) / peak * 140
    for frac in (1, 0.5):
        y = Yf(peak * frac)
        c.hline(ox + 40, ox + 700, y, K, 1)
        tb(c, ox + 34, y + 4, ctx.num(peak * frac, 0), "lc400", 12, align="r")
    pts = [(X(hh), Yf(w)) for hh, w in zip(v["hours"], v["watts"]) if t0 <= hh <= t1]
    if len(pts) >= 2:
        c.poly(pts + [(pts[-1][0], oy + 200), (pts[0][0], oy + 200)], fill=Y)
        c.stroke(pts, G, 3)
        n = len(pts)
        for j, (fr, sg) in enumerate(((0.3, 1), (0.5, -1), (0.7, 1))):
            x, y = pts[int(fr * (n - 1))]
            c.path(f"M {x} {y} Q {x - 4} {y - sg * 26} {x - 22} {y - sg * 30} Q {x - 16} {y - sg * 8} {x} {y} Z",
                   stroke=G, width=2)
    c.hline(ox + 40, ox + 700, oy + 199.5, K, 2)
    for hh, lab in zip(v["ticks"], v["tick_labels"]):
        x = X(hh)
        c.vline(x - 0.5, oy + 200, oy + 207, K, 1)
        tb(c, x, oy + 224, lab, "lc400", 14, align="c")
    if v.get("now_visible"):
        nx = X(v["now"])
        ny = pts[-1][1] if len(pts) >= 2 else Yf(v.get("power", 0))
        c.rect((nx - 1, ny, nx + 1, oy + 200), fill=K)
        berry(c, nx, ny, 8)
        lw = c.tw(v["now_text"], "cav", 22)
        lx = nx + 14 if nx + 14 + lw < 770 else nx - 14 - lw
        tb(c, lx, ny - 10, v["now_text"], "cav", 22, G)
    if v.get("max_text"):
        foot = ctx.t("peak today {w} at {t}", "Spitze heute {w} um {t}", w=v["max_text"], t=v["max_time"])
        s, t, _ = shrink(c, foot, "lc400i", 13, 500, min_size=10)
        tb(c, ox + 700, oy + 244, t, "lc400i", s, align="r")
    return c.finish()


# ================================================================== waterlevel
def _arrow(c, x, y, trend, col=K):
    """18 × 18 arrow: rising ↑, falling ↓, steady →."""
    if trend == "rising":
        c.path("M 9 16 L 9 3 M 3 9 L 9 2 L 15 9", stroke=col, width=2, dx=x, dy=y, closed_fill=False)
    elif trend == "falling":
        c.path("M 9 2 L 9 15 M 3 9 L 9 16 L 15 9", stroke=col, width=2, dx=x, dy=y, closed_fill=False)
    elif trend == "steady":
        c.path("M 2 9 L 15 9 M 9 3 L 16 9 L 9 15", stroke=col, width=2, dx=x, dy=y, closed_fill=False)


def waterlevel(ctx, v):
    c = _canvas()
    # reeds (right)
    ox = 680
    for d, w in (("M 40 220 C 40 160 36 110 44 50", 2.5), ("M 76 220 C 76 170 82 120 78 80", 2.5),
                 ("M 58 220 C 54 170 30 130 6 110", 2), ("M 66 220 C 70 170 96 140 116 120", 2)):
        c.path(d, stroke=G, width=w, dx=ox)
    c.rrect((ox + 37, 56, ox + 51, 100), 7, fill=K)
    c.rrect((ox + 71, 86, ox + 84, 124), 6.5, fill=K)
    c.stroke([(ox + 44, 56), (ox + 44, 34)], G, 2)
    c.stroke([(ox + 78, 86), (ox + 78, 68)], G, 2)

    head = ctx.t("Gauge {s}", "Pegel {s}", s=v["station"]) + (f" · {v['water']}" if v.get("water") else "")
    s, t, _ = shrink(c, head, "cav", 30, 620, min_size=18)
    c.text(40, 26, t, "cav", s, G)
    top = 26 + c.line_h("cav", 30) + 2
    base = top + c._baseline(0, "lc400", 92, 1)
    num, unit = v["value_num"], v.get("unit", "")
    ns = 92
    while ns > 40 and c.tw(num, "lc400", ns) + 10 + c.tw(unit, "lc400i", 40) > 300:
        ns -= 4
    vc = R if v.get("high") else K
    tb(c, 40, base, num, "lc400", ns, vc)
    x = 40 + c.tw(num, "lc400", ns) + 10
    if unit and num != "–":
        tb(c, x, base, unit, "lc400i", 40, vc)
        x += c.tw(unit, "lc400i", 40)
    x += 20
    wcol = 660 - x
    st = v.get("state_text", "")
    ch = v.get("change_24h_text", "")
    tl = " ".join(p for p in (v.get("trend_text", ""), f"{ch} / 24 h" if ch else "") if p)
    # column: state (italic 28) above, trend line (17) on the baseline of the number
    if tl:
        has_arrow = bool(v.get("trend"))
        s2, t2, _ = shrink(c, tl, "lc400", 17, wcol - (24 if has_arrow else 0), min_size=11)
        if has_arrow:
            _arrow(c, x, base - 15, v["trend"], R if v.get("high") else K)
        tb(c, x + (24 if has_arrow else 0), base, t2, "lc400", s2)
    if st:
        s3, t3, _ = shrink(c, st, "lc400i", 28, wcol, min_size=14)
        tb(c, x, base - 30, t3, "lc400i", s3, R if v.get("high") else K)

    # source label
    parts = [(ctx.t("Source", "Quelle").upper(), "lc400", 11, 2, K), (v.get("source", ""), "lc400i", 15, 0, K),
             (ctx.t("Updated {t}", "Stand {t}", t=v.get("now_text", "")), "cav", 20, 0, G)]
    by0 = 160
    bh = 4 + c.line_h("cav", 20) + 4 + 3
    bl = by0 + 5.5 + c._baseline(0, "cav", 20, None)
    xx = 40 + 13.5
    for txt, r, sz, tr, col in parts:
        tb(c, xx, bl, txt, r, sz, col, track=tr)
        xx += c.tw(txt, r, sz, tr) - tr + 12
    label_box(c, 40, by0, xx - 12 + 13.5, by0 + bh)

    # chart
    oy = 210
    X0, X1 = 140, 750
    days = v.get("days") or 7
    small_caps(c, X0, oy + 20 - c._baseline(0, "lc400", 13, None),
               ctx.t("The last {n} days", "Die letzten {n} Tage", n=days), size=13, track=3, width=420)
    vals, xs = v.get("values") or [], v.get("x") or []
    lo_d = min([x for x in (v.get("min"), v.get("mw")) if x is not None] or [0])
    hsw = v.get("hsw")
    hi = hsw if hsw is not None else (v.get("axis_hi") or (max(vals) if vals else 1))
    hi = max(hi, v.get("max") or hi)
    lo = lo_d - 0.18 * (hi - lo_d) if hi > lo_d else lo_d - 10
    yt, yb = oy + 50, oy + 208
    Yf = lambda cm: yb - (cm - lo) / (hi - lo) * (yb - yt)
    labels = []
    if hsw is not None:
        y = Yf(hsw)
        c.rect((X0, y - 0.75, X1, y + 0.75), fill=R)
        tb(c, X0 - 10, y + 5, f"HSW {ctx.num(hsw, 0)}", "lc400", 14, R, align="r")
        s4, t4, _ = shrink(c, ctx.t("highest navigable water level", "höchster Schifffahrtswasserstand"),
                           "lc400i", 14, 440, min_size=10)
        tb(c, X1, y - 8, t4, "lc400i", s4, R, align="r")
        labels.append(y)
    if len(vals) >= 2 and len(xs) == len(vals):
        pts = [(X0 + xx_ * (X1 - X0), Yf(val)) for xx_, val in zip(xs, vals)]
        c.poly(pts + [(X1, yb), (X0, yb)], fill=B)
        c.stroke(pts, K, 2, cap=False)
        if v.get("mw") is not None:
            y = Yf(v["mw"])
            c.rect((X0, y - 0.75, X1, y + 0.75), fill=Wh)
            if all(abs(y - q) > 16 for q in labels):
                tb(c, X0 - 10, y + 5, f"MW {ctx.num(v['mw'], 0)}", "lc400", 14, align="r")
        berry(c, X1, pts[-1][1], 7)
    c.rect((X0, yb - 0.75, X1, yb + 0.75), fill=K)
    ticks = v.get("day_ticks") or []
    for i, dtk in enumerate(ticks):
        x = X0 + dtk["x"] * (X1 - X0)
        c.vline(x - 0.5, yb, yb + 6, K, 1)
        nxt = X0 + (ticks[i + 1]["x"] if i + 1 < len(ticks) else 1.0) * (X1 - X0)
        if nxt - x >= 24:
            tb(c, (x + nxt) / 2, oy + 230, dtk["weekday"], "lc400", 14, align="c")
    return c.finish()


# ================================================================== birthdays
def birthdays(ctx, v):
    c = _canvas()
    for d in ("M 120 440 C 116 380 110 260 70 150", "M 122 440 C 124 360 130 240 120 90",
              "M 124 440 C 130 390 150 300 180 200"):
        c.path(d, stroke=G, width=3)
    for lf in ((116, 380, -1, 30, 70), (126, 340, 1, 30, 64), (112, 290, -1, 26, 50), (146, 300, 1, 30, 50),
               (122, 210, -1, 20, 42), (124, 160, 1, 22, 40)):
        leaf(c, *lf)
    for k in range(6):
        a = k * math.pi / 3
        berry(c, 120 + 14 * math.cos(a), 84 + 14 * math.sin(a), 11, R)
    berry(c, 120, 84, 9, Y)
    berry(c, 68, 144, 10, Y)
    berry(c, 182, 194, 9, R)
    c.poly([(100, 420), (146, 420), (140, 452), (106, 452)], fill=Wh, outline=K, width=2)
    c.path("M 104 428 Q 123 440 142 428", stroke=R, width=2)

    X, Wd = 260, 500
    if v.get("festive"):
        top = v.get("festive_title", "")
        big = v.get("festive_names", "")
        sub = v.get("festive_line", "") or ctx.date(v["today"])
        rows = [p for p in v["people"] if p["days"] > 0][:4]
        topcol = R
    else:
        f = v["first"]
        top = f["when"]
        big = f"{f['name']} {f['age_text']}".strip() if f.get("age_text") else f["name"]
        sub = f["date_long"]
        rows = v["others"][:4]
        topcol = G
    y = 30
    s, t, _ = shrink(c, top, "cav", 32, Wd, min_size=18)
    c.text(X, y, t, "cav", s, topcol)
    y += c.line_h("cav", 32) + 2
    size, lines, L, _ = c.fit(big, "lc400i", 60, Wd, 2 * 63, lh=1.05, min_size=26)
    if len(lines) > 2:
        lines = lines[:2]
        lines[-1] = ell(c, lines[-1] + " …", "lc400i", size, Wd)
    if len(lines) == 1 and size == 60:
        L = 63
    c.para(X, y, Wd, lines, "lc400i", size, L)
    y += len(lines) * L + 2 + 4
    s, t, _ = shrink(c, sub, "lc400", 22, Wd, min_size=13)
    c.text(X, min(y, 172), t, "lc400", s)

    y = 206
    c.hline(X, X + 60, y + 3, K, 1)
    c.circle(X + 73.5, y + 3.5, 3.5, fill=G)
    c.hline(X + 87, X + 147, y + 3, K, 1)
    y += 7 + 8
    for p in rows:
        base = y + 8 + c._baseline(0, "lc400i", 24, None)
        ins = p["when"]
        iw = c.tw(ins, "cav", 24)
        tb(c, X + Wd, base, ins, "cav", 24, G, align="r")
        s1, t1, _ = shrink(c, p["name"], "lc400i", 24, 140, min_size=14)
        tb(c, X, base, t1, "lc400i", s1)
        tb(c, X + 154, base, ell(c, p["date_short"], "lc400", 18, 80), "lc400", 18)
        if p.get("age_text"):
            s2, t2, _ = shrink(c, p["age_text"], "lc400", 18, X + Wd - iw - 14 - (X + 248), min_size=11)
            tb(c, X + 248, base, t2, "lc400", s2)
        c.hline(X, X + Wd, y + 47, K, 1)
        y += 48
    foot = " · ".join(p for p in (v["title"], v.get("place", ""), f"No. {v['today'].timetuple().tm_yday}") if p)
    small_caps(c, X, 480 - 22 - c.line_h("lc400", 11), foot, width=Wd)
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    c = _canvas()
    sprig(c, 560, 0, "M 240 26 C 190 30 140 22 84 48",
          [(190, 26, -1, 22, 36), (160, 27, 1, -28, 28), (128, 32, -1, 20, 38), (108, 40, 1, -30, 22)], (80, 51, 9, R))
    ts = 40
    while ts > 24 and c.tw(v["title"], "lc400i", ts) > 300:
        ts -= 2
    base = 24 + c._baseline(0, "lc400i", 40, None)
    tt = ell(c, v["title"], "lc400i", ts, 300)
    tb(c, 40, base, tt, "lc400i", ts)
    x2 = 40 + c.tw(tt, "lc400i", ts) + 18
    s2, t2, _ = shrink(c, v.get("subtitle", ""), "cav", 24, 620 - x2, min_size=13)
    tb(c, x2, base, t2, "cav", s2, G)

    items = v["items"][:6]
    n = len(items)
    rowh, gap = (160, 16) if n <= 4 else (108, 8)
    lh11 = c.line_h("lc400", 11)
    for k, it in enumerate(items):
        x0 = 40 + (k % 2) * (352 + 16)
        y0 = 92 + (k // 2) * (rowh + gap)
        c.rect((x0, y0, x0 + 352, y0 + rowh), outline=K, width=2)
        ix, iw = x0 + 17.5, 352 - 35
        y = y0 + 11.5
        col = COL.get(it.get("color"), K) if it.get("ok") else K
        # row 1: period + daily change
        b1 = y + c._baseline(0, "lc400", 17, None)
        if it.get("ok"):
            chg = it["change_text"]
            tb(c, ix + iw, b1, chg, "lc400", 17, col, align="r")
            per = ctx.t("{n} days", "{n} Tage", n=v["days"]) + " " + it["period_text"]
            pw = iw - c.tw(chg, "lc400", 17) - 12
            s, t, tr = shrink(c, per.upper(), "lc400", 11, pw, 2, 8)
            tb(c, ix, b1, t, "lc400", s, track=tr)
        elif it.get("error"):
            s, t, tr = shrink(c, it["error"], "lc400i", 13, iw, 0, 9)
            tb(c, ix, b1, t, "lc400i", s, R)
        y += c.line_h("lc400", 17) + 4
        # row 2: name + last close
        b2 = y + c._baseline(0, "lc400i", 24, None)
        last = it["last_text"] if it.get("ok") else "–"
        lw = c.tw(last, "lc400", 24)
        tb(c, ix + iw, b2, last, "lc400", 24, align="r")
        s, t, _ = shrink(c, it["label"], "lc400i", 24, iw - lw - 14, min_size=13)
        tb(c, ix, b2, t, "lc400i", s)
        y += c.line_h("lc400i", 24) + 4 + 4
        sh = y0 + rowh - 12 - y
        if sh >= 16:
            c.hline(ix, ix + 316, y + sh - 2, K, 1)
            if it.get("ok") and len(it["values"]) >= 2:
                vals = it["values"]
                mn, mx = min(vals), max(vals)
                rng = (mx - mn) or 1
                pts = [(ix + 4 + i * (300 / (len(vals) - 1)), y + 6 + (1 - (val - mn) / rng) * (sh - 14))
                       for i, val in enumerate(vals)]
                c.stroke(pts, col, 2.5)
                c.circle(pts[-1][0], pts[-1][1], 5, fill=col, outline=K, width=1)
    small_caps(c, 40, 480 - 18 - lh11, v.get("footer", ""), width=720)
    return c.finish()
