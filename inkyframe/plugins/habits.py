"""Habit tracker – one small calendar grid per habit. Tick today's habits in the web app."""
import datetime as dt
import hashlib

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting

from . import _calendar as C


def habit_list(ctx):
    return [h.strip() for h in (ctx.settings.get("habits") or "").splitlines() if h.strip()][:6]


def streak(days_done, today):
    n, d = 0, today
    if d.isoformat() not in days_done:          # today not ticked yet doesn't break the streak
        d -= dt.timedelta(days=1)
    while d.isoformat() in days_done:
        n += 1
        d -= dt.timedelta(days=1)
    return n


def best_streak(days_done):
    """Longest run of consecutive days in a set of ISO dates."""
    best = 0
    for k in days_done:
        d = dt.date.fromisoformat(k)
        if (d - dt.timedelta(days=1)).isoformat() in days_done:
            continue                                  # not the start of a run
        n = 1
        while (d + dt.timedelta(days=n)).isoformat() in days_done:
            n += 1
        best = max(best, n)
    return best


def week_grid(days_done, today, weeks):
    """Calendar grid like the regular screen: `weeks` columns (oldest first, the last one is the current
    week), each a list of 7 flags Monday…Sunday – True done, False not done, None = day after today."""
    start = today - dt.timedelta(days=today.weekday() + 7 * (weeks - 1))
    grid = []
    for w in range(weeks):
        col = []
        for wd in range(7):
            day = start + dt.timedelta(days=w * 7 + wd)
            col.append(None if day > today else day.isoformat() in days_done)
        grid.append(col)
    return grid


PALETTE = ["green", "blue", "red", "black", "green", "blue"]      # colour of the 1st … 6th habit


