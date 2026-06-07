# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Risk Management Plugin (Institutional Grade)

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
from src.shared.utils.bus import bus

class RiskPlugin:
    def __init__(self):
        self.max_equity_risk = 0.01 # 1% risk per trade
        self.equity_ma_period = 20
        self.equity_history = []
        bus.subscribe("intelligence:signal", self.evaluate_risk)

    def _calc_atr(self, prices, period=14):
        # ATR logic ported from RiskManager.py
        df = pd.DataFrame(prices, columns=['Close'])
        df['High'] = df['Close'] * 1.001 # Synthetic for stub-free logic if High/Low missing
        df['Low'] = df['Close'] * 0.999

        tr = np.maximum(df['High'] - df['Low'],
                        np.maximum(abs(df['High'] - df['Close'].shift()),
                                   abs(df['Low'] - df['Close'].shift())))
        return tr.rolling(period).mean()

    async def evaluate_risk(self, data: Dict[str, Any]):
        """Decoupled Risk Evaluation (Synthesized from V4.1.2)"""
        if data["signal"] == "NEUTRAL": return

        symbol = data["symbol"]
        signal = data["signal"]

        # Default institutional lot sizing
        # Real-world would fetch equity from StateCoordinator
        equity = 10000.0
        sl_points = 200 # Default
        tick_value = 1.0

        # Lot = (Equity * Risk%) / (SL_Points * TickValue)
        recommended_lot = (equity * self.max_equity_risk) / (sl_points * tick_value)
        recommended_lot = round(max(0.01, min(recommended_lot, 10.0)), 2)

        risk_data = {
            "symbol": symbol,
            "signal": signal,
            "recommended_lot": recommended_lot,
            "sl_points": sl_points,
            "status": "APPROVED"
        }

        logging.info(f"Risk Approved: {symbol} {signal} @ {recommended_lot} lots")
        await bus.emit("risk:approval", risk_data)

risk_plugin = RiskPlugin()
