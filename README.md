# 🌌 Autonomous MT5 Autotrader (V3.2.0_20260606)

## Status: 100% Completed & Production Ready (L99 Certified)

### 🚀 New in V3.2.0: Dual-Mode Execution
AAT now supports **simultaneous** Scalping and Trading. The system evaluates micro-trends (M1-M15) and macro-regimes (H1-D1) in parallel, managing independent risk baskets for each.

---

## 🛠 Dual-Mode Configuration

### 1. Python Engine
```bash
export PYTHONPATH=$(pwd)
python Python/V3_1_0/MainEngine.py
```
*The engine automatically outputs `mode`, `scalp_signal`, and `trade_signal` payloads.*

### 2. MT5 EA Setup
1. Attach `MQL5/V3_1_0/Experts/Scalper_v3_2_0.mq5` to a chart.
2. The dashboard now displays:
   - **MODE**: SCALP, TRADE, BOTH, or NEUTRAL.
   - **SCALP/TRADE**: Independent directional signals.
   - **CONF-S/CONF-T**: Individual consensus confidence scores.

---

## 📜 Audit & Evolution
- **Dynamic Exits**: TP/SL are now calculated using ML multipliers (`tp_mult`, `sl_mult`) for adaptive volatility management.
- **Audit Logs**: `sqlite3 db/aat_trading.db "SELECT * FROM aat_audit;"`
- **Author**: Simon Peter | **License**: 100% FOSS