class Habits(Plugin):
    id = "habits"
    name = {"en": "Habit Tracker", "de": "Gewohnheiten"}
    icon = "✓"
    description = "Up to six habits with a GitHub-style calendar and streaks. Tick them off in the app."
    author = "inkyframe"
    settings = [
        Setting("habits", "textarea", "Habits (one per line, max 6)", default="Read\nExercise\nNo phone after 10 pm"),
        Setting("weeks", "number", "Weeks shown", default=12, min=4, max=16),
    ]

    # one "tick" button per habit, generated from the current list
    def extra_settings(self, ctx):
        log = ctx.load_state().get("log", {})
        today = log.get(ctx.today.isoformat(), [])
        return [Setting(f"toggle_{i}", "action", ("☑ " if h in today else "☐ ") + h + " – today")
                for i, h in enumerate(habit_list(ctx))]

    def action(self, ctx, key, value=None):
        if not key.startswith("toggle_"):
            raise ValueError(f"unknown action {key}")
        habits = habit_list(ctx)
        i = int(key.split("_")[1])
        if i >= len(habits):
            raise ValueError("habit no longer exists")
        state = ctx.load_state()
        log = state.setdefault("log", {})
        day = log.setdefault(ctx.today.isoformat(), [])
        h = habits[i]
        if h in day:
            day.remove(h)
            msg = f"“{h}” unticked"
        else:
            day.append(h)
            msg = f"“{h}” done today ✓"
        cutoff = (ctx.today - dt.timedelta(days=400)).isoformat()      # keep the file small
        state["log"] = {k: v for k, v in log.items() if k >= cutoff and v}
        ctx.save_state(state)
        return {"message": msg}

    def content_key(self, ctx):
        st = hashlib.md5(repr(sorted(ctx.load_state().get("log", {}).items())).encode()).hexdigest()
        return f"{ctx.today}|{st}|{sorted(ctx.settings.items())}|{ctx.lang}"

    def sample(self, ctx):
        import random
        rnd = random.Random(7)
        habits = [ctx.t("Read", "Lesen"), ctx.t("Exercise", "Sport"),
                  ctx.t("No phone after 10 pm", "Kein Handy ab 22 Uhr"), ctx.t("Meditate", "Meditieren")]
        log = {}
        for back in range(16 * 7):
            day = (ctx.today - dt.timedelta(days=back)).isoformat()
            log[day] = [h for j, h in enumerate(habits) if rnd.random() < (0.85 if back < 9 else 0.6 - j * 0.08)]
        return {"habits": habits, "log": log}

    def view(self, ctx, data):
        """Display-ready facts for the studio layouts – see docs/views/habits.md."""
        today, lang = ctx.today, ctx.lang
        log = data["log"]
        weeks = int(ctx.settings.get("weeks", 12) or 12)
        unit = ctx.t("d", "T")
        items = []
        for i, h in enumerate(data["habits"][:6]):
            done = {k for k, v in log.items() if h in v}
            sk = streak(done, today)
            days = [(today - dt.timedelta(days=41 - n)).isoformat() in done for n in range(42)]
            items.append({
                "name": h, "color": PALETTE[i], "streak": sk, "streak_text": f"{sk} {unit}",
                "hot": sk >= 7, "best": best_streak(done), "done_today": today.isoformat() in done,
                "days": days, "done_count": sum(days), "rate": round(sum(days) / 42, 3),
                "grid": week_grid(done, today, 6), "grid_all": week_grid(done, today, weeks),
            })
        return {
            "title": ctx.t("Habits", "Gewohnheiten"), "today": today, "date_text": ctx.date(today),
            "date_short": ctx.date(today, "short"), "weekday": C.weekday(today, lang),
            "weekday_short": C.weekday_short(today, lang),
            "weekday_letters": list(C.weekday_letters(lang)), "day_unit": unit,
            "weeks": 6, "days": 42, "now": [5, today.weekday()], "weeks_all": weeks,
            "start": today - dt.timedelta(days=today.weekday() + 35),
            "best": max((it["best"] for it in items), default=0),
            "best_streak": max((it["streak"] for it in items), default=0),
            "habits": items,
        }

    def render(self, ctx, data=None):
        habits = data["habits"] if data else habit_list(ctx)
        log = data["log"] if data else ctx.load_state().get("log", {})
        if not habits:
            return ctx.message(ctx.t("No habits yet", "Noch keine Gewohnheiten"),
                               ctx.t("Add some under Plugins → Habit Tracker.", "Unter Plugins → Gewohnheiten eintragen."))
        from inkyframe import layouts
        v = self.view(ctx, {"habits": habits, "log": log})
        special = layouts.render(ctx, self.id, v)
        if special is not None:
            return special
        weeks = int(ctx.settings.get("weeks", 12))
        img, d = ctx.canvas()
        ctx.header(d, ctx.t("Habits", "Gewohnheiten"), ctx.date(ctx.today))
        cols = 3 if len(habits) > 4 else 2 if len(habits) > 1 else 1
        rows = (len(habits) + cols - 1) // cols
        pw, ph = (ctx.W - 60) // cols, (ctx.H - 120) // rows
        palette = [ctx.GREEN, ctx.BLUE, ctx.RED, ctx.BLACK, ctx.GREEN, ctx.BLUE]
        today = ctx.today
        start = today - dt.timedelta(days=today.weekday() + 7 * (weeks - 1))   # Monday, N weeks ago
        for i, h in enumerate(habits):
            x0, y0 = 30 + (i % cols) * pw, 112 + (i // cols) * ph
            done = {k for k, v in log.items() if h in v}
            col = palette[i]
            f = gfx.font("sans-bold", 18)
            name = h if gfx.text_w(d, h, f) < pw - 90 else gfx.wrap(d, h, f, pw - 90)[0] + "…"
            d.text((x0 + 10, y0 + 4), name, font=f, fill=ctx.BLACK)
            sk = streak(done, today)
            st = f"{sk} {ctx.t('d', 'T')}"
            d.text((x0 + pw - 20 - gfx.text_w(d, st, f), y0 + 4), st, font=f, fill=ctx.ACCENT if sk >= 7 else ctx.BLACK)
            cell = max(6, min((pw - 30) // weeks, (ph - 50) // 7))
            gx, gy = x0 + 10, y0 + 34
            for w in range(weeks):
                for wd in range(7):
                    day = start + dt.timedelta(days=w * 7 + wd)
                    if day > today:
                        continue
                    cx, cy = gx + w * cell, gy + wd * cell
                    if day.isoformat() in done:
                        d.rectangle((cx, cy, cx + cell - 3, cy + cell - 3), fill=col)
                    else:
                        d.rectangle((cx, cy, cx + cell - 3, cy + cell - 3), outline=ctx.BLACK)
                    if day == today:
                        d.rectangle((cx - 2, cy - 2, cx + cell - 1, cy + cell - 1), outline=ctx.RED, width=2)
        return img
