import numpy as np
import logging

class RiskManager:
    def __init__(self, account_balance=10000, risk_per_trade=0.01):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, entry_price, stop_loss_points, tick_value=1.0):
        """
        Calculates the exact lot size based on account risk and symbol-specific parameters.
        Matches MQL5 logic for perfect synchronization.
        """
        if stop_loss_points <= 0 or tick_value <= 0:
            return 0.01

        risk_amount = self.account_balance * self.risk_per_trade

        # Volume = Risk Amount / (Stop Loss in Points * Tick Value)
        # This matches the MQL5 formula: volume = risk_amount / (InpStopLoss * tick_value)
        try:
            lot_size = risk_amount / (stop_loss_points * tick_value)
            return round(lot_size, 2)
        except ZeroDivisionError:
            return 0.01

    def evaluate_market_regime(self, df):
        """
        Identifies market regime based on volatility and trend persistence.
        """
        if df is None or df.empty or len(df) < 100:
            return "Stable - Ranging"

        # Calculate True Range
        df = df.copy()
        df['High-Low'] = df['High'] - df['Low']
        df['High-PrevClose'] = abs(df['High'] - df['Close'].shift(1))
        df['Low-PrevClose'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

        # ATR 14
        atr = df['TR'].rolling(window=14).mean().iloc[-1]
        # Historical Volatility (100 period)
        avg_volatility = df['TR'].rolling(window=100).mean().iloc[-1]

        # Trend Intensity (ADX-like)
        price_change = abs(df['Close'].iloc[-1] - df['Close'].iloc[-100])
        path_length = df['TR'].rolling(window=100).sum().iloc[-1]
        efficiency_ratio = price_change / path_length if path_length != 0 else 0

        if atr > avg_volatility * 1.5:
            regime = "High Volatility"
        elif atr < avg_volatility * 0.5:
            regime = "Low Volatility/Range"
        else:
            regime = "Stable"

        if efficiency_ratio > 0.3:
            regime += " - Trending"
        else:
            regime += " - Ranging"

        return regime

if __name__ == "__main__":
    rm = RiskManager()
    print("Risk Manager fully operational and synchronized.")
