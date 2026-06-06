import numpy as np
import pandas as pd
import xgboost as xgb
import faiss
import logging
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class StrategyMaster:
    def __init__(self):
        self.xgb_model = self._load_xgb_model()
        self.faiss_index = faiss.IndexFlatL2(64)
        self._init_faiss()
        self.tokenizer = None
        self.bert_model = None
        self._init_finbert()

    def _load_xgb_model(self):
        model = xgb.XGBClassifier()
        model_path = "Python/models/xgb_v2.json"
        if os.path.exists(model_path):
            model.load_model(model_path)
        else:
            X = np.random.rand(100, 10)
            y = np.random.randint(0, 2, 100)
            model.fit(X, y)
        return model

    def _init_faiss(self):
        patterns = np.random.rand(1000, 64).astype('float32')
        self.faiss_index.add(patterns)

    def _init_finbert(self):
        if os.environ.get("SKIP_FINBERT") == "1":
            logging.info("Skipping FinBERT initialization (Test Mode)")
            return
        try:
            # Attempt to load local FinBERT, if fails it might download (requires internet)
            model_name = "ProsusAI/finbert"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            logging.info("FinBERT initialized successfully")
        except Exception as e:
            logging.error(f"FinBERT Initialization Error: {e}. Falling back to VADER-like logic.")

    def get_sentiment_score(self, text):
        if not self.bert_model or not self.tokenizer:
            # Fallback logic
            bullish = ['buy', 'bullish', 'growth', 'upward', 'high']
            bearish = ['sell', 'bearish', 'decline', 'downward', 'low']
            score = 0
            for w in text.lower().split():
                if w in bullish: score += 1
                if w in bearish: score -= 1
            return np.tanh(score)

        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = self.bert_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        # FinBERT labels: 0: positive, 1: negative, 2: neutral
        sentiment = torch.argmax(probs).item()
        if sentiment == 0: return probs[0][0].item()
        if sentiment == 1: return -probs[0][1].item()
        return 0

    def get_consensus_signal(self, df_dict, sentiment_text=""):
        tf_results = {}
        weights = {'M1':0.5, 'M5':1, 'M15':1.5, 'H1':3, 'H4':4, 'D1':5}
        total_score = 0

        sentiment_score = self.get_sentiment_score(sentiment_text) if sentiment_text else 0

        for tf, df in df_dict.items():
            if df is None or df.empty or len(df) < 50: continue
            score = self._vsa_analysis(df)

            # FAISS Pattern Match
            pattern = df['Close'].pct_change().fillna(0).tail(64).values.astype('float32')
            if len(pattern) == 64:
                D, I = self.faiss_index.search(pattern.reshape(1, -1), 5)
                # If matches are 'good', boost score (Simplified logic)
                if D[0][0] < 0.01: score *= 1.2

            tf_results[tf] = score
            total_score += score * weights.get(tf, 1)

        total_score += sentiment_score * 20

        signal = "NEUTRAL"
        if total_score > 15: signal = "BUY"
        elif total_score < -15: signal = "SELL"

        # Monte Carlo Verification
        if signal != "NEUTRAL":
            if not self.run_monte_carlo(df_dict.get('H1'), signal):
                signal = "NEUTRAL" # Discard if failed simulation

        return signal, total_score, tf_results

    def _vsa_analysis(self, df):
        close = df['Close']
        vol = df['Volume']
        spread = df['High'] - df['Low']
        avg_vol = vol.rolling(20).mean()
        curr_vol = vol.iloc[-1]
        curr_close = close.iloc[-1]
        prev_close = close.iloc[-2]

        score = 0
        if curr_vol > avg_vol.iloc[-1] * 1.5:
            if curr_close > prev_close: score += 2 # Accumulation
            else: score -= 2 # Distribution

        if curr_close > df['Close'].rolling(50).mean().iloc[-1]: score += 1
        else: score -= 1
        return score

    def run_monte_carlo(self, df, signal, sims=100):
        if df is None or len(df) < 100: return False
        returns = df['Close'].pct_change().dropna().values
        success = 0
        for _ in range(sims):
            path = np.random.choice(returns, 24)
            if (signal == "BUY" and np.sum(path) > 0) or (signal == "SELL" and np.sum(path) < 0):
                success += 1
        return (success / sims) >= 0.6
