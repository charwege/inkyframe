"""Pixel design – signature layouts of the plugins (ports of mockups/project/Pixel-*.dc.html).

8-bit look: dark screen, double white pixel boxes, Press Start 2P for labels, VT323 for text,
small pixel sprites (hearts, lamps, bins …) drawn block by block.
"""
import math

from ..designs import HEART, _pixel_box, _sprite, numeric_date
from ..plugins import _calendar as C
from ..studio import B, G, K, R, Y, Canvas, Wh, _adv

PS, VT = "ps2p", "vt"
COL = {"black": K, "white": Wh, "red": R, "yellow": Y, "green": G, "blue": B}
TRI = ["x...", "xx..", "xxx.", "xxxx", "xxx.", "xx..", "x..."]        # ▶ as 7 pixel rows


# ================================================================== helpers
def _w(c, text, role, size):
    """Text width, measuring glyphs the design font lacks with the fallback font."""
    if not text:
        return 0
    f = c.font(role, size)
    return sum(_adv(c.d, ch, f) for ch in text)


def _fs(c, text, role, size, width, min_size=8):
    """Largest size <= size at which text fits width."""
    while size > min_size and _w(c, text, role, size) > width:
        size -= 1
    return size


def _ell(c, text, role, size, width):
    if _w(c, text, role, size) <= width:
        return text
    while text and _w(c, text + "…", role, size) > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _line(c, x, top, text, role, size, width, fill=Wh, align="l", min_size=None, lh=1):
    """One line shrunk (down to min_size) and then ellipsised to width. Returns the size used."""
    s = _fs(c, text, role, size, width, min_size or max(8, int(size * 0.6)))
    c.text(x, top, _ell(c, text, role, s, width), role, s, fill, lh=lh, align=align)
    return s


def _wrap(c, text, role, size, width, max_lines):
    """Word wrap (also after hyphens); the last line gets an ellipsis if text is left over."""
    words = []
    for w in text.split():
        parts = w.split("-")
        for i, p in enumerate(parts):
            words.append(p + ("-" if i < len(parts) - 1 else ""))
    lines, cur = [], ""
    for w in words:
        sep = "" if cur.endswith("-") or not cur else " "
        t = cur + sep + w
        if not cur or _w(c, t, role, size) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        rest = " ".join(lines[max_lines - 1:])
        lines = lines[:max_lines - 1] + [_ell(c, rest, role, size, width)]
    return [_ell(c, l, role, size, width) for l in lines]


