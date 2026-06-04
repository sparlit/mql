import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class StrategyMaster:
    def __init__(self):
        self.strategies = ["TrendFollowing", "MeanReversion", "Breakout"]

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def trend_following_signal(self, df):
        ema_short = df['Close'].ewm(span=12, adjust=False).mean()
        ema_long = df['Close'].ewm(span=26, adjust=False).mean()
        macd = ema_short - ema_long
        signal_line = macd.ewm(span=9, adjust=False).mean()

        if macd.iloc[-1] > signal_line.iloc[-1] and macd.iloc[-2] <= signal_line.iloc[-2]:
            return 1 # Buy
        elif macd.iloc[-1] < signal_line.iloc[-1] and macd.iloc[-2] >= signal_line.iloc[-2]:
            return -1 # Sell
        return 0

    def mean_reversion_signal(self, df):
        rsi = self.calculate_rsi(df['Close'])
        if rsi.iloc[-1] < 30:
            return 1 # Oversold - Buy
        elif rsi.iloc[-1] > 70:
            return -1 # Overbought - Sell
        return 0

    def breakout_signal(self, df):
        window = 20
        upper_band = df['High'].rolling(window=window).max()
        lower_band = df['Low'].rolling(window=window).min()

        if df['Close'].iloc[-1] > upper_band.iloc[-2]:
            return 1
        elif df['Close'].iloc[-1] < lower_band.iloc[-2]:
            return -1
        return 0

    def scalping_signal(self, df):
        # High frequency scalping logic based on price action and stochastic
        # Using shorter window
        window = 5
        fast_sma = df['Close'].rolling(window=window).mean()
        slow_sma = df['Close'].rolling(window=20).mean()

        if fast_sma.iloc[-1] > slow_sma.iloc[-1] and fast_sma.iloc[-2] <= slow_sma.iloc[-2]:
            return 1
        elif fast_sma.iloc[-1] < slow_sma.iloc[-1] and fast_sma.iloc[-2] >= slow_sma.iloc[-2]:
            return -1
        return 0

    def get_consensus_signal(self, df_dict):
        # df_dict: {'H1': df1, 'M15': df2, 'D1': df3}
        tf_weights = {'M15': 1, 'H1': 2, 'D1': 3}
        total_consensus = 0

        for tf, df in df_dict.items():
            if df is None or df.empty: continue

            signals = [
                self.trend_following_signal(df),
                self.mean_reversion_signal(df),
                self.breakout_signal(df),
                self.scalping_signal(df)
            ]
            tf_consensus = sum(signals)
            total_consensus += tf_consensus * tf_weights.get(tf, 1)

        if total_consensus >= 5:
            return "BUY", total_consensus
        elif total_consensus <= -5:
            return "SELL", total_consensus
        else:
            return "NEUTRAL", total_consensus

if __name__ == "__main__":
    # Test logic
    master = StrategyMaster()
    print("Strategy Master initialized")
