"""Waste collection – next pickups from your municipality's iCal calendar.
Can take over the display the evening before a pickup."""
import datetime as dt

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting

from . import _calendar as C
from . import _ical

# keyword -> panel colour (first match wins; German and English)
# keyword -> panel colour (first match wins; covers the display languages' usual bin names)
BINS = [
    (("sperr", "bulky", "schadstoff", "hazard", "encombrant", "voluminos", "ingombrant", "grofvuil"), "red"),
    (("gelb", "wertstoff", "leichtverpack", "recycl", "plastic", "plast", "förpack", "emballage", "envase", "embalag",
      "imballagg", "pmd", "muovi", "tworzyw", "metal"), "yellow"),
    (("papier", "pappe", "paper", "cardboard", "papper", "papir", "paperi", "papel", "carta", "carton"), "blue"),
    (("bio", "grün", "garten", "organic", "garden", "compost", "orgán", "orgân", "organi", "umido", "gft", "matavfall",
      "madaffald", "biojäte"), "green"),
    (("glas", "glass", "verre", "vidrio", "vetro", "vidro", "szkło", "lasi"), "green"),
    (("rest", "haus", "general", "residual", "trash", "refuse", "ordures", "indifferen", "resto", "sekajäte",
      "zmiesz", "restaffald"), "black"),
]


def bin_color(name):
    n = name.lower()
    for keys, col in BINS:
        if any(k in n for k in keys):
            return col
    return "black"


def draw_bin(d, x, y, s, color, outline):
    """Simple wheelie bin icon, s = height."""
    w = int(s * .72)
    d.rectangle((x, y + s * .14, x + w, y + s * .22), fill=color, outline=outline, width=2)      # lid
    d.polygon([(x + 3, y + s * .24), (x + w - 3, y + s * .24), (x + w - 7, y + s * .92), (x + 7, y + s * .92)],
              fill=color, outline=outline)
    d.ellipse((x + 4, y + s * .86, x + 4 + s * .16, y + s * 1.02), fill=outline)
    d.line((x + w * .35, y + s * .08, x + w * .65, y + s * .08), fill=outline, width=3)          # handle


