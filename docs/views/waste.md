# waste – `Waste.view(ctx, data)`

Sample values: `plugin.sample(ctx)`, language `de`, 10 Nov 2026. The hook is only called when there is at
least one pickup in the look-ahead window (so `soon` or `rows` is filled); "not configured" and "no
collections" stay the regular screen.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | translated screen title | `"Müllabfuhr"` |
| `place` | str | name of the frame's location, may be `""` | `"Berlin"` |
| `today` | `date` | | `date(2026, 11, 10)` |
| `date_text` / `date_short` | str | today, long / short | `"Dienstag, 10. November"` / `"10.11."` |
| `weekday` / `weekday_short` | str | today | `"Dienstag"` / `"Di"` |
| `week` | int | ISO week | `46` |
| `soon` | dict or `None` | the highlighted pickup day: today if there is one, else tomorrow; `None` if neither | see below |
| `rows` | list of item | all later pickups in date order (everything except the `soon` day); the regular screen shows the first 6 | 4 items |
| `items` | list of item | every pickup incl. the `soon` ones | 6 items |
| `look_ahead` | int | setting "Look ahead (days)" | `21` |
| `empty_text` | str | translated "no collections" sentence (for an empty `rows` under `soon`) | `"Keine Abholung in den nächsten 21 Tagen"` |

item (one pickup of one bin):

| field | type | meaning | sample (`rows[0]`) |
|---|---|---|---|
| `name` | str | name from the calendar | `"Altpapier"` |
| `color` | str | bin colour name: `"black"`, `"red"`, `"yellow"`, `"green"`, `"blue"` | `"blue"` |
| `date` | `date` | | `date(2026, 11, 14)` |
| `days` | int | days from today (0 = today) | `4` |
| `weekday` / `weekday_short` | str | | `"Samstag"` / `"Sa"` |
| `date_short` / `date_long` | str | | `"14.11."` / `"Samstag, 14. November"` |
| `date_text` | str | as on the regular screen | `"Sa, 14.11."` |
| `in_text` | str | translated | `"in 4 Tagen"` |

`soon`: `date`, `days` (0 or 1), `weekday`, `weekday_short`, `date_short`, `date_long`, `date_text` as in an
item (sample: `date(2026, 11, 11)`, `1`, `"Mittwoch"`, `"Mi"`, `"11.11."`, `"Mittwoch, 11. November"`,
`"Mi, 11.11."`), plus

| field | type | meaning | sample |
|---|---|---|---|
| `label` | str | translated "Today" / "Tomorrow" | `"Morgen"` |
| `is_today` | bool | | `False` |
| `items` | list of `{name, color}` | the bins of that day | `[{"name": "Gelber Sack", "color": "yellow"}, {"name": "Restabfall", "color": "black"}]` |
| `names` | list of str | | `["Gelber Sack", "Restabfall"]` |
| `names_text` | str | joined with " + " | `"Gelber Sack + Restabfall"` |

Sample `rows`: Altpapier blue 4, Bioabfall green 8, Restabfall black 15, Gelber Sack yellow 15.
If pickups are today *and* tomorrow, `soon` is today and tomorrow's are the first `rows` (`days` 1).

Helpers in `inkyframe.plugins.waste`:
- `bin_color(name)` → colour name.
- `draw_bin(d, x, y, s, color, outline)` – the wheelie-bin icon on a PIL `ImageDraw`, `s` = height, width
  ≈ 0.72·s, `color`/`outline` are RGB tuples (`ctx.COLORS[item["color"]]`).

Not available (mockups show it): a pickup time ("bis 6:00 Uhr") and the "put the bins out tonight" hint – the
latter is a layout text; show it only when `soon` and not `soon["is_today"]`.
