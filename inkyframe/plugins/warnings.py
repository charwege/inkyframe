"""Official weather warnings for your location (Deutscher Wetterdienst via the free Bright Sky API).
Can take over the display while a warning of the chosen level is active. Germany only."""
import datetime as dt

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting

LEVELS = ["minor", "moderate", "severe", "extreme"]
LEVEL_TEXT = {"minor": ("Warning", "Wetterwarnung"), "moderate": ("Severe weather", "Markantes Wetter"),
              "severe": ("Severe weather warning", "Unwetterwarnung"),
              "extreme": ("Extreme weather warning", "Extremes Unwetter")}


def _parse(ts):
    try:
        return dt.datetime.fromisoformat(ts).astimezone()
    except (TypeError, ValueError):
        return None


def triangle(d, x, y, s, fill, outline):
    d.polygon([(x + s / 2, y), (x + s, y + s * .88), (x, y + s * .88)], fill=fill, outline=outline)
    d.polygon([(x + s / 2, y + 6), (x + s - 6, y + s * .88 - 4), (x + 6, y + s * .88 - 4)], outline=outline)
    w = max(3, s // 12)
    d.rectangle((x + s / 2 - w / 2, y + s * .3, x + s / 2 + w / 2, y + s * .62), fill=outline)
    d.ellipse((x + s / 2 - w * .7, y + s * .68, x + s / 2 + w * .7, y + s * .68 + w * 1.4), fill=outline)


class WeatherWarnings(Plugin):
    id = "warnings"
    name = {"en": "Weather Warnings", "de": "Unwetterwarnung"}
    icon = "⚠"
    description = "DWD warnings for your location (Germany). Can take over the screen during a warning."
    author = "inkyframe"
    can_interrupt = True
    refresh_minutes = 15
    settings = [
        Setting("interrupt_level", "select", "Take over the display from", default="moderate", options=[
            ("minor", "Any warning (yellow)"), ("moderate", "Severe weather (orange)"),
            ("severe", "Severe weather warning (red)"), ("extreme", "Extreme only (violet)")]),
    ]

    def alerts(self, ctx):
        loc = ctx.location
        res = ctx.fetch_json("https://api.brightsky.dev/alerts", ttl=10 * 60,
                             params={"lat": loc["lat"], "lon": loc["lon"]})
        now = ctx.now.astimezone()
        out = []
        for a in res.get("alerts", []):
            exp = _parse(a.get("expires"))
            if exp and exp < now:
                continue
            out.append(a)
        out.sort(key=lambda a: -LEVELS.index(a.get("severity", "minor")) if a.get("severity") in LEVELS else 0)
        return {"alerts": out, "place": (res.get("location") or {}).get("name", loc.get("name", ""))}

    def content_key(self, ctx):
        try:
            data = self.alerts(ctx)
            return "|".join(a.get("id", "") for a in data["alerts"]) + f"|{ctx.lang}|{ctx.today}"
        except Exception:
            return f"err|{ctx.today}"

    def wants_display(self, ctx):
        try:
            alerts = self.alerts(ctx)["alerts"]
        except Exception:
            return False
        min_level = LEVELS.index(ctx.settings.get("interrupt_level", "moderate"))
        return any(LEVELS.index(a.get("severity", "minor")) >= min_level
                   for a in alerts if a.get("severity") in LEVELS)

    def status(self, ctx):
        try:
            n = len(self.alerts(ctx)["alerts"])
            return "OK · no warnings" if n == 0 else f"OK · {n} active warning(s)"
        except Exception as e:
            return f"error: {e}"

    def sample(self, ctx):
        now = ctx.now.astimezone()
        return {"place": ctx.location.get("name", "Berlin"), "alerts": [{
            "severity": "moderate", "event_en": "Storm gusts", "event_de": "Sturmböen",
            "headline_en": "Official WARNING of STORM GUSTS", "headline_de": "Amtliche WARNUNG vor STURMBÖEN",
            "description_en": "Storm gusts of up to 75 km/h (21 m/s, 40 kn, Bft 9) from westerly directions may occur.",
            "description_de": "Es treten Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 40 kn, Bft 9) aus westlicher Richtung auf.",
            "onset": now.isoformat(), "expires": (now + dt.timedelta(hours=9)).isoformat()}]}

    def render(self, ctx, data=None):
        data = data or self.alerts(ctx)
        alerts, de = data["alerts"], ctx.lang == "de"
        img, d = ctx.canvas()
        if not alerts:
            y = ctx.header(d, ctx.t("Weather warnings", "Wetterwarnungen"), data["place"])
            cx, cy = ctx.W // 2, 250
            d.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), outline=ctx.GREEN, width=8)
            d.line((cx - 30, cy, cx - 8, cy + 24, cx + 34, cy - 26), fill=ctx.GREEN, width=10)
            ctx.text_center(d, ctx.t("No warnings right now", "Derzeit keine Warnungen"),
                            gfx.font("serif", 36), cx, 340)
            ctx.footer(d, ctx.t("Source: Deutscher Wetterdienst via Bright Sky · {t}", "Quelle: Deutscher Wetterdienst über Bright Sky · {t}",
                                t=f"{ctx.now:%H:%M}"))
            return img

        a = alerts[0]
        sev = a.get("severity", "minor")
        col = ctx.YELLOW if sev == "minor" else ctx.RED
        d.rectangle((0, 0, ctx.W, 12), fill=col)
        triangle(d, 40, 40, 120, col, ctx.BLACK)
        en, de_txt = LEVEL_TEXT.get(sev, LEVEL_TEXT["minor"])
        d.text((190, 40), ctx.t(en, de_txt).upper(), font=gfx.font("sans-bold", 18), fill=ctx.RED if sev != "minor" else ctx.BLACK)
        event = a.get("event_de" if de else "event_en") or a.get("event_en") or ""
        f, lines, lh = gfx.fit_text(d, event, "serif-bold", ctx.W - 230, 90, 52, 26, 1.1)
        gfx.draw_lines(d, lines, f, lh, 190, 66, ctx.W - 230, align="left")
        on, ex = _parse(a.get("onset")), _parse(a.get("expires"))
        span = ""
        if on and ex:
            from ._calendar import weekday_short
            a_txt = f"{weekday_short(on, ctx.lang)} {on:%H:%M}"
            b_txt = f"{ex:%H:%M}" if ex.date() == on.date() else f"{weekday_short(ex, ctx.lang)} {ex:%H:%M}"
            span = ctx.t("{a} – {b}", "{a} bis {b} Uhr", a=a_txt, b=b_txt)
        d.text((190, 66 + len(lines) * lh + 6), f"{data['place']} · {span}", font=gfx.font("sans", 18), fill=ctx.BLACK)

        desc = a.get("description_de" if de else "description_en") or a.get("headline_en") or ""
        f2, l2, lh2 = gfx.fit_text(d, desc, "serif", ctx.W - 80, 200 if len(alerts) == 1 else 140, 28, 16, 1.25)
        gfx.draw_lines(d, l2, f2, lh2, 40, 200, ctx.W - 80, align="left")
        if len(alerts) > 1:
            more = ", ".join((x.get("event_de" if de else "event_en") or "") for x in alerts[1:4])
            d.text((40, ctx.H - 64), ctx.t("Also: {m}", "Außerdem: {m}", m=more), font=gfx.font("sans-bold", 16), fill=ctx.BLACK)
        ctx.footer(d, ctx.t("Deutscher Wetterdienst via Bright Sky · updated {t}", "Deutscher Wetterdienst über Bright Sky · Stand {t}",
                            t=f"{ctx.now:%H:%M}"))
        return img
