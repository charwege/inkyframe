"""Signature layouts of the studio designs for the plugins (one module per design).

inkyframe/layouts/<design>.py holds one function per plugin id:

    def chess(ctx, v):            # v = the dict returned by the plugin's view(ctx, data)
        c = Canvas("bauhaus", Wh)
        ...
        return c.finish()

A plugin calls layouts.render(ctx, self.id, view) after it has its data; if the chosen design
has no layout for it (or the layout fails), None comes back and the plugin draws its regular screen.
Texts a design adds are translated in inkyframe/layouts/i18n_<design>.py
(STRINGS = {"fr": {"English text": "…"}, …}); see docs/views/ for the fields of every view.
"""
import importlib
import logging

log = logging.getLogger("inkyframe.layouts")
STUDIO = ("bauhaus", "newspaper", "deco", "pixel", "zen", "swiss", "memphis", "blueprint", "botanical", "chalk")
PLUGINS = ("chess", "spotify", "grid", "wordclock", "countdown", "art", "waste", "warnings", "wifi", "habits",
           "sudoku", "solar", "waterlevel", "birthdays", "watchlist")
_mods = {}
STRICT = False          # tests set this: a failing layout raises instead of falling back


def module(theme):
    if theme not in STUDIO:
        return None
    if theme not in _mods:
        try:
            _mods[theme] = importlib.import_module(f"inkyframe.layouts.{theme}")
        except ModuleNotFoundError as e:
            if e.name != f"inkyframe.layouts.{theme}":
                raise
            _mods[theme] = None
    return _mods[theme]


def has(theme, pid):
    m = module(theme)
    return bool(m and callable(getattr(m, pid, None)))


def render(ctx, pid, view):
    """Image of the design's own layout for this plugin, or None."""
    if not has(ctx.theme, pid):
        return None
    try:
        return getattr(module(ctx.theme), pid)(ctx, view)
    except Exception:
        if STRICT:
            raise
        log.warning("layout %s/%s failed – using the regular screen", ctx.theme, pid, exc_info=True)
        return None


def extra_strings(lang):
    """Translations the design layouts bring along (i18n_<design>.py)."""
    out = {}
    for theme in STUDIO:
        try:
            m = importlib.import_module(f"inkyframe.layouts.i18n_{theme}")
        except ModuleNotFoundError:
            continue
        out.update(getattr(m, "STRINGS", {}).get(lang, {}))
    return out
