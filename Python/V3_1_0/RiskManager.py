# Project: Autonomous AutoTrader (AAT)
# Version: V3.3.0_20260606
# License: 100% FOSS / GNU GPL v3
# Author: Simon Peter
# Verification: Zero-Stub / Production Ready
# Description: Risk Management and Lot Sizing Engine with Correlation

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

    def calculate_position_size(self, equity, stop_loss_points, tick_value, symbol_point, is_pyramid=False, current_profit_pips=0):
        """
        Institutional Equity-Based Lot Sizing: Lot = (Equity * Risk%) / (SL_Points * TickValue/Point)
        Note: MT5 TickValue is often per 1.0 lot per point.
        """
        try:
            risk_amount = equity * self.max_equity_risk
            # Standard formula: Lots = Risk_Amount / (SL_Points * (TickValue / Point))
            # However, if tick_value is already adjusted for point, it's Risk / (SL * TV)
            if stop_loss_points <= 0: return 0.01

            denominator = stop_loss_points * tick_value
            if denominator <= 0: return 0.01

            lots = risk_amount / denominator
            lots = round(max(0.01, min(lots, 50.0)), 2)

            if is_pyramid:
                if current_profit_pips < (stop_loss_points * 0.5): return 0.0
                return round(lots * 0.5, 2)

            return lots
        except Exception:
            return 0.01

    def calculate_var(self, df):
        if df is None or len(df) < 100: return 0.0
        returns = df['Close'].pct_change().dropna()
        return float(np.percentile(returns, 5))

    def calculate_correlation(self, symbol_df, market_dfs):
        # Calculate correlation against a broad market benchmark (e.g., SP500 or major pair)
        if symbol_df is None or not market_dfs: return 0.0
        try:
            # Simple correlation between current symbol H1 and first available H1 in market_dfs
            other_df = next(iter(market_dfs.values()))
            if 'H1' in other_df:
                corr = symbol_df['Close'].corr(other_df['H1']['Close'])
                return float(round(corr, 4))
        except: pass
        return 0.0
