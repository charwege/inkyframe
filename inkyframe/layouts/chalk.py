"""Chalkboard ("Kreide") layouts for the plugins – ports of mockups/project/Kreide-<Stem>.dc.html."""
import math

from ..designs import CHALK_BORDER, hour, lower_first, numeric_date
from ..plugins import _calendar as C
from ..studio import B, G, K, R, Y, Canvas, Wh

COL = {"green": G, "yellow": Y, "red": R, "blue": B, "black": K, "white": Wh}
STAR = "M 0 0 l 5 -13 l 5 13 l 13 0 l -10 8 l 4 13 l -12 -8 l -12 8 l 4 -13 l -10 -8 Z"


# ------------------------------------------------------------------ helpers
def _board(bg=K):
    c = Canvas("chalk", bg)
    c.path(CHALK_BORDER, stroke=Wh, width=3)
    return c


def _wbox(c, x0, y0, x1, y1, col=Wh, width=3, fill=None, wob=5):
    """Hand-drawn box like the mockups' 'M 66 38 Q 260 33 454 39 Q 458 230 453 425 …' frames."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    w = min(wob, (x1 - x0) / 12, (y1 - y0) / 12)
    d = (f"M {x0} {y0} Q {mx} {y0 - w} {x1} {y0 + w / 5} Q {x1 + w * .8} {my} {x1 - w / 5} {y1} "
         f"Q {mx} {y1 + w} {x0 + w / 5} {y1 - w / 5} Q {x0 - w * .8} {my} {x0} {y0} Z")
    c.path(d, stroke=col, width=width, fill=fill)


def _uline(c, x0, x1, y, col=Y, width=3):
    """Slightly curved chalk underline."""
    c.path(f"M {x0} {y} Q {(x0 + x1) / 2} {y - 7} {x1} {y - 1}", stroke=col, width=width)


def _star(c, x, y, col=Y, s=1.0, width=2.5):
    c.path(STAR, stroke=col, width=width, dx=x, dy=y, sx=s)


def _ellipse(c, cx, cy, rx, ry, deg, col, width=3):
    a = math.radians(deg)
    pts = [(cx + rx * math.cos(t) * math.cos(a) - ry * math.sin(t) * math.sin(a),
            cy + rx * math.cos(t) * math.sin(a) + ry * math.sin(t) * math.cos(a))
           for t in [k / 72 * 2 * math.pi for k in range(73)]]
    c.stroke(pts, col, width, cap=False)


def _ell(c, text, role, size, width, track=0.0):
    """Cut text with … to width."""
    if c.tw(text, role, size, track) <= width:
        return text
    while text and c.tw(text + "…", role, size, track) > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _line(c, x, top, text, role, size, width, fill=Wh, lh=None, min_size=12, align="l"):
    """One line shrunk (then cut) to width. Returns the size used."""
    s = size
    while s > min_size and c.tw(text, role, s) > width:
        s -= 1
    c.text(x, top, _ell(c, text, role, s, width), role, s, fill, lh=lh, align=align)
    return s


def _block(c, x, top, width, height, text, role, size, fill=Wh, lh=1.15, min_size=12, align="l", max_lines=None):
    """Wrapped text fitted into width × height. Returns the bottom y."""
    s, lines, L, _ = c.fit(text, role, size, width, height, lh=lh, min_size=min_size)
    n = max(1, int((height + 0.5) // L)) if max_lines is None else max_lines
    if len(lines) > n:
        lines = lines[:n]
        lines[-1] = _ell(c, lines[-1] + " …", role, s, width)
    c.para(x, top, width, lines, role, s, L, fill, align=align)
    return top + len(lines) * L


# ------------------------------------------------------------------ chess
def chess(ctx, v):
    from ..plugins import chess_puzzle
    c = _board()
    _wbox(c, 66, 38, 454, 425, Wh, 2.5)
    s, x0, y0 = 46, 76, 44
    dark = {"green": G, "blue": B, "red": R}.get(v.get("dark"), G)
    last = [tuple(rc) for rc in v.get("last_cells") or []]
    for r, row in enumerate(v["board"]):
        for col, p in enumerate(row):
            bg = Y if (r, col) in last else dark if (r + col) % 2 else Wh
            c.rect((x0 + col * s, y0 + r * s, x0 + (col + 1) * s, y0 + (r + 1) * s), fill=bg)
            chess_puzzle.draw_piece(c.d, p, x0 + col * s + s // 2, y0 + r * s + s // 2, s, ink=K, paper=Wh)
    if v.get("show_coords", True):
        for i, rk in enumerate(v["ranks"]):
            c.text(51, y0 + i * s, rk, "ph", 18, Wh, lh=46 / 18, align="c")
        for i, f in enumerate(v["files"]):
            c.text(x0 + i * s + 23, 428, f, "ph", 18, Wh, lh=1, align="c")
    if len(last) == 2:
        r, col = last[1]
        _ellipse(c, x0 + col * s + 23, y0 + r * s + 23, 29, 27, -10, R, 3.5)
    # right column
    _line(c, 480, 40, v["title"], "cb", 42, 270, Wh, lh=1, min_size=24)
    c.path("M 478 96 Q 600 88 744 95", stroke=Y, width=3)
    c.path("M 492 140 l 22 0 m -8 -8 l 8 8 l -8 8", stroke=Wh, width=3)
    _line(c, 524, 124, v["to_move"], "ph", 28, 230, Wh, lh=1, min_size=16)
    big = v["mate"] or (v["themes"][0] if v["themes"] else v["side"])
    num = str(v["mate_in"]) if v["mate"] and v.get("mate_in") is not None else ""
    head = big[:-len(num)] if num and big.endswith(num) else big
    if num and head != big:
        size = 64
        while size > 28 and c.tw(head + num, "cb", size) > 264:
            size -= 2
        c.text(480, 166 + (64 - size) / 2, head, "cb", size, Wh, lh=1)
        nx = 480 + c.tw(head, "cb", size) + 10
        c.text(nx, 166 + (64 - size) / 2, num, "cb", size, R, lh=1)
        cx = nx + c.tw(num, "cb", size) / 2
        _ellipse(c, cx, 202, max(24, c.tw(num, "cb", size) / 2 + 10), 38, -8, Y, 3)
    else:
        _line(c, 480, 166, big, "cb", 64, 264, Wh, lh=1, min_size=26)
    themes = " · ".join(t for t in v["themes"] if t not in (v["mate"], big))
    if themes:
        _block(c, 480, 252, 266, 42, themes, "ph", 22, Y, lh=1.0, min_size=14, max_lines=2)
    c.dashed((480, 300, 740, 300), Wh, 2, 8, 6)
    y = 316
    for t in (v["rating_text"], v["solution_text"]):
        if t:
            _line(c, 480, y, "• " + t, "ph", 24, 266, Wh, lh=1.15, min_size=15)
            y += 24 * 1.15 + 4
    _line(c, 480, 396, f"{v['hint']} :)", "ph", 22, 236, Y, min_size=13)
    _star(c, 726, 392)
    return c.finish()


# ------------------------------------------------------------------ spotify
def spotify(ctx, v):
    c = _board()
    if v.get("image") is not None:
        pic = ctx.punch(ctx.cover_fit(v["image"], 292, 296))
        c.img.paste(pic, (56, 77))
    else:      # the mockup's chalk drawing as a stand-in
        c.circle(160, 180, 64, fill=Y)
        c.path("M 70 360 L 200 210 L 330 360 Z", stroke=R, width=4)
        c.path("M 104 360 L 200 250 L 296 360", stroke=R, width=3)
        c.path("M 240 96 Q 290 92 334 98 M 240 116 Q 290 112 334 118 M 240 136 Q 290 132 334 138", stroke=B, width=5)
        c.circle(300, 300, 18, outline=G, width=4)
    _wbox(c, 52, 74, 352, 376, Wh, 3)
    label = v["label"] + (" …" if v.get("playing") else "")
    _line(c, 394, 36, label, "cb", 40, 290, Y, lh=1, min_size=22)
    c.path("M 392 82 Q 500 74 620 80", stroke=Y, width=3)
    c.path("M 700 64 l 0 -34 l 26 -6 l 0 34 M 700 40 l 26 -6", stroke=Wh, width=3)
    c.ellipse((683, 57, 701, 71), fill=Wh)
    c.ellipse((709, 51, 727, 65), fill=Wh)
    _block(c, 394, 104, 360, 44 * 1.05 * 2 + 8, v["track"], "cb", 44, Wh, lh=1.05, min_size=24)
    y = 226
    if v["artist"]:
        _line(c, 394, y, "• " + v["artist"], "ph", 26, 360, Wh, lh=1.15, min_size=16)
        y += 26 * 1.15 + 6
    if v["album"]:
        pre = "• " + ctx.t("from", "aus") + " "
        s = 26
        while s > 16 and c.tw(pre + v["album"], "ph", s) > 360:
            s -= 1
        c.text(394, y, pre, "ph", s, Wh, lh=1.15)
        x = 394 + c.tw(pre, "ph", s)
        c.text(x, y, _ell(c, v["album"], "ph", s, 754 - x), "ph", s, Y, lh=1.15)
    c.dashed((396, 346, 754, 346), Wh, 2, 8, 6)
    c.circle(396, 346, 6, fill=R)
    if v.get("duration_text"):
        c.text(754, 362, v["duration_text"], "ph", 22, Wh, lh=1, align="r")
    _line(c, 60, 398, ctx.t("turn it up!", "schön laut drehen!"), "ph", 22, 300, Y, min_size=14)
    c.text(754, 480 - 34 - c.line_h("ph", 22), v["source"], "ph", 22, Wh, align="r")
    return c.finish()


# ------------------------------------------------------------------ grid signal
def grid(ctx, v):
    c = _board()
    # traffic light
    _wbox(c, 72, 42, 150, 238, Wh, 3)
    c.path("M 111 240 L 111 268 M 92 270 L 130 270", stroke=Wh, width=3)
    on_y = None
    for (lt, cy) in zip(v["lights"], (78, 140, 202)):
        col = COL.get(lt["color"], Wh)
        if lt["on"]:
            c.circle(111, cy, 24, fill=col, outline=Wh, width=3)
            on_y = cy
        else:
            c.circle(111, cy, 22, outline=col, width=3)
    sig = COL.get(v.get("color"), Wh)
    if on_y is not None:
        c.path(f"M 152 {on_y} l 14 -6 M 152 {on_y + 8} l 16 4 M 150 {on_y - 12} l 12 -12", stroke=sig, width=3)
    title = v["title"] + (f" · {v['place']}" if v.get("place") else "")
    _line(c, 200, 36, title, "cb", 30, 300, Y, lh=1, min_size=18)
    name = v["signal_name"] or "–"
    name = name[:1].upper() + name[1:]
    s = 82
    while s > 30 and c.tw(name, "cb", s) > 300:
        s -= 2
    c.text(200, 70 + (82 - s) * 0.8, _ell(c, name, "cb", s, 300), "cb", s, Wh, lh=1)
    c.path("M 200 152 Q 330 144 460 150", stroke=sig, width=3)
    if v.get("share_text"):
        _line(c, 200, 162, ctx.t("{p} renewable power", "{p} Ökostrom", p=v["share_text"]), "ph", 30, 300, Wh,
              lh=1.1, min_size=16)
    tips = {"green": ctx.t("Now: wash, charge, run the dishwasher!", "Jetzt waschen, laden, spülen!"),
            "yellow": ctx.t("Better wait a little.", "Lieber noch etwas warten."),
            "red": ctx.t("Save power for now.", "Jetzt lieber Strom sparen.")}
    tip = tips.get(v.get("color"))
    if tip:
        _star(c, 204, 236)
        _line(c, 238, 226, tip, "ph", 30, 512, Wh, lh=1.1, min_size=16)
    # rest of today
    segs = [g for g in v.get("segments") or [] if g.get("now") or g["start"] >= v["now_pos"] * 24]
    if segs:
        c.text(520, 54, ctx.t("Rest of today:", "Heute noch:"), "cb", 26, Wh, lh=1.15)
        y = 54 + 26 * 1.15 + 4
        for g in segs[:4]:
            pre = f"• {g['from']}–{g['to']} "
            s = 22
            while s > 13 and c.tw(pre + g["name"], "ph", s) > 236:
                s -= 1
            c.text(520, y, pre, "ph", s, Wh, lh=1.15)
            x = 520 + c.tw(pre, "ph", s)
            col = COL.get(g.get("color"), Wh)
            c.text(x, y, _ell(c, g["name"], "ph", s, 756 - x), "ph", s, G if col == G else col, lh=1.15)
            y += 22 * 1.15 + 4
    # 24 h band
    X0, X1, T, Bt = 60, 740, 356, 388

    def hx(h):
        return X0 + (X1 - X0) * h / 24

    for g in v.get("segments") or []:
        c.rect((hx(g["start"]), T, hx(g["end"]), Bt), fill=COL.get(g.get("color"), K))
    for g in v.get("segments") or []:
        c.poly([(hx(g["start"]), T), (hx(g["end"]), T), (hx(g["end"]), Bt), (hx(g["start"]), Bt)], outline=Wh,
               width=2.5)
    if not v.get("segments"):
        c.poly([(X0, T), (X1, T), (X1, Bt), (X0, Bt)], outline=Wh, width=2.5)
    for h in (0, 6, 12, 18, 24):
        c.path(f"M {hx(h)} 392 L {hx(h)} 400", stroke=Wh, width=2)
    fy = 404
    c.text(44, fy, hour(0, ctx.lang), "ph", 18, Wh, lh=1)
    for h in (6, 12, 18):
        c.text(hx(h), fy, str(h), "ph", 18, Wh, lh=1, align="c")
    c.text(756, fy, hour(24, ctx.lang), "ph", 18, Wh, lh=1, align="r")
    best = v.get("best")
    if best and best.get("day") == "today":
        bx0, bx1 = hx(best["start"]), hx(min(24, best["end"]))
        c.path(f"M {bx0} {T - 4} L {bx0} {T - 10} L {bx1} {T - 10} L {bx1} {T - 4}", stroke=Y, width=2.5)
    nx = hx(v["now_pos"] * 24)
    c.dashed((nx, 332, nx, 400), Wh, 3, 6, 5)
    c.path(f"M {nx - 10} 340 L {nx} 352 L {nx + 10} 340", stroke=Wh, width=3)
    lab = f"{v['now_label']} {v['time']}"
    lw = c.tw(lab, "ph", 20)
    lx = min(max(nx, 44 + lw / 2), 756 - lw / 2)
    c.text(lx, 308, lab, "ph", 20, Wh, lh=1, align="c")
    if v.get("best_text"):
        _line(c, 60, 272, v["best_text"], "ph", 22, 680, Y, lh=1.1, min_size=14)
    _line(c, 400, 426, v["source"], "ph", 15, 640, Wh, lh=1, min_size=11, align="c")
    return c.finish()


# ------------------------------------------------------------------ word clock
def wordclock(ctx, v):
    c = _board()
    _wbox(c, 203, 40, 597, 440, Wh, 2.5)
    lit = {tuple(x) for x in v["lit"]}
    x0, y0, cw, ch = 213, 50, 34, 38
    rows = len(v["grid"])
    if rows * ch > 380:
        ch = 380 / rows
    for r, row in enumerate(v["grid"]):
        for col, letter in enumerate(row[:11]):
            cx = x0 + col * cw + cw / 2
            if (r, col) in lit:
                c.text(cx, y0 + r * ch, letter, "cb", 32, Y, lh=ch / 32, align="c")
            elif v.get("off") is not None:
                c.text(cx, y0 + r * ch, letter, "ph", 26, B, lh=ch / 26, align="c")
    for w in v["words"]:
        a = x0 + w["col"] * cw + 4
        b = x0 + (w["col"] + w["len"]) * cw - 3
        y = y0 + w["row"] * ch + ch - 3
        c.path(f"M {a} {y} Q {(a + b) / 2} {y - 3} {b} {y}", stroke=Wh, width=3)
    # date
    _line(c, 40, 40, v["weekday"], "cb", 42, 150, Wh, lh=1, min_size=20)
    c.path("M 40 96 Q 110 90 182 95", stroke=Y, width=3)
    _line(c, 40, 96, C.long_date(v["today"], ctx.lang, weekday=False), "ph", 26, 150, Wh, lh=1.1, min_size=14)
    _line(c, 40, 96 + 26 * 1.1 + 2, f"{v['year']} · {ctx.t('WK {n}', 'KW {n}', n=v['week'])}", "ph", 22, 150, Y,
          min_size=13)
    # dial (5-minute step of the grid)
    c.circle(115, 340, 58, outline=Wh, width=3)
    c.path("M 115 288 L 115 298 M 167 340 L 157 340 M 115 392 L 115 382 M 63 340 L 73 340", stroke=Wh, width=3)
    ha = math.radians((v["hour"] % 12 + v["minute"] / 60) * 30)
    ma = math.radians(v["minute"] * 6)
    c.stroke([(115, 340), (115 + 30 * math.sin(ha), 340 - 30 * math.cos(ha))], Wh, 5)
    c.stroke([(115, 340), (115 + 43 * math.sin(ma), 340 - 43 * math.cos(ma))], Y, 3)
    c.circle(115, 340, 5, fill=R)
    c.text(115, 412, v["time"], "ph", 20, Wh, align="c")
    # right column: the sentence, the moon
    _line(c, 622, 50, v["title"], "cb", 30, 134, Wh, lh=1, min_size=16)
    for i in range(4):
        cx = 642 + i * 30
        if i < v["minute"] // 15:          # quarters of the hour gone
            c.circle(cx, 104, 10, fill=Y)
        else:
            c.circle(cx, 104, 10, outline=Wh, width=3)
    _block(c, 622, 132, 134, 22 * 1.15 * 4, v["phrase_time"], "ph", 22, Wh, lh=1.15, min_size=14)
    _star(c, 742, 236, Y, 0.78, 2)
    C.draw_moon(c.d, 688, 292, 32, v["phase"], Wh, K, Wh)
    pts = [(688 + 42 * math.cos(t), 292 + 42 * math.sin(t)) for t in [k / 72 * 2 * math.pi for k in range(73)]]
    for k in range(0, 72, 2):
        c.stroke(pts[k:k + 2], Wh, 3, cap=False)
    _line(c, 688, 350, v["moon"], "cb", 30, 150, Wh, lh=1, min_size=15, align="c")
    ph = v["phase"]
    tip = ctx.t("Stargazing time!", "Sterne gucken!") if ph < 0.07 or ph > 0.93 else \
        ctx.t("Bright night!", "Helle Nacht!") if 0.43 < ph < 0.57 else ""
    if tip:
        _line(c, 688, 388, tip, "ph", 20, 150, Y, min_size=13, align="c")
    return c.finish()


# ------------------------------------------------------------------ countdown
def _tally(c, n, x0=180, y0=352, y1=402, pitch=60):
    for i in range(n):
        g, k = divmod(i, 5)
        gx = x0 + g * pitch
        if k < 4:
            x = gx + k * 11
            w = i % 3 - 1
            c.stroke([(x + w, y0 + (i % 2) * 2), (x - w, y1 - (i % 2) * 2)], Wh, 3.5)
        else:
            c.stroke([(gx - 8, y1 - 8), (gx + 42, y0 + 6)], Wh, 3.5)


def countdown(ctx, v):
    c = _board()
    _ellipse(c, 180, 186, 128, 100, -7, R, 3.5)
    _ellipse(c, 182, 184, 120, 94, -4, R, 2)
    c.path("M 346 140 Q 440 132 520 138", stroke=Y, width=3)
    _star(c, 702, 240, Y, 1.15)
    c.path("M 690 70 l 26 -34 l 26 34 Z M 682 96 l 34 -40 l 34 40 Z M 716 96 L 716 112", stroke=G, width=3)
    c.circle(716, 30, 4, fill=Y)
    state = v["state"]
    top = ctx.t("Still", "Noch") if state == "future" else ctx.t("Already", "Schon") if state == "past" else ""
    if top:
        c.text(56, 36, top, "cb", 36, Y, lh=1)
    big = v["big"]
    s = 190
    while s > 40 and c.tw(big, "cb", s) > 230:
        s -= 4
    c.text(180, 86 + (190 - s) / 2, big, "cb", s, Wh, lh=1, align="c")
    if v["small"]:
        _line(c, 346, 64, v["small"], "cb", 72, 330, Wh, lh=1, min_size=28)
    _block(c, 346, 156, 330, 36 * 1.1 * 2, v["event"], "ph", 36, Wh, lh=1.1, min_size=18)
    _line(c, 346, 250, f"{v['target_weekday']}, {v['date']}", "ph", 26, 340, Y, min_size=14)
    c.dashed((60, 312, 740, 312), Wh, 2, 8, 6)
    n = v["count"]
    if n > 0:
        if n <= 45:
            lab, k = ctx.t("Tally:", "Strichliste:"), n
        elif n <= 315:
            lab, k = ctx.t("Tally (weeks):", "Strichliste (Wochen):"), -(-n // 7)
        else:
            lab, k = ctx.t("Tally (months):", "Strichliste (Monate):"), min(45, -(-n * 12 // 365))
        _line(c, 60, 326, lab, "ph", 20, 680, Wh, min_size=12)
        _tally(c, k)
    if state == "today":
        foot = ctx.t("Today's the day :)", "Heute ist es so weit :)")
    elif state == "future" and n <= 45:
        foot = ctx.t("Wipe off one line every morning :)", "Jeden Morgen einen Strich wegwischen :)")
    else:
        foot = ""
    if foot:
        _line(c, 400, 418, foot, "ph", 22, 680, Y, min_size=13, align="c")
    return c.finish()


# ------------------------------------------------------------------ art
def art(ctx, v):
    c = _board()
    bx, by, bw, bh = 66, 65, 430, 337
    img = v["image"]
    sc = min(bw / v["width"], bh / v["height"])
    w, h = max(1, round(v["width"] * sc)), max(1, round(v["height"] * sc))
    pic = img.convert("RGB").resize((w, h))
    c.img.paste(pic, (bx + (bw - w) // 2, by + (bh - h) // 2))
    _wbox(c, 44, 44, 518, 424, Y, 4)
    _wbox(c, 62, 62, 500, 406, Wh, 2.5)
    c.path("M 44 44 L 62 62 M 518 43 L 500 61 M 517 424 L 499 406 M 45 423 L 63 405", stroke=Y, width=2.5)
    # caption column
    s, lines, L, _ = c.fit(v["title"], "cb", 36, 210, 36 * 1.05 * 2, lh=1.05, min_size=20)
    lines = lines[:2]
    c.para(552, 38, 210, lines, "cb", s, L, Wh)
    uy = 38 + len(lines) * L + 6
    c.path(f"M 552 {uy + 4} Q 650 {uy - 4} 752 {uy + 2}", stroke=Y, width=3)
    y = _block(c, 552, uy + 22, 210, 32 * 1.05 * 3, v["work"], "cb", 32, Y, lh=1.05, min_size=18)
    y += 12
    if v["artist"]:
        y = _block(c, 552, y, 210, 26 * 1.1 * 2, v["artist"], "ph", 26, Wh, lh=1.1, min_size=16) + 6
    bullets = [b for b in (v["date"], v["medium"], v["museum"]) if b]
    for b in bullets:
        if y + 24 * 1.1 > 340:
            break
        _line(c, 552, y, "• " + b, "ph", 24, 210, Wh, lh=1.1, min_size=14)
        y += 24 * 1.1 + 6
    if v.get("museum_city"):
        c.path("M 554 382 q 20 -24 60 -20", stroke=Wh, width=2.5)
        c.path("M 554 382 l 2 -12 m -2 12 l 11 -3", stroke=Wh, width=2.5)
        _line(c, 622, 352, v["museum_city"], "ph", 20, 140, Wh, lh=1.1, min_size=12)
    _line(c, 552, 412, ctx.t("New picture every day", "Bild wechselt täglich"), "ph", 18, 210, Y, min_size=12)
    return c.finish()


# ------------------------------------------------------------------ waste
def _bin(c, x, y, col, sc=1.0, w=3):
    """Chalk wheelie bin; (x, y) = top left of the mockup's 64 × 120 drawing (lid at y + 10)."""
    stripe = Wh if col == K else K
    c.path("M 0 10 L 64 10 L 64 20 L 0 20 Z M 20 10 L 23 0 L 41 0 L 44 10", fill=col, stroke=Wh, width=w,
           dx=x, dy=y, sx=sc)
    c.path("M 4 20 L 12 106 L 52 106 L 60 20 Z", fill=col, stroke=Wh, width=w, dx=x, dy=y, sx=sc)
    c.path("M 20 36 L 24 92 M 32 36 L 32 92 M 44 36 L 40 92", stroke=stripe, width=2.5 if col == K else 3,
           dx=x, dy=y, sx=sc)
    for wx in (18, 46):
        c.circle(x + wx * sc, y + 112 * sc, 7 * sc, fill=K, outline=Wh, width=max(1, round(w * sc)))


