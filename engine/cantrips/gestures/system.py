from __future__ import annotations

from cantrips.gestures.base import BaseGesture
from cantrips.models import GestureContext, GestureEvent


class SummonHudGesture(BaseGesture):
    name = "summon_hud"

    def __init__(self, velocity_threshold: float) -> None:
        self.velocity_threshold = velocity_threshold
        self.rearm_threshold = velocity_threshold * 0.6
        self.armed = True

    def detect(self, context: GestureContext) -> GestureEvent | None:
        y_velocity = context.y_velocity
        x_velocity = context.x_velocity

        if abs(y_velocity) < self.rearm_threshold:
            self.armed = True
            return None

        vertical_dominant = abs(y_velocity) > abs(x_velocity) * 1.15
        if not vertical_dominant or not self.armed:
            return None

        if y_velocity < -self.velocity_threshold:
            self.armed = False
            return GestureEvent(name=self.name)
        return None


class DismissHudGesture(BaseGesture):
    name = "dismiss_hud"

    def __init__(self, velocity_threshold: float) -> None:
        self.velocity_threshold = velocity_threshold
        self.rearm_threshold = velocity_threshold * 0.6
        self.armed = True

    def detect(self, context: GestureContext) -> GestureEvent | None:
        y_velocity = context.y_velocity
        x_velocity = context.x_velocity

        if abs(y_velocity) < self.rearm_threshold:
            self.armed = True
            return None

        vertical_dominant = abs(y_velocity) > abs(x_velocity) * 1.15
        if not vertical_dominant or not self.armed:
            return None

        if y_velocity > self.velocity_threshold:
            self.armed = False
            return GestureEvent(name=self.name)
        return None
