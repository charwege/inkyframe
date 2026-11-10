"""Countdown – days until an event.

This plugin is intentionally small and heavily commented: copy it as a starting point
for your own plugin (or run `python -m inkyframe.dev new myplugin`).
"""
import datetime as dt

from inkyframe.plugin import Plugin, Setting


class Countdown(Plugin):
    # --- identity: shown in the web app ---------------------------------------------
    id = "countdown"                                   # unique, lowercase
    name = {"en": "Countdown", "de": "Countdown"}      # plain str or {"en": ..., "de": ...}
    icon = "⏳"
    description = "Days until a date you choose – holidays, birthdays, a trip."
    author = "inkyframe"

    # --- settings: the web app builds the form from this list ------------------------
    settings = [
        Setting("title", "text", "Event", default="Summer holidays"),
        Setting("date", "date", "Date", default=f"{dt.date.today().year + 1}-07-01"),
        Setting("color", "color", "Accent colour (empty = design accent)", default=""),
    ]

    # Re-render whenever this value changes (default would be once a day; settings matter too).
    def content_key(self, ctx):
        return f"{ctx.today}|{ctx.settings['title']}|{ctx.settings['date']}|{ctx.settings['color']}|{ctx.lang}"

    # Offline demo data so previews and CI work without network (optional).
    def sample(self, ctx):
        return {"title": ctx.t("Summer holidays", "Sommerferien"), "date": ctx.today + dt.timedelta(days=42)}

    # --- view: the facts of the screen as a plain dict (used by the studio layouts) ----
    def view(self, ctx, data):
        from . import _calendar as C
        title = (data or {}).get("title") or ctx.settings["title"]
        target = (data or {}).get("date") or dt.date.fromisoformat(ctx.settings["date"])
        today = ctx.today
        days = (target - today).days
        if days > 1:
            big, small = str(days), ctx.t("days until", "Tage bis")
        elif days == 1:
            big, small = "1", ctx.t("day until", "Tag bis")
        elif days == 0:
            big, small = ctx.t("Today!", "Heute!"), ""
        else:
            big, small = str(-days), ctx.t("days since", "Tage seit")
        count = abs(days)
        first, last = min(today, target), max(today, target)
        region = ctx.location.get("holidays", "none")
        strip = []
        for i in range(count + 1 if count <= 366 else 0):      # one entry per day, today … event
            day = first + dt.timedelta(days=i)
            strip.append({"date": day, "day": day.day, "weekday": day.weekday(),
                          "weekend": day.weekday() >= 5, "special": C.is_special(day, region),
                          "first_of_month": day.day == 1, "today": day == today, "target": day == target})
        color = ctx.settings.get("color") or ""
        return {
            "title": self.display_name(ctx.lang), "event": title,
            "days": days, "count": count, "big": big, "small": small,
            "state": "future" if days > 0 else ("today" if days == 0 else "past"),
            "weeks": count // 7, "rest_days": count % 7,
            "weekends": sum(1 for i in range(1, count + 1) if (first + dt.timedelta(days=i)).weekday() == 5)
            if count <= 3660 else count // 7,
            "target": target, "date": ctx.date(target, weekday=False, year=True),
            "date_short": ctx.date(target, "short"),
            "target_weekday": C.weekday(target, ctx.lang), "target_month": C.month(target, ctx.lang),
            "today": today, "today_text": ctx.date(today, weekday=False, year=True),
            "today_short": ctx.date(today, "short"), "today_weekday": C.weekday(today, ctx.lang),
            "week_from": first.isocalendar()[1], "week_to": last.isocalendar()[1],
            "strip": strip, "color": color if color in ctx.COLORS else "",
            "now": ctx.now, "time": f"{ctx.now:%H:%M}", "place": ctx.location.get("name", ""),
        }

    # --- drawing: return an 800×480 PIL image -----------------------------------------
    def render(self, ctx, data=None):
        title = (data or {}).get("title") or ctx.settings["title"]
        try:
            target = (data or {}).get("date") or dt.date.fromisoformat(ctx.settings["date"])
        except ValueError:
            return ctx.message(ctx.t("Please set a valid date", "Bitte ein gültiges Datum eintragen"))
        days = (target - ctx.today).days
        accent = ctx.COLORS.get(ctx.settings.get("color") or "", ctx.ACCENT)

        # Studio designs bring their own layout; they draw from the view (docs/views/countdown.md).
        from inkyframe import layouts
        v = self.view(ctx, data)
        special = layouts.render(ctx, self.id, v)
        if special is not None:
            return special

        img, d = ctx.canvas()                       # white canvas + ImageDraw
        ctx.frame(d)                                # border in the chosen design
        big, small = v["big"], v["small"]

        ctx.text_center(d, small, ctx.font("serif-italic", 30), ctx.W // 2, 70)
        f = ctx.font("serif-bold", 190 if len(big) <= 3 else 110)
        d.text((ctx.W // 2, 210), big, font=f, fill=accent, anchor="mm")
        ctx.fit_center(d, title, box=(80, 320, ctx.W - 160, 90), kind="serif", max_size=48)
        date_str = ctx.date(target, weekday=False, year=True)
        ctx.text_center(d, date_str, ctx.font("sans", 18), ctx.W // 2, ctx.H - 60)
        return img
