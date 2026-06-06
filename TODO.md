# 📝 AAT - Autonomous Autotrader Project Roadmap

## 🚀 Phase 1: Core Architecture & Security (Priority: High)
- [ ] **AES-256 Socket Encryption**: Implement encrypted communication between MQL5 and Python with Token Auth.
- [ ] **Heartbeat & Latency Monitor**: Bidirectional health checks with auto-fallback to file-based IPC.
- [ ] **Shared Memory DLL**: Implement custom C++ DLL for ultra-low latency inter-chart data sharing.
- [ ] **Resource-Aware Initialization**: Hardware benchmarking to auto-scale NLP models (FinBERT vs Lite).

## 🧠 Phase 2: The "Brain" (Python Intelligence)
- [ ] **Multi-Source Data Aggregator**:
    - [ ] Forex Factory (News) with Date-Aware Parsing.
    - [ ] FXStreet (Sentiment) + Social Media Proxy Feeds.
    - [ ] Polymarket/Kalshi (Prediction Markets) for macro-risk filtering.
    - [ ] OANDA/Dukascopy/IB Consensus Price Feed.
- [ ] **Strategy Master V2**:
    - [ ] **Consensus Engine**: Regime-Adaptive weighting (Trending vs Ranging).
    - [ ] **Scalping Module**: Order Flow Imbalance + VSA (Wyckoff/TradeGuider).
    - [ ] **News Straddle**: ATR-Adaptive pending orders with perfect trailing SL/TP.
    - [ ] **Historical Pattern Matcher**: FAISS-based multi-scale similarity search.
- [ ] **Risk Manager V2**:
    - [ ] **Correlation Engine**: Multi-symbol risk splitting.
    - [ ] **Monte Carlo Pre-Trade**: 100 on-the-fly micro-backtests (Win Rate > 60% required).
    - [ ] **Pyramid Scaling**: "House Money" logic (Layer 3 closes 25% of Layer 1).
    - [ ] **Drawdown Breach**: "Cool-Down" mode (24h pause after limit hit).

## 📊 Phase 3: The "Executor" (MQL5 & Dashboard)
- [ ] **Cyber-Pro Dashboard**: CCanvas-based high-contrast UI with real-time telemetry.
- [ ] **Interactive Config Tab**: In-chart strategy toggles and risk multipliers.
- [ ] **Dynamic Timeframe Sync**: Real-time partial bar analysis (Developing H4).
- [ ] **Universal Bridge**: Automatic detection of Hedge vs Netting accounts.

## 🛠 Phase 4: Self-Evolution & Maintenance
- [ ] **Weekend Optimizer**: Automated Saturday re-tuning of weights using SQLite trade logs.
- [ ] **Auto-Rotating Logs**: Monthly SQLite archival and weekly VACUUM.
- [ ] **Portable Environment**: Self-contained installer script for all FOSS dependencies.

---
**Status:** Architecture Hardening in Progress.
