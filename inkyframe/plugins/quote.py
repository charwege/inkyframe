"""Thought of the day: a quote or a question, changing daily. Add your own in the web app."""
import hashlib

from inkyframe import gfx, i18n
from inkyframe.gfx import BLACK
from inkyframe.plugin import Plugin, Setting

QUOTES_EN = [
    ("It is not that we have a short time to live, but that we waste a lot of it.", "Seneca"),
    ("We suffer more often in imagination than in reality.", "Seneca"),
    ("It is not because things are difficult that we do not dare; it is because we do not dare that they are difficult.", "Seneca"),
    ("While we are postponing, life speeds by.", "Seneca"),
    ("The happiness of your life depends upon the quality of your thoughts.", "Marcus Aurelius"),
    ("Men are disturbed not by things, but by the views which they take of them.", "Epictetus"),
    ("Knowing is not enough; we must apply. Willing is not enough; we must do.", "Goethe"),
    ("Nothing is worth more than this day.", "Goethe"),
    ("It is only with the heart that one can see rightly; what is essential is invisible to the eye.", "Antoine de Saint-Exupéry"),
    ("A journey of a thousand miles begins with a single step.", "Laozi"),
    ("Knowing others is intelligence; knowing yourself is true wisdom.", "Laozi"),
    ("No man ever steps in the same river twice.", "Heraclitus"),
    ("Life can only be understood backwards; but it must be lived forwards.", "Søren Kierkegaard"),
    ("He who has a why to live can bear almost any how.", "Friedrich Nietzsche"),
    ("Be patient toward all that is unsolved in your heart and try to love the questions themselves.", "Rainer Maria Rilke"),
    ("Have courage to use your own understanding!", "Immanuel Kant"),
    ("The limits of my language mean the limits of my world.", "Ludwig Wittgenstein"),
    ("Experience is the name everyone gives to their mistakes.", "Oscar Wilde"),
    ("I know that I know nothing.", "Socrates"),
    ("Well begun is half done.", "Aristotle"),
    ("The unexamined life is not worth living.", "Socrates"),
    ("Waste no more time arguing about what a good man should be. Be one.", "Marcus Aurelius"),
    ("Well done is better than well said.", "Benjamin Franklin"),
    ("Our life is frittered away by detail. Simplify, simplify.", "Henry David Thoreau"),
]

QUOTES_DE = [
    ("Es ist nicht wenig Zeit, die wir haben, sondern es ist viel Zeit, die wir nicht nutzen.", "Seneca"),
    ("Wir leiden öfter in der Vorstellung als in der Wirklichkeit.", "Seneca"),
    ("Nicht weil es schwer ist, wagen wir es nicht, sondern weil wir es nicht wagen, ist es schwer.", "Seneca"),
    ("Während man es aufschiebt, verrinnt das Leben.", "Seneca"),
    ("Das Glück deines Lebens hängt von der Beschaffenheit deiner Gedanken ab.", "Marc Aurel"),
    ("Nicht die Dinge selbst beunruhigen die Menschen, sondern ihre Urteile über die Dinge.", "Epiktet"),
    ("Es ist nicht genug zu wissen, man muss auch anwenden; es ist nicht genug zu wollen, man muss auch tun.", "Goethe"),
    ("Nichts ist höher zu schätzen als der Wert des Tages.", "Goethe"),
    ("Es hört doch jeder nur, was er versteht.", "Goethe"),
    ("Man sieht nur mit dem Herzen gut. Das Wesentliche ist für die Augen unsichtbar.", "Antoine de Saint-Exupéry"),
    ("Eine Reise von tausend Meilen beginnt mit dem ersten Schritt.", "Laotse"),
    ("Wer andere kennt, ist klug. Wer sich selbst kennt, ist weise.", "Laotse"),
    ("Man kann nicht zweimal in denselben Fluss steigen.", "Heraklit"),
    ("Das Leben kann nur rückwärts verstanden werden, muss aber vorwärts gelebt werden.", "Søren Kierkegaard"),
    ("Wer ein Warum zum Leben hat, erträgt fast jedes Wie.", "Friedrich Nietzsche"),
    ("Habe Geduld gegen alles Ungelöste in deinem Herzen und versuche, die Fragen selbst liebzuhaben.", "Rainer Maria Rilke"),
    ("Ich weiß nicht, ob es besser wird, wenn es anders wird. Aber es muss anders werden, wenn es gut werden soll.", "Georg Christoph Lichtenberg"),
    ("Habe Mut, dich deines eigenen Verstandes zu bedienen!", "Immanuel Kant"),
    ("Die Grenzen meiner Sprache bedeuten die Grenzen meiner Welt.", "Ludwig Wittgenstein"),
    ("Der Mensch ist nur da ganz Mensch, wo er spielt.", "Friedrich Schiller"),
    ("Erfahrung ist der Name, den jeder seinen Fehlern gibt.", "Oscar Wilde"),
    ("Stets findet Überraschung statt. Da, wo man’s nicht erwartet hat.", "Wilhelm Busch"),
    ("Mut steht am Anfang des Handelns, Glück am Ende.", "Demokrit"),
    ("Ich weiß, dass ich nichts weiß.", "Sokrates"),
    ("Die Natur macht keine Sprünge.", "Gottfried Wilhelm Leibniz"),
]

