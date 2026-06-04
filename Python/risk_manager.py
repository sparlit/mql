import numpy as np

class RiskManager:
    def __init__(self, account_balance=10000, risk_per_trade=0.01):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, entry_price, stop_loss, symbol="EURUSD"):
        risk_amount = self.account_balance * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss)

        if price_risk == 0:
            return 0

        # Simplified lot size calculation (assuming 1 lot = 100,000 units)
        # In real MT5, we would use SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE)
        lot_size = risk_amount / (price_risk * 100000)
        return round(lot_size, 2)

    def evaluate_market_regime(self, df):
        # Calculate volatility (ATR)
        df['High-Low'] = df['High'] - df['Low']
        df['High-PrevClose'] = abs(df['High'] - df['Close'].shift(1))
        df['Low-PrevClose'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
        atr = df['TR'].rolling(window=14).mean().iloc[-1]

        avg_volatility = df['TR'].rolling(window=100).mean().iloc[-1]

        if atr > avg_volatility * 1.5:
            return "High Volatility - Reduce Risk"
        elif atr < avg_volatility * 0.5:
            return "Low Volatility - Range Bound"
        else:
            return "Normal"

if __name__ == "__main__":
    rm = RiskManager()
    print("Risk Manager initialized")
