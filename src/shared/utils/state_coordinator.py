# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Cross-Terminal State Coordinator

import asyncio
from typing import Dict, Any
from src.core.events import bus

class StateCoordinator:
    def __init__(self):
        self.state: Dict[str, Any] = {}
        # Subscribe to state updates via internal bus
        bus.subscribe("state:update", self.update_state)

    async def update_state(self, data: Dict[str, Any]):
        key = data.get("key")
        value = data.get("value")
        if key:
            self.state[key] = value
            # Optionally broadcast to all connected EAs
            await bus.emit("state:broadcast", {"key": key, "value": value})

    def get_state(self, key: str):
        return self.state.get(key)

coordinator = StateCoordinator()

async def state_manager():
    """Background task for state reconciliation"""
    while True:
        await asyncio.sleep(10)
