"""Watchlist – a few stocks, ETFs or indices with daily change and a small chart.
Data: Stooq (no key) or Alpha Vantage (free key). Prices are delayed; for information only."""
import csv
import io

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting


def parse_symbols(text):
    out = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        label, _, sym = line.partition("=")
        sym = (sym or label).strip()
        out.append((label.strip() if _ else sym.upper(), sym))
    return out[:6]


def fmt_num(v, lang):
    from ._calendar import number
    return number(v, lang)


def spark_points(values, x, y, w, h):
    """Sparkline of a series scaled into the box (x, y, w, h) – list of (px, py), lowest value at the bottom."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1
    n = max(len(values) - 1, 1)
    return [(x + i / n * w, y + h - (v - lo) / rng * h) for i, v in enumerate(values)]


class Watchlist(Plugin):
    id = "watchlist"
    name = {"en": "Watchlist", "de": "Watchlist"}
    icon = "↗"
    description = "Up to six stocks, ETFs or indices: last close, daily change and a 30-day chart."
    author = "inkyframe"
    refresh_minutes = 60
    settings = [
        Setting("symbols", "textarea", "Symbols (Label = symbol)", default="DAX = ^dax\nMSCI World = eunl.de\nApple = aapl.us",
                help="Stooq symbols: aapl.us, ^dax, eunl.de … – for Alpha Vantage: AAPL, IBM …"),
        Setting("provider", "select", "Data source", default="stooq",
                options=[("stooq", "Stooq (no key)"), ("alphavantage", "Alpha Vantage (free key)")]),
        Setting("api_key", "secret", "Alpha Vantage API key", default=""),
        Setting("days", "number", "Chart (trading days)", default=30, min=5, max=120),
    ]

    def series(self, ctx, symbol):
        if ctx.settings.get("provider") == "alphavantage":
            j = ctx.fetch_json("https://www.alphavantage.co/query", ttl=6 * 3600, params={
                "function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey": ctx.settings.get("api_key", "")})
            ts = j.get("Time Series (Daily)")
            if not ts:
                raise RuntimeError(j.get("Note") or j.get("Information") or j.get("Error Message") or "no data")
            return [(day, float(v["4. close"])) for day, v in sorted(ts.items())]
        text = ctx.fetch_text("https://stooq.com/q/d/l/", ttl=3 * 3600, params={"s": symbol.lower(), "i": "d"})
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows or "Close" not in rows[0]:
            raise RuntimeError(f"no data for {symbol}")
        return [(r["Date"], float(r["Close"])) for r in rows if r.get("Close") not in (None, "", "null")]

    def fetch(self, ctx):
        n = int(ctx.settings.get("days", 30))
        out = []
        for label, sym in parse_symbols(ctx.settings.get("symbols")):
            try:
                out.append({"label": label, "series": self.series(ctx, sym)[-(n + 1):]})
            except Exception as e:
                out.append({"label": label, "error": str(e)[:60]})
        return out

    def content_key(self, ctx):
        return f"{ctx.today}|{ctx.now.hour}|{sorted((k, v) for k, v in ctx.settings.items() if k != 'api_key')}|{ctx.lang}"

    def sample(self, ctx):
        import math
        def mk(label, base, drift, wob, last):
            s = [(str(i), base * (1 + drift * i / 30 + wob * math.sin(i / 3))) for i in range(30)]
            return {"label": label, "series": s + [("30", s[-1][1] * (1 + last / 100))]}
        return [mk("DAX", 19850, 0.03, 0.012, 0.84), mk("MSCI World", 101.4, 0.02, 0.008, 0.31),
                mk("Apple", 228.3, -0.04, 0.02, -1.12), mk("Siemens Energy", 54.2, 0.09, 0.03, 2.45)]

    def view(self, ctx, data):
        """Display-ready facts for the design layouts (docs/views/watchlist.md)."""
        days = ctx.settings.get("days", 30)
        items = []
        for it in data:
            series = it.get("series") or []
            row = {"label": it["label"], "error": it.get("error") or "", "ok": False,
                   "dates": [t for t, _ in series], "values": [v for _, v in series]}
            if not row["error"] and len(series) >= 2:
                vals = row["values"]
                last, prev, first = vals[-1], vals[-2], vals[0]
                ch = (last - prev) / prev * 100 if prev else 0
                per = (last - first) / first * 100 if first else 0
                sign = lambda p: "+" if p > 0 else ""
                row.update(
                    ok=True, last=last, prev=prev, first=first, last_date=series[-1][0],
                    last_text=fmt_num(last, ctx.lang),
                    change=ch, change_text=f"{sign(ch)}{ctx.num(ch)} %",
                    direction="up" if ch > 0 else "down" if ch < 0 else "flat",
                    color="green" if ch > 0 else "red" if ch < 0 else "black",
                    period_change=per, period_text=f"{sign(per)}{ctx.num(per)} %",
                    min=min(vals), max=max(vals))
            items.append(row)
        src = "Alpha Vantage" if ctx.settings.get("provider") == "alphavantage" else "Stooq"
        return {
            "title": "Watchlist", "name": self.display_name(ctx.lang),
            "subtitle": ctx.t("Last close · change · {n} days", "Letzter Schluss · Änderung · {n} Tage", n=days),
            "days": int(days), "count": len(items), "items": items,
            "source": src, "now_text": f"{ctx.now:%H:%M}", "today": ctx.today,
            "place": ctx.location.get("name", ""),
            "footer": ctx.t("Source: {s} · delayed · {t}", "Quelle: {s} · verzögert · Stand {t}", s=src, t=f"{ctx.now:%H:%M}"),
        }

    def render(self, ctx, data=None):
        items = data if data is not None else self.fetch(ctx)
        if not items:
            return ctx.message(ctx.t("Watchlist is empty", "Watchlist ist leer"),
                               ctx.t("Add symbols under Plugins → Watchlist.", "Symbole unter Plugins → Watchlist eintragen."))
        data = items
        from inkyframe import layouts
        v = self.view(ctx, data)
        special = layouts.render(ctx, self.id, v)
        if special is not None:
            return special
        img, d = ctx.canvas()
        y = ctx.header(d, "Watchlist", ctx.t("Last close · change · {n} days", "Letzter Schluss · Änderung · {n} Tage",
                                             n=ctx.settings.get("days", 30)))
        rh = min(70, (ctx.H - y - 40) // len(items))
        fl, fv, fc = gfx.font("sans-bold", 22), gfx.font("serif", 24), gfx.font("sans-bold", 20)
        for it in items:
            d.text((40, y + rh // 2), it["label"], font=fl, fill=ctx.BLACK, anchor="lm")
            if it.get("error"):
                d.text((300, y + rh // 2), it["error"], font=gfx.font("sans", 16), fill=ctx.RED, anchor="lm")
            elif len(it["series"]) >= 2:
                vals = [v for _, v in it["series"]]
                last, prev = vals[-1], vals[-2]
                ch = (last - prev) / prev * 100 if prev else 0
                col = ctx.GREEN if ch > 0 else ctx.RED if ch < 0 else ctx.BLACK
                d.text((440, y + rh // 2), fmt_num(last, ctx.lang), font=fv, fill=ctx.BLACK, anchor="rm")
                pct = f"{'+' if ch > 0 else ''}{ctx.num(ch)} %"
                bw = gfx.text_w(d, pct, fc) + 16
                d.rectangle((460, y + rh // 2 - 16, 460 + bw, y + rh // 2 + 16), fill=col)
                d.text((468, y + rh // 2), pct, font=fc, fill=ctx.WHITE if col != ctx.BLACK else ctx.WHITE, anchor="lm")
                # sparkline
                sx, sw, sh = 610, ctx.W - 40 - 610, rh - 22
                lo, hi = min(vals), max(vals)
                rng = (hi - lo) or 1
                pts = [(sx + i / (len(vals) - 1) * sw, y + 11 + sh - (v - lo) / rng * sh) for i, v in enumerate(vals)]
                d.line(pts, fill=ctx.BLACK, width=2)
                d.ellipse((pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4), fill=col)
            d.line((40, y + rh - 2, ctx.W - 40, y + rh - 2), fill=ctx.BLACK, width=1)
            y += rh
        src = "Alpha Vantage" if ctx.settings.get("provider") == "alphavantage" else "Stooq"
        ctx.footer(d, ctx.t("Source: {s} · delayed · {t}", "Quelle: {s} · verzögert · Stand {t}", s=src, t=f"{ctx.now:%H:%M}"))
        return img
