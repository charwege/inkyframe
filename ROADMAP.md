# Plugin ideas & roadmap

Good starting points for contributors – open an issue if you start one so nobody duplicates work.

| Idea | Data source | Notes |
|---|---|---|
| On this day | Wikipedia feed API | 2–3 events of today's date |
| Public transport departures | e.g. HAFAS / transport.rest | refresh every 2–5 min only in the morning? |
| Photo frame | uploads from the phone | needs an upload setting type |
| Note / message | text from the web app | big, friendly typography |
| Calendar agenda | iCal URL | today + tomorrow (reuse `plugins/_ical.py`) |
| Air quality / pollen | Open-Meteo air quality | |
| Electricity price | Energy-Charts day-ahead price | complements *Grid Signal* |
| Word of the day / vocabulary | local list | language learning |
| Moon & night sky | computed | full-screen moon phase, planets |
| Home Assistant board | HA REST API | a few sensors as tiles |

## Core ideas
- **Physical buttons** (removed in 2.1, planned to return as an optional module)
- More display languages, more holiday regions
- Other Inky sizes (4.0", 13.3")
- Installing plugins from a URL in the web app
