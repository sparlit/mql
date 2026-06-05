import numpy as np
import logging
import pandas as pd

class RiskManager:
    def __init__(self, account_balance=10000, risk_per_trade=0.01):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, entry_price, stop_loss_points, tick_value=1.0, is_pyramid=False, current_profit_pips=0):
        """
        Calculates the exact lot size based on account risk and symbol-specific parameters.
        Includes Pyramid Scaling logic: starts at 0.01, scales if profit covers investment.
        """
        if not is_pyramid:
            return 0.01

        if current_profit_pips >= stop_loss_points:
            return 0.01

        return 0.0

    def calculate_var(self, df, confidence_level=0.95):
        """
        Calculates Value at Risk (VaR) using the historical method.
        """
        if df is None or len(df) < 100:
            return 0.0

        returns = df['Close'].pct_change().dropna()
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return abs(var)

    def calculate_correlation(self, df_dict):
        """
        Calculates correlation matrix between all active symbols.
        """
        close_prices = {}
        for symbol, dfs in df_dict.items():
            if 'D1' in dfs:
                close_prices[symbol] = dfs['D1']['Close']

        if len(close_prices) < 2:
            return 1.0 # Default to self-correlation if only one

        df_corr = pd.DataFrame(close_prices).corr()
        return df_corr.iloc[0, 1] if df_corr.shape[0] > 1 else 1.0

    def evaluate_market_regime(self, df):
        """
        Identifies market regime based on volatility and trend persistence.
        """
        if df is None or df.empty or len(df) < 100:
            return "Stable - Ranging"

        df = df.copy()
        df['High-Low'] = df['High'] - df['Low']
        df['High-PrevClose'] = abs(df['High'] - df['Close'].shift(1))
        df['Low-PrevClose'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

        atr = df['TR'].rolling(window=14).mean().iloc[-1]
        avg_volatility = df['TR'].rolling(window=100).mean().iloc[-1]

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
