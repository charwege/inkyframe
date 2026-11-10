NAME = "Deutsch"
STRINGS = {}          # German texts are passed inline: ctx.t("Hello", "Hallo")

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
WEEKDAYS_SHORT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
WEEKDAY_LETTERS = "MDMDFSS"
MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
          "September", "Oktober", "November", "Dezember"]
MONTHS_GEN = MONTHS
MONTHS_SHORT = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
FIRST_WEEKDAY = 0
LONG_DATE = "{wd}, {d}. {mg}"
LONG_DATE_NO_WD = "{d}. {mg}"
LONG_DATE_YEAR = "{d}. {mg} {y}"
SHORT_DATE = "{d:02d}.{m:02d}."
DECIMAL, THOUSANDS = ",", "."
QUOTE_MARKS = ("„", "“")
MOON = ["Neumond", "Zunehmende Sichel", "Erstes Viertel", "Zunehmender Mond", "Vollmond",
        "Abnehmender Mond", "Letztes Viertel", "Abnehmende Sichel"]
QUOTES = None         # taken from plugins/quote.py
QUESTIONS = None
