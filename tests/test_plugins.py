"""Every plugin must load and render an 800×480 RGB image from its sample data – in both languages."""
import os
import tempfile

os.environ.setdefault("INKYFRAME_DATA", tempfile.mkdtemp())

import pytest  # noqa: E402

from inkyframe import dev, store  # noqa: E402
from inkyframe.themes import THEMES  # noqa: E402
from inkyframe import plugin as P  # noqa: E402

store.load()
P.discover()


def test_no_load_failures():
    assert not P.FAILED, P.FAILED


def test_check_passes():
    assert dev.check() == []


@pytest.mark.parametrize("pid", sorted(P.REGISTRY))
@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize("theme", list(THEMES))
def test_render_sample(pid, lang, theme):
    cfg = store.get()
    cfg["language"] = lang
    cfg["theme"] = theme
    p = P.REGISTRY[pid]
    if p.sample(P.Context(p, cfg)) is None:
        pytest.skip("plugin has no sample data")
    img = P.render(pid, cfg, sample=True)
    assert img.size == (800, 480) and img.mode == "RGB"


def test_wordclock_phrases():
    import datetime as dt
    from inkyframe.plugins import wordclock as W

    def say(lang, hhmm):
        h, m = map(int, hhmm.split(":"))
        cells, hours = W.words_for(dt.datetime(2026, 1, 1, h, m), lang)
        grid = W.EN_GRID if lang == "en" else W.DE_GRID
        return "".join(grid[r][c] for r, c in sorted(cells | hours))

    assert say("de", "13:25") == "ESISTFÜNFVORHALBZWEI"
    assert say("de", "01:00") == "ESISTEINUHR"
    assert say("en", "13:35") == "ITISTWENTYFIVETOTWO"
    assert say("en", "12:00") == "ITISTWELVEOCLOCK"


def test_dark_designs_remap():
    from inkyframe import gfx
    from PIL import Image
    img = Image.new("RGB", (10, 10), (255, 255, 255))
    img.putpixel((1, 1), (0, 0, 0))
    out = gfx.postprocess(img, "chalk")
    assert out.getpixel((5, 5)) == (0, 0, 0) and out.getpixel((1, 1)) == (255, 255, 255)
    assert gfx.postprocess(img, "classic").getpixel((5, 5)) == (255, 255, 255)


def test_font_css_url():
    from inkyframe import fonts
    assert fonts.css_url("Inter Tight", 900, False).endswith("family=Inter+Tight:wght@900&display=swap")
    assert ":ital,wght@1,400" in fonts.css_url("Libre Caslon Text", 400, True)


@pytest.mark.parametrize("lang", __import__("inkyframe.i18n", fromlist=["ORDER"]).ORDER)
def test_translations_complete(lang):
    from inkyframe import i18n, i18n_keys
    if lang in ("en", "de"):
        return
    assert i18n_keys.missing(lang) == [], f"{lang}: missing translations"
    loc = i18n.locale(lang)
    assert len(loc.WEEKDAYS) == 7 and len(loc.MONTHS) == 12 and len(loc.MONTHS_GEN) == 12 and len(loc.MOON) == 8
    assert len(loc.WEEKDAY_LETTERS) == 7
    assert len(loc.QUESTIONS) > 3, "the sample uses QUESTIONS[3]"


@pytest.mark.parametrize("pid", sorted(P.REGISTRY))
@pytest.mark.parametrize("lang", __import__("inkyframe.i18n", fromlist=["ORDER"]).ORDER)
def test_render_every_language(pid, lang):
    cfg = store.get()
    cfg["language"] = lang
    img = P.render(pid, cfg, sample=True)
    assert img.size == (800, 480)



@pytest.mark.parametrize("theme", ["bauhaus", "newspaper", "deco", "pixel", "zen", "swiss", "memphis", "blueprint",
                                   "botanical", "chalk"])
@pytest.mark.parametrize("pid", ["weather", "quote"])
def test_studio_signature_layouts(theme, pid):
    """Every studio design draws its own weather / thought-of-the-day layout – in every language."""
    from inkyframe import i18n
    for lang in i18n.ORDER:
        cfg = store.get()
        cfg["language"] = lang
        cfg["theme"] = theme
        img = P.render(pid, cfg, sample=True)
        assert img.size == (800, 480) and img.info.get("studio"), (theme, lang)


class _FakeDisplay:
    available = False

    def __init__(self):
        self.shown = []

    def show(self, img):
        self.shown.append(img)


def _engine():
    from inkyframe.engine import Engine
    return Engine(_FakeDisplay())


def test_rotation_design_per_plugin():
    store.update({"theme": "classic", "demo": {"enabled": False}, "quiet": {"enabled": False},
                  "interrupts": {"spotify": False},
                  "auto": {"enabled": True, "items": [{"mode": "quote", "minutes": 10, "enabled": True, "theme": "bauhaus"},
                                                      {"mode": "wordclock", "minutes": 10, "enabled": True}]}})
    e = _engine()
    e.tick()
    assert (e.status["mode"], e.status["theme"]) == ("quote", "bauhaus")
    assert e.display.shown[-1].info.get("studio")            # drawn with the Bauhaus layout
    e.rot_since -= 601
    e.tick()
    assert (e.status["mode"], e.status["theme"]) == ("wordclock", "classic")
    store.update({"auto": {"enabled": False}})


def test_demo_mode_walks_plugins_designs_languages():
    from inkyframe import i18n
    store.update({"demo": {"enabled": True, "seconds": 20, "plugins": True, "designs": True, "languages": True},
                  "quiet": {"enabled": True, "start": "00:00", "end": "23:59"}})
    e = _engine()
    seen = []
    for _ in range(4):
        e.tick()
        seen.append((e.status["mode"], e.status["theme"], e.status["language"]))
        e.demo_next()
    assert len(set(seen)) == 4 and len(e.display.shown) == 4       # quiet hours don't stop the demo
    assert [s[1] for s in seen] == list(THEMES)[:4]
    assert [s[2] for s in seen] == list(i18n.ORDER)[:4]
    assert e.status["demo"]["next"]["step"] == 4
    e.select("weather")                                          # picking a screen ends the demo
    assert not store.get()["demo"]["enabled"]
    store.update({"quiet": {"enabled": False}})
