# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Institutional Risk Plugin (ATR + Equity Protection)

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any
from src.shared.utils.bus import bus
from src.shared.utils.state_coordinator import coordinator

class RiskPlugin:
    def __init__(self):
        self.max_equity_risk = 0.01 # 1% risk per trade
        bus.subscribe("intelligence:signal", self.evaluate_risk)

    def _calc_atr(self, df: pd.DataFrame, period=14):
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    async def evaluate_risk(self, data: Dict[str, Any]):
        if data["signal"] == "NEUTRAL": return

        symbol = data["symbol"]
        signal = data["signal"]

        # Fetch actual market data from coordinator
        market_data = coordinator.get_state(f"last_seen_{symbol}")
        if not market_data:
            logging.warning(f"Risk denial: No market data for {symbol}")
            return

        ohlc = market_data.get("ohlc", {}).get("M15")
        if not ohlc: return

        df = pd.DataFrame(ohlc, columns=['open', 'high', 'low', 'close', 'volume'])
        atr = self._calc_atr(df).iloc[-1]

        # Fetch real equity (synced from MT5 via StateCoordinator)
        equity = coordinator.get_state("account_equity") or 1000.0

        # SL calculation: 2 * ATR
        sl_dist = atr * 2
        if sl_dist == 0: sl_dist = 0.0002 # Fallback for low vol

        # Lot = (Equity * Risk%) / (SL_Distance * TickValue)
        # Simplified: Lot = (Equity * 0.01) / (ATR * 2 * 100000) for Forex
        risk_amount = equity * self.max_equity_risk
        recommended_lot = risk_amount / (sl_dist * 100000) # Assuming 100k contract
        recommended_lot = round(max(0.01, min(recommended_lot, 50.0)), 2)

        risk_data = {
            "symbol": symbol,
            "signal": signal,
            "recommended_lot": recommended_lot,
            "sl_price": df['close'].iloc[-1] - sl_dist if signal == "BUY" else df['close'].iloc[-1] + sl_dist,
            "status": "APPROVED"
        }

        logging.info(f"RISK_APPROVED: {symbol} {signal} {recommended_lot} lots | Equity: {equity}")
        await bus.emit("risk:approval", risk_data)

risk_plugin = RiskPlugin()
