from __future__ import annotations

from cantrips.config import AppConfig
from cantrips.gestures.base import BaseGesture
from cantrips.gestures.playback import ClosedFistGesture, HorizontalSwipeGesture, OpenPalmGesture
from cantrips.gestures.system import DismissHudGesture, SummonHudGesture


class GestureRegistry:
    def __init__(self, config: AppConfig) -> None:
        self.strategies: list[BaseGesture] = [
            SummonHudGesture(config.swipe_velocity_threshold),
            DismissHudGesture(config.swipe_velocity_threshold),
            OpenPalmGesture(),
            ClosedFistGesture(),
            HorizontalSwipeGesture(config.horizontal_swipe_threshold),
        ]

    def evaluate(self, context):
        events = []
        for strategy in self.strategies:
            event = strategy.detect(context)
            if event:
                events.append(event)
        return events
