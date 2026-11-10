"""inkyframe plugin API.

A plugin is one Python file that defines a subclass of `Plugin`:

    from inkyframe.plugin import Plugin, Setting

    class Hello(Plugin):
        id = "hello"
        name = "Hello"
        icon = "☺"
        settings = [Setting("text", "text", "Greeting", default="Hello world")]

        def render(self, ctx, data=None):
            img, d = ctx.canvas()
            ctx.fit_center(d, ctx.settings["text"])
            return img

Bundled plugins live in `inkyframe/plugins/`, your own ones can be dropped into
`data/plugins/` (then restart the service).
See docs/PLUGINS.md for the full guide.
"""
import datetime as dt
import importlib
import json
import importlib.util
import inspect
import logging
import os
import pkgutil
import traceback

from . import gfx, store

log = logging.getLogger("inkyframe.plugins")
API_VERSION = 1

SETTING_TYPES = ("text", "textarea", "number", "bool", "select", "secret", "date", "time",
                 "color", "action", "info")


class Setting:
    """Declarative setting – the web app builds the form from these.

    type: text | textarea | number | bool | select | secret | date | time | color | action | info
      - select:  options=[("value", "Label"), ...]
      - color:   one of the six panel colours
      - action:  a button; calls `Plugin.action_<key>(ctx, value)`. With `input="placeholder"`
                 a text field is shown and its value passed along.
      - info:    read-only text (label only)
    """

    def __init__(self, key, type, label, default=None, options=None, help=None,
                 min=None, max=None, input=None):
        assert type in SETTING_TYPES, f"unknown setting type {type!r}"
        self.key, self.type, self.label, self.default = key, type, label, default
        self.options, self.help, self.min, self.max, self.input = options, help, min, max, input

    def to_dict(self):
        d = {"key": self.key, "type": self.type, "label": self.label, "default": self.default}
        for k in ("options", "help", "min", "max", "input"):
            v = getattr(self, k)
            if v is not None:
                d[k] = [list(o) if isinstance(o, (list, tuple)) else [o, o] for o in v] if k == "options" else v
        return d


