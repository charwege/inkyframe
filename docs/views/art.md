# art – `ArtOfTheDay.view(ctx, data)`

Sample values: `plugin.sample(ctx)`, language `de`, 10 Nov 2026. The hook is not called when the setting
*Layout* is "Picture only" – then the picture fills the frame in every design.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | translated screen title | `"Kunst des Tages"` |
| `work` | str | title of the artwork (not translated) | `"Evening over the Hills"` |
| `artist` | str | artist, may be `""` | `"Sample Painter"` |
| `date` | str | date as the museum writes it, may be `""` | `"1889"` |
| `caption` | str | artist · date (what the regular screen prints under the title) | `"Sample Painter · 1889"` |
| `medium` | str | technique, `""` if the museum gives none | `""` (live e.g. `"Oil on canvas"`) |
| `dimensions` | str | size as the museum writes it, `""` if unknown | `""` (live e.g. `"73.2 × 92.1 cm (28 13/16 × 36 1/4 in.)"`) |
| `origin` | str | place of origin, `""` if unknown | `""` (live e.g. `"France"`) |
| `image` | PIL `Image` (RGB) | the picture, already fetched and colour-boosted for the panel (setting *Colour boost*); original size, scale/crop it into your frame | 600×450 |
| `width`, `height` | int | pixel size of `image` | `600`, `450` |
| `aspect` | float | width / height | `1.333` |
| `landscape` | bool | aspect > 1.25 (the regular screen then puts the caption below, else beside) | `True` |
| `museum` | str | always the source collection | `"Art Institute of Chicago"` |
| `museum_city` | str | | `"Chicago"` |
| `license` | str | translated | `"Gemeinfrei"` |
| `today` | `date` | | `date(2026, 11, 10)` |
| `date_text` | str | `ctx.date(today)` | `"Dienstag, 10. November"` |
| `date_short` | str | `ctx.date(today, "short")` | `"10.11."` |
| `doy` | int | day of the year (the picture changes daily) | `314` |

`medium`, `dimensions`, `origin` are English texts from the museum and are empty in the sample – draw
those rows only when filled.

Helpers: `ctx.cover_fit(image, w, h)` crops to fill a box; for "fit inside" resize with
`min(w / width, h / height)` as the regular screen does.

Not available (mockups show it): a description text of the picture, a sheet/"No." number other than `doy`,
a museum in the frame's own town (the mockups' "Alte Nationalgalerie · Berlin" is `museum` · `museum_city`).
