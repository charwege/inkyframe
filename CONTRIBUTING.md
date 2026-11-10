# Contributing

Thanks for helping inkyframe grow! The easiest and most welcome contribution is a **new plugin**.

## Ways to help
- **Build a plugin** – see [docs/PLUGINS.md](docs/PLUGINS.md). Ideas are collected in issues labelled
  `plugin idea`; pick one or open your own.
- **Share a plugin idea** – open an issue with the *Plugin idea* template, even if you can't code it.
- **Translate** – plugins use `ctx.t(en, de)`; every other language lives in `inkyframe/locales/<code>.py`, keyed by the English text. To add a language copy `locales/en.py`, translate it, add the code to `ORDER` in `inkyframe/i18n.py` and run `pytest` (it lists missing keys).
- **Add public holidays for your region** in `_calendar.py`.
- **Report bugs** with the *Bug report* template (include `journalctl -u inkyframe -n 50`).

## Plugin pull request checklist
- [ ] One file in `inkyframe/plugins/`, one `Plugin` subclass, unique lowercase `id`
- [ ] `name`, `icon`, `description`, `author` set
- [ ] `sample()` returns offline data, so the plugin renders without network
- [ ] Text via `ctx.t(en, de)` – new English strings also need an entry in each `locales/*.py` (pytest tells you which)
- [ ] No API keys or personal data in the code – use `Setting(..., "secret", ...)`
- [ ] `content_key()` changes only when the picture really changes (e-ink refreshes are slow)
- [ ] `python -m inkyframe.dev check` and `pytest` pass
- [ ] Preview image added to `docs/img/<id>.png` (`python -m inkyframe.dev render <id> --sample --out docs/img`)
- [ ] Any new dependency added to `requirements.txt` and imported **inside** the plugin
      (so a missing package only disables that plugin)

## Code style
Plain Python 3.11, no framework magic. Keep core changes small and discuss bigger ones in an issue first.
Plugins must not touch the display or GPIO directly – the engine does that.

## Licence
By contributing you agree that your contribution is licensed under the MIT licence of this project.
