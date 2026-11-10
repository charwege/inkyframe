# View: `chess` (Chess Puzzle)

`ChessPuzzle.view(ctx, data)` in `inkyframe/plugins/chess_puzzle.py`. Samples: `plugin.sample()`, English, 10 Nov 2026 13:37.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | screen title | `"Puzzle of the day"` |
| `title_a`, `title_b` | str | the two halves of the title as the regular screen sets them | `"Puzzle"`, `"of the day"` |
| `name` | str | plugin name | `"Chess Puzzle"` |
| `id` | str | Lichess puzzle id | `"demo1"` |
| `url` | str | address of the puzzle (no scheme) | `"lichess.org/training/demo1"` |
| `source` | str | | `"Lichess"` |
| `fen` | str | full FEN of the position | `"r1bqk2r/pppp1ppp/… b KQkq - 0 4"` |
| `board` | list[8] of list[8] of str | pieces **as shown on screen**: `board[0]` is the top row, `board[r][0]` the left square. FEN letters, upper case = white, lower case = black, `""` = empty. Already turned so the side to move sits at the bottom | `board[0] == ["R","","","K","Q","B","N","R"]` |
| `flip` | bool | True = black at the bottom (black to move) | `True` |
| `files` | list[8] of str | file letters left → right, matching `board` | `["h","g","f","e","d","c","b","a"]` |
| `ranks` | list[8] of str | rank digits top → bottom, matching `board` | `["1","2",…,"8"]` |
| `dark` | str | colour name of the dark squares (setting): green, blue, black, red | `"green"` |
| `show_coords` | bool | setting "Show coordinates" | `True` |
| `last` | tuple(str, str) or None | last move played: from, to | `("d2", "d3")` |
| `last_cells` | list of (row, col) | the same two squares as indexes into `board` (from, to); `[]` if unknown | `[(1, 4), (2, 4)]` |
| `last_text` | str | | `"d2 – d3"` |
| `white_to_move` | bool | | `False` |
| `side` | str | side to move | `"Black"` |
| `to_move` | str | | `"Black to move"` |
| `move_number` | int or None | full-move number of the position (the last move was move `move_number` of white if black is to move, else move `move_number − 1` of black) | `4` |
| `mate` | str | the "mate in n" theme, `""` if the puzzle has none | `"Mate in 2"` |
| `mate_in` | int or None | n of it | `2` |
| `themes` | list[str] | the other themes, translated (at most 4 incl. mate) | `["Kingside attack", "Sacrifice", "Short"]` |
| `themes_text` | str | joined with " · " | `"Kingside attack · Sacrifice · Short"` |
| `rating` | int or None | puzzle rating | `1843` |
| `rating_text` | str | `""` without rating | `"Rating 1843"` |
| `moves` | int | own moves of the solution | `2` |
| `solution_text` | str | | `"Solution: 2 moves"` |
| `hint` | str | | `"Solution in the web app"` |
| `now`, `today` | datetime, date | render time | |
| `date`, `time` | str | | `"November 10, 2026"`, `"13:37"` |
| `place` | str | name of the configured location (may be `""`) | `"Berlin"` |

The solution moves themselves are deliberately not in the view (the screen must not spoil them).

## Helpers (`from inkyframe.plugins import chess_puzzle`)

- `draw_piece(d, piece, cx, cy, size, ink=BLACK, paper=WHITE)` – draws one piece centred in a square of
  `size` px around `(cx, cy)` with the bundled symbol font (design fonts have no chess glyphs). `piece` is a
  letter from `board`; `""` draws nothing. White pieces: `paper` body with `ink` outline, black pieces: solid
  `ink`. Typical loop:
  ```python
  for r, row in enumerate(v["board"]):
      for c, p in enumerate(row):
          chess_puzzle.draw_piece(d, p, x0 + c * s + s // 2, y0 + r * s + s // 2, s)
  ```
- Square colour: square `(r, c)` of `board` is dark when `(r + c) % 2 == 1` (same for both orientations).
- `board_rows(fen, flip=False)` → the 8×8 list; `cell_of("d3", flip)` → `(row, col)`.
- `draw_board(d, fen, x0, y0, size, flip, last=None, dark=GREEN, coords=True)` – the complete regular board.
- `theme_name(key, lang)` – translated Lichess theme.

## Shown in mockups, not available

- "Nr. 314 / Blatt 314" is the day of the year, not a puzzle number – the puzzle only has the Lichess `id`.
- Move notation of the last move with move number ("3. d2–d3") can be built from `move_number` + `last`;
  SAN of the last move is not kept.
