"""Water level of a river gauge – PEGELONLINE (Federal Waterways and Shipping Administration, Germany).
Covers federal waterways (Rhine, Elbe, Weser, Danube, canals …); smaller rivers run by the federal
states are not included."""
import datetime as dt
import urllib.parse

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting

API = "https://www.pegelonline.wsv.de/webservices/rest-api/v2"
STATE = {"low": ("low", "niedrig"), "normal": ("normal", "normal"), "high": ("high", "hoch")}


class WaterLevel(Plugin):
    id = "waterlevel"
    name = {"en": "Water Level", "de": "Pegelstand"}
    icon = "≈"
    description = "Current level and 7-day curve of a river gauge on a German federal waterway (PEGELONLINE)."
    author = "inkyframe"
    refresh_minutes = 60
    settings = [
        Setting("station", "text", "Gauge (station name)", default="", help="Use “Find gauge” to look up the exact name."),
        Setting("find", "action", "Find gauge", input="Search, e.g. Köln, Minden, Hann. Münden"),
        Setting("days", "number", "Days shown", default=7, min=2, max=30),
    ]

    def action_find(self, ctx, value=None):
        q = (value or "").strip()
        if not q:
            raise ValueError("Type part of a place name first.")
        res = ctx.fetch_json(f"{API}/stations.json", ttl=24 * 3600, params={"fuzzyId": q})
        if not res:
            return {"message": "No gauge found."}
        names = [f"{s['longname']} ({s.get('water', {}).get('longname', '').title()})" for s in res[:8]]
        return {"message": "Copy one of these into “Gauge”: " + " · ".join(names)}

    def fetch(self, ctx):
        name = ctx.settings.get("station", "").strip()
        if not name:
            return None
        st = urllib.parse.quote(name, safe="")
        meta = ctx.fetch_json(f"{API}/stations/{st}.json", ttl=24 * 3600)
        ts = ctx.fetch_json(f"{API}/stations/{st}/W.json", ttl=15 * 60,
                            params={"includeCurrentMeasurement": "true", "includeCharacteristicValues": "true"})
        days = int(ctx.settings.get("days", 7))
        series = ctx.fetch_json(f"{API}/stations/{st}/W/measurements.json", ttl=30 * 60, params={"start": f"P{days}D"})
        chars = {c.get("shortname"): c.get("value") for c in ts.get("characteristicValues", []) or []}
        return {"name": meta.get("longname", name), "water": meta.get("water", {}).get("longname", ""),
                "unit": ts.get("unit", "cm"), "current": ts.get("currentMeasurement", {}),
                "series": [(m["timestamp"], m["value"]) for m in series if m.get("value") is not None],
                "mw": chars.get("MW"), "hsw": chars.get("HSW")}

    def content_key(self, ctx):
        return f"{ctx.today}|{ctx.now.hour}|{sorted(ctx.settings.items())}|{ctx.lang}"

    def sample(self, ctx):
        import math
        now = ctx.now.astimezone()
        series = []
        for i in range(7 * 96, -1, -1):
            t = now - dt.timedelta(minutes=15 * i)
            series.append((t.isoformat(), 412 + 85 * math.sin(i / 180) + 12 * math.sin(i / 25)))
        return {"name": "KÖLN", "water": "RHEIN", "unit": "cm", "series": series, "mw": 380, "hsw": 830,
                "current": {"value": series[-1][1], "timestamp": series[-1][0], "stateMnwMhw": "normal"}}

    def render(self, ctx, data=None):
        data = data or self.fetch(ctx)
        if data is None:
            return ctx.message(ctx.t("Choose a gauge", "Pegel auswählen"),
                               ctx.t("Search for a station under Plugins → Water Level.",
                                     "Unter Plugins → Pegelstand eine Messstelle suchen."))
        img, d = ctx.canvas()
        ctx.header(d, data["name"].title(), data["water"].title())
        cur = data["current"] or {}
        val = cur.get("value")
        unit = data["unit"]
        series = [(dt.datetime.fromisoformat(t), v) for t, v in data["series"]]
        if val is None and series:
            val = series[-1][1]
        big = gfx.font("serif-bold", 76)
        txt = f"{round(val)} {unit}" if val is not None else "–"
        d.text((ctx.W - 40 - gfx.text_w(d, txt, big), 22), txt, font=big, fill=ctx.BLUE)

        # trend over the last 3 hours
        if len(series) > 12:
            diff = series[-1][1] - series[-13][1]
            arrow = "↗" if diff > 2 else "↘" if diff < -2 else "→"
            word = ctx.t("rising", "steigend") if diff > 2 else ctx.t("falling", "fallend") if diff < -2 else ctx.t("steady", "gleichbleibend")
            st = STATE.get(cur.get("stateMnwMhw", ""), None)
            line = f"{arrow} {word}" + (f" · {ctx.t('level', 'Stand')} {ctx.t(*st)}" if st else "")
            f = gfx.font("sans", 20)
            d.text((ctx.W - 40 - gfx.text_w(d, line, f), 110), line, font=f,
                   fill=ctx.RED if cur.get("stateMnwMhw") == "high" else ctx.BLACK)

        if len(series) >= 2:
            gx, gy, gw, gh = 70, 170, ctx.W - 110, 240
            vals = [v for _, v in series]
            lo, hi = min(vals), max(vals)
            for ref in (data.get("mw"),):
                if ref:
                    lo, hi = min(lo, ref), max(hi, ref)
            pad = max((hi - lo) * 0.12, 5)
            lo, hi = lo - pad, hi + pad
            t0, t1 = series[0][0], series[-1][0]
            span = (t1 - t0).total_seconds() or 1
            X = lambda t: gx + (t - t0).total_seconds() / span * gw
            Y = lambda v: gy + gh - (v - lo) / (hi - lo) * gh
            pts = [(X(t), Y(v)) for t, v in series]
            d.line(pts, fill=ctx.BLUE, width=3)
            if data.get("mw") and lo < data["mw"] < hi:
                y = Y(data["mw"])
                for xx in range(gx, gx + gw, 10):
                    d.line((xx, y, xx + 5, y), fill=ctx.BLACK, width=1)
                d.text((gx + gw - 140, y - 20), ctx.t("mean water (MW)", "Mittelwasser (MW)"), font=gfx.font("sans", 13), fill=ctx.BLACK)
            d.line((gx, gy + gh, gx + gw, gy + gh), fill=ctx.BLACK, width=2)
            for k in range(3):
                v = lo + (hi - lo) * (k + 0.5) / 3
                d.text((gx - 58, Y(v) - 8), f"{round(v)} {unit}", font=gfx.font("sans", 12), fill=ctx.BLACK)
            day = t0.replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=1)
            while day < t1:
                x = X(day)
                d.line((x, gy + gh, x, gy + gh + 6), fill=ctx.BLACK, width=1)
                ctx.text_center(d, ctx.date(day.date(), "short"), gfx.font("sans", 12), int(x), gy + gh + 8)
                day += dt.timedelta(days=1)
        ctx.footer(d, ctx.t("Source: PEGELONLINE (WSV) · {t}", "Quelle: PEGELONLINE (WSV) · Stand {t}", t=f"{ctx.now:%H:%M}"))
        return img
