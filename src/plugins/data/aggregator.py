# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Data Aggregation Plugin

import requests
import asyncio
import logging
from src.core.events import bus

class DataPlugin:
    def __init__(self):
        bus.subscribe("system:startup", self.start_aggregation)

    async def start_aggregation(self, data):
        asyncio.create_task(self.aggregation_loop())

    async def aggregation_loop(self):
        while True:
            try:
                sentiment = 0.0
                await bus.emit("data:sentiment_update", {"sentiment": sentiment})
            except Exception as e:
                logging.error(f"Aggregation error: {e}")
            await asyncio.sleep(300)

data_plugin = DataPlugin()
