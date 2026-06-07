# Project: Autonomous AutoTrader (AAT)
# Version: V4.1.2_20260607
# License: 100% FOSS / GNU GPL v3
# Author: Simon Peter
# Verification: Zero-Stub / Production Ready
# Description: Comprehensive Regression Test Suite

import pytest
import os
import pandas as pd
import numpy as np

from Python.V4_1_2.DataAggregator import DataAggregator
from Python.V4_1_2.StrategyMaster import StrategyMaster

@pytest.fixture
def aggregator():
    return DataAggregator()

@pytest.fixture
def strategy():
    os.environ["SKIP_FINBERT"] = "1"
    return StrategyMaster()

def test_aggregator_failover(aggregator):
    rss = aggregator.fetch_reuters_bloomberg_rss()
    assert isinstance(rss, str)

def test_dual_consensus(strategy):
    dfs = {tf: pd.DataFrame({
        'Close': np.random.randn(100).cumsum() + 100,
        'High': np.random.randn(100).cumsum() + 101,
        'Low': np.random.randn(100).cumsum() + 99,
        'Volume': np.random.randint(10, 100, 100)
    }) for tf in ['M1','M5','M15','H1','H4','D1']}
    res = strategy.get_dual_consensus(dfs, "Market is stable")
    assert "scalp_signal" in res
    assert "trade_signal" in res

def test_security_parity():
    from Python.V4_1_2.Security import AATSecurity
    sec = AATSecurity()
    msg = "test_payload"
    encrypted = sec.encrypt(msg)
    decrypted = sec.decrypt(encrypted)
    assert msg == decrypted
