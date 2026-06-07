# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Data Aggregation Plugin (Hardened Scraping)

import requests
import asyncio
import logging
import random
from bs4 import BeautifulSoup
from src.shared.utils.bus import bus

class DataPlugin:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        bus.subscribe("system:startup", self.start_aggregation)

    async def start_aggregation(self, data):
        asyncio.create_task(self.aggregation_loop())

    def _fetch_headlines(self, url):
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            res = self.session.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'html.parser')
                return " ".join([h.text.strip() for h in soup.find_all(['h3', 'a'])[:5]])
        except Exception as e:
            logging.error(f"Scraper error for {url}: {e}")
        return ""

    async def aggregation_loop(self):
        while True:
            try:
                # Multi-Tiered FOSS Sentiment Gathering
                headlines = self._fetch_headlines("https://www.dailyfx.com/market-news")
                sentiment = 0.5 # Neutral base
                if "bullish" in headlines.lower() or "gain" in headlines.lower():
                    sentiment += 0.2
                elif "bearish" in headlines.lower() or "drop" in headlines.lower():
                    sentiment -= 0.2

                await bus.emit("data:sentiment_update", {"sentiment": sentiment, "text": headlines})
            except Exception as e:
                logging.error(f"Aggregation loop error: {e}")
            await asyncio.sleep(300)

data_plugin = DataPlugin()
