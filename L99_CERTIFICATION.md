# 🏅 L99 Certification Verification Manual

This document provides step-by-step instructions to verify the production-readiness and "L99" status of the Autonomous MT5 Autotrader.

## 1. Environment Verification
Ensure all dependencies are isolated and version-locked.
```bash
# Verify Python Environment
pip list | grep -E "torch|transformers|xgboost|faiss|questdb"
```

## 2. Infrastructure Testing (QuestDB & SQLite)
1. Start QuestDB (Standard Docker or Portable).
2. Run `Python/AAT_MainEngine_V1_0_0.py`.
3. Use `Python/AAT_StressTest_V1_0_0.py` to simulate 50 concurrent client connections.
4. Verify SQLite audit logs: `sqlite3 db/aat_trading.db "SELECT * FROM aat_audit;"`.
5. Verify QuestDB signal ingestion via QuestDB Web Console (Port 9000).

## 3. Data Ingestion Robustness
1. Run `python Python/test_aggregator_robustness.py`.
2. Observe status codes. 403/404 errors should trigger the **Multi-tier Fallback** (RSS/yfinance).
3. Confirm symbol-specific sentiment is being filtered in `engine_debug.log`.

## 4. Strategy & Intelligence
1. **FinBERT Quantization**: Verify engine startup logs for "FinBERT initialized with Dynamic Quantization".
2. **Weekend Optimization**: Run `python Python/optimizer.py` and verify `Python/models/faiss_signatures.npy` is updated.
3. **Monte Carlo**: Attach EA to MT5 and verify "Signal Discarded" logs if MC success rate < 60%.

## 5. MT5 Execution & Dashboard
1. Attach `AutonomousTrader_B042_Scalper_v2.0_20260606.mq5` to a chart.
2. Verify **Cyber-Pro Dashboard** displays:
   - Real-time **Latency** (ms).
   - **STABLE** or **ARB ALERT** status.
   - Consensus scores across all TFs.
3. Confirm **Auto-Charts** tiles all 6 timeframes upon initialization.

---
**Status: 100% Completed | Verified Production Ready**
