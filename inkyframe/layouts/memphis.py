"""Memphis – signature layouts for the plugins (ports of mockups/project/Memphis-*.dc.html).

Bold primaries, hard offset shadows, rotated red tags, zigzags, squiggles, triangles and dot grids.
Fonts: rmo = Rubik Mono One, r800 / r700 = Rubik.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from ..designs import _hard_box, moon_disc, numeric_date
from ..studio import B, G, K, R, Y, Canvas, Wh
from ..studio import H as SH
from ..studio import W as SW

T = "memphis"
COL = {"red": R, "yellow": Y, "green": G, "blue": B, "black": K, "white": Wh}


# ================================================================== helpers
class _Canvas(Canvas):
    """Canvas with a work-around for data/fonts/memphis/st-rmo.ttf: its upper-case Ä/À are swapped and
    FreeType's stroker drops the accents of composite glyphs. The face is caps-only, so its lower-case
    glyphs look the same and are correct -> Rubik Mono One text is drawn and measured in lower case."""

    def text(self, x, top, text, role, size, *a, **kw):
        if role == "rmo":
            text = text.lower()
            kw.pop("upper", None)
        return super().text(x, top, text, role, size, *a, **kw)

    def tw(self, text, role, size, track=0.0):
        return super().tw(text.lower() if role == "rmo" and text else text, role, size, track)


def _col(name, default=K):
    return COL.get(name or "", default)


def _fs(c, text, role, size, maxw, track=0.0, mn=9):
    """Largest size <= size at which text fits maxw on one line."""
    while size > mn and c.tw(text, role, size, track) - track > maxw:
        size -= 1
    return size


def _ell(c, text, role, size, maxw, track=0.0):
    if c.tw(text, role, size, track) - track <= maxw:
        return text
    while text and c.tw(text + "…", role, size, track) - track > maxw:
        text = text[:-1]
    return text.rstrip() + "…"


def _one(c, text, role, size, maxw, track=0.0, mn=12):
    """Shrink to mn, then ellipsis. Returns (text, size)."""
    s = _fs(c, text, role, size, maxw, track, mn)
    return _ell(c, text, role, s, maxw, track), s


def _lines(c, text, role, size, maxw, maxl, track=0.0):
    """Wrap; at most maxl lines (last one ellipsised)."""
    ls = c.wrap(text, role, size, maxw, track)
    if len(ls) > maxl:
        ls = ls[:maxl]
        ls[-1] = _ell(c, ls[-1] + " …", role, size, maxw, track) if c.tw(ls[-1] + "…", role, size, track) > maxw \
            else ls[-1] + "…"
    return [_ell(c, l, role, size, maxw, track) for l in ls]


def _tag(c, text, x, y, size=15, track=2, deg=3, maxw=None, pad=(4, 12), fill=R, ink=Wh, border=3, mn=9):
    """Rotated label box; (x, y) = top-left of the unrotated box (CSS layout). Returns (w, h)."""
    if maxw:
        size = _fs(c, text, "r800", size, maxw - 2 * pad[1] - 2 * border, track, mn)
        text = _ell(c, text, "r800", size, maxw - 2 * pad[1] - 2 * border, track)
    tw = c.tw(text, "r800", size, track) - track
    h = c.line_h("r800", size)
    bw, bh = tw + 2 * pad[1] + 2 * border, h + 2 * pad[0] + 2 * border
    lay, ld = c.layer(bw, bh)
    ld.rectangle((0, 0, math.ceil(bw) - 1, math.ceil(bh) - 1), fill=fill, outline=K, width=border)
    c.text(border + pad[1], border + pad[0], text, "r800", size, ink, track=track, draw=ld)
    c.paste_rotated(lay, x + bw / 2, y + bh / 2, deg)
    return bw, bh


def _pop(c, x, y, text, size, fill=Wh, shadow=R, sh=6, ring=3, role="rmo", align="l"):
    """Rubik Mono One with -webkit-text-stroke and a hard text-shadow (lh 1). The stroke is a dilated glyph
    mask (PIL's stroke loses the accents of this font's composite glyphs)."""
    st = max(1, round(ring / 2))
    m = Image.new("L", (SW, SH), 0)
    md = ImageDraw.Draw(m)
    md.fontmode = "1"
    c.text(x, y, text, role, size, 255, lh=1, align=align, draw=md)
    outer = m.filter(ImageFilter.MaxFilter(2 * st + 1))
    if sh:
        shifted = Image.new("L", (SW, SH), 0)
        shifted.paste(outer, (sh, sh))
        c.img.paste(shadow, (0, 0, SW, SH), shifted)
    c.img.paste(K, (0, 0, SW, SH), outer)
    c.img.paste(fill, (0, 0, SW, SH), m)


def _kv(c, x, y, label, value, shadow, w=None, vsize=22, lsize=12, pad=(6, 10), sh=5, maxw=300, vcol=K,
        fill=Wh, lcol=K):
    """Box with small label + big value (border 3, hard shadow). w=None: auto width. Returns (w, h)."""
    label = label.upper()
    if w is None:
        inner = min(maxw - 2 * pad[1] - 6, max(c.tw(label, "r700", lsize), c.tw(value, "r800", vsize)))
        w = inner + 2 * pad[1] + 6
    inner = w - 2 * pad[1] - 6
    label, ls = _one(c, label, "r700", lsize, inner, mn=8)
    value, vs = _one(c, value, "r800", vsize, inner, mn=11)
    h = 6 + 2 * pad[0] + c.line_h("r700", lsize) + c.line_h("r800", vsize)
    _hard_box(c, (x, y, x + w, y + h), shadow, sh, fill=fill)
    c.text(x + 3 + pad[1], y + 3 + pad[0], label, "r700", ls, lcol)
    c.text(x + 3 + pad[1], y + 3 + pad[0] + c.line_h("r700", lsize), value, "r800", vs, vcol)
    return w, h


def _zig(c, pts, col=K, w=4):
    c.stroke(pts, col, w, cap=False)


def _zigzag(c, x, y, n, step, amp, col=K, w=4):
    _zig(c, [(x + i * step, y if i % 2 == 0 else y - amp) for i in range(n)], col, w)


def _tri(c, pts, fill, w=3):
    c.poly(pts, fill=fill, outline=K, width=w)


def _dots(c, x0, y0, nx, ny, dx=16, dy=16, r=3, col=K):
    for j in range(ny):
        for i in range(nx):
            c.circle(x0 + i * dx, y0 + j * dy, r, fill=col)


def _sq(c, x, y, col, w=5, humps=4, s=15):
    c.path(f"M {x} {y} q {s} {-s * 4 / 3:.2f} {2 * s} 0" + f" t {2 * s} 0" * (humps - 1), stroke=col, width=w)


def _rbox(c, box, r, fill, outline=K, width=4, shadow=None, sh=0):
    x0, y0, x1, y1 = box
    if shadow is not None and sh:
        c.rrect((x0 + sh, y0 + sh, x1 + sh, y1 + sh), r, fill=shadow)
    c.rrect(box, r, fill=fill, outline=outline, width=width)


def _disc(c, cx, cy, d, fill, border=3, shadow=None, sh=0, outline=K):
    """CSS circle of outer diameter d."""
    r = d / 2
    if shadow is not None and sh:
        c.circle(cx + sh, cy + sh, r, fill=shadow)
    c.circle(cx, cy, r, fill=outline)
    c.circle(cx, cy, r - border, fill=fill)


def _paste(c, img, x, y, w, h, ctx, cover=True):
    if img is None:
        return False
    if cover:
        im = ctx.cover_fit(img.convert("RGB"), w, h)
    else:
        s = min(w / img.width, h / img.height)
        im = img.convert("RGB").resize((max(1, round(img.width * s)), max(1, round(img.height * s))))
    c.img.paste(im, (round(x + (w - im.width) / 2), round(y + (h - im.height) / 2)))
    return True


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = _Canvas(T, Wh)
    _zigzag(c, 560, 32, 7, 20, 20, K, 4)
    _tri(c, [(740, 14), (772, 68), (708, 68)], Y)
    _sq(c, 610, 462, B)
    _dots(c, 470, 20, 5, 3)
    _hard_box(c, (36, 36, 444, 444), K, 10, border=4)
    last = {tuple(rc) for rc in (v.get("last_cells") or [])}
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            x, y = 40 + col * 50, 40 + r * 50
            bg = G if (r, col) in last else (Y if (r + col) % 2 == 1 else Wh)
            c.rect((x, y, x + 50, y + 50), fill=bg)
            chess_puzzle.draw_piece(c.d, p, x + 25, y + 25, 50, ink=K, paper=Wh)
    X, Wd = 486, 280
    y = 84
    _, th = _tag(c, (v["title"] + "!").upper(), X, y, maxw=Wd + 10)
    y += th + 16
    # side to move
    L = c.line_h("r800", 26)
    _disc(c, X + 14, y + L / 2, 28, K if not v["white_to_move"] else Wh, shadow=Y, sh=3)
    t, s = _one(c, v["to_move"], "r800", 26, Wd - 38, mn=14)
    c.text(X + 38, y, t, "r800", s, K)
    y += L + 16
    big = (v["mate"] or ctx.t("Your move!", "Dein Zug!")).upper()
    size, lines, LL, _ = c.fit(big, "rmo", 52, Wd - 8, 2 * 52 + 2, lh=1, min_size=24)
    for ln in lines[:2]:
        _pop(c, X, y, ln, size)
        y += size + 2
    y += 14
    if v["themes_text"] or v["themes"]:
        th_text = " · ".join(t for t in v["themes"] if t != v["mate"]) or v["themes_text"]
        ts = _fs(c, th_text, "r700", 17, Wd, mn=13)
        ls = _lines(c, th_text, "r700", ts, Wd, 2)
        for ln in ls:
            c.text(X, y, ln, "r700", ts, K)
            y += c.line_h("r700", ts)
        y += 16
    boxes = []
    if v.get("rating"):
        boxes.append((ctx.t("Rating", "Wertung"), str(v["rating"]), Y))
    boxes.append((ctx.t("Solution", "Lösung"),
                  ctx.t("{n} moves", "{n} Züge", n=v["moves"]) if v["moves"] != 1 else ctx.t("1 move", "1 Zug"), G))
    bw = (Wd - 14 * (len(boxes) - 1)) / len(boxes)
    bh = 0
    for i, (lab, val, sc) in enumerate(boxes):
        _, bh = _kv(c, X + i * (bw + 14), y, lab, val, sc, w=bw)
    y += bh + 20
    t, s = _one(c, v["hint"], "rmo", 12, Wd, mn=8)
    c.text(X, min(y, 432), t, "rmo", s, B)
    return c.finish()


# ================================================================== spotify
def _cover_art(c, x, y):
    """The mockup's abstract stand-in cover (used when there is no picture)."""
    c.rect((x, y, x + 352, y + 352), fill=B)
    c.rect((x, y + 236, x + 352, y + 352), fill=Y)
    c.hline(x, x + 352, y + 234, K, 4)
    c.circle(x + 132, y + 150, 94, fill=K)
    c.circle(x + 132, y + 150, 90, fill=R)
    c.poly([(x + 214, y + 66), (x + 320, y + 236), (x + 108, y + 236)], fill=Wh, outline=K, width=4)
    c.path(f"M {x + 70} {y + 290} q 18 -24 36 0 t 36 0 t 36 0 t 36 0 t 36 0", stroke=K, width=6)
    c.path(f"M {x + 250} {y + 352} a 60 60 0 0 1 120 0 z", fill=G, stroke=K, width=4)
    for j in range(4):
        for i in range(4):
            c.circle(x + 268 + i * 18, y + 24 + j * 18, 4, fill=Wh)
    _zig(c, [(x + 20, y + 40), (x + 36, y + 24), (x + 52, y + 40), (x + 68, y + 24), (x + 84, y + 40)], Y, 5)


