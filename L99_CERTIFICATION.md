# 🏅 L99 Certification Verification Manual (V3.1.0_20260606)

This document provides step-by-step instructions to verify the production-readiness of the Autonomous MT5 Autotrader V3.1.0.

## 1. Environment Verification
```bash
# Install and Verify Python Environment
pip install -r Python/requirements.txt
pip list | grep -E "torch|transformers|xgboost|faiss|questdb|pandas|yfinance"
```

## 2. Infrastructure Testing
1. Start QuestDB (Standard Docker or Portable) on port 9009.
2. Start Engine:
   - Linux: `PYTHONPATH=. python3 Python/V3_1_0/MainEngine.py`
   - Windows (PS): `$env:PYTHONPATH="."; python Python/V3_1_0/MainEngine.py`
   - Windows (CMD): `set PYTHONPATH=. && python Python/V3_1_0/MainEngine.py`
3. Run `PYTHONPATH=. python3 Python/V3_1_0/stress_test.py` to simulate 10 concurrent connections.
4. Verify SQLite audit logs: `sqlite3 db/aat_trading.db "SELECT * FROM aat_audit;"`.
5. Verify Maintenance logs: `sqlite3 db/aat_trading.db "SELECT * FROM dev_maintenance_log;"`.

## 3. Unit Testing
Run the versioned regression suite:
```bash
# Linux
export PYTHONPATH=$(pwd)
python3 -m pytest Python/V3_1_0/test_suite_v3.py

# Windows (PS)
$env:PYTHONPATH="."
python -m pytest Python/V3_1_0/test_suite_v3.py
```

## 4. MT5 Dashboard
Verify the dashboard displays:
- **ENGINE V4.0.0 OK**
- **LATENCY** in ms.
- **STABLE** or **ARB ALERT** status.
- **WATCHDOG** status (STABLE / RECOVERING / HALT).

## 5. V4.0 Feature Verification
### Watchdog & Heartbeat (AP 29)
1. Close the Python Engine.
2. Observe EA moving all positions to Break-Even (BE) and status changing to **WATCHDOG HALT** after 15s.
3. Restart Python Engine.
4. Observe status changing to **RECOVERING 1/3**, **2/3**, then **STABLE**.

### Non-Blocking Communication (AP 30)
1. Open MT5 Chart and move the window while EA is analyzing.
2. UI should remain fluid with zero "Not Responding" events.

### Arbitrage & Shared Memory (AP 31)
1. Open two MT5 terminals.
2. Verify `SharedMemory.dll` is in `MQL5/Libraries/V3_1_0/`.
3. Check `engine_debug.log` for shared benchmark updates.
