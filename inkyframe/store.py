"""Persistent settings (data/config.json) with defaults, deep merge and migration."""
import copy
import json
import os
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("INKYFRAME_DATA", os.path.join(BASE_DIR, "data"))
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
FONT_DIR = os.path.join(DATA_DIR, "fonts")
USER_PLUGIN_DIR = os.path.join(DATA_DIR, "plugins")
CURRENT_PNG = os.path.join(DATA_DIR, "current.png")

DEFAULTS = {
    "language": "en",                  # language used ON the display: en | de
    "theme": "classic",                # display design, see themes.py (classic, modern, playful, bauhaus, zen …)
    "app_theme": "auto",               # web app design: auto (= display design) or any design name
    "location": {"name": "Berlin", "lat": 52.5200, "lon": 13.4050, "holidays": "de"},
    "mode": "weather",                 # fixed mode when rotation is off
    "auto": {
        "enabled": False,
        "hold_minutes": 30,            # how long a manually chosen mode stays while rotating
        "items": [                     # order = rotation order
            # optional per item: "theme": "<design>" – shown in that design instead of the frame's
            {"mode": "weather", "minutes": 20, "enabled": True},
            {"mode": "quote", "minutes": 10, "enabled": True},
            {"mode": "chess", "minutes": 10, "enabled": True},
            {"mode": "grid", "minutes": 10, "enabled": False},
            {"mode": "wordclock", "minutes": 15, "enabled": False},
            {"mode": "countdown", "minutes": 10, "enabled": False},
        ],
    },
    # plugins allowed to take over the display (e.g. Spotify while music plays)
    "interrupts": {"spotify": True},
    "quiet": {"enabled": True, "start": "23:00", "end": "06:30"},
    # demo mode for showcase videos: walks through plugins / designs / languages with built-in sample data
    "demo": {"enabled": False, "seconds": 60, "plugins": True, "designs": True, "languages": False},
    "display": {"rotate180": False, "saturation": 0.5, "crisp_text": True},
    "plugins": {},                     # per-plugin settings (defaults come from each plugin)
}

_lock = threading.RLock()
_cache = None


def deep_merge(base, extra):
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def migrate(stored):
    """Convert configs from the first (German-only) version."""
    if not stored or "plugins" in stored:
        return stored
    old_plugin_keys = ("weather", "quote", "chess", "grid", "spotify", "wordclock")
    if not any(k in stored for k in old_plugin_keys):
        return stored
    new = {k: v for k, v in stored.items() if k not in old_plugin_keys + ("spotify_priority",)}
    new["language"] = "de"
    plugins = {}
    w = stored.get("weather", {})
    if w:
        new["location"] = {"name": w.get("name", "Berlin"), "lat": w.get("lat", 52.5200),
                           "lon": w.get("lon", 13.405), "holidays": "de"}
        plugins["weather"] = {"refresh_minutes": w.get("refresh_minutes", 30)}
    for k in ("quote", "chess", "grid", "wordclock"):
        if k in stored:
            plugins[k] = stored[k]
    sp = dict(stored.get("spotify", {}))
    if sp:
        plugins["spotify"] = sp
    new["plugins"] = plugins
    new["interrupts"] = {"spotify": bool(stored.get("spotify_priority", True))}
    return new


def _drop_buttons(cfg):
    """Buttons were removed in 2.1 – keep the hold time, drop the rest."""
    b = cfg.pop("buttons", None)
    if isinstance(b, dict) and "hold_minutes" in b:
        cfg.setdefault("auto", {}).setdefault("hold_minutes", b["hold_minutes"])
    return cfg


def _ensure_dirs():
    for d in (DATA_DIR, FONT_DIR, USER_PLUGIN_DIR):
        os.makedirs(d, exist_ok=True)


def _write(cfg):
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CONFIG_PATH)


def load():
    global _cache
    with _lock:
        _ensure_dirs()
        stored = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, encoding="utf-8") as f:
                    stored = json.load(f)
            except (OSError, ValueError):
                stored = {}
        had_buttons = "buttons" in stored
        migrated = _drop_buttons(migrate(stored))
        _cache = deep_merge(DEFAULTS, migrated)
        if migrated is not stored or had_buttons:
            _write(_cache)
        return copy.deepcopy(_cache)


def get():
    with _lock:
        if _cache is None:
            return load()
        return copy.deepcopy(_cache)


def update(patch):
    """Partial update (deep merge) and save. Lists are replaced, not merged."""
    global _cache
    with _lock:
        cfg = deep_merge(get(), patch)
        _ensure_dirs()
        _write(cfg)
        _cache = cfg
        return copy.deepcopy(cfg)
