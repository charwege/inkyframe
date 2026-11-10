"""Developer tools – work on plugins without a Raspberry Pi.

  python -m inkyframe.dev list                       all plugins
  python -m inkyframe.dev render weather             render live data -> preview/weather.png
  python -m inkyframe.dev render weather --sample    use the plugin's offline sample data
  python -m inkyframe.dev render wordclock --lang de --time 13:37
  python -m inkyframe.dev gallery --sample           render all plugins -> preview/
  python -m inkyframe.dev gallery --sample --theme modern   … in another design (classic|modern|playful)
  python -m inkyframe.dev check                      validate all plugins (used by CI)
  python -m inkyframe.dev new myplugin               scaffold data/plugins/myplugin.py
"""
import argparse
import datetime as dt
import os
import sys
import textwrap

from . import plugin as P
from . import store
from .i18n import ORDER
from .themes import THEMES

OUT = "preview"


def _cfg(lang, theme=None):
    cfg = store.get()
    if lang:
        cfg["language"] = lang
    if theme:
        cfg["theme"] = theme
    return cfg


def _now(t):
    if not t:
        return None
    h, m = map(int, t.split(":"))
    return dt.datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)


def cmd_list(a):
    for p in P.REGISTRY.values():
        flag = "" if p.builtin else "  (user)"
        print(f"{p.icon}  {p.id:<12} {p.display_name()}{flag}")
    for name, err in P.FAILED.items():
        print(f"✗  {name}: failed to load\n{textwrap.indent(err, '     ')}")


def _render_one(pid, a):
    img = P.render(pid, _cfg(a.lang, a.theme), _now(a.time), sample=a.sample)
    os.makedirs(a.out, exist_ok=True)
    suffix = (f"_{a.lang}" if a.lang else "") + (f"_{a.theme}" if a.theme else "")
    path = os.path.join(a.out, f"{pid}{suffix}.png")
    img.save(path)
    print("wrote", path)
    return img


def cmd_render(a):
    if a.plugin not in P.REGISTRY:
        sys.exit(f"unknown plugin {a.plugin!r} – try: python -m inkyframe.dev list")
    _render_one(a.plugin, a)


def cmd_gallery(a):
    for pid in P.REGISTRY:
        try:
            _render_one(pid, a)
        except Exception as e:
            print(f"✗ {pid}: {e}")


def check():
    """Return a list of problems. A plugin passes if it loads, has metadata and renders
    an 800×480 RGB image from its sample data (plugins without samples are only loaded)."""
    problems = [f"{n}: failed to load" for n in P.FAILED]
    seen = set()
    for pid, p in P.REGISTRY.items():
        if not pid.isidentifier() or pid != pid.lower():
            problems.append(f"{pid}: id must be lowercase letters/digits/_")
        if pid in seen:
            problems.append(f"{pid}: duplicate id")
        seen.add(pid)
        if not p.display_name():
            problems.append(f"{pid}: missing name")
        keys = [s.key for s in p.settings]
        if len(keys) != len(set(keys)):
            problems.append(f"{pid}: duplicate setting keys")
        for s in p.settings:
            if s.type == "action" and not hasattr(p, f"action_{s.key}"):
                problems.append(f"{pid}: action setting {s.key!r} has no method action_{s.key}")
        for lang, theme in (("en", "classic"), ("de", "classic"), ("en", "modern"), ("de", "playful")):
            cfg = _cfg(lang, theme)
            ctx = P.Context(p, cfg)
            if p.sample(ctx) is None:
                continue
            try:
                img = P.render(pid, cfg, sample=True)
                if img.size != (P.Context.W, P.Context.H) or img.mode != "RGB":
                    problems.append(f"{pid}: render must return 800×480 RGB, got {img.size} {img.mode}")
            except Exception as e:
                problems.append(f"{pid} ({lang}): render with sample data failed: {e!r}")
    return problems


def cmd_check(a):
    problems = check()
    for p in problems:
        print("✗", p)
    print(f"{len(P.REGISTRY)} plugins, {len(problems)} problems")
    sys.exit(1 if problems else 0)


TEMPLATE = '''"""{title} – describe what this plugin shows."""
from inkyframe.plugin import Plugin, Setting


class {cls}(Plugin):
    id = "{pid}"
    name = "{title}"
    icon = "★"
    description = "One sentence about what this shows."
    author = "your-github-name"
    settings = [
        Setting("text", "text", "Text", default="Hello, frame!"),
    ]

    def sample(self, ctx):
        return {{"text": "Hello from the sample data"}}

    def render(self, ctx, data=None):
        text = (data or {{}}).get("text") or ctx.settings["text"]
        img, d = ctx.canvas()
        ctx.fit_center(d, text, kind="serif-bold", max_size=80)
        return img
'''


def cmd_new(a):
    pid = a.id.lower()
    if not pid.isidentifier():
        sys.exit("id must be letters, digits and underscores")
    os.makedirs(store.USER_PLUGIN_DIR, exist_ok=True)
    path = os.path.join(store.USER_PLUGIN_DIR, f"{pid}.py")
    if os.path.exists(path):
        sys.exit(f"{path} exists already")
    cls = "".join(w.capitalize() for w in pid.split("_"))
    with open(path, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(pid=pid, cls=cls, title=pid.replace("_", " ").title()))
    print(f"created {path}\nnext: python -m inkyframe.dev render {pid} --sample")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m inkyframe.dev", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    for name, fn in (("render", cmd_render), ("gallery", cmd_gallery)):
        sp = sub.add_parser(name)
        if name == "render":
            sp.add_argument("plugin")
        sp.add_argument("--sample", action="store_true", help="use offline sample data")
        sp.add_argument("--lang", choices=ORDER)
        sp.add_argument("--time", help="pretend time HH:MM")
        sp.add_argument("--theme", choices=list(THEMES), help="display design")
        sp.add_argument("--out", default=OUT)
        sp.set_defaults(fn=fn)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    sp = sub.add_parser("new")
    sp.add_argument("id")
    sp.set_defaults(fn=cmd_new)
    a = ap.parse_args(argv)
    store.load()
    P.discover()
    a.fn(a)


if __name__ == "__main__":
    main()
