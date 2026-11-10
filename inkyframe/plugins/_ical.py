"""Minimal iCalendar reader (no dependency): VEVENT DTSTART + SUMMARY, yearly RRULE."""
import datetime as dt
import re


def _unfold(text):
    return re.sub(r"\r?\n[ \t]", "", text).splitlines()


def _unescape(s):
    return (s.replace(r"\n", " ").replace(r"\,", ",").replace(r"\;", ";")
             .replace("\\\\", "\\").strip())


def _date(value):
    m = re.match(r"(\d{4})(\d{2})(\d{2})", value)
    return dt.date(int(m[1]), int(m[2]), int(m[3])) if m else None


def parse(text):
    """Return [{"date": date, "summary": str, "yearly": bool}] for every VEVENT."""
    events, cur = [], None
    for line in _unfold(text):
        if line == "BEGIN:VEVENT":
            cur = {"summary": "", "date": None, "yearly": False}
        elif line == "END:VEVENT" and cur is not None:
            if cur["date"]:
                events.append(cur)
            cur = None
        elif cur is not None and ":" in line:
            key, _, value = line.partition(":")
            name = key.split(";")[0].upper()
            if name == "DTSTART":
                cur["date"] = _date(value)
            elif name == "SUMMARY":
                cur["summary"] = _unescape(value)
            elif name == "RRULE" and "FREQ=YEARLY" in value.upper():
                cur["yearly"] = True
    return events


def upcoming(events, start, days):
    """Expand yearly events and return (date, summary) within [start, start+days), sorted."""
    end = start + dt.timedelta(days=days)
    out = []
    for e in events:
        d = e["date"]
        if e["yearly"]:
            for y in (start.year, start.year + 1):
                try:
                    cand = d.replace(year=y)
                except ValueError:          # 29 Feb
                    cand = dt.date(y, 3, 1)
                if start <= cand < end:
                    out.append((cand, e["summary"]))
        elif start <= d < end:
            out.append((d, e["summary"]))
    return sorted(out)


def fetch_text(url, ttl=6 * 3600):
    from inkyframe import gfx
    return gfx.get_text(re.sub(r"^webcal://", "https://", url.strip()), ttl=ttl)
