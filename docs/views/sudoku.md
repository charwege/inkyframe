# sudoku – `Sudoku.view(ctx, data)`

`data` = `(puzzle, solution)` (two flat lists of 81 numbers). Samples: `plugin.sample()`, 2026-11-10, en / de.
The solution is deliberately **not** in the view (it is only revealed in the web app).

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | screen title (same in all languages) | `"Sudoku"` |
| `subtitle` | str | second title line | `"of the day"` / `"des Tages"` |
| `name` | str | plugin name | `"Sudoku of the Day"` / `"Sudoku des Tages"` |
| `grid` | list[9] of list[9] of int | the givens row by row, `0` = empty cell | `[[0,1,0,3,5,0,0,0,0], …]` |
| `puzzle` | list[81] of int | the same flat (index = row*9 + col) | `[0, 1, 0, …, 7]` |
| `givens` | int | number of given digits | `31` |
| `empty` | int | cells to fill (81 − givens) | `50` |
| `givens_text` | str | | `"31 givens"` / `"31 Vorgaben"` |
| `level` | str | `"easy"`, `"medium"`, `"hard"` (plugin setting) | `"medium"` |
| `level_no` | int | 1–3 (the regular screen fills that many of 3 dots) | `2` |
| `level_max` | int | always 3 | `3` |
| `level_name` | str | translated level | `"Medium"` / `"Mittel"` |
| `weekday` | str | today | `"Tuesday"` / `"Dienstag"` |
| `date` | str | today without weekday | `"November 10"` / `"10. November"` |
| `date_long` | str | today with weekday | `"Tuesday, November 10"` |
| `today` | date | | `date(2026, 11, 10)` |
| `hint` | str | | `"Solution in the web app"` / `"Lösung in der Web-App"` |
| `place` | str | configured location name (may be `""`) | `"Berlin"` |

Helper: `inkyframe.plugins.sudoku.rows(puzzle)` → 9 rows of 9 (what `grid` holds).
Block (b = 0…8) cells: `grid[b//3*3 + y][b%3*3 + x]`.

Not available: a rule text ("every row, column … contains 1–9") – a layout that wants it brings its own
translated string; the issue/sheet number of the mockups ("Nr. 314") is just the day of the year
(`today.timetuple().tm_yday`).
