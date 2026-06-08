# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Hub-and-Spoke Distributed Sync Service

import sqlite3
import asyncio
import logging
import httpx
import json
import os
from datetime import datetime
from src.shared.utils.bus import bus

class HybridSyncService:
    def __init__(self, local_db="db/aat_trading.db"):
        self.local_db = local_db
        # In a production environment, this URL would come from vault.json
        self.remote_url = "http://sovereign-hub.local/api/sync"
        self.node_id = os.uname().nodename if hasattr(os, 'uname') else "windows-node"
        bus.subscribe("system:startup", self.start_sync_task)

    async def start_sync_task(self, data):
        asyncio.create_task(self.sync_loop())

    async def sync_loop(self):
        while True:
            try:
                await self.perform_sync()
            except Exception as e:
                logging.debug(f"Sync heartbeat: Hub unreachable (Normal in standalone mode)")
            await asyncio.sleep(300) # Sync every 5 minutes

    async def perform_sync(self):
        """Hub-and-Spoke: Sync local audit trail to central hub"""
        conn = sqlite3.connect(self.local_db)
        cursor = conn.cursor()

        # Fetch last 100 unsynced logs (mocking 'synced' flag logic)
        cursor.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 100")
        trades = cursor.fetchall()
        conn.close()

        if not trades: return

        payload = {
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "data": trades
        }

        async with httpx.AsyncClient() as client:
            # We use a short timeout to prevent blocking the microkernel
            response = await client.post(self.remote_url, json=payload, timeout=2.0)
            if response.status_code == 200:
                logging.info(f"Successfully synced {len(trades)} records to Hub.")

sync_service = HybridSyncService()