def waste(ctx, v):
    c = _board()
    soon, rows = v.get("soon"), list(v.get("rows") or [])
    if soon:
        label, names, items = soon["label"], soon["names_text"], soon["items"]
        when = f"{soon['weekday']}, {soon['date_short']}"
        if not soon["is_today"]:
            when += " – " + ctx.t("put them out tonight!", "heute Abend rausstellen!")
    else:
        d0 = rows[0]["date"]
        first = [r for r in rows if r["date"] == d0]
        rows = rows[len(first):]
        label = first[0]["in_text"]
        label = label[:1].upper() + label[1:]
        names = " + ".join(r["name"] for r in first)
        items = [{"name": r["name"], "color": r["color"]} for r in first]
        when = f"{first[0]['weekday']}, {first[0]['date_short']}"
    _line(c, 40, 36, label + ":", "cb", 38, 520, Y, lh=1, min_size=20)
    c.path("M 40 78 Q 100 72 156 77", stroke=Y, width=3)
    s, lines, L, _ = c.fit(names, "cb", 50, 530, 54, lh=1, min_size=26)
    if len(lines) > 1:
        s, lines, L, _ = c.fit(names, "cb", 30, 530, 56, lh=0.95, min_size=16)
        lines = lines[:2]
        c.para(40, 92, 530, lines, "cb", s, L, Wh)
    else:
        c.para(40, 92, 530, lines, "cb", s, L, Wh)
    _line(c, 40, 152, when, "ph", 22, 530, Wh, lh=1, min_size=13)
    for i, it in enumerate(items[:2]):
        _bin(c, 586 + i * 90, 44, COL.get(it["color"], K))
    _star(c, 750, 36)
    c.dashed((40, 196, 760, 196), Wh, 2, 8, 6)
    y = 210
    if not rows:
        _line(c, 50, 230, v["empty_text"], "ph", 26, 700, Wh, min_size=14)
    for r in rows[:4]:
        col = COL.get(r["color"], K)
        _bin(c, 52, y + 3, col, 30 / 64, 2)
        _line(c, 102, y + 13, r["date_text"], "ph", 26, 120, Wh, lh=1, min_size=14)
        ww = c.tw(r["in_text"], "ph", 26)
        c.text(750, y + 13, r["in_text"], "ph", 26, Y, lh=1, align="r")
        _line(c, 240, y + 11, r["name"], "cb", 30, 750 - ww - 18 - 240, Wh, lh=1, min_size=14)
        y += 56
    return c.finish()


