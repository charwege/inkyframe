"""Birthdays – upcoming birthdays with countdown; a festive screen on the day itself."""
import datetime as dt
import random
import re

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting

from . import _calendar as C
from . import _ical


def parse_list(text):
    """Lines like 'Anna — 24.12.1985', 'Ben - 03.07.' or 'Clara 1990-05-17'."""
    out = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})?", line)
        iso = re.search(r"(\d{4})-(\d{2})-(\d{2})", line)
        if iso:
            y, mo, da = int(iso[1]), int(iso[2]), int(iso[3])
            name = line[:iso.start()]
        elif m:
            da, mo, y = int(m[1]), int(m[2]), int(m[3]) if m[3] else None
            name = line[:m.start()]
        else:
            continue
        name = name.strip(" -—–:,")
        if name:
            out.append({"name": name, "month": mo, "day": da, "year": y})
    return out


def next_date(b, today):
    for y in (today.year, today.year + 1):
        try:
            d = dt.date(y, b["month"], b["day"])
        except ValueError:                   # 29 Feb in a non-leap year
            d = dt.date(y, 3, 1)
        if d >= today:
            return d
    return d


class Birthdays(Plugin):
    id = "birthdays"
    name = {"en": "Birthdays", "de": "Geburtstage"}
    icon = "🎂"
    description = "Upcoming birthdays with days to go and age. Festive screen on the day."
    author = "inkyframe"
    can_interrupt = True
    settings = [
        Setting("people", "textarea", "Birthdays", default="",
                help="One per line: “Name — 24.12.1985” (year optional)."),
        Setting("ical_url", "text", "…or an iCal link (optional)", default="",
                help="e.g. the birthday calendar of your address book."),
        Setting("take_over", "bool", "Show the festive screen on the day", default=True),
        Setting("from", "time", "Festive screen from", default="07:00"),
        Setting("until", "time", "… until", default="12:00"),
    ]

    def people(self, ctx):
        ppl = parse_list(ctx.settings.get("people"))
        url = (ctx.settings.get("ical_url") or "").strip()
        if url:
            for e in _ical.parse(_ical.fetch_text(url)):
                name = re.sub(r"^(Geburtstag( von)?|Birthday( of)?)\s*:?\s*|('s)? birthday$|s? Geburtstag$", "",
                              e["summary"], flags=re.I).strip()
                y = e["date"].year if e["date"].year > 1900 else None
                ppl.append({"name": name, "month": e["date"].month, "day": e["date"].day, "year": y})
        return ppl

    def content_key(self, ctx):
        return f"{ctx.today}|{sorted(ctx.settings.items())}|{ctx.lang}"

    def wants_display(self, ctx):
        s = ctx.settings
        if not s.get("take_over"):
            return False
        now = ctx.now.strftime("%H:%M")
        if not (s.get("from", "07:00") <= now < s.get("until", "12:00")):
            return False
        try:
            return any(next_date(b, ctx.today) == ctx.today for b in self.people(ctx))
        except Exception:
            return False

    def sample(self, ctx):
        t = ctx.today
        mk = lambda n, days, y: {"name": n, "month": (t + dt.timedelta(days=days)).month,
                                 "day": (t + dt.timedelta(days=days)).day, "year": y}
        return [mk("Anna", 3, 1988), mk("Grandpa", 11, 1946), mk("Ben", 26, None), mk("Clara", 40, 2019),
                mk("Mia", 58, 1995)]

    def render(self, ctx, data=None):
        people = data if data is not None else self.people(ctx)
        if not people:
            return ctx.message(ctx.t("No birthdays yet", "Noch keine Geburtstage"),
                               ctx.t("Add them under Plugins → Birthdays.", "Unter Plugins → Geburtstage eintragen."))
        today = ctx.today
        upcoming = sorted(((next_date(b, today), b) for b in people), key=lambda x: x[0])
        img, d = ctx.canvas()
        celebs = [b for dd, b in upcoming if dd == today]
        if celebs:
            rnd = random.Random(str(today))
            cols = [ctx.RED, ctx.YELLOW, ctx.GREEN, ctx.BLUE]
            for _ in range(140):                       # confetti
                x, y, s = rnd.randint(0, ctx.W), rnd.randint(0, ctx.H), rnd.randint(4, 9)
                if 120 < y < 380 and 80 < x < 720:
                    continue
                d.polygon([(x, y), (x + s, y + s // 2), (x + s // 3, y + s)], fill=rnd.choice(cols))
            ctx.text_center(d, ctx.t("Happy birthday", "Alles Gute zum Geburtstag"), gfx.font("serif-italic", 34), ctx.W // 2, 130, ctx.ACCENT)
            names = " & ".join(b["name"] for b in celebs)
            ctx.fit_center(d, names + "!", box=(100, 180, ctx.W - 200, 120), kind="serif-bold", max_size=80)
            ages = [f"{b['name']}: {today.year - b['year']}" for b in celebs if b.get("year")]
            if ages:
                line = ctx.t("turns {n}", "wird {n}", n=ages[0].split(": ")[1]) if len(ages) == 1 else ", ".join(ages)
                ctx.text_center(d, line, gfx.font("sans", 24), ctx.W // 2, 320)
            return img

        y = ctx.header(d, ctx.t("Birthdays", "Geburtstage"), ctx.t("coming up", "demnächst"))
        first = True
        for dd, b in upcoming[:5]:
            days = (dd - today).days
            age = " · " + ctx.t("turns {n}", "wird {n}", n=dd.year - b["year"]) if b.get("year") else ""
            if first:
                d.rectangle((40, y + 4, ctx.W - 40, y + 110), outline=ctx.BLACK, width=2)
                f = gfx.font("serif-bold", 120 if days < 100 else 90)
                num = str(days)
                d.text((70, y + 58), num, font=f, fill=ctx.ACCENT, anchor="lm")
                xx = 90 + gfx.text_w(d, num, f)
                d.text((xx, y + 20), b["name"], font=gfx.font("serif-bold", 38), fill=ctx.BLACK)
                when = ctx.t("tomorrow", "morgen") if days == 1 else ctx.t("in {n} days", "in {n} Tagen", n=days)
                datestr = ctx.date(dd)
                d.text((xx, y + 70), f"{when} · {datestr}{age}", font=gfx.font("sans", 19), fill=ctx.BLACK)
                y += 136
                first = False
                continue
            f = gfx.font("sans", 22)
            d.text((60, y), b["name"], font=gfx.font("sans-bold", 22), fill=ctx.BLACK)
            ds = ctx.date(dd, "short")
            d.text((380, y), ds + age, font=f, fill=ctx.BLACK)
            rel = ctx.t("in {n} d", "in {n} T.", n=days)
            d.text((ctx.W - 60 - gfx.text_w(d, rel, f), y), rel, font=f, fill=ctx.BLACK)
            d.line((60, y + 36, ctx.W - 60, y + 36), fill=ctx.BLACK, width=1)
            y += 50
        return img
