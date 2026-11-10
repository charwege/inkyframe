# solar – `Solar.view(ctx, data)`

`data` = plugin state `{"latest": {power, today_kwh, total_kwh}, "curve": [["HH:MM", W], …], "history": {day: kWh}}`.
Samples: `plugin.sample()` at 2026-11-10 13:37, en / de. The curve is recorded every 5 minutes and only
reaches up to *now*.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | screen title | `"Solar power"` / `"Solarstrom"` |
| `subtitle` | str | | `"Today"` / `"Heute"` |
| `place` | str | configured location name (may be `""`) | `"Berlin"` |
| `power` | float | current output in W | `776.5` |
| `power_w` | int | rounded | `776` |
| `power_text` | str | | `"776 W"` |
| `power_label` | str | | `"right now"` / `"gerade jetzt"` |
| `power_frac` | float | power / system peak, 0…1 (for gauges) | `0.97` |
| `today_kwh` | float | yield today | `2.971` |
| `today_num` / `today_text` | str | | `"2.97"` / `"2.97 kWh"` (de `"2,97 kWh"`) |
| `saved` | float | today_kwh × price, in € | `0.891` |
| `saved_num` / `saved_text` | str | | `"0.89"` / `"0.89 €"` |
| `today_line` | str | line of the regular screen | `"today · approx. 0.89 € saved"` / `"heute · ca. 0,89 € gespart"` |
| `total_kwh` | float \| None | lifetime yield (OpenDTU only; None with Home Assistant) | `1234.5` |
| `total_num` / `total_text` / `total_line` | str | `""` when unknown | `"1,234"` / `"1,234 kWh"` / `"1,234 kWh in total"` (de `"1.234 kWh insgesamt"`) |
| `peak` | float | system peak power in Wp (setting) = top of the chart | `800.0` |
| `peak_text` | str | | `"800 W"` |
| `price` | float | ct/kWh (setting) | `30.0` |
| `curve` | list of `[str, float]` | today's power curve `["HH:MM", W]`, raw | `[["06:30", 0.0], …, ["13:35", 776.5]]` (86 points) |
| `times` | list[str] | the `HH:MM` of `curve` | `["06:30", …]` |
| `hours` | list[float] | the same as decimal hours (x values) | `[6.5, 6.583, …, 13.583]` |
| `watts` | list[float] | the W of `curve` (y values; clamp to `peak` like the regular screen) | `[0.0, 2.1, …, 776.5]` |
| `max_w` | float \| None | highest value recorded today | `780.0` |
| `max_text` / `max_time` | str | `""` without curve | `"780 W"` / `"13:15"` |
| `t0`, `t1` | int | hour range of the regular chart | `5`, `22` |
| `ticks` / `tick_labels` | list[int] / list[str] | hour ticks | `[6, 9, 12, 15, 18, 21]` / `["06", "09", …]` |
| `now` | float | current time as decimal hour (the `now` line) | `13.617` |
| `now_text` | str | | `"13:37"` |
| `now_visible` | bool | now lies within t0…t1 | `True` |
| `history` | list of `{"day": "YYYY-MM-DD", "kwh": float}` | yield of up to 60 earlier days, oldest first; may be empty | `[]` |
| `footer` | str | | `"Updated 13:37"` / `"Stand 13:37"` |
| `today` | date | | `date(2026, 11, 10)` |

x of a point: `(hours[i] - t0) / (t1 - t0)`; y: `min(watts[i], peak) / peak`. Fewer than 2 points → no curve.
Module constants: `solar.T0`, `solar.T1`, `solar.TICKS`.

Not available (shown in some mockups): a forecast / expected curve for the rest of the day (dashed line),
sunrise/sunset, the kind or orientation of the system ("Balkonkraftwerk · Südseite"). "Spitze heute 800 W" can be
`max_text` (measured) or `peak_text` (system size).