# ------------------------------------------------------------------ weather warnings
def warnings(ctx, v):
    c = _board()
    col = Y if v["color"] == "yellow" else R
    c.path("M 140 44 Q 196 136 236 220 Q 140 226 46 218 Q 92 128 140 44 Z", stroke=col, width=5)
    c.path("M 140 98 L 141 168", stroke=Wh, width=8)
    c.circle(141, 194, 6, fill=Wh)
    _line(c, 270, 36, v["title"], "cb", 32, 480, Y, lh=1, min_size=18)
    ev = v["event"]
    doodle = c.tw(ev, "cb", 80) <= 320
    s = 80
    while s > 30 and c.tw(ev, "cb", s) > 490:
        s -= 2
    c.text(270, 76 + (80 - s) * 0.75, _ell(c, ev, "cb", s, 490), "cb", s, Wh, lh=1)
    if doodle:
        c.path("M 600 70 Q 660 66 700 70 q 24 2 22 -18 q -4 -18 -22 -10 M 600 96 Q 680 92 736 96 q 22 2 20 18 "
               "q -4 16 -20 8 M 620 122 L 690 122", stroke=Wh, width=3, dx=4, dy=-16)
    c.path("M 270 160 Q 400 152 560 158", stroke=R, width=3)
    c.path("M 270 168 Q 400 161 540 166", stroke=R, width=2)
    # level row
    lv = ctx.t("Level {n} of {m}", "Stufe {n} von {m}", n=v["level"], m=v["levels"])
    lw = c.tw(lv, "ph", 20)
    room = 490 - lw - 14 - (v["levels"] * 28 - 6) - 14
    s = _line(c, 270, 180, v["level_text"], "ph", 26, room, Wh, lh=1, min_size=14)
    x = 270 + min(room, c.tw(v["level_text"], "ph", s)) + 14
    for i in range(v["levels"]):
        c.rect((x, 182, x + 22, 204), fill=col if i < v["level"] else None, outline=Wh, width=2)
        x += 28
    c.text(x + 8, 183, lv, "ph", 20, Y, lh=1)
    _line(c, 270, 222, v["place_span"] or v["place"], "ph", 24, 490, Wh, lh=1, min_size=14)
    c.dashed((40, 276, 760, 276), Wh, 2, 8, 6)
    fy = 480 - 34 - c.line_h("ph", 22)
    text = v["description"] or v["headline"]
    if v.get("instruction"):
        text += "\n" + v["instruction"]
    _block(c, 56, 292, 688, fy - 6 - 292, text, "ph", 28, Wh, lh=1.3, min_size=15)
    src = v["source"]
    sw = c.tw(src, "ph", 20)
    c.text(744, fy + 1, src, "ph", 20, Wh, align="r")
    left = v["more_text"] or ctx.t("Take care out there!", "Draußen gut aufpassen!")
    _line(c, 56, fy, left, "ph", 22, 688 - sw - 24, Y, min_size=12)
    return c.finish()


