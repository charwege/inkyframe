"""Solar power – balcony PV / rooftop output today, from OpenDTU or Home Assistant (local network)."""
import datetime as dt
import math

import requests

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


T0, T1 = 5, 22            # hours the day's curve covers
TICKS = (6, 9, 12, 15, 18, 21)


def _minutes(hm):
    return int(hm[:2]) * 60 + int(hm[3:])


class Solar(Plugin):
    id = "solar"
    name = {"en": "Solar Power", "de": "Solarstrom"}
    icon = "☼"
    description = "Current output, today's yield and the day's curve of your (balcony) PV system."
    author = "inkyframe"
    poll_minutes = 5          # records the power curve in the background
    refresh_minutes = 15
    settings = [
        Setting("source", "select", "Data source", default="opendtu",
                options=[("opendtu", "OpenDTU (Hoymiles inverters)"), ("homeassistant", "Home Assistant")]),
        Setting("host", "text", "OpenDTU address", default="", help="e.g. 192.168.178.50 or opendtu.local"),
        Setting("ha_url", "text", "Home Assistant URL", default="", help="e.g. http://homeassistant.local:8123"),
        Setting("ha_token", "secret", "Home Assistant long-lived token", default=""),
        Setting("ha_power", "text", "Power entity (W)", default="sensor.pv_power"),
        Setting("ha_energy", "text", "Energy today entity (kWh/Wh)", default="sensor.pv_energy_today"),
        Setting("peak", "number", "System peak power (Wp)", default=800, min=50, max=30000),
        Setting("price", "number", "Electricity price (ct/kWh)", default=30, min=0, max=100),
        Setting("refresh_minutes", "number", "Redraw every (min)", default=15, min=5, max=120),
    ]

    # ---------------------------------------------------------------- data
    def read(self, ctx):
        s = ctx.settings
        if s.get("source") == "homeassistant":
            if not (s.get("ha_url") and s.get("ha_token")):
                return None
            h = {"Authorization": f"Bearer {s['ha_token']}"}
            base = s["ha_url"].rstrip("/")

            def state(entity):
                r = requests.get(f"{base}/api/states/{entity}", headers=h, timeout=8)
                r.raise_for_status()
                j = r.json()
                return _num(j.get("state")), (j.get("attributes") or {}).get("unit_of_measurement", "")
            p, pu = state(s["ha_power"])
            e, eu = state(s["ha_energy"])
            if pu == "kW" and p is not None:
                p *= 1000
            if eu == "Wh" and e is not None:
                e /= 1000
            return {"power": p or 0.0, "today_kwh": e or 0.0, "total_kwh": None}
        if not s.get("host"):
            return None
        host = s["host"].strip()
        url = host if host.startswith("http") else f"http://{host}"
        j = requests.get(f"{url}/api/livedata/status", timeout=8).json()
        t = j.get("total", {})
        return {"power": _num(t.get("Power", {}).get("v")) or 0.0,
                "today_kwh": (_num(t.get("YieldDay", {}).get("v")) or 0.0) / 1000,
                "total_kwh": _num(t.get("YieldTotal", {}).get("v"))}

    def poll(self, ctx):
        v = self.read(ctx)
        if v is None:
            return
        st = ctx.load_state()
        day = ctx.today.isoformat()
        if st.get("day") != day:
            if st.get("day"):
                st.setdefault("history", {})[st["day"]] = st.get("last_kwh", 0)
            st.update(day=day, curve=[])
        st["curve"].append([ctx.now.strftime("%H:%M"), round(v["power"], 1)])
        st["last_kwh"] = v["today_kwh"]
        st["latest"] = v
        hist = st.get("history", {})
        st["history"] = dict(sorted(hist.items())[-60:])
        ctx.save_state(st)

    def content_key(self, ctx):
        return f"{ctx.today}|{ctx.lang}|{sorted((k, v) for k, v in ctx.settings.items() if k != 'ha_token')}"

    def sample(self, ctx):
        curve = []
        for m in range(6 * 60 + 30, min(ctx.now.hour * 60 + ctx.now.minute, 20 * 60), 5):
            x = (m - 6.5 * 60) / (13.5 * 60)
            cloud = 0.75 if 11 * 60 < m < 12 * 60 + 30 else 1
            curve.append([f"{m // 60:02d}:{m % 60:02d}", round(780 * math.sin(math.pi * x) ** 1.5 * cloud, 1)])
        kwh = sum(p for _, p in curve) * 5 / 60 / 1000
        return {"latest": {"power": curve[-1][1] if curve else 0, "today_kwh": kwh, "total_kwh": 1234.5},
                "curve": curve, "history": {}}

    # ---------------------------------------------------------------- view
    def view(self, ctx, data):
        """Display-ready facts for the design layouts (docs/views/solar.md)."""
        v = data["latest"]
        s = ctx.settings
        peak = float(s.get("peak", 800))
        price = float(s.get("price", 30))
        power = v.get("power") or 0
        kwh = v.get("today_kwh") or 0
        euro = kwh * price / 100
        total = v.get("total_kwh") or None
        curve = [[t, p] for t, p in data.get("curve", [])]
        watts = [p for _, p in curve]
        top = max(range(len(curve)), key=lambda i: watts[i]) if curve else None
        nm = ctx.now.hour * 60 + ctx.now.minute
        history = [{"day": k, "kwh": e} for k, e in sorted((data.get("history") or {}).items())]
        return {
            "title": ctx.t("Solar power", "Solarstrom"), "subtitle": ctx.t("Today", "Heute"),
            "place": ctx.location.get("name", ""),
            "power": power, "power_w": round(power), "power_text": f"{round(power)} W",
            "power_label": ctx.t("right now", "gerade jetzt"),
            "power_frac": min(max(power, 0), peak) / peak if peak else 0,
            "today_kwh": kwh, "today_num": ctx.num(kwh), "today_text": f"{ctx.num(kwh)} kWh",
            "saved": euro, "saved_num": ctx.num(euro), "saved_text": f"{ctx.num(euro)} €",
            "today_line": ctx.t("today · approx. {e} € saved", "heute · ca. {e} € gespart", e=ctx.num(euro)),
            "total_kwh": total, "total_num": ctx.num(total, 0) if total else "",
            "total_text": f"{ctx.num(total, 0)} kWh" if total else "",
            "total_line": ctx.t("{t} kWh in total", "{t} kWh insgesamt", t=ctx.num(total, 0)) if total else "",
            "peak": peak, "peak_text": f"{int(peak)} W", "price": price,
            "curve": curve, "times": [t for t, _ in curve], "hours": [_minutes(t) / 60 for t, _ in curve],
            "watts": watts,
            "max_w": watts[top] if curve else None, "max_text": f"{round(watts[top])} W" if curve else "",
            "max_time": curve[top][0] if curve else "",
            "t0": T0, "t1": T1, "ticks": list(TICKS), "tick_labels": [f"{h:02d}" for h in TICKS],
            "now": nm / 60, "now_text": f"{ctx.now:%H:%M}", "now_visible": T0 * 60 <= nm <= T1 * 60,
            "history": history,
            "footer": ctx.t("Updated {t}", "Stand {t}", t=f"{ctx.now:%H:%M}"),
            "today": ctx.today,
        }

    # ---------------------------------------------------------------- drawing
    def render(self, ctx, data=None):
        if data is None:
            self.poll(ctx)                      # make sure we have a fresh value
            st = ctx.load_state()
            if not st.get("latest"):
                return ctx.message(ctx.t("Solar source not set up", "Solar-Quelle nicht eingerichtet"),
                                   ctx.t("Enter your OpenDTU address or Home Assistant details under Plugins → Solar Power.",
                                         "OpenDTU-Adresse oder Home-Assistant-Daten unter Plugins → Solarstrom eintragen."))
            data = st
        from inkyframe import layouts
        v = self.view(ctx, data)
        special = layouts.render(ctx, self.id, v)
        if special is not None:
            return special
        v, curve = data["latest"], data.get("curve", [])
        peak = float(ctx.settings.get("peak", 800))
        img, d = ctx.canvas()
        ctx.header(d, ctx.t("Solar power", "Solarstrom"), ctx.t("Today", "Heute"))

        # sun icon
        cx, cy, r = ctx.W - 90, 70, 24
        for i in range(8):
            a = i * math.pi / 4
            d.line((cx + math.cos(a) * r * 1.4, cy + math.sin(a) * r * 1.4, cx + math.cos(a) * r * 1.9,
                    cy + math.sin(a) * r * 1.9), fill=ctx.RED, width=4)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ctx.YELLOW, outline=ctx.RED, width=3)

        big = gfx.font("serif-bold", 64)
        now_txt = f"{round(v['power'])} W"
        d.text((40, 112), now_txt, font=big, fill=ctx.BLACK)
        d.text((40, 186), ctx.t("right now", "gerade jetzt"), font=gfx.font("serif-italic", 18), fill=ctx.BLACK)
        x2 = 330
        kwh = v.get("today_kwh") or 0
        d.text((x2, 112), f"{ctx.num(kwh)} kWh", font=gfx.font("serif-bold", 44), fill=ctx.BLACK)
        euro = kwh * float(ctx.settings.get("price", 30)) / 100
        sub = ctx.t("today · approx. {e} € saved", "heute · ca. {e} € gespart", e=ctx.num(euro))
        d.text((x2, 166), sub, font=gfx.font("sans", 18), fill=ctx.BLACK)
        if v.get("total_kwh"):
            d.text((x2, 192), ctx.t("{t} kWh in total", "{t} kWh insgesamt", t=ctx.num(v["total_kwh"], 0)),
                   font=gfx.font("sans", 16), fill=ctx.BLACK)

        # curve 05:00–22:00
        gx, gy, gw, gh = 60, 240, ctx.W - 100, 170
        t0, t1 = 5 * 60, 22 * 60
        to_x = lambda hm: gx + (int(hm[:2]) * 60 + int(hm[3:]) - t0) / (t1 - t0) * gw
        to_y = lambda p: gy + gh - min(p, peak) / peak * gh
        pts = [(to_x(t), to_y(p)) for t, p in curve if t0 <= int(t[:2]) * 60 + int(t[3:]) <= t1]
        if len(pts) >= 2:
            d.polygon(pts + [(pts[-1][0], gy + gh), (pts[0][0], gy + gh)], fill=ctx.YELLOW)
            d.line(pts, fill=ctx.BLACK, width=2)
        for frac in (0.5, 1.0):
            yy = gy + gh - gh * frac
            for xx in range(gx, gx + gw, 8):
                d.point((xx, yy), fill=ctx.BLACK)
            d.text((gx - 52, yy - 8), f"{int(peak * frac)} W", font=gfx.font("sans", 12), fill=ctx.BLACK)
        d.line((gx, gy + gh, gx + gw, gy + gh), fill=ctx.BLACK, width=2)
        for hh in (6, 9, 12, 15, 18, 21):
            ctx.text_center(d, f"{hh:02d}", gfx.font("sans", 13), int(gx + (hh * 60 - t0) / (t1 - t0) * gw), gy + gh + 6)
        nm = ctx.now.hour * 60 + ctx.now.minute
        if t0 <= nm <= t1:
            nx = gx + (nm - t0) / (t1 - t0) * gw
            d.line((nx, gy, nx, gy + gh), fill=ctx.RED, width=2)
        ctx.footer(d, ctx.t("Updated {t}", "Stand {t}", t=f"{ctx.now:%H:%M}"))
        return img
