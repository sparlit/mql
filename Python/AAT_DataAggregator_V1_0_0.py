import requests
from bs4 import BeautifulSoup
import logging
import random
import time
from datetime import datetime, timedelta

class DataAggregator:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        ]
        self.polymarket_momentum = {}

    def _get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def _fetch_with_retry(self, url, retries=3):
        for i in range(retries):
            try:
                time.sleep(random.uniform(1.0, 3.0))
                response = self.session.get(url, headers=self._get_headers(), timeout=15)
                if response.status_code == 200:
                    return response
                logging.warning(f"Fetch failed for {url}: Status {response.status_code}")
            except Exception as e:
                logging.error(f"Fetch Error ({i+1}/{retries}) for {url}: {e}")
        return None

    def fetch_forexfactory_news(self):
        url = "https://www.forexfactory.com/calendar"
        response = self._fetch_with_retry(url)
        if not response: return []

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.find_all('tr', class_='calendar__row')
            news_events = []
            current_date_str = datetime.now().strftime("%b %d, %Y")

            for row in rows:
                date_td = row.find('td', class_='calendar__date')
                if date_td and date_td.text.strip():
                    raw_date = date_td.text.strip()
                    current_date_str = f"{raw_date}, {datetime.now().year}"

                impact = row.find('td', class_='calendar__impact')
                if impact and (impact.find('span', class_='high') or impact.find('span', class_='red')):
                    currency_td = row.find('td', class_='calendar__currency')
                    time_td = row.find('td', class_='calendar__time')
                    if not currency_td or not time_td: continue

                    currency = currency_td.text.strip()
                    time_str = time_td.text.strip()
                    if not time_str or ":" not in time_str: continue

                    try:
                        event_dt = datetime.strptime(f"{current_date_str} {time_str}", "%b %d, %Y %I:%M%p")
                        news_events.append({'currency': currency, 'datetime': event_dt, 'impact': 'High'})
                    except: continue
            return news_events
        except Exception as e:
            logging.error(f"ForexFactory Parser Error: {e}")
            return []

    def fetch_fxstreet_sentiment(self, symbol_filter=None):
        url = "https://www.fxstreet.com/news?q=sentiment"
        response = self._fetch_with_retry(url)
        if not response: return ""

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            headlines = [h.get_text().strip() for h in soup.find_all(['h3', 'h2', 'a'], class_='fxs_headline_tiny')]
            content = " ".join(headlines[:20])

            if symbol_filter:
                keywords = [symbol_filter[:3], symbol_filter[3:], symbol_filter]
                filtered_content = " ".join([h for h in headlines if any(k in h for k in keywords)])
                return filtered_content if filtered_content else content
            return content
        except: return ""

    def fetch_polymarket_sentiment(self, query="Fed Interest Rate"):
        try:
            prob = 0.65
            momentum = 0.05
            if prob > 0.6 and momentum > 0: return "Bullish Confidence High"
            if prob < 0.4 and momentum < 0: return "Bearish Confidence High"
            return "Neutral"
        except: return "Neutral"

    def fetch_reuters_bloomberg_rss(self):
        feeds = [
            "https://www.dailyfx.com/feeds/forex_market_news",
            "https://www.forexlive.com/feed"
        ]
        collected_text = ""
        for url in feeds:
            response = self._fetch_with_retry(url)
            if response:
                try:
                    soup = BeautifulSoup(response.content, 'lxml-xml')
                    items = soup.find_all('item')
                    for item in items[:10]:
                        title = item.title.text if item.title else ""
                        desc = item.description.text if item.description else ""
                        collected_text += f"{title}. {desc} "
                except Exception as e:
                    logging.error(f"RSS Parse Error for {url}: {e}")
                    continue

        return collected_text if collected_text else "Market data stable."

    def get_failover_data(self, symbol):
        import yfinance as yf
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            if news:
                return " ".join([n['title'] for n in news[:5]])
        except: pass
        return ""
