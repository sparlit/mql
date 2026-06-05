import pytest
import pandas as pd
import numpy as np
from AAT_RiskManager_V1_0_0 import RiskManager

@pytest.fixture
def rm():
    return RiskManager()

def make_df(n=110):
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    df = pd.DataFrame({
        "Open": np.random.randn(n) + 1.1,
        "High": np.random.randn(n) + 1.11,
        "Low": np.random.randn(n) + 1.09,
        "Close": np.random.randn(n) + 1.1,
        "Volume": np.random.randint(100, 1000, n)
    }, index=idx)
    return df

def test_calculate_position_size(rm):
    # Initial trade
    assert rm.calculate_position_size(1.1, 200, 1.0, False) == 0.01
    # Pyramid scale-in success
    assert rm.calculate_position_size(1.1, 200, 1.0, True, 250) == 0.01
    # Pyramid scale-in fail (profit < sl)
    assert rm.calculate_position_size(1.1, 200, 1.0, True, 50) == 0.0

def test_calculate_var(rm):
    df = make_df(120)
    var = rm.calculate_var(df)
    assert isinstance(var, float)
    assert var >= 0

def test_calculate_correlation(rm):
    df1 = make_df(120)
    df2 = make_df(120)
    df_dict = {
        'EURUSD': {'D1': df1},
        'GBPUSD': {'D1': df2}
    }
    corr = rm.calculate_correlation(df_dict)
    assert isinstance(corr, float)
    assert -1.0 <= corr <= 1.0

def test_evaluate_market_regime(rm):
    df = make_df(120)
    regime = rm.evaluate_market_regime(df)
    assert isinstance(regime, str)
    assert any(x in regime for x in ["Stable", "High Volatility", "Low Volatility"])
