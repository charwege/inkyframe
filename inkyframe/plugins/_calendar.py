"""Shared calendar helpers: names, holidays, moon phase."""
import datetime as dt
import math

from inkyframe import i18n


def _cap(x):
    return x[:1].upper() + x[1:]


def weekday(d, lang):
    return _cap(i18n.get(lang, "WEEKDAYS")[d.weekday()])


def weekday_short(d, lang):
    return _cap(i18n.get(lang, "WEEKDAYS_SHORT")[d.weekday()])


def weekday_letters(lang):
    return i18n.get(lang, "WEEKDAY_LETTERS")


def first_weekday(lang):
    return i18n.get(lang, "FIRST_WEEKDAY") if lang in i18n.ORDER else 6


def month(d, lang):
    return _cap(i18n.get(lang, "MONTHS")[d.month - 1])


def _fields(d, lang):
    loc = i18n.locale(lang)
    return {"wd": i18n.get(lang, "WEEKDAYS")[d.weekday()], "d": d.day, "m": d.month,
            "mon": i18n.get(lang, "MONTHS")[d.month - 1], "mg": (getattr(loc, "MONTHS_GEN", None) or i18n.get(lang, "MONTHS"))[d.month - 1],
            "ms": i18n.get(lang, "MONTHS_SHORT")[d.month - 1], "y": d.year}


def long_date(d, lang, weekday=True, year=False):
    """“Tuesday, November 10” · “Dienstag, 10. November” · “mardi 10 novembre” …"""
    key = "LONG_DATE_YEAR" if year else ("LONG_DATE" if weekday else "LONG_DATE_NO_WD")
    return _cap(i18n.get(lang, key).format(**_fields(d, lang)))


def short_date(d, lang):
    """“Nov 14” · “14.11.” · “14/11” …"""
    return i18n.get(lang, "SHORT_DATE").format(**_fields(d, lang))


def number(v, lang, digits=2):
    s = f"{v:,.{digits}f}"
    dec, th = i18n.get(lang, "DECIMAL"), i18n.get(lang, "THOUSANDS")
    return s.replace(",", "\0").replace(".", dec).replace("\0", th)


def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    return dt.date(y, (h + l - 7 * m + 114) // 31, (h + l - 7 * m + 114) % 31 + 1)


# Region codes: "none", "de" (nationwide), "de-ni" (Lower Saxony). Contributions welcome!
HOLIDAY_REGIONS = [("none", "No holidays"), ("de", "Germany (nationwide)"),
                   ("de-ni", "Germany – Lower Saxony"), ("de-by", "Germany – Bavaria"),
                   ("de-nw", "Germany – North Rhine-Westphalia")]


def holidays(y, region, lang="en"):
    if not region or region == "none":
        return {}
    e, td = easter(y), dt.timedelta
    L = lambda en, de: i18n.tr(lang, en, de)
    h = {
        dt.date(y, 1, 1): L("New Year's Day", "Neujahr"),
        e - td(2): L("Good Friday", "Karfreitag"),
        e: L("Easter Sunday", "Ostersonntag"),
        e + td(1): L("Easter Monday", "Ostermontag"),
        dt.date(y, 5, 1): L("Labour Day", "Tag der Arbeit"),
        e + td(39): L("Ascension Day", "Christi Himmelfahrt"),
        e + td(49): L("Whit Sunday", "Pfingstsonntag"),
        e + td(50): L("Whit Monday", "Pfingstmontag"),
        dt.date(y, 10, 3): L("German Unity Day", "Tag der Deutschen Einheit"),
        dt.date(y, 12, 25): L("Christmas Day", "1. Weihnachtstag"),
        dt.date(y, 12, 26): L("Boxing Day", "2. Weihnachtstag"),
    }
    if region == "de-ni":
        h[dt.date(y, 10, 31)] = L("Reformation Day", "Reformationstag")
    if region in ("de-by", "de-nw"):
        h[e + td(60)] = L("Corpus Christi", "Fronleichnam")
        h[dt.date(y, 11, 1)] = L("All Saints' Day", "Allerheiligen")
    if region == "de-by":
        h[dt.date(y, 1, 6)] = L("Epiphany", "Heilige Drei Könige")
        h[dt.date(y, 8, 15)] = L("Assumption Day", "Mariä Himmelfahrt")
    return h


def is_special(day, region):
    return day.weekday() == 6 or day in holidays(day.year, region)


def moon_phase(when):
    """0 = new moon, 0.5 = full moon."""
    ref = dt.datetime(2000, 1, 6, 18, 14)
    return ((when - ref).total_seconds() / 86400 % 29.530588853) / 29.530588853


def moon_name(p, lang="en"):
    bounds = [0.03, 0.22, 0.28, 0.47, 0.53, 0.72, 0.78, 0.97]
    names = i18n.get(lang, "MOON")
    for i, b in enumerate(bounds):
        if p < b:
            return names[i]
    return names[0]


def draw_moon(d, cx, cy, r, phase, lit, dark, outline):
    """Pixel-exact moon; `dark=None` leaves the shadow transparent."""
    k = math.cos(2 * math.pi * phase)
    waxing = phase < 0.5
    for y in range(-r, r + 1):
        half = math.sqrt(max(r * r - y * y, 0))
        for x in range(-r, r + 1):
            if x * x + y * y > r * r:
                continue
            on = (x > half * k) if waxing else (x < -half * k)
            if on:
                d.point((cx + x, cy + y), fill=lit)
            elif dark is not None:
                d.point((cx + x, cy + y), fill=dark)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=outline, width=2)