# ------------------------------------------------------------------ guest wifi
def wifi(ctx, v):
    from ..plugins import wifi as W
    c = _board()
    c.rect((56, 44, 386, 374), fill=Wh)
    W.draw_modules(c.d, v["modules"], 56, 44, 330, dark=K, light=Wh, quiet=2)
    _wbox(c, 50, 40, 392, 378, Y, 3)
    _line(c, 60, 404, v["hint"], "ph", 24, 226, Wh, lh=1, min_size=13)
    c.path("M 290 418 q 50 4 80 -24", stroke=Wh, width=2.5)
    c.path("M 358 392 l 12 2 l -2 12", stroke=Wh, width=2.5)
    _line(c, 430, 40, v["title"], "cb", 54, 258, Wh, lh=1, min_size=24)
    c.path("M 430 106 Q 560 98 700 104", stroke=Y, width=3)
    c.path("M 694 64 q 26 -24 52 0 M 703 73 q 17 -15 34 0 M 712 82 q 8 -7 16 0", stroke=Wh, width=3)
    c.circle(720, 90, 4, fill=Wh)
    c.text(430, 128, v["network_label"] + ":", "ph", 22, Y, lh=1)
    _block(c, 430, 154, 320, 62, v["ssid"], "cb", 46, Wh, lh=1, min_size=20)
    if v["password"]:
        c.text(430, 226, v["password_label"] + ":", "ph", 22, Y, lh=1)
        s = _line(c, 440, 256, v["password"], "ph", 40, 290, Wh, lh=1, min_size=16)
        pw = min(290, c.tw(v["password"], "ph", s))
        _ellipse(c, 440 + pw / 2, 256 + s / 2 + 4, pw / 2 + 30, max(20, s * 0.85), -3, R, 3)
    if v["open"] or not v["security"]:
        sec = ctx.t("Open network", "Offenes Netz")
    else:
        sec = ctx.t("Encryption: {s}", "Verschlüsselung: {s}", s=v["security"])
    _line(c, 430, 334, "• " + sec, "ph", 22, 320, Wh, lh=1, min_size=13)
    foot = v["note"] or ctx.t("Nice to have you here :)", "Schön, dass du da bist :)")
    _line(c, 430, 404, foot, "ph", 22, 326, Y, min_size=13)
    return c.finish()


