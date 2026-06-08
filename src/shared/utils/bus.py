# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Event-Driven Bus with Audit Logging

import asyncio
import logging
import sqlite3
import json
from typing import Dict, Any, Callable, List

class EventBus:
    def __init__(self, audit_db="db/sovereign_audit.db"):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.audit_db = audit_db

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def emit(self, event_type: str, data: Any):
        # Ruthless Log: Record critical events in the Sovereign Log
        if event_type in ["risk:approval", "intelligence:signal", "system:startup"]:
            try:
                conn = sqlite3.connect(self.audit_db)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sovereign_log (event_type, source, details) VALUES (?, ?, ?)",
                    (event_type.upper(), "EventBus", json.dumps(data))
                )
                conn.commit()
                conn.close()
            except Exception as e:
                logging.error(f"Audit log error: {e}")

        if event_type in self.subscribers:
            tasks = [callback(data) for callback in self.subscribers[event_type]]
            if tasks:
                await asyncio.gather(*tasks)

bus = EventBus()
