from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    websocket_host: str = os.getenv("CANTRIPS_WS_HOST", "127.0.0.1")
    websocket_port: int = int(os.getenv("CANTRIPS_WS_PORT", "8765"))
    active_fps: int = int(os.getenv("CANTRIPS_ACTIVE_FPS", "30"))
    inactive_fps: int = int(os.getenv("CANTRIPS_INACTIVE_FPS", "15"))
    discrete_cooldown_ms: int = int(os.getenv("CANTRIPS_DISCRETE_COOLDOWN_MS", "1000"))
    swipe_command_cooldown_ms: int = int(os.getenv("CANTRIPS_SWIPE_COMMAND_COOLDOWN_MS", "1800"))
    swipe_velocity_threshold: float = float(os.getenv("CANTRIPS_SWIPE_VELOCITY_THRESHOLD", "0.05"))
    horizontal_swipe_threshold: float = float(os.getenv("CANTRIPS_HORIZONTAL_SWIPE_THRESHOLD", "0.06"))
    engagement_zone_min: float = float(os.getenv("CANTRIPS_ENGAGEMENT_ZONE_MIN", "0.10"))
    engagement_zone_max: float = float(os.getenv("CANTRIPS_ENGAGEMENT_ZONE_MAX", "0.90"))
    hand_model_complexity: int = int(os.getenv("CANTRIPS_HAND_MODEL_COMPLEXITY", "1"))
    hand_min_detection_confidence: float = float(
        os.getenv("CANTRIPS_HAND_MIN_DETECTION_CONFIDENCE", "0.65")
    )
    hand_min_tracking_confidence: float = float(
        os.getenv("CANTRIPS_HAND_MIN_TRACKING_CONFIDENCE", "0.65")
    )
    camera_index: int = int(os.getenv("CANTRIPS_CAMERA_INDEX", "0"))


CONFIG = AppConfig()
