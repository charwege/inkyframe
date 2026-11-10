# wifi – `GuestWifi.view(ctx, data)`

Sample values: `plugin.sample(ctx)`, language `de`. The hook is only called when a network name is set.

| field | type | meaning | sample |
|---|---|---|---|
| `title` | str | translated screen title | `"Gäste-WLAN"` |
| `hint` | str | translated | `"Mit der Handykamera scannen"` |
| `network_label` | str | translated | `"Netzwerk"` |
| `password_label` | str | translated | `"Passwort"` |
| `ssid` | str | network name | `"Gäste"` |
| `password` | str | password **to print**; `""` when the owner switched "Show password as text" off, or the network is open – then draw no password row | `"sunflower-42"` |
| `security` | str | `"WPA"` (= WPA/WPA2/WPA3), `"WEP"` or `""` for an open network | `"WPA"` |
| `open` | bool | open network without password | `False` |
| `hidden` | bool | hidden network | `False` |
| `note` | str | the owner's note, may be `""` | `"Herzlich willkommen!"` |
| `payload` | str | text inside the QR code (contains the password – never print it) | `"WIFI:T:WPA;S:Gäste;P:sunflower-42;;"` |
| `modules` | list of rows of bool | the QR code, `True` = dark; square, without quiet zone | 29 × 29 |
| `size` | int | modules per side | `29` |
| `place` | str | name of the frame's location, may be `""` | `"Berlin"` |
| `today` | `date` | | `date(2026, 11, 10)` |
| `date_text` | str | | `"Dienstag, 10. November"` |

Helpers in `inkyframe.plugins.wifi`:
- `draw_modules(d, modules, x, y, size, dark=(0, 0, 0), light=None, quiet=4)` – draws the code on a PIL
  `ImageDraw` into the square `(x, y, size)` with whole-pixel modules, centred; `light` fills the square
  first; returns the module size in px. With `light` set it is pixel-identical to `ctx.qr(...)`.
- `qr_modules(settings)` → `modules`; `wifi_payload(ssid, password, security, hidden)` → `payload`.

Keep the code scannable: dark modules on a light ground with good contrast (black on white/yellow), at
least 2 modules of quiet zone, square modules of whole pixels (≥ 6 px), nothing drawn over it.

Not available (mockups show it): "WPA2" as exact standard (the setting only knows WPA/WEP/open); a translated
word for "encryption"/"open network" (bring it in the layout's i18n file).
