"""Display designs (themes).

A theme changes fonts, headers, frames, the accent colour and – for dark designs – the
colours of every plugin. Plugins that use ctx.font / ctx.header / ctx.frame / ctx.ACCENT
follow automatically; dark designs are produced by remapping colours after rendering.

Fonts
  * "fonts":  file stems searched in data/fonts and /usr/share/fonts (apt packages)
  * "google": Google Fonts downloaded by `python -m inkyframe.fonts` into data/fonts/<theme>/
  Missing fonts fall back to DejaVu ("fallback": serif | sans | mono).
Kinds: serif, serif-bold, serif-italic, sans, sans-bold, sans-cond, display (headers), symbols.
"""
import glob
import os

THEMES = {
    "classic": {
        "label": "Classic", "group": "basic", "accent": "red",
        "description": "Serif type, fine double rules, calm and timeless.",
        "fonts": {},
    },
    "modern": {
        "label": "Modern", "group": "basic", "accent": "blue", "fallback": "sans",
        "description": "Clean sans-serif (Inter), bold headings, colour bar accents.",
        "fonts": {"serif": ["Inter-Regular"], "serif-bold": ["Inter-Bold"], "serif-italic": ["Inter-Italic"],
                  "sans": ["Inter-Regular"], "sans-bold": ["Inter-SemiBold", "Inter-Bold"], "sans-cond": ["Inter-Regular"]},
    },
    "playful": {
        "label": "Playful", "group": "basic", "accent": "red", "fallback": "sans",
        "description": "Friendly rounded type, colourful labels and confetti dots.",
        "fonts": {"serif": ["ComicNeue-Regular", "Poppins-Medium"], "serif-bold": ["ComicNeue-Bold", "Poppins-Bold"],
                  "serif-italic": ["ComicNeue-Italic", "Poppins-Italic"], "sans": ["ComicNeue-Regular", "Poppins-Regular"],
                  "sans-bold": ["ComicNeue-Bold", "Poppins-SemiBold"], "sans-cond": ["ComicNeue-Regular", "Poppins-Regular"]},
    },
    # ------------------------------------------------------------------ studio designs
    "bauhaus": {
        "label": "Bauhaus", "group": "studio", "accent": "red", "fallback": "sans",
        "description": "Circle, square, triangle – primary colours and bold capitals.",
        "google": {"serif": ("Archivo", 500, False), "serif-bold": ("Archivo Black", 400, False),
                   "serif-italic": ("Archivo", 500, True), "sans": ("Archivo", 400, False),
                   "sans-bold": ("Archivo", 800, False), "sans-cond": ("Archivo", 400, False),
                   "display": ("Archivo Black", 400, False)},
    },
    "newspaper": {
        "label": "Newspaper", "group": "studio", "accent": "red", "fallback": "serif",
        "description": "Front page: Playfair headlines, columns, double rules.",
        "google": {"serif": ("Source Serif 4", 400, False), "serif-bold": ("Playfair Display", 900, False),
                   "serif-italic": ("Playfair Display", 400, True), "sans": ("Source Serif 4", 400, False),
                   "sans-bold": ("Source Serif 4", 600, False), "sans-cond": ("Source Serif 4", 400, False),
                   "display": ("Playfair Display", 900, False)},
    },
    "deco": {
        "label": "Art déco", "group": "studio", "accent": "yellow", "fallback": "sans",
        "description": "Black and gold, sunburst fans and stepped frames.",
        "remap": {"white": "black", "black": "white", "blue": "yellow"},
        "google": {"serif": ("Poiret One", 400, False), "serif-bold": ("Limelight", 400, False),
                   "serif-italic": ("Poiret One", 400, False), "sans": ("Josefin Sans", 400, False),
                   "sans-bold": ("Josefin Sans", 600, False), "sans-cond": ("Josefin Sans", 400, False),
                   "display": ("Limelight", 400, False)},
    },
    "pixel": {
        "label": "Pixel", "group": "studio", "accent": "green", "fallback": "mono",
        "description": "Retro game: dialogue boxes, pixel fonts, on black.",
        "remap": {"white": "black", "black": "white", "blue": "green"},
        "google": {"serif": ("VT323", 400, False), "serif-bold": ("VT323", 400, False),
                   "serif-italic": ("VT323", 400, False), "sans": ("VT323", 400, False),
                   "sans-bold": ("VT323", 400, False), "sans-cond": ("VT323", 400, False),
                   "display": ("Press Start 2P", 400, False)},
        "size": 1.25,            # VT323 runs small – scale every font size up
    },
    "zen": {
        "label": "Zen", "group": "studio", "accent": "red", "fallback": "serif",
        "description": "Lots of white space, light serif, a red seal.",
        "google": {"serif": ("Cormorant Garamond", 500, False), "serif-bold": ("Cormorant Garamond", 600, False),
                   "serif-italic": ("Cormorant Garamond", 400, True), "sans": ("Zen Kaku Gothic New", 400, False),
                   "sans-bold": ("Zen Kaku Gothic New", 700, False), "sans-cond": ("Zen Kaku Gothic New", 400, False),
                   "display": ("Cormorant Garamond", 500, False)},
    },
    "swiss": {
        "label": "Swiss", "group": "studio", "accent": "red", "fallback": "sans",
        "description": "Strict grid, huge numbers, one red square.",
        "fonts": {"serif": ["InterTight-Regular", "Inter-Regular"], "serif-bold": ["InterTight-Black", "Inter-Black", "Inter-Bold"],
                  "serif-italic": ["InterTight-Italic", "Inter-Italic"], "sans": ["InterTight-Medium", "Inter-Medium", "Inter-Regular"],
                  "sans-bold": ["InterTight-Bold", "Inter-Bold"], "sans-cond": ["InterTight-Regular", "Inter-Regular"]},
        "google": {"serif": ("Inter Tight", 400, False), "serif-bold": ("Inter Tight", 900, False),
                   "serif-italic": ("Inter Tight", 400, True), "sans": ("Inter Tight", 500, False),
                   "sans-bold": ("Inter Tight", 700, False), "sans-cond": ("Inter Tight", 400, False),
                   "display": ("Inter Tight", 700, False)},
    },
    "memphis": {
        "label": "Memphis", "group": "studio", "accent": "red", "fallback": "sans",
        "description": "80s shapes, squiggles, hard black shadows.",
        "google": {"serif": ("Rubik", 500, False), "serif-bold": ("Rubik", 800, False),
                   "serif-italic": ("Rubik", 500, True), "sans": ("Rubik", 500, False),
                   "sans-bold": ("Rubik", 700, False), "sans-cond": ("Rubik", 400, False),
                   "display": ("Rubik", 800, False)},
    },
    "blueprint": {
        "label": "Blueprint", "group": "studio", "accent": "yellow", "fallback": "mono",
        "description": "Technical drawing: white lines on blue grid paper, monospace.",
        "remap": {"white": "blue", "black": "white", "blue": "yellow"},
        "pattern": "grid",
        "google": {"serif": ("IBM Plex Mono", 400, False), "serif-bold": ("IBM Plex Mono", 600, False),
                   "serif-italic": ("IBM Plex Mono", 400, True), "sans": ("IBM Plex Mono", 400, False),
                   "sans-bold": ("IBM Plex Mono", 600, False), "sans-cond": ("IBM Plex Mono", 400, False),
                   "display": ("IBM Plex Mono", 600, False)},
        "size": 0.92,            # monospace runs wide
    },
    "botanical": {
        "label": "Botanical", "group": "studio", "accent": "green", "fallback": "serif",
        "description": "Herbarium: Caslon type, leafy sprigs, specimen label.",
        "google": {"serif": ("Libre Caslon Text", 400, False), "serif-bold": ("Libre Caslon Text", 700, False),
                   "serif-italic": ("Libre Caslon Text", 400, True), "sans": ("Libre Caslon Text", 400, False),
                   "sans-bold": ("Libre Caslon Text", 700, False), "sans-cond": ("Libre Caslon Text", 400, False),
                   "display": ("Libre Caslon Text", 400, True)},
        "size": 0.95,
    },
    "chalk": {
        "label": "Chalkboard", "group": "studio", "accent": "yellow", "fallback": "sans",
        "description": "Handwritten chalk on a black board, doodles included.",
        "remap": {"white": "black", "black": "white", "blue": "yellow"},
        "google": {"serif": ("Patrick Hand", 400, False), "serif-bold": ("Caveat Brush", 400, False),
                   "serif-italic": ("Patrick Hand", 400, False), "sans": ("Patrick Hand", 400, False),
                   "sans-bold": ("Patrick Hand", 400, False), "sans-cond": ("Patrick Hand", 400, False),
                   "display": ("Caveat Brush", 400, False)},
        "size": 1.08,
    },
}
DEFAULT = "classic"

