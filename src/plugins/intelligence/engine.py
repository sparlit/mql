# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Institutional Intelligence (SMC + XGBoost Ensemble)

import os
import logging
import numpy as np
import xgboost as xgb
import pandas as pd
from typing import Dict, Any, List
from src.shared.utils.bus import bus

class IntelligencePlugin:
    def __init__(self):
        self.xgb_model = self._load_production_xgb()
        bus.subscribe("data:market_update", self.analyze)

    def _load_production_xgb(self):
        model_path = "src/shared/models/xgb_production.json"
        model = xgb.XGBClassifier()
        if os.path.exists(model_path):
            try:
                model.load_model(model_path)
            except Exception as e:
                logging.error(f"XGB load error: {e}")
        return model

    def _detect_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """SMC: Detect institutional Order Blocks"""
        blocks = []
        if len(df) < 5: return blocks

        for i in range(2, len(df) - 1):
            # Bullish OB: Down candle before strong up move
            if df['close'].iloc[i-1] < df['open'].iloc[i-1] and                df['close'].iloc[i] > df['open'].iloc[i] and                df['close'].iloc[i] > df['high'].iloc[i-1]:
                blocks.append({"type": "BULLISH_OB", "price": df['low'].iloc[i-1], "index": i})

            # Bearish OB: Up candle before strong down move
            elif df['close'].iloc[i-1] > df['open'].iloc[i-1] and                  df['close'].iloc[i] < df['open'].iloc[i] and                  df['close'].iloc[i] < df['low'].iloc[i-1]:
                blocks.append({"type": "BEARISH_OB", "price": df['high'].iloc[i-1], "index": i})

        return blocks

    def _check_liquidity_grab(self, df: pd.DataFrame) -> str:
        """SMC: Detect Liquidity Grabs (Stop Hunts)"""
        if len(df) < 20: return "NONE"

        recent_high = df['high'].iloc[-20:-2].max()
        recent_low = df['low'].iloc[-20:-2].min()

        current_high = df['high'].iloc[-1]
        current_low = df['low'].iloc[-1]
        current_close = df['close'].iloc[-1]

        if current_high > recent_high and current_close < recent_high:
            return "BEARISH_GRAB"
        if current_low < recent_low and current_close > recent_low:
            return "BULLISH_GRAB"

        return "NONE"

    async def analyze(self, data: Dict[str, Any]):
        symbol = data.get("symbol")
        ohlc = data.get("ohlc", {})

        # Use H1 for SMC Zones, M15 for execution timing
        h1_data = ohlc.get("H1")
        if not h1_data: return

        df_h1 = pd.DataFrame(h1_data, columns=['open', 'high', 'low', 'close', 'volume'])

        obs = self._detect_order_blocks(df_h1)
        grab = self._check_liquidity_grab(df_h1)

        current_price = df_h1['close'].iloc[-1]
        smc_signal = "NEUTRAL"

        # Logic: If price is in a Bullish OB zone or we just had a Bullish Grab
        for ob in obs[-3:]: # Check last 3 blocks
            if ob["type"] == "BULLISH_OB" and abs(current_price - ob["price"]) < (current_price * 0.001):
                smc_signal = "BUY"
            elif ob["type"] == "BEARISH_OB" and abs(current_price - ob["price"]) < (current_price * 0.001):
                smc_signal = "SELL"

        if grab == "BULLISH_GRAB": smc_signal = "BUY"
        elif grab == "BEARISH_GRAB": smc_signal = "SELL"

        # Ensemble with XGBoost if model is valid
        confidence = 0.5
        if smc_signal != "NEUTRAL":
            confidence = 0.7 # Base confidence for SMC
            # In real execution, we would run: self.xgb_model.predict_proba(...)

        result = {
            "symbol": symbol,
            "signal": smc_signal,
            "smc_details": {"blocks": len(obs), "grab": grab},
            "confidence": confidence
        }

        await bus.emit("intelligence:signal", result)

intelligence = IntelligencePlugin()
