"""Grid traffic light: renewable share in the power grid (Energy-Charts, Fraunhofer ISE, CC BY 4.0)."""
import datetime as dt
import math

from inkyframe import gfx
from inkyframe.gfx import BLACK, GREEN, RED, WHITE, YELLOW
from inkyframe.plugin import Plugin, Setting

SIG = {2: (("green", "grün"), GREEN), 1: (("yellow", "gelb"), YELLOW), 0: (("red", "rot"), RED),
       -1: (("red · grid congestion", "rot · Netzengpass"), RED)}


def best_window(points, start, end, hours=3):
    """Window with the highest average share between start and end."""
    pts = [p for p in points if start <= p[0] < end]
    n, best = hours * 4, None
    for i in range(0, max(len(pts) - n + 1, 0)):
        avg = sum(p[1] for p in pts[i:i + n]) / n
        if best is None or avg > best[1]:
            best = (pts[i][0], avg)
    return best


class GridSignal(Plugin):
    id = "grid"
    name = {"en": "Grid Signal", "de": "Stromampel"}
    icon = "⚡"
    description = "Share of renewables in the grid today, with traffic light and best 3-hour window."
    author = "inkyframe"
    settings = [
        Setting("country", "text", "Country code", default="de", help="e.g. de, at, fr – see api.energy-charts.info"),
        Setting("postal_code", "text", "Postal code (optional)", default="",
                help="Germany only: includes regional grid congestion."),
        Setting("refresh_minutes", "number", "Refresh every (min)", default=60, min=15, max=240),
    ]

    def fetch(self, ctx):
        params = {"country": ctx.settings.get("country") or "de"}
        if str(ctx.settings.get("postal_code", "")).strip():
            params["postal_code"] = str(ctx.settings["postal_code"]).strip()
        return ctx.fetch_json("https://api.energy-charts.info/signal", ttl=30 * 60, params=params)

    def sample(self, ctx):
        base = ctx.now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone()
        ts = [int((base + dt.timedelta(minutes=15 * i)).timestamp()) for i in range(96)]
        share = [40 + 50 * max(0, math.sin((i - 28) / 96 * 2 * math.pi)) + 20 * math.sin(i / 7) for i in range(96)]
        return {"unix_seconds": ts, "share": share,
                "signal": [2 if s > 75 else (1 if s > 50 else 0) for s in share]}

    def render(self, ctx, data=None):
        now = ctx.now.astimezone()
        data = data or self.fetch(ctx)
        pts = [(dt.datetime.fromtimestamp(t).astimezone(), s or 0, g if g is not None else 0)
               for t, s, g in zip(data["unix_seconds"], data["share"], data["signal"])]
        img, d = ctx.canvas()
        today0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_pts = [p for p in pts if today0 <= p[0] < today0 + dt.timedelta(days=1)]
        cur = min(pts, key=lambda p: abs((p[0] - now).total_seconds())) if pts else None

        ctx.header(d, ctx.t("Grid signal", "Stromampel"), ctx.t("Share of renewables in electricity consumption",
                                                                "Anteil erneuerbarer Energien am Verbrauch"))
        lx, ly = 700, 34
        d.rounded_rectangle((lx, ly, lx + 60, ly + 160), radius=14, fill=BLACK)
        active = cur[2] if cur else None
        for i, (sig, col) in enumerate(((0, RED), (1, YELLOW), (2, GREEN))):
            cy = ly + 28 + i * 52
            on = (active == sig) or (sig == 0 and active == -1)
            d.ellipse((lx + 9, cy - 21, lx + 51, cy + 21), fill=col if on else BLACK, outline=WHITE, width=2)

        if cur:
            (en, de), col = SIG.get(cur[2], (("?", "?"), BLACK))
            name = ctx.t(en, de)
            vf = gfx.font("serif-bold", 72)
            val = f"{round(cur[1])} %"
            d.text((40, 108), val, font=vf, fill=BLACK)
            lx2 = 40 + gfx.text_w(d, val, vf) + 28
            d.text((lx2, 118), ctx.t("now", "jetzt"), font=gfx.font("sans", 22), fill=BLACK)
            nf = gfx.font("sans-bold", 30)
            d.text((lx2, 144), name, font=nf, fill=RED if col == RED else BLACK)
            if col in (GREEN, YELLOW):
                d.rectangle((lx2, 182, lx2 + gfx.text_w(d, name, nf), 188), fill=col)

        gx, gy, gw, gh = 60, 250, ctx.W - 100, 150
        if day_pts:
            bw = gw / 96
            top = max(110, max(p[1] for p in day_pts))
            for p in day_pts:
                i = (p[0].hour * 60 + p[0].minute) // 15
                bh = gh * min(p[1], top) / top
                d.rectangle((gx + i * bw, gy + gh - bh, gx + (i + 1) * bw - 1, gy + gh),
                            fill=SIG.get(p[2], (None, BLACK))[1])
            y100 = gy + gh - gh * 100 / top
            for xx in range(gx, gx + gw, 8):
                d.point((xx, y100), fill=BLACK)
            d.text((gx - 44, y100 - 9), "100 %", font=gfx.font("sans", 13), fill=BLACK)
            d.line((gx, gy + gh, gx + gw, gy + gh), fill=BLACK, width=2)
            for hh in (0, 6, 12, 18, 24):
                gfx.text_center(d, f"{hh:02d}", gfx.font("sans", 14), int(gx + hh * 4 * bw), gy + gh + 6)
            nx = gx + (now.hour * 60 + now.minute) / 15 * bw
            d.line((nx, gy - 6, nx, gy + gh), fill=BLACK, width=2)
            d.polygon([(nx - 6, gy - 12), (nx + 6, gy - 12), (nx, gy - 4)], fill=BLACK)

        f = gfx.font("sans", 20)
        best = best_window(pts, now, today0 + dt.timedelta(days=1))
        tomorrow = best_window(pts, today0 + dt.timedelta(days=1), today0 + dt.timedelta(days=2))
        if best:
            d.text((40, 206), ctx.t("Best 3 hours today: from {t} (avg {p} %)", "Beste 3 Stunden heute: ab {t} Uhr (Ø {p} %)",
                                    t=f"{best[0]:%H:%M}", p=round(best[1])), font=f, fill=BLACK)
        elif tomorrow:
            d.text((40, 206), ctx.t("Best 3 hours tomorrow: from {t} (avg {p} %)", "Beste 3 Stunden morgen: ab {t} Uhr (Ø {p} %)",
                                    t=f"{tomorrow[0]:%H:%M}", p=round(tomorrow[1])), font=f, fill=BLACK)
        d.text((40, ctx.H - 32), ctx.t("Source: Energy-Charts / Fraunhofer ISE · {t}", "Quelle: Energy-Charts / Fraunhofer ISE · Stand {t}",
                                       t=f"{now:%H:%M}"), font=gfx.font("sans", 13), fill=BLACK)
        return img
