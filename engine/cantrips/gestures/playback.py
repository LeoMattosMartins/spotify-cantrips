from __future__ import annotations

import math

from cantrips.gestures.base import BaseGesture
from cantrips.models import GestureContext, GestureEvent


FINGER_TIP_IDS = [4, 8, 12, 16, 20]
FINGER_PIP_IDS = [3, 6, 10, 14, 18]


class OpenPalmGesture(BaseGesture):
    name = "play"

    def detect(self, context: GestureContext) -> GestureEvent | None:
        if not context.system_active:
            return None

        palm = context.landmarks[0]
        extended = 0
        far_count = 0
        for tip_id, pip_id in zip(FINGER_TIP_IDS, FINGER_PIP_IDS):
            tip = context.landmarks[tip_id]
            pip = context.landmarks[pip_id]
            if tip[1] < pip[1]:
                extended += 1
            if math.dist((tip[0], tip[1]), (palm[0], palm[1])) > 0.11:
                far_count += 1

        if extended >= 3 and far_count >= 4:
            return GestureEvent(name=self.name)
        return None


class ClosedFistGesture(BaseGesture):
    name = "pause"

    def detect(self, context: GestureContext) -> GestureEvent | None:
        if not context.system_active:
            return None

        palm = context.landmarks[0]
        near_count = 0
        for tip_id in FINGER_TIP_IDS:
            tip = context.landmarks[tip_id]
            dist = math.dist((tip[0], tip[1]), (palm[0], palm[1]))
            if dist < 0.10:
                near_count += 1
        if near_count >= 4:
            return GestureEvent(name=self.name)
        return None


class HorizontalSwipeGesture(BaseGesture):
    name = "horizontal_swipe"

    def __init__(self, threshold: float) -> None:
        self.threshold = threshold
        self.rearm_threshold = threshold * 0.4
        self.armed = True

    def detect(self, context: GestureContext) -> GestureEvent | None:
        if not context.system_active:
            return None

        x_velocity = context.x_velocity
        y_velocity = context.y_velocity

        if abs(x_velocity) < self.rearm_threshold:
            self.armed = True
            return None

        horizontal_dominant = abs(x_velocity) > abs(y_velocity) * 1.4
        if not horizontal_dominant or not self.armed:
            return None

        if x_velocity > self.threshold:
            self.armed = False
            return GestureEvent(name="next_track")

        if x_velocity < -self.threshold:
            self.armed = False
            return GestureEvent(name="previous_track")

        return None
