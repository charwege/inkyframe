"""Web app (Flask) + startup of the engine.   Run:  python3 run.py"""
import io
import logging
import os
import time

from flask import Flask, abort, jsonify, render_template, request, send_file

from . import __version__, gfx, i18n, store, themes
from . import plugin as P
from .display import Display
from .engine import Engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("inkyframe")

app = Flask(__name__)
store.load()
P.discover()
display = Display()
engine = Engine(display)
MASK = "••••••"


def _plugin_payload(cfg):
    out = []
    for p in P.REGISTRY.values():
        ctx = P.Context(p, cfg)
        desc = p.describe(cfg.get("language", "en"), ctx)
        values = {}
        for s in p.settings:
            if s.type in ("action", "info"):
                continue
            v = ctx.settings.get(s.key, s.default)
            values[s.key] = (MASK if v else "") if s.type == "secret" else v
        desc["values"] = values
        try:
            desc["status"] = p.status(ctx)
        except Exception as e:
            desc["status"] = f"status error: {e}"
        out.append(desc)
    return out


@app.get("/")
def index():
    cfg = store.get()
    theme = cfg.get("app_theme", "auto")
    return render_template("index.html", theme=cfg.get("theme", "classic") if theme == "auto" else theme)


@app.get("/api/state")
def state():
    cfg = store.get()
    st = dict(engine.status)
    st.update(next_change=engine.next_change(cfg), display=display.available, now=int(time.time()),
              override_until=engine.override["until"] if engine.override else None)
    global_cfg = {k: v for k, v in cfg.items() if k != "plugins"}
    from .plugins._calendar import HOLIDAY_REGIONS
    from . import fonts
    ok = themes.status()
    theme_list = [{"id": k, "label": t["label"], "description": t["description"], "group": t.get("group", "basic"),
                   "fonts_ok": ok.get(k, True), "downloadable": "google" in t, "dark": bool(t.get("remap")),
                   "progress": fonts.progress.get(k, "")}
                  for k, t in themes.THEMES.items()]
    preview = cfg.get("mode") if cfg.get("mode") in P.REGISTRY and cfg.get("mode") != "spotify" else "quote"
    return jsonify(config=global_cfg, status=st, plugins=_plugin_payload(cfg),
                   holiday_regions=HOLIDAY_REGIONS, version=__version__,
                   themes=theme_list, design_preview=preview, languages=i18n.languages(),
                   failed=list(P.FAILED))


@app.post("/api/config")
def config():
    """Global settings (everything except per-plugin settings)."""
    patch = request.get_json(force=True) or {}
    patch.pop("plugins", None)
    if "language" in patch and patch["language"] not in i18n.ORDER:
        return jsonify(ok=False, error="unknown language"), 400
    if "theme" in patch and patch["theme"] not in themes.THEMES:
        return jsonify(ok=False, error="unknown design"), 400
    store.update(patch)
    if "theme" in patch and "google" in themes.get(patch["theme"]) and not themes.fonts_ok(patch["theme"], store.FONT_DIR):
        from . import fonts
        fonts.download_async(patch["theme"])           # fetch the design's fonts in the background
    engine.refresh()
    return jsonify(ok=True)


@app.post("/api/plugins/<pid>/settings")
def plugin_settings(pid):
    p = P.get(pid) or abort(404)
    body = request.get_json(force=True) or {}
    allowed = {s.key: s for s in p.settings if s.type not in ("action", "info")}
    clean = {}
    for k, v in body.items():
        s = allowed.get(k)
        if not s or (s.type == "secret" and v == MASK):
            continue
        if s.type == "number":
            try:
                v = float(v) if "." in str(v) else int(v)
            except ValueError:
                continue
        clean[k] = v
    store.update({"plugins": {pid: clean}})
    engine.refresh()
    return jsonify(ok=True)


@app.post("/api/plugins/<pid>/action/<key>")
def plugin_action(pid, key):
    p = P.get(pid) or abort(404)
    value = (request.get_json(force=True) or {}).get("value")
    try:
        res = p.run_action(P.Context(p), key, value)
    except Exception as e:
        log.warning("action %s.%s failed: %s", pid, key, e)
        return jsonify(ok=False, error=str(e)), 400
    engine.refresh()
    return jsonify(ok=True, **res)


@app.post("/api/fonts/<theme>")
def load_fonts(theme):
    if theme not in themes.THEMES:
        abort(404)
    from . import fonts
    fonts.download_async(theme)
    return jsonify(ok=True)


@app.post("/api/show/<pid>")
def show(pid):
    P.get(pid) or abort(404)
    engine.select(pid)
    return jsonify(ok=True)


@app.post("/api/auto")
def auto():
    on = (request.get_json(force=True) or {}).get("enabled", True)
    if on:
        engine.resume_auto()
    else:
        store.update({"auto": {"enabled": False}, "mode": engine.cur_mode or store.get()["mode"]})
        engine.override = None
        engine.refresh()
    return jsonify(ok=True)


@app.post("/api/refresh")
def refresh():
    engine.refresh()
    return jsonify(ok=True)


@app.get("/current.png")
def current_png():
    if not os.path.exists(store.CURRENT_PNG):
        abort(404)
    return send_file(store.CURRENT_PNG, mimetype="image/png", max_age=0)


_preview_cache = {}


@app.get("/api/preview/<pid>.png")
def preview(pid):
    P.get(pid) or abort(404)
    cfg = store.get()
    if request.args.get("theme") in themes.THEMES:
        cfg["theme"] = request.args["theme"]
    sample = request.args.get("sample") == "1"
    key = (pid, cfg["theme"], cfg.get("language"), time.strftime("%Y%m%d%H"), themes.fonts_ok(cfg["theme"], store.FONT_DIR))
    if sample and key in _preview_cache:          # design thumbnails: render once per hour
        return send_file(io.BytesIO(_preview_cache[key]), mimetype="image/png", max_age=0)
    try:
        img = P.render(pid, cfg, sample=sample)
    except Exception as e:
        gfx.set_theme(cfg.get("theme"))
        img = gfx.postprocess(gfx.message_screen("Preview failed", str(e)[:140]), cfg.get("theme"))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    if sample:
        _preview_cache[key] = buf.getvalue()
    buf.seek(0)
    return send_file(buf, mimetype="image/png", max_age=0)


def main():
    engine.start()
    port = int(os.environ.get("INKYFRAME_PORT", "8080"))
    log.info("web app on port %s", port)
    app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