# ------------------------------------------------------------------ habits
HABIT_COL = {"green": G, "blue": B, "red": R, "black": Wh, "yellow": Y, "white": Wh}


def habits(ctx, v):
    c = _board()
    hs = v["habits"][:6]
    head = f"{v['weekday_short']}, {v['date_short']} · " + ctx.t("last 6 weeks", "letzte 6 Wochen")
    hw = min(c.tw(head, "ph", 22), 400)
    _line(c, 40, 30, v["title"], "cb", 48, 700 - hw - 24, Wh, lh=1, min_size=24)
    _line(c, 756, 44, head, "ph", 22, 400, Y, min_size=13, align="r")
    c.path("M 40 86 Q 160 78 290 85", stroke=Y, width=3)
    nrow = max(1, -(-len(hs) // 2))
    gap = 22
    rh = (338 - (nrow - 1) * gap) / nrow
    if len(hs) > 1:
        c.dashed((400, 112, 400, 434), Wh, 2, 8, 6)
    for k in range(1, nrow):
        y = 102 + k * (rh + gap) - gap / 2
        c.dashed((52, y, 748, y), Wh, 2, 8, 6)
    nm = 28 if nrow < 3 else 24
    p = min(20, (rh - nm - 6) / 6)
    cs = max(4, p - 4)
    best = max((h["streak"] for h in hs), default=0)
    lab = ctx.t("days in a row", "Tage am Stück")
    circled = False
    for i, h in enumerate(hs):
        x0 = 52 + (i % 2) * 370
        y0 = 102 + (i // 2) * (rh + gap)
        col = HABIT_COL.get(h["color"], Wh)
        _line(c, x0, y0, h["name"], "cb", nm, 326, Wh, lh=1, min_size=14)
        gy = y0 + nm + 6
        for w, week in enumerate(h["grid"][-6:]):
            for d, done in enumerate(week):
                if done is None:
                    continue
                bx, by = x0 + d * p, gy + w * p
                today = [w, d] == list(v["now"])
                if today:
                    c.rect((bx, by, bx + cs, by + cs), fill=col if done else None, outline=R, width=3)
                elif done:
                    c.rect((bx, by, bx + cs, by + cs), fill=col)
                else:
                    c.rect((bx, by, bx + cs, by + cs), outline=Wh, width=2)
        sx = x0 + 7 * p + 22 + 55
        ss = int(min(64, rh - nm - 30))
        top = gy + 6 * p - 4 - ss - 20
        c.text(sx, top, str(h["streak"]), "cb", ss, col, lh=1, align="c")
        _line(c, sx, top + ss, lab, "ph", 20 if nrow < 3 else 16, 326 - (sx - x0) + 55 - 4, Wh, lh=1,
              min_size=11, align="c")
        if not circled and best > 0 and h["streak"] == best:
            circled = True
            _ellipse(c, sx, top + ss / 2 + 2, max(26, c.tw(str(best), "cb", ss) / 2 + 14), ss * 0.52, -8, R, 3)
            if nrow < 3:
                _star(c, min(742, sx + 102), top - 4)
    return c.finish()


# ------------------------------------------------------------------ sudoku
def sudoku(ctx, v):
    c = _board()
    x0, y0, s = 52, 40, 44
    for i in range(1, 9):
        if i % 3:
            c.hline(x0, x0 + 9 * s, y0 + i * s - 0.75, Wh, 1)
            c.vline(x0 + i * s - 0.75, y0, y0 + 9 * s, Wh, 1)
    c.path("M 184 40 Q 186 238 183 436 M 316 40 Q 314 238 317 436 M 52 172 Q 250 174 448 171 "
           "M 52 304 Q 250 302 448 305", stroke=Wh, width=4)
    c.path("M 52 40 Q 250 36 448 40 Q 452 238 448 436 Q 250 440 52 436 Q 48 238 52 40 Z", stroke=Wh, width=4)
    for r, row in enumerate(v["grid"]):
        for col, n in enumerate(row):
            if n:
                c.text(x0 + col * s + s / 2, y0 + r * s, str(n), "ph", 30, Wh, lh=s / 30, align="c")
    _line(c, 486, 40, v["name"], "cb", 38, 264, Wh, lh=1, min_size=20)
    c.path("M 486 96 Q 600 88 730 95", stroke=Y, width=3)
    ls = _line(c, 486, 124, v["level_name"], "ph", 26, 160, Wh, lh=1, min_size=14)
    dx = max(590, 486 + c.tw(v["level_name"], "ph", ls) + 22)
    for i in range(v["level_max"]):
        if i < v["level_no"]:
            c.circle(dx + i * 26, 139, 9, fill=Y)
        else:
            c.circle(dx + i * 26, 139, 9, outline=Wh, width=3)
    y = 176
    for t in (v["givens_text"], ctx.t("Pencil ready?", "Bleistift bereit?")):
        _line(c, 486, y, "• " + t, "ph", 24, 264, Wh, lh=1.15, min_size=14)
        y += 24 * 1.15 + 4
    c.dashed((486, 270, 740, 270), Wh, 2, 8, 6)
    _block(c, 486, 290, 196, 34 * 1.05 * 2, ctx.t("Good luck!", "Viel Glück!"), "cb", 34, G, lh=1.05, min_size=18)
    c.path("M 690 330 l 40 -40 l 10 10 l -40 40 Z M 690 330 l -6 16 l 16 -6", stroke=Y, width=2.5)
    _line(c, 486, 396, f"{v['hint']} :)", "ph", 22, 270, Y, min_size=13)
    return c.finish()


# ------------------------------------------------------------------ solar
def solar(ctx, v):
    c = _board()
    _line(c, 40, 36, v["title"], "cb", 48, 250, Wh, lh=1, min_size=24)
    c.path("M 40 90 Q 140 82 250 88", stroke=Y, width=3)
    sub = v["subtitle"] + (f" · {v['place']}" if v.get("place") else "")
    _line(c, 40, 102, sub, "ph", 22, 250, Y, lh=1, min_size=13)
    y = 140
    _line(c, 40, y, f"• {lower_first(v['subtitle'])} {v['today_text']}", "ph", 24, 250, Wh, lh=1.15, min_size=14)
    y += 24 * 1.15 + 4
    tl = v.get("today_line") or ""
    saved = tl.split(" · ", 1)[1] if " · " in tl else v["saved_text"]
    c.text(40, y, "• ", "ph", 24, Wh, lh=1.15)
    _line(c, 40 + c.tw("• ", "ph", 24), y, saved, "ph", 24, 236, G, lh=1.15, min_size=14)
    y += 24 * 1.15 + 4
    if v.get("total_line"):
        _line(c, 40, y, "• " + v["total_line"], "ph", 24, 250, Wh, lh=1.15, min_size=14)
    _ellipse(c, 452, 126, 150, 80, -5, Y, 3)
    _line(c, 455, 56, v["power_label"], "ph", 22, 280, Wh, lh=1, min_size=13, align="c")
    s = 96
    while s > 40 and c.tw(v["power_text"], "cb", s) > 280:
        s -= 4
    c.text(455, 82 + (96 - s) / 2, v["power_text"], "cb", s, Wh, lh=1, align="c")
    # smiling sun
    c.circle(690, 104, 34, fill=Y)
    c.path("M 690 54 L 690 38 M 690 154 L 690 170 M 640 104 L 624 104 M 740 104 L 756 104 M 655 69 L 643 57 "
           "M 725 69 L 737 57 M 655 139 L 643 151 M 725 139 L 737 151", stroke=Y, width=3)
    c.path("M 678 98 l 0 2 M 702 98 l 0 2 M 676 114 q 14 12 28 0", stroke=K, width=3)
    # chart
    t0, t1, peak = v["t0"], v["t1"], v["peak"] or 1

    def px(h):
        return 60 + (h - t0) / (t1 - t0) * 680

    def py(w):
        return 425 - min(max(w, 0), peak) / peak * 150

    c.dashed((60, 425, 740, 425), Wh, 2, 8, 6)
    c.dashed((60, 275, 740, 275), Wh, 1, 3, 8)
    c.text(66, 282, v["peak_text"], "ph", 18, Wh, lh=1)
    pts = [(px(h), py(w)) for h, w in zip(v["hours"], v["watts"])
           if t0 <= h <= t1]
    if len(pts) >= 2:
        c.stroke(pts, Wh, 4)
    if v.get("now_visible"):
        nx = px(v["now"])
        c.dashed((nx, 280, nx, 425), R, 2, 4, 5)
        if pts:
            c.circle(pts[-1][0], pts[-1][1], 8, fill=R)
    ticks = list(v["ticks"])
    for i, t in enumerate(ticks):
        lab = hour(t, ctx.lang) if i == len(ticks) - 1 and ctx.lang == "de" else str(t)
        x = min(px(t), 756 - c.tw(lab, "ph", 18) / 2)
        c.text(x, 432, lab, "ph", 18, Wh, lh=1, align="c")
    return c.finish()


# ------------------------------------------------------------------ water level
def waterlevel(ctx, v):
    c = _board()
    _line(c, 40, 36, v["name"], "cb", 48, 320, Wh, lh=1, min_size=24)
    sub = " · ".join(x for x in (v["station"], v["water"]) if x)
    _line(c, 40, 92, sub, "ph", 26, 320, Y, lh=1, min_size=14)
    c.path("M 40 136 Q 150 128 270 134", stroke=Y, width=3)
    s = 96
    while s > 40 and c.tw(v["value_text"], "cb", s) > 320:
        s -= 4
    c.text(40, 150 + (96 - s) * 0.7, v["value_text"], "cb", s, Wh, lh=1)
    st = v["state"]
    if v["state_text"]:
        scol = R if st == "high" else Y if st == "low" else G
        ss = _line(c, 40, 252, v["state_text"], "ph", 30, 300, scol, lh=1, min_size=16)
        if st == "normal":
            ex = 40 + c.tw(v["state_text"], "ph", ss) + 10
            c.path(f"M {ex} 264 l 10 11 l 24 -28", stroke=G, width=3)
    lines = []
    if v["trend_text"]:
        lines.append(v["trend_text"])
    if v.get("change_24h_text"):
        lines.append(f"{v['change_24h_text']}/24 h")
    if lines:
        tr = v["trend"]
        if tr == "rising":
            c.path("M 48 330 l 0 -36 m -10 12 l 10 -12 l 10 12", stroke=R, width=3)
        elif tr == "falling":
            c.path("M 48 294 l 0 36 m -10 -12 l 10 12 l 10 -12", stroke=Y, width=3)
        elif tr == "steady":
            c.path("M 32 312 l 30 0 m -12 -10 l 12 10 l -12 10", stroke=Wh, width=3)
        y = 290
        for ln in lines:
            _line(c, 70, y, ln, "ph", 24, 290, Wh, lh=1.15, min_size=14)
            y += 24 * 1.15
    c.path("M 40 380 q 20 -10 40 0 q 20 10 40 0 q 20 -10 40 0 q 20 10 40 0 q 20 -10 40 0 q 20 10 40 0 "
           "q 20 -10 40 0", stroke=B, width=4)
    _line(c, 40, 480 - 32 - c.line_h("ph", 18), v["footer"], "ph", 18, 320, Wh, min_size=11)
    # chart
    _line(c, 392, 36, ctx.t("the last {n} days", "die letzten {n} Tage", n=v["days"]), "cb", 26, 350, Wh, lh=1,
          min_size=16)
    c.path("M 380 400 L 740 400", stroke=Wh, width=2.5)
    c.path("M 380 70 L 380 400", stroke=Wh, width=2.5)
    vals = v["values"]
    if vals and v["x"]:
        bottom = min([v["min"]] + ([v["mw"]] if v.get("mw") is not None else []))
        top = v["hsw"] if v.get("hsw") is not None else v["max"]
        top = max(top, v["max"])
        span = (top - bottom) or 1
        lo, hi = bottom - 0.15 * span, top + 0.01 * span

        def py(val):
            return 400 - (val - lo) / (hi - lo) * 292

        for ref in v.get("refs") or []:
            y = py(ref["value"])
            col = R if ref["key"] == "HSW" else Y
            c.dashed((380, y, 740, y), col, 2, 10, 7)
            ly = y - 28 if ref["key"] == "HSW" else y + 8
            c.text(392, ly, ref["text"], "ph", 20, col, lh=1)
        step = max(1, len(vals) // 200)
        idx = list(range(0, len(vals), step))
        if idx[-1] != len(vals) - 1:
            idx.append(len(vals) - 1)
        pts = [(384 + v["x"][i] * 346, py(vals[i])) for i in idx]
        c.stroke(pts, Wh, 4)
        c.circle(pts[-1][0], pts[-1][1], 8, fill=R)
    xs = [t["x"] for t in v.get("day_ticks") or []]
    bounds = [0.0] + xs + [1.0]
    labels = [None] + [t["weekday"] for t in v.get("day_ticks") or []]
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        lab = labels[k]
        if lab and (b - a) * 346 >= 24:
            c.text(384 + (a + b) / 2 * 346, 410, lab, "ph", 18, Wh, lh=1, align="c")
    return c.finish()


# ------------------------------------------------------------------ birthdays
def _cake(c):
    c.path("M 600 120 Q 670 114 740 120 L 740 184 Q 670 190 600 184 Z", stroke=Wh, width=3)
    c.path("M 600 140 q 12 12 23 0 q 12 12 23 0 q 12 12 23 0 q 12 12 23 0 q 12 12 23 0 q 12 12 25 0", stroke=R,
           width=3)
    c.path("M 590 190 Q 670 196 750 190", stroke=Wh, width=3)
    c.path("M 630 116 L 630 86 M 670 114 L 670 82 M 710 116 L 710 86", stroke=Wh, width=4)
    c.path("M 630 78 q -6 -8 0 -16 q 6 8 0 16 Z M 670 74 q -6 -8 0 -16 q 6 8 0 16 Z M 710 78 q -6 -8 0 -16 "
           "q 6 8 0 16 Z", fill=Y, stroke=Y, width=2)
    _star(c, 566, 70, Y, 0.78, 2)
    _star(c, 754, 64, G, 0.78, 2)


def birthdays(ctx, v):
    c = _board()
    _cake(c)
    if v.get("festive"):
        label, big, num, sub = v["festive_title"], v["festive_names"], "", v["festive_line"] or v["date_long"]
        rows = [p for p in v["people"] if p["days"] > 0][:4]
    else:
        f = v["first"]
        label = f["when"] + ":"
        num = str(f["age"]) if f.get("age") is not None and f["age_text"].endswith(str(f["age"])) else ""
        big = f"{f['name']} {f['age_text']}".strip()
        sub = f["date_long"]
        rows = v["others"][:4]
    _line(c, 44, 32, label, "cb", 34, 510, Y, lh=1, min_size=18)
    s = 72
    while s > 28 and c.tw(big, "cb", s) > 500:
        s -= 2
    big = _ell(c, big, "cb", s, 500)
    ty = 72 + (72 - s) * 0.7
    if num and big.endswith(num):
        head = big[:-len(num)]
        c.text(44, ty, head, "cb", s, Wh, lh=1)
        nx = 44 + c.tw(head, "cb", s) + 8
        c.text(nx, ty, num, "cb", s, Wh, lh=1)
        nw = c.tw(num, "cb", s)
        _ellipse(c, nx + nw / 2, ty + s * 0.55, nw / 2 + 14, s * 0.6, -8, R, 3)
    else:
        c.text(44, ty, big, "cb", s, Wh, lh=1)
    c.path("M 44 152 Q 220 144 420 150", stroke=Y, width=3)
    _line(c, 44, 170, sub, "ph", 28, 530, Wh, lh=1, min_size=15)
    c.dashed((44, 232, 756, 232), Wh, 2, 8, 6)
    y = 248
    for p in rows:
        when = p["when"]
        ww = c.tw(when, "ph", 26)
        c.text(746, y + 10, when, "ph", 26, Y, lh=1, align="r")
        _line(c, 56, y + 7, p["name"], "cb", 32, 144, Wh, lh=1, min_size=14)
        _line(c, 206, y + 10, p["date_short"], "ph", 26, 114, Wh, lh=1, min_size=14)
        if p["age_text"]:
            room = 746 - ww - 16 - 326
            at, age = p["age_text"], str(p["age"]) if p.get("age") is not None else ""
            if age and at.endswith(age) and p["age"] % 10 == 0 and c.tw(at, "ph", 26) <= room:
                pre = at[:-len(age)]
                c.text(326, y + 10, pre, "ph", 26, Wh, lh=1)
                c.text(326 + c.tw(pre, "ph", 26), y + 10, age, "ph", 26, R, lh=1)
            else:
                _line(c, 326, y + 10, at, "ph", 26, room, Wh, lh=1, min_size=13)
        y += 50
    return c.finish()


# ------------------------------------------------------------------ watchlist
def watchlist(ctx, v):
    from ..plugins import watchlist as WL
    c = _board()
    c.text(40, 32, v["title"], "cb", 48, Wh, lh=1)
    tw = c.tw(v["title"], "cb", 48)
    c.path(f"M 40 86 Q {40 + tw / 2} 80 {40 + tw} 85", stroke=Y, width=3)
    sx = 40 + tw + 30
    _line(c, sx, 50, v["subtitle"], "ph", 22, 676 - sx, Y, lh=1, min_size=12)
    c.path("M 690 70 L 712 48 L 726 60 L 752 34 M 740 34 L 752 34 L 752 46", stroke=G, width=3)
    items = v["items"][:6]
    n = max(1, len(items))
    rh = min(76, 308 / n)
    k = rh / 76
    for i, it in enumerate(items):
        top = 116 + i * rh
        mid = top + rh / 2
        if i:
            c.dashed((44, top, 756, top), Wh, 2, 8, 6)
        ns = max(16, round(32 * min(1, k * 1.15)))
        _line(c, 48, mid - ns / 2, it["label"], "cb", ns, 212, Wh, lh=1, min_size=14)
        vs = max(15, round(28 * min(1, k * 1.15)))
        if not it.get("ok"):
            c.text(406, mid - vs / 2, "–", "ph", vs, Wh, lh=1, align="r")
            continue
        col = {"green": G, "red": R}.get(it["color"], Wh)
        _line(c, 406, mid - vs / 2, it["last_text"], "ph", vs, 140, Wh, lh=1, min_size=12, align="r")
        _line(c, 532, mid - vs / 2, it["change_text"], "ph", vs - 2, 110, col, lh=1, min_size=12, align="r")
        sh = 44 * k
        pts = WL.spark_points(it["values"], 562, mid - sh / 2, 176, sh)
        if len(pts) >= 2:
            c.stroke(pts, col, 3)
            c.circle(pts[-1][0], pts[-1][1], 5, fill=col)
    fy = 480 - 30 - c.line_h("ph", 18)
    d = v["today"]
    left = f"{C.weekday_short(d, ctx.lang)}, {numeric_date(d, ctx.lang, year=False)}"
    c.text(48, fy, left, "ph", 18, Y)
    _line(c, 752, fy, v["footer"], "ph", 18, 600, Wh, min_size=11, align="r")
    return c.finish()
