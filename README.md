# 🌌 Autonomous AutoTrader (AAT) V4.0.0

## 🛡️ Production-Grade L99 Certified FOSS Trading System

Autonomous AutoTrader (AAT) is an industrial-grade, 100% FOSS hybrid trading system combining the execution power of **MetaTrader 5 (MQL5)** with the advanced intelligence of **Python**. V4.0 introduces the **Industrial Safety Protocol (ISP)**, making it one of the most robust autonomous systems for high-stakes environments.

---

## 🚀 Key Features in V4.0

### 1. Active System Watchdog (AP 29)
Maximum safety for high-stakes trading. The EA monitors the Python engine's heartbeat. If latency exceeds **15 seconds**, the system triggers:
- **Emergency Halt**: Prevents new trades.
- **Capital Protection**: Moves all open positions to **Break-Even (+20 points)** immediately.
- **3-Stage Recovery**: Automatic resumption only after 3 consecutive successful heartbeats.

### 2. Non-Blocking Async Communication (AP 30)
Refactored MQL5 socket architecture using a **Non-Blocking State Machine**.
- **Zero UI Freeze**: The MT5 terminal remains fluid even during heavy AI inference.
- **Latency Tracking**: Real-time monitoring of round-trip communication time.

### 3. Shared-Memory Arbitrage (AP 31)
Evolutionary arbitrage monitoring using a custom C++ DLL (`SharedMemory.dll`).
- **Benchmark Sync**: Instantly share `yfinance` benchmark prices across all terminal instances.
- **Real-Time Alerts**: Detects broker price discrepancies >50 points instantly.

---

## 🧠 Intelligence Stack

- **Sentiment Engine**: FinBERT (ProsusAI) with **Dynamic Quantization** for high-speed CPU inference.
- **Consensus Model**: XGBoost Classifier combined with Multi-Timeframe VSA (Volume Spread Analysis).
- **Signature Matching**: **FAISS** (Facebook AI Similarity Search) to match current market patterns against 10,000+ historical "Master Signatures".
- **Dual-Mode**: Parallel execution engines for **Scalping** (M1-M15) and **Trend Trading** (H1-D1).

---

## 📉 Risk Management & Security

- **Dynamic Lot Sizing**: Risk-adjusted position sizing based on real-time equity, ATR volatility, and stop-loss.
- **Pyramid Scaling**: "House Money" logic—closes 25% of Layer 1 when Layer 3 opens, moving the basket to risk-neutral.
- **AES-256-CBC**: All communication between MQL5 and Python is encrypted with military-grade AES-256.
- **Audit Trail**: Every decision, health transition, and watchdog event is logged to a local **SQLite** database (`aat_audit`).

---

## 🛠️ Installation & Setup

### Prerequisites
- MetaTrader 5 Terminal.
- Python 3.10+.
- QuestDB (Optional, for high-volume time-series logging).

### 1. Python Environment Setup
```bash
# Clone and Install Dependencies
pip install pandas numpy yfinance xgboost scikit-learn faiss-cpu cryptography transformers torch beautifulsoup4 requests questdb lxml pytest
```

### 2. Python Brain Execution
```bash
export PYTHONPATH=$(pwd)
python3 Python/V3_1_0/MainEngine.py
```

### 3. MT5 EA Configuration
1. Copy `MQL5/Experts/V3_1_0/Scalper_v4_0_0.mq5` to your MT5 Experts folder.
2. Ensure `SharedMemory.dll` is in `MQL5/Libraries/V3_1_0/`.
3. Enable "Allow DLL imports" in MT5 settings.
4. Input `InpWatchdogSec` (default: 15) and `InpRiskPercent`.

---

## 📁 Directory Structure
- `MQL5/`: Expert Advisors, Include files, and C++ Libraries.
- `Python/V3_1_0/`: Core Logic, Strategy, Risk, and Security modules.
- `db/`: Persistent SQLite audit logs.
- `L99_CERTIFICATION.md`: Detailed verification and stress-testing manual.

---

## 🏅 Certification & Ethics
- **100% FOSS**: Zero stubs, zero hidden wrappers, zero placeholders.
- **Zero-Stub Policy**: Production-ready code from day one.
- **Author**: Simon Peter
- **License**: GNU GPL v3
