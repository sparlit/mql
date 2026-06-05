import pandas as pd

class RiskManager:
    def __init__(self):
        """
        Initialize RiskManager configuration.
        
        Sets default risk and pyramiding limits:
        - max_equity_risk (float): Maximum fraction of account equity allowed at risk per trade (0.05).
        - pyramid_limit (int): Maximum number of additional pyramided entries allowed (5).
        """
        self.max_equity_risk = 0.05
        self.pyramid_limit = 5

    def evaluate_market_regime(self, df):
        """
        Determine the current market volatility regime based on ATR comparison to its 50-period rolling average.
        
        Parameters:
            df (pandas.DataFrame): Price series containing at least 'High', 'Low', and 'Close' columns and at least 50 rows.
        
        Returns:
            str: One of "High Volatility" if the latest ATR is greater than 1.5× the 50-period ATR average, "Low Volatility" if it is less than 0.5× that average, or "Stable" otherwise.
        """
        if df is None or len(df) < 50: return "Stable"
        atr = self._calc_atr(df)
        avg_atr = atr.rolling(50).mean().iloc[-1]
        curr_atr = atr.iloc[-1]

        if curr_atr > avg_atr * 1.5: return "High Volatility"
        if curr_atr < avg_atr * 0.5: return "Low Volatility"
        return "Stable"

    def _calc_atr(self, df, period=14):
        """
        Compute the Average True Range (ATR) series from price data.
        
        Parameters:
            df (pandas.DataFrame): OHLC price data containing 'High', 'Low', and 'Close' columns.
            period (int): Window length for the rolling mean used to produce the ATR (default 14).
        
        Returns:
            pandas.Series: ATR values computed as the rolling mean of the true range; the first `period - 1` entries will be `NaN`.
        """
        high_low = df['High'] - df['Low']
        high_cp = abs(df['High'] - df['Close'].shift())
        low_cp = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def calculate_lot_size(self, balance, risk_pct, sl_points, tick_value):
        """
        Calculate the position lot size based on account balance, risk percentage, stop-loss distance, and per-point value.
        
        Parameters:
            balance (float): Total account balance used to compute risk amount.
            risk_pct (float): Percentage of the balance to risk for the trade (e.g., 1.0 for 1%).
            sl_points (float): Stop-loss distance in price points.
            tick_value (float): Monetary value of one price point.
        
        Returns:
            float: Lot size rounded to 2 decimal places. If `sl_points` or `tick_value` is zero, returns `0.01`.
        """
        risk_amount = balance * (risk_pct / 100)
        if sl_points == 0 or tick_value == 0: return 0.01
        lot = risk_amount / (sl_points * tick_value)
        return round(lot, 2)
