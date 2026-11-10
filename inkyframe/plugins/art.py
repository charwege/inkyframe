"""Art of the day – a public-domain painting from the Art Institute of Chicago open API."""
import hashlib
import json
import math

from PIL import Image, ImageDraw

from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting

API = "https://api.artic.edu/api/v1/artworks/search"
IIIF = "https://www.artic.edu/iiif/2/{}/full/843,/0/default.jpg"
HEADERS = {"AIC-User-Agent": "inkyframe (e-ink picture frame)"}


class ArtOfTheDay(Plugin):
    id = "art"
    name = {"en": "Art of the Day", "de": "Kunst des Tages"}
    icon = "🖼"
    description = "A public-domain painting every day (Art Institute of Chicago), prepared for the 6-colour panel."
    author = "inkyframe"
    theme_remap = False      # keep photos/covers untouched in dark designs
    settings = [
        Setting("kind", "select", "Artworks", default="painting",
                options=[("painting", "Paintings"), ("print", "Prints & drawings"), ("any", "Everything")]),
        Setting("layout", "select", "Layout", default="auto",
                options=[("auto", "Picture + caption"), ("full", "Picture only (fills the frame)")]),
        Setting("saturation", "number", "Colour boost (1 = none)", default=1.3, min=1, max=2),
    ]

    def pick(self, ctx):
        filters = [{"term": {"is_public_domain": True}}, {"exists": {"field": "image_id"}}]
        kind = ctx.settings.get("kind", "painting")
        if kind == "painting":
            filters.append({"term": {"artwork_type_id": 1}})
        elif kind == "print":
            filters.append({"terms": {"artwork_type_id": [18, 13]}})   # print, drawing
        seed = int(hashlib.sha1(f"{ctx.today}{kind}".encode()).hexdigest(), 16)
        query = {"query": {"bool": {"filter": filters}}, "limit": 100, "page": seed % 10 + 1,
                 "fields": ["id", "title", "artist_title", "artist_display", "date_display", "image_id"]}
        res = ctx.fetch_json(API, ttl=12 * 3600, params={"params": json.dumps(query)}, headers=HEADERS)
        items = [a for a in res.get("data", []) if a.get("image_id")]
        if not items:
            raise RuntimeError("no artworks returned")
        art = items[(seed // 10) % len(items)]
        return {"title": art.get("title") or "", "artist": art.get("artist_title")
                or (art.get("artist_display") or "").split("\n")[0], "date": art.get("date_display") or "",
                "image": ctx.fetch_image(IIIF.format(art["image_id"]), ttl=24 * 3600)}

    def sample(self, ctx):
        # A small generated "landscape" so previews work offline.
        img = Image.new("RGB", (600, 450))
        d = ImageDraw.Draw(img)
        for y in range(450):
            t = y / 450
            d.line((0, y, 600, y), fill=(int(70 + 150 * t), int(120 + 80 * t), int(200 - 90 * t)))
        d.ellipse((400, 60, 500, 160), fill=(250, 210, 80))
        for i, col in enumerate([(40, 90, 50), (60, 120, 60), (90, 140, 70)]):
            pts = [(x, 300 + i * 40 + 30 * math.sin(x / (60 + i * 20) + i)) for x in range(0, 601, 20)]
            d.polygon(pts + [(600, 450), (0, 450)], fill=col)
        return {"title": "Evening over the Hills", "artist": "Sample Painter", "date": "1889", "image": img}

    def render(self, ctx, data=None):
        art = data or self.pick(ctx)
        W, H = ctx.W, ctx.H
        pic = gfx.punch_for_eink(art["image"], saturation=float(ctx.settings.get("saturation", 1.3)))
        if ctx.settings.get("layout") == "full":
            img, _ = ctx.canvas()
            img.paste(ctx.cover_fit(pic, W, H), (0, 0))
            return img

        img, d = ctx.canvas()
        landscape = pic.width / pic.height > 1.25
        if landscape:          # picture on top, caption strip below
            box_w, box_h = W - 40, H - 100
        else:                  # picture left, caption right
            box_w, box_h = W - 290, H - 40
        scale = min(box_w / pic.width, box_h / pic.height)
        pw, ph = int(pic.width * scale), int(pic.height * scale)
        pic = pic.resize((pw, ph), Image.LANCZOS)
        if landscape:
            px, py = (W - pw) // 2, 20 + (box_h - ph) // 2
            img.paste(pic, (px, py))
            d.rectangle((px - 1, py - 1, px + pw, py + ph), outline=ctx.BLACK)
            cap = f"{art['title']}"
            f, lines, lh = gfx.fit_text(d, cap, "serif-italic", W - 80, 34, 24, 14)
            gfx.draw_lines(d, lines[:1], f, lh, 40, H - 72, W - 80)
            ctx.text_center(d, " · ".join(x for x in (art["artist"], art["date"]) if x),
                            gfx.font("sans", 15), W // 2, H - 38)
        else:
            px, py = 20 + (box_w - pw) // 2, (H - ph) // 2
            img.paste(pic, (px, py))
            d.rectangle((px - 1, py - 1, px + pw, py + ph), outline=ctx.BLACK)
            RX, RW = W - 250, 220
            d.text((RX, 40), ctx.t("Art of the day", "Kunst des Tages").upper(), font=gfx.font("sans-bold", 13), fill=ctx.ACCENT)
            d.line((RX, 62, RX + RW, 62), fill=ctx.BLACK, width=1)
            f, lines, lh = gfx.fit_text(d, art["title"], "serif-italic", RW, 200, 30, 16, 1.2)
            gfx.draw_lines(d, lines, f, lh, RX, 80, RW, align="left")
            y = 80 + len(lines) * lh + 18
            for line in gfx.wrap(d, art["artist"], gfx.font("serif", 20), RW)[:3]:
                d.text((RX, y), line, font=gfx.font("serif", 20), fill=ctx.BLACK)
                y += 26
            d.text((RX, y + 4), art["date"], font=gfx.font("sans", 16), fill=ctx.BLACK)
            d.text((RX, H - 46), "Art Institute of Chicago", font=gfx.font("sans", 12), fill=ctx.BLACK)
            d.text((RX, H - 30), ctx.t("Public domain", "Gemeinfrei"), font=gfx.font("sans", 12), fill=ctx.BLACK)
        return img
