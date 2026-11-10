"""Water level of a river gauge – PEGELONLINE (Federal Waterways and Shipping Administration, Germany).
Covers federal waterways (Rhine, Elbe, Weser, Danube, canals …); smaller rivers run by the federal
states are not included."""
import datetime as dt
import urllib.parse

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting

from . import _calendar as C

API = "https://www.pegelonline.wsv.de/webservices/rest-api/v2"
STATE = {"low": ("low", "niedrig"), "normal": ("normal", "normal"), "high": ("high", "hoch")}


def trend(series):
    """(key, change in the last 3 h) from the 15-minute series – key is "" with too little data."""
    if len(series) <= 12:
        return "", None
    diff = series[-1][1] - series[-13][1]
    return ("rising" if diff > 2 else "falling" if diff < -2 else "steady"), diff


def axis_range(values, mw=None):
    """(lo, hi) of the regular chart: min/max incl. mean water, padded by 12 % (at least 5)."""
    lo, hi = min(values), max(values)
    if mw:
        lo, hi = min(lo, mw), max(hi, mw)
    pad = max((hi - lo) * 0.12, 5)
    return lo - pad, hi + pad


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

    def view(self, ctx, data):
        """Display-ready facts for the design layouts (docs/views/waterlevel.md)."""
        cur = data.get("current") or {}
        unit = data.get("unit") or "cm"
        series = [(dt.datetime.fromisoformat(t), v) for t, v in data.get("series", [])]
        times, values = [t for t, _ in series], [v for _, v in series]
        val = cur.get("value")
        if val is None and series:
            val = values[-1]
        key, diff = trend(series)
        words = {"rising": ctx.t("rising", "steigend"), "falling": ctx.t("falling", "fallend"),
                 "steady": ctx.t("steady", "gleichbleibend"), "": ""}
        arrow = {"rising": "↗", "falling": "↘", "steady": "→", "": ""}[key]
        state = cur.get("stateMnwMhw", "") if cur.get("stateMnwMhw", "") in STATE else ""
        state_text = ctx.t(*STATE[state]) if state else ""
        line = ""
        if key:
            line = f"{arrow} {words[key]}" + (f" · {ctx.t('level', 'Stand')} {state_text}" if state else "")
        high = cur.get("stateMnwMhw") == "high"
        mw, hsw = data.get("mw"), data.get("hsw")
        signed = lambda x: f"{'+' if round(x) > 0 else '−' if round(x) < 0 else '±'}{abs(round(x))} {unit}"

        ch24 = None                                      # change against the reading 24 h before the last one
        if len(series) >= 2 and (times[-1] - times[0]) >= dt.timedelta(hours=24):
            ref = times[-1] - dt.timedelta(hours=24)
            ch24 = values[-1] - min(series, key=lambda p: abs((p[0] - ref).total_seconds()))[1]

        x, day_ticks, lo, hi = [], [], None, None
        if len(series) >= 2:
            lo, hi = axis_range(values, mw)
            t0, t1 = times[0], times[-1]
            span = (t1 - t0).total_seconds() or 1
            x = [(t - t0).total_seconds() / span for t in times]
            day = t0.replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=1)
            while day < t1:
                day_ticks.append({"x": (day - t0).total_seconds() / span, "date": day.date(),
                                  "label": ctx.date(day.date(), "short"),
                                  "weekday": C.weekday_short(day.date(), ctx.lang)})
                day += dt.timedelta(days=1)
        return {
            "title": data["name"].title(), "subtitle": data["water"].title(),
            "name": self.display_name(ctx.lang),
            "station": data["name"].title(), "water": data["water"].title(), "place": data["name"].title(),
            "unit": unit, "value": val, "value_num": str(round(val)) if val is not None else "–",
            "value_text": f"{round(val)} {unit}" if val is not None else "–", "value_color": "blue",
            "trend": key, "trend_text": words[key], "trend_arrow": arrow, "trend_diff": diff,
            "state": state, "state_text": state_text, "high": high,
            "status_line": line, "status_color": "red" if high else "black",
            "change_24h": ch24, "change_24h_text": signed(ch24) if ch24 is not None else "",
            "times": times, "values": values, "x": x,
            "min": min(values) if values else None, "max": max(values) if values else None,
            "axis_lo": lo, "axis_hi": hi, "day_ticks": day_ticks,
            "days": int(ctx.settings.get("days", 7)),
            "hours": round((times[-1] - times[0]).total_seconds() / 3600) if len(times) >= 2 else 0,
            "mw": mw, "mw_text": f"{round(mw)} {unit}" if mw else "",
            "mw_label": ctx.t("mean water (MW)", "Mittelwasser (MW)"),
            "hsw": hsw, "hsw_text": f"{round(hsw)} {unit}" if hsw else "",
            "to_hsw": hsw - val if hsw and val is not None else None,
            "to_hsw_text": f"{round(hsw - val)} {unit}" if hsw and val is not None else "",
            "refs": [{"key": k, "value": r, "text": f"{k} {round(r)} {unit}"}
                     for k, r in (("MW", mw), ("HSW", hsw)) if r],
            "now_text": f"{ctx.now:%H:%M}", "today": ctx.today,
            "source": "PEGELONLINE (WSV)",
            "footer": ctx.t("Source: PEGELONLINE (WSV) · {t}", "Quelle: PEGELONLINE (WSV) · Stand {t}", t=f"{ctx.now:%H:%M}"),
        }

    def render(self, ctx, data=None):
        data = data or self.fetch(ctx)
        if data is None:
            return ctx.message(ctx.t("Choose a gauge", "Pegel auswählen"),
                               ctx.t("Search for a station under Plugins → Water Level.",
                                     "Unter Plugins → Pegelstand eine Messstelle suchen."))
        from inkyframe import layouts
        v = self.view(ctx, data)
        special = layouts.render(ctx, self.id, v)
        if special is not None:
            return special
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
