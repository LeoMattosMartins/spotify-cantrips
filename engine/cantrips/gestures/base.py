from __future__ import annotations

from abc import ABC, abstractmethod

from cantrips.models import GestureContext, GestureEvent


class BaseGesture(ABC):
    name: str

    @abstractmethod
    def detect(self, context: GestureContext) -> GestureEvent | None:
        raise NotImplementedError
