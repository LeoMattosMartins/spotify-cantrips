from __future__ import annotations

from cantrips.config import AppConfig
from cantrips.models import GestureEvent
from cantrips.spotify_client import SpotifyController
from cantrips.state import EngineState


class ActionDispatcher:
    def __init__(self, spotify: SpotifyController, state: EngineState, config: AppConfig) -> None:
        self.spotify = spotify
        self.state = state
        self.config = config

    def dispatch(self, event: GestureEvent) -> dict:
        if event.name == "summon_hud":
            self.state.system_active = True
            return {"type": "system", "active": True}

        if event.name == "dismiss_hud":
            self.state.system_active = False
            return {"type": "system", "active": False}

        if event.name in {"next_track", "previous_track"}:
            if not self.state.can_dispatch_swipe():
                return {"type": "noop"}
            if not self.state.can_dispatch_discrete():
                return {"type": "noop"}
            if event.name == "next_track":
                self.spotify.next_track()
            else:
                self.spotify.previous_track()
            return {"type": "action", "name": event.name}

        if event.name in {"play", "pause"}:
            if not self.state.can_dispatch_discrete():
                return {"type": "noop"}
            if event.name == "play":
                self.spotify.play()
            else:
                self.spotify.pause()
            return {"type": "action", "name": event.name}

        return {"type": "noop"}
