"""Lichess puzzle of the day. Needs `pip install chess` (python-chess) to replay the game."""
import re

from inkyframe import gfx
from inkyframe.gfx import BLACK, BLUE, GREEN, RED, WHITE, YELLOW
from inkyframe.plugin import Plugin, Setting

GLYPH = {"k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"}
OUTLINE = {"k": "♔", "q": "♕", "r": "♖", "b": "♗", "n": "♘", "p": "♙"}

# German names for Lichess themes; English is derived from the camelCase key.
THEMES_DE = {
    "mateIn1": "Matt in 1", "mateIn2": "Matt in 2", "mateIn3": "Matt in 3",
    "mateIn4": "Matt in 4", "mate": "Matt", "fork": "Gabel", "pin": "Fesselung",
    "skewer": "Spieß", "sacrifice": "Opfer", "endgame": "Endspiel", "middlegame": "Mittelspiel",
    "opening": "Eröffnung", "crushing": "Entscheidender Vorteil", "advantage": "Vorteil",
    "short": "Kurz", "long": "Lang", "veryLong": "Sehr lang", "oneMove": "Ein Zug",
    "discoveredAttack": "Abzugsangriff", "deflection": "Ablenkung", "attraction": "Hinlenkung",
    "hangingPiece": "Hängende Figur", "backRankMate": "Grundreihenmatt", "promotion": "Umwandlung",
    "quietMove": "Stiller Zug", "defensiveMove": "Verteidigung", "kingsideAttack": "Königsangriff",
    "queensideAttack": "Damenflügelangriff", "trappedPiece": "Gefangene Figur",
    "doubleCheck": "Doppelschach", "zugzwang": "Zugzwang", "intermezzo": "Zwischenzug",
    "clearance": "Räumung", "interference": "Verstellung", "xRayAttack": "Röntgenangriff",
    "rookEndgame": "Turmendspiel", "pawnEndgame": "Bauernendspiel", "queenEndgame": "Damenendspiel",
    "smotheredMate": "Ersticktes Matt", "exposedKing": "Offener König", "master": "Meisterpartie",
}



def theme_name(key, lang):
    from inkyframe import i18n
    words = re.sub(r"([a-z])([A-Z0-9])", r"\1 \2", key).split()
    english = " ".join(words).capitalize() if words else key
    return i18n.tr(lang, english, THEMES_DE.get(key))


DARK = {"green": GREEN, "blue": BLUE, "black": BLACK, "red": RED, "yellow": YELLOW}


def _sq(name):
    return "abcdefgh".index(name[0]), int(name[1]) - 1


