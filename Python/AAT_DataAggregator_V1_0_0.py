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

            current_date_str = datetime.now().strftime("%b %d, %Y")

            for row in rows:
                # Update current_date if a new date is found in the row
                date_td = row.find('td', class_='calendar__date')
                if date_td and date_td.text.strip() != "":
                    date_text = date_td.text.strip()
                    try:
                        parts = date_text.split()
                        if len(parts) >= 2:
                            month_day = " ".join(parts[-2:])
                            current_date_str = f"{month_day}, {datetime.now().year}"
                    except:
                        pass

                impact = row.find('td', class_='calendar__impact')
                if impact and (impact.find('span', class_='high') or impact.find('span', class_='red')):
                    currency_td = row.find('td', class_='calendar__currency')
                    event_td = row.find('td', class_='calendar__event')
                    time_td = row.find('td', class_='calendar__time')

                    if not currency_td or not event_td or not time_td: continue

                    currency = currency_td.text.strip()
                    event = event_td.text.strip()
                    time_str = time_td.text.strip()

                    if not time_str or ":" not in time_str: continue

                    try:
                        event_dt = datetime.strptime(f"{current_date_str} {time_str}", "%b %d, %Y %I:%M%p")
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
            if response.status_code != 200: return "Neutral"
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
            if response.status_code != 200: return "Neutral"
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
