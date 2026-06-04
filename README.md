# Autonomous MT5 Autotrader (100% FOSS)

A fully autonomous, zero-stub, "set and forget" trading system for MetaTrader 5, powered by a multi-strategy Python analysis engine.

## 🏗 Architecture
- **MetaTrader 5 (MQL5):** Handles real-time visualization (Dashboard), order execution, and trailing stop/take-profit management.
- **Python Engine:** Performs heavy lifting, including data ingestion from multiple sources (Yahoo Finance, etc.), multi-timeframe analysis, and strategy consensus verification.
- **Communication:** Real-time bi-directional bridge using standard TCP Sockets (WinAPI) for low-latency data exchange.

## 🚀 Features
- **Zero Stubs:** Every component is 100% functional and production-ready.
- **Multi-Strategy Consensus:** Integrates Trend Following, Mean Reversion, Breakout, and Scalping.
- **Advanced Risk Management:** Dynamic lot sizing based on account equity and ATR-based market regime detection.
- **Real-time Dashboard:** Multi-column/row grid inside the MT5 terminal showing trend, signal confidence, and engine status.
- **Autonomous Scalping:** Built-in high-frequency logic for capture of small price movements.
- **Double Verification:** Trades only commence when multiple strategies reach a high-confidence consensus.

## 📋 Pre-Requirements
1. **MetaTrader 5 Terminal:** Installed and logged into a broker account.
2. **Python 3.10+:** Installed on the same machine (or accessible via network).
3. **Dependencies:**
   - `pip install pandas numpy yfinance scipy statsmodels scikit-learn`
4. **MT5 Permissions:**
   - Enable **"Allow DLL imports"** in MT5 (Tools > Options > Expert Advisors). This is required for the WinAPI Socket bridge.

## 🛠 Installation

### 1. Python Engine Setup
1. Navigate to the `Python/` directory.
2. Install requirements: `pip install -r requirements.txt`.
3. Start the engine: `python main_engine.py`.
   - The engine will listen on `127.0.0.1:5555` for signals from MT5.

### 2. MQL5 Expert Advisor Setup
1. Open your MT5 Data Folder (File > Open Data Folder).
2. Copy the contents of the `MQL5/` directory into your terminal's `MQL5/` folder:
   - `MQL5/Experts/AutonomousTrader.mq5` -> `MQL5/Experts/`
   - `MQL5/Include/*.mqh` -> `MQL5/Include/`
3. Restart MT5 or refresh the Navigator panel.
4. Compile `AutonomousTrader.mq5` in MetaEditor.
5. Drag the `AutonomousTrader` EA onto any chart.

## ⚙️ Configuration
The EA provides several inputs in the configuration window:
- **Risk Percent:** Percentage of account balance to risk per trade.
- **Magic Number:** Unique ID for the EA's trades.
- **Stop Loss / Take Profit:** Initial points for risk management.
- **Trailing SL/TP:** Toggle for autonomous trailing logic.

## 🔄 Workflow (Set and Forget)
1. Ensure the Python `main_engine.py` is running.
2. Attach the EA to your desired symbols and timeframes.
3. The EA will poll the Python engine every 60 seconds for a fresh "Master Conclusion".
4. If a "Verified" consensus is reached, the trade is executed automatically with calculated lot sizes.
5. The EA manages the trade until exit via Trailing Stop or Take Profit.

## 🛡 Post-Requirements & Maintenance
- **Stability:** Monitor the `Engine Status` on the dashboard. `TRADE VERIFIED` indicates active autonomous operation.
- **Updates:** If you add new strategies to `strategy_master.py`, the engine will automatically include them in the consensus calculation on the next tick.
- **Logs:** Check the MT5 "Experts" tab and the Python console for detailed execution logs.

## ⚖️ License
100% Free and Open Source Software (FOSS).
