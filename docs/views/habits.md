# habits – `Habits.view(ctx, data)`

Sample values: `plugin.sample(ctx)`, language `de`, Tuesday 10 Nov 2026. The hook is only called with at
least one habit (at most 6).

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | translated screen title | `"Gewohnheiten"` |
| `today` | `date` | | `date(2026, 11, 10)` |
| `date_text` / `date_short` | str | today, long / short | `"Dienstag, 10. November"` / `"10.11."` |
| `weekday` / `weekday_short` | str | today | `"Dienstag"` / `"Di"` |
| `weekday_letters` | list of 7 str | Monday…Sunday – the rows of `grid` | `["M", "D", "M", "D", "F", "S", "S"]` |
| `day_unit` | str | translated short unit for days | `"T"` |
| `weeks` | int | columns of `grid` – always 6 | `6` |
| `days` | int | length of a habit's `days` – always 42 | `42` |
| `now` | [int, int] | today's cell in `grid`: [column, row] = [5, weekday 0–6] | `[5, 1]` |
| `start` | `date` | Monday of `grid`'s first column | `date(2026, 10, 5)` |
| `weeks_all` | int | setting "Weeks shown" = columns of `grid_all` (4–16) | `12` |
| `best` | int | longest streak ever of any habit (within the log, ≤ 400 days) | `13` |
| `best_streak` | int | longest current streak of any habit | `9` |
| `habits` | list of habit | in the owner's order | 4 entries |

habit:

| field | type | meaning | sample (`habits[0]`) |
|---|---|---|---|
| `name` | str | | `"Lesen"` |
| `color` | str | the plugin's colour of this habit: green, blue, red, black, green, blue | `"green"` |
| `streak` | int | current days in a row (today not ticked yet does not break it) | `5` |
| `streak_text` | str | as on the regular screen | `"5 T"` |
| `hot` | bool | streak ≥ 7 (regular screen prints it in the accent colour) | `False` |
| `best` | int | longest streak in the log | `13` |
| `done_today` | bool | | `True` |
| `days` | list of 42 bool | the last 42 days, oldest first, `days[-1]` = today | 33 × `True` |
| `done_count` | int | `True`s in `days` | `33` |
| `rate` | float | `done_count / 42` | `0.786` |
| `grid` | 6 lists of 7 | calendar grid of the last 6 weeks: column = week (oldest first, last = current week), row = Monday…Sunday; `True` done, `False` not done, `None` = day after today (draw nothing) | last column `[True, True, None, None, None, None, None]` |
| `grid_all` | `weeks_all` lists of 7 | same for the configured number of weeks (regular screen) | 12 columns |

Sample habits: Lesen green 5 (best 13, 33/42), Sport blue 4 (best 9, 27/42), Kein Handy ab 22 Uhr red 5
(best 7, 24/42), Meditieren black 9 (best 9, 19/42).

`grid` holds 36–42 real days depending on the weekday; `days` always 42 (use it for "x of 42 days").

Helpers in `inkyframe.plugins.habits`: `week_grid(done_dates, today, weeks)`, `streak(done_dates, today)`,
`best_streak(done_dates)` (`done_dates` = set of ISO date strings), `PALETTE`.

Not available (mockups show it): per-habit notes/tags (Deco "note", Pixel "tag") – the plugin only knows
the name and the ticks.
