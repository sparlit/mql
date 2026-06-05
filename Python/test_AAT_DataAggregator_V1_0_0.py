import pytest
from unittest.mock import patch, MagicMock
from AAT_DataAggregator_V1_0_0 import DataAggregator
from datetime import datetime

@pytest.fixture
def agg():
    return DataAggregator()

def test_fetch_forexfactory_news(agg):
    with patch('requests.get') as mock_get:
        mock_html = """
        <tr class="calendar__row">
            <td class="calendar__time">10:00am</td>
            <td class="calendar__currency">USD</td>
            <td class="calendar__impact"><span class="high">!</span></td>
            <td class="calendar__event">CPI</td>
        </tr>
        """
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = mock_html.encode('utf-8')

        news = agg.fetch_forexfactory_news()
        assert isinstance(news, list)
        if len(news) > 0:
            assert news[0]['currency'] == 'USD'
            assert news[0]['event'] == 'CPI'
            assert isinstance(news[0]['datetime'], datetime)

def test_fetch_fxstreet_sentiment(agg):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"The market is bullish today."
        sentiment = agg.fetch_fxstreet_sentiment()
        assert sentiment == "Bullish"

def test_fetch_polymarket_sentiment(agg):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "Fed hike expected in December"
        sentiment = agg.fetch_polymarket_sentiment()
        assert sentiment == "Hawkish"
