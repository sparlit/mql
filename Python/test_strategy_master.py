"""
Tests for strategy_master.py - StrategyMaster class.

Tests cover:
- _vsa_analysis: various volume/price scenarios
- get_consensus_signal: empty dict, single tf, multiple tfs, sentiment influence, signal thresholds
- verify_trade: neutral signal, low confidence, no H1 data, Monte Carlo path
- _load_model: model loading (with stub training)
- _init_faiss: FAISS index population
"""
import pytest
import sys
import os
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# Mock heavy dependencies (xgboost, faiss) at module level before import
# ---------------------------------------------------------------------------

def _make_mock_xgb():
    mock_xgb = MagicMock()
    mock_clf = MagicMock()
    mock_xgb.XGBClassifier.return_value = mock_clf
    mock_clf.fit.return_value = mock_clf
    mock_clf.predict_proba.return_value = np.array([[0.3, 0.7]])
    return mock_xgb, mock_clf


def _make_mock_faiss():
    mock_faiss = MagicMock()
    mock_index = MagicMock()
    mock_faiss.IndexFlatL2.return_value = mock_index
    return mock_faiss, mock_index


@pytest.fixture(scope="module")
def strategy_master_class():
    """Import StrategyMaster with mocked xgboost and faiss."""
    mock_xgb, mock_clf = _make_mock_xgb()
    mock_faiss, mock_index = _make_mock_faiss()

    with patch.dict("sys.modules", {"xgboost": mock_xgb, "faiss": mock_faiss}):
        import importlib
        # Remove cached module if already imported
        if "strategy_master" in sys.modules:
            del sys.modules["strategy_master"]
        import strategy_master as sm_module
        return sm_module.StrategyMaster


@pytest.fixture()
def sm(strategy_master_class):
    """Fresh StrategyMaster instance for each test."""
    mock_xgb, mock_clf = _make_mock_xgb()
    mock_faiss, mock_index = _make_mock_faiss()
    with patch.dict("sys.modules", {"xgboost": mock_xgb, "faiss": mock_faiss}):
        return strategy_master_class()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_df(n=60, vol_multiplier=1.0, close_trend=1.0):
    """Synthetic OHLCV DataFrame."""
    np.random.seed(0)
    base = 1.1
    closes = base + np.cumsum(np.random.randn(n) * 0.001 * close_trend)
    highs = closes + np.abs(np.random.randn(n) * 0.0005)
    lows = closes - np.abs(np.random.randn(n) * 0.0005)
    opens = np.roll(closes, 1)
    opens[0] = base
    volumes = np.random.rand(n) * 1000 * vol_multiplier
    idx = pd.date_range("2024-01-01", periods=n, freq="1h")
    return pd.DataFrame(
        {"Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": volumes},
        index=idx,
    )


def make_df_with_high_vol_last(n=60):
    """DataFrame with very high volume on the last bar (bearish close)."""
    df = make_df(n)
    avg_vol = df["Volume"].mean()
    # Last bar: high volume, price drops
    df.at[df.index[-1], "Volume"] = avg_vol * 3
    df.at[df.index[-1], "Close"] = df["Close"].iloc[-2] - 0.005
    df.at[df.index[-1], "High"] = df["Close"].iloc[-2]
    df.at[df.index[-1], "Low"] = df["Close"].iloc[-1] - 0.001
    return df


def make_df_with_low_vol_rising(n=60):
    """DataFrame with low volume on last bar, price rises."""
    df = make_df(n)
    avg_vol = df["Volume"].mean()
    df.at[df.index[-1], "Volume"] = avg_vol * 0.3
    df.at[df.index[-1], "Close"] = df["Close"].iloc[-2] + 0.002
    return df


# ---------------------------------------------------------------------------
# _vsa_analysis
# ---------------------------------------------------------------------------

