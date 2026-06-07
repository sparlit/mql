# 🏅 L99 Certification Verification Manual (V4.1.2 Sovereign Citadel)

This document provides definitive, step-by-step instructions to verify the production-readiness of the AAT V4.1.2 stack.

## 1. Environment Integrity
```bash
# Check Essential Libs
python -c "import torch, xgboost, cryptography, requests; print('INTEGRITY: OK')"

# Verify local model cache exists or is ready to be created
ls Python/models/finbert/config.json || echo "First run will cache models locally."
```

## 2. Infrastructure Verification
1.  **Symmetric Heartbeat**:
    -   Start Engine. Attach EA. Observe status **STABLE**.
    -   Force-close Python Engine.
    -   Verify EA moves positions to BE and status changes to **WATCHDOG HALT** within 10 seconds.
2.  **MT5-Primary Ingress**:
    -   Check `engine_debug.log` for: `[INFO] Received OHLC data from MT5`.
    -   This confirms the engine is not relying on `yfinance` for primary decisions.
3.  **Tiered AI Sentiment**:
    -   Start a local LLM server on port 8082 (Optional).
    -   Verify Python logs show: `[DEBUG] Local LLM analysis successful` or `[DEBUG] Falling back to FinBERT`.
4.  **Process Pool Performance**:
    -   Ensure `engine_debug.log` shows zero "Inference Timeout" errors during fast-moving markets.

## 3. Regression Testing
Run the automated suite to ensure parity:
```bash
# Windows
$env:PYTHONPATH="."
python -m pytest Python/V3_1_0/test_suite_v3.py

# Linux
export PYTHONPATH=$(pwd)
python3 -m pytest Python/V3_1_0/test_suite_v3.py
```

## 4. UI/UX "Glass Cockpit" Protocol
-   **Click Test**: Click `[ HEALTH ]`, `[ ANALYTICS ]`, and `[ SETTINGS ]`. Verify tab content switches instantly.
-   **Header Monitor**: Ensure "AAT SOVEREIGN CITADEL V4.1.2" remains visible and neon-green during stable operation.
-   **Settings Integrity**: Verify "AI SERVER: 127.0.0.1:8082" is displayed in the Settings tab.

## 5. Risk Safeguard Verification
1.  **Equity MA**:
    -   Manually simulate a drawdown (or reduce balance in demo).
    -   Verify Python logs: `Risk scaled down due to Equity MA breach`.
2.  **ATR Trailing**:
    -   Verify `MQL5 Experts Log` shows `PositionModify` when profit > 1.5x current ATR.