class Context:
    """Everything a plugin needs while rendering. Passed as `ctx`."""

    W, H = gfx.W, gfx.H
    BLACK, WHITE, RED, YELLOW, GREEN, BLUE = gfx.BLACK, gfx.WHITE, gfx.RED, gfx.YELLOW, gfx.GREEN, gfx.BLUE
    COLORS = gfx.COLORS

    def __init__(self, plugin, cfg=None, now=None):
        self.plugin = plugin
        self.cfg = cfg if cfg is not None else store.get()
        self.lang = self.cfg.get("language", "en")
        self.location = self.cfg.get("location", {})
        self.now = now or dt.datetime.now()
        self.settings = plugin.resolve_settings(self.cfg)
        self.theme = self.cfg.get("theme", "classic")
        gfx.set_theme(self.theme)           # fonts & decorations follow the chosen design

    @property
    def ACCENT(self):
        """Accent colour of the current design (classic/playful: red, modern: blue)."""
        return gfx.accent()

    # -- time & language --
    @property
    def today(self):
        return self.now.date()

    def t(self, en, de=None, **fmt):
        """Pick the text for the display language: ctx.t("Hello", "Hallo")."""
        from . import i18n
        if isinstance(en, dict):
            text = en.get(self.lang) or i18n.tr(self.lang, en.get("en") or next(iter(en.values())), en.get("de"))
        else:
            text = i18n.tr(self.lang, en, de)
        return text.format(**fmt) if fmt else text

    def num(self, v, digits=2):
        """Number with the language's decimal and thousands separators."""
        from .plugins import _calendar
        return _calendar.number(v, self.lang, digits)

    def date(self, d, style="long", weekday=True, year=False):
        """Localised date: style "long" (“Tuesday, November 10”) or "short" (“Nov 10”, “10.11.”)."""
        from .plugins import _calendar
        return _calendar.short_date(d, self.lang) if style == "short" else _calendar.long_date(d, self.lang, weekday, year)

    # -- drawing --
    canvas = staticmethod(gfx.canvas)
    font = staticmethod(gfx.font)
    wrap = staticmethod(gfx.wrap)
    fit_text = staticmethod(gfx.fit_text)
    draw_lines = staticmethod(gfx.draw_lines)
    text_center = staticmethod(gfx.text_center)
    text_w = staticmethod(gfx.text_w)
    cover_fit = staticmethod(gfx.cover_fit)
    punch = staticmethod(gfx.punch_for_eink)
    message = staticmethod(gfx.message_screen)

    def fit_center(self, d, text, box=None, kind="serif", max_size=72, min_size=18, fill=None):
        """Wrap and centre text inside box=(x, y, w, h) (default: whole screen with margin)."""
        x, y, w, h = box or (60, 60, self.W - 120, self.H - 120)
        f, lines, lh = gfx.fit_text(d, text, kind, w, h, max_size, min_size)
        top = y + (h - len(lines) * lh) // 2
        gfx.draw_lines(d, lines, f, lh, x, top, w, fill=fill or self.BLACK)

    def header(self, d, title, subtitle=None, x=40, color=None):
        """Title (+ subtitle) top-left in the style of the chosen design. Returns the y below it."""
        return gfx.header(d, title, subtitle, x, color)

    def footer(self, d, text, x=40):
        """Small source/credit line at the bottom."""
        gfx.footer(d, text, x)

    def frame(self, d, inset=22, color=None):
        """Decorative border in the style of the chosen design."""
        gfx.frame(d, inset, color)

    # -- network (cached) --
    fetch_json = staticmethod(gfx.get_json)
    fetch_image = staticmethod(gfx.get_image)
    fetch_text = staticmethod(gfx.get_text)

    # -- QR codes (no extra dependency) --
    def qr(self, d, text, x, y, size, dark=None, light=None):
        from . import qr
        return qr.draw(d, text, x, y, size, dark or self.BLACK, light or self.WHITE)

    # -- persistence --
    def save_settings(self, **values):
        """Persist values in the plugin's settings (e.g. OAuth tokens). Not shown in the form."""
        store.update({"plugins": {self.plugin.id: values}})
        self.settings.update(values)

    def _state_path(self):
        return os.path.join(store.DATA_DIR, "state", f"{self.plugin.id}.json")

    def load_state(self, default=None):
        """Plugin-private JSON data (logs, history …) in data/state/<id>.json."""
        try:
            with open(self._state_path(), encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {} if default is None else default

    def save_state(self, data):
        path = self._state_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, path)


