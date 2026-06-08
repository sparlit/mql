# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Hardened Data Aggregator (Scraping + Institutional Metadata)

import requests
import asyncio
import logging
import random
import sqlite3
from bs4 import BeautifulSoup
from src.shared.utils.bus import bus

class DataPlugin:
    def __init__(self, db_path="db/aat_trading.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        bus.subscribe("system:startup", self.start_aggregation)

    async def start_aggregation(self, data):
        asyncio.create_task(self.aggregation_loop())

    def _fetch_headlines(self, url):
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            res = self.session.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'lxml')
                return " ".join([h.text.strip() for h in soup.find_all(['h3', 'a'])[:10]])
        except Exception as e:
            logging.error(f"Scraper error for {url}: {e}")
        return ""

    async def aggregation_loop(self):
        while True:
            try:
                # Multi-Tiered FOSS Sentiment Gathering
                headlines = self._fetch_headlines("https://www.dailyfx.com/market-news")
                sentiment = 0.5 # Neutral base
                text = headlines.lower()

                if any(word in text for word in ["bullish", "gain", "higher", "rally", "hawkish"]):
                    sentiment += 0.25
                if any(word in text for word in ["bearish", "drop", "lower", "fall", "dovish"]):
                    sentiment -= 0.25

                # Log news to DB for institutional audit
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS news (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, text TEXT, sentiment REAL)")
                cursor.execute("INSERT INTO news (text, sentiment) VALUES (?, ?)", (headlines[:200], sentiment))
                conn.commit()
                conn.close()

                await bus.emit("data:sentiment_update", {"sentiment": sentiment, "text": headlines[:100]})
            except Exception as e:
                logging.error(f"Aggregation loop error: {e}")
            await asyncio.sleep(600) # Every 10 mins

data_plugin = DataPlugin()