QUESTIONS_EN = [
    "What are you looking forward to today – specifically?",
    "What small step today would feel big in a year?",
    "Who could you honestly thank today?",
    "What would you do today if you weren't afraid of the outcome?",
    "Which one thing would make today a good day?",
    "What can you leave out today?",
    "What are you grateful for right now, without thinking twice?",
    "Which conversation have you been putting off?",
    "What did you do for the first time recently?",
    "How will you know tonight that today was a good day?",
    "Who haven't you called in far too long?",
    "What would your future self advise you today?",
    "Which good habit gets too little time?",
    "Where can you be generous today?",
    "What matters to you that isn't in any calendar?",
    "When did you last do something purely out of curiosity?",
    "What would you tell a friend in your situation?",
    "Which decision have you actually already made?",
    "What surprised you this week?",
    "What do you want to make time for today?",
    "Which question do you ask yourself too rarely?",
    "What makes you proud right now?",
    "What can you make simpler today?",
    "When were you last truly focused – and why?",
    "What small joy can you give someone today?",
    "What would you learn if you had a year off?",
    "What made you laugh out loud recently?",
    "Which idea won't let go of you?",
    "What do you need today to stay true to yourself?",
]

QUESTIONS_DE = [
    "Worauf freust du dich heute – ganz konkret?",
    "Was wäre heute ein kleiner Schritt, der sich in einem Jahr groß anfühlt?",
    "Wem könntest du heute ein ehrliches Danke sagen?",
    "Was würdest du heute tun, wenn du keine Angst vor dem Ergebnis hättest?",
    "Welche eine Sache würde den Tag zu einem guten Tag machen?",
    "Was darfst du heute weglassen?",
    "Wofür bist du gerade dankbar, ohne lange nachzudenken?",
    "Welches Gespräch schiebst du vor dir her?",
    "Was hast du zuletzt zum ersten Mal gemacht?",
    "Woran merkst du heute Abend, dass der Tag gut war?",
    "Wen hast du schon zu lange nicht mehr angerufen?",
    "Was würde dein zukünftiges Ich dir heute raten?",
    "Welche Gewohnheit tut dir gut – und kommt zu kurz?",
    "Wo kannst du heute großzügig sein?",
    "Was ist dir wichtig, das in keinem Kalender steht?",
    "Wann hast du zuletzt etwas nur aus Neugier getan?",
    "Was würdest du einem Freund in deiner Lage sagen?",
    "Welche Entscheidung ist eigentlich längst getroffen?",
    "Was hat dich diese Woche überrascht?",
    "Wofür möchtest du dir heute Zeit nehmen?",
    "Welche Frage stellst du dir zu selten?",
    "Was macht dich gerade stolz?",
    "Was kannst du heute einfacher machen?",
    "Wann warst du zuletzt richtig konzentriert – und warum?",
    "Welche kleine Freude kannst du heute jemandem machen?",
    "Was würdest du lernen, wenn du ein Jahr frei hättest?",
    "Was soll heute nicht passieren – und was kannst du dafür tun?",
    "Worüber hast du zuletzt laut gelacht?",
    "Welche Idee lässt dich gerade nicht los?",
    "Was brauchst du heute, um gut bei dir zu bleiben?",
]