class Waste(Plugin):
    id = "waste"
    name = {"en": "Waste Collection", "de": "Müllabfuhr"}
    icon = "🗑"
    description = "Next bin collections from an iCal link (most German waste services offer one)."
    author = "inkyframe"
    can_interrupt = True
    settings = [
        Setting("ical_url", "text", "iCal / webcal link", default="",
                help="Download link of your collection calendar, e.g. from your municipality's website."),
        Setting("days", "number", "Look ahead (days)", default=21, min=3, max=60),
        Setting("remind_from", "time", "Take over the evening before from", default="18:00"),
        Setting("remind_until", "time", "… until (next morning)", default="08:00"),
    ]

    def events(self, ctx):
        url = ctx.settings.get("ical_url", "").strip()
        if not url:
            return None
        return _ical.upcoming(_ical.parse(_ical.fetch_text(url)), ctx.today, int(ctx.settings.get("days", 21)))

    def content_key(self, ctx):
        return f"{ctx.today}|{ctx.settings.get('ical_url')}|{ctx.lang}"

    def refresh_interval(self, ctx):
        return 6 * 60

    def wants_display(self, ctx):
        """Evening before a pickup (and the morning of it)."""
        try:
            evs = self.events(ctx) or []
        except Exception:
            return False
        now = ctx.now.strftime("%H:%M")
        tomorrow = ctx.today + dt.timedelta(days=1)
        if now >= ctx.settings.get("remind_from", "18:00") and any(d == tomorrow for d, _ in evs):
            return True
        return now < ctx.settings.get("remind_until", "08:00") and any(d == ctx.today for d, _ in evs)

    def sample(self, ctx):
        t = ctx.today
        rec, gen = ctx.t("Recycling", "Gelber Sack"), ctx.t("General waste", "Restabfall")
        names = [rec, gen, ctx.t("Paper", "Altpapier"), ctx.t("Organic waste", "Bioabfall"), gen, rec]
        return [(t + dt.timedelta(days=n), names[i]) for i, n in enumerate((1, 1, 4, 8, 15, 15))]

    def view(self, ctx, data):
        """Display-ready facts for the studio layouts – see docs/views/waste.md."""
        today, lang = ctx.today, ctx.lang

        def item(dd, s):
            days = (dd - today).days
            return {"name": s, "color": bin_color(s), "date": dd, "days": days,
                    "weekday": C.weekday(dd, lang), "weekday_short": C.weekday_short(dd, lang),
                    "date_short": ctx.date(dd, "short"), "date_long": ctx.date(dd),
                    "date_text": f"{C.weekday_short(dd, lang)}, {ctx.date(dd, 'short')}",
                    "in_text": ctx.t("in {n} days", "in {n} Tagen", n=days)}

        items = [item(dd, s) for dd, s in data]
        soon = None
        first = [it for it in items if it["days"] in (0, 1)]
        if first:
            when = first[0]["date"]
            group = [it for it in first if it["date"] == when]
            soon = {k: group[0][k] for k in ("date", "days", "weekday", "weekday_short", "date_short",
                                             "date_long", "date_text")}
            soon.update(label=ctx.t("Today", "Heute") if when == today else ctx.t("Tomorrow", "Morgen"),
                        is_today=when == today, items=[{"name": it["name"], "color": it["color"]} for it in group],
                        names=[it["name"] for it in group], names_text=" + ".join(it["name"] for it in group))
        n = int(ctx.settings.get("days", 21) or 21)
        return {
            "title": ctx.t("Waste collection", "Müllabfuhr"), "place": ctx.location.get("name", ""),
            "today": today, "date_text": ctx.date(today), "date_short": ctx.date(today, "short"),
            "weekday": C.weekday(today, lang), "weekday_short": C.weekday_short(today, lang),
            "week": today.isocalendar()[1],
            "soon": soon, "rows": [it for it in items if not soon or it["date"] != soon["date"]],
            "items": items, "look_ahead": n,
            "empty_text": ctx.t("No collections in the next {n} days", "Keine Abholung in den nächsten {n} Tagen",
                                n=ctx.settings.get("days", 21)),
        }

    def render(self, ctx, data=None):
        evs = data if data is not None else self.events(ctx)
        if evs is None:
            return ctx.message(ctx.t("Add your collection calendar", "Abfuhrkalender eintragen"),
                               ctx.t("Paste the iCal link in the web app under Plugins → Waste Collection.",
                                     "iCal-Link in der Web-App unter Plugins → Müllabfuhr einfügen."))
        if evs:                                    # "no collections" stays the regular screen
            from inkyframe import layouts
            v = self.view(ctx, evs)
            special = layouts.render(ctx, self.id, v)
            if special is not None:
                return special
        img, d = ctx.canvas()
        y = ctx.header(d, ctx.t("Waste collection", "Müllabfuhr"))
        today, lang = ctx.today, ctx.lang

        # highlight: today / tomorrow
        soon = [(dd, s) for dd, s in evs if (dd - today).days in (0, 1)]
        if soon:
            when = soon[0][0]
            label = ctx.t("Tomorrow", "Morgen") if when != today else ctx.t("Today", "Heute")
            d.rectangle((40, y + 6, ctx.W - 40, y + 116), outline=ctx.BLACK, width=3)
            d.text((64, y + 18), label, font=gfx.font("serif-italic", 26), fill=ctx.ACCENT)
            names = " + ".join(s for dd, s in soon if dd == when)
            f, lines, lh = gfx.fit_text(d, names, "serif-bold", ctx.W - 300, 64, 44, 22)
            gfx.draw_lines(d, lines, f, lh, 64, y + 52, ctx.W - 300, align="left")
            x = ctx.W - 70
            for dd, s in reversed([e for e in soon if e[0] == when][:3]):
                x -= 70
                draw_bin(d, x, y + 20, 84, ctx.COLORS[bin_color(s)], ctx.BLACK)
            y += 140
        else:
            y += 10

        # list
        rows = [e for e in evs if not soon or e[0] != soon[0][0]][:6]
        if not rows and not soon:
            ctx.fit_center(d, ctx.t("No collections in the next {n} days", "Keine Abholung in den nächsten {n} Tagen",
                                    n=ctx.settings.get("days", 21)), box=(60, y, ctx.W - 120, 200), max_size=34)
        fs, fb = gfx.font("sans", 22), gfx.font("sans-bold", 22)
        for dd, s in rows:
            if y > ctx.H - 70:
                break
            draw_bin(d, 48, y - 4, 40, ctx.COLORS[bin_color(s)], ctx.BLACK)
            days = (dd - today).days
            date_txt = f"{C.weekday_short(dd, lang)}, {ctx.date(dd, 'short')}"
            d.text((100, y), date_txt, font=fb, fill=ctx.BLACK)
            d.text((260, y), s, font=fs, fill=ctx.BLACK)
            rel = ctx.t("in {n} days", "in {n} Tagen", n=days)
            d.text((ctx.W - 40 - gfx.text_w(d, rel, fs), y), rel, font=fs, fill=ctx.BLACK)
            y += 46
        return img