_DEJAVU = {
    "serif": "DejaVuSerif.ttf", "serif-bold": "DejaVuSerif-Bold.ttf", "serif-italic": "DejaVuSerif-Italic.ttf",
    "sans": "DejaVuSans.ttf", "sans-bold": "DejaVuSans-Bold.ttf", "sans-cond": "DejaVuSansCondensed.ttf",
    "symbols": "DejaVuSans.ttf", "display": "DejaVuSerif-Bold.ttf",
}
_FALLBACKS = {
    "sans": {"serif": "DejaVuSans.ttf", "serif-bold": "DejaVuSans-Bold.ttf", "serif-italic": "DejaVuSans-Oblique.ttf",
             "display": "DejaVuSans-Bold.ttf"},
    "mono": {"serif": "DejaVuSansMono.ttf", "serif-bold": "DejaVuSansMono-Bold.ttf", "serif-italic": "DejaVuSansMono-Oblique.ttf",
             "sans": "DejaVuSansMono.ttf", "sans-bold": "DejaVuSansMono-Bold.ttf", "sans-cond": "DejaVuSansMono.ttf",
             "display": "DejaVuSansMono-Bold.ttf"},
    "serif": {"sans-bold": "DejaVuSerif-Bold.ttf"},
}
_SEARCH_DIRS = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.local/share/fonts")]
_found = {}


