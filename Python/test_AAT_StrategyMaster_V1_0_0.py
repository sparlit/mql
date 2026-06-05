import pytest
import pandas as pd
import numpy as np
from AAT_StrategyMaster_V1_0_0 import StrategyMaster

@pytest.fixture
def sm():
    return StrategyMaster()

def make_df(n=50):
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    df = pd.DataFrame({
        "Open": np.random.randn(n) + 1.1,
        "High": np.random.randn(n) + 1.11,
        "Low": np.random.randn(n) + 1.09,
        "Close": np.random.randn(n) + 1.1,
        "Volume": np.random.randint(100, 1000, n)
    }, index=idx)
    return df

def test_calculate_rsi(sm):
    df = make_df(30)
    rsi = sm.calculate_rsi(df['Close'])
    assert isinstance(rsi, pd.Series)
    assert len(rsi) == 30
    assert rsi.iloc[-1] >= 0 and rsi.iloc[-1] <= 100

def test_trend_following_signal(sm):
    df = make_df(40)
    signal = sm.trend_following_signal(df)
    assert signal in [0, 1, -1]

def test_mean_reversion_signal(sm):
    df = make_df(30)
    signal = sm.mean_reversion_signal(df)
    assert signal in [0, 1, -1]

def test_breakout_signal(sm):
    df = make_df(30)
    signal = sm.breakout_signal(df)
    assert signal in [0, 1, -1]

def test_scalping_signal(sm):
    df = make_df(30)
    signal = sm.scalping_signal(df)
    assert signal in [0, 1, -1]

def test_harmonic_pattern_signal(sm):
    df = make_df(60)
    signal = sm.harmonic_pattern_signal(df)
    assert signal in [0, 1, -1]

def test_get_consensus_signal(sm):
    df = make_df(60)
    df_dict = {'H1': df, 'M15': df}
    signal, conf, tf_results = sm.get_consensus_signal(df_dict)
    assert signal in ["BUY", "SELL", "NEUTRAL"]
    assert isinstance(conf, (int, float))
    assert 'H1' in tf_results
    assert 'M15' in tf_results
