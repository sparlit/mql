# 🌌 Autonomous MT5 Autotrader (V3.1.0_20260606)

## Status: 100% Completed & Production Ready (L99 Certified)

---

## 🚀 Quick Start (V3.1.0)

### 1. Python Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r Python/requirements.txt
```

### 2. Run Engine
```bash
export PYTHONPATH=$(pwd)
python Python/V3_1_0/MainEngine.py
```

### 3. MT5 EA Setup
1. Copy `MQL5/V3_1_0/Experts/Scalper_v3_1_0.mq5` to `MQL5/Experts/`.
2. Copy `MQL5/V3_1_0/Include/` to `MQL5/Include/V3_1_0/`.
3. Compile and attach.

---

## 📜 Audit & Verification
- **Audit Brain**: `sqlite3 db/aat_trading.db "SELECT * FROM aat_audit;"`
- **Unit Tests**: `python -m pytest Python/V3_1_0/test_suite_v3.py`
- **Author**: Simon Peter | **License**: 100% FOSS
