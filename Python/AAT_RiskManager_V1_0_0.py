import pandas as pd

class RiskManager:
    def __init__(self):
        self.max_equity_risk = 0.05
        self.pyramid_limit = 5

    def evaluate_market_regime(self, df):
        if df is None or len(df) < 50: return "Stable"
        atr = self._calc_atr(df)
        avg_atr = atr.rolling(50).mean().iloc[-1]
        curr_atr = atr.iloc[-1]

        if curr_atr > avg_atr * 1.5: return "High Volatility"
        if curr_atr < avg_atr * 0.5: return "Low Volatility"
        return "Stable"

    def _calc_atr(self, df, period=14):
        high_low = df['High'] - df['Low']
        high_cp = abs(df['High'] - df['Close'].shift())
        low_cp = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def calculate_lot_size(self, balance, risk_pct, sl_points, tick_value):
        risk_amount = balance * (risk_pct / 100)
        if sl_points == 0 or tick_value == 0: return 0.01
        lot = risk_amount / (sl_points * tick_value)
        return round(lot, 2)
