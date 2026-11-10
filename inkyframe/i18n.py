"""Display languages.

Every language is one file in inkyframe/locales/<code>.py with:
  NAME           native name shown in the web app
  STRINGS        {"English text": "translation"} – keys are the English texts plugins pass to ctx.t()
  WEEKDAYS, WEEKDAYS_SHORT, WEEKDAY_LETTERS, MONTHS, MONTHS_GEN (month in a date, e.g. Polish genitive)
  FIRST_WEEKDAY  0 = Monday, 6 = Sunday
  LONG_DATE, LONG_DATE_NO_WD, LONG_DATE_YEAR, SHORT_DATE   format patterns, see en.py
  DECIMAL, THOUSANDS, QUOTE_MARKS
  QUOTES, QUESTIONS  content for the "Thought of the day" plugin
Adding a language = copying en.py, translating it and adding the code to ORDER below.
"""
import importlib

ORDER = ["en", "de", "fr", "es", "it", "pt", "nl", "sv", "da", "nb", "fi", "pl"]
_cache = {}


def locale(lang):
    lang = lang if lang in ORDER else "en"
    if lang not in _cache:
        mod = importlib.import_module(f"inkyframe.locales.{lang}")
        from . import layouts
        for k, v in layouts.extra_strings(lang).items():      # texts of the studio layouts
            mod.STRINGS.setdefault(k, v)
        _cache[lang] = mod
    return _cache[lang]


def languages():
    return [(code, locale(code).NAME) for code in ORDER]


def tr(lang, en, de=None):
    """Translate an English text. German may come inline (ctx.t("Hello", "Hallo"))."""
    if lang == "en" or lang not in ORDER:
        return en
    if lang == "de" and de is not None:
        return de
    return locale(lang).STRINGS.get(en) or (de if lang == "de" else None) or en


def get(lang, attr):
    """Locale attribute with English fallback."""
    return getattr(locale(lang), attr, None) or getattr(locale("en"), attr)