def get(name):
    return THEMES.get(name) or THEMES[DEFAULT]


def clear_cache():
    _found.clear()


def _find(stem, extra_dirs):
    key = (stem, tuple(extra_dirs))
    if key in _found:
        return _found[key]
    hit = None
    for base in list(extra_dirs) + _SEARCH_DIRS:
        for ext in ("ttf", "otf", "ttc"):
            matches = glob.glob(os.path.join(base, "**", f"{stem}.{ext}"), recursive=True)
            if matches:
                hit = sorted(matches)[0]
                break
        if hit:
            break
    _found[key] = hit
    return hit


def font_path(theme, kind, font_dir):
    """Resolve the font file for a theme + kind. Custom/downloaded files win:
    data/fonts/<theme>/<kind>.ttf, then data/fonts/<kind>.ttf (all themes)."""
    t = get(theme)
    candidates = [kind] + (["serif-bold"] if kind == "display" else [])
    for k in candidates:
        if k == "symbols":
            break
        for p in (os.path.join(font_dir, theme, f"{k}.ttf"), os.path.join(font_dir, theme, f"{k}.otf")):
            if os.path.exists(p):
                return p
        if "google" not in t:            # user overrides for the system-font themes
            p = os.path.join(font_dir, f"{k}.ttf")
            if os.path.exists(p):
                return p
        for stem in t.get("fonts", {}).get(k, []):
            p = _find(stem, [os.path.join(font_dir, theme), font_dir])
            if p:
                return p
    name = _FALLBACKS.get(t.get("fallback"), {}).get(kind, _DEJAVU.get(kind, "DejaVuSans.ttf"))
    return _find(name[:-4], [font_dir]) or _find(_DEJAVU.get(kind, "DejaVuSans.ttf")[:-4], [font_dir])


def size_factor(theme):
    return get(theme).get("size", 1.0)


def fonts_ok(name, font_dir):
    """True if the design's intended fonts are present (downloaded or installed)."""
    t = get(name)
    if "google" in t:
        if all(os.path.exists(os.path.join(font_dir, name, f"{k}.ttf")) for k in t["google"]):
            return True
        if t.get("fonts"):                # e.g. Swiss can live with system Inter
            return all(any(_find(s, []) for s in stems) for stems in t["fonts"].values())
        return False
    return all(any(_find(s, []) for s in stems) for stems in t.get("fonts", {}).values())


def status(font_dir=None):
    from . import store
    fd = font_dir or store.FONT_DIR
    return {name: fonts_ok(name, fd) for name in THEMES}