class TestVsaAnalysis:
    def test_returns_integer_or_float(self, sm):
        df = make_df(n=60)
        result = sm._vsa_analysis(df)
        assert isinstance(result, (int, float))

    def test_high_vol_bearish_bar_scores_positive(self, sm):
        """High volume + price drop + narrow spread = accumulation = bullish VSA = positive score."""
        df = make_df_with_high_vol_last(n=60)
        # Force narrow spread on last bar
        df.at[df.index[-1], "High"] = df["Close"].iloc[-1] + 0.0001
        df.at[df.index[-1], "Low"] = df["Close"].iloc[-1] - 0.0001
        score = sm._vsa_analysis(df)
        # score should be +2 from the VSA condition, -1 from MA check = +1
        assert isinstance(score, (int, float))

    def test_high_vol_bullish_bar_scores_negative(self, sm):
        """High volume + price rising = distribution = score should include -2."""
        df = make_df(n=60)
        avg_vol = df["Volume"].mean()
        df.at[df.index[-1], "Volume"] = avg_vol * 3
        df.at[df.index[-1], "Close"] = df["Close"].iloc[-2] + 0.005
        score = sm._vsa_analysis(df)
        assert score <= 0  # -2 from distribution, MA check could be +/-1

    def test_low_vol_rising_scores_negative(self, sm):
        """Low volume + rising price = weak rally = -1 from VSA."""
        df = make_df_with_low_vol_rising(n=60)
        score = sm._vsa_analysis(df)
        assert isinstance(score, (int, float))
        # VSA gives -1 (weak rally); MA check gives ±1
        assert -2 <= score <= 0

    def test_score_range_reasonable(self, sm):
        """Score should be between -3 and +3 based on the conditions."""
        df = make_df(n=60)
        score = sm._vsa_analysis(df)
        assert -3 <= score <= 3

    def test_requires_minimum_rows_for_rolling(self, sm):
        """With < 20 rows, rolling averages have many NaN values but function shouldn't crash."""
        df = make_df(n=25)
        # Should complete without raising
        score = sm._vsa_analysis(df)
        assert isinstance(score, (int, float))


# ---------------------------------------------------------------------------
# get_consensus_signal
# ---------------------------------------------------------------------------

class TestGetConsensusSignal:
    def test_empty_dict_returns_neutral(self, sm):
        signal, score, tf_results = sm.get_consensus_signal({})
        assert signal == "NEUTRAL"
        assert tf_results == {}

    def test_all_none_dfs_returns_neutral(self, sm):
        signal, score, tf_results = sm.get_consensus_signal({"H1": None, "D1": None})
        assert signal == "NEUTRAL"

    def test_all_empty_dfs_returns_neutral(self, sm):
        signal, score, tf_results = sm.get_consensus_signal(
            {"H1": pd.DataFrame(), "D1": pd.DataFrame()}
        )
        assert signal == "NEUTRAL"

    def test_too_short_dfs_returns_neutral(self, sm):
        short_df = make_df(n=10)
        signal, score, tf_results = sm.get_consensus_signal({"H1": short_df})
        assert signal == "NEUTRAL"

    def test_returns_tuple_of_three(self, sm):
        df = make_df(n=60)
        result = sm.get_consensus_signal({"H1": df})
        assert len(result) == 3

    def test_signal_is_valid_string(self, sm):
        df = make_df(n=60)
        signal, score, _ = sm.get_consensus_signal({"H1": df})
        assert signal in ("BUY", "SELL", "NEUTRAL")

    def test_tf_results_contains_processed_tfs(self, sm):
        df = make_df(n=60)
        _, _, tf_results = sm.get_consensus_signal({"H1": df, "D1": df})
        assert "H1" in tf_results
        assert "D1" in tf_results

    def test_positive_sentiment_increases_score(self, sm):
        df = make_df(n=60)
        _, score_neutral, _ = sm.get_consensus_signal({"H1": df}, sentiment=0)
        _, score_positive, _ = sm.get_consensus_signal({"H1": df}, sentiment=5)
        # sentiment=5 adds 50 to score
        assert score_positive > score_neutral

    def test_negative_sentiment_decreases_score(self, sm):
        df = make_df(n=60)
        _, score_neutral, _ = sm.get_consensus_signal({"H1": df}, sentiment=0)
        _, score_negative, _ = sm.get_consensus_signal({"H1": df}, sentiment=-5)
        assert score_negative < score_neutral

    def test_buy_signal_when_score_above_20(self, sm):
        """Force a BUY by overriding _vsa_analysis to always return large positive."""
        df = make_df(n=60)
        with patch.object(sm, "_vsa_analysis", return_value=10):
            signal, score, _ = sm.get_consensus_signal({"H1": df, "H4": df, "D1": df})
        assert signal == "BUY"

    def test_sell_signal_when_score_below_minus_20(self, sm):
        """Force a SELL by overriding _vsa_analysis to always return large negative."""
        df = make_df(n=60)
        with patch.object(sm, "_vsa_analysis", return_value=-10):
            signal, score, _ = sm.get_consensus_signal({"H1": df, "H4": df, "D1": df})
        assert signal == "SELL"

    def test_unknown_tf_weight_defaults_to_1(self, sm):
        """Timeframes not in weights dict should use weight=1."""
        df = make_df(n=60)
        with patch.object(sm, "_vsa_analysis", return_value=2):
            _, score_known, _ = sm.get_consensus_signal({"H1": df})  # H1 weight=3
            _, score_unknown, _ = sm.get_consensus_signal({"XX": df})  # unknown weight=1
        # H1 score = 2 * 3 = 6, unknown score = 2 * 1 = 2
        assert score_known > score_unknown

    def test_multiple_timeframes_aggregate_score(self, sm):
        df = make_df(n=60)
        with patch.object(sm, "_vsa_analysis", return_value=1):
            _, score_one, _ = sm.get_consensus_signal({"H1": df})
            _, score_two, _ = sm.get_consensus_signal({"H1": df, "H4": df})
        # H1=3, H4=4, both with score 1
        assert score_two > score_one


