"""Decides what is shown and refreshes the panel only when the image actually changes.

Priority (highest first):
  0. Demo mode – walks through plugins / designs / languages with sample data (for showcase videos)
  1. Manual choice in the web app – lasts `hold_minutes` while rotation is on
  2. Interrupting plugins (e.g. Spotify while music plays)
  3. Rotation
  4. Fixed mode
Quiet hours: no refreshes (the image simply stays), a manual choice still works.
"""
import datetime as dt
import hashlib
import logging
import threading
import time
import traceback

from . import gfx, i18n, store, themes
from . import plugin as P

log = logging.getLogger("inkyframe.engine")
POLL_SECONDS = 15


class Engine(threading.Thread):
    def __init__(self, display):
        super().__init__(daemon=True, name="engine")
        self.display = display
        self.wake = threading.Event()
        self.lock = threading.Lock()
        self.force = False
        self.override = None            # {"mode": str, "until": ts | None}
        self.rot_index = 0
        self.rot_since = time.time()
        self.demo_step = 0
        self.demo_since = 0.0
        self.demo_on = False
        self.cur_tag = None
        self.cur_mode = None
        self.cur_key = None
        self.cur_hash = None
        self.rendered_at = 0
        self.polled = {}
        self.status = {"mode": None, "reason": "", "updated": None, "error": None, "busy": False}

    # ---- external control (web app) ----
    def select(self, mode):
        """Show a mode now. Temporary while rotation is on, permanent otherwise."""
        cfg = store.get()
        if mode not in P.REGISTRY:
            return
        if cfg.get("demo", {}).get("enabled"):
            store.update({"demo": {"enabled": False}})     # picking a screen ends the demo
        with self.lock:
            if cfg["auto"]["enabled"]:
                hold = int(cfg["auto"].get("hold_minutes", 30))
                self.override = {"mode": mode, "until": time.time() + hold * 60}
            else:
                self.override = None
                store.update({"mode": mode})
            self.force = True
        self.wake.set()

    def resume_auto(self):
        with self.lock:
            self.override = None
            self.force = True
        store.update({"auto": {"enabled": True}})
        self.wake.set()

    def refresh(self):
        with self.lock:
            self.force = True
        self.wake.set()

    def demo_next(self):
        with self.lock:
            self.demo_since = 0.0
        self.wake.set()

    # ---- demo mode ----
    @staticmethod
    def demo_lists(cfg):
        d = cfg.get("demo", {})
        order = [i["mode"] for i in cfg["auto"]["items"] if i["mode"] in P.REGISTRY]
        order += [pid for pid in P.REGISTRY if pid not in order]
        fixed = cfg.get("mode") if cfg.get("mode") in P.REGISTRY else order[0]
        return (order if d.get("plugins", True) else [fixed],
                list(themes.THEMES) if d.get("designs", True) else [cfg.get("theme", "classic")],
                list(i18n.ORDER) if d.get("languages") else [cfg.get("language", "en")])

    def demo_plan(self, cfg, step=None):
        plugins, designs, langs = self.demo_lists(cfg)
        s = self.demo_step if step is None else step
        return {"mode": plugins[s % len(plugins)], "theme": designs[s % len(designs)],
                "language": langs[s % len(langs)], "step": s}

    def _demo_tick(self, cfg):
        now = time.time()
        secs = max(20, int(cfg["demo"].get("seconds", 60)))
        if not self.demo_on:                      # just switched on: start with the first screen
            self.demo_on, self.demo_step, self.demo_since = True, 0, now
        elif now - self.demo_since >= secs and not self.status.get("busy"):
            self.demo_step += 1
            self.demo_since = now
        return self.demo_plan(cfg)

    # ---- logic ----
    @staticmethod
    def _rotation_theme(cfg, mode):
        """Design chosen for this plugin in the rotation list (only while rotation is on)."""
        if not cfg["auto"]["enabled"]:
            return None
        for i in cfg["auto"]["items"]:
            if i["mode"] == mode and i.get("theme") in themes.THEMES:
                return i["theme"]
        return None

    @staticmethod
    def _in_quiet(cfg):
        q = cfg.get("quiet", {})
        if not q.get("enabled"):
            return False
        now = dt.datetime.now().strftime("%H:%M")
        start, end = q.get("start", "23:00"), q.get("end", "06:30")
        return (start <= now or now < end) if start > end else (start <= now < end)

    def _pick_mode(self, cfg):
        now = time.time()
        if self.override:
            if self.override["until"] and now > self.override["until"]:
                self.override = None
            else:
                return self.override["mode"], "manual"
        for pid, on in cfg.get("interrupts", {}).items():
            p = P.get(pid)
            if on and p and p.can_interrupt:
                try:
                    if p.wants_display(P.Context(p, cfg)):
                        return pid, f"{p.display_name()} interrupt"
                except Exception:
                    log.debug("interrupt check %s failed", pid, exc_info=True)
        if cfg["auto"]["enabled"]:
            items = [i for i in cfg["auto"]["items"] if i.get("enabled") and i["mode"] in P.REGISTRY]
            if items:
                self.rot_index %= len(items)
                dur = max(1, int(items[self.rot_index].get("minutes", 10))) * 60
                if now - self.rot_since >= dur:
                    self.rot_index = (self.rot_index + 1) % len(items)
                    self.rot_since = now
                return items[self.rot_index]["mode"], "rotation"
        mode = cfg.get("mode", "weather")
        return (mode if mode in P.REGISTRY else next(iter(P.REGISTRY))), "fixed"

    def next_change(self, cfg):
        """For the web app: when does the rotation switch next?"""
        if cfg.get("demo", {}).get("enabled"):
            return int(self.demo_since + max(20, int(cfg["demo"].get("seconds", 60))))
        if not cfg["auto"]["enabled"] or self.override:
            return None
        items = [i for i in cfg["auto"]["items"] if i.get("enabled")]
        if not items:
            return None
        dur = int(items[self.rot_index % len(items)].get("minutes", 10)) * 60
        return int(self.rot_since + dur)

    def _poll_all(self, cfg):
        now = time.time()
        for pid, p in P.REGISTRY.items():
            if p.poll_minutes and now - self.polled.get(pid, 0) >= p.poll_minutes * 60:
                self.polled[pid] = now
                try:
                    p.poll(P.Context(p, cfg))
                except Exception as e:
                    log.warning("poll %s failed: %s", pid, e)

    def tick(self):
        cfg = store.get()
        self._poll_all(cfg)
        demo = bool(cfg.get("demo", {}).get("enabled"))
        with self.lock:
            force, self.force = self.force, False
            if demo:
                plan = self._demo_tick(cfg)
                mode, reason = plan["mode"], "demo"
                cfg["theme"], cfg["language"] = plan["theme"], plan["language"]
            else:
                self.demo_on = False
                mode, reason = self._pick_mode(cfg)
                cfg["theme"] = self._rotation_theme(cfg, mode) or cfg.get("theme", "classic")
        if self._in_quiet(cfg) and not force and not demo:
            self.status["reason"] = "quiet hours"
            return
        mod = P.get(mode)
        ctx = P.Context(mod, cfg)
        try:
            key = None if demo else mod.content_key(ctx)
        except Exception:
            key = None
        tag = (mode, cfg["theme"], cfg.get("language"), plan["step"] if demo else None)
        interval = 0 if demo else mod.refresh_interval(ctx) * 60
        due = (force or tag != self.cur_tag or key != self.cur_key
               or (interval and time.time() - self.rendered_at >= interval))
        self.status.update(mode=mode, reason=reason, theme=cfg["theme"], language=cfg.get("language"),
                           demo=dict(plan, next=self.demo_plan(store.get(), plan["step"] + 1)) if demo else None)
        if not due:
            return
        self.status["busy"] = True
        try:
            try:
                data = None
                if demo:                               # sample data: nothing personal in a showcase video
                    try:
                        data = mod.sample(ctx)
                    except Exception:
                        data = None
                img = P.finish(mod, ctx, mod.render(ctx, data))
                self.status["error"] = None
            except Exception as e:
                log.error("render %s failed:\n%s", mode, traceback.format_exc())
                name = mod.display_name(cfg.get("language", "en"))
                self.status["error"] = f"{name}: {e}"
                if tag == self.cur_tag and not force:
                    self.rendered_at = time.time()   # keep the old image, retry later
                    return
                img = gfx.postprocess(gfx.message_screen(
                    ctx.t("{n} is unavailable right now", "{n} gerade nicht verfügbar", n=name), str(e)[:140]), ctx.theme)
            h = hashlib.md5(img.tobytes()).hexdigest()
            if h != self.cur_hash or force:
                log.info("showing %s (%s)", mode, reason)
                self.display.show(img)
                self.cur_hash = h
                self.status["updated"] = int(time.time())
            self.cur_mode, self.cur_key, self.rendered_at, self.cur_tag = mode, key, time.time(), tag
            if demo:
                self.demo_since = time.time()      # count the seconds from when the panel finished drawing
        finally:
            self.status["busy"] = False

    def run(self):
        while True:
            try:
                self.tick()
            except Exception:
                log.error("engine error:\n%s", traceback.format_exc())
            self.wake.wait(POLL_SECONDS)
            self.wake.clear()
