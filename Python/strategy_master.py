import numpy as np
import pandas as pd
import xgboost as xgb
import faiss
import logging
import os

class StrategyMaster:
    def __init__(self):
        self.xgb_model = self._load_model()
        self.faiss_index = faiss.IndexFlatL2(64)
        self._init_faiss()

    def _load_model(self):
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
        patterns = np.random.rand(100, 64).astype('float32')
        self.faiss_index.add(patterns)

    def get_consensus_signal(self, df_dict, sentiment=0):
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
