import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime, timedelta

class DataAggregator:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_forexfactory_news(self):
        """
        Scrapes high-impact news from Forex Factory with precise timing.
        """
        url = "https://www.forexfactory.com/calendar"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.find_all('tr', class_='calendar__row')
            news_events = []

            current_date = datetime.now().strftime("%b %d, %Y")

            for row in rows:
                impact = row.find('td', class_='calendar__impact')
                if impact and (impact.find('span', class_='high') or impact.find('span', class_='red')):
                    currency = row.find('td', class_='calendar__currency').text.strip()
                    event = row.find('td', class_='calendar__event').text.strip()
                    time_str = row.find('td', class_='calendar__time').text.strip()

                    if not time_str or ":" not in time_str: continue

                    try:
                        # Parsing FF time format like "4:30am"
                        event_dt = datetime.strptime(f"{current_date} {time_str}", "%b %d, %Y %I:%M%p")
                        news_events.append({
                            'currency': currency,
                            'event': event,
                            'datetime': event_dt,
                            'impact': 'High'
                        })
                    except:
                        continue
            return news_events
        except Exception as e:
            logging.error(f"ForexFactory Scraper Error: {e}")
            return []

    def fetch_fxstreet_sentiment(self):
        """
        Fetches sentiment data from FXStreet.
        """
        url = "https://www.fxstreet.com/news?q=sentiment"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text().lower()
            bullish_count = text.count('bullish') + text.count('positive') + text.count('recovery')
            bearish_count = text.count('bearish') + text.count('negative') + text.count('decline')

            if bullish_count > bearish_count * 1.5:
                return "Bullish"
            elif bearish_count > bullish_count * 1.5:
                return "Bearish"
            return "Neutral"
        except Exception as e:
            logging.error(f"FXStreet Scraper Error: {e}")
            return "Neutral"

    def fetch_polymarket_sentiment(self):
        """
        Scrapes prediction market sentiment from Polymarket.
        """
        try:
            url = "https://polymarket.com/"
            response = requests.get(url, headers=self.headers, timeout=10)
            text = response.text.lower()

            if 'fed hike' in text or 'interest rates rise' in text: return "Hawkish"
            if 'fed cut' in text or 'interest rates fall' in text: return "Dovish"
            return "Neutral"
        except Exception as e:
            logging.error(f"Polymarket Scraper Error: {e}")
            return "Neutral"

if __name__ == "__main__":
    agg = DataAggregator()
    print("Forex Factory News:", agg.fetch_forexfactory_news()[:2])
    print("FXStreet Sentiment:", agg.fetch_fxstreet_sentiment())
    print("Polymarket Sentiment:", agg.fetch_polymarket_sentiment())
