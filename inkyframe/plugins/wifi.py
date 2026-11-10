"""Guest Wi-Fi – a QR code your visitors scan to join the network."""
from inkyframe import gfx
from inkyframe.plugin import Plugin, Setting


def wifi_payload(ssid, password, security="WPA", hidden=False):
    esc = lambda s: "".join("\\" + c if c in '\\;,:"' else c for c in s)
    parts = [f"T:{security}" if security != "nopass" else "T:nopass", f"S:{esc(ssid)}"]
    if security != "nopass":
        parts.append(f"P:{esc(password)}")
    if hidden:
        parts.append("H:true")
    return "WIFI:" + ";".join(parts) + ";;"


class GuestWifi(Plugin):
    id = "wifi"
    name = {"en": "Guest Wi-Fi", "de": "Gäste-WLAN"}
    icon = "📶"
    description = "QR code to join your Wi-Fi – handy to show when visitors arrive."
    author = "inkyframe"
    settings = [
        Setting("ssid", "text", "Network name (SSID)", default=""),
        Setting("password", "secret", "Password", default=""),
        Setting("security", "select", "Security", default="WPA",
                options=[("WPA", "WPA/WPA2/WPA3"), ("WEP", "WEP"), ("nopass", "Open network")]),
        Setting("hidden", "bool", "Hidden network", default=False),
        Setting("show_password", "bool", "Show password as text", default=True),
        Setting("note", "text", "Note (optional)", default=""),
    ]

    def content_key(self, ctx):
        return f"{sorted(ctx.settings.items())}|{ctx.lang}"

    def sample(self, ctx):
        return {"ssid": ctx.t("Guests", "Gäste"), "password": "sunflower-42",
                "security": "WPA", "hidden": False, "show_password": True,
                "note": ctx.t("Welcome! Make yourself at home.", "Herzlich willkommen!")}

    def render(self, ctx, data=None):
        s = data or ctx.settings
        if not s.get("ssid"):
            return ctx.message(ctx.t("Wi-Fi not set up yet", "WLAN noch nicht eingerichtet"),
                               ctx.t("Enter network name and password under Plugins → Guest Wi-Fi.",
                                     "Netzwerkname und Passwort unter Plugins → Gäste-WLAN eintragen."))
        img, d = ctx.canvas()
        size = 420
        ctx.qr(d, wifi_payload(s["ssid"], s.get("password", ""), s.get("security", "WPA"), s.get("hidden")),
               30, (ctx.H - size) // 2, size)
        RX, RW = 480, ctx.W - 480 - 30
        # simple Wi-Fi symbol
        cx, cy = RX + 30, 92
        for r in (40, 27, 14):
            d.arc((cx - r, cy - r, cx + r, cy + r), 225, 315, fill=ctx.ACCENT, width=6)
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=ctx.ACCENT)
        d.text((RX, 120), ctx.t("Guest Wi-Fi", "Gäste-WLAN"), font=gfx.font("serif", 34), fill=ctx.BLACK)
        d.text((RX, 160), ctx.t("Scan with your phone camera", "Mit der Handykamera scannen"),
               font=gfx.font("serif-italic", 17), fill=ctx.BLACK)
        d.line((RX, 196, RX + RW, 196), fill=ctx.BLACK, width=1)
        y = 212
        d.text((RX, y), ctx.t("Network", "Netzwerk").upper(), font=gfx.font("sans-bold", 13), fill=ctx.BLACK)
        f, lines, lh = gfx.fit_text(d, s["ssid"], "sans-bold", RW, 70, 30, 16, 1.15)
        gfx.draw_lines(d, lines, f, lh, RX, y + 20, RW, align="left")
        y += 30 + len(lines) * lh
        if s.get("show_password") and s.get("security") != "nopass" and s.get("password"):
            d.text((RX, y), ctx.t("Password", "Passwort").upper(), font=gfx.font("sans-bold", 13), fill=ctx.BLACK)
            f, lines, lh = gfx.fit_text(d, s["password"], "sans", RW, 70, 26, 14, 1.15)
            gfx.draw_lines(d, lines, f, lh, RX, y + 20, RW, align="left")
            y += 30 + len(lines) * lh
        if s.get("note"):
            fn = gfx.font("serif-italic", 18)
            lines = gfx.wrap(d, s["note"], fn, RW)[:3]
            ny = max(y + 10, ctx.H - 40 - 24 * len(lines))
            for line in lines:
                d.text((RX, ny), line, font=fn, fill=ctx.BLACK)
                ny += 24
        return img
