# 🏅 L99 Certification Verification Manual (V5.0.0 Sovereign Citadel)

This document provides definitive, step-by-step instructions to verify the production-readiness of the AAT V5.0.0 Microkernel architecture.

## 1. Environment Integrity
```bash
# Verify Python 3.10+ and requirements
python --version
python -c "import fastapi, torch, xgboost, cryptography, requests, sklearn, onnxruntime; print('INTEGRITY: OK')"

# Verify filesystem version control (Zero Legacy Folders)
# The following should return errors (meaning legacy folders are gone)
ls Python/V4_1_2/ 2>/dev/null || echo "LEGACY REMOVED: OK"
ls MQL5/Experts/V4_1_2/ 2>/dev/null || echo "LEGACY REMOVED: OK"

# Verify new structure
ls MQL5/Experts/AAT_Sovereign_EA.mq5
ls src/core/main.py
```

## 2. Infrastructure Stress-Testing
1.  **Event Bus Latency**:
    -   Start Engine.
    -   Verify logs: `[INFO] AAT Microkernel V5.0.0 starting...`.
    -   The system should initialize in < 5s on SSD hardware.
2.  **Socket Ingress Decryption**:
    -   Connect using a mock client with AES-256-CBC.
    -   Verify engine prints: `Brain listening on 0.0.0.0:4444`.
    -   Verify `src/plugins/execution/ingress.py` emits `data:market_update` upon valid decryption.
3.  **Atomic State Handling**:
    -   Run `python -m pytest tests/test_core.py`.
    -   Verify all 2 tests pass (Bus Emission and Vault loading).

## 3. Intelligence Tiering Protocol
1.  **ONNX INT8 Quantization**:
    -   Run `python src/shared/models/quantize_model.py`.
    -   Verify `src/shared/models/finbert_onnx/model_quantized.onnx` exists.
2.  **Consensus Engine**:
    -   Examine `src/plugins/intelligence/engine.py`.
    -   Ensure `IntelligencePlugin` successfully loads `xgb_production.json` if present.

## 4. UI/UX "Glass Cockpit" Verification
-   **Dashboard Load**: Navigate to `http://127.0.0.1:8000`.
-   **Telemetry Visibility**: Ensure "SYSTEM STATUS: STABLE" is visible in the top right.
-   **Log Stream**: Confirm the "Risk & Audit Trail" section displays live event emissions.

## 5. Quantitative Safeguards
1.  **ATR-Derived Sizing**:
    -   Check `src/plugins/execution/risk.py`.
    -   Verify lot size is calculated using the formula: `(Equity * Risk%) / (SL_Points * TickValue)`.
2.  **Symmetric Watchdog**:
    -   Ensure `src/plugins/execution/ingress.py` closes connections gracefully on invalid payloads to prevent memory leaks.
