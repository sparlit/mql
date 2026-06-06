# 🌌 Autonomous MT5 Autotrader (100% FOSS)

## Status: 100% Completed & Production Ready (L99 Certified)

### 🚀 Key Features
- **Cyber-Pro Dashboard**: High-performance `CCanvas` UI with real-time telemetry (P&L, VaR, Spread, Countdown).
- **Hybrid Intelligence**: FinBERT Sentiment + XGBoost + FAISS Pattern Matching.
- **Adaptive Execution**: News Straddle (ATR-Adaptive), Pyramid Scaling (House Money logic), and multi-broker arbitrage detection.
- **Industrial Security**: AES-256-CBC encrypted communication between MT5 and Python Brain.
- **Autonomous Maintenance**: Weekend Bayesian Optimization for strategy tuning and SQLite/QuestDB logging.

### 🛠 Installation

#### 1. Python Brain
```bash
pip install -r Python/requirements.txt
python Python/AAT_MainEngine_V1_0_0.py
```

#### 2. MT5 Executor
- Copy `MQL5/Include/*.mqh` to your MT5 Include folder.
- Copy `MQL5/Experts/AutonomousTrader_B042_Scalper_v2.0_20260606.mq5` to Experts.
- Enable **DLL Imports** in MT5.
- Compile and Attach to any chart.

### 📜 FOSS Compliance
This project is 100% Free and Open Source. The C++ source for `SharedMemory.dll` is included in `MQL5/Libraries/`.
