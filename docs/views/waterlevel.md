# waterlevel – `WaterLevel.view(ctx, data)`

`data` = result of `fetch()`: `{name, water, unit, current, series: [(iso time, value)], mw, hsw}`.
Samples: `plugin.sample()` at 2026-11-10 13:37, en / de (15-minute readings of 7 days).

| field | type | meaning | sample |
|---|---|---|---|
| `title` / `station` / `place` | str | gauge name, title-cased | `"Köln"` |
| `subtitle` / `water` | str | river, title-cased | `"Rhein"` |
| `name` | str | plugin name | `"Water Level"` / `"Pegelstand"` |
| `unit` | str | | `"cm"` |
| `value` | float \| None | current level | `412.0` |
| `value_num` / `value_text` | str | `"–"` when unknown | `"412"` / `"412 cm"` |
| `value_color` | str | colour of the big value | `"blue"` |
| `trend` | str | `"rising"`, `"falling"`, `"steady"` or `""` (≤ 12 readings) – change of the last 3 h, ±2 threshold | `"falling"` |
| `trend_text` | str | translated | `"falling"` / `"fallend"` |
| `trend_arrow` | str | `↗` `↘` `→` or `""` | `"↘"` |
| `trend_diff` | float \| None | change in the last 3 h (12 readings) | `-11.2` |
| `state` | str | `"low"`, `"normal"`, `"high"` or `""` (PEGELONLINE MNW/MHW classification) | `"normal"` |
| `state_text` | str | translated | `"normal"` |
| `high` | bool | state is high | `False` |
| `status_line` | str | line of the regular screen (`""` without trend) | `"↘ falling · level normal"` / `"↘ fallend · Stand normal"` |
| `status_color` | str | `"red"` when high, else `"black"` | `"black"` |
| `change_24h` | float \| None | last reading minus the reading 24 h earlier (None if the series is shorter) | `-35.5` |
| `change_24h_text` | str | signed, with unit (add "/ 24 h" yourself) | `"−35 cm"` |
| `times` | list[datetime] | raw series: time stamps (tz-aware), oldest first | 673 items, `2026-11-03 13:37+01:00 … 2026-11-10 13:37+01:00` |
| `values` | list[float] | raw series: levels | `[376.4, 376.9, …, 412.0]` |
| `x` | list[float] | position of each reading in the time span, 0…1 (`[]` with < 2 readings) | `[0.0, 0.0015, …, 1.0]` |
| `min` / `max` | float \| None | lowest / highest reading | `376.4` / `503.3` |
| `axis_lo` / `axis_hi` | float \| None | y range of the regular chart (min/max incl. MW, 12 % padding) | `361.2` / `518.5` |
| `day_ticks` | list of `{"x": float, "date": date, "label": str, "weekday": str}` | midnights inside the span | `{"x": 0.0618, "date": date(2026,11,4), "label": "Nov 4" / "04.11.", "weekday": "Wed" / "Mi"}` … 7 items |
| `days` | int | days requested (setting) | `7` |
| `hours` | int | hours the series really spans | `168` |
| `mw` | number \| None | reference line: mean water | `380` |
| `mw_text` | str | | `"380 cm"` |
| `mw_label` | str | | `"mean water (MW)"` / `"Mittelwasser (MW)"` |
| `hsw` | number \| None | reference line: highest navigable water level | `830` |
| `hsw_text` | str | | `"830 cm"` |
| `to_hsw` / `to_hsw_text` | float \| None / str | room up to HSW | `418.0` / `"418 cm"` |
| `refs` | list of `{"key", "value", "text"}` | the reference lines that exist | `[{"key": "MW", "value": 380, "text": "MW 380 cm"}, {"key": "HSW", "value": 830, "text": "HSW 830 cm"}]` |
| `now_text` | str | | `"13:37"` |
| `today` | date | | `date(2026, 11, 10)` |
| `source` | str | | `"PEGELONLINE (WSV)"` |
| `footer` | str | | `"Source: PEGELONLINE (WSV) · 13:37"` / `"Quelle: PEGELONLINE (WSV) · Stand 13:37"` |

The series ends at the last reading, so `now` is the right edge (`x == 1.0`). HSW usually lies far outside
`axis_lo…axis_hi` – a layout that draws the HSW line must choose its own y range (e.g. `min(min, mw) … hsw`).

Helpers in `inkyframe.plugins.waterlevel`: `trend(series)` → `(key, diff)` for a list of `(time, value)`;
`axis_range(values, mw=None)` → `(lo, hi)`.

Not available: other marks than MW and HSW (e.g. "Hochwassermarke I/II", MNW, MHW values), a forecast.
