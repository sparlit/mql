import pandas as pd
import numpy as np

class RiskManager:
    def __init__(self):
        self.max_equity_risk = 0.05
        self.pyramid_limit = 5
        self.account_balance = 10000

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

    def calculate_position_size(self, entry_price, stop_loss_points, tick_value, is_pyramid=False, current_profit_pips=0):
        # Base lot 0.01 for first qty
        if not is_pyramid: return 0.01

        # Pyramid logic:
        # "when the trades moves into a profit position of a certain pips that covers the investment value,
        # then follow the pyramid system of trading."
        # investment value = 0.01 * stop_loss_points * tick_value
        investment_value = 0.01 * stop_loss_points * tick_value
        current_profit_val = current_profit_pips * tick_value * 0.01 # Assuming 0.01 lot for profit calculation

        if current_profit_pips >= stop_loss_points:
            return 0.01 # Fixed 0.01 as requested: "0.01 as first qty for all symbols"

        return 0.0

    def calculate_var(self, df):
        if df is None or len(df) < 100: return 0.0
        returns = df['Close'].pct_change().dropna()
        return np.percentile(returns, 5)

    def calculate_correlation(self, all_dfs):
        # Simplified correlation between the first two available symbols
        if len(all_dfs) < 2: return 0.0
        keys = list(all_dfs.keys())
        df1 = all_dfs[keys[0]]['H1']['Close']
        df2 = all_dfs[keys[1]]['H1']['Close']
        return df1.corr(df2)
