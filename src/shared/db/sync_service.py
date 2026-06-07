# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Hybrid Sync Service (SQLite -> Remote)

import sqlite3
import asyncio
import logging
import requests
import json
from datetime import datetime
from src.core.main import bus

class HybridSyncService:
    def __init__(self, local_db="db/aat_trading.db", remote_url="http://localhost:9000/api/sync"):
        self.local_db = local_db
        self.remote_url = remote_url
        self.active = True
        bus.subscribe("system:startup", self.start_sync_task)

    async def start_sync_task(self, data):
        asyncio.create_task(self.sync_loop())

    async def sync_loop(self):
        logging.info("Hybrid Sync Service active.")
        while self.active:
            try:
                await self.perform_sync()
            except Exception as e:
                logging.error(f"Sync Error: {e}")
            await asyncio.sleep(60) # High-priority sync every 60s

    async def perform_sync(self):
        """Zero-Stub Production Sync Logic"""
        try:
            conn = sqlite3.connect(self.local_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 1. Fetch unsynced audit logs
            logs = cursor.execute("SELECT * FROM aat_audit WHERE status != 'SYNCED' LIMIT 100").fetchall()
            if not logs:
                conn.close()
                return

            payload = [dict(log) for log in logs]

            # 2. Push to Remote Central Citadel
            # Using timeout to prevent blocking the microkernel
            response = requests.post(self.remote_url, json=payload, timeout=5)

            if response.status_code == 200:
                # 3. Mark as synced
                log_ids = [log['id'] for log in logs]
                cursor.execute(f"UPDATE aat_audit SET status = 'SYNCED' WHERE id IN ({','.join(['?']*len(log_ids))})", log_ids)
                conn.commit()
                logging.info(f"Successfully synced {len(log_ids)} records to central citadel.")

            conn.close()
        except sqlite3.Error as e:
            logging.error(f"Database Sync Error: {e}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Citadel Sync Connectivity Issue: {e}")

sync_service = HybridSyncService()