def content(lang):
    """(quotes, questions) for a display language; languages bring their own in locales/<lang>.py."""
    if lang == "de":
        return QUOTES_DE, QUESTIONS_DE
    loc = i18n.locale(lang)
    if lang != "en" and getattr(loc, "QUOTES", None) and getattr(loc, "QUESTIONS", None):
        return loc.QUOTES, loc.QUESTIONS
    return QUOTES_EN, QUESTIONS_EN


def parse_custom(text):
    out = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        for sep in (" — ", " – ", " - "):
            if sep in line:
                t, a = line.rsplit(sep, 1)
                out.append(("quote", t.strip(), a.strip()))
                break
        else:
            out.append(("question", line, "") if line.endswith("?") else ("quote", line, ""))
    return out


class Quote(Plugin):
    id = "quote"
    name = {"en": "Thought of the Day", "de": "Impuls des Tages"}
    icon = "❝"
    description = "A quote or a question to carry through the day. Changes daily; add your own lines."
    author = "inkyframe"
    settings = [
        Setting("kind", "select", "Content", default="mixed",
                options=[("mixed", "Quotes & questions"), ("quotes", "Quotes only"), ("questions", "Questions only")]),
        Setting("only_custom", "bool", "Only my own entries", default=False),
        Setting("custom", "textarea", "My own entries", default="",
                help="One per line. Quote with author: “Text — Author”. Lines ending in “?” are questions."),
    ]

    def content_key(self, ctx):
        return f"{ctx.today}|{ctx.lang}|{sorted(ctx.settings.items())}"

    def pick(self, ctx):
        s = ctx.settings
        kind = s.get("kind", "mixed")
        quotes, questions = content(ctx.lang)
        pool = []
        if not s.get("only_custom"):
            if kind in ("mixed", "quotes"):
                pool += [("quote", t, a) for t, a in quotes]
            if kind in ("mixed", "questions"):
                pool += [("question", t, "") for t in questions]
        pool += [c for c in parse_custom(s.get("custom")) if kind == "mixed" or c[0] == kind[:-1]]
        if not pool:
            return ("question", ctx.t("No entries yet – add your own in the web app?",
                                      "Keine Einträge – eigene Sätze in der Web-App ergänzen?"), "")
        h = int(hashlib.sha1(ctx.today.isoformat().encode()).hexdigest(), 16)
        return pool[h % len(pool)]

    def sample(self, ctx):
        return ("question", content(ctx.lang)[1][3], "")

    def render(self, ctx, data=None):
        kind, text, author = data or self.pick(ctx)
        img, d = ctx.canvas()
        W, H = ctx.W, ctx.H
        ctx.frame(d)
        label = ctx.t("Question of the day", "Frage des Tages") if kind == "question" \
            else ctx.t("Thought of the day", "Gedanke des Tages")
        lf = gfx.font("serif-italic", 22)
        gfx.text_center(d, label, lf, W // 2, 52, ctx.ACCENT)
        tw = gfx.text_w(d, label, lf)
        for sx in (-1, 1):
            x1 = W // 2 + sx * (tw // 2 + 16)
            d.line((x1, 66, x1 + sx * 60, 66), fill=ctx.ACCENT, width=2)
        box_w, box_h = W - 180, 260 if author else 300
        quote_marks = i18n.get(ctx.lang, "QUOTE_MARKS")
        body = f"{quote_marks[0]}{text}{quote_marks[1]}" if kind == "quote" else text
        f, lines, lh = gfx.fit_text(d, body, "serif" if kind == "quote" else "serif-bold",
                                    box_w, box_h, max_size=64, min_size=22, spacing=1.22)
        total = len(lines) * lh
        top = 100 + (box_h - total) // 2 + (0 if author else 10)
        gfx.draw_lines(d, lines, f, lh, 90, top, box_w)
        if author:
            gfx.text_center(d, f"— {author}", gfx.font("serif-italic", 26), W // 2, top + total + 22)
        return img
