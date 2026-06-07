# 🏅 L99 Certification Verification Manual (V4.1.2 Sovereign Citadel)

This document provides definitive, step-by-step instructions to verify the production-readiness of the AAT V4.1.2 masterpiece.

## 1. Environment Integrity Check
```bash
# Verify Python 3.10+ and requirements
python --version
python -c "import torch, xgboost, cryptography, requests, sklearn; print('INTEGRITY: OK')"

# Verify filesystem version control
ls MQL5/Experts/V4_1_2/Scalper_v4_1_2.mq5
ls Python/V4_1_2/MainEngine.py
```

## 2. Infrastructure Stress-Testing
1.  **Symmetric Watchdog Loop**:
    -   Start Engine. Observe status **STABLE**.
    -   Force-close Python process.
    -   Verify EA moves positions to BE (+20 points) and status changes to **WATCHDOG HALT** within exactly 10s.
2.  **MT5-Primary Ingress Verification**:
    -   Examine `engine_debug.log`.
    -   Verify presence of: `[INFO] Received OHLC data from MT5 (6 timeframes)`.
3.  **Atomic Shared Memory (IPC)**:
    -   Open 3 terminal instances on the same machine.
    -   Verify `engine_debug.log` shows zero `WaitForSingleObject` timeout errors.
4.  **Process Pool Efficiency**:
    -   Run `python Python/V4_1_2/stress_test.py`.
    -   Verify sub-10ms response times under 10 concurrent requests.

## 3. Intelligence Tiering Protocol
1.  **Sentiment Failover**:
    -   Disconnect Internet.
    -   Verify logs: `[DEBUG] Local FinBERT analysis successful` (Loaded from `./Python/models/finbert`).
2.  **AI Server Sync**:
    -   Start local server @ `http://127.0.0.1:8082`.
    -   Verify logs: `[DEBUG] Primary Local LLM analysis successful`.

## 4. UI/UX "Glass Cockpit" Verification
-   **Click Fidelity**: Test click-switching between `[ HEALTH ]`, `[ ANALYTICS ]`, and `[ SETTINGS ]`.
-   **Header Stability**: Ensure "AAT SOVEREIGN CITADEL V4.1.2" remains visible across all tab states.
-   **Telemetry**: Confirm real-time updates for Latency (ms) and Heartbeat (Epoch).

## 5. Quantitative Safeguards
1.  **Equity MA Breach**:
    -   Simulate account drawdown by 3%.
    -   Verify Python logs: `Risk scaled to 0.5x due to Equity MA breach (Level 1)`.
2.  **ATR-Derived Trailing**:
    -   Observe trade execution logs.
    -   Verify `PositionModify` distance matches the `trailing_points` received from the brain.