def draw_board(d, fen, x0, y0, size, flip, last=None, dark=GREEN, coords=True):
    s = size // 8
    rows = fen.split()[0].split("/")
    hl = {_sq(n) for n in last} if last else set()
    for r in range(8):
        for c in range(8):
            file_, rank = (7 - c, r) if flip else (c, 7 - r)
            x, y = x0 + c * s, y0 + r * s
            col = WHITE if (file_ + rank) % 2 else dark
            if (file_, rank) in hl:
                col = YELLOW
            d.rectangle((x, y, x + s - 1, y + s - 1), fill=col)
    d.rectangle((x0 - 2, y0 - 2, x0 + 8 * s + 1, y0 + 8 * s + 1), outline=BLACK, width=2)

    pf = gfx.font("symbols", int(s * 0.86))
    for rank_idx, row in enumerate(rows):
        rank = 7 - rank_idx
        file_ = 0
        for ch in row:
            if ch.isdigit():
                file_ += int(ch)
                continue
            c, r = (7 - file_, rank) if flip else (file_, 7 - rank)
            cx, cy = x0 + c * s + s // 2, y0 + r * s + s // 2
            p = ch.lower()
            bbox = d.textbbox((0, 0), GLYPH[p], font=pf, anchor="mm")
            pos = (cx, cy + (bbox[1] + bbox[3]) // -2 + 0)
            if ch.isupper():   # white piece: white fill + black outline
                d.text(pos, GLYPH[p], font=pf, fill=WHITE, anchor="mm")
                d.text(pos, OUTLINE[p], font=pf, fill=BLACK, anchor="mm")
            else:
                d.text(pos, GLYPH[p], font=pf, fill=BLACK, anchor="mm")
            file_ += 1
    if coords:
        cf = gfx.font("sans", 14)
        files = "hgfedcba" if flip else "abcdefgh"
        ranks = "12345678" if flip else "87654321"
        for i in range(8):
            gfx.text_center(d, files[i], cf, x0 + i * s + s // 2, y0 + 8 * s + 4)
            d.text((x0 - 16, y0 + i * s + s // 2 - 8), ranks[i], font=cf, fill=BLACK)



class ChessPuzzle(Plugin):
    id = "chess"
    name = {"en": "Chess Puzzle", "de": "Schach-Puzzle"}
    icon = "♞"
    description = "The Lichess daily puzzle – board, side to move and themes. Reveal the solution in the app."
    author = "inkyframe"
    settings = [
        Setting("dark", "select", "Dark squares", default="green",
                options=[("green", "Green"), ("blue", "Blue"), ("black", "Black"), ("red", "Red")]),
        Setting("show_coords", "bool", "Show coordinates", default=True),
        Setting("solution", "action", "Reveal solution"),
    ]

    def puzzle(self, ctx):
        import chess
        data = ctx.fetch_json("https://lichess.org/api/puzzle/daily", ttl=3 * 3600)
        moves = data["game"]["pgn"].split()
        solution = data["puzzle"]["solution"]
        ply = int(data["puzzle"]["initialPly"])

        def play(n):
            b, last = chess.Board(), None
            for san in moves[:n]:
                last = b.push_san(san)
            return b, last

        # Lichess sends the PGN up to the puzzle position; check both interpretations to be safe.
        for n in (ply + 1, len(moves)):
            board, last = play(n)
            if chess.Move.from_uci(solution[0]) in board.legal_moves:
                break
        sol_san, b2 = [], board.copy()
        for u in solution:
            mv = chess.Move.from_uci(u)
            sol_san.append(b2.san(mv))
            b2.push(mv)
        return {
            "id": data["puzzle"]["id"], "fen": board.fen(), "white_to_move": board.turn == chess.WHITE,
            "last": (chess.square_name(last.from_square), chess.square_name(last.to_square)) if last else None,
            "rating": data["puzzle"].get("rating"), "themes": data["puzzle"].get("themes", []),
            "solution": sol_san, "start_move": board.fullmove_number,
        }

    def sample(self, ctx):
        return {"id": "demo1", "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4",
                "white_to_move": False, "last": ("d2", "d3"), "rating": 1843,
                "themes": ["mateIn2", "kingsideAttack", "sacrifice", "short"],
                "solution": ["Bxf2+", "Kxf2", "Ng4+"], "start_move": 4}

    def action_solution(self, ctx, value=None):
        p = self.puzzle(ctx)
        n, white, out = p["start_move"], p["white_to_move"], []
        for i, m in enumerate(p["solution"]):
            if white:
                out.append(f"{n}. {m}")
            else:
                out.append((f"{n}… " if i == 0 else "") + m)
                n += 1
            white = not white
        return {"message": "  ".join(out), "link": f"https://lichess.org/training/{p['id']}"}

    def render(self, ctx, data=None):
        data = data or self.puzzle(ctx)
        img, d = ctx.canvas()
        s = ctx.settings
        size = 432
        x0, y0 = 40, (ctx.H - size) // 2 - 6
        draw_board(d, data["fen"], x0, y0, size, flip=not data["white_to_move"], last=data["last"],
                   dark=DARK.get(s.get("dark", "green"), GREEN), coords=s.get("show_coords", True))

        RX, RW = 510, ctx.W - 510 - 30
        d.text((RX, 40), ctx.t("Puzzle", "Puzzle"), font=gfx.font("serif", 30), fill=BLACK)
        d.text((RX, 74), ctx.t("of the day", "des Tages"), font=gfx.font("serif-italic", 30), fill=BLACK)
        d.line((RX, 124, RX + RW, 124), fill=BLACK, width=2)
        wtm = data["white_to_move"]
        d.rectangle((RX, 146, RX + 26, 172), fill=WHITE if wtm else BLACK, outline=BLACK, width=2)
        side = ctx.t("White", "Weiß") if wtm else ctx.t("Black", "Schwarz")
        d.text((RX + 38, 142), ctx.t("{s} to move", "{s} am Zug", s=side), font=gfx.font("serif-bold", 26), fill=BLACK)

        keys = data["themes"][:4]
        mate = next((k for k in keys if k.startswith("mateIn")), None)
        y = 196
        if mate:
            d.text((RX, y), theme_name(mate, ctx.lang), font=gfx.font("sans-bold", 22), fill=ctx.ACCENT)
            y += 34
        f = gfx.font("sans", 18)
        rest = [theme_name(k, ctx.lang) for k in keys if k != mate]
        for line in gfx.wrap(d, " · ".join(rest), f, RW) if rest else []:
            d.text((RX, y), line, font=f, fill=BLACK)
            y += 24
        y += 10
        if data.get("rating"):
            d.text((RX, y), ctx.t("Rating {r}", "Wertung {r}", r=data["rating"]), font=f, fill=BLACK)
            y += 24
        n = (len(data["solution"]) + 1) // 2
        sol = ctx.t("Solution: {n} move", "Lösung: {n} eigener Zug", n=n) if n == 1 \
            else ctx.t("Solution: {n} moves", "Lösung: {n} eigene Züge", n=n)
        d.text((RX, y), sol, font=f, fill=BLACK)
        fsm = gfx.font("sans", 14)
        d.text((RX, ctx.H - 70), ctx.t("Solution in the web app", "Lösung in der Web-App"), font=fsm, fill=BLACK)
        d.text((RX, ctx.H - 50), f"lichess.org/training/{data['id']}", font=fsm, fill=BLACK)
        return img
