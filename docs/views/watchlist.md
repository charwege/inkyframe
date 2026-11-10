# watchlist – `Watchlist.view(ctx, data)`

`data` = list of `{"label", "series": [(date str, close), …]}` or `{"label", "error"}` (up to 6).
Samples: `plugin.sample()` at 2026-11-10 13:37, en / de.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | screen title (same in all languages) | `"Watchlist"` |
| `name` | str | plugin name | `"Watchlist"` |
| `subtitle` | str | | `"Last close · change · 30 days"` / `"Letzter Schluss · Änderung · 30 Tage"` |
| `days` | int | trading days of the chart (setting) | `30` |
| `count` | int | number of items | `4` |
| `items` | list of item | in the user's order | DAX, MSCI World, Apple, Siemens Energy |
| `source` | str | `"Stooq"` or `"Alpha Vantage"` | `"Stooq"` |
| `now_text` | str | | `"13:37"` |
| `today` | date | | `date(2026, 11, 10)` |
| `place` | str | configured location name (may be `""`) | `"Berlin"` |
| `footer` | str | | `"Source: Stooq · delayed · 13:37"` / `"Quelle: Stooq · verzögert · Stand 13:37"` |

item – the first five fields always exist, the rest **only when `ok` is True**:

| field | type | meaning | sample (DAX / Apple) |
|---|---|---|---|
| `label` | str | name given by the user | `"DAX"` |
| `error` | str | fetch error, `""` if none (regular screen prints it in red) | `""` |
| `ok` | bool | no error and at least 2 closes | `True` |
| `values` | list[float] | raw closes, oldest first (days + 1 values; `[]` on error) | `[19850.0, 19947.8, …, 20539.7]` (31) |
| `dates` | list[str] | their dates as delivered (`"YYYY-MM-DD"`; sample: `"0"…"30"`) | `["0", …, "30"]` |
| `last` / `prev` / `first` | float | last close, the one before, first of the series | `20539.69` / `20368.59` / `19850.0` |
| `last_date` | str | date of the last close (raw) | `"30"` |
| `last_text` | str | last close, 2 decimals | `"20,539.69"` / `"20.539,69"` |
| `change` | float | daily change in % | `0.84` / `-1.12` |
| `change_text` | str | | `"+0.84 %"` / `"-1.12 %"` (de `"+0,84 %"`) |
| `direction` | str | `"up"`, `"down"`, `"flat"` | `"up"` / `"down"` |
| `color` | str | `"green"` up, `"red"` down, `"black"` flat (badge and end dot of the regular screen) | `"green"` / `"red"` |
| `period_change` / `period_text` | float / str | first → last of the series in % | `3.47` / `"+3.47 %"`; Apple `-5.42` |
| `min` / `max` | float | range of `values` | `19850.0` / `20562.07` |

Sample: DAX 20,539.69 +0.84 % · MSCI World 103.49 +0.31 % · Apple 215.93 −1.12 % · Siemens Energy 59.96 +2.45 %.

Helper: `inkyframe.plugins.watchlist.spark_points(values, x, y, w, h)` → list of `(px, py)` scaled into the box
(lowest value on the bottom edge); `parse_symbols`, `fmt_num(v, lang)` exist as before. The dotted "level 30 days
ago" line of the newspaper mockup is the y of `first`.

Not available: the kind of an item (index / ETF / stock – mockup "INDEX", "AKTIE"), currency, ticker symbol,
intraday prices, a weekday for the last close when the provider gives no real date (parse `last_date` defensively).
