"""Extra font faces used by the studio designs' signature layouts (weather + thought of the day).

Each entry becomes data/fonts/<theme>/st-<role>.ttf, downloaded by `python -m inkyframe.fonts`
together with the theme's regular fonts. If a face is missing, the theme's base kind is used.
role -> (Google family, weight, italic, fallback kind)
"""

FACES = {
    "bauhaus": {
        "black": ("Archivo Black", 400, False, "display"),
        "x800": ("Archivo", 800, False, "sans-bold"),
        "x600": ("Archivo", 600, False, "sans-bold"),
    },
    "newspaper": {
        "pf900": ("Playfair Display", 900, False, "display"),
        "pf700": ("Playfair Display", 700, False, "serif-bold"),
        "pf700i": ("Playfair Display", 700, True, "serif-italic"),
        "pf400i": ("Playfair Display", 400, True, "serif-italic"),
        "ss400": ("Source Serif 4", 400, False, "serif"),
        "ss400i": ("Source Serif 4", 400, True, "serif-italic"),
        "ss600": ("Source Serif 4", 600, False, "sans-bold"),
    },
    "deco": {
        "lime": ("Limelight", 400, False, "display"),
        "poiret": ("Poiret One", 400, False, "serif"),
        "jos": ("Josefin Sans", 400, False, "sans"),
    },
    "pixel": {
        "ps2p": ("Press Start 2P", 400, False, "display"),
        "vt": ("VT323", 400, False, "sans"),
    },
    "zen": {
        "cg300": ("Cormorant Garamond", 300, False, "serif"),
        "cg400i": ("Cormorant Garamond", 400, True, "serif-italic"),
        "zk400": ("Zen Kaku Gothic New", 400, False, "sans"),
        "zk700": ("Zen Kaku Gothic New", 700, False, "sans-bold"),
    },
    "swiss": {
        "it900": ("Inter Tight", 900, False, "serif-bold"),
        "it700": ("Inter Tight", 700, False, "sans-bold"),
        "it500": ("Inter Tight", 500, False, "sans"),
    },
    "memphis": {
        "rmo": ("Rubik Mono One", 400, False, "display"),
        "r800": ("Rubik", 800, False, "serif-bold"),
        "r700": ("Rubik", 700, False, "sans-bold"),
    },
    "blueprint": {
        "pm300": ("IBM Plex Mono", 300, False, "serif"),
        "pm400": ("IBM Plex Mono", 400, False, "sans"),
        "pm600": ("IBM Plex Mono", 600, False, "sans-bold"),
    },
    "botanical": {
        "lc400": ("Libre Caslon Text", 400, False, "serif"),
        "lc400i": ("Libre Caslon Text", 400, True, "serif-italic"),
        "cav": ("Caveat", 500, False, "serif-italic"),
    },
    "chalk": {
        "cb": ("Caveat Brush", 400, False, "display"),
        "ph": ("Patrick Hand", 400, False, "sans"),
    },
}


def google_spec(theme):
    """Entries for themes.THEMES[theme]["google"] (kind -> (family, weight, italic))."""
    return {f"st-{role}": (fam, w, it) for role, (fam, w, it, _) in FACES.get(theme, {}).items()}
