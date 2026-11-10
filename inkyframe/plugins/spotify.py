"""Spotify "Now playing" – album cover + title.

Setup (once):
  1. developer.spotify.com/dashboard → create an app, tick "Web API",
     redirect URI exactly: http://127.0.0.1:8888/callback
  2. Enter client ID + secret in the web app → "Connect".
  3. After logging in, your phone shows an unreachable 127.0.0.1 page. Copy that whole
     address and paste it into the web app. Done.
Spotify only allows plain-http redirect URIs on loopback addresses – hence the copy & paste.
"""
import base64
import secrets
import threading
import time
import urllib.parse

import requests

from inkyframe import gfx
from inkyframe.gfx import BLACK, WHITE
from inkyframe.plugin import Plugin, Setting

SCOPES = "user-read-currently-playing user-read-playback-state user-read-recently-played"
REDIRECT = "http://127.0.0.1:8888/callback"


class Spotify(Plugin):
    id = "spotify"
    name = "Spotify"
    icon = "♫"
    description = "Shows the cover of what's playing. Can take over the display while music plays."
    author = "inkyframe"
    can_interrupt = True
    theme_remap = False      # keep photos/covers untouched in dark designs
    settings = [
        Setting("setup", "info", "1) Create an app at developer.spotify.com/dashboard (Web API). "
                "2) Redirect URI exactly: " + REDIRECT + "  3) Save ID + secret, then Connect. "
                "4) After login your phone shows an error page – copy its full address into “Finish”."),
        Setting("client_id", "text", "Client ID", default=""),
        Setting("client_secret", "secret", "Client secret", default=""),
        Setting("layout", "select", "Layout", default="split",
                options=[("split", "Cover + title"), ("cover", "Cover only")]),
        Setting("linger_minutes", "number", "Keep cover after pause (min)", default=5, min=0, max=60),
        Setting("connect", "action", "Connect with Spotify"),
        Setting("finish", "action", "Finish connection", input="Paste the 127.0.0.1 address here"),
        Setting("disconnect", "action", "Disconnect"),
    ]

    def __init__(self):
        self._lock = threading.Lock()
        self._token = {"value": None, "exp": 0}
        self._np = {"at": 0, "data": None}
        self._last = {"track": None, "playing_seen": 0}
        self._state = None

    # ---------------------------------------------------------------- OAuth
    @staticmethod
    def connected(ctx):
        s = ctx.settings
        return bool(s.get("client_id") and s.get("client_secret") and s.get("refresh_token"))

    @staticmethod
    def _basic(s):
        return base64.b64encode(f"{s['client_id']}:{s['client_secret']}".encode()).decode()

    def action_connect(self, ctx, value=None):
        s = ctx.settings
        if not (s.get("client_id") and s.get("client_secret")):
            raise ValueError("Save client ID and secret first.")
        self._state = secrets.token_urlsafe(12)
        q = {"client_id": s["client_id"], "response_type": "code", "redirect_uri": REDIRECT,
             "scope": SCOPES, "state": self._state, "show_dialog": "true"}
        return {"open_url": "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(q)}

    def action_finish(self, ctx, value=None):
        s, pasted = ctx.settings, (value or "").strip()
        code = pasted
        if "code=" in pasted or "error=" in pasted:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query)
            if "error" in qs:
                raise ValueError(f"Spotify says: {qs['error'][0]}")
            code = qs["code"][0]
            st = qs.get("state", [None])[0]
            if self._state and st and st != self._state:
                raise ValueError("State mismatch – please start the connection again.")
        r = requests.post("https://accounts.spotify.com/api/token", timeout=15,
                          headers={"Authorization": f"Basic {self._basic(s)}"},
                          data={"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT})
        if r.status_code != 200:
            raise ValueError(f"Token request failed: {r.text[:200]}")
        tok = r.json()
        with self._lock:
            self._token.update(value=tok["access_token"], exp=time.time() + tok["expires_in"] - 60)
        ctx.save_settings(refresh_token=tok["refresh_token"])
        return {"message": "Connected to Spotify."}

    def action_disconnect(self, ctx, value=None):
        ctx.save_settings(refresh_token="")
        with self._lock:
            self._token.update(value=None, exp=0)
        return {"message": "Disconnected."}

    def _access(self, ctx):
        with self._lock:
            if self._token["value"] and time.time() < self._token["exp"]:
                return self._token["value"]
        s = ctx.settings
        r = requests.post("https://accounts.spotify.com/api/token", timeout=15,
                          headers={"Authorization": f"Basic {self._basic(s)}"},
                          data={"grant_type": "refresh_token", "refresh_token": s["refresh_token"]})
        r.raise_for_status()
        tok = r.json()
        if tok.get("refresh_token"):
            ctx.save_settings(refresh_token=tok["refresh_token"])
        with self._lock:
            self._token.update(value=tok["access_token"], exp=time.time() + tok["expires_in"] - 60)
            return self._token["value"]

    # ---------------------------------------------------------------- data
    @staticmethod
    def _track(item):
        imgs = item.get("album", {}).get("images", [])
        return {"title": item.get("name", ""),
                "artist": ", ".join(a["name"] for a in item.get("artists", [])),
                "album": item.get("album", {}).get("name", ""),
                "album_id": item.get("album", {}).get("id", ""),
                "duration_ms": item.get("duration_ms"),
                "image": imgs[0]["url"] if imgs else None}

    def now_playing(self, ctx, max_age=10):
        if not self.connected(ctx):
            return None
        now = time.time()
        if now - self._np["at"] < max_age:
            return self._np["data"]
        data = None
        try:
            r = requests.get("https://api.spotify.com/v1/me/player/currently-playing",
                             headers={"Authorization": f"Bearer {self._access(ctx)}"},
                             params={"additional_types": "episode"}, timeout=10)
            if r.status_code == 200 and r.content:
                j = r.json()
                item = j.get("item")
                if item:
                    if item.get("type") == "episode":
                        show = item.get("show", {})
                        imgs = item.get("images") or show.get("images", [])
                        info = {"title": item["name"], "artist": show.get("publisher", ""),
                                "album": show.get("name", ""), "album_id": item.get("id", ""),
                                "duration_ms": item.get("duration_ms"),
                                "image": imgs[0]["url"] if imgs else None}
                    else:
                        info = self._track(item)
                    data = dict(info, playing=bool(j.get("is_playing")))
            elif r.status_code == 204:
                data = {"playing": False}
        except requests.RequestException:
            data = self._np["data"]
        self._np.update(at=now, data=data)
        if data and data.get("title"):
            self._last["track"] = {k: v for k, v in data.items() if k != "playing"}
        if data and data.get("playing"):
            self._last["playing_seen"] = now
        return data

    def wants_display(self, ctx):
        if not self.connected(ctx):
            return False
        np = self.now_playing(ctx)
        if np and np.get("playing"):
            return True
        linger = float(ctx.settings.get("linger_minutes", 5)) * 60
        return bool(self._last["playing_seen"]) and time.time() - self._last["playing_seen"] < linger

    def status(self, ctx):
        if not self.connected(ctx):
            return "Not connected"
        np = self._np["data"]
        if np and np.get("title"):
            return f"Connected · {'playing' if np.get('playing') else 'paused'}: {np['title']} – {np['artist']}"
        return "Connected"

    def content_key(self, ctx):
        np = self.now_playing(ctx)
        t = (np if np and np.get("title") else None) or self._last["track"]
        # Only redraw when the album changes – saves the e-ink panel on every new song.
        return f"{t.get('album_id')}|{ctx.settings.get('layout')}|{ctx.lang}" if t else "none"

    def _recent(self, ctx):
        try:
            r = requests.get("https://api.spotify.com/v1/me/player/recently-played",
                             headers={"Authorization": f"Bearer {self._access(ctx)}"},
                             params={"limit": 1}, timeout=10)
            items = r.json().get("items", [])
            return self._track(items[0]["track"]) if items else None
        except Exception:
            return None

    def sample(self, ctx):
        from PIL import Image, ImageDraw
        cov = Image.new("RGB", (640, 640))
        d = ImageDraw.Draw(cov)
        for i in range(640):
            d.line((0, i, 640, i), fill=(int(40 + i / 4), 30, int(200 - i / 5)))
        d.ellipse((160, 160, 480, 480), fill=(240, 200, 40))
        return {"title": "A Rather Long Song Title (Remastered)", "artist": "The Performers",
                "album": "Album of the Week", "cover": cov, "playing": True, "duration_ms": 245000}

    # ---------------------------------------------------------------- view
    def view(self, ctx, data):
        """Display-ready facts for the studio layouts – see docs/views/spotify.md.

        data: a track dict (as from sample()/now_playing()); render() adds "state"
        ("playing" | "paused" | "recent") and the fetched "cover" image.
        """
        state = data.get("state") or ("playing" if data.get("playing", True) else "paused")
        label = {"paused": ctx.t("Paused", "Pausiert"),
                 "recent": ctx.t("Recently played", "Zuletzt gehört")}.get(state) or ctx.t("Now playing", "Läuft gerade")
        cover = data.get("cover")
        if cover is not None and cover.mode != "RGB":
            cover = cover.convert("RGB")
        ms = data.get("duration_ms")
        secs = int(round(ms / 1000)) if isinstance(ms, (int, float)) and ms > 0 else None
        if secs is None:
            dur = ""
        elif secs >= 3600:
            dur = f"{secs // 3600}:{secs % 3600 // 60:02d}:{secs % 60:02d}"
        else:
            dur = f"{secs // 60}:{secs % 60:02d}"
        return {
            "title": self.display_name(ctx.lang), "source": "Spotify",
            "label": label, "state": state, "playing": state == "playing",
            "track": data.get("title", ""), "artist": data.get("artist", ""), "album": data.get("album", ""),
            "image": cover, "has_image": cover is not None,
            "duration": secs, "duration_text": dur,
            "cover_only": ctx.settings.get("layout") == "cover",
            "now": ctx.now, "today": ctx.today, "date": ctx.date(ctx.today, year=True),
            "time": f"{ctx.now:%H:%M}", "place": ctx.location.get("name", ""),
        }

    # ---------------------------------------------------------------- drawing
    def render(self, ctx, data=None):
        label = ctx.t("Now playing", "Läuft gerade")
        state = "playing"
        track = data
        if track is None:
            if not self.connected(ctx):
                return ctx.message(ctx.t("Spotify is not connected yet", "Spotify ist noch nicht verbunden"),
                                   ctx.t("Set it up in the web app under Plugins → Spotify.",
                                         "In der Web-App unter Plugins → Spotify einrichten."))
            np = self.now_playing(ctx, max_age=0)
            if np and np.get("title"):
                track = np
                if not np.get("playing"):
                    label, state = ctx.t("Paused", "Pausiert"), "paused"
            else:
                track = self._last["track"] or self._recent(ctx)
                label, state = ctx.t("Recently played", "Zuletzt gehört"), "recent"
        if not track:
            return ctx.message(ctx.t("Nothing playing", "Gerade läuft nichts"),
                               ctx.t("The cover appears as soon as music plays.",
                                     "Sobald Musik spielt, erscheint hier das Cover."))
        cover = track.get("cover") or (ctx.fetch_image(track["image"]) if track.get("image") else None)
        data = dict(track, cover=cover, state=state)
        from inkyframe import layouts
        v = self.view(ctx, data)
        special = layouts.render(ctx, self.id, v)
        if special is not None:
            return special
        side = ctx.H
        img, d = ctx.canvas(WHITE)
        if ctx.settings.get("layout") == "cover" and cover:
            img.paste(ctx.punch(ctx.cover_fit(cover, side, side)), ((ctx.W - side) // 2, 0))
            return img
        if cover:
            img.paste(ctx.punch(ctx.cover_fit(cover, side, side)), (0, 0))
        RX, RW = side + 28, ctx.W - side - 52
        d.text((RX, 34), label.upper(), font=gfx.font("sans-bold", 15), fill=BLACK)
        d.line((RX, 58, RX + RW, 58), fill=BLACK, width=2)
        f, lines, lh = gfx.fit_text(d, track["title"], "serif-bold", RW, 190, 40, 20, 1.18)
        y = 76
        gfx.draw_lines(d, lines, f, lh, RX, y, RW, align="left")
        y += len(lines) * lh + 18
        f2, l2, lh2 = gfx.fit_text(d, track["artist"], "serif", RW, 90, 26, 16, 1.2)
        gfx.draw_lines(d, l2, f2, lh2, RX, y, RW, align="left")
        y += len(l2) * lh2 + 14
        f3 = gfx.font("serif-italic", 18)
        for line in gfx.wrap(d, track.get("album", ""), f3, RW)[:3]:
            d.text((RX, y), line, font=f3, fill=BLACK)
            y += 24
        d.text((RX, ctx.H - 40), "♫ Spotify", font=gfx.font("symbols", 16), fill=BLACK)
        return img
