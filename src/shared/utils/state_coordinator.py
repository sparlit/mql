# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Cross-Terminal State Coordinator with SQL persistence

import asyncio
import sqlite3
import json
from typing import Dict, Any
from src.shared.utils.bus import bus

class StateCoordinator:
    def __init__(self, db_path="db/aat_trading.db"):
        self.db_path = db_path
        self.state: Dict[str, Any] = {}
        bus.subscribe("data:market_update", self.on_market_update)
        bus.subscribe("state:update", self.update_state)

    async def on_market_update(self, data: Dict[str, Any]):
        symbol = data.get("symbol")
        if symbol:
            self.state[f"last_seen_{symbol}"] = data
            # Persist heartbeat to DB
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS heartbeat (symbol TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("INSERT INTO heartbeat (symbol) VALUES (?)", (symbol,))
                conn.commit()
                conn.close()
            except Exception:
                pass

    async def update_state(self, data: Dict[str, Any]):
        key = data.get("key")
        value = data.get("value")
        if key:
            self.state[key] = value

    def get_state(self, key: str):
        return self.state.get(key)

coordinator = StateCoordinator()
