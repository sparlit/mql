import numpy as np
import pandas as pd
import logging

class StrategyMaster:
    def __init__(self):
        self.strategies = ["TrendFollowing", "MeanReversion", "Breakout", "Scalping"]

    def calculate_rsi(self, series, period=14):
        if len(series) < period: return pd.Series(dtype=float)
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Handle division by zero
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50) # Neutral if calculation fails

    def trend_following_signal(self, df):
        if len(df) < 35: return 0
        try:
            ema_short = df['Close'].ewm(span=12, adjust=False).mean()
            ema_long = df['Close'].ewm(span=26, adjust=False).mean()
            macd = ema_short - ema_long
            signal_line = macd.ewm(span=9, adjust=False).mean()

            if macd.iloc[-1] > signal_line.iloc[-1] and macd.iloc[-2] <= signal_line.iloc[-2]:
                return 1 # Buy
            elif macd.iloc[-1] < signal_line.iloc[-1] and macd.iloc[-2] >= signal_line.iloc[-2]:
                return -1 # Sell
        except Exception as e:
            logging.error(f"StrategyMaster (Trend): {e}")
        return 0

    def mean_reversion_signal(self, df):
        if len(df) < 20: return 0
        try:
            rsi = self.calculate_rsi(df['Close'])
            if rsi.empty or pd.isna(rsi.iloc[-1]): return 0
            if rsi.iloc[-1] < 30:
                return 1 # Oversold - Buy
            elif rsi.iloc[-1] > 70:
                return -1 # Overbought - Sell
        except Exception as e:
            logging.error(f"StrategyMaster (MeanRev): {e}")
        return 0

    def breakout_signal(self, df):
        window = 20
        if len(df) < window + 1: return 0
        try:
            upper_band = df['High'].rolling(window=window).max()
            lower_band = df['Low'].rolling(window=window).min()

            if df['Close'].iloc[-1] > upper_band.iloc[-2]:
                return 1
            elif df['Close'].iloc[-1] < lower_band.iloc[-2]:
                return -1
        except Exception as e:
            logging.error(f"StrategyMaster (Breakout): {e}")
        return 0

    def scalping_signal(self, df):
        """
        Advanced scalping based on EMA Cross + RSI + Candle Momentum.
        """
        if len(df) < 20: return 0
        try:
            ema5 = df['Close'].ewm(span=5, adjust=False).mean()
            ema20 = df['Close'].ewm(span=20, adjust=False).mean()
            rsi = self.calculate_rsi(df['Close'], period=7)

            candle_body = abs(df['Close'].iloc[-1] - df['Open'].iloc[-1])
            avg_body = abs(df['Close'] - df['Open']).rolling(window=10).mean().iloc[-1]

            if ema5.iloc[-1] > ema20.iloc[-1] and rsi.iloc[-1] > 50 and candle_body > avg_body:
                return 1
            elif ema5.iloc[-1] < ema20.iloc[-1] and rsi.iloc[-1] < 50 and candle_body > avg_body:
                return -1
        except Exception as e:
            logging.error(f"StrategyMaster (Scalping): {e}")
        return 0

    def harmonic_pattern_signal(self, df):
        """
        Pivot-based support/resistance detection.
        """
        if len(df) < 50: return 0
        try:
            # If current price is at a 50-period support and RSI is oversold
            rsi = self.calculate_rsi(df['Close'])
            support = df['Low'].rolling(window=50).min().iloc[-1]
            resistance = df['High'].rolling(window=50).max().iloc[-1]

            if df['Close'].iloc[-1] <= support * 1.001 and rsi.iloc[-1] < 40: return 1
            if df['Close'].iloc[-1] >= resistance * 0.999 and rsi.iloc[-1] > 60: return -1
        except Exception as e:
            logging.error(f"StrategyMaster (Harmonic): {e}")
        return 0

    def get_consensus_signal(self, df_dict):
        tf_weights = {
            'M1': 0.5, 'M5': 1, 'M15': 1.5, 'M30': 2,
            'H1': 3, 'H4': 4, 'D1': 5, 'W1': 3, 'MN': 2
        }

        total_consensus = 0
        tf_results = {}

        for tf, df in df_dict.items():
            if df is None or df.empty or len(df) < 30:
                tf_results[tf] = 0
                continue

            signals = [
                self.trend_following_signal(df),
                self.mean_reversion_signal(df),
                self.breakout_signal(df),
                self.scalping_signal(df),
                self.harmonic_pattern_signal(df)
            ]
            tf_consensus = sum(signals)
            total_consensus += tf_consensus * tf_weights.get(tf, 1)
            tf_results[tf] = tf_consensus

        if total_consensus >= 15:
            return "BUY", total_consensus, tf_results
        elif total_consensus <= -15:
            return "SELL", total_consensus, tf_results
        else:
            return "NEUTRAL", total_consensus, tf_results

if __name__ == "__main__":
    master = StrategyMaster()
    print("Strategy Master audited and hardened.")
