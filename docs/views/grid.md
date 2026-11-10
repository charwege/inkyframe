# View: `grid` (Grid Signal / Stromampel)

`GridSignal.view(ctx, data)` in `inkyframe/plugins/grid.py`. Samples: `plugin.sample()`, English, 13:37.
Signal values: `2` green, `1` yellow, `0` red, `-1` red because of grid congestion.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | screen title | `"Grid signal"` |
| `subtitle` | str | | `"Share of renewables in electricity consumption"` |
| `signal` | int or None | signal right now (None: no data) | `2` |
| `color` | str or None | its colour name: green, yellow, red | `"green"` |
| `signal_name` | str | translated name (`"red · grid congestion"` for −1) | `"green"` |
| `congestion` | bool | `signal == -1` | `False` |
| `share` | int or None | renewable share now, percent (can exceed 100) | `109` |
| `share_text` | str | | `"109 %"` |
| `now_label` | str | | `"now"` |
| `lights` | list[3] of dict | traffic light top → bottom: `{"color": "red"/"yellow"/"green", "on": bool}` | green on |
| `shares` | list[96] of float or None | today's share per quarter hour (index 0 = 00:00), None = no value | `[40.0, 42.8, 45.6, …]` |
| `signals` | list[96] of int or None | signal per quarter hour | `[0, 0, 0, 0, 1, …]` |
| `colors` | list[96] of str or None | colour name per quarter hour (the regular chart's bar colours) | `["red", …, "yellow", …]` |
| `hours` | list[24] of dict | per hour: `{"hour": 0…23, "share": int or None (average), "signal": lowest signal of the hour or None, "color": str or None}` | `{"hour": 0, "share": 44, "signal": 0, "color": "red"}` |
| `segments` | list of dict | runs of one colour over today, in order: `{"start": 0.0, "end": 1.0}` (hours as float, end ≤ 24), `"from": "00:00", "to": "01:00"`, `"signal"`, `"color"`, `"name"` (translated), `"now": bool` (contains the current time) | first: red 00:00–01:00 |
| `scale_max` | float | top of the regular chart's scale: max(110, highest share) | `110` |
| `share_min`, `share_max` | int or None | lowest / highest share today | `20`, `109` |
| `now` | datetime (local, tz-aware) | | |
| `time` | str | | `"13:37"` |
| `now_pos` | float | position of now in the day, 0…1 | `0.567` |
| `now_index` | int | index of the current quarter hour in the series | `54` |
| `best` | dict or None | best 3-hour window (rest of today, else tomorrow): `{"day": "today"/"tomorrow", "time": "13:45", "to": "16:45", "start": 13.75, "end": 16.75, "avg": 94}` | see left |
| `best_text` | str | the regular screen's sentence, `""` without window | `"Best 3 hours today: from 13:45 (avg 94 %)"` |
| `source` | str | credit line (data is CC BY 4.0 – keep it visible) | `"Source: Energy-Charts / Fraunhofer ISE · 13:37"` |
| `country` | str | setting, upper case | `"DE"` |
| `postal_code` | str | setting, may be `""` | `""` |
| `place` | str | name of the frame's location (not the grid region; may be `""`) | `"Berlin"` |
| `today`, `date` | date, str | | `"November 10, 2026"` |

## Helpers

- `grid.best_window(points, start, end, hours=3)` – as used for `best`.
- `grid.SIG` – signal → ((English, German name), RGB colour).

## Shown in mockups, not available

The mockups show a different kind of traffic light (grid *operation* state). The plugin knows the renewable
share and the Energy-Charts colour only:
- state texts such as "normaler Netzbetrieb", "Strom sparen", "Verbrauch verschieben" and the advice line
  "Jetzt waschen, laden, spülen" – not in the data; the plugin's own words are just the colour names
  (`signal_name`, `segments[].name`). A layout that wants wording per colour must bring its own texts.
- a region name such as "Baden-Württemberg" – only `country` / `postal_code`.
- What the plugin has instead: `share`, the share curve (`shares`) and `best`.