def spotify(ctx, v):
    c = _Canvas(T, Wh)
    _zigzag(c, 600, 30, 7, 20, 20, G, 5)
    _sq(c, 40, 458, R)
    _tri(c, [(250, 440), (280, 470), (220, 470)], B)
    _disc(c, 766, 40, 36 + 6, Y)
    # cover
    _hard_box(c, (40, 46, 400, 406), K, 12, fill=B, border=4)
    if v.get("image") is not None:
        c.img.paste(ctx.punch(ctx.cover_fit(v["image"].convert("RGB"), 352, 352)), (44, 50))
    else:
        _cover_art(c, 44, 50)
        c.rect((40, 46, 400, 406), outline=K, width=4)
    X, Wd = 444, 316
    y = 50
    _, th = _tag(c, (v["label"] + "!").upper(), X, y, maxw=Wd)
    y += th + 14 + 4
    # bottom stack (from the bottom up)
    bot = 430
    sp_h = c.line_h("rmo", 13)
    c.text(X + Wd, bot - sp_h, v["source"], "rmo", 13, G, align="r")
    bot -= sp_h + 14
    if v["duration_text"]:
        c.text(X + Wd, bot - sp_h, v["duration_text"], "rmo", 13, K, align="r")
        c.text(X, bot - sp_h, "♫", "r800", 13, K)
        bot -= sp_h + 4 + 6
    # decorative bar (no playback position)
    c.rect((X + 5, bot - 22 + 5, X + Wd + 5, bot + 5), fill=K)
    c.rect((X, bot - 22, X + Wd, bot), fill=Wh)
    seg = (Wd - 6) / 8
    for i in range(8):
        c.rect((X + 3 + i * seg, bot - 19, X + 3 + (i + 1) * seg, bot - 3), fill=(R, Y, B, G)[i % 4])
        if i:
            c.vline(X + 3 + i * seg - 1, bot - 19, bot - 3, K, 3)
    c.rect((X, bot - 22, X + Wd, bot), outline=K, width=3)
    avail_bot = bot - 22 - 14
    # album box, artist, title
    alb_h = (6 + 12 + c.line_h("r700", 12) + c.line_h("r800", 18) + 5) if v["album"] else 0
    art_h = c.line_h("r800", 22) if v["artist"] else 0
    rest = (alb_h + 14 if alb_h else 0) + (art_h + 14 if art_h else 0)
    size, lines, L, _ = c.fit(v["track"], "r800", 30, Wd, max(40, avail_bot - y - rest), lh=1.12, min_size=16)
    lines = lines[:max(1, int((avail_bot - y - rest) // L))]
    if len(c.wrap(v["track"], "r800", size, Wd)) > len(lines):
        lines[-1] = _ell(c, lines[-1] + "…", "r800", size, Wd)
    c.para(X, y, Wd, lines, "r800", size, L, K)
    y += len(lines) * L + 14
    if v["artist"]:
        t, s = _one(c, v["artist"], "r800", 22, Wd, mn=14)
        c.text(X, y, t, "r800", s, B)
        y += art_h + 14
    if v["album"]:
        _kv(c, X, y, ctx.t("Album", "Album"), v["album"], Y, vsize=18, pad=(6, 12), maxw=Wd)
    return c.finish()


# ================================================================== grid (Stromampel)
def grid(ctx, v):
    c = _Canvas(T, Wh)
    _zigzag(c, 580, 30, 7, 20, 20, K, 4)
    _tri(c, [(720, 150), (760, 220), (680, 220)], B)
    _sq(c, 610, 300, R)
    _dots(c, 600, 90, 4, 3)
    sig = _col(v["color"], Y)
    # traffic light
    _rbox(c, (44, 30, 168, 320), 26, K, K, 4, shadow=sig if v["color"] else Y, sh=10)
    for i, lt in enumerate(v["lights"]):
        cy = 34 + 15 + 37 + i * 89
        lc = _col(lt["color"])
        if lt["on"]:
            c.circle(106, cy, 37, fill=Wh)
            c.circle(106, cy, 33, fill=lc)
        else:
            c.circle(106, cy, 37, fill=lc)
            c.circle(106, cy, 31, fill=Wh)
    X, Wd = 210, 460
    y = 34
    _, th = _tag(c, f"{v['title']} {v['now_label']}!".upper(), X, y, maxw=Wd + 80)
    y += th + 12
    parts = (v["signal_name"] or "–").split(" · ")
    big = parts[0].upper()
    s = _fs(c, big, "rmo", 92, 380, mn=40)                 # clear of the dot grid
    _pop(c, X, y, big, s, fill=sig if v["color"] else Wh, shadow=K, sh=8, ring=4)
    y += s + 12
    sub = parts[1:]
    if v["share_text"]:
        sub.append(ctx.t("{p} renewables", "{p} Ökostrom", p=v["share_text"]))
    if sub:
        t, ss = _one(c, " · ".join(sub), "r800", 28, Wd, mn=16)       # clear of the triangle
        c.text(X, y, t, "r800", ss, K)
        y += c.line_h("r800", 28) + 12
    tip = {"green": ctx.t("Wash, charge, run the dishwasher now", "Jetzt waschen, laden, spülen"),
           "yellow": ctx.t("Better wait for green", "Besser auf Grün warten"),
           "red": ctx.t("Postpone big consumers", "Großverbraucher verschieben")}.get(v["color"])
    if tip:
        _kv(c, X, y + 4, ctx.t("Tip", "Tipp"), tip, sig, vsize=22, pad=(8, 14), sh=6, maxw=540)
    # 24 h band
    bx0, by0, bx1, by1 = 40, 344, 752, 448
    _hard_box(c, (bx0, by0, bx1, by1), K, 8)
    ix0, ix1 = bx0 + 3 + 14, bx1 - 3 - 14
    hy = by0 + 3 + 8
    hl = ctx.t("Today · 0–24 h", "Heute · 00–24 Uhr").upper()
    hl, hs = _one(c, hl, "r800", 12, 220, mn=9)
    c.text(ix0, hy, hl, "r800", hs, K)
    if v["best_text"]:
        bw = ix1 - ix0 - c.tw(hl, "r800", hs) - 18 - 18
        t, s2 = _one(c, v["best_text"], "r700", 12, bw, mn=9)
        tw = c.tw(t, "r700", s2)
        c.text(ix1, hy, t, "r700", s2, K, align="r")
        sx = ix1 - tw - 6 - 16
        c.rect((sx, hy + 1, sx + 16, hy + 17), fill=K)
        c.rect((sx + 2, hy + 3, sx + 14, hy + 15), fill=G)
    gy0 = hy + 15 + 6
    gy1 = gy0 + 34
    c.rect((ix0, gy0, ix1, gy1), fill=Wh)
    gx0, gx1 = ix0 + 3, ix1 - 3
    cw = (gx1 - gx0) / 24
    for i, h in enumerate(v["hours"][:24]):
        a = gx0 + i * cw
        c.rect((a, gy0 + 3, a + cw, gy1 - 3), fill=_col(h.get("color"), Wh))
        if i < 23:
            c.vline(a + cw - 2, gy0 + 3, gy1 - 3, K, 2)
    c.rect((ix0, gy0, ix1, gy1), outline=K, width=3)
    nx = gx0 + (gx1 - gx0) * max(0.0, min(1.0, v["now_pos"]))
    c.rect((nx - 2, gy0 - 8, nx + 3, gy1 + 8), fill=K)
    ly = gy1 + 6
    nt = v["time"]
    ntw = c.tw(nt, "rmo", 11)
    c.text(nx, ly, nt, "rmo", 11, R, align="c")
    for frac, lab in ((0, "00"), (.25, "06"), (.5, "12"), (.75, "18"), (1, "24")):
        px = gx0 + (gx1 - gx0) * frac
        lw = c.tw(lab, "rmo", 11)
        x0 = px if frac == 0 else px - lw if frac == 1 else px - lw / 2
        if x0 + lw + 6 > nx - ntw / 2 and x0 - 6 < nx + ntw / 2:
            continue
        c.text(x0, ly, lab, "rmo", 11, K)
    src, s3 = _one(c, v["source"], "r700", 11, 700, mn=8)
    c.text(40, 459, src, "r700", s3, K)
    return c.finish()


# ================================================================== wordclock
def wordclock(ctx, v):
    c = _Canvas(T, Wh)
    _sq(c, 22, 26, B)
    _zigzag(c, 650, 464, 7, 16, 16, K, 4)
    _tri(c, [(60, 400), (96, 460), (24, 460)], G)
    _dots(c, 700, 16, 4, 3, 16, 10)
    # date column (centre x = 92)
    cx = 92
    y = 66
    wd = v["weekday"].upper()
    s = _fs(c, wd, "r800", 14, 150 - 26, 2, 9)
    tw = c.tw(wd, "r800", s, 2) - 2 + 26
    _, th = _tag(c, wd, cx - tw / 2, y, size=s, deg=4, pad=(4, 10))
    y += th + 12
    _disc(c, cx, y + 58, 116, Y, border=4, shadow=K, sh=6)
    day = str(v["day"])
    c.text(cx, y + 58 - 25, day, "rmo", 50, K, lh=1, align="c")
    y += 116 + 12 + 4
    my = f"{v['month'][:3].upper()} {v['year']}"
    s = _fs(c, my, "r800", 18, 150, 2, 10)
    c.text(cx + 1, y, my, "r800", s, K, track=2, align="c")
    y += c.line_h("r800", 18) + 12
    wk = ctx.t("WK {n}", "KW {n}", n=v["week"])
    c.text(cx, y, wk, "rmo", _fs(c, wk, "rmo", 12, 150), B, align="c")
    # letter grid
    _hard_box(c, (180, 36, 620, 440), Y, 12, fill=K, border=4)
    lit = {tuple(rc) for rc in v["lit"]}
    rows, cols = v["rows"], v["cols"]
    cs = min(36, 396 // max(1, cols), 360 // max(1, rows))
    gx = 180 + 4 + 18 + (396 - cs * cols) / 2
    gy = 36 + 4 + 18 + (360 - cs * rows) / 2
    fs = round(20 * cs / 36)
    lh = c.line_h("rmo", fs, 1)
    for r, line in enumerate(v["grid"]):
        for k, ch in enumerate(line):
            col = Y if (r, k) in lit else B
            c.text(gx + k * cs + cs / 2, gy + r * cs + (cs - lh) / 2, ch, "rmo", fs, col, lh=1, align="c")
    # right column (centre x = 714)
    cx = 714
    y = 50
    q = v["minute"] // 15
    for i in range(4):
        _disc(c, cx - 39 + 9 + i * 26, y + 9, 18, R if i < q else Wh)
    y += 18 + 12
    y += c.line_h("r800", 12) + 12          # (the mockup's "+ 2 MINUTEN" line: not in the data)
    # dial
    _disc(c, cx, y + 52, 104, Wh, shadow=B, sh=6)
    ox, oy, sc = cx - 49, y + 3, 0.98
    for bx, by, bw, bh in ((47, 6, 6, 12), (47, 82, 6, 12), (6, 47, 12, 6), (82, 47, 12, 6)):
        c.rect((ox + bx * sc, oy + by * sc, ox + (bx + bw) * sc, oy + (by + bh) * sc), fill=K)
    ccx, ccy = ox + 50 * sc, oy + 50 * sc
    ha = math.radians((v["hour"] % 12 + v["minute"] / 60) * 30)
    ma = math.radians(v["minute"] * 6)
    c.stroke([(ccx, ccy), (ccx + 22 * sc * math.sin(ha), ccy - 22 * sc * math.cos(ha))], K, 6)
    c.stroke([(ccx, ccy), (ccx + 34 * sc * math.sin(ma), ccy - 34 * sc * math.cos(ma))], R, 4)
    c.circle(ccx, ccy, 5, fill=K)
    y += 104 + 12 + 2
    c.text(cx, y, v["time"], "rmo", 18, K, align="c")
    y += c.line_h("rmo", 18) + 12 + 4
    c.circle(cx + 4, y + 21 + 4, 21, fill=Y)
    c.circle(cx, y + 21, 21, fill=K)
    moon_disc(c, cx, y + 21, 18, v["phase"], Wh, K, K)
    y += 42 + 12
    t, s = _one(c, v["moon"].upper(), "r800", 12, 150, mn=8)
    c.text(cx, y, t, "r800", s, K, align="c")
    return c.finish()


# ================================================================== countdown
def countdown(ctx, v):
    c = _Canvas(T, Y)
    c.circle(800, 0, 64, fill=K)
    c.circle(800, 0, 60, fill=B)
    _sq(c, 20, 24, K)
    _tri(c, [(720, 260), (760, 330), (680, 330)], Wh)
    _zigzag(c, 470, 330, 7, 20, 20, G, 5)
    # big box
    _hard_box(c, (40, 40, 420, 356), K, 14, border=4)
    X, Wd = 40 + 4 + 28, 380 - 8 - 56
    y = 40 + 4 + 22
    tag = {"future": ctx.t("To go!", "Noch!"), "past": ctx.t("Already!", "Schon!"),
           "today": ctx.t("It's today!", "Heute ist es so weit!")}.get(v["state"], "!")
    _, th = _tag(c, tag.upper(), X, y, maxw=Wd)
    y += th + 6 + 8
    big = v["big"].upper()
    small = v["small"].upper()
    hb = 356 - 4 - 22 - y - ((6 + c.line_h("rmo", 34, 1) + 6) if small else 0)
    s = min(168, int(hb) - 10)
    s = _fs(c, big, "rmo", s, Wd - 10, mn=30)
    by = y + (hb - s) / 2 if not small else y
    _pop(c, X, by, big, s, fill=Wh, shadow=R, sh=10, ring=5)
    if small:
        y = by + s + 6 + 6
        t, ss = _one(c, small, "rmo", 34, Wd, mn=14)
        c.text(X, y + (34 - ss) / 2, t, "rmo", ss, K, lh=1)
    # event + target
    RX, RW = 462, 300
    y = 70
    size, lines, L, _ = c.fit(v["event"].upper(), "rmo", 26, RW, 4 * 26 * 1.15, lh=1.15, min_size=13)
    lines = _lines(c, " ".join(lines), "rmo", size, RW, 4)
    for ln in lines:
        c.text(RX, y, ln, "rmo", size, K, lh=1.15)
        y += L
    y += 14 + 8
    _, bh = _kv(c, RX, y, ctx.t("Target", "Ziel"), f"{v['target_weekday']}, {v['date']}", G, w=RW,
                vsize=20, pad=(8, 12), sh=6)
    y += bh + 6 + 14
    if v["state"] == "future" and v["weekends"]:
        _kv(c, RX, y, ctx.t("Weekends", "Wochenenden"), str(v["weekends"]), B, vsize=20, pad=(8, 12), sh=6)
    # day strip
    bx0, by0, bx1, by1 = 40, 386, 752, 452
    _hard_box(c, (bx0, by0, bx1, by1), K, 8)
    ix0, ix1 = bx0 + 3 + 10, bx1 - 3 - 10
    hy = by0 + 3 + 6
    left = f"{ctx.t('Today', 'Heute')} · {v['today_short']}".upper()
    right = f"{v['date_short']} {v['event']}!".upper()
    leg = ctx.t("Weekend", "Wochenende").upper()
    lw = c.tw(left, "r800", 12)
    gw = c.tw(leg, "r800", 12) + 16
    right = _ell(c, right, "r800", 12, (ix1 - ix0) - lw - gw - 40)
    rw = c.tw(right, "r800", 12)
    c.text(ix0, hy, left, "r800", 12, K)
    c.text(ix1, hy, right, "r800", 12, R, align="r")
    gx = ix0 + lw + ((ix1 - rw) - (ix0 + lw) - gw) / 2
    c.rect((gx, hy + 3, gx + 10, hy + 13), fill=K)
    c.rect((gx + 2, hy + 5, gx + 8, hy + 11), fill=B)
    c.text(gx + 16, hy, leg, "r800", 12, K)
    sy0, sy1 = hy + c.line_h("r800", 12) + 4, by1 - 3 - 6
    strip = v["strip"]
    n = len(strip)
    if n:
        gap = 3 if n <= 60 else 0
        cw = ((ix1 - ix0) + gap) / n - gap
        for i, d in enumerate(strip):
            x = ix0 + i * (cw + gap)
            col = R if d["target"] else Y if d["today"] else B if d["weekend"] else Wh
            if gap:
                c.rect((x, sy0, x + cw, sy1), fill=K)
                c.rect((x + 2, sy0 + 2, x + cw - 2, sy1 - 2), fill=col)
            else:
                c.rect((x, sy0, x + cw + 0.5, sy1), fill=col)
        if not gap:
            c.rect((ix0, sy0, ix1, sy1), outline=K, width=2)
    return c.finish()


# ================================================================== art
def art(ctx, v):
    c = _Canvas(T, Wh)
    _tri(c, [(742, 12), (774, 66), (710, 66)], R)
    _sq(c, 600, 458, G)
    _zigzag(c, 40, 24, 7, 16, 16, K, 4)
    _dots(c, 600, 20, 4, 3)
    _hard_box(c, (40, 40, 518, 428), B, 12, border=4)
    # picture, fitted inside the 440 × 350 slot, the inner 3 px frame hugs it
    sw, sh = 440, 350
    s = min(sw / v["width"], sh / v["height"])
    w, h = max(1, round(v["width"] * s)), max(1, round(v["height"] * s))
    px, py = 59 + (sw - w) / 2, 59 + (sh - h) / 2
    c.rect((px - 3, py - 3, px + w + 3, py + h + 3), fill=K)
    c.img.paste(v["image"].convert("RGB").resize((w, h)), (round(px), round(py)))
    lab = ctx.t("Picture", "Bild").upper()
    lw = c.tw(lab, "rmo", 11)
    lh = c.line_h("rmo", 11)
    c.rect((px + w - 10 - lw - 16, py + 10, px + w - 10, py + 10 + lh + 6), fill=K)
    c.text(px + w - 10 - 8, py + 13, lab, "rmo", 11, Wh, align="r")
    # text column
    X, Wd = 556, 214
    y = 84
    _, th = _tag(c, (v["title"] + "!").upper(), X, y, size=14, pad=(4, 10), maxw=Wd + 20)
    y += th + 14 + 4
    date = v["date"]
    ds = _fs(c, date.upper(), "rmo", 44, Wd - 6, mn=16) if date else 0
    box_h = 6 + 12 + c.line_h("r700", 12) + c.line_h("r800", 18) + 5
    art_lines = _lines(c, v["artist"], "r700", 20, Wd, 2) if v["artist"] else []
    rest = (len(art_lines) * 23 + 14 if art_lines else 0) + (ds + 14 if date else 0) + box_h
    room = 450 - y - rest
    size, lines, L, _ = c.fit(v["work"], "r800", 30, Wd, room, lh=1.08, min_size=15)
    maxl = max(1, int(room // L))
    if len(lines) > maxl:
        lines = _lines(c, v["work"], "r800", size, Wd, maxl)
    c.para(X, y, Wd, lines, "r800", size, L, K)
    y += len(lines) * L + 14
    for ln in art_lines:
        c.text(X, y, ln, "r700", 20, B, lh=1.15)
        y += 23
    if art_lines:
        y += 14
    if date:
        t = _ell(c, date.upper(), "rmo", ds, Wd - 6)
        _pop(c, X, y, t, ds, fill=Wh, shadow=Y, sh=6 if ds > 24 else 4, ring=3 if ds > 24 else 2)
        y += ds + 14
    _kv(c, X, y, ctx.t("Museum", "Museum"), v["museum"], G, vsize=18, pad=(6, 12), maxw=Wd + 20)
    return c.finish()


# ================================================================== waste
def _bin(c, x, y, s, col, big=False):
    """Wheelie bin from the mockup's 40 × 48 svg, scaled by s."""
    line = K if col in (Y, Wh) else Wh
    w = 2 if big else 3
    P = lambda a, b: (x + a * s, y + b * s)  # noqa: E731
    if big:
        c.rect((x + 14 * s, y + 1 * s, x + 26 * s, y + 6 * s), outline=K, width=max(2, round(2 * s)))
    c.poly([P(7, 13), P(33, 13), P(30, 45), P(10, 45)], fill=col, outline=K, width=max(2, round(w * s)))
    c.rect((x + 3 * s, y + 6 * s, x + 37 * s, y + 13 * s), fill=col)
    c.rect((x + 3 * s, y + 6 * s, x + 37 * s, y + 13 * s), outline=K, width=max(2, round(w * s)))
    for lx in ((15, 20, 25) if big else (20,)):
        c.stroke([P(lx, 18), P(lx, 40)], line, max(2, w * s), cap=False)


def waste(ctx, v):
    c = _Canvas(T, Wh)
    _zigzag(c, 560, 30, 7, 20, 20, K, 4)
    _sq(c, 300, 26, B)
    _tri(c, [(760, 4), (786, 34), (734, 34)], G)
    rows = list(v["rows"])
    soon = v["soon"]
    if soon:
        tag = f"{soon['label']} · {soon['weekday_short']} {soon['date_short']}!"
        items = soon["items"]
    else:
        first = rows[0]
        items = [{"name": r["name"], "color": r["color"]} for r in rows if r["date"] == first["date"]]
        rows = [r for r in rows if r["date"] != first["date"]]
        tag = f"{first['in_text']} · {first['weekday_short']} {first['date_short']}!"
    # hero box
    _hard_box(c, (40, 44, 748, 210), Y, 12, border=4)
    bins = items[:3]
    bw = 84 * len(bins) + 14 * (len(bins) - 1)
    bx = 748 - 4 - 26 - bw
    for i, it in enumerate(bins):
        _bin(c, bx + i * 98, 44 + (166 - 100) / 2, 2.1, _col(it["color"]), big=True)
    X = 40 + 4 + 26
    Wd = bx - 20 - X
    th = c.line_h("r800", 15) + 14                      # height of the tag box
    text = "\n+ ".join(it["name"] for it in items)
    size, lines, L, _ = c.fit(text, "r800", 38, Wd, 166 - 8 - 36 - th - 10, lh=1.05, min_size=16)
    maxl = max(1, int((166 - 8 - 36 - th - 10) // L))
    if len(lines) > maxl:
        lines = lines[:maxl]
        lines[-1] = _ell(c, lines[-1] + "…", "r800", size, Wd)
    blk = th + 10 + len(lines) * L
    y = 44 + (166 - blk) / 2
    _tag(c, tag.upper(), X, y, maxw=Wd)
    y += th + 10
    c.para(X, y, Wd, lines, "r800", size, L, K)
    # list
    y = 236
    if not rows:
        _hard_box(c, (40, y, 748, y + 46), K, 5)
        t, s = _one(c, v["empty_text"], "r800", 20, 708 - 30, mn=12)
        c.text(40 + 15, y + (46 - c.line_h("r800", s)) / 2, t, "r800", s, K)
    for r in rows[:4]:
        col = _col(r["color"])
        _hard_box(c, (40, y, 748, y + 46), col, 5)
        _bin(c, 40 + 3 + 12, y + 6, 0.7, col)
        d = f"{r['weekday_short']} {r['date_short']}".upper()
        d, ds = _one(c, d, "rmo", 16, 140, mn=10)
        tx = 40 + 3 + 12 + 28 + 16
        c.text(tx, y + (46 - c.line_h("rmo", ds)) / 2, d, "rmo", ds, K)
        when = r["in_text"].upper()
        ws = _fs(c, when, "r800", 15, 200, 1, 10)
        ww = c.tw(when, "r800", ws, 1) - 1 + 20
        wx = 748 - 3 - 12 - ww
        wh = c.line_h("r800", ws) + 8
        c.rect((wx, y + (46 - wh) / 2, wx + ww, y + (46 + wh) / 2), fill=K)
        c.text(wx + 10, y + (46 - wh) / 2 + 4, when, "r800", ws, Wh, track=1)
        nx = tx + 140 + 16
        t, s = _one(c, r["name"], "r800", 22, wx - 16 - nx, mn=13)
        c.text(nx, y + (46 - c.line_h("r800", s)) / 2, t, "r800", s, K)
        y += 46 + 9
    return c.finish()


# ================================================================== warnings
def warnings(ctx, v):
    c = _Canvas(T, Y)
    _sq(c, 30, 34, K)
    _sq(c, 40, 420, B, humps=5)
    _sq(c, 60, 450, B)
    _zigzag(c, 30, 90, 5, 16, 16, G, 4)
    acol = _col(v["color"], R)
    # triangle (210 × 186 svg at 50, 100)
    ox, oy = 50, 100
    c.poly([(ox + 113, oy + 22), (ox + 206, oy + 182), (ox + 20, oy + 182)], fill=K)
    c.poly([(ox + 103, oy + 6), (ox + 196, oy + 170), (ox + 10, oy + 170)], fill=R if acol == R else Wh,
           outline=K, width=5)
    for bx, by, bw, bh in ((94, 62, 18, 62), (94, 134, 18, 18)):
        c.rect((ox + bx - 1, oy + by - 1, ox + bx + bw + 1, oy + by + bh + 1), fill=K)
        c.rect((ox + bx + 2, oy + by + 2, ox + bx + bw - 2, oy + by + bh - 2), fill=Wh)
    cx = 155
    y = 100 + 186 + 12
    if v["expires"] is not None:
        big = ctx.t("until {t}", "bis {t}", t=f"{v['expires']:%H:%M}").upper()
    else:
        big = v["onset_text"].upper()
    if big:
        s = _fs(c, big, "rmo", 28, 240, mn=14)
        c.text(cx, y + (28 - s) / 2, big, "rmo", s, K, lh=1, align="c")
        y += 28 + 12
    badge = v["more_text"] or v["place"]
    if badge:
        badge = badge.upper()
        s = _fs(c, badge, "r800", 15, 250 - 20, 2, 10)
        badge = _ell(c, badge, "r800", s, 250 - 20, 2)
        bw = c.tw(badge, "r800", s, 2) - 2 + 20
        bh = c.line_h("r800", s) + 6
        c.rect((cx - bw / 2, y, cx + bw / 2, y + bh), fill=K)
        c.text(cx - bw / 2 + 10, y + 3, badge, "r800", s, Wh, track=2)
    # card
    _hard_box(c, (296, 36, 758, 436), K, 14, border=4)
    X, Wd = 296 + 4 + 28, 462 - 8 - 56
    y = 36 + 4 + 24
    _, th = _tag(c, (ctx.t("Warning", "Warnung") + "!").upper(), X, y, maxw=Wd)
    y += th + 14 + 2
    ev = v["event"].upper()
    size, lines, L, _ = c.fit(ev, "rmo", 40, Wd - 8, 2 * 40, lh=1, min_size=18)
    lines = _lines(c, " ".join(lines), "rmo", size, Wd - 8, 2)
    for ln in lines:
        _pop(c, X, y, ln, size, fill=Wh, shadow=B, sh=6 if size > 24 else 4, ring=3)
        y += size + 2
    y += 14 - 2
    # level row
    lv = ctx.t("Level {n}/{m}", "Stufe {n}/{m}", n=v["level"], m=v["levels"]).upper()
    lvw = c.tw(lv, "r800", 12)
    sq_y = y + (c.line_h("r800", 20) - 20) / 2
    for i in range(v["levels"]):
        x0 = X + i * 29
        c.rect((x0, sq_y, x0 + 24, sq_y + 20), fill=K)
        c.rect((x0 + 3, sq_y + 3, x0 + 21, sq_y + 17), fill=acol if i < v["level"] else Wh)
    lx = X + v["levels"] * 29 - 5 + 12
    t, s = _one(c, v["level_text"], "r800", 20, X + Wd - lvw - 12 - lx, mn=11)
    c.text(lx, y, t, "r800", s, K)
    c.text(X + Wd, y + (c.line_h("r800", 20) - c.line_h("r800", 12)) / 2, lv, "r800", 12, K, align="r")
    y += c.line_h("r800", 20) + 14
    span = v["span"] if (not v["more_text"] and v["place"]) else v["place_span"]
    if span:
        sp, ss = _one(c, span, "r800", 18, Wd - 30, mn=11)
        bw = c.tw(sp, "r800", ss) + 30
        bh = c.line_h("r800", 18) + 18
        _hard_box(c, (X, y, X + bw, y + bh), Y, 5)
        c.text(X + 15, y + 9 + (c.line_h("r800", 18) - c.line_h("r800", ss)) / 2, sp, "r800", ss, K)
        y += bh + 14 + 4
    src_h = c.line_h("rmo", 12)
    bottom = 436 - 4 - 24 - src_h - 10
    text = v["description"] + (("\n" + v["instruction"]) if v["instruction"] else "")
    size, lines, L, _ = c.fit(text, "r700", 18, Wd, bottom - y, lh=1.32, min_size=11)
    maxl = max(0, int((bottom - y) // L))
    if len(lines) > maxl:
        lines = _lines(c, " ".join(lines), "r700", size, Wd, maxl) if maxl else []
    c.para(X, y, Wd, lines, "r700", size, L, K)
    t, s = _one(c, v["source"], "rmo", 12, Wd, mn=8)
    c.text(X, 436 - 4 - 24 - src_h, t, "rmo", s, B)
    return c.finish()


# ================================================================== wifi
def wifi(ctx, v):
    from ..plugins import wifi as W
    c = _Canvas(T, Wh)
    c.circle(36, 40, 54, fill=K)
    c.circle(36, 40, 50, fill=B)
    _sq(c, 60, 452, R)
    _zigzag(c, 600, 30, 7, 20, 20, K, 4)
    _tri(c, [(740, 380), (776, 442), (704, 442)], G)
    _dots(c, 600, 410, 4, 3, 14, 14)
    _hard_box(c, (60, 62, 408, 410), K, 12, border=4)
    W.draw_modules(c.d, v["modules"], 64 + 4, 66 + 4, 332, dark=K, light=Wh, quiet=2)
    X, Wd = 456, 304
    y = 58
    _, th = _tag(c, (v["title"] + "!").upper(), X, y, maxw=Wd)
    y += th + 12
    c.text(X, y, _ell(c, v["network_label"].upper(), "r800", 12, Wd), "r800", 12, K)
    y += c.line_h("r800", 12) + 6
    ssid = v["ssid"]
    ss = _fs(c, ssid, "rmo", 46, Wd - 8, mn=16)
    ssid = _ell(c, ssid, "rmo", ss, Wd - 8)
    L = ss * 1.05
    _pop(c, X, y + (L - ss) / 2, ssid, ss, fill=Wh, shadow=B, sh=6 if ss > 24 else 4, ring=3)
    y += L + 12
    if v["password"]:
        _, bh = _kv(c, X, y, v["password_label"], v["password"], Y, vsize=30, pad=(8, 14), sh=6, maxw=Wd)
        y += bh + 12
    # security
    if v["security"]:
        badge, txt, bcol = v["security"], ctx.t("Encryption", "Verschlüsselung"), B
    else:
        badge, txt, bcol = ctx.t("Open", "Offen").upper(), ctx.t("No password", "Kein Passwort"), G
    bw = c.tw(badge, "rmo", 14) + 26
    bh = c.line_h("rmo", 14) + 12
    c.rect((X, y, X + bw, y + bh), fill=bcol, outline=K, width=3)
    c.text(X + 13, y + 6, badge, "rmo", 14, Wh)
    t, s = _one(c, txt, "r700", 13, Wd - bw - 10, mn=9)
    c.text(X + bw + 10, y + (bh - c.line_h("r700", s)) / 2, t, "r700", s, K)
    y += bh + 12 + 10
    # arrow + hint
    ls = _lines(c, v["hint"], "r800", 20, Wd - 56, 2)
    hh = len(ls) * c.line_h("r800", 20)
    ay = y + (hh - 28) / 2
    c.poly([(X, ay + 14), (X + 16, ay + 2), (X + 16, ay + 9), (X + 42, ay + 9), (X + 42, ay + 19), (X + 16, ay + 19),
            (X + 16, ay + 26)], fill=G, outline=K, width=3)
    for ln in ls:
        c.text(X + 56, y, ln, "r800", 20, K)
        y += c.line_h("r800", 20)
    if v["note"] and y < 430:
        y += 12
        for ln in _lines(c, v["note"], "r700", 16, 240, max(1, int((462 - y) // 19))):   # clear of the triangle
            c.text(X, y, ln, "r700", 16, B)
            y += 19
    return c.finish()


# ================================================================== habits
def habits(ctx, v):
    c = _Canvas(T, Wh)
    _sq(c, 300, 38, B)
    _zigzag(c, 440, 40, 7, 16, 16, K, 4)
    _tri(c, [(770, 440), (796, 480), (744, 480)], Y)
    rt1 = ctx.t("Last 6 weeks", "Letzte 6 Wochen").upper()
    rt2 = ctx.t("until {d}", "bis {d}", d=f"{v['weekday_short']} {v['date_short']}").upper()
    rw = max(c.tw(rt1, "r800", 12), c.tw(rt2, "rmo", 12))
    _tag(c, (v["title"] + "!").upper(), 40, 22, maxw=748 - rw - 40 - 40 - 200)
    c.text(748, 22, rt1, "r800", 12, K, align="r")
    c.text(748, 22 + c.line_h("r800", 12) + 2, rt2, "rmo", 12, B, align="r")
    hs = v["habits"][:6]
    n = len(hs)
    cols = 1 if n == 1 else 2
    rows = (n + cols - 1) // cols
    gx, gy = 24, 22 if rows < 3 else 14
    cw = (708 - gx * (cols - 1)) / cols
    ch = (370 - gy * (rows - 1)) / rows
    nr, nc = v["now"][1], v["now"][0]
    for i, h in enumerate(hs):
        x0 = 40 + (i % cols) * (cw + gx)
        y0 = 74 + (i // cols) * (ch + gy)
        col = _col(h["color"])
        _hard_box(c, (x0, y0, x0 + cw, y0 + ch), col, 9 if rows < 3 else 6, border=4)
        pad = 14 if rows < 3 else 10
        inner_h = ch - 8 - 2 * pad
        qmax = 18.0 if cols == 2 else 34.0
        q = min(qmax, (inner_h + 4) / 6 - 4)
        gap = 4 if q >= 12 else 3
        q = min(qmax, (inner_h + gap) / 6 - gap)
        f = min(q / 18, 1.5)
        gx0, gy0 = x0 + 4 + pad, y0 + 4 + pad + (inner_h - (6 * q + 5 * gap)) / 2
        for wk, week in enumerate(h["grid"][:6]):
            for wd, done in enumerate(week[:7]):
                if done is None:
                    continue
                a, b = gx0 + wd * (q + gap), gy0 + wk * (q + gap)
                bd = 4 if (wk == nc and wd == nr) else 2
                c.rect((a, b, a + q, b + q), fill=K)
                c.rect((a + bd, b + bd, a + q - bd, b + q - bd), fill=col if done else Wh)
        tx = gx0 + 7 * q + 6 * gap + 16 * max(f, .6)
        tw = x0 + cw - 4 - pad - tx
        ty0, ty1 = y0 + 4 + pad, y0 + ch - 4 - pad
        # bottom: streak number + unit, "in a row"
        big = round(46 * max(f, .55))
        unit = ctx.t("day", "Tag") if h["streak"] == 1 else ctx.t("days", "Tage")
        sub = ctx.t("in a row", "in Folge")
        sub_s = 12 if f > .7 else 10
        sub_t, sub_s = _one(c, sub, "r700", sub_s, tw, mn=8)
        sy = ty1 - c.line_h("r700", sub_s)
        c.text(tx, sy, sub_t, "r700", sub_s, K)
        num = str(h["streak"])
        big = _fs(c, num, "rmo", big, tw * .6, mn=14)
        ny = sy - 4 - big
        c.text(tx, ny, num, "rmo", big, col, lh=1, stroke=1, stroke_fill=K)
        ux = tx + c.tw(num, "rmo", big) + 6
        us = 15 if f > .7 else 12
        ut, us = _one(c, unit.upper(), "r800", us, tx + tw - ux, mn=8)
        base_off = c._baseline(ny, "rmo", big, 1) - c._baseline(0, "r800", us, None)
        c.text(ux, base_off, ut, "r800", us, K)
        # name on top
        ns = round(18 * min(max(f, 1), 1.4)) if f > .7 else 15
        nl = max(1, int((ny - 4 - ty0) // (ns * 1.12)))
        for ln in _lines(c, h["name"], "r800", ns, tw, nl):
            c.text(tx, ty0, ln, "r800", ns, K, lh=1.12)
            ty0 += ns * 1.12
    return c.finish()


# ================================================================== sudoku
def sudoku(ctx, v):
    c = _Canvas(T, Y)
    lay, ld = c.layer(84, 84)
    ld.rectangle((0, 0, 83, 83), fill=B, outline=K, width=4)
    c.paste_rotated(lay, 740, 396, -14)
    _sq(c, 600, 36, K)
    _zigzag(c, 490, 456, 7, 16, 16, R, 5)
    _tri(c, [(752, 250), (784, 306), (720, 306)], Wh)
    _hard_box(c, (40, 36, 446, 442), K, 12, fill=K, border=4)
    for r, row in enumerate(v["grid"]):
        for k, d in enumerate(row):
            x = 44 + (k // 3) * 134 + (k % 3) * 44
            y = 40 + (r // 3) * 134 + (r % 3) * 44
            c.rect((x, y, x + 42, y + 42), fill=Wh)
            if d:
                c.text(x + 21, y + (42 - 21) / 2, str(d), "rmo", 21, K, lh=1, align="c")
    X, Wd = 496, 260
    y = 74
    _, th = _tag(c, (v["name"] + "!").upper(), X, y, maxw=Wd + 20)
    y += th + 16
    lv = v["level_name"].upper()
    s = _fs(c, lv, "rmo", 38, Wd - 8, mn=16)
    _pop(c, X, y + (38 - s), lv, s, fill=Wh, shadow=K, sh=6)
    y += 38 + 8 + 6
    for i in range(v["level_max"]):
        _disc(c, X + 11 + i * 30, y + 11, 22, R if i < v["level_no"] else Wh)
    y += 22 + 16
    # givens box
    num = str(v["givens"])
    nw = c.tw(num, "rmo", 38)
    lab_w = Wd - 28 - 6 - nw - 12
    ls = _lines(c, ctx.t("digits given", "Zahlen vorgegeben"), "r800", 17, lab_w, 2)
    tw = max(c.tw(l, "r800", 17) for l in ls)
    bw = 6 + 28 + nw + 12 + tw
    bh = 6 + 16 + 38
    _hard_box(c, (X, y, X + bw, y + bh), B, 6)
    c.text(X + 17, y + 11, num, "rmo", 38, K, lh=1)
    ty = y + (bh - len(ls) * 17 * 1.1) / 2
    for ln in ls:
        c.text(X + 17 + nw + 12, ty, ln, "r800", 17, K, lh=1.1)
        ty += 17 * 1.1
    y += bh + 16
    _, bh = _kv(c, X, y, ctx.t("Today", "Heute"), v["date_long"], G, vsize=18, pad=(6, 12), sh=6, maxw=Wd)
    y += bh + 16 + 4
    for ln in _lines(c, v["hint"].upper(), "rmo", 12, 186, 3):     # keep clear of the blue square
        c.text(X, y, ln, "rmo", 12, B)
        y += c.line_h("rmo", 12)
    return c.finish()


# ================================================================== solar
def solar(ctx, v):
    c = _Canvas(T, Wh)
    _sq(c, 220, 228, B)
    _zigzag(c, 390, 232, 7, 16, 16, K, 4)
    _dots(c, 520, 180, 4, 3)
    # sun
    ox, oy = 28, 24
    for i in range(8):
        a = i * math.pi / 4
        pts = [(ox + 80 + math.cos(a + d) * rr, oy + 80 + math.sin(a + d) * rr) for d, rr in ((-.22, 52), (0, 78), (.22, 52))]
        c.poly(pts, fill=R, outline=K, width=3)
    c.circle(ox + 86, oy + 86, 46, fill=K)
    c.circle(ox + 80, oy + 80, 48, fill=K)
    c.circle(ox + 80, oy + 80, 44, fill=Y)
    # power
    X = 206
    y = 46
    _, th = _tag(c, f"{v['title']} {v['power_label']}!".upper(), X, y, maxw=380)
    y += th + 12
    s = _fs(c, v["power_text"], "rmo", 78, 370, mn=30)
    _pop(c, X, y + (78 - s), v["power_text"], s, fill=Wh, shadow=Y, sh=8, ring=4)
    # boxes
    y = 28
    boxes = [(ctx.t("Today", "Heute"), v["today_text"], G), (ctx.t("Saved", "Gespart"), f"≈ {v['saved_text']}", Y)]
    if v["total_text"]:
        boxes.append((ctx.t("Total", "Insgesamt"), v["total_text"], B))
    for lab, val, sc in boxes:
        _, bh = _kv(c, 600, y, lab, val, sc, w=160, vsize=21, pad=(5, 10))
        y += bh + 14
    # chart
    bx0, by0, bx1, by1 = 40, 262, 752, 440
    _hard_box(c, (bx0, by0, bx1, by1), K, 8)
    ix0, ix1 = bx0 + 3 + 14, bx1 - 3 - 14
    hy = by0 + 3 + 8
    t0, t1 = v["t0"], v["t1"]
    right = f"{ctx.t('Now', 'Jetzt')}  {v['now_text']}".upper()
    rw = c.tw(right, "r800", 12)
    left = ctx.t("Output today · {a}–{b} h", "Leistung heute · {a}–{b} Uhr", a=f"{t0:02d}", b=f"{t1:02d}").upper()
    left, ls = _one(c, left, "r800", 12, ix1 - ix0 - rw - 20, mn=9)
    c.text(ix0, hy, left, "r800", ls, K)
    c.text(ix1, hy, right, "r800", 12, R, align="r")
    gy = hy + c.line_h("r800", 12) + 4
    Wc = ix1 - ix0
    base = gy + 118
    peak = v["peak"] or max(v["watts"] or [1]) or 1

    def px(h):
        return ix0 + (h - t0) / (t1 - t0) * Wc

    def py(w):
        return base - max(0.0, min(w, peak)) / peak * 108

    pts = [(px(h), py(w)) for h, w in zip(v["hours"], v["watts"]) if t0 <= h <= t1]
    if len(pts) >= 2:
        poly = [(pts[0][0], base)] + pts + [(pts[-1][0], base)]
        c.poly(poly, fill=Y)
        c.stroke(poly, K, 3)
    c.hline(ix0, ix1, base - 1.5, K, 3)
    if v["now_visible"]:
        nx = px(v["now"])
        c.rect((nx - 2, gy + 4, nx + 2, base - 1), fill=R)
        if pts:
            c.circle(nx, pts[-1][1], 7, fill=K)
            c.circle(nx, pts[-1][1], 4, fill=R)
    n = len(v["ticks"])
    for i, (h, lab) in enumerate(zip(v["ticks"], v["tick_labels"])):
        al = "l" if i == 0 and h - t0 < 1 else "r" if i == n - 1 and t1 - h < 1 else "c"
        c.text(px(h), base + 6, lab, "rmo", 12, K, align=al)
    return c.finish()


# ================================================================== waterlevel
def waterlevel(ctx, v):
    c = _Canvas(T, Wh)
    _sq(c, 40, 432, B)
    _sq(c, 70, 460, B)
    _tri(c, [(300, 400), (330, 452), (270, 452)], Y)
    _zigzag(c, 200, 26, 7, 16, 16, K, 4)
    X, Wd = 40, 300
    y = 46
    tag = v["station"] + (f" · {v['water']}" if v["water"] else "") + "!"
    _, th = _tag(c, tag.upper(), X, y, maxw=Wd + 10)
    y += th + 12 + 6
    val = v["value_num"]
    s = _fs(c, val, "rmo", 104, Wd - 10, mn=36)
    _pop(c, X, y + (104 - s), val, s, fill=Wh, shadow=B, sh=8, ring=4)
    y += 104 + 12
    unit = v["unit"].upper()
    us = _fs(c, unit, "rmo", 28, 120, mn=12)
    c.text(X, y + 3 + (28 - us), unit, "rmo", us, K, lh=1)
    if v["state_text"]:
        st = v["state_text"].upper()
        bx = X + c.tw(unit, "rmo", us) + 16
        ss = _fs(c, st, "r800", 18, X + Wd - bx - 34, 2, 10)
        bw = c.tw(st, "r800", ss, 2) - 2 + 30
        bh = c.line_h("r800", ss) + 14
        bcol = {"high": R, "low": B}.get(v["state"], G)
        c.rect((bx + 4, y + 4, bx + bw + 4, y + bh + 4), fill=K)
        c.rect((bx, y, bx + bw, y + bh), fill=bcol, outline=K, width=3)
        c.text(bx + 15, y + 7, st, "r800", ss, Wh, track=2)
        y += max(bh, 34) + 12
    else:
        y += 34 + 12
    l1 = ""
    if v["trend"]:
        l1 = {"rising": "▲", "falling": "▼"}.get(v["trend"], "▶") + " " + v["trend_text"]
    l2 = f"{v['change_24h_text']} / 24 h" if v["change_24h"] is not None else ""
    if l1 or l2:
        w = max(c.tw(l1, "r800", 22), c.tw(l2, "r700", 17)) + 30
        w = min(w, Wd)
        h = 6 + 12 + (c.line_h("r800", 22) if l1 else 0) + (c.line_h("r700", 17) if l2 else 0)
        _hard_box(c, (X, y + 4, X + w, y + 4 + h), Y, 6)
        yy = y + 4 + 9
        if l1:
            t, s1 = _one(c, l1, "r800", 22, w - 30, mn=12)
            c.text(X + 15, yy, t, "r800", s1, K)
            yy += c.line_h("r800", 22)
        if l2:
            t, s2 = _one(c, l2, "r700", 17, w - 30, mn=10)
            c.text(X + 15, yy, t, "r700", s2, K)
        y += 4 + h + 6 + 6
    t, s = _one(c, v["source"], "rmo", 12, Wd, mn=8)
    c.text(X, min(y, 400), t, "rmo", s, B)
    # chart card
    _hard_box(c, (362, 36, 760, 436), K, 12, border=4)
    ix, iw = 362 + 4 + 14, 398 - 8 - 28
    hy = 36 + 4 + 10
    left = ctx.t("Last {n} days · {u}", "Letzte {n} Tage · {u}", n=v["days"], u=v["unit"]).upper()
    right = ctx.t("To HSW: {v}", "Bis HSW: {v}", v=v["to_hsw_text"]).upper() if v["to_hsw_text"] else ""
    rw = c.tw(right, "r800", 12) if right else 0
    left, ls = _one(c, left, "r800", 12, iw - rw - 14, mn=8)
    c.text(ix, hy, left, "r800", ls, K)
    if right:
        c.text(ix + iw, hy, right, "r800", 12, B, align="r")
    sy = hy + c.line_h("r800", 12) + 6
    bottom = sy + 326
    vals = v["values"]
    marks = [vals[-1]] if vals else []
    if v["mw"] is not None:
        marks.append(v["mw"])
    lo0 = min(vals + marks) if vals or marks else 0
    hi0 = max(vals + marks + ([v["hsw"]] if v["hsw"] is not None else [])) if vals or marks else 1
    rng = (hi0 - lo0) or 1
    lo, hi = lo0 - rng * .12, hi0 + rng * .02

    def yv(val):
        return bottom - (val - lo) / (hi - lo) * 290

    if v["hsw"] is not None:
        hy2 = yv(v["hsw"])
        c.hline(ix, ix + iw, hy2 - 2, R, 4)
        c.text(ix + 4, hy2 - 8 - 13, f"HSW {v['hsw']}", "rmo", 12, R)
    if len(v["x"]) >= 2:
        pts = [(ix + 3 + xx * (iw - 7), yv(val)) for xx, val in zip(v["x"], vals)]
        poly = [(ix + 3, bottom)] + pts + [(pts[-1][0], bottom)]
        c.poly(poly, fill=B)
        c.stroke(poly + [poly[0]], K, 3)
    if v["mw"] is not None:
        my = yv(v["mw"])
        c.dashed((ix, my, ix + iw, my), K, 3, 8, 6)
        lab = f"MW {v['mw']}"
        lw = c.tw(lab, "rmo", 12)
        c.rect((ix + 2, my - 8 - 16, ix + 8 + lw, my - 6), fill=Wh)
        c.text(ix + 4, my - 8 - 15, lab, "rmo", 12, K)
    if vals and len(v["x"]) >= 2:
        _disc(c, pts[-1][0] - 4, pts[-1][1], 14 + 6, Y)
    ticks = v["day_ticks"]
    for i, t in enumerate(ticks):
        end = ticks[i + 1]["x"] if i + 1 < len(ticks) else 1.0
        if (end - t["x"]) * iw < 28:
            continue
        cxl = ix + 3 + (t["x"] + end) / 2 * (iw - 7)
        c.text(cxl, bottom + 6, t["weekday"], "r800", 13, K, align="c")
    return c.finish()


# ================================================================== birthdays
def _cake(c, x, y):
    for bx, by, bw, bh, col in ((22, 12, 8, 28, B), (48, 6, 8, 34, R), (74, 12, 8, 28, G)):
        c.rect((x + bx - 1.5, y + by - 1.5, x + bx + bw + 1.5, y + by + bh + 1.5), fill=K)
        c.rect((x + bx + 1.5, y + by + 1.5, x + bx + bw - 1.5, y + by + bh - 1.5), fill=col)
    c.rect((x + 6, y + 38, x + 98, y + 72), fill=K)
    c.rect((x + 10, y + 42, x + 94, y + 68), fill=Y)
    c.rect((x + 0, y + 68, x + 104, y + 112), fill=K)
    c.rect((x + 4, y + 72, x + 100, y + 108), fill=R)
    _zig(c, [(x + 4 + i * 12, y + (90 if i % 2 == 0 else 80)) for i in range(9)], Wh, 4)


def birthdays(ctx, v):
    c = _Canvas(T, Y)
    c.circle(20, 470, 58, fill=K)
    c.circle(20, 470, 54, fill=B)
    _sq(c, 620, 22, K)
    _zigzag(c, 470, 22, 7, 16, 16, G, 4)
    f = v["first"]
    _hard_box(c, (40, 40, 440, 430), K, 14, border=4)
    _cake(c, 310, 132)
    X, Wd = 70, 340
    y = 68
    tag = (v["festive_title"] if v["festive"] else f["when"]) + "!"
    _, th = _tag(c, tag.upper(), X, y, maxw=Wd)
    y += th + 14 + 6
    name = v["festive_names"] if v["festive"] else f["name"]
    nm = name.upper()
    size, lines, L, _ = c.fit(nm, "rmo", 58, 230, 2 * 58, lh=1, min_size=20)
    lines = _lines(c, " ".join(lines), "rmo", size, 230, 2)
    if len(lines) == 1 and size < 58:      # one line: may run under the cake if it is short enough
        size = _fs(c, nm, "rmo", 58, 230)
    for ln in lines:
        c.text(X, y, ln, "rmo", size, K, lh=1)
        y += size
    y += 14
    party_y = 430 - 4 - 24 - (6 + 16 + c.line_h("r700", 12) + c.line_h("r800", 22))
    y = max(y, 132 + 112 + 6)              # the age row sits below the cake
    if f["age"] is not None and f["age_text"] and y + 72 < party_y - 6:
        num = str(f["age"])
        pre, _, post = f["age_text"].partition(num)
        if not _:
            pre, post = f["age_text"], ""
        x = X
        ry = y + (72 - c.line_h("r800", 28)) / 2
        if pre.strip():
            t, s = _one(c, pre.strip(), "r800", 28, 150, mn=14)
            c.text(x, ry, t, "r800", s, K)
            x += c.tw(t, "r800", s) + 12
        ns = _fs(c, num, "rmo", 72, X + Wd - x - 10, mn=30)
        _pop(c, x, y + (72 - ns), num, ns, fill=Y, shadow=B, sh=7, ring=4)
        x += c.tw(num, "rmo", ns) + 12
        if post.strip():
            t, s = _one(c, post.strip(), "r800", 28, max(20, X + Wd - x), mn=12)
            c.text(x, ry, t, "r800", s, K)
    lab = ctx.t("Party day", "Party-Tag")
    _kv(c, X, party_y, lab, f["date_long"], G, vsize=22, pad=(8, 14), sh=6, maxw=Wd)
    # the next ones
    y = 40
    pal = [(B, Wh), (G, Wh), (R, Wh), (Y, K)]
    for i, p in enumerate(v["others"][:4]):
        bg, ink = pal[i % 4]
        _hard_box(c, (474, y, 760, y + 82), K, 6)
        c.rect((477, y + 3, 477 + 84, y + 79), fill=bg)
        c.vline(477 + 84, y + 3, y + 79, K, 3)
        d, ds = _one(c, p["date_short"].upper(), "rmo", 13, 74, mn=8)
        c.text(477 + 42, y + (82 - c.line_h("rmo", ds)) / 2, d, "rmo", ds, ink, align="c")
        tx, tw = 477 + 87 + 12, 760 - 3 - 12 - (477 + 87 + 12)
        sub = " · ".join(t for t in (p["age_text"], p["when"]) if t)
        hh = c.line_h("r800", 24) + 2 + c.line_h("r700", 15)
        ty = y + (82 - hh) / 2
        t, s = _one(c, p["name"], "r800", 24, tw, mn=14)
        c.text(tx, ty, t, "r800", s, K)
        t, s = _one(c, sub, "r700", 15, tw, mn=10)
        c.text(tx, ty + c.line_h("r800", 24) + 2, t, "r700", s, K)
        y += 82 + 14
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    from ..plugins import _calendar as C
    from ..plugins.watchlist import spark_points
    c = _Canvas(T, Wh)
    _sq(c, 610, 462, B)
    _zigzag(c, 470, 42, 7, 16, 16, K, 4)
    date = f"{C.weekday_short(v['today'], ctx.lang)} {numeric_date(v['today'], ctx.lang)}".upper()
    dw = c.tw(date, "rmo", 12)
    c.text(748, 30, date, "rmo", 12, B, align="r")
    tw, th = _tag(c, (ctx.t("Stock market", "Börse") + "!").upper(), 40, 22, maxw=220)
    sx = 40 + tw + 18
    t, s = _one(c, v["subtitle"], "r800", 18, min(748 - dw - 20, 462) - sx, mn=11)   # clear of the zigzag
    c.text(sx, 22 + (th - c.line_h("r800", s)) / 2, t, "r800", s, K)
    items = v["items"][:6]
    n = max(1, len(items))
    gap = 12 if n <= 4 else 9
    bottom = 480 - 16 - c.line_h("r700", 12) - 8          # above the footer line
    rh = min(78.0, (bottom - 74 - gap * (n - 1)) / n)
    f = rh / 78
    y = 74
    for it in items:
        ok = it.get("ok")
        col = _col(it.get("color"), K) if ok else K
        _hard_box(c, (40, y, 752, y + rh), col, 6 if f > .8 else 4)
        x = 40 + 3 + 16
        ns, vs = round(20 * max(f, .7)), round(22 * max(f, .62))
        hh = c.line_h("r800", ns) + 2 + vs * 1.1
        ty = y + (rh - hh) / 2
        t, s = _one(c, it["label"], "r800", ns, 214, mn=10)
        c.text(x, ty, t, "r800", s, K)
        val = it["last_text"] if ok else "–"
        t, s = _one(c, val, "rmo", vs, 214, mn=9)
        c.text(x, ty + c.line_h("r800", ns) + 2, t, "rmo", s, K, lh=1.1)
        bx = 752 - 3 - 16 - 128
        bh = c.line_h("r800", 19) + 10 if f > .75 else c.line_h("r800", 15) + 8
        bs = 19 if f > .75 else 15
        if ok:
            arrow = {"up": "▲", "down": "▼"}.get(it["direction"], "▶")
            badge = f"{arrow} {it['change_text']}"
            sw_, sh_ = 284, max(20, 52 * f)
            spx, spy = x + 214 + 18, y + (rh - sh_) / 2
            pts = spark_points(it["values"], spx + 4, spy + 6 * f, 276, sh_ - 12 * f)
            if len(pts) >= 2:
                c.dashed((spx, pts[0][1], spx + sw_, pts[0][1]), K, 2, 4, 5)
                c.stroke(pts, col, 4)
                c.circle(pts[-1][0], pts[-1][1], 6, fill=K)
                c.circle(pts[-1][0], pts[-1][1], 4, fill=col)
        else:
            badge = "–"
        c.rect((bx, y + (rh - bh) / 2, bx + 128, y + (rh + bh) / 2), fill=col, outline=K, width=3)
        t, s = _one(c, badge, "r800", bs, 116, mn=10)
        c.text(bx + 64, y + (rh - c.line_h("r800", s)) / 2, t, "r800", s, Wh, align="c")
        y += rh + gap
    t, s = _one(c, v["footer"], "r700", 12, 560, mn=8)
    c.text(40, 480 - 16 - c.line_h("r700", s), t, "r700", s, K)
    return c.finish()
