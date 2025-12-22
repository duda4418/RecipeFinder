from __future__ import annotations

from typing import Callable, Dict, Any, List


EventHandler = Callable[[str, Dict[str, Any]], None]


class EventBus:
    def __init__(self) -> None:
        self._subs: List[EventHandler] = []

    def subscribe(self, handler: EventHandler) -> None:
        self._subs.append(handler)

    def emit(self, event: str, payload: Dict[str, Any]) -> None:
        for h in self._subs:
            h(event, payload)

