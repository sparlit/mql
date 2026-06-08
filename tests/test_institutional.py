import pytest
import pandas as pd
from src.plugins.intelligence.engine import IntelligencePlugin
from src.plugins.execution.risk import RiskPlugin

@pytest.mark.asyncio
async def test_order_block_detection():
    intel = IntelligencePlugin()
    # Create a Bullish OB pattern
    data = {
        'open': [10, 11, 9, 12, 13],
        'high': [11, 12, 10, 13, 14],
        'low': [9, 10, 8, 11, 12],
        'close': [11, 10, 8, 13, 14], # 8 is the bottom of the OB candle
        'volume': [100, 100, 200, 300, 300]
    }
    df = pd.DataFrame(data)
    obs = intel._detect_order_blocks(df)
    assert any(ob['type'] == 'BULLISH_OB' for ob in obs)

@pytest.mark.asyncio
async def test_atr_calculation():
    risk = RiskPlugin()
    data = {
        'high': [1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.20, 1.21, 1.22, 1.23, 1.24],
        'low': [1.09, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.20, 1.21, 1.22, 1.23],
        'close': [1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.20, 1.21, 1.22, 1.23, 1.24]
    }
    df = pd.DataFrame(data)
    atr = risk._calc_atr(df, period=10)
    assert not atr.isnull().all()
    assert atr.iloc[-1] > 0
