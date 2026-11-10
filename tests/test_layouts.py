"""Studio layouts: every layout a design ships must render in every language without falling back."""
import os
import tempfile

os.environ.setdefault("INKYFRAME_DATA", tempfile.mkdtemp())

import pytest  # noqa: E402

from inkyframe import i18n, layouts, store  # noqa: E402
from inkyframe import plugin as P  # noqa: E402

store.load()
P.discover()


@pytest.mark.parametrize("theme", layouts.STUDIO)
@pytest.mark.parametrize("pid", layouts.PLUGINS)
def test_layout(theme, pid):
    if not layouts.has(theme, pid):
        pytest.skip("no layout yet")
    layouts.STRICT = True
    try:
        for lang in i18n.ORDER:
            cfg = store.get()
            cfg["language"], cfg["theme"] = lang, theme
            img = P.render(pid, cfg, sample=True)
            assert img.size == (800, 480) and img.mode == "RGB"
            assert img.info.get("studio"), f"{theme}/{pid}/{lang} fell back to the regular screen"
    finally:
        layouts.STRICT = False