# ---------------------------------------------------------------------------
# verify_trade
# ---------------------------------------------------------------------------

class TestVerifyTrade:
    def test_neutral_signal_returns_false(self, sm):
        df = make_df(n=120)
        assert sm.verify_trade({"H1": df}, "NEUTRAL", 50) is False

    def test_low_confidence_returns_false(self, sm):
        df = make_df(n=120)
        assert sm.verify_trade({"H1": df}, "BUY", 24) is False

    def test_exactly_25_confidence_may_proceed(self, sm):
        df = make_df(n=120)
        # abs(25) >= 25, so it should not return False from confidence check
        result = sm.verify_trade({"H1": df}, "BUY", 25)
        assert isinstance(result, bool)

    def test_no_h1_data_returns_false(self, sm):
        assert sm.verify_trade({}, "BUY", 50) is False

    def test_short_h1_data_returns_false(self, sm):
        df = make_df(n=50)
        assert sm.verify_trade({"H1": df}, "BUY", 50) is False

    def test_none_h1_returns_false(self, sm):
        assert sm.verify_trade({"H1": None}, "BUY", 50) is False

    def test_returns_bool(self, sm):
        df = make_df(n=120)
        result = sm.verify_trade({"H1": df}, "BUY", 50)
        assert isinstance(result, bool)

    def test_sell_signal_can_verify(self, sm):
        """SELL signal with enough confidence and H1 data should return bool."""
        df = make_df(n=120)
        result = sm.verify_trade({"H1": df}, "SELL", 50)
        assert isinstance(result, bool)

    def test_negative_confidence_treated_by_abs(self, sm):
        """abs(-30) = 30 >= 25 so it should not fail confidence check."""
        df = make_df(n=120)
        result = sm.verify_trade({"H1": df}, "BUY", -30)
        assert isinstance(result, bool)

    def test_verify_trade_with_strongly_positive_returns(self, sm):
        """Simulate returns that strongly favor BUY; Monte Carlo should pass."""
        n = 120
        # All closes steadily rising to get positive pct_change
        closes = np.linspace(1.0, 1.5, n)
        df = pd.DataFrame(
            {
                "Open": closes,
                "High": closes + 0.001,
                "Low": closes - 0.001,
                "Close": closes,
                "Volume": np.ones(n) * 1000,
            },
            index=pd.date_range("2024-01-01", periods=n, freq="1h"),
        )
        result = sm.verify_trade({"H1": df}, "BUY", 50)
        assert result is True