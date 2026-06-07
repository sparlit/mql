# 🏅 L99 Certification Verification Manual (V4.1.0 Sovereign Citadel)

This document provides step-by-step instructions to verify the production-readiness of the Sovereign Citadel AAT V4.1.0.

## 1. Environment Verification
```bash
# Verify Python Environment & Vault
python -c "import cryptography; print('Security Layer: OK')"
ls Python/V3_1_0/vault.json || echo "Vault missing (Warning: Local Induction will create it)"
```

## 2. Infrastructure Testing (Sovereign Core)
1. **Symmetric Heartbeat (AP 29 Refined)**:
   - Start Engine: `PYTHONPATH=. python Python/V3_1_0/MainEngine.py`
   - Observe MT5 Dashboard status: **STABLE** (Green).
   - Kill Python process. Observe dashboard status: **WATCHDOG HALT** (Red) within exactly 10s.
2. **MT5-Primary Ingress (AP 30 Refined)**:
   - Check `engine_debug.log`.
   - Verify log line: `[DEBUG] Reconciling position ...` and `[INFO] Received OHLC data from MT5`.
3. **Atomic Shared Memory (AP 31 Refined)**:
   - Open 3 terminals. Verify `engine_debug.log` shows zero race condition errors for shared benchmark updates.

## 3. Unit Testing
Run the refined V4.1.0 regression suite:
```bash
$env:PYTHONPATH="."
python -m pytest Python/V3_1_0/test_suite_v3.py
```

## 4. UI/UX "Glass Cockpit"
Verify the dashboard features:
- **Global Header**: "AAT SOVEREIGN CITADEL V4.1.0" in Neon Green.
- **Tabs**: Clickable `[ HEALTH ]`, `[ ANALYTICS ]`, and `[ SETTINGS ]`.
- **Latency**: Sub-50ms (Localhost) or Sub-200ms (VPS).

## 5. Risk & Execution Verification
1. **Equity MA Protection**:
   - Manually reduce account balance by 5%.
   - Verify Python log: `Risk scaled down to 0.25x due to Equity MA breach`.
2. **ATR Trailing**:
   - Open a test trade. Verify EA modifies SL after profit exceeds 1.5x ATR.
