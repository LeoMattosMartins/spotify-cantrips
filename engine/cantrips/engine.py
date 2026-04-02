from __future__ import annotations

import time

import cv2
import mediapipe as mp

from cantrips.bridge import TelemetryBridge
from cantrips.config import CONFIG
from cantrips.dispatcher import ActionDispatcher
from cantrips.gestures import GestureRegistry
from cantrips.models import GestureContext
from cantrips.spotify_client import SpotifyController
from cantrips.state import EngineState


class CantripsEngine:
    def __init__(self) -> None:
        self.config = CONFIG
        self.bridge = TelemetryBridge(self.config.websocket_host, self.config.websocket_port)
        self.state = EngineState(
            self.config.discrete_cooldown_ms,
            self.config.swipe_command_cooldown_ms,
        )
        self.spotify = SpotifyController()
        self.dispatcher = ActionDispatcher(self.spotify, self.state, self.config)
        self.registry = GestureRegistry(self.config)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=self.config.hand_model_complexity,
            min_detection_confidence=self.config.hand_min_detection_confidence,
            min_tracking_confidence=self.config.hand_min_tracking_confidence,
            max_num_hands=1,
        )

    def _in_engagement_zone(self, x: float, y: float) -> bool:
        return (
            self.config.engagement_zone_min <= x <= self.config.engagement_zone_max
            and self.config.engagement_zone_min <= y <= self.config.engagement_zone_max
        )

    def run(self) -> None:
        self.bridge.start()
        capture = cv2.VideoCapture(self.config.camera_index)
        if not capture.isOpened():
            raise RuntimeError("Failed to open camera.")

        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    continue

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self.hands.process(rgb)

                payload = {
                    "system_active": self.state.system_active,
                    "landmarks": [],
                    "track": self.spotify.current_track(),
                    "debug": {
                        "hand_detected": False,
                        "in_engagement_zone": False,
                        "x_velocity": 0.0,
                        "y_velocity": 0.0,
                        "zone": {
                            "x_min": self.config.engagement_zone_min,
                            "x_max": self.config.engagement_zone_max,
                            "y_min": self.config.engagement_zone_min,
                            "y_max": self.config.engagement_zone_max,
                        },
                    },
                }

                if result.multi_hand_landmarks:
                    hand = result.multi_hand_landmarks[0]
                    landmarks = [(lm.x, lm.y, lm.z) for lm in hand.landmark]
                    palm_x, palm_y, _ = landmarks[0]
                    self.state.push_palm(palm_x, palm_y)
                    x_vel, y_vel = self.state.velocity()
                    in_zone = self._in_engagement_zone(palm_x, palm_y)
                    payload["debug"] = {
                        "hand_detected": True,
                        "in_engagement_zone": in_zone,
                        "x_velocity": round(x_vel, 4),
                        "y_velocity": round(y_vel, 4),
                        "zone": {
                            "x_min": self.config.engagement_zone_min,
                            "x_max": self.config.engagement_zone_max,
                            "y_min": self.config.engagement_zone_min,
                            "y_max": self.config.engagement_zone_max,
                        },
                    }

                    context = GestureContext(
                        landmarks=landmarks,
                        x_velocity=x_vel,
                        y_velocity=y_vel,
                        in_engagement_zone=in_zone,
                        system_active=self.state.system_active,
                    )

                    events = self.registry.evaluate(context)
                    for event in events:
                        if event.name not in {"summon_hud", "dismiss_hud"} and not in_zone:
                            continue
                        self.dispatcher.dispatch(event)

                    if self.state.system_active:
                        payload["landmarks"] = landmarks
                        self.bridge.broadcast(payload)
                    else:
                        self.bridge.broadcast(
                            {
                                "system_active": False,
                                "landmarks": [],
                                "track": payload["track"],
                                "debug": payload["debug"],
                            }
                        )
                else:
                    self.bridge.broadcast(payload)

                fps = self.config.active_fps if self.state.system_active else self.config.inactive_fps
                time.sleep(1 / fps)

        finally:
            capture.release()


def run() -> None:
    CantripsEngine().run()
