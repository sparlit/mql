# 🌌 Autonomous MT5 Autotrader (V3.3.0_20260606)

## Status: 100% Completed & Production Ready (L99 Certified)

### 🚀 Major Enhancements in V3.3.0
- **High-Priority Architecture**: Centralized constants (`AAT-Constants.mqh`) and utilities (`AAT-Utils.mqh`).
- **Performance**: Dashboard updates are now throttled to 500ms to reduce CPU overhead.
- **Risk Intelligence**: Real-time symbol correlation is now factored into the consensus engine.
- **MQL5 Stability**: Shifted from static to dynamic arrays for position management.

---

## 🚀 Quick Start (V3.3.0)

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
1. Copy `MQL5/Experts/V3_1_0/Scalper_v3_3_0.mq5` to your MT5 Experts folder.
2. Copy `MQL5/Include/V3_1_0/*.mqh` to your MT5 Include folder.
3. Compile and attach.

---

## 📜 Audit & Verification
- **Audit Brain**: `sqlite3 db/aat_trading.db "SELECT * FROM aat_audit;"`
- **Unit Tests**: `python -m pytest Python/V3_1_0/`
- **Author**: Simon Peter | **License**: 100% FOSS
