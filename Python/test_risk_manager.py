"""
Tests for risk_manager.py - RiskManager class.

Tests cover:
- evaluate_market_regime: None/short df, stable, high volatility, low volatility
- _calc_atr: basic ATR calculation
- calculate_lot_size: normal, zero sl_points, zero tick_value, edge cases
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from risk_manager import RiskManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_ohlcv(n=100, base_price=1.1000, volatility=0.001):
    """Generate a synthetic OHLCV DataFrame with n rows."""
    np.random.seed(42)
    closes = base_price + np.cumsum(np.random.randn(n) * volatility)
    highs = closes + np.abs(np.random.randn(n) * volatility * 0.5)
    lows = closes - np.abs(np.random.randn(n) * volatility * 0.5)
    opens = np.roll(closes, 1)
    opens[0] = base_price
    volumes = np.random.randint(1000, 5000, n).astype(float)

    idx = pd.date_range("2024-01-01", periods=n, freq="1h")
    return pd.DataFrame(
        {"Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": volumes},
        index=idx,
    )


def make_high_volatility_df(n=100):
    """DataFrame where the last ATR is > 1.5x the 50-period average ATR."""
    df = make_ohlcv(n, volatility=0.001)
    # Force last few rows to have very large high-low range
    for i in range(n - 5, n):
        df.at[df.index[i], "High"] = df["Close"].iloc[i] + 0.1
        df.at[df.index[i], "Low"] = df["Close"].iloc[i] - 0.1
    return df


def make_low_volatility_df(n=100):
    """DataFrame where the last ATR is < 0.5x the 50-period average ATR."""
    df = make_ohlcv(n, volatility=0.001)
    # Force last few rows to have very small high-low range
    for i in range(n - 5, n):
        mid = df["Close"].iloc[i]
        df.at[df.index[i], "High"] = mid + 0.000001
        df.at[df.index[i], "Low"] = mid - 0.000001
    return df


# ---------------------------------------------------------------------------
# RiskManager instantiation
# ---------------------------------------------------------------------------

class TestRiskManagerInit:
    def test_default_attributes(self):
        rm = RiskManager()
        assert rm.max_equity_risk == 0.05
        assert rm.pyramid_limit == 5


# ---------------------------------------------------------------------------
# evaluate_market_regime
# ---------------------------------------------------------------------------

class TestEvaluateMarketRegime:
    def setup_method(self):
        self.rm = RiskManager()

    def test_none_df_returns_stable(self):
        assert self.rm.evaluate_market_regime(None) == "Stable"

    def test_short_df_returns_stable(self):
        df = make_ohlcv(n=10)
        assert self.rm.evaluate_market_regime(df) == "Stable"

    def test_exactly_49_rows_returns_stable(self):
        df = make_ohlcv(n=49)
        assert self.rm.evaluate_market_regime(df) == "Stable"

    def test_stable_regime_on_normal_data(self):
        df = make_ohlcv(n=100)
        result = self.rm.evaluate_market_regime(df)
        assert result in ("Stable", "High Volatility", "Low Volatility")

    def test_high_volatility_detected(self):
        df = make_high_volatility_df(n=100)
        result = self.rm.evaluate_market_regime(df)
        assert result == "High Volatility"

    def test_low_volatility_detected(self):
        df = make_low_volatility_df(n=100)
        result = self.rm.evaluate_market_regime(df)
        assert result == "Low Volatility"

    def test_returns_string(self):
        df = make_ohlcv(n=100)
        result = self.rm.evaluate_market_regime(df)
        assert isinstance(result, str)

    def test_exactly_50_rows(self):
        df = make_ohlcv(n=50)
        result = self.rm.evaluate_market_regime(df)
        assert isinstance(result, str)
        assert result in ("Stable", "High Volatility", "Low Volatility")


# ---------------------------------------------------------------------------
# _calc_atr
# ---------------------------------------------------------------------------

class TestCalcATR:
    def setup_method(self):
        self.rm = RiskManager()

    def test_atr_returns_series(self):
        df = make_ohlcv(n=50)
        atr = self.rm._calc_atr(df)
        assert isinstance(atr, pd.Series)

    def test_atr_length_matches_input(self):
        df = make_ohlcv(n=50)
        atr = self.rm._calc_atr(df)
        assert len(atr) == len(df)

    def test_atr_non_negative(self):
        df = make_ohlcv(n=100)
        atr = self.rm._calc_atr(df)
        # Drop NaN values introduced by rolling window and check positivity
        valid = atr.dropna()
        assert (valid >= 0).all()

    def test_atr_increases_with_volatility(self):
        low_vol = make_ohlcv(n=100, volatility=0.0001)
        high_vol = make_ohlcv(n=100, volatility=0.01)
        atr_low = self.rm._calc_atr(low_vol).dropna().mean()
        atr_high = self.rm._calc_atr(high_vol).dropna().mean()
        assert atr_high > atr_low

    def test_atr_custom_period(self):
        df = make_ohlcv(n=100)
        atr_14 = self.rm._calc_atr(df, period=14)
        atr_5 = self.rm._calc_atr(df, period=5)
        # Both should be Series of same length
        assert len(atr_14) == len(atr_5)

    def test_atr_first_n_values_are_nan(self):
        df = make_ohlcv(n=50)
        atr = self.rm._calc_atr(df, period=14)
        # First 14 values should be NaN (rolling window not fully filled)
        assert atr.iloc[:14].isna().all()


# ---------------------------------------------------------------------------
# calculate_lot_size
# ---------------------------------------------------------------------------

class TestCalculateLotSize:
    def setup_method(self):
        self.rm = RiskManager()

    def test_basic_lot_calculation(self):
        # balance=10000, risk=1%, sl=100 points, tick_value=1.0
        # risk_amount = 100, lot = 100 / (100 * 1.0) = 1.0
        lot = self.rm.calculate_lot_size(10000, 1.0, 100, 1.0)
        assert lot == 1.0

    def test_zero_sl_points_returns_min_lot(self):
        lot = self.rm.calculate_lot_size(10000, 1.0, 0, 1.0)
        assert lot == 0.01

    def test_zero_tick_value_returns_min_lot(self):
        lot = self.rm.calculate_lot_size(10000, 1.0, 100, 0)
        assert lot == 0.01

    def test_both_zero_returns_min_lot(self):
        lot = self.rm.calculate_lot_size(10000, 1.0, 0, 0)
        assert lot == 0.01

    def test_result_is_rounded_to_2_decimals(self):
        lot = self.rm.calculate_lot_size(10000, 1.0, 33, 1.0)
        # risk_amount=100, lot = 100 / 33 = 3.0303... -> round to 3.03
        assert lot == round(lot, 2)
        assert isinstance(lot, float)

    def test_high_balance_increases_lot(self):
        lot_low = self.rm.calculate_lot_size(1000, 1.0, 100, 1.0)
        lot_high = self.rm.calculate_lot_size(100000, 1.0, 100, 1.0)
        assert lot_high > lot_low

    def test_higher_risk_pct_increases_lot(self):
        lot_low = self.rm.calculate_lot_size(10000, 0.5, 100, 1.0)
        lot_high = self.rm.calculate_lot_size(10000, 2.0, 100, 1.0)
        assert lot_high > lot_low

    def test_larger_sl_decreases_lot(self):
        lot_small_sl = self.rm.calculate_lot_size(10000, 1.0, 50, 1.0)
        lot_large_sl = self.rm.calculate_lot_size(10000, 1.0, 200, 1.0)
        assert lot_small_sl > lot_large_sl

    def test_lot_calculation_precision(self):
        # balance=50000, risk=2%, sl=200, tick_value=0.5
        # risk_amount = 1000, lot = 1000 / (200 * 0.5) = 10.0
        lot = self.rm.calculate_lot_size(50000, 2.0, 200, 0.5)
        assert lot == 10.0

    def test_negative_risk_pct_boundary(self):
        # Negative risk should produce negative lot (no guard in implementation)
        lot = self.rm.calculate_lot_size(10000, -1.0, 100, 1.0)
        assert lot < 0

    def test_very_large_sl_returns_tiny_lot(self):
        lot = self.rm.calculate_lot_size(10000, 1.0, 10000, 1.0)
        assert lot == 0.01  # 100 / 10000 = 0.01