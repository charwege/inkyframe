"""Collect every English text that a translation must cover (used by the tests and translators).

  python -m inkyframe.i18n_keys          print the keys
  python -m inkyframe.i18n_keys fr       print only the keys missing in French
"""
import ast
import os
import sys


def literal_keys():
    base = os.path.dirname(os.path.abspath(__file__))
    keys = set()
    for root, _, files in os.walk(base):
        for fn in files:
            if not fn.endswith(".py") or "locales" in root:
                continue
            tree = ast.parse(open(os.path.join(root, fn), encoding="utf-8").read())
            for n in ast.walk(tree):
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "t"
                        and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
                    keys.add(n.args[0].value)
    return keys


def dynamic_keys():
    from .plugins import grid, sudoku, warnings, weather
    from .plugins._calendar import holidays
    from . import plugin as P
    keys = {en for en, _, _ in weather.WMO.values()}
    keys |= {en for (en, _), _ in grid.SIG.values()}
    keys |= {en for en, _ in warnings.LEVEL_TEXT.values()}
    keys |= {en for en, _ in sudoku.LEVEL_NAMES.values()}
    for region in ("de-ni", "de-by"):
        keys |= set(holidays(2026, region, "en").values())
    if not P.REGISTRY:
        P.discover()
    for p in P.REGISTRY.values():
        if p.builtin:
            keys.add(p.name.get("en") if isinstance(p.name, dict) else p.name)
    return keys


def all_keys():
    return sorted(literal_keys() | dynamic_keys())


def missing(lang):
    from . import i18n
    have = i18n.locale(lang).STRINGS
    return [k for k in all_keys() if k not in have]


if __name__ == "__main__":
    from . import store
    store.load()
    keys = missing(sys.argv[1]) if len(sys.argv) > 1 else all_keys()
    for k in keys:
        print(repr(k))
    print(f"# {len(keys)}", file=sys.stderr)
