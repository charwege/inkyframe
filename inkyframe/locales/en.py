NAME = "English"
STRINGS = {}          # English is the source language

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAYS_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_LETTERS = "MTWTFSS"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
MONTHS_GEN = MONTHS
MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FIRST_WEEKDAY = 6
# placeholders: {wd} weekday, {d} day, {m} month number, {mon} month name, {mg} month in a date,
#               {ms} short month, {y} year
LONG_DATE = "{wd}, {mon} {d}"
LONG_DATE_NO_WD = "{mon} {d}"
LONG_DATE_YEAR = "{mon} {d}, {y}"
SHORT_DATE = "{ms} {d}"
DECIMAL, THOUSANDS = ".", ","
QUOTE_MARKS = ("“", "”")
MOON = ["New moon", "Waxing crescent", "First quarter", "Waxing gibbous", "Full moon",
        "Waning gibbous", "Last quarter", "Waning crescent"]
QUOTES = None         # taken from plugins/quote.py
QUESTIONS = None
