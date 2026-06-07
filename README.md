# 🌌 Autonomous AutoTrader (AAT) V4.0.0

Autonomous AutoTrader (AAT) is a high-performance, 100% FOSS hybrid trading system. It synergizes the deterministic execution of **MetaTrader 5 (MQL5)** with the advanced machine learning and NLP capabilities of **Python**. V4.0 introduces the **Industrial Safety Protocol (ISP)**, setting a new standard for autonomous capital protection.

---

## 🚀 Version 4.0 Core Evolutions

### 1. Active System Watchdog (AP 29)
The "Heartbeat" protocol ensures maximum safety. The MQL5 EA monitors the Python brain's responsiveness.
- **Emergency Halt**: If latency >15s, the system halts all new trade logic.
- **Capital Protection**: Automatically moves all open positions to **Break-Even (+20 points)**.
- **3-Stage Recovery**: Resumes operation only after 3 consecutive successful heartbeats (OK status).

### 2. Async Non-Blocking Communication (AP 30)
Refactored MQL5 socket architecture using a **Non-Blocking State Machine**.
- **Responsive UI**: The MetaTrader 5 terminal remains fluid and responsive even during heavy inference.
- **Latency Monitoring**: Real-time round-trip telemetry displayed on the Cyber-Pro dashboard.

### 3. Shared-Memory Arbitrage (AP 31)
High-speed benchmark price distribution using a custom C++ DLL.
- **Benchmark Sync**: Instantly share `yfinance` or reference terminal prices across all chart instances.
- **Discrepancy Alerts**: Real-time detection of broker price deviations >50 points.

---

## 🧠 Intelligence Stack

- **Sentiment Analysis**: FinBERT (ProsusAI) with **Dynamic Quantization** for sub-100ms CPU inference.
- **Consensus Engine**: XGBoost Classifier integrating Multi-Timeframe VSA (Volume Spread Analysis).
- **Pattern Matching**: **FAISS** (Facebook AI Similarity Search) used to query current patterns against 10,000+ historical "Master Signatures".
- **Dual-Mode Execution**: Simultaneous Scalping (M1-M15) and Trend Trading (H1-D1) via parallel analysis threads.

---

## 🛠️ Installation & Setup (Step-by-Step)

### Prerequisites
- MetaTrader 5 Terminal (Build 4000+ recommended).
- Python 3.10 or higher.
- SharedMemory.dll (included in `MQL5/Libraries/V3_1_0/`).

### 💻 Windows Setup
1. **Prepare Environment**:
   ```powershell
   # Run the automated setup script
   .\setup_portable_python.bat
   ```
2. **Start the Python Engine**:
   - **Using PowerShell**:
     ```powershell
     $env:PYTHONPATH = "."
     python Python/V3_1_0/MainEngine.py
     ```
   - **Using Command Prompt (CMD)**:
     ```cmd
     set PYTHONPATH=.
     python Python/V3_1_0/MainEngine.py
     ```
   - **Using Automated Script**:
     ```powershell
     .\run_engine.bat
     ```

### 🐧 Linux Setup (Bash)
1. **Prepare Environment**:
   ```bash
   # Make script executable and run
   chmod +x setup_portable_python.sh
   ./setup_portable_python.sh
   pip install -r Python/requirements.txt
   ```
2. **Start the Python Engine**:
   ```bash
   # Run with PYTHONPATH set to root
   PYTHONPATH=. python3 Python/V3_1_0/MainEngine.py
   ```

### 📈 MetaTrader 5 Configuration
1. **Files Deployment**:
   - Copy `MQL5/Experts/V3_1_0/Scalper_v4_0_0.mq5` to `MQL5/Experts/`.
   - Ensure `SharedMemory.dll` is in `MQL5/Libraries/V3_1_0/`.
2. **Terminal Settings**:
   - Navigate to `Tools -> Options -> Expert Advisors`.
   - Check **"Allow DLL imports"**.
   - Check **"Allow WebRequest for listed URL"** and add `http://127.0.0.1`.
3. **Execution**:
   - Attach the EA to any chart.
   - Monitor the **HEALTH** column on the dashboard for "STABLE" status.

---

## 📊 Risk Management & Security
- **Dynamic Lot Sizing**: Calculates risk based on equity, ATR, and stop-loss distance.
- **Pyramid Logic**: "House Money" scaling closes partial profit to fund further layers risk-free.
- **AES-256 Transport**: All data between MQL5 and Python is encrypted via AES-256-CBC.
- **Audit Logging**: Local SQLite database (`db/aat_trading.db`) logs all signals and safety events.

---

## 📁 Repository Structure
- `MQL5/`: Expert Advisors, Include utilities, and DLL libraries.
- `Python/V3_1_0/`: Modular logic (Main, Strategy, Risk, Data, Security).
- `db/`: Persistent audit and trading logs.
- `L99_CERTIFICATION.md`: Verification manual and stress-test guide.

---

## 🏅 Certification & License
- Zero-Stub, 100% production-ready code.
- **License**: GNU GPL v3 (100% FOSS).
- **Author**: Simon Peter
