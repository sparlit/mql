# 🔥 Project Phoenix - AAT V7.0.0

## The Sovereign Institutional Trading Platform

### Status

✅ Production Stable Core

✅ Institutional Governance Layer Integrated

✅ Adaptive Multi-Asset Trading Platform

✅ Research Extensions Under Continuous Validation

---

## 👁️ 1. Vision & Mission

**Vision:** To democratize institutional-grade algorithmic trading through a transparent, auditable, and resilient trading platform that prioritizes capital preservation, statistical validity, and operational survivability above prediction.

**Mission:** Project Phoenix does not target fixed returns. Its objective is to maximize long-term risk-adjusted expectancy while maintaining strict capital preservation through institutional-grade governance, execution discipline, and adaptive market participation.

### Primary Performance Objectives

| Metric                        | Target   |
| ----------------------------- | -------- |
| Sharpe Ratio                  | > 2.0    |
| Sortino Ratio                 | > 3.0    |
| MAR Ratio                     | > 1.5    |
| Risk of Ruin                  | < 0.1%   |
| Maximum Drawdown              | < 5%     |
| Capital Preservation Priority | Absolute |

---

## 💎 2. Core Values

- **Sovereignty:** 100% FOSS. Your data, your keys, your execution.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Performance:** Sub-millisecond internal event latency, optimized for consumer-to-pro hardware.
- **Resilience:** Defensive architecture designed to survive market volatility and network instability.
- **Institutional Discipline:** Capital preservation is the primary objective; profit is a secondary outcome of discipline.

---

## 🏗️ 3. Architecture (V7.0 Phoenix Microkernel)

Project Phoenix utilizes a multi-layer **Event-Driven Asynchronous Microkernel** with a focus on High Availability and state persistence.

### 🧩 System Overview
- **Sovereign Ingress:** AES-256-CBC Secure Gateway for all MQL5 traffic.
- **DataHub HA Architecture:** Manages Primary/Secondary state, Event Journaling, and Replay Queues to ensure zero data loss.
- **Centralized Event Bus:** `src/shared/utils/bus.py` handles zero-coupling distribution.
- **Model Governance Engine:** Supervisors all predictive systems and monitors for drift.
- **Execution Analytics Engine:** Monitors fill rates, slippage, and broker health.

### 🛠️ Technical Specifications
- **Core Engine:** Python 3.11+ FastAPI Orchestrator.
- **Security:** JWT RBAC + AES-256-CBC Encryption.
- **Persistence:** SQLite (Audit) + QuestDB (High-frequency telemetry) + Event Journal.
- **Inference:** ONNX Runtime for INT8 quantized XGBoost and Transformer models.

---

## 📈 4. Structural Market Reality & Intelligence

### Liquidity Inference Framework
Project Phoenix recognizes that liquidity cannot be directly observed in decentralized retail FX markets. We operate on **Liquidity Inference** rather than prediction.

Liquidity models are classified as:
* **Observed Liquidity**
* **Estimated Liquidity**
* **Hypothesized Liquidity**

Market movement results from Liquidity Seeking, Macro Events, Dealer Hedging, Options Flow, Central Bank Activity, Systematic Fund Rebalancing, or Volatility Regime Shifts. No single explanatory framework is assumed.

### Institutional Decision Framework
Every trade must pass an 8-stage constrained decision process:
1. Market Regime Identification
2. Liquidity Inference
3. Macro Event Assessment
4. Portfolio Exposure Assessment
5. Strategy Qualification
6. Risk Qualification
7. Execution Qualification
8. Position Authorization

**Failure at any stage immediately vetoes execution.**

### Market Regime Engine V2
Market states are no longer limited to four categories. Supported states:
- Trend Low/High Volatility
- Range Low/High Volatility
- Compression
- Expansion
- Crisis
- Event Driven
- Transition Regime
- Unknown State (Defaults to reduced risk or no trade)

---

## 🧠 5. Model Governance & AI (Layer 5.5)

### Model Governance Engine
Supervises all predictive systems with:
* **Drift Detection:** Monitors PSI, Feature/Label Drift, Regime Drift, and Prediction Drift. Models exceeding thresholds enter Shadow Mode.
* **Confidence Decay:** Dynamic scores that decay with model age. Models without retraining gradually lose influence.
* **Champion–Challenger Framework:** Promotion path: Research → Validation → Walk Forward → Shadow Trading → Challenger → Champion.
* **Reality Verification Engine:** Continuous measurement of prediction error (Win Prob, R/R, Duration, Drawdown). Persistent degradation reduces model authority.

### Macro Intelligence Layer
Dedicated Macro Event Engine monitoring: CPI, NFP, FOMC, ECB/BOE Decisions, GDP, PMI, and Major Geopolitical Events.
**Behavior during High Impact Events:** Reduce Risk, Restrict Entries, Increase Spread Protection, and Resume only after stabilization.

