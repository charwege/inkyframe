# View: `wordclock` (Word Clock)

`WordClock.view(ctx, data=None)` in `inkyframe/plugins/wordclock.py` (needs no data). Samples: English
grid, 10 Nov 2026 13:37. Cells are `(row, col)` with row 0 = top line, col 0 = left letter.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | plugin name | `"Word Clock"` |
| `grid_lang` | str | language of the letter grid: `"de"` or `"en"` (other display languages use the English grid) | `"en"` |
| `grid` | list[10] of str (11 letters each) | the letter grid | `["ITLISASAMPM", "ACQUARTERDC", …]` |
| `rows`, `cols` | int | | `10`, `11` |
| `time_cells` | sorted list of (row, col) | lit cells of the time words ("IT IS … PAST/TO", "ES IST … UHR") | `[(0,0), (0,1), (0,3), …]` |
| `hour_cells` | sorted list of (row, col) | lit cells of the hour word (the regular screen colours it separately) | `[(6,8), (6,9), (6,10)]` |
| `lit` | sorted list of (row, col) | both together | |
| `words` | list of dict | lit words in reading order: `{"text": "TWENTY", "row": 2, "col": 0, "len": 6, "hour": False}` | IT, IS, TWENTY, FIVE, TO, TWO |
| `phrase` | str | the sentence the grid shows | `"It is twenty five to two"` (de: `"Es ist fünf nach halb zwei"`) |
| `phrase_time` | str | without "It is" / "Es ist" | `"twenty five to two"` |
| `hour_word` | str | | `"TWO"` |
| `hour` | int | 0…23 | `13` |
| `minute` | int | minute rounded down to 5 – what the grid shows | `35` |
| `time` | str | digital time of the grid (5-minute step) | `"13:35"` |
| `style` | str | setting: dark, dark-dim, dark-clean, light | `"dark"` |
| `bg` | str | background colour name of the style | `"black"` |
| `off` | str or None | unlit letters: colour name, `"dim"` (finely dotted ≈ grey) or None (hidden) | `"white"` |
| `on`, `hour_color` | str | colour names of time words / hour word | `"red"`, `"red"` |
| `now`, `today` | datetime, date | render time (exact minute in `now`) | |
| `weekday`, `day`, `month`, `year` | str, int, str, int | date panel | `"Tuesday"`, `10`, `"November"`, `2026` |
| `date` | str | | `"November 10, 2026"` |
| `week`, `day_of_year` | int | ISO week, day of the year | `46`, `314` |
| `special` | bool | Sunday or public holiday (regular screen prints the day in the accent colour) | `False` |
| `phase` | float | moon phase 0…1 (0 new, 0.5 full) | `0.022` |
| `moon` | str | translated phase name | `"New moon"` |
| `place` | str | name of the configured location (may be `""`) | `"Berlin"` |

The grid language follows the setting, so in a French display `phrase` and `grid` are English while
`weekday`, `month`, `moon` are French.

## Helpers

- `wordclock.words_for(t, lang)` → `(time-word cells, hour-word cells)` as two sets of `(row, col)`;
  `wordclock.lit_words(t, lang)` → the `words` list.
- Moon drawing: `_calendar.draw_moon(d, cx, cy, r, v["phase"], lit, dark, outline)` (`from inkyframe.plugins import _calendar`).
- Dial hands as on the regular screen: hour hand at `(hour % 12 + minute / 60) * 30°`, minute hand at
  `minute * 6°`, measured clockwise from 12.

## Shown in mockups, not available

- "+2 Minuten" / the exact time "13:37": the clock is redrawn every 5 minutes only (e-ink refresh), so the
  extra minutes would be stale; `time` and `minute` are the 5-minute step. (`now` still holds the exact
  render time.)
- "erste Sichel am Donnerstag" (date of the next moon phase) – not computed.
