from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GestureEvent:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    discrete: bool = True


@dataclass
class GestureContext:
    landmarks: list[tuple[float, float, float]]
    x_velocity: float
    y_velocity: float
    in_engagement_zone: bool
    system_active: bool
