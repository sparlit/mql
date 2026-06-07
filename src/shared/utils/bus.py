# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Event-Driven Bus (Shared Utility)

import asyncio
import logging
from typing import Dict, Any, Callable, List

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def emit(self, event_type: str, data: Any):
        if event_type in self.subscribers:
            tasks = [callback(data) for callback in self.subscribers[event_type]]
            await asyncio.gather(*tasks)

bus = EventBus()
