# warnings – `WeatherWarnings.view(ctx, data)`

Sample values: `plugin.sample(ctx)`, language `de`, 10 Nov 2026 13:37. The hook is only called with at
least one active alert; "no warnings" stays the regular screen. The top-level fields describe the most
severe alert (`alerts[0]`).

Alert fields (top level and every entry of `alerts`):

| field | type | meaning | sample |
|---|---|---|---|
| `severity` | str | `"minor"`, `"moderate"`, `"severe"`, `"extreme"` | `"moderate"` |
| `level` | int | 1–4 | `2` |
| `level_text` | str | translated name of the level | `"Markantes Wetter"` |
| `color` | str | `"yellow"` for level 1, else `"red"` | `"red"` |
| `event` | str | what is warned of (German or English, else English) | `"Sturmböen"` |
| `headline` | str | official headline, may be `""` | `"Amtliche WARNUNG vor STURMBÖEN"` |
| `description` | str | full text | `"Es treten Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 40 kn, Bft 9) aus westlicher Richtung auf."` |
| `instruction` | str | official advice, `""` if none | `""` |
| `onset`, `expires` | aware `datetime` or `None` | local time | 13:37 today, 22:37 today |
| `onset_text`, `expires_text` | str | weekday + time, `""` if unknown | `"Di 13:37"`, `"Di 22:37"` |
| `span` | str | as on the regular screen (end without weekday on the same day), `""` if unknown | `"Di 13:37 bis 22:37 Uhr"` |
| `active` | bool | onset reached | `True` |
| `progress` | float or `None` | position of now between onset (0) and expires (1) – the `now` mark of a timeline | `0.0` |

Top level only:

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | translated screen title | `"Wetterwarnungen"` |
| `place` | str | place the warning is for | `"Berlin"` |
| `place_span` | str | `place · span` | `"Berlin · Di 13:37 bis 22:37 Uhr"` |
| `levels` | int | number of levels | `4` |
| `level_names` | list of 4 str | translated names of level 1…4 | `["Wetterwarnung", "Markantes Wetter", "Unwetterwarnung", "Extremes Unwetter"]` |
| `alerts` | list of dict | all active alerts, most severe first | 1 entry |
| `count` | int | `len(alerts)` | `1` |
| `more` | list of str | `event` of alerts 2–4 | `[]` |
| `more_text` | str | translated "Also: …", `""` if none | `""` (e.g. `"Außerdem: Frost, Glätte"`) |
| `source` | str | | `"Deutscher Wetterdienst"` |
| `updated` | str | time of this rendering | `"13:37"` |
| `footer` | str | translated source line of the regular screen | `"Deutscher Wetterdienst über Bright Sky · Stand 13:37"` |
| `now` | `datetime` | | |
| `today` | `date` | | `date(2026, 11, 10)` |
| `date_text` | str | | `"Dienstag, 10. November"` |
| `weekday_short` | str | | `"Di"` |

Helper in `inkyframe.plugins.warnings`: `triangle(d, x, y, s, fill, outline)` – the warning triangle with
exclamation mark on a PIL `ImageDraw` (width `s`, height 0.88·s, RGB tuples).

Not available (mockups show it): wind speed, Beaufort and wind direction as separate values (they only occur
inside `description`, and only for wind warnings); the mockups' household tips are layout texts –
`instruction` is the only official advice.
