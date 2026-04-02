from __future__ import annotations

import time
from collections import deque


class EngineState:
    def __init__(self, discrete_cooldown_ms: int, swipe_command_cooldown_ms: int) -> None:
        self.system_active = False
        self.discrete_cooldown_ms = discrete_cooldown_ms
        self.swipe_command_cooldown_ms = swipe_command_cooldown_ms
        self._last_discrete_at = 0.0
        self._last_swipe_at = 0.0
        self.palm_history: deque[tuple[float, float]] = deque(maxlen=5)

    def can_dispatch_discrete(self) -> bool:
        now = time.time() * 1000
        if now - self._last_discrete_at >= self.discrete_cooldown_ms:
            self._last_discrete_at = now
            return True
        return False

    def can_dispatch_swipe(self) -> bool:
        now = time.time() * 1000
        if now - self._last_swipe_at >= self.swipe_command_cooldown_ms:
            self._last_swipe_at = now
            return True
        return False

    def push_palm(self, x: float, y: float) -> None:
        self.palm_history.append((x, y))

    def velocity(self) -> tuple[float, float]:
        if len(self.palm_history) < 4:
            return (0.0, 0.0)
        start_x, start_y = self.palm_history[0]
        end_x, end_y = self.palm_history[-1]
        return (end_x - start_x, end_y - start_y)
