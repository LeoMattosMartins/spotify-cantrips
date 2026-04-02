from __future__ import annotations

import math

from cantrips.gestures.base import BaseGesture
from cantrips.models import GestureContext, GestureEvent


class VariablePinchGesture(BaseGesture):
    name = "set_volume"

    def detect(self, context: GestureContext) -> GestureEvent | None:
        if not context.system_active:
            return None
        thumb_tip = context.landmarks[4]
        index_tip = context.landmarks[8]
        pinch_distance = math.dist((thumb_tip[0], thumb_tip[1]), (index_tip[0], index_tip[1]))
        return GestureEvent(name=self.name, payload={"pinch_distance": pinch_distance}, discrete=False)
