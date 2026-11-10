"""Sudoku of the day – generated locally (same puzzle for everyone on the same date).
Grab a pencil: print-like layout; the solution is revealed in the web app."""
import random

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting

from . import _calendar as C

CLUES = {"easy": 38, "medium": 31, "hard": 27}
LEVEL_NAMES = {"easy": ("Easy", "Leicht"), "medium": ("Medium", "Mittel"), "hard": ("Hard", "Schwer")}


def _candidates(g, i):
    r, c = divmod(i, 9)
    used = set(g[r * 9:(r + 1) * 9]) | set(g[c::9])
    br, bc = r // 3 * 3, c // 3 * 3
    for rr in range(br, br + 3):
        used |= set(g[rr * 9 + bc:rr * 9 + bc + 3])
    return [v for v in range(1, 10) if v not in used]


def solve(g, rnd=None, limit=2):
    """Backtracking with 'fewest candidates first'. Returns (solution_count, first_solution)."""
    g = list(g)
    found = []

    def rec():
        best, best_c = None, None
        for i, v in enumerate(g):
            if v == 0:
                cands = _candidates(g, i)
                if not cands:
                    return False
                if best_c is None or len(cands) < len(best_c):
                    best, best_c = i, cands
                    if len(cands) == 1:
                        break
        if best is None:
            found.append(list(g))
            return len(found) >= limit
        if rnd:
            rnd.shuffle(best_c)
        for v in best_c:
            g[best] = v
            if rec():
                return True
        g[best] = 0
        return False

    rec()
    return len(found), (found[0] if found else None)


def generate(seed, level="medium"):
    rnd = random.Random(seed)
    _, full = solve([0] * 81, rnd=rnd, limit=1)
    puzzle = list(full)
    target = CLUES.get(level, 31)
    cells = list(range(81))
    rnd.shuffle(cells)
    for i in cells:
        if sum(1 for v in puzzle if v) <= target:
            break
        keep = puzzle[i]
        puzzle[i] = 0
        if solve(puzzle, limit=2)[0] != 1:
            puzzle[i] = keep
    return puzzle, full


def rows(puzzle):
    """Flat list of 81 numbers -> 9 rows of 9 (0 = empty cell)."""
    return [list(puzzle[r * 9:(r + 1) * 9]) for r in range(9)]


class Sudoku(Plugin):
    id = "sudoku"
    name = {"en": "Sudoku of the Day", "de": "Sudoku des Tages"}
    icon = "#"
    description = "A new Sudoku every day, generated on the frame. Reveal the solution in the app."
    author = "inkyframe"
    settings = [
        Setting("level", "select", "Difficulty", default="medium",
                options=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]),
        Setting("solution", "action", "Reveal today's solution"),
    ]

    def puzzle(self, ctx):
        level = ctx.settings.get("level", "medium")
        key = f"{ctx.today}|{level}"
        st = ctx.load_state()
        if st.get("key") != key:                          # generate once per day, then reuse
            p, s = generate(f"inkyframe-{key}", level)
            st = {"key": key, "puzzle": p, "solution": s}
            ctx.save_state(st)
        return st["puzzle"], st["solution"]

    def action_solution(self, ctx, value=None):
        _, sol = self.puzzle(ctx)
        rows = [" ".join("".join(map(str, sol[r * 9 + c:r * 9 + c + 3])) for c in (0, 3, 6)) for r in range(9)]
        return {"message": " / ".join(rows)}

    def content_key(self, ctx):
        return f"{ctx.today}|{ctx.settings.get('level')}|{ctx.lang}"

    def sample(self, ctx):
        return generate("inkyframe-sample", "medium")

    def view(self, ctx, data):
        """Display-ready facts for the design layouts (docs/views/sudoku.md)."""
        puzzle = list(data[0])
        level = ctx.settings.get("level", "medium")
        if level not in LEVEL_NAMES:
            level = "medium"
        givens = sum(1 for v in puzzle if v)
        return {
            "title": "Sudoku", "subtitle": ctx.t("of the day", "des Tages"),
            "name": self.display_name(ctx.lang),
            "grid": rows(puzzle), "puzzle": puzzle,
            "givens": givens, "empty": 81 - givens,
            "givens_text": ctx.t("{n} givens", "{n} Vorgaben", n=givens),
            "level": level, "level_no": {"easy": 1, "medium": 2, "hard": 3}[level], "level_max": 3,
            "level_name": ctx.t(*LEVEL_NAMES[level]),
            "weekday": C.weekday(ctx.today, ctx.lang), "date": ctx.date(ctx.today, weekday=False),
            "date_long": ctx.date(ctx.today), "today": ctx.today,
            "hint": ctx.t("Solution in the web app", "Lösung in der Web-App"),
            "place": ctx.location.get("name", ""),
        }

    def render(self, ctx, data=None):
        data = data or self.puzzle(ctx)
        puzzle, _ = data
        from inkyframe import layouts
        v = self.view(ctx, data)
        special = layouts.render(ctx, self.id, v)
        if special is not None:
            return special
        img, d = ctx.canvas()
        cell = 48
        size = cell * 9
        x0, y0 = 30, (ctx.H - size) // 2
        f = gfx.font("serif-bold", 30)
        for i, v in enumerate(puzzle):
            r, c = divmod(i, 9)
            if v:
                d.text((x0 + c * cell + cell / 2, y0 + r * cell + cell / 2 + 1), str(v), font=f, fill=ctx.BLACK, anchor="mm")
        for k in range(10):
            w = 4 if k % 3 == 0 else 1
            d.line((x0 + k * cell, y0, x0 + k * cell, y0 + size), fill=ctx.BLACK, width=w)
            d.line((x0, y0 + k * cell, x0 + size, y0 + k * cell), fill=ctx.BLACK, width=w)

        RX = x0 + size + 40
        d.text((RX, 50), "Sudoku", font=gfx.font("serif", 40), fill=ctx.BLACK)
        d.text((RX, 98), ctx.t("of the day", "des Tages"), font=gfx.font("serif-italic", 26), fill=ctx.BLACK)
        d.line((RX, 144, ctx.W - 30, 144), fill=ctx.BLACK, width=2)
        date = f"{C.weekday(ctx.today, ctx.lang)}\n{ctx.date(ctx.today, weekday=False)}"
        y = 164
        for line in date.split("\n"):
            d.text((RX, y), line, font=gfx.font("serif", 24), fill=ctx.BLACK)
            y += 32
        level = ctx.settings.get("level", "medium")
        names = LEVEL_NAMES[level]
        dots = {"easy": 1, "medium": 2, "hard": 3}[level]
        y += 18
        for k in range(3):
            d.ellipse((RX + k * 26, y + 4, RX + k * 26 + 16, y + 20), fill=ctx.ACCENT if k < dots else None, outline=ctx.BLACK, width=2)
        d.text((RX + 86, y), ctx.t(*names), font=gfx.font("sans-bold", 20), fill=ctx.BLACK)
        givens = sum(1 for v in puzzle if v)
        d.text((RX, y + 40), ctx.t("{n} givens", "{n} Vorgaben", n=givens), font=gfx.font("sans", 17), fill=ctx.BLACK)
        d.text((RX, ctx.H - 60), ctx.t("Solution in the web app", "Lösung in der Web-App"), font=gfx.font("sans", 14), fill=ctx.BLACK)
        return img
