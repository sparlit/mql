# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Cross-Terminal State Coordinator

import asyncio
from typing import Dict, Any
from src.shared.utils.bus import bus

class StateCoordinator:
    def __init__(self):
        self.state: Dict[str, Any] = {}
        # Subscribe to market updates to track symbols
        bus.subscribe("data:market_update", self.on_market_update)
        bus.subscribe("state:update", self.update_state)

    async def on_market_update(self, data: Dict[str, Any]):
        symbol = data.get("symbol")
        if symbol:
            self.state[f"last_seen_{symbol}"] = data

    async def update_state(self, data: Dict[str, Any]):
        key = data.get("key")
        value = data.get("value")
        if key:
            self.state[key] = value

    def get_state(self, key: str):
        return self.state.get(key)

coordinator = StateCoordinator()
