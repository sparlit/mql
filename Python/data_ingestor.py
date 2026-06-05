import yfinance as yf
import pandas as pd
import logging
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class DataIngestor:
    def __init__(self):
        self.cache = {}
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    def fetch_all_data(self, symbol):
        prices = self.fetch_prices(symbol)
        news = self.fetch_forex_factory_news()
        sentiment = self.analyze_sentiment(news, symbol)
        return {"prices": prices, "news": news, "sentiment": sentiment}

    def fetch_prices(self, symbol):
        yf_symbol = self._map_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        intervals = {
            'M1': '1m', 'M5': '5m', 'M15': '15m', 'M30': '30m',
            'H1': '1h', 'H4': '1h', 'D1': '1d', 'W1': '1wk', 'MN': '1mo'
        }
        dfs = {}
        for tf, interval in intervals.items():
            df = ticker.history(period='5d' if 'm' in interval else '1y', interval=interval)
            if tf == 'H4' and not df.empty:
                df = df.resample('4h').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
            dfs[tf] = df
        return dfs

    def fetch_forex_factory_news(self):
        try:
            url = "https://www.forexfactory.com/calendar.php"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            news_items = []
            rows = soup.select(".calendar__row")
            for row in rows:
                event = row.select_one(".calendar__event-title")
                impact = row.select_one(".calendar__impact span")
                if event and impact:
                    news_items.append({
                        "event": event.text.strip(),
                        "impact": impact.get('class')[0] if impact.get('class') else "low"
                    })
            return news_items
        except Exception as e:
            logging.error(f"News fetch error: {e}")
            return []

    def analyze_sentiment(self, news_items, symbol):
        if not news_items: return 0

        texts = [item['event'] for item in news_items if any(c in item['event'] for c in symbol[:3])]
        if not texts: return 0

        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # FinBERT labels: 0: positive, 1: negative, 2: neutral
        mean_sentiment = predictions[:, 0].mean().item() - predictions[:, 1].mean().item()
        return mean_sentiment

    def _map_symbol(self, symbol):
        mapping = {"XAUUSD": "GC=F", "GOLD": "GC=F", "US30": "YM=F", "NAS100": "NQ=F"}
        base = symbol.split('.')[0].split('_')[0]
        if base in mapping: return mapping[base]
        if len(base) == 6: return f"{base}=X"
        return base
