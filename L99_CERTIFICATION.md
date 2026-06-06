# 🏅 L99 Certification Verification Manual (V3.1.0_20260606)

This document provides step-by-step instructions to verify the production-readiness of the Autonomous MT5 Autotrader V3.1.0.

## 1. Environment Verification
```bash
# Verify Python Environment
pip list | grep -E "torch|transformers|xgboost|faiss|questdb"
```

## 2. Infrastructure Testing
1. Start QuestDB (Standard Docker or Portable).
2. Run `export PYTHONPATH=$(pwd) && python3 Python/V3_1_0/MainEngine.py`.
3. Run `python3 Python/V3_1_0/stress_test.py` to simulate 10 concurrent connections.
4. Verify SQLite audit logs: `sqlite3 db/aat_trading.db "SELECT * FROM aat_audit;"`.

## 3. Unit Testing
Run the versioned regression suite:
```bash
export PYTHONPATH=$(pwd)
python3 -m pytest Python/V3_1_0/test_suite_v3.py
```

## 4. MT5 Dashboard
Verify the dashboard displays:
- **ENGINE V3.1.0 OK**
- **LATENCY** in ms.
- **STABLE** or **ARB ALERT** status.
