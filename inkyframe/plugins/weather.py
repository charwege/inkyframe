"""Weather & calendar – Open-Meteo (no API key needed)."""
import calendar as _cal
import math

from inkyframe import gfx
from inkyframe.gfx import BLACK, BLUE, RED, WHITE, YELLOW
from inkyframe.plugin import Plugin, Setting

from . import _calendar as C

# WMO weather codes -> (English, German, icon)
WMO = {
    0: ("Clear", "Klar", "sun"), 1: ("Mainly clear", "Überwiegend klar", "sun"),
    2: ("Partly cloudy", "Teils bewölkt", "part"), 3: ("Overcast", "Bedeckt", "cloud"),
    45: ("Fog", "Nebel", "fog"), 48: ("Rime fog", "Reifnebel", "fog"),
    51: ("Light drizzle", "Leichter Niesel", "rain"), 53: ("Drizzle", "Nieselregen", "rain"),
    55: ("Heavy drizzle", "Starker Niesel", "rain"), 56: ("Freezing drizzle", "Gefrierender Niesel", "rain"),
    57: ("Freezing drizzle", "Gefrierender Niesel", "rain"), 61: ("Light rain", "Leichter Regen", "rain"),
    63: ("Rain", "Regen", "rain"), 65: ("Heavy rain", "Starker Regen", "rain"),
    66: ("Freezing rain", "Gefrierender Regen", "rain"), 67: ("Freezing rain", "Gefrierender Regen", "rain"),
    71: ("Light snow", "Leichter Schnee", "snow"), 73: ("Snow", "Schnee", "snow"),
    75: ("Heavy snow", "Starker Schnee", "snow"), 77: ("Snow grains", "Schneegriesel", "snow"),
    80: ("Showers", "Regenschauer", "rain"), 81: ("Showers", "Regenschauer", "rain"),
    82: ("Violent showers", "Heftige Schauer", "rain"), 85: ("Snow showers", "Schneeschauer", "snow"),
    86: ("Snow showers", "Schneeschauer", "snow"), 95: ("Thunderstorm", "Gewitter", "storm"),
    96: ("Thunderstorm, hail", "Gewitter, Hagel", "storm"), 99: ("Thunderstorm, hail", "Gewitter, Hagel", "storm"),
}


# --- weather icons -----------------------------------------------------------
def _cloud(d, x, y, s, fill=WHITE):
    d.ellipse((x, y + s * .35, x + s * .55, y + s * .85), fill=fill, outline=BLACK, width=3)
    d.ellipse((x + s * .25, y + s * .1, x + s * .8, y + s * .7), fill=fill, outline=BLACK, width=3)
    d.ellipse((x + s * .5, y + s * .35, x + s, y + s * .85), fill=fill, outline=BLACK, width=3)
    d.rectangle((x + s * .28, y + s * .5, x + s * .78, y + s * .83), fill=fill)
    d.line((x + s * .25, y + s * .85, x + s * .78, y + s * .85), fill=BLACK, width=3)


def _sun(d, cx, cy, r):
    for i in range(8):
        a = i * math.pi / 4
        d.line((cx + math.cos(a) * r * 1.35, cy + math.sin(a) * r * 1.35,
                cx + math.cos(a) * r * 1.85, cy + math.sin(a) * r * 1.85), fill=RED, width=4)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YELLOW, outline=RED, width=3)


