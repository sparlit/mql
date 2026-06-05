import yfinance as yf
import pandas as pd
import logging
import requests
from bs4 import BeautifulSoup

class DataIngestor:
    def __init__(self):
        """
        Initialize DataIngestor state and trigger lazy loading of NLP resources.
        
        Creates an empty in-memory cache, sets `tokenizer` and `model` to `None`, and attempts to lazily load the FinBERT tokenizer/model for later sentiment analysis.
        """
        self.cache = {}
        self.tokenizer = None
        self.model = None
        self._lazy_init_nlp()

    def _lazy_init_nlp(self):
        """
        Lazily initialize FinBERT tokenizer and sequence-classification model and attach them to the instance.
        
        On success sets `self.tokenizer`, `self.model`, and `self.torch`. On failure leaves those attributes unchanged and emits a warning.
        """
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            self.torch = torch
            logging.info("FinBERT NLP Engine initialized successfully.")
        except Exception as e:
            logging.warning(f"NLP Engine lazy-load failed (normal for first-run or CI timeout): {e}")

    def fetch_all_data(self, symbol):
        """
        Orchestrates ingestion by fetching historical prices, Forex Factory news, and a sentiment score for the given symbol.
        
        Parameters:
            symbol (str): Instrument symbol or alias to fetch data for (e.g., "XAUUSD", "US30", "AAPL"). The symbol is mapped internally to a yfinance-compatible ticker when necessary.
        
        Returns:
            dict: A dictionary with keys:
                - "prices": dict mapping timeframe keys (e.g., "M1", "H4", "D1") to pandas DataFrame of historical OHLCV data.
                - "news": list of news/event items parsed from the Forex Factory calendar (each item is a dict with at least "event" and "impact").
                - "sentiment": float sentiment score computed from the news items for the symbol (0 when no model, no news, or no matching events).
        """
        prices = self.fetch_prices(symbol)
        news = self.fetch_forex_factory_news()
        sentiment = self.analyze_sentiment(news, symbol)
        return {"prices": prices, "news": news, "sentiment": sentiment}

    def fetch_prices(self, symbol):
        """
        Fetch historical OHLCV price data across multiple standard timeframes for a given symbol.
        
        The function resolves the provided symbol into a yfinance-compatible ticker, requests history for each timeframe, and returns a dict of pandas.DataFrame objects keyed by timeframe codes. Minute-based intervals ('M1','M5','M15','M30') are fetched with a 5-day period; hourly/daily/weekly/monthly intervals use a 1-year period. When the 'H4' timeframe is produced, data is resampled into 4-hour bars using OHLCV aggregations (Open: first, High: max, Low: min, Close: last, Volume: sum) and rows with missing values are dropped.
        
        Parameters:
            symbol (str): Financial symbol to fetch (will be converted to a yfinance ticker if needed).
        
        Returns:
            dict: Mapping from timeframe codes ('M1','M5','M15','M30','H1','H4','D1','W1','MN') to pandas.DataFrame containing indexed OHLCV price series.
        """
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
        """
        Retrieve and parse Forex Factory calendar events from the site's calendar page.
        
        Returns:
            list[dict]: A list of news items where each dict contains:
                - "event" (str): the event title text.
                - "impact" (str): the impact level (the first CSS class on the impact element or "low" if absent).
            Returns an empty list if fetching or parsing fails or no events are found.
        """
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
        """
        Compute an aggregate sentiment score from Forex news items for a given symbol.
        
        Filters news items whose 'event' text contains any of the first three characters of `symbol`, runs the model to obtain class probabilities for each matching event, and returns the mean probability of class index 0 minus the mean probability of class index 1. If `news_items` is empty, the model is unavailable, or no events match the symbol filter, returns 0.
        
        Parameters:
            news_items (list[dict]): Iterable of news item dictionaries; each item must include an 'event' string.
            symbol (str): Asset symbol whose first three characters are used to select relevant news events.
        
        Returns:
            float: Mean(probability of class 0) - Mean(probability of class 1), or 0 when no sentiment is computed.
        """
        if not news_items or self.model is None: return 0

        texts = [item['event'] for item in news_items if any(c in item['event'] for c in symbol[:3])]
        if not texts: return 0

        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with self.torch.no_grad():
            outputs = self.model(**inputs)
            predictions = self.torch.nn.functional.softmax(outputs.logits, dim=-1)

        mean_sentiment = predictions[:, 0].mean().item() - predictions[:, 1].mean().item()
        return mean_sentiment

    def _map_symbol(self, symbol):
        """
        Map a user-provided symbol to a yfinance-compatible ticker.
        
        Parameters:
            symbol (str): Input symbol which may include suffixes (e.g., "EURUSD.1" or "ABC_DEF"); only the leading base segment is considered.
        
        Returns:
            str: A yfinance-ready ticker. Known aliases (for example, "GOLD"/"XAUUSD") are converted to their futures tickers; if the base is six characters long, `=X` is appended; otherwise the base is returned unchanged.
        """
        mapping = {"XAUUSD": "GC=F", "GOLD": "GC=F", "US30": "YM=F", "NAS100": "NQ=F"}
        base = symbol.split('.')[0].split('_')[0]
        if base in mapping: return mapping[base]
        if len(base) == 6: return f"{base}=X"
        return base
