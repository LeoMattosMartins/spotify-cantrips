from __future__ import annotations

import os
from typing import Any

import spotipy
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth


class SpotifyController:
    def __init__(self) -> None:
        self.sp = self._build_client()

    def _build_client(self) -> spotipy.Spotify | None:
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
        if not all([client_id, client_secret, redirect_uri]):
            print("[Cantrips] Spotify credentials missing. Engine running in dry mode.")
            return None

        scope = "user-read-playback-state user-modify-playback-state"
        auth = SpotifyOAuth(scope=scope, open_browser=True, cache_path=".spotify-cache")
        return spotipy.Spotify(auth_manager=auth)

    def get_active_device(self) -> str | None:
        if not self.sp:
            return None
        data = self.sp.devices()
        for device in data.get("devices", []):
            if device.get("is_active"):
                return str(device.get("id"))
        return None

    def _with_active_device(self, callback: Any) -> None:
        if not self.sp:
            return
        device_id = self.get_active_device()
        if not device_id:
            return
        try:
            callback(device_id)
        except SpotifyException:
            return

    def play(self) -> None:
        self._with_active_device(lambda device_id: self.sp.start_playback(device_id=device_id))

    def pause(self) -> None:
        self._with_active_device(lambda device_id: self.sp.pause_playback(device_id=device_id))

    def next_track(self) -> None:
        self._with_active_device(lambda device_id: self.sp.next_track(device_id=device_id))

    def previous_track(self) -> None:
        self._with_active_device(lambda device_id: self.sp.previous_track(device_id=device_id))

    def current_track(self) -> dict[str, str]:
        if not self.sp:
            return {"name": "Unknown", "artist": "Unknown"}
        playback = self.sp.current_playback()
        item = (playback or {}).get("item") or {}
        artists = item.get("artists") or []
        return {
            "name": item.get("name", "Unknown"),
            "artist": artists[0].get("name", "Unknown") if artists else "Unknown",
        }
