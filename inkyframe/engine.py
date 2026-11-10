"""Decides what is shown and refreshes the panel only when the image actually changes.

Priority (highest first):
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

from . import gfx, store
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

    # ---- logic ----
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
        with self.lock:
            force, self.force = self.force, False
            mode, reason = self._pick_mode(cfg)
        if self._in_quiet(cfg) and not force:
            self.status["reason"] = "quiet hours"
            return
        mod = P.get(mode)
        ctx = P.Context(mod, cfg)
        try:
            key = mod.content_key(ctx)
        except Exception:
            key = None
        interval = mod.refresh_interval(ctx) * 60
        due = (force or mode != self.cur_mode or key != self.cur_key
               or (interval and time.time() - self.rendered_at >= interval))
        self.status.update(mode=mode, reason=reason)
        if not due:
            return
        self.status["busy"] = True
        try:
            try:
                img = P.finish(mod, ctx, mod.render(ctx))
                self.status["error"] = None
            except Exception as e:
                log.error("render %s failed:\n%s", mode, traceback.format_exc())
                name = mod.display_name(cfg.get("language", "en"))
                self.status["error"] = f"{name}: {e}"
                if mode == self.cur_mode and not force:
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
            self.cur_mode, self.cur_key, self.rendered_at = mode, key, time.time()
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