def _fit(c, text, role, size, width, height, lh=1.0, min_size=10):
    """(size, lines) – largest size whose wrapped lines fit width × height."""
    while True:
        L = size * lh
        n = max(1, int((height + 0.5) // L))
        words = _wrap(c, text, role, size, width, 99)
        if len(words) <= n or size <= min_size:
            return size, _wrap(c, text, role, size, width, n)
        size -= 1


def _hearts(c, x, y, n, s=2, col=R, gap=4):
    """n pixel hearts from x (left edge); returns the width."""
    w = 7 * s
    for k in range(n):
        _sprite(c, HEART, x + k * (w + gap), y, s, {"r": col if not isinstance(col, list) else col[k]})
    return n * w + (n - 1) * gap if n else 0


def _tri(c, x, y, s=3, col=Wh):
    _sprite(c, TRI, x, y, s, {"x": col})
    return 4 * s


def _rows(c, rows, x, y, s, colors):
    _sprite(c, rows, x, y, s, colors)


def _dt(ctx, today=None):
    d = today or ctx.today
    return f"{C.weekday_short(d, ctx.lang).upper()} {numeric_date(d, ctx.lang)}"


def _header(c, left, mid, right, lcol=Wh, mcol=Y, rcol=G, size=13, top=18):
    """Top line: three texts spread like CSS justify-content: space-between over 18…782."""
    texts = [t.upper() for t in (left, mid, right)]
    while size > 8 and sum(_w(c, t, PS, size) for t in texts) + 2 * 18 > 764:
        size -= 1
    ws = [_w(c, t, PS, size) for t in texts]
    room = 764 - 2 * 18 - ws[1] - ws[2]
    if ws[0] > room:                       # place names may be long: cut the left text
        texts[0] = _ell(c, texts[0], PS, size, room)
        ws[0] = _w(c, texts[0], PS, size)
    gap = (764 - sum(ws)) / 2
    c.text(18, top, texts[0], PS, size, lcol, lh=1)
    c.text(18 + ws[0] + gap, top, texts[1], PS, size, mcol, lh=1)
    c.text(782, top, texts[2], PS, size, rcol, lh=1, align="r")


def _tipbox(c, box, text, size=28, hearts=3, pad=16, hcol=R, right=None, rcol=G, rsize=12):
    """Plain 4 px box with '▶ text' and hearts (or a small label) on the right."""
    x0, y0, x1, y1 = box
    c.rect(box, outline=Wh, width=4)
    inner = y1 - y0 - 8
    rw = 0
    if right:
        rs = _fs(c, right.upper(), PS, rsize, 200)
        rw = _w(c, right.upper(), PS, rs)
        c.text(x1 - 4 - pad, y0 + 4 + (inner - rs) / 2, right.upper(), PS, rs, rcol, lh=1, align="r")
    elif hearts:
        rw = 7 * 2 * hearts + 4 * (hearts - 1)
        _hearts(c, x1 - 4 - pad - rw, y0 + 4 + (inner - 12) / 2, hearts, 2, hcol)
    tx = x0 + 4 + pad
    if text:
        tw = _tri(c, tx, y0 + 4 + (inner - 21) / 2, 3)
        avail = x1 - 4 - pad - rw - 14 - (tx + tw + 10)
        _line(c, tx + tw + 10, y0 + 4 + (inner - size) / 2, text, VT, size, avail, Wh, min_size=16)


def _strip_num(text, n):
    """'Wertung 1843' -> 'Wertung' (the label part of a translated '<label> <number>' text)."""
    return text.replace(str(n), "").replace(":", "").strip() if n is not None else text


# ================================================================== chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = Canvas("pixel", K)
    _header(c, v["place"], _dt(ctx, v["today"]), ctx.t("BOSS LEVEL", "BOSS-LEVEL"), rcol=R)
    # board box
    _pixel_box(c, (18, 45, 422, 462))
    s = 44
    bx, by = 54, 61
    dark = COL.get(v["dark"], G)
    if dark == K:
        dark = G
    hi = set(tuple(x) for x in v.get("last_cells") or [])
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            x, y = bx + col * s, by + r * s
            fill = Y if (r, col) in hi else dark if (r + col) % 2 == 1 else Wh
            c.rect((x, y, x + s, y + s), fill=fill)
            chess_puzzle.draw_piece(c.d, p, x + s // 2, y + s // 2, s, ink=K, paper=Wh)
    if v.get("show_coords", True):
        for r, lab in enumerate(v["ranks"]):
            c.text(34 + 7, by + r * s + (s - 22) / 2, lab, VT, 22, Wh, lh=1, align="c")
        for col, lab in enumerate(v["files"]):
            c.text(bx + col * s + s / 2, by + 8 * s + 4, lab, VT, 22, Wh, lh=1, align="c")
    # right column
    x0, x1 = 440, 782
    W = x1 - x0
    _line(c, x0, 45 + 2.6, v["title"].upper(), PS, 13, W, G)
    top = 45 + 18 + 14
    themes = [t for t in v.get("themes") or [] if t != v.get("mate")]
    big = v.get("mate") or (themes.pop(0) if themes else v.get("title_a", ""))
    th = " · ".join(themes)
    bh = 4 + 16 + 20 + 12 + 26 + (12 + 28 if th else 0) + 16 + 4
    _pixel_box(c, (x0, top, x1, top + bh))
    ix, iw = x0 + 4 + 18, W - 8 - 36
    y = top + 4 + 16
    c.rect((ix, y, ix + 20, y + 20), fill=K if not v["white_to_move"] else Wh, outline=Wh, width=4)
    _line(c, ix + 32, y + 3.5, v["to_move"].upper(), PS, 13, iw - 32, Wh)
    y += 20 + 12
    _line(c, ix, y, big.upper(), PS, 26, iw, R, min_size=12)
    y += 26 + 12
    if th:
        _line(c, ix, y, th, VT, 28, iw, Wh, min_size=18)
    # facts
    rows = []
    if v.get("rating") is not None:
        rows.append((_strip_num(v["rating_text"], v["rating"]), str(v["rating"])))
    sol = v.get("solution_text", "")
    if ":" in sol:
        a, b = sol.split(":", 1)
        rows.append((a.strip(), b.strip()))
    elif sol:
        rows.append(("", sol))
    if v.get("last_text"):
        rows.append((ctx.t("Last move", "Letzter Zug"), v["last_text"].replace(" – ", " → ")))
    y = top + bh + 14
    lw = max([_w(c, a.upper(), VT, 28) for a, _ in rows] + [0])
    lw = min(lw, 150)
    for i, (a, b) in enumerate(rows):
        if a:
            _line(c, x0 + 4, y, a.upper(), VT, 28, lw, Y, min_size=16)
        vx = x0 + 4 + (lw + 12 if lw else 0)
        hw = 34 if i == 1 else 0
        s2 = _line(c, vx, y, b, VT, 28, x1 - vx - hw, Wh, min_size=16)
        if i == 1:
            _hearts(c, vx + _w(c, _ell(c, b, VT, s2, x1 - vx - hw), VT, s2) + 8, y + 9, 2, 2, R, 2)
        y += 28 + 6
    _tipbox(c, (x0, 408, x1, 462), v["hint"], size=26, hearts=0, pad=14)
    return c.finish()


# ================================================================== spotify
COVER = ["bbbbbbbbbbbbbbb", "bbbbbbbbbwbbbbb", "bbwbbbbbbbbbbbb", "bbbbbbyyybbbbbb", "bbbbbyyyyybbbwb",
         "bbbbbyyyyybbbbb", "bbbbbyyyyybbbbb", "bbbbbbyyybbbbbb", "bbbbbbbbbbbbbbb", "bbbrbbbbbbbrbbb",
         "bbrrrbbbbbrrrbb", "brrrrrbbbrrrrrb", "rrrrrrrbrrrrrrr", "gggggggrggggggg", "ggwggggwggggwgg"]


def spotify(ctx, v):
    c = Canvas("pixel", K)
    _header(c, v["place"], _dt(ctx, v["today"]), ctx.t("SOUND TEST", "SOUND TEST"))
    _pixel_box(c, (18, 45, 354, 381))
    if v.get("image") is not None:
        c.img.paste(ctx.punch(ctx.cover_fit(v["image"], 300, 300)), (36, 63))
    else:
        _sprite(c, COVER, 36, 63, 20)
    x0, x1 = 372, 782
    W = x1 - x0
    lab = v["label"].upper()
    _line(c, x0, 45, "♪ " + lab, PS, 13, W, G)
    y = 45 + 13 + 12
    # track, artist, album
    rest = (12 + 32 if v.get("artist") else 0) + (12 + 26 if v.get("album") else 0)
    size, lines = _fit(c, v["track"], VT, 46, W, 330 - y - rest, lh=0.95, min_size=26)
    L = size * 0.95
    for ln in lines:
        c.text(x0, y, ln, VT, size, Wh, lh=0.95)
        y += L
    if v.get("artist"):
        y += 12
        _line(c, x0, y, v["artist"], VT, 32, W, Y, min_size=22)
        y += 32
    if v.get("album"):
        y += 12
        _line(c, x0, y, v["album"], VT, 26, W, Wh, min_size=18)
    # decorative bar (no playback position on e-ink) + controls + total length
    by = 342
    n, gap = 20, 3
    bw = (W - (n - 1) * gap) / n
    for i in range(n):
        bxx = x0 + i * (bw + gap)
        c.rect((bxx, by, bxx + bw, by + 16), outline=B, width=3)
    ry = 366
    ctr = "◀◀  ❚❚  ▶▶" if v.get("playing") else "◀◀  ▶  ▶▶"
    c.text(x0 + W / 2, ry + 6, ctr, PS, 13, Y, lh=1, align="c")
    if v.get("duration_text"):
        c.text(x1, ry, v["duration_text"], VT, 26, Wh, lh=1, align="r")
    _tipbox(c, (18, 406, 782, 462), ctx.t("Background music via Spotify", "Hintergrundmusik via Spotify"))
    return c.finish()


# ================================================================== grid (traffic light of green power)
def _lamp_rows(lights):
    on = {l["color"]: l["on"] for l in lights}
    rows = ["wwwwwww"]
    for i, (col, ch) in enumerate((("red", "r"), ("yellow", "y"), ("green", "g"))):
        if on.get(col):
            rows += [f"w.{ch*3}.w", f"w{ch*5}w", f"w{ch*5}w", f"w{ch*5}w", f"w.{ch*3}.w"]
        else:
            rows += [f"w.{ch*3}.w", f"w{ch}...{ch}w", f"w{ch}...{ch}w", f"w{ch}...{ch}w", f"w.{ch*3}.w"]
        rows.append("w.....w" if i < 2 else "wwwwwww")
    return rows


def grid(ctx, v):
    c = Canvas("pixel", K)
    scol = COL.get(v.get("color") or "", Wh)
    _header(c, v["place"], f"{C.weekday_short(v['today'], ctx.lang).upper()} {v['time']}",
            f"{ctx.t('Eco level', 'Öko-Level')} {v['share_text']}" if v.get("share") is not None else "",
            rcol=scol if scol != Wh else G)
    # lamp
    _pixel_box(c, (18, 45, 126, 221))
    _sprite(c, _lamp_rows(v["lights"]), 44, 57, 8, {"w": Wh, "r": R, "y": Y, "g": G})
    x0, x1 = 144, 782
    W = x1 - x0
    y = 45 + (176 - 173) / 2
    _line(c, x0, y, f"{v['title']} · {v['now_label']}".upper(), PS, 13, W, Y)
    y += 13 + 14
    _line(c, x0, y, (v.get("signal_name") or "–").upper(), PS, 52, W, scol, min_size=20)
    y += 52 + 14
    _line(c, x0, y, v.get("share_text") or "–", VT, 40, W, Wh)
    y += 40 + 14
    sig = v.get("signal")
    full = 0 if sig is None else max(0, sig) + 1
    hw = 3 * 14 + 2 * 4
    _line(c, x0, y, v.get("subtitle", ""), VT, 26, W - hw - 12, Wh, min_size=16)
    _hearts(c, x1 - hw, y + 7, 3, 2, [scol if k < full else B for k in range(3)])
    # 24 h band
    bx0, bx1, top, bot = 18, 782, 235, 392
    _pixel_box(c, (bx0, top, bx1, bot))
    ix0, ix1 = 42, 758
    IW = ix1 - ix0
    y = top + 4 + 14
    c.text(ix0, y + 4, ctx.t("Today", "Heute").upper(), PS, 12, B, lh=1)
    lw = _w(c, ctx.t("Today", "Heute").upper(), PS, 12)
    _line(c, ix1, y, v.get("source", ""), VT, 20, IW - lw - 20, Wh, align="r", min_size=14)
    y += 20 + 6
    nx = ix0 + IW * (v.get("now_pos") or 0)
    tx = min(max(nx, ix0 + 30), ix1 - 30)
    c.text(tx, y, v["time"], PS, 11, Wh, lh=1, align="c")
    c.text(nx, y + 11, "▼", PS, 11, R, lh=1, align="c")
    y += 22 + 6
    hb = bot - 4 - 14 - 22 - 6 - y
    gap = 2
    cw = (IW - 23 * gap) / 24
    for i, h in enumerate(v["hours"]):
        hx = ix0 + i * (cw + gap)
        col = COL.get(h.get("color") or "")
        if col:
            c.rect((hx, y, hx + cw, y + hb), fill=col)
        else:
            c.rect((hx, y, hx + cw, y + hb), outline=B, width=3)
    c.rect((nx - 2, y, nx + 2, y + hb), fill=Wh)
    y += hb + 6
    for i, lab in enumerate(("00", "06", "12", "18", "24")):
        c.text(ix0 + IW * i / 4, y, lab, VT, 22, Wh, lh=1, align="l" if i == 0 else "r" if i == 4 else "c")
    tip = v.get("best_text") or v.get("subtitle", "")
    _tipbox(c, (18, 406, 782, 462), tip, right=ctx.t("BONUS TIME", "BONUS-ZEIT") if sig == 2 else None,
            hearts=0)
    return c.finish()


# ================================================================== wordclock
def _moon_rows(phase, n=9):
    """n × n pixel moon: white ring, lit part yellow (waxing lit on the right)."""
    rows = []
    r = n / 2
    k = math.cos(2 * math.pi * phase)
    for j in range(n):
        row = ""
        for i in range(n):
            dx, dy = i + 0.5 - r, j + 0.5 - r
            d = math.hypot(dx, dy)
            if d > r - 0.2:
                row += "."
                continue
            if d > r - 1.25:
                row += "w"
                continue
            half = math.sqrt(max(0.0, (r - 1) ** 2 - dy * dy)) or 1
            nx = dx / half
            lit = nx > k if phase <= 0.5 else nx < -k
            row += "y" if lit else "."
        rows.append(row)
    return rows


def wordclock(ctx, v):
    c = Canvas("pixel", K)
    # letter grid
    bx0, bx1 = 180, 620
    _pixel_box(c, (bx0, 18, bx1, 462))
    rows, cols = v["rows"], v["cols"]
    cw = min(36, (bx1 - bx0 - 8 - 36) / cols)
    ch = min(38, (444 - 8 - 40) / rows)
    gx = bx0 + (bx1 - bx0 - cw * cols) / 2
    gy = 18 + (444 - ch * rows) / 2
    lit = set(tuple(x) for x in v["lit"])
    fs = 20
    for r, line in enumerate(v["grid"]):
        for col, letter in enumerate(line):
            c.text(gx + col * cw + cw / 2, gy + r * ch + (ch - fs) / 2, letter, PS, fs,
                   Y if (r, col) in lit else B, lh=1, align="c")
    # left column
    x0, W = 18, 144
    y = 26
    if v.get("place"):
        _line(c, x0, y, v["place"].upper(), PS, 12, W, G)
    y += 12 + 14
    _line(c, x0, y, v["weekday"].upper(), PS, 15, W, Wh)
    y += 15 + 14
    ds = numeric_date(v["today"], ctx.lang, year=False)
    s = _fs(c, ds, PS, 22, W)
    c.text(x0, y, ds, PS, s, Y, lh=1.3)
    c.text(x0, y + s * 1.3, str(v["year"]), PS, s, Y, lh=1.3)
    y += 2 * s * 1.3 + 14
    _line(c, x0, y, f"{ctx.t('WK {n}', 'KW {n}', n=v['week'])} · {ctx.t('Day {n}', 'Tag {n}', n=v['day_of_year'])}",
          VT, 26, W, Wh, min_size=16)
    # + minutes box (derived from the exact render time)
    extra = max(0, min(4, v["now"].minute - v["minute"])) if v.get("now") else 0
    bt = 462 - 107
    c.rect((x0, bt, x0 + W, 462), outline=Wh, width=4)
    _line(c, x0 + 16, bt + 16, ctx.t("+ MINUTES", "+ MINUTEN"), PS, 11, W - 32, Wh)
    for i in range(4):
        dx = x0 + 16 + i * 28
        if i < extra:
            c.rect((dx, bt + 37, dx + 20, bt + 57), fill=Y)
        else:
            c.rect((dx, bt + 37, dx + 20, bt + 57), outline=B, width=4)
    _line(c, x0 + 16, bt + 67, ctx.t("+{n} min.", "+{n} Min.", n=extra), VT, 24, W - 32, Wh)
    # right column
    x1 = 782
    _line(c, x1, 26, ctx.t("TIME LEVEL", "ZEIT-LEVEL"), PS, 12, W, B, align="r")
    c.text(x1, 26 + 12 + 14, v["time"], PS, 20, Y, lh=1, align="r")
    moon = v.get("moon", "")
    ms, mlines = _fit(c, moon, VT, 28, W, 56, lh=1, min_size=18)
    yb = 462 - len(mlines) * ms
    for i, ln in enumerate(mlines):
        c.text(x1, yb + i * ms, ln, VT, ms, Wh, lh=1, align="r")
    yb -= 10 + 11
    _line(c, x1, yb, ctx.t("Moon", "Mond").upper(), PS, 11, W, Wh, align="r")
    yb -= 10 + 72
    _sprite(c, _moon_rows(v.get("phase", 0)), x1 - 72, yb, 8, {"w": Wh, "y": Y})
    return c.finish()


# ================================================================== countdown
TREE = ["....y....", "...ggg...", "..ggggg..", "...grg...", "..ggggg..", ".ggyggrg.", "..ggggg..", ".gggrgggg",
        "ggggggggg", "....w....", "...www..."]


def countdown(ctx, v):
    import datetime as dt
    c = Canvas("pixel", K)
    _header(c, v["place"], _dt(ctx, v["today"]),
            ctx.t("WORLD {a}-{b}", "WELT {a}-{b}", a=v["week_from"], b=v["week_to"]))
    # level map (right)
    mx0, mx1 = 480, 782
    _pixel_box(c, (mx0, 45, mx1, 392))
    ix = mx0 + 4 + 16
    y = 45 + 4 + 14
    _line(c, ix, y, ctx.t("LEVEL MAP", "LEVEL-KARTE"), PS, 11, 262, B)
    y += 11 + 4 + 4
    mon = v["today"] - dt.timedelta(days=v["today"].weekday())
    for i in range(7):
        wd = C.weekday_short(mon + dt.timedelta(days=i), ctx.lang).upper().rstrip(".")[:2]
        c.text(ix + i * 38 + 17, y, wd, PS, 11, Wh, lh=1, align="c")
    y += 11 + 4
    lo, hi = min(v["today"], v["target"]), max(v["today"], v["target"])
    start = lo - dt.timedelta(days=lo.weekday())
    for k in range(49):
        d = start + dt.timedelta(days=k)
        cx, cy = ix + (k % 7) * 38, y + (k // 7) * 34
        box = (cx, cy, cx + 34, cy + 30)
        if d == v["today"]:
            c.rect(box, fill=R)
            fg = Wh
        elif d == v["target"]:
            c.rect(box, fill=Y)
            fg = K
        elif lo < d < hi:
            c.rect(box, outline=Wh, width=3)
            fg = Wh
        else:
            fg = B
        c.text(cx + 17, cy + 4, str(d.day), VT, 22, fg, lh=1, align="c")
    y += 7 * 34 + 4
    lx = ix
    for col, txt in ((R, ctx.t("Today", "Heute")), (Y, ctx.t("Goal", "Ziel"))):
        c.rect((lx, y + 6, lx + 10, y + 16), fill=col)
        s = _fs(c, txt, VT, 20, 100)
        c.text(lx + 16, y, txt, VT, s, Wh, lh=1)
        lx += 16 + _w(c, txt, VT, s) + 14
    # big number + tree (left)
    W = 444
    big = v["big"].upper()
    bs = _fs(c, big, PS, 120, W - 96, 24)
    c.text(18, 45 + (120 - bs), big, PS, bs, Y, lh=1)
    _sprite(c, TREE, 18 + _w(c, big, PS, bs) + 24, 45 + 120 - 88, 8,
            {"y": Y, "g": G, "r": R, "w": Wh})
    y = 45 + 120 + 14
    if v.get("small"):
        _line(c, 18, y, v["small"].upper(), VT, 40, W, Wh, min_size=24)
        y += 40 + 14
    goal = ctx.t("Goal: {d}", "Ziel: {d}", d=f"{v['target_weekday']}, {v['date']}")
    ev = v.get("event", "").upper()
    if ev:
        es, el = _fit(c, ev, PS, 22, W, 392 - 30 - 14 - y, lh=1.25, min_size=11)
        for i, ln in enumerate(el):
            c.text(18, y + i * es * 1.25, ln, PS, es, G, lh=1.25)
    _line(c, 18, 392 - 30, goal, VT, 30, W, Wh, min_size=18)
    n = v["count"]
    if v["state"] == "future":
        tip = ctx.t("{n} more squares to the goal. Hang in there!", "Noch {n} Felder bis zum Ziel. Durchhalten!", n=n)
    elif v["state"] == "today":
        tip = ctx.t("Goal reached!", "Ziel erreicht!")
    else:
        tip = ctx.t("{n} squares since the goal.", "{n} Felder seit dem Ziel.", n=n)
    _tipbox(c, (18, 406, 782, 462), tip)
    return c.finish()


# ================================================================== art
def art(ctx, v):
    c = Canvas("pixel", K)
    _pixel_box(c, (18, 18, 514, 462))
    sx, sy, sw, sh = 36, 40, 460, 400
    img = v.get("image")
    if img is not None:
        k = min(sw / img.width, sh / img.height)
        w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
        pic = ctx.punch(img.resize((w, h)))
        c.img.paste(pic, (sx + (sw - w) // 2, sy + (sh - h) // 2))
    x0, x1 = 532, 782
    W = x1 - x0
    ts, tl = _fit(c, v["title"].upper(), PS, 12, W, 36, lh=1.5, min_size=8)
    for i, ln in enumerate(tl):
        c.text(x0, 18 + i * ts * 1.5, ln, PS, ts, G, lh=1.5)
    y = 18 + len(tl) * ts * 1.5 + 14
    _line(c, x0, y, f"{ctx.t('Day {n}', 'Tag {n}', n=v['doy'])} · {v['date_short']}".upper(), PS, 11, W, Y)
    y += 11 + 14
    # info box
    iw = W - 8 - 32
    bot_max = 410 - 14
    fixed = []
    if v.get("artist"):
        fixed.append(("artist", 28))
    if v.get("date"):
        fixed.append(("date", 16))
    fixed.append(("museum", 24))
    for key in ("medium", "origin"):
        if v.get(key):
            fixed.append((key, 22))
    room = bot_max - y - 8 - 36 - sum(h + 10 for _, h in fixed)
    ws, wl = _fit(c, v["work"], VT, 40, iw, max(38, min(room, 3 * 38)), lh=0.95, min_size=24)
    bh = 8 + 36 + len(wl) * ws * 0.95 + sum(h + 10 for _, h in fixed)
    while fixed and y + bh > bot_max:          # drop optional rows if the box gets too tall
        k, h = fixed.pop()
        bh -= h + 10
    _pixel_box(c, (x0, y, x1, y + bh))
    ix = x0 + 4 + 16
    yy = y + 4 + 18
    for ln in wl:
        c.text(ix, yy, ln, VT, ws, Wh, lh=0.95)
        yy += ws * 0.95
    for key, h in fixed:
        yy += 10
        if key == "artist":
            _line(c, ix, yy, v["artist"], VT, 28, iw, Y, min_size=18)
        elif key == "date":
            _line(c, ix, yy, v["date"], PS, 16, iw, Wh, min_size=8)
        elif key == "museum":
            _line(c, ix, yy, v["museum"], VT, 24, iw, Wh, min_size=18)
        else:
            _line(c, ix, yy, v[key], VT, 22, iw, Wh, min_size=16)
        yy += h
    _tipbox(c, (x0, 410, x1, 462), ctx.t("Tomorrow: level {n}", "Morgen: Level {n}", n=v["doy"] + 1),
            size=24, pad=12)
    return c.finish()


# ================================================================== waste
BIN = ["...oooo...", "oooooooooo", "offffffffo", "oooooooooo", ".offffffo.", ".ofoffofo.", ".ofoffofo.",
       ".ofoffofo.", ".ofoffofo.", ".offffffo.", ".oooooooo.", ".oo....oo."]


def _bin(c, x, y, s, color):
    fill = COL.get(color, K)
    cols = {"o": Wh}
    if fill != K:
        cols["f"] = fill
    _sprite(c, BIN, x, y, s, cols)


def waste(ctx, v):
    c = Canvas("pixel", K)
    _header(c, v["place"], _dt(ctx, v["today"]), ctx.t("QUEST: BINS", "QUEST: TONNEN"))
    soon, rows = v.get("soon"), list(v.get("rows") or [])
    if soon:
        label = soon["label"]
        items, names = soon["items"], soon["names_text"]
        when = f"{soon['weekday_short']} {soon['date_short']}"
        tonight = not soon["is_today"]
    else:                                   # nothing today/tomorrow: highlight the next pickup day
        d0 = rows[0]["date"]
        first = [r for r in rows if r["date"] == d0]
        rows = rows[len(first):]
        label = first[0]["in_text"]
        items = [{"name": r["name"], "color": r["color"]} for r in first]
        names = " + ".join(r["name"] for r in first)
        when = f"{first[0]['weekday_short']} {first[0]['date_short']}"
        tonight = False
    # top box
    tx0 = 18 + 4 + 22
    nb = min(len(items), 2)
    tx = tx0 + nb * (80 + 22) + 6
    W = 782 - 4 - 22 - tx
    ns, nl = _fit(c, names, VT, 42, W, 2 * 40, lh=0.95, min_size=26)
    th = 14 + 10 + len(nl) * ns * 0.95 + (10 + 26 if tonight else 0)
    ch = max(96, th)
    bot = 45 + 4 + 18 + ch + 18 + 4
    _pixel_box(c, (18, 45, 782, bot))
    for i, it in enumerate(items[:nb]):
        _bin(c, tx0 + i * 102, 45 + 22 + (ch - 96) / 2, 8, it["color"])
    y = 45 + 22 + (ch - th) / 2
    _line(c, tx, y, f"{label} · {when}".upper(), PS, 14, W, R)
    y += 14 + 10
    for ln in nl:
        c.text(tx, y, ln, VT, ns, Wh, lh=0.95)
        y += ns * 0.95
    if tonight:
        y += 10
        _tri(c, tx, y + 3, 3, Y)
        _line(c, tx + 22, y, ctx.t("Put them out tonight!", "Heute Abend rausstellen!"), VT, 26, W - 22, Y)
    # list
    top = bot + 14
    c.rect((18, top, 782, 462), outline=Wh, width=4)
    inner_t, inner_b = top + 4 + 12, 462 - 4 - 12
    n = max(0, min(len(rows), int((inner_b - inner_t + 6) // 54)))
    if not rows:
        _line(c, 42, (inner_t + inner_b) / 2 - 16, v.get("empty_text", ""), VT, 32, 716, Wh)
    gap = (inner_b - inner_t - n * 48) / max(1, n - 1) if n > 1 else 0
    y = inner_t if n > 1 else (inner_t + inner_b - 48) / 2
    for i, it in enumerate(rows[:n]):
        x = 42
        _bin(c, x, y, 4, it["color"])
        x += 40 + 20
        _line(c, x, y + 17, f"{it['weekday_short']} {it['date_short']}".upper(), PS, 14, 150, Wh)
        x += 150 + 20
        iw = _w(c, it["in_text"], VT, 28)
        c.text(758, y + 10, it["in_text"], VT, 28, Y if i == 0 else Wh, lh=1, align="r")
        _line(c, x, y + 8, it["name"], VT, 32, 758 - iw - 20 - x, Wh, min_size=20)
        y += 48 + gap
    return c.finish()


# ================================================================== warnings
def _sign_rows():
    rows = []
    for r in range(13):
        half = r * 7 // 12
        row = ""
        for x in range(15):
            inside = 7 - half <= x <= 7 + half
            bang = x == 7 and (4 <= r <= 8 or r == 10)
            row += "y" if inside and not bang else "."
        rows.append(row)
    return rows


def warnings(ctx, v):
    c = Canvas("pixel", K)
    _header(c, v["place"], f"! {ctx.t('Warning', 'Warnung')} !",
            f"{v['weekday_short']} {v['updated']}", mcol=R, rcol=Y)
    lvl, nlv = v.get("level", 1), v.get("levels", 4)
    acc = R if lvl >= 3 else Y
    # sign + headline
    y0 = 51
    _sprite(c, _sign_rows(), 28, y0 + 5, 8, {"y": acc})
    x0, x1 = 176, 772
    W = x1 - x0
    _line(c, x0, y0, v["event"].upper(), PS, 38, W, R, min_size=14)
    _line(c, x0, y0 + 50, v["level_text"], VT, 36, W, Y, min_size=22)
    lab = ctx.t("Level {a}/{b}", "Stufe {a}/{b}", a=lvl, b=nlv).upper()
    ls = _fs(c, lab, PS, 12, W - nlv * 34 - 12)
    c.text(x0, y0 + 98 + (16 - ls) / 2, lab, PS, ls, Wh, lh=1)
    bx = x0 + _w(c, lab, PS, ls) + 12
    for i in range(nlv):
        box = (bx + i * 34, y0 + 98, bx + i * 34 + 28, y0 + 114)
        if i < lvl:
            c.rect(box, fill=acc)
        else:
            c.rect(box, outline=B, width=4)
    # text box
    top, bot = y0 + 114 + 14, 424
    _pixel_box(c, (18, top, 782, bot))
    ix, iw = 18 + 4 + 24, 764 - 8 - 48
    y = top + 4 + 18
    _line(c, ix, y, (v.get("place_span") or v["place"]).upper(), PS, 12, iw, G)
    y += 12 + 12
    body = v.get("description") or v.get("headline") or ""
    if v.get("instruction"):
        body = f"{body}\n{v['instruction']}" if body else v["instruction"]
    tail = 26
    ds, dl = _fit(c, body.replace("\n", " "), VT, 34, iw, bot - 4 - 18 - tail - 8 - y, lh=1.02, min_size=18)
    for ln in dl:
        c.text(ix, y, ln, VT, ds, Wh, lh=1.02)
        y += ds * 1.02
    yb = bot - 4 - 18 - 14
    c.text(ix + iw, yb, "▼", PS, 14, R, lh=1, align="r")
    if v.get("more_text"):
        _line(c, ix, yb - 6, v["more_text"], VT, 26, iw - 30, Y, min_size=18)
    # footer
    hw = _hearts(c, 782 - 4 * 14 - 3 * 4, 445, 4, 2, [R if k < lvl else B for k in range(4)])
    _line(c, 18, 438, v.get("footer") or v.get("source", ""), VT, 24, 764 - hw - 20, Wh, min_size=16)
    return c.finish()


# ================================================================== wifi
WIFI = [".wwwwwww.", "w.......w", "..wwwww..", ".w.....w.", "...www...", ".........", "....y...."]


def wifi(ctx, v):
    from ..plugins import wifi as wf
    c = Canvas("pixel", K)
    # QR
    qy = 18 + (444 - 397) // 2
    c.rect((18, qy, 415, qy + 397), outline=Wh, width=4)
    wf.draw_modules(c.d, v["modules"], 28, qy + 10, 377, dark=K, light=Wh, quiet=2)
    x0, x1 = 437, 782
    W = x1 - x0
    _sprite(c, WIFI, x1 - 72, 18, 8, {"w": Wh, "y": Y})
    ts, tl = _fit(c, v["title"].upper(), PS, 20, W - 72 - 12, 52, lh=1.3, min_size=10)
    for i, ln in enumerate(tl):
        c.text(x0, 18 + i * ts * 1.3, ln, PS, ts, Y, lh=1.3)
    y = 18 + max(56, len(tl) * ts * 1.3) + 14
    _line(c, x0, y, ctx.t("Player 2, join in?", "Spieler 2 beitreten?").upper(), PS, 12, W, G)
    y += 12 + 14
    fields = [(v["network_label"], v["ssid"], 44, Wh)]
    if v.get("password"):
        fields.append((v["password_label"], v["password"], 44, Y))
    sec = v.get("security") or ""
    fields.append((ctx.t("Security", "Sicherheit"),
                   sec if sec and not v.get("open") else ctx.t("Open network", "Offenes Netz"), 30, Wh))
    bh = 4 + 16 + sum(11 + 6 + h for _, _, h, _ in fields) + 14 * (len(fields) - 1) + 16 + 4
    _pixel_box(c, (x0, y, x1, y + bh))
    ix, iw = x0 + 4 + 18, W - 8 - 36
    yy = y + 4 + 16
    for i, (lab, val, h, col) in enumerate(fields):
        if i:
            yy += 14
        _line(c, ix, yy, lab.upper(), PS, 11, iw, B)
        yy += 11 + 6
        _line(c, ix, yy, val, VT, h, iw, col, min_size=20)
        yy += h
    y += bh
    if v.get("note") and y + 14 + 26 <= 408 - 10:
        _line(c, x0, y + 14, v["note"], VT, 26, W, G, min_size=18)
    _tipbox(c, (x0, 408, x1, 462), v["hint"], size=26, pad=14)
    return c.finish()


# ================================================================== habits
def habits(ctx, v):
    c = Canvas("pixel", K)
    _header(c, v["title"], _dt(ctx, v["today"]), ctx.t("{n} weeks", "{n} Wochen", n=v["weeks"]))
    hs = v["habits"][:6]
    n = len(hs)
    cols = n if n <= 3 else (2 if n == 4 else 3)
    nrows = 1 if n <= 3 else 2
    gap = 14
    bw = (764 - (cols - 1) * gap) / cols
    bh = (417 - (nrows - 1) * gap) / nrows
    big = cols <= 2
    nowc, nowr = v["now"]
    for k, h in enumerate(hs):
        bx = 18 + (k % cols) * (bw + gap)
        by = 45 + (k // cols) * (bh + gap)
        _pixel_box(c, (bx, by, bx + bw, by + bh))
        col = COL.get(h["color"], Wh)
        if col == K:
            col = Wh
        px = 18 if big else 14
        ix0, ix1 = bx + 4 + px, bx + bw - 4 - px
        cell, cg = 16, 4
        gw = 7 * cell + 6 * cg
        gh = 6 * cell + 5 * cg
        cs = 34 if big else 24
        ch = 28 + 10 + max(gh, 11 + 8 + cs + 8 + 24)
        y = by + (bh - ch) / 2
        # name + tag
        if h["streak"] > 0 and h["streak"] >= h.get("best", 0):
            tag, tc = ctx.t("HIGHSCORE!", "HIGHSCORE!"), R
        elif h.get("done_today"):
            tag, tc = "+1", G
        else:
            tag, tc = "", G
        tw = 0
        if tag:
            ts = _fs(c, tag, PS, 11, (ix1 - ix0) / 2)
            tw = _w(c, tag, PS, ts)
            c.text(ix1, y + 12, tag, PS, ts, tc, lh=1, align="r")
        _line(c, ix0, y, h["name"], VT, 28, ix1 - ix0 - tw - (10 if tw else 0), Wh, min_size=18)
        y += 28 + 10
        # weeks as rows, Monday…Sunday as columns
        for w, week in enumerate(h["grid"][-6:]):
            for d, done in enumerate(week):
                if done is None:
                    continue
                x, yy = ix0 + d * (cell + cg), y + w * (cell + cg)
                border = R if (w, d) == (nowc, nowr) else col
                if done:
                    c.rect((x, yy, x + cell, yy + cell), fill=col)
                    if border != col:
                        c.rect((x, yy, x + cell, yy + cell), outline=border, width=3)
                else:
                    c.rect((x, yy, x + cell, yy + cell), outline=border, width=3)
        # combo
        cx = ix0 + gw + (22 if big else 12)
        cw = ix1 - cx
        sy = y + gh - (11 + 8 + cs + 8 + 24)
        _line(c, cx, sy, ctx.t("COMBO", "COMBO"), PS, 11, cw, Wh)
        sy += 11 + 8
        _line(c, cx, sy, f"×{h['streak']}", PS, cs, cw, col, min_size=10)
        sy += cs + 8
        _line(c, cx, sy, h["streak_text"], VT, 24, cw, Wh, min_size=14)
    return c.finish()


# ================================================================== sudoku
QBLOCK = ["yyyyyyyyyyyy", "ykyyyyyyyyky", "yyyykkkkyyyy", "yyykkyykkyyy", "yyykkyykkyyy", "yyyyyyykkyyy",
          "yyyyyykkyyyy", "yyyyykkyyyyy", "yyyyykkyyyyy", "yyyyyyyyyyyy", "ykyyykkyyyky", "yyyyyyyyyyyy"]


def sudoku(ctx, v):
    c = Canvas("pixel", K)
    gx, gy = 18, 18 + (444 - 418) // 2
    c.rect((gx, gy, gx + 418, gy + 418), fill=Wh)
    for r in range(9):
        for col in range(9):
            x = gx + 4 + (col // 3) * 138 + (col % 3) * 45
            y = gy + 4 + (r // 3) * 138 + (r % 3) * 45
            c.rect((x, y, x + 44, y + 44), fill=K)
            n = v["grid"][r][col]
            if n:
                c.text(x + 22 + 1, y + 12, str(n), PS, 20, Wh, lh=1, align="c")
    x0, x1 = 458, 782
    W = x1 - x0
    _sprite(c, QBLOCK, x1 - 96, 18, 8, {"y": Y, "k": K})
    tw = W - 96 - 10
    t1, t2 = v["title"].upper(), v["subtitle"].upper()
    ts = min(_fs(c, t1, PS, 13, tw), _fs(c, t2, PS, 13, tw))
    c.text(x0, 18, _ell(c, t1, PS, ts, tw), PS, ts, G, lh=1.5)
    c.text(x0, 18 + ts * 1.5, _ell(c, t2, PS, ts, tw), PS, ts, G, lh=1.5)
    y = 18 + 2 * ts * 1.5 + 10
    _line(c, x0, y, _dt(ctx, v["today"]), PS, 11, tw, Y)
    y = max(y + 11, 18 + 96) + 16
    bh = 4 + 18 + 11 + 12 + 36 + 12 + 28 + 12 + 28 + 18 + 4
    _pixel_box(c, (x0, y, x1, y + bh))
    ix, iw = x0 + 4 + 18, W - 8 - 36
    yy = y + 4 + 18
    _line(c, ix, yy, ctx.t("Difficulty", "Stufe").upper(), PS, 11, iw, B)
    yy += 11 + 12
    for i in range(v.get("level_max", 3)):
        bx = ix + i * 26
        if i < v["level_no"]:
            c.rect((bx, yy + 8, bx + 20, yy + 28), fill=Y)
        else:
            c.rect((bx, yy + 8, bx + 20, yy + 28), outline=B, width=4)
    lx = ix + v.get("level_max", 3) * 26 - 6 + 14
    _line(c, lx, yy, v["level_name"], VT, 36, ix + iw - lx, Wh, min_size=20)
    yy += 36 + 12
    _line(c, ix, yy, v["givens_text"], VT, 28, iw, Wh, min_size=18)
    yy += 28 + 12
    _line(c, ix, yy, ctx.t("{n} cells free", "{n} Felder frei", n=v["empty"]), VT, 28, iw, Wh, min_size=18)
    _tipbox(c, (x0, 408, x1, 462), v["hint"], size=26, pad=14)
    return c.finish()


# ================================================================== solar
def _sun_rows():
    rows = []
    for y in range(13):
        row = ""
        for x in range(13):
            dx, dy = x - 6, y - 6
            d = math.hypot(dx, dy)
            ray = (dx == 0 or dy == 0 or dx == dy or dx == -dy) and 4.9 <= d <= 6.5
            row += "y" if d <= 3.6 or ray else "."
        rows.append(row)
    return rows


def solar(ctx, v):
    c = Canvas("pixel", K)
    _header(c, v["place"], v["title"], ctx.t("POWER-UP", "POWER-UP"))
    # now
    _sprite(c, _sun_rows(), 24, 45 + 11, 8, {"y": Y})
    tx = 24 + 104 + 26
    bx0 = 492
    tw = bx0 - 18 - tx
    _line(c, tx, 45 + 26, f"{ctx.t('now', 'jetzt')} · {v['now_text']}".upper(), PS, 12, tw, Wh)
    _line(c, tx, 45 + 26 + 12 + 12, v["power_text"], PS, 50, tw, Y, min_size=20)
    # today box
    _pixel_box(c, (bx0, 45, 782, 171))
    ix, iw = bx0 + 4 + 18, 290 - 8 - 36
    y = 45 + 4 + 14
    lab = ctx.t("Today", "Heute").upper() + " "
    ls = _fs(c, lab, PS, 11, iw / 2)
    c.text(ix, y + 10, lab, PS, ls, B, lh=1)
    lw = _w(c, lab, PS, ls) + 6
    _line(c, ix + lw, y, v["today_text"], VT, 26, iw - lw, Wh, min_size=16)
    y += 26 + 6
    c.rect((ix, y + 6, ix + 16, y + 22), fill=Y)
    _line(c, ix + 26, y, ctx.t("≈ {e} saved", "≈ {e} gespart", e=v["saved_text"]), VT, 26, iw - 26, Wh, min_size=16)
    y += 26 + 6
    if v.get("total_line"):
        _line(c, ix, y, v["total_line"], VT, 26, iw, G, min_size=16)
    # chart
    top, bot = 185, 462
    _pixel_box(c, (18, top, 782, bot))
    ix0, ix1 = 42, 758
    IW = ix1 - ix0
    y = top + 4 + 14
    t0, t1 = v["t0"], v["t1"]
    peak = v.get("peak") or max(v.get("watts") or [1]) or 1
    step = next((s for s in (10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000, 20000, 50000)
                 if peak / s <= 10), 100000)
    lab = ctx.t("Output today", "Leistung heute").upper()
    ls = _fs(c, lab, PS, 12, IW / 2 - 10)
    c.text(ix0, y + 6, lab, PS, ls, B, lh=1)
    leg = ctx.t("now · one block = {w} W", "jetzt · ein Block = {w} W", w=ctx.num(step, 0))
    lw = IW - _w(c, lab, PS, ls) - 20
    s = _fs(c, leg, VT, 22, lw - 18, 14)
    legw = _w(c, _ell(c, leg, VT, s, lw - 18), VT, s)
    c.text(ix1, y, _ell(c, leg, VT, s, lw - 18), VT, s, Wh, lh=1, align="r")
    c.rect((ix1 - legw - 18, y + 6, ix1 - legw - 8, y + 16), fill=R)
    y += 22 + 6
    base = bot - 4 - 14 - 22 - 6 - 4         # top of the 4 px base line
    c.rect((ix0, base, ix1, base + 4), fill=Wh)
    nb = max(1, int((base - 3 - y + 3) // 17))
    slots = int((t1 - t0) * 2)
    gap = 3
    cw = (IW - (slots - 1) * gap) / slots
    hours, watts = v.get("hours") or [], v.get("watts") or []
    nowslot = int((v["now"] - t0) * 2) if v.get("now_visible") else -1
    for i in range(slots):
        a, b = t0 + i / 2, t0 + (i + 1) / 2
        vals = [min(w, peak) for h, w in zip(hours, watts) if a <= h < b]
        if not vals:
            continue
        w = max(vals)
        k = min(nb, max(1, round(w / step))) if w > 0 else 0
        col = R if i == nowslot else Y
        x = ix0 + i * (cw + gap)
        for j in range(k):
            yb = base - 3 - j * 17
            c.rect((x, yb - 14, x + cw, yb), fill=col)
    for tick, lab in zip(v["ticks"], v["tick_labels"]):
        x = ix0 + (tick - t0) / (t1 - t0) * IW
        c.text(x, base + 4 + 6, lab, VT, 22, Wh, lh=1, align="c")
    return c.finish()


# ================================================================== waterlevel
DUCK = ["....ww......", "...wwwr.....", "....ww......", ".wwwwwwww...", "wwwwwwwww...", ".bbbbbbbbbb.",
        "bbbbbbbbbbbb"]


def waterlevel(ctx, v):
    c = Canvas("pixel", K)
    head = f"{v['station']} · {v['water']}" if v.get("water") else v["station"]
    _header(c, head, _dt(ctx, v["today"]), ctx.t("Water level", "Wasser-Level"), rcol=B)
    # footer
    c.rect((18, 414, 782, 462), outline=Wh, width=4)
    hw = _hearts(c, 782 - 4 - 16 - 50, 432, 3, 2, R)
    _line(c, 18 + 4 + 16, 426, v.get("footer") or v.get("source", ""), VT, 24, 764 - 8 - 32 - 50 - 16, Wh,
          min_size=16)
    # left column
    x0, W = 18, 232
    y = 45
    _line(c, x0, y, v["name"].upper(), PS, 12, W, Wh)
    y += 12 + 14
    unit = v.get("unit", "")
    num = v.get("value_num", "–")
    uw = _w(c, unit, VT, 34) + 8 if unit else 0
    ns = _fs(c, num, PS, 54, W - uw, 20)
    c.text(x0, y + (54 - ns), num, PS, ns, Y, lh=1)
    if unit:
        c.text(x0 + _w(c, num, PS, ns) + 8, y + 54 - 34 + 2, unit, VT, 34, Wh, lh=1)
    y += 54 + 14
    if v.get("state_text"):
        scol = R if v.get("high") else Y if v.get("state") == "low" else G
        st = v["state_text"].upper()
        ss = _fs(c, st, PS, 16, W - 32)
        sw = _w(c, st, PS, ss)
        c.rect((x0, y, x0 + sw + 32, y + 40), outline=scol, width=4)
        c.text(x0 + 16, y + 12 + (16 - ss) / 2, st, PS, ss, scol, lh=1)
        y += 40 + 14
    if v.get("trend"):
        arrow = {"rising": "▲", "falling": "▼"}.get(v["trend"], "▶")
        acol = {"rising": R, "falling": G}.get(v["trend"], Wh)
        c.text(x0, y + 8, arrow, PS, 14, acol, lh=1)
        _line(c, x0 + 22, y, v.get("trend_text", ""), VT, 30, W - 22, Wh, min_size=18)
        y += 30 + 4
    if v.get("change_24h_text"):
        _line(c, x0, y, f"{v['change_24h_text']}/24 h", VT, 30, W, Wh, min_size=18)
    _sprite(c, DUCK, x0, 400 - 56, 8, {"w": Y, "r": R, "b": B})
    # chart box
    bx0, bx1, top, bot = 268, 782, 45, 400
    _pixel_box(c, (bx0, top, bx1, bot))
    ix0, ix1 = bx0 + 4 + 18, bx1 - 4 - 18
    IW = ix1 - ix0
    y = top + 4 + 14
    _line(c, ix0, y, ctx.t("Last {n} days", "Letzte {n} Tage", n=v.get("days", 7)).upper(), PS, 12, IW, B)
    cy0 = y + 12 + 6
    cy1 = bot - 4 - 14 - 22 - 6
    CH = cy1 - cy0
    vals, xs = v.get("values") or [], v.get("x") or []
    if len(vals) >= 2 and len(xs) == len(vals):
        mw, hsw = v.get("mw"), v.get("hsw")
        lo = min(vals + ([mw] if mw is not None else []))
        hi = max(vals + ([hsw] if hsw is not None else []))
        span = (hi - lo) or 1
        lo -= span * 0.15
        hi += span * 0.06
        Y_ = lambda val: cy0 + round((CH - (val - lo) / (hi - lo) * CH) / 4) * 4   # noqa: E731
        nbin = max(2, v.get("days", 7) * 4)
        bins = [[] for _ in range(nbin)]
        for xv, val in zip(xs, vals):
            bins[min(nbin - 1, int(xv * nbin))].append(val)
        pts, last = [], None
        for i, b in enumerate(bins):
            val = sum(b) / len(b) if b else last
            if val is None:
                continue
            last = val
            xa, xb = ix0 + round(i * IW / nbin), ix0 + round((i + 1) * IW / nbin)
            pts += [(xa, Y_(val)), (xb, Y_(val))]
        if pts:
            c.poly([(pts[0][0], cy1)] + pts + [(pts[-1][0], cy1)], fill=B)
            c.d.line(pts, fill=Wh, width=4)
        refs = {r["key"]: r for r in v.get("refs") or []}
        if hsw is not None:
            yy = Y_(hsw)
            c.rect((ix0, yy - 2, ix1, yy + 2), fill=R)
            c.text(ix0 + 6, yy + 4, refs.get("HSW", {}).get("text", f"HSW {hsw}"), VT, 24, R, lh=1)
        if mw is not None:
            yy = Y_(mw)
            for xx in range(ix0, ix1, 16):
                c.rect((xx, yy - 2, min(xx + 8, ix1), yy + 2), fill=Y)
            c.text(ix0 + 6, yy - 6 - 24, refs.get("MW", {}).get("text", f"MW {mw}"), VT, 24, Y, lh=1)
    ticks = v.get("day_ticks") or []
    edges = [t["x"] for t in ticks] + [1.0]
    for i, t in enumerate(ticks):
        mid = (edges[i] + edges[i + 1]) / 2
        if edges[i + 1] - edges[i] < 0.06:
            continue
        c.text(ix0 + mid * IW, cy1 + 6, t["weekday"], VT, 22, Wh, lh=1, align="c")
    return c.finish()


# ================================================================== birthdays
CAKE = [".y...y...y.", ".r...r...r.", ".r...r...r.", "wwwwwwwwwww", "wwrwwwrwwrw", "rrrrrrrrrrr", "rrrrrrrrrrr",
        "wwwwwwwwwww", "rrrrrrrrrrr", "rrrrrrrrrrr", "bbbbbbbbbbb"]


def birthdays(ctx, v):
    c = Canvas("pixel", K)
    _header(c, v["title"], _dt(ctx, v["today"]), ctx.t("LEVEL UP!", "LEVEL UP!"))
    f = v["first"]
    if v.get("festive"):
        when = v["festive_title"]
        big = v["festive_names"] or f["name"]
        sub = v.get("festive_line") or f["date_long"]
        others = [p for p in v["people"] if p["days"] > 0][:4]
    else:
        when = f["when"]
        big = f"{f['name']} {f['age_text']}".strip()
        sub = f["date_long"]
        others = v["others"][:4]
    # top box
    top, bot = 45, 201
    _pixel_box(c, (18, top, 782, bot))
    _sprite(c, CAKE, 18 + 4 + 26, top + (156 - 88) / 2, 8, {"y": Y, "r": R, "w": Wh, "b": B})
    tx = 18 + 4 + 26 + 88 + 30
    age = f.get("age")
    lvw = 0
    if age is not None and not (v.get("festive") and len(v.get("celebrants") or []) > 1):
        l1 = ctx.t("LVL {n}", "LVL {n}", n=age - 1)
        l2 = "▶ " + ctx.t("LVL {n}", "LVL {n}", n=age)
        lvw = max(_w(c, l1, PS, 12), _w(c, l2, PS, 12))
        c.text(782 - 4 - 26, bot - 4 - 18 - 12 * 1.6 * 2, l1, PS, 12, Wh, lh=1.6, align="r")
        c.text(782 - 4 - 26, bot - 4 - 18 - 12 * 1.6, l2, PS, 12, G, lh=1.6, align="r")
    W = 782 - 4 - 26 - (lvw + 30 if lvw else 0) - tx
    y = top + (156 - 112) / 2
    _line(c, tx, y, when.upper(), PS, 14, W, R)
    y += 14 + 8
    _line(c, tx, y, big, VT, 54, W, Wh, min_size=28)
    y += 54 + 8
    _line(c, tx, y, sub, VT, 28, W, Y, min_size=18)
    # list
    top = bot + 14
    c.rect((18, top, 782, 462), outline=Wh, width=4)
    ix0, ix1 = 18 + 4 + 24, 782 - 4 - 24
    colx = [ix0, ix0 + 50, ix1 - 430, ix1 - 300, ix1]       # #, name, date, level, (right) to go
    y0, y1 = top + 4 + 14, 462 - 4 - 14
    hdr = ["#", ctx.t("Name", "Name"), ctx.t("Date", "Datum"), ctx.t("Level", "Level"), ctx.t("To go", "Noch")]
    n = len(others)
    rows_h = 11 + n * 32
    gap = (y1 - y0 - rows_h) / max(1, n) if n else 0
    for i, h in enumerate(hdr):
        width = (colx[i + 1] - colx[i] - 10) if i < 3 else 120 if i == 3 else 160
        s = _fs(c, h.upper(), PS, 11, width)
        if i == 4:
            c.text(ix1, y0, _ell(c, h.upper(), PS, s, width), PS, s, B, lh=1, align="r")
        else:
            c.text(colx[i], y0, _ell(c, h.upper(), PS, s, width), PS, s, B, lh=1)
    y = y0 + 11 + gap
    for k, p in enumerate(others):
        c.text(colx[0], y + 12, f"{k + 2}.", PS, 13, Y, lh=1)
        _line(c, colx[1], y, p["name"], VT, 32, colx[2] - colx[1] - 10, Wh, min_size=20)
        _line(c, colx[2], y, p["date_short"], VT, 32, 120, Wh, min_size=20)
        _line(c, colx[3], y, p["age_text"] or ctx.t("LVL {n}", "LVL {n}", n="?"), VT, 32, 130, Wh, min_size=18)
        _line(c, ix1, y, p["when"], VT, 32, 160, Wh, align="r", min_size=18)
        y += 32 + gap
    return c.finish()


# ================================================================== watchlist
def watchlist(ctx, v):
    c = Canvas("pixel", K)
    parts = v.get("subtitle", "").split(" · ")
    mid, right = (parts[0], parts[-1]) if len(parts) >= 3 else (v.get("subtitle", ""), "")
    _header(c, v["title"], mid, right, rcol=B)
    items = v["items"][:6]
    top, bot = 45, 424
    _pixel_box(c, (18, top, 782, bot))
    ix0, ix1 = 18 + 4 + 22, 782 - 4 - 22
    y0, y1 = top + 4 + 12, bot - 4 - 12
    n = max(1, len(items))
    rh = (y1 - y0) / n
    cols = [ix0, ix0 + 196 + 14, ix1 - 128 - 14 - 176, ix1 - 128]     # name, chart, price, change
    up = down = 0
    for k, it in enumerate(items):
        ry = y0 + k * rh
        if k < len(items) - 1:
            c.rect((ix0, ry + rh - 2, ix1, ry + rh + 2), fill=B)
        ok = it.get("ok")
        col = COL.get(it.get("color", "black"), Wh) if ok else R
        if col == K:
            col = Wh
        big = rh >= 70
        ns = 30 if big else max(20, min(30, int(rh - 26)))
        block = (11 + 6 if big else 0) + ns
        cy = ry + (rh - block) / 2
        if ok and big:
            d = it.get("direction")
            tag = ctx.t("BONUS", "BONUS") if d == "up" else ctx.t("DAMAGE", "SCHADEN") if d == "down" else ""
            if tag:
                _line(c, cols[0], cy, tag, PS, 11, 196, col)
            cy += 17
        _line(c, cols[0], cy, it["label"], VT, ns, 196, Wh, min_size=16)
        mid_y = ry + rh / 2
        if ok:
            if it.get("direction") == "up":
                up += 1
            elif it.get("direction") == "down":
                down += 1
            ch = min(50, rh - 16)
            from ..plugins import watchlist as wl
            pts = wl.spark_points(it["values"], cols[1], mid_y - ch / 2, cols[2] - 14 - cols[1], ch)
            if len(pts) > 1:
                c.d.line(pts, fill=col, width=4)
            _line(c, cols[2] + 176, mid_y - 8.5, it["last_text"], PS, 17, 176, Wh, align="r", min_size=9)
            arrow = "▲ " if it.get("direction") == "up" else "▼ " if it.get("direction") == "down" else ""
            _line(c, ix1, mid_y - 6.5, arrow + it["change_text"], PS, 13, 128, col, align="r", min_size=8)
        else:
            if it.get("error"):
                _line(c, cols[1], mid_y - 11, it["error"], VT, 22, cols[2] + 176 - cols[1], R, min_size=14)
            c.text(ix1, mid_y - 13, "–", VT, 26, Wh, lh=1, align="r")
    score = f"{up} ▲ · {down} ▼"
    sw = _w(c, score, PS, 12)
    c.text(782, 438 + 6, score, PS, 12, G, lh=1, align="r")
    _line(c, 18, 438, v.get("footer", ""), VT, 24, 764 - sw - 20, Wh, min_size=16)
    return c.finish()
