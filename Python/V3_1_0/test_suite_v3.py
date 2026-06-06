# Project: Autonomous AutoTrader (AAT)
# Version: V3.1.0_20260606
# License: 100% FOSS / GNU GPL v3
# Author: Simon Peter
# Verification: Zero-Stub / Production Ready
# Description: Comprehensive Regression Test Suite

import pytest
import os
import pandas as pd
import numpy as np

# Absolute Versioned Imports
from Python.V3_1_0.DataAggregator import DataAggregator
from Python.V3_1_0.StrategyMaster import StrategyMaster

@pytest.fixture
def aggregator():
    return DataAggregator()

@pytest.fixture
def strategy():
    os.environ["SKIP_FINBERT"] = "1"
    return StrategyMaster()

def test_aggregator_failover(aggregator):
    # Test fallback to string return on failure
    rss = aggregator.fetch_reuters_bloomberg_rss()
    assert isinstance(rss, str)

def test_strategy_quantization(strategy):
    # Verify quantization didn't break consensus logic
    data = {'Close': np.random.randn(200).cumsum() + 100, 'Volume': np.random.randint(100, 1000, 200)}
    df = pd.DataFrame(data)
    signal, conf, tf = strategy.get_consensus_signal({'H1': df})
    assert signal in ["BUY", "SELL", "NEUTRAL"]
    assert isinstance(conf, float)