def draw_icon(d, kind, x, y, s):
    if kind == "sun":
        _sun(d, x + s // 2, y + s // 2, s // 4)
    elif kind == "part":
        _sun(d, x + s * .35, y + s * .35, s // 6)
        _cloud(d, x + s * .2, y + s * .25, s * .8)
    elif kind in ("cloud", "fog"):
        _cloud(d, x, y + s * .05, s)
        if kind == "fog":
            for i in range(3):
                yy = y + s * .95 + i * 9
                d.line((x + s * .1, yy, x + s * .9, yy), fill=BLACK, width=3)
    elif kind in ("rain", "snow", "storm"):
        _cloud(d, x, y - s * .05, s)
        for i in range(4):
            xx = x + s * .2 + i * s * .18
            if kind == "snow":
                d.text((xx - 6, y + s * .82), "*", font=gfx.font("sans-bold", 26), fill=BLUE)
            else:
                d.line((xx, y + s * .85, xx - 8, y + s * 1.05), fill=BLUE, width=4)
        if kind == "storm":
            cx = x + s * .5
            d.polygon([(cx, y + s * .7), (cx - 14, y + s * 1.0), (cx, y + s * .95),
                       (cx - 8, y + s * 1.2), (cx + 16, y + s * .88), (cx + 2, y + s * .9),
                       (cx + 10, y + s * .7)], fill=YELLOW, outline=BLACK)


class Weather(Plugin):
    id = "weather"
    name = {"en": "Weather & Calendar", "de": "Wetter & Kalender"}
    icon = "☀"
    description = "Today's weather, rain chance over the day, sun times, moon phase and a month calendar."
    author = "inkyframe"
    settings = [
        Setting("refresh_minutes", "number", "Refresh every (min)", default=30, min=10, max=240),
        Setting("units", "select", "Units", default="celsius",
                options=[("celsius", "°C"), ("fahrenheit", "°F")]),
    ]

    def content_key(self, ctx):
        return f"{ctx.today}|{ctx.location}|{ctx.lang}|{ctx.settings.get('units')}"

    def fetch(self, ctx):
        loc = ctx.location
        return ctx.fetch_json("https://api.open-meteo.com/v1/forecast", ttl=20 * 60, params={
            "latitude": loc["lat"], "longitude": loc["lon"], "timezone": "auto",
            "temperature_unit": ctx.settings.get("units", "celsius"),
            "current": "temperature_2m,weather_code,apparent_temperature",
            "hourly": "temperature_2m,precipitation_probability",
            "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,weather_code",
            "forecast_days": 1,
        })

    def sample(self, ctx):
        return {
            "current": {"temperature_2m": 8.4, "weather_code": 61, "apparent_temperature": 5.9},
            "daily": {"temperature_2m_max": [10.2], "temperature_2m_min": [4.1],
                      "sunrise": [f"{ctx.today}T07:39"], "sunset": [f"{ctx.today}T16:41"]},
            "hourly": {"precipitation_probability":
                       [5, 5, 10, 10, 15, 20, 30, 45, 60, 70, 80, 75, 60, 45, 30, 20, 15, 10, 10, 5, 5, 0, 0, 0]},
        }

    def render(self, ctx, data=None):
        import datetime as dt
        data = data or self.fetch(ctx)
        from inkyframe import designs
        special = designs.weather(ctx, data)       # signature layout of the chosen studio design
        if special is not None:
            return special
        now, today, lang = ctx.now, ctx.today, ctx.lang
        W, H = ctx.W, ctx.H
        img, d = ctx.canvas()
        region = ctx.location.get("holidays", "none")

        # ---------- left column: calendar ----------
        hol = C.holidays(today.year, region, lang)
        accent = RED if C.is_special(today, region) else BLACK
        LX, LW = 28, 260
        gfx.text_center(d, C.weekday(today, lang), gfx.font("serif", 34), LX + LW // 2, 26, accent)
        gfx.text_center(d, str(today.day), gfx.font("serif-bold", 128), LX + LW // 2, 58, accent)
        gfx.text_center(d, f"{C.month(today, lang)} {today.year}", gfx.font("serif", 24), LX + LW // 2, 196)
        if today in hol:
            gfx.text_center(d, hol[today], gfx.font("serif-italic", 20), LX + LW // 2, 226, RED)

        top, cw, ch = 262, LW // 7, 24
        fsm = gfx.font("sans", 15)
        first = C.first_weekday(lang)          # Sunday in English, Monday elsewhere
        letters = C.weekday_letters(lang)
        order = [(first + i) % 7 for i in range(7)]
        for i, wd in enumerate(order):
            gfx.text_center(d, letters[wd], gfx.font("sans-bold", 14), LX + i * cw + cw // 2, top,
                            RED if wd == 6 else BLACK)
        for r, week in enumerate(_cal.Calendar(firstweekday=first).monthdatescalendar(today.year, today.month)):
            for c, day in enumerate(week):
                if day.month != today.month:
                    continue
                cx, cy = LX + c * cw + cw // 2, top + 22 + r * ch
                col = RED if C.is_special(day, region) else BLACK
                if day == today:
                    d.ellipse((cx - 13, cy - 2, cx + 13, cy + 21), fill=accent)
                    col = WHITE
                gfx.text_center(d, str(day.day), fsm, cx, cy + 1, col)

        d.line((310, 28, 310, H - 28), fill=BLACK, width=2)

        # ---------- right side: weather ----------
        RX = 336
        cur, daily, hourly = data["current"], data["daily"], data["hourly"]
        en, de, kind = WMO.get(int(cur["weather_code"]), ("", "", "cloud"))
        d.text((RX, 22), ctx.location.get("name", ""), font=gfx.font("serif-italic", 22), fill=BLACK)
        draw_icon(d, kind, RX, 64, 110)
        d.text((RX + 135, 48), f"{round(cur['temperature_2m'])}°", font=gfx.font("serif-bold", 92), fill=BLACK)
        d.text((RX + 140, 152), ctx.t(en, de), font=gfx.font("sans", 20), fill=BLACK)
        tmax, tmin = round(daily["temperature_2m_max"][0]), round(daily["temperature_2m_min"][0])
        fx = gfx.font("sans", 20)
        d.text((RX + 140, 180), f"↑ {tmax}°", font=fx, fill=RED)
        d.text((RX + 225, 180), f"↓ {tmin}°", font=fx, fill=BLUE)
        d.text((RX + 310, 180), ctx.t("feels {t}°", "gefühlt {t}°", t=round(cur["apparent_temperature"])),
               font=fx, fill=BLACK)

        sr = dt.datetime.fromisoformat(daily["sunrise"][0])
        ss = dt.datetime.fromisoformat(daily["sunset"][0])
        length = ss - sr
        hrs, mins = length.seconds // 3600, (length.seconds % 3600) // 60
        y2, f18 = 224, gfx.font("sans", 18)
        _sun(d, RX + 12, y2 + 12, 7)
        d.text((RX + 32, y2), f"{sr:%H:%M} – {ss:%H:%M}", font=f18, fill=BLACK)
        d.text((RX + 32, y2 + 24), ctx.t("Day: {h} h {m:02d} min", "Tag: {h} h {m:02d} min", h=hrs, m=mins),
               font=f18, fill=BLACK)
        ph = C.moon_phase(now)
        C.draw_moon(d, RX + 262, y2 + 22, 18, ph, YELLOW, BLACK, BLACK)
        d.text((RX + 290, y2 + 10), C.moon_name(ph, lang), font=f18, fill=BLACK)

        probs = [p if p is not None else 0 for p in hourly["precipitation_probability"][:24]]
        gx, gy, gw, gh = RX + 30, 310, W - RX - 60, 120
        d.text((RX, 282), ctx.t("Chance of rain · max {p} %", "Regenwahrscheinlichkeit · max. {p} %", p=max(probs)),
               font=gfx.font("sans-bold", 16), fill=BLACK)
        bw = gw / 24
        for i, p in enumerate(probs):
            bh = gh * p / 100
            if bh > 0:
                d.rectangle((gx + i * bw + 1, gy + gh - bh, gx + (i + 1) * bw - 2, gy + gh), fill=BLUE)
        d.line((gx, gy + gh, gx + gw, gy + gh), fill=BLACK, width=2)
        for pct in (50, 100):
            yy = gy + gh - gh * pct / 100
            for xx in range(int(gx), int(gx + gw), 8):
                d.point((xx, yy), fill=BLACK)
            d.text((gx - 30, yy - 8), f"{pct}", font=gfx.font("sans", 13), fill=BLACK)
        for hh in (0, 6, 12, 18):
            gfx.text_center(d, f"{hh:02d}", gfx.font("sans", 14), int(gx + hh * bw + bw / 2), gy + gh + 6)
        nx = gx + (now.hour + now.minute / 60) * bw
        d.line((nx, gy - 4, nx, gy + gh), fill=RED, width=2)
        d.polygon([(nx - 6, gy - 10), (nx + 6, gy - 10), (nx, gy - 2)], fill=RED)
        d.text((RX, H - 26), ctx.t("Updated {t}", "Stand {t}", t=f"{now:%H:%M}"), font=gfx.font("sans", 13), fill=BLACK)
        return img
