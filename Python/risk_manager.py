import numpy as np

class RiskManager:
    def __init__(self, account_balance=10000, risk_per_trade=0.01):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, entry_price, stop_loss, tick_value=1.0, tick_size=0.00001, contract_size=100000):
        """
        Calculates the exact lot size based on account risk and symbol-specific parameters.
        """
        risk_amount = self.account_balance * self.risk_per_trade
        price_risk_points = abs(entry_price - stop_loss) / tick_size

        if price_risk_points == 0:
            return 0

        # Risk per lot in account currency
        # risk_per_lot = (price_risk_points * tick_value)
        # lot_size = risk_amount / risk_per_lot

        # Standard Forex Calculation:
        # Lot Size = Risk Amount / (Stop Loss in Pips * Value per Pip)
        # Here we use points for maximum precision across all asset classes
        lot_size = risk_amount / (price_risk_points * tick_value)

        return round(lot_size, 2)

    def evaluate_market_regime(self, df):
        """
        Identifies market regime based on volatility and trend persistence.
        """
        if df is None or df.empty or len(df) < 100:
            return "Normal"

        # Calculate True Range
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
    print("Risk Manager fully operational.")