### Machine Learning Architecture V2
- **FinBERT:** Sentiment Classification & Freshness Weighting.
- **FAISS:** Historical Signature Retrieval.
- **Offline XGBoost:** Nightly Retraining & Walk Forward Validation.
- **Online Learning:** Adaptive Random Forest & Hoeffding Tree Models.

### Reinforcement Learning Policy
RL systems may not directly control capital. Approved workflow:
RL Recommendation → Risk Engine Validation → Position Authorization → Execution.

---

## 🛡️ 6. Institutional Risk Architecture V2

### Multi-Layer Risk Stack
- Layer 1: Trade Risk
- Layer 2: Strategy Risk
- Layer 3: Symbol Risk
- Layer 4: Currency Risk
- Layer 5: Portfolio Risk
- Layer 6: Broker Risk
- Layer 7: Infrastructure Risk

Any layer may independently halt trading.

### Exposure Graph Engine
Computes true global exposure. Example: EURUSD Long + GBPUSD Long + AUDUSD Long is recognized as concentrated USD Short Exposure. Currency exposure limits are enforced globally (USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD).

### Execution & Broker Health
- **Execution Analytics:** Monitors Fill Rate, Slippage, Spread Conditions, Latency, and Reject Rate.
- **Broker Health Engine:** Continuous Broker Health Score based on Spread, Slippage, Rejections, and Stability. Risk scales automatically based on broker quality.

### Kill Switch Hierarchy
- Level 1: Strategy Halt
- Level 2: Symbol Halt
- Level 3: Portfolio Freeze
- Level 4: Broker Isolation
- Level 5: Emergency Liquidation
- Level 6: Safe Mode
- Level 7: Human Authorization Required

---

## 🛰️ 7. Reliability & Resilience

### DataHub High Availability Architecture
Evolution from single DataHub to:
**Primary DataHub + Secondary DataHub + Event Journal + Replay Queue.**
Event sourcing architecture guarantees reconstruction after failure. All events are recoverable.

### Chaos Engineering Framework
Continuous resilience testing for: MT5 Disconnect, Network Split, Tick Delay, Data Corruption, Database Failure, Worker Crash, and Clock Drift. The platform must survive all tests without capital loss.

---

## 🔬 8. Research & Verification

### Research Validation Laboratory
Mandatory validation pipeline:
Research → Backtest → Validation → Walk Forward → Paper Trading → Shadow Trading → Production. No strategy bypasses this process.

### Statistical Verification
Required Metrics:
- Deflated Sharpe Ratio
- White Reality Check
- Probability of Backtest Overfitting (PBO)
- CSCV Validation
- Monte Carlo Simulation (100,000+ Runs)
- CVaR & Risk of Ruin Analysis

### L99 Certification Framework V2
- L99-A: Code Integrity
- L99-B: Infrastructure Reliability
- L99-C: Risk Management
- L99-D: Execution Quality
- L99-E: Research Validation
- L99-F: Resilience & Recovery
All certifications must pass independently.

---

## 👥 9. Team & Roles

- **Architect:** Lead Designer of the Microkernel and Event-Driven logic.
- **Quant Engineer:** Developer of Liquidity Inference logic and AI model training/quantization.
- **Security Specialist:** Oversight of AES encryption, RBAC, and Audit integrity.
- **UI/UX Designer:** Crafting the "FinCon Terminal" (Bloomberg-class Glass Cockpit) experience.

---

## 🏅 Institutional Audit Trail
Every trade records full decision provenance (Why Trade? Why Now? Why Size? Why Confidence? Why Regime? Why Exposure?). The platform is designed to be explainable, auditable, measurable, and falsifiable at every level.

---

## 🗺️ 10. Roadmap: The Sovereign Ascent (V7.0)

### 📍 Phase 1: Institutional Core & Governance (Current)
- [ ] Implement **Model Governance Engine (Layer 5.5)** for drift detection and confidence decay.
- [ ] Finalize **DataHub HA Architecture** with Event Journaling and Replay Queues.
- [ ] Integrate **Exposure Graph Engine** for global currency risk enforcement.
- [ ] Resolve EventBus circular dependencies and standardize AES response handling.

### 🚀 Phase 2: Advanced Liquidity & Intelligence
- [ ] Deploy **Execution Analytics & Broker Health Engines**.
- [ ] Integrate **Macro Intelligence Layer** (Automatic risk reduction during CPI/FOMC).
- [ ] Implement **Wyckoff Phase Detection** and Similarity Search (FAISS) for regime alignment.
- [ ] Standardize local model quantization (ONNX) for all XGBoost ensembles.

### 🌐 Phase 3: The FinCon Terminal & Scale
- [ ] Launch **"FinCon Terminal"**: A Bloomberg-class React/Next.js dashboard for institutional monitoring.
- [ ] Implement **Chaos Engineering Framework** for continuous resilience testing.
- [ ] Deploy **Multi-Broker Hub synchronization** for concurrent terminal management.
- [ ] Finalize **L99 Certification Framework V2** automation.