class Plugin:
    """Base class. Override what you need; only `id`, `name` and `render` are required."""

    id = ""                  # unique, lowercase, used in config & URLs
    name = ""                # str or {"en": ..., "de": ...}
    icon = "▢"               # one character shown in the web app
    description = ""
    author = ""
    version = "1.0"
    api_version = API_VERSION
    settings = []            # list[Setting]
    refresh_minutes = 0      # re-render every N minutes (0 = only when content_key changes)
    can_interrupt = False    # may take over the display (see wants_display)
    poll_minutes = 0         # >0: poll(ctx) is called in the background every N minutes
    theme_remap = True       # dark designs recolour the finished image; False for photo plugins
    builtin = False

    # --- lifecycle hooks ---
    def content_key(self, ctx):
        """Cheap value; whenever it changes the plugin is re-rendered. Default: once a day."""
        return ctx.today.isoformat()

    def render(self, ctx, data=None):
        """Return a PIL image of 800×480. `data` is sample data during offline previews."""
        raise NotImplementedError

    def sample(self, ctx):
        """Optional offline data for previews / CI. Return None to fetch live data."""
        return None

    def refresh_interval(self, ctx):
        """Minutes between re-renders. A setting called "refresh_minutes" overrides the class value."""
        return int(ctx.settings.get("refresh_minutes", self.refresh_minutes) or 0)

    def poll(self, ctx):
        """Background hook (see poll_minutes): collect data even while not on screen."""

    def wants_display(self, ctx):
        """For can_interrupt plugins: return True to take over the display right now."""
        return False

    def status(self, ctx):
        """Short status line shown in the plugin's settings panel."""
        return ""

    # --- helpers used by the framework ---
    def display_name(self, lang="en"):
        from . import i18n
        if isinstance(self.name, dict):
            return self.name.get(lang) or i18n.tr(lang, self.name.get("en") or self.id, self.name.get("de"))
        return i18n.tr(lang, self.name) if self.name else self.id

    def resolve_settings(self, cfg):
        vals = {s.key: s.default for s in self.settings if s.type not in ("action", "info")}
        vals.update(cfg.get("plugins", {}).get(self.id, {}))
        return vals

    def extra_settings(self, ctx):
        """Optional: settings that depend on the current config (e.g. one button per habit).
        Action keys without an `action_<key>` method are routed to `action(ctx, key, value)`."""
        return []

    def action(self, ctx, key, value=None):
        raise ValueError(f"unknown action {key}")

    def run_action(self, ctx, key, value=None):
        fn = getattr(self, f"action_{key}", None)
        res = fn(ctx, value) if fn else self.action(ctx, key, value)
        return res or {}

    def describe(self, lang="en", ctx=None):
        extra = self.extra_settings(ctx) if ctx else []
        return {
            "id": self.id, "name": self.display_name(lang), "icon": self.icon,
            "description": self.description, "author": self.author, "version": self.version,
            "settings": [s.to_dict() for s in list(self.settings) + list(extra)],
            "can_interrupt": self.can_interrupt, "builtin": self.builtin,
        }


# --------------------------------------------------------------------------- registry
REGISTRY = {}
FAILED = {}


def _collect(module, builtin):
    found = 0
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, Plugin) and obj is not Plugin and obj.__module__ == module.__name__:
            p = obj()
            if not p.id:
                raise ValueError(f"{obj.__name__} has no id")
            if p.id in REGISTRY:
                log.warning("plugin id %s defined twice – %s wins", p.id, module.__name__)
            p.builtin = builtin
            REGISTRY[p.id] = p
            found += 1
    return found


def discover():
    """Load bundled plugins (inkyframe/plugins) and user plugins (data/plugins/*.py)."""
    REGISTRY.clear()
    FAILED.clear()
    from . import plugins as pkg
    for info in sorted(pkgutil.iter_modules(pkg.__path__), key=lambda i: i.name):
        if info.name.startswith("_"):
            continue
        try:
            _collect(importlib.import_module(f"{pkg.__name__}.{info.name}"), builtin=True)
        except Exception:
            FAILED[info.name] = traceback.format_exc(limit=3)
            log.error("plugin %s failed to load:\n%s", info.name, FAILED[info.name])
    udir = store.USER_PLUGIN_DIR
    if os.path.isdir(udir):
        for fn in sorted(os.listdir(udir)):
            if not fn.endswith(".py") or fn.startswith("_"):
                continue
            name = f"inkyframe_user_{fn[:-3]}"
            try:
                spec = importlib.util.spec_from_file_location(name, os.path.join(udir, fn))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                _collect(mod, builtin=False)
            except Exception:
                FAILED[fn] = traceback.format_exc(limit=3)
                log.error("user plugin %s failed to load:\n%s", fn, FAILED[fn])
    log.info("plugins: %s", ", ".join(REGISTRY))
    return REGISTRY


def get(pid):
    return REGISTRY.get(pid)


def render(pid, cfg=None, now=None, sample=False):
    """Render a plugin; with sample=True its offline sample data is used if it has any."""
    p = REGISTRY[pid]
    ctx = Context(p, cfg, now)
    data = p.sample(ctx) if sample else None
    return finish(p, ctx, p.render(ctx, data))


def finish(plugin, ctx, img):
    """Apply the design's colour remap (dark designs) to a rendered image."""
    gfx.set_theme(ctx.theme)
    if img.info.get("studio"):          # signature layouts are drawn in their final colours
        return img
    return gfx.postprocess(img, ctx.theme, remap=plugin.theme_remap)
