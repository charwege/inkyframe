"""Inky Impression driver. Without a panel (e.g. on a PC) only the preview PNG is written."""
import logging
import threading

from PIL import Image

from . import store

log = logging.getLogger("inkyframe.display")


class Display:
    def __init__(self):
        self.inky = None
        self.lock = threading.Lock()
        try:
            from inky.auto import auto
            self.inky = auto(ask_user=False, verbose=False)
            log.info("Inky detected: %s %s", type(self.inky).__name__, self.inky.resolution)
        except Exception as e:  # no panel / no driver -> preview only
            log.warning("No Inky display found (%s) – preview only.", e)

    @property
    def available(self):
        return self.inky is not None

    def show(self, img: Image.Image):
        cfg = store.get()["display"]
        img.save(store.CURRENT_PNG)
        if not self.inky:
            return
        out = img
        if cfg.get("rotate180"):
            out = out.rotate(180)
        if out.size != tuple(self.inky.resolution):
            out = out.resize(self.inky.resolution)
        with self.lock:   # a Spectra refresh takes ~25–30 s
            try:
                self.inky.set_image(out, saturation=float(cfg.get("saturation", 0.5)))
            except TypeError:
                self.inky.set_image(out)
            self.inky.show()
