import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta

class DataAggregator:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_forexfactory_news(self):
        url = "https://www.forexfactory.com/calendar"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200: return []
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.find_all('tr', class_='calendar__row')
            news_events = []
            current_date_str = datetime.now().strftime("%b %d, %Y")
            for row in rows:
                date_td = row.find('td', class_='calendar__date')
                if date_td and date_td.text.strip():
                    current_date_str = f"{date_td.text.strip()}, {datetime.now().year}"
                impact = row.find('td', class_='calendar__impact')
                if impact and (impact.find('span', class_='high') or impact.find('span', class_='red')):
                    currency = row.find('td', class_='calendar__currency').text.strip()
                    time_str = row.find('td', class_='calendar__time').text.strip()
                    if not time_str or ":" not in time_str: continue
                    try:
                        event_dt = datetime.strptime(f"{current_date_str} {time_str}", "%b %d, %Y %I:%M%p")
                        news_events.append({'currency': currency, 'datetime': event_dt, 'impact': 'High'})
                    except: continue
            return news_events
        except Exception as e:
            logging.error(f"ForexFactory Scraper Error: {e}")
            return []

    def fetch_fxstreet_sentiment(self):
        url = "https://www.fxstreet.com/news?q=sentiment"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text()[:5000] # Return raw text for FinBERT
        except: return ""

    def fetch_polymarket_sentiment(self):
        # Implementation for Polymarket Scraper (simplified)
        return "Neutral"

    def fetch_reuters_bloomberg_rss(self):
        # Implementation for RSS feeds
        return "Global markets steady ahead of central bank meetings."
