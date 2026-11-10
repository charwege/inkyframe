# View: `countdown` (Countdown)

`Countdown.view(ctx, data)` in `inkyframe/plugins/countdown.py`; `data` may be None (then title and date
come from the settings). Samples: `plugin.sample()`, English, today = 10 Nov 2026.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | plugin name | `"Countdown"` |
| `event` | str | name of the event (setting "Event") | `"Summer holidays"` |
| `days` | int | days until the event; negative = it has passed | `42` |
| `count` | int | `abs(days)` | `42` |
| `big` | str | the big figure of the regular screen (`"Today!"` on the day) | `"42"` |
| `small` | str | line above it: "days until", "day until", "days since", `""` on the day | `"days until"` |
| `state` | str | `"future"`, `"today"` or `"past"` | `"future"` |
| `weeks`, `rest_days` | int | `count` as full weeks + remaining days | `6`, `0` |
| `weekends` | int | Saturdays between today and the event | `6` |
| `target` | date | the event's date | `date(2026, 12, 22)` |
| `date` | str | long date with year (as on the regular screen) | `"December 22, 2026"` |
| `date_short` | str | | `"Dec 22"` |
| `target_weekday`, `target_month` | str | | `"Tuesday"`, `"December"` |
| `today` | date | | `date(2026, 11, 10)` |
| `today_text`, `today_short`, `today_weekday` | str | | `"November 10, 2026"`, `"Nov 10"`, `"Tuesday"` |
| `week_from`, `week_to` | int | ISO week of the earlier / later of today and event | `46`, `52` |
| `strip` | list of dict | one entry per day from the earlier to the later of today and event, both included (`count + 1` entries; `[]` if more than 366 days): `{"date": date, "day": 10, "weekday": 0…6 (Mon = 0), "weekend": bool (Sat/Sun), "special": bool (Sunday or public holiday of the configured region), "first_of_month": bool, "today": bool, "target": bool}` | 43 entries |
| `color` | str | accent colour name from the setting, `""` = use the design's accent | `""` |
| `now`, `time` | datetime, str | render time | `"13:37"` |
| `place` | str | name of the configured location (may be `""`) | `"Berlin"` |

An invalid date in the settings stays a message screen of the plugin.

## Helpers

None needed. Month names for a strip: `_calendar.month(entry["date"], ctx.lang)`.

## Shown in mockups, not available

- Sentences like "bis zu den Weihnachtsferien" / "Erster Ferientag": the plugin only has `small` + `event`
  (no article or case for the event name).
- "dreißig Werktage": working days are not counted (can be derived from `strip`: not `weekend`, not `special`).
- Progress since a start date: there is no start date, only today and the target.
