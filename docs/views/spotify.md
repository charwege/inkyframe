# View: `spotify` (Spotify)

`Spotify.view(ctx, data)` in `inkyframe/plugins/spotify.py`. `data` is a track dict; `render()` adds the
fetched cover and the state before it calls the view. Samples: `plugin.sample()`, English.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | plugin / screen title | `"Spotify"` |
| `source` | str | | `"Spotify"` |
| `label` | str | translated state line | `"Now playing"` (also `"Paused"`, `"Recently played"`) |
| `state` | str | `"playing"`, `"paused"` or `"recent"` (nothing active – last/recently played track) | `"playing"` |
| `playing` | bool | `state == "playing"` | `True` |
| `track` | str | song or episode title | `"A Rather Long Song Title (Remastered)"` |
| `artist` | str | artists joined with ", " (podcasts: publisher); may be `""` | `"The Performers"` |
| `album` | str | album (podcasts: show name); may be `""` | `"Album of the Week"` |
| `image` | PIL `Image` (RGB) or None | the cover, already fetched, original size (usually 640×640), not yet dithered | 640×640 image |
| `has_image` | bool | | `True` |
| `duration` | int or None | track length in seconds | `245` |
| `duration_text` | str | `m:ss` (`h:mm:ss` from one hour), `""` if unknown | `"4:05"` |
| `cover_only` | bool | setting Layout = "Cover only" | `False` |
| `now`, `today` | datetime, date | render time | |
| `date`, `time` | str | | `"November 10, 2026"`, `"13:37"` |
| `place` | str | name of the configured location (may be `""`) | `"Berlin"` |

"Not connected" and "Nothing playing" stay message screens of the plugin; a layout always gets a track.

## Helpers

- Cover on the panel like the regular screen: `img.paste(ctx.punch(ctx.cover_fit(v["image"], w, h)), (x, y))`
  (`cover_fit` crops to the box, `punch` raises contrast/saturation for e-ink). The plugin has
  `theme_remap = False`, so the picture is not recoloured in dark designs.

## Shown in mockups, not available

- Playback position / progress bar ("2:14", "noch 1:51", "55 %"): the screen is only redrawn when the album
  changes, a position would be wrong almost immediately. Only the total `duration` is provided.
- Room / device ("Wohnzimmer"): the plugin does not query the player's device.
