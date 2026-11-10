"""Download the Google Fonts used by the designs as TTF files into data/fonts/<theme>/.

  python -m inkyframe.fonts            all designs
  python -m inkyframe.fonts zen pixel  only these

All fonts are licensed under the SIL Open Font License (see fonts.google.com).
"""
import os
import re
import sys
import threading
import urllib.parse

import requests

from . import store, themes

# An unknown user agent makes the Google Fonts CSS API answer with plain TrueType files.
UA = {"User-Agent": "inkyframe-font-fetcher/1.0"}
_lock = threading.Lock()
progress = {}          # theme -> "downloading" | "ok" | "error: …"


def css_url(family, weight, italic):
    fam = urllib.parse.quote_plus(family)
    axis = f":ital,wght@1,{weight}" if italic else f":wght@{weight}"
    return f"https://fonts.googleapis.com/css2?family={fam}{axis}&display=swap"


def ttf_url(family, weight, italic):
    css = requests.get(css_url(family, weight, italic), headers=UA, timeout=20)
    css.raise_for_status()
    urls = re.findall(r"url\((https://[^)]+)\)\s*format\(['\"]truetype['\"]\)", css.text)
    if not urls:
        urls = [u for u in re.findall(r"url\((https://[^)]+\.ttf)\)", css.text)]
    if not urls:
        raise RuntimeError(f"no TrueType file offered for {family} {weight}{' italic' if italic else ''}")
    return urls[-1]          # the last block is the basic Latin subset when several are listed


def download(theme, force=False):
    t = themes.get(theme)
    spec = t.get("google")
    if not spec:
        return []
    out_dir = os.path.join(store.FONT_DIR, theme)
    os.makedirs(out_dir, exist_ok=True)
    cache, written = {}, []
    for kind, (family, weight, italic) in spec.items():
        path = os.path.join(out_dir, f"{kind}.ttf")
        if os.path.exists(path) and not force:
            continue
        key = (family, weight, italic)
        if key not in cache:
            r = requests.get(ttf_url(family, weight, italic), headers=UA, timeout=60)
            r.raise_for_status()
            cache[key] = r.content
        with open(path, "wb") as f:
            f.write(cache[key])
        written.append(path)
    themes.clear_cache()
    from . import gfx
    gfx.clear_font_cache()
    return written


def download_async(theme):
    """Used by the web app: download in the background, track progress."""
    def run():
        progress[theme] = "downloading"
        try:
            download(theme)
            progress[theme] = "ok"
        except Exception as e:
            progress[theme] = f"error: {e}"
    with _lock:
        if progress.get(theme) == "downloading":
            return
        threading.Thread(target=run, daemon=True).start()


def main(argv=None):
    names = (argv if argv is not None else sys.argv[1:]) or [k for k, t in themes.THEMES.items() if "google" in t]
    store.load()
    failed = 0
    for name in names:
        try:
            files = download(name)
            print(f"✓ {name}: {len(files)} new file(s)")
        except Exception as e:
            failed += 1
            print(f"✗ {name}: {e} – this design falls back to DejaVu")
    return 1 if failed and failed == len(names) else 0


if __name__ == "__main__":
    sys.exit(main())
