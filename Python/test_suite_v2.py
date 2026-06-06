import pytest
import os
import json
from Python.AAT_DataAggregator_V1_0_0 import DataAggregator
from Python.AAT_StrategyMaster_V1_0_0 import StrategyMaster

@pytest.fixture
def aggregator():
    return DataAggregator()

@pytest.fixture
def strategy():
    os.environ["SKIP_FINBERT"] = "1"
    return StrategyMaster()

def test_aggregator_fallback(aggregator):
    # Test that fallback returns at least the stable message or some text
    rss = aggregator.fetch_reuters_bloomberg_rss()
    assert len(rss) > 0

def test_sentiment_filtering(aggregator):
    text = "The EURUSD is looking strong while Gold is weak."
    filtered = aggregator.fetch_fxstreet_sentiment(symbol_filter="EURUSD")
    # Even if scrape fails, it should return something or empty string, not crash
    assert isinstance(filtered, str)

def test_strategy_monte_carlo(strategy):
    import pandas as pd
    import numpy as np
    data = {'Close': np.random.randn(200).cumsum() + 100}
    df = pd.DataFrame(data)
    result = strategy.run_monte_carlo(df, "BUY", sims=10)
    assert isinstance(result, bool)

def test_optimizer_signatures():
    # Verify signatures file creation
    import subprocess
    subprocess.run(["python3", "Python/optimizer.py"], check=True)
    assert os.path.exists("Python/models/faiss_signatures.npy")
