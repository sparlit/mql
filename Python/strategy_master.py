import numpy as np
import pandas as pd
import xgboost as xgb
import faiss
import logging
import os

class StrategyMaster:
    def __init__(self):
        """
        Initialize the StrategyMaster instance by loading the XGBoost model and preparing a FAISS index with initial vectors.
        
        This sets up the classifier used for pattern scoring and creates/populates the 64-dimensional FAISS IndexFlatL2 used for nearest-neighbor pattern lookup.
        """
        self.xgb_model = self._load_model()
        self.faiss_index = faiss.IndexFlatL2(64)
        self._init_faiss()

    def _load_model(self):
        """
        Load an XGBoost classifier from a predefined model file or create and return a minimal trained placeholder if the file is absent.
        
        Returns:
            xgb.XGBClassifier: The classifier loaded from "Python/models/xgb_v2.json" when available, otherwise a fitted dummy XGBClassifier trained on randomly generated data.
        """
        model = xgb.XGBClassifier()
        model_path = "Python/models/xgb_v2.json"
        if os.path.exists(model_path):
            model.load_model(model_path)
        else:
            # Zero-stub: Train a dummy model if none exists to ensure functional object
            X = np.random.rand(100, 10)
            y = np.random.randint(0, 2, 100)
            model.fit(X, y)
        return model

    def _init_faiss(self):
        # Zero-stub: Populate FAISS with initial random patterns if empty
        """
        Populate the FAISS index with a set of random 64-dimensional vectors to provide initial patterns.
        
        This initializes the instance's `faiss_index` by adding 100 random float32 vectors of dimension 64; intended as a stub dataset when no real patterns are available.
        """
        patterns = np.random.rand(100, 64).astype('float32')
        self.faiss_index.add(patterns)

    def get_consensus_signal(self, df_dict, sentiment=0):
        """
        Compute a consensus trading signal by aggregating VSA-derived scores across timeframes.
        
        Parameters:
            df_dict (dict): Mapping of timeframe strings (e.g., 'M1', 'M5', 'H1', 'D1') to pandas DataFrame candles for that timeframe. DataFrames with fewer than 50 rows or that are empty are ignored.
            sentiment (int): External sentiment adjustment applied as a multiplier of 10 to the aggregated score (positive favors buy, negative favors sell).
        
        Returns:
            tuple: A 3-tuple (signal, total_score, tf_results):
                - signal (str): One of "BUY", "SELL", or "NEUTRAL" determined by thresholds on the aggregated score.
                - total_score (float): Weighted sum of per-timeframe VSA scores after applying timeframe weights and the sentiment adjustment.
                - tf_results (dict): Per-timeframe numeric scores produced by the internal _vsa_analysis for each included timeframe.
        """
        tf_results = {}
        weights = {'M1':0.5, 'M5':1, 'M15':1.5, 'H1':3, 'H4':4, 'D1':5}
        total_score = 0

        for tf, df in df_dict.items():
            if df is None or df.empty or len(df) < 50: continue
            score = self._vsa_analysis(df)
            tf_results[tf] = score
            total_score += score * weights.get(tf, 1)

        total_score += sentiment * 10

        signal = "NEUTRAL"
        if total_score > 20: signal = "BUY"
        elif total_score < -20: signal = "SELL"

        return signal, total_score, tf_results

    def _vsa_analysis(self, df):
        """
        Compute a volume-spread-analysis (VSA) style score for the most recent bar.
        
        Parameters:
            df (pandas.DataFrame): Time series with columns 'Close', 'Volume', 'High', and 'Low'. Must contain at least 50 rows.
        
        Returns:
            int: Signed score where positive values indicate net bullish pressure and negative values indicate net bearish pressure.
        """
        close = df['Close']
        vol = df['Volume']
        spread = df['High'] - df['Low']

        avg_vol = vol.rolling(20).mean()
        avg_spread = spread.rolling(20).mean()

        curr_vol = vol.iloc[-1]
        curr_spread = spread.iloc[-1]
        curr_close = close.iloc[-1]
        prev_close = close.iloc[-2]

        score = 0
        if curr_vol > avg_vol.iloc[-1] * 2 and curr_close > prev_close: score -= 2
        elif curr_vol < avg_vol.iloc[-1] * 0.5 and curr_close > prev_close: score -= 1
        elif curr_vol > avg_vol.iloc[-1] * 1.5 and curr_close < prev_close and curr_spread < avg_spread.iloc[-1]: score += 2
        if curr_close > df['Close'].rolling(50).mean().iloc[-1]: score += 1
        else: score -= 1
        return score

    def verify_trade(self, dfs, signal, confidence):
        """
        Validate whether a proposed trade signal is supported by Monte Carlo sampling of recent H1 returns.
        
        This method rejects neutral or low-confidence signals, requires an 'H1' dataframe with at least 100 rows, computes percent-change returns from the H1 Close series, and runs 100 simulations where each simulation samples 24 returns (with replacement) to check directional wins for the given signal. The trade is approved only if at least 60 of the 100 simulations are wins.
        
        Parameters:
            dfs (dict): Mapping of timeframe keys (e.g., 'H1', 'M15') to pandas DataFrame objects containing market data with a 'Close' column.
            signal (str): Proposed trade direction, expected values are 'BUY', 'SELL', or 'NEUTRAL'.
            confidence (float or int): Numeric confidence score; signals with absolute value less than 25 are rejected.
        
        Returns:
            bool: `True` if the Monte Carlo simulation yields at least 60 winning samples out of 100, `False` otherwise.
        """
        if signal == "NEUTRAL" or abs(confidence) < 25: return False
        h1_df = dfs.get('H1')
        if h1_df is None or len(h1_df) < 100: return False

        returns = h1_df['Close'].pct_change().dropna()
        win_count = 0
        for _ in range(100):
            sim_path = np.random.choice(returns, 24)
            if (signal == "BUY" and sim_path.mean() > 0) or (signal == "SELL" and sim_path.mean() < 0):
                win_count += 1
        return win_count >= 60
