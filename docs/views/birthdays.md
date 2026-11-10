# birthdays – `Birthdays.view(ctx, data)`

`data` = list of `{"name", "month", "day", "year" (or None)}`. Samples: `plugin.sample()` on 2026-11-10, en / de.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | screen title | `"Birthdays"` / `"Geburtstage"` |
| `subtitle` | str | | `"coming up"` / `"demnächst"` |
| `place` | str | configured location name (may be `""`) | `"Berlin"` |
| `today` | date | | `date(2026, 11, 10)` |
| `date_long` / `date_short` | str | today | `"Tuesday, November 10"` / `"Nov 10"` (de `"Dienstag, 10. November"` / `"10.11."`) |
| `count` | int | number of people | `5` |
| `people` | list of person | **all** birthdays, next one first | 5 items |
| `first` | person | `people[0]` – the big box of the regular screen | Anna |
| `others` | list of person | `people[1:5]` – the rows of the regular screen | Grandpa, Ben, Clara, Mia |
| `festive` | bool | someone has their birthday today | `False` |
| `celebrants` | list of person | the people with `days == 0` | `[]` |
| `festive_title` | str | | `"Happy birthday"` / `"Alles Gute zum Geburtstag"` |
| `festive_names` | str | `""` if not festive | e.g. `"Anna & Ben!"` |
| `festive_line` | str | one with known age: `"turns 38"`; several: `"Anna: 38, Ben: 40"`; else `""` | `""` |

person:

| field | type | meaning | sample (first) |
|---|---|---|---|
| `name` | str | | `"Anna"` |
| `days` | int | days until the birthday (0 = today) | `3` |
| `date` | date | next birthday | `date(2026, 11, 13)` |
| `year` | int \| None | year of birth if known | `1988` |
| `date_long` | str | | `"Friday, November 13"` / `"Freitag, 13. November"` |
| `date_short` | str | | `"Nov 13"` / `"13.11."` |
| `weekday` | str | | `"Friday"` / `"Freitag"` |
| `day` / `month` | int / str | | `13` / `"November"` |
| `age` | int \| None | age they turn | `38` |
| `age_text` | str | `""` without year (Ben) | `"turns 38"` / `"wird 38"` |
| `when` | str | `"Today"`, `"tomorrow"` or | `"in 3 days"` / `"in 3 Tagen"` |
| `when_short` | str | | `"in 3 d"` / `"in 3 T."` |

Sample rows: Anna 3 d (38) · Grandpa 11 d (80) · Ben 26 d (no year) · Clara 40 d (7) · Mia 58 d (32).

**Festive day:** the hook is called *before* the regular festive screen (confetti, "Happy birthday", names).
A layout gets `festive=True` and must either draw its own festive version from `celebrants` /
`festive_*`, or `return None` to let the plugin draw the regular festive screen.

Timeline (Blueprint "Zeitachse 60 Tage"): x = `days / 60` for people with `days <= 60`; `now` is x = 0.

Not available: per-person colours (the regular screen only uses the design accent for the big number),
photos, relationship. Names are shown as entered (the mockups' "Opa" is "Grandpa" in the sample).
