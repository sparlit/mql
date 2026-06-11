# 🪐 Project Phoenix - AAT Master Blueprint
## **Version: 10.0.11**
### *The Sovereign Institutional Trading Operating System*

---

### 🏛️ Project Status & Current Phase
✅ **Production Stable Core (MVP Scope)**
✅ **Modular Monolith Architecture (Phased Implementation)**
✅ **PostgreSQL-ACID Persistence (Replacing SQLite)**
🔄 **Institutional Governance Layer Under Refinement**
🔄 **Adaptive Multi-Asset Trading Platform (FX Focus Phase 1)**
🔄 **Research Extensions Under Continuous Validation**
🟡 **Execution Path:** MT5 (Phase 1 MVP) → FIX Gateway (Phase 2 Sovereign)
🟡 **Intelligence:** XGBoost + LSTM Ensemble (Simplified)

⚠️ **CRITICAL NOTE:** V7.1.0 represents a ground-up rebuild focused on **Operational Excellence** over architectural vanity. All features must directly contribute to capital preservation or regulatory compliance.

---

## 👁️ 1. Vision & Mission
**Vision:** To democratize institutional-grade algorithmic trading through a transparent, auditable, and resilient trading platform that prioritizes capital preservation, statistical validity, and operational survivability above prediction.

**Mission:** Project Phoenix maximizes long-term risk-adjusted expectancy while maintaining strict capital preservation through institutional-grade governance, execution discipline, and adaptive market participation.

**Scope Constraint:** V7.1.0 focuses exclusively on retail FX via MT5 as the MVP execution venue. FIX 4.4/5.0 gateway is Phase 2. Multi-asset expansion is Phase 3. This constraint is non-negotiable for operational feasibility.

---

## 💎 2. Core Values & Divine Principles
- **Sovereignty:** 100% FOSS. Broker-Agnostic Execution. Sovereignty is the *ability to leave*.
- **Transparency:** No black boxes. Every decision is logged, audited, and verifiable.
- **Performance:** Sub-100ms internal latency (Python/MT5 reality). Sub-millisecond is Phase 2 (C++).
- **Resilience:** Chaos-native architecture. Graceful degradation on failure.
- **Institutional Discipline:** Capital preservation is the primary objective; profit is a secondary outcome.
- **Regulatory Compliance:** Institutional means **Regulatory-grade**. MiFID III, Basel III, and GDPR are core requirements.
- **Pragmatic Execution:** Deliver working core before perfection.
- **Simplicity Rule:** If a component doesn't directly protect capital, it doesn't exist in V1.

---

## 🏗️ 3. Architecture Overview (V7.1 Phoenix Modular Monolith)
Project Phoenix utilizes a **Modular Monolith** architecture with clean service boundaries, prioritizing operational simplicity over theoretical complexity.

### 3.1. Sovereign Ingress Layer
- **Adapters:** Split into Execution Adapters (MT5, FIX 4.4/5.0, Paper Trading) each implementing the same interface.
- **ECN Connectivity:** Integrate with institutional ECNs (EBS, Reuters, Currenex) via FIX.
- **Critique:** The MQL5 dependency is a single point of failure. MT5 brokers are B-book adversaries.
- **God's Solution:** Add **FIX 4.4/5.0 gateway** as primary execution path immediately. MT5 moves to fallback.

### 3.2. Core Engine (FastAPI)
- **Components:** Event Bus, Risk Engine (7-Layer), Position Manager, Model Gov, Execution Engine, Audit & Compliance.
- **Decision Engine:** Split into **Context Loop** (Slow/Governance) and **Execution Loop** (Fast/Signal).
- **God's Solution:** Simplify to a **Modular Monolith**. Separate **Core engine** (synchronous, deterministic) from **Analytics** (async).

---

## 🛠️ 4. Technical Specifications
- **Core Engine:** Python 3.11+ FastAPI (Synchronous core, Async analytics).
- **Inference:** ONNX Runtime for INT8 quantized models.
- **Security:** JWT RBAC + AES-256-GCM Encryption.
- **Event Bus:** Redis Streams with **Protocol Buffers (Protobuf)** for type-safe message passing and schema validation via Buf Registry.

### 4.1. The Persistence Layer
- **PostgreSQL 15+:** ACID Governance store (Replacing SQLite). Mandatory for audit compliance.
- **QuestDB:** High-frequency telemetry and time-series analytics.
- **Redis Cluster:** Hot state, session data, and SPMC messaging.
- **Event Store:** Apache Kafka or Redpanda (event sourcing backbone) with log compaction.
- **Backup:** Daily snapshots to S3 with **7-year retention**.

---

## 📈 5. Structural Market Reality & Intelligence
### 5.1. The Institutional Reality Audit (Brutal Truths)
1. **MT5 is a Retail Trap:** B-book brokers take the other side of trades. Phase 1 proves logic on MT5; Phase 2 migrates to FIX.
2. **SQLite is not for Audit:** Institutional compliance requires ACID-compliant, replicated storage. PostgreSQL is mandatory.
3. **Custom Event Buses Deadlock:** Legacy `bus.py` is deprecated. Redis Streams + Protobuf provide the backbone.
4. **The ML Frankenstein is Dead:** Removed FinBERT/FAISS/RL bloat. Simplified to **XGBoost + LSTM**.
5. **Compliance is not an Add-on:** MiFID III, Basel FRTB, and GDPR hash chains are core from Day 1.

### 5.2. Liquidity Inference Framework
* **Observed Liquidity:** Level 2 order book data.
* **Estimated Liquidity:** Derived from spread, tick frequency, volume profiles.
* **Hypothesized Liquidity:** Theoretical assumptions.
- **God's Solution:** Cross-validation via multiple broker feeds. Data lineage and Data Quality Scores.

### 5.3. Institutional Decision Framework (8-Stage Gauntlet)
1. Regime Identification -> 2. Liquidity Inference -> 3. Macro Event Assessment -> 4. Portfolio Exposure Assessment -> 5. Strategy Qualification -> 6. Risk Qualification -> 7. Execution Qualification -> 8. Position Authorization.

---

## 🧠 6. Model Governance & AI (Layer 5.5)
### 6.1. Model Governance Engine
- **Drift Detection:** PSI, Feature/Label/Regime/Prediction Drift.
- **Confidence Decay:** Dynamic scores decay after 6 months.
- **Reality Verification Engine:** Continuous prediction error measurement.

### 6.2. The Champion–Challenger Pipeline
- **Promotion:** Research → Validation → Walk Forward → Paper Trading → Shadow Trading → Challenger → Champion.
- **Transaction Costs:** Include spread, commission, slippage, and impact in ALL tests.

### 6.3. Machine Learning Architecture V2 (Simplified)
- **Primary:** XGBoost (1-hour forward return terciles).
- **Secondary:** LSTM (1-hour realized volatility forecast).
- **Online Learning:** Incremental XGBoost (`xgboost.QuantileDMatrix`).

---

## 🛡️ 7. Institutional Risk Architecture
### 7.1. Risk Precedence & Multi-Layer Stack
**Precedence (Highest to Lowest):**
1. Portfolio Risk -> 2. Currency Risk -> 3. Symbol Risk -> 4. Strategy Risk -> 5. Trade Risk -> 6. Broker Risk -> 7. Infrastructure Risk.
- **Veto Power:** Any layer may independently veto. Pre-trade Monte Carlo simulation is mandatory.
- **Latency Budget:** < 14ms total check.

### 7.2. Kill Switch Hierarchy (4-Level)
1. **Level 1 (Strategy):** Halt specific strategy on volatility/drawdown breach.
2. **Level 2 (Symbol):** Freeze symbol on extreme spread or data gap.
3. **Level 3 (Global):** Flatten all positions (Absolute Capital Firewall).
4. **Level 4 (Infrastructure):** Safe-Mode disconnect on heartbeat failure or audit corruption.

### 7.3. Exposure Graph Engine
Computes true global exposure using **delta-adjusted notional** with **volatility-adjusted exposure** and **marginal VaR**.

---

## 🛰️ 8. Reliability, Resilience & Recovery
### 8.1. DataHub High Availability Architecture
- **Infrastructure:** Primary PostgreSQL (write master) + synchronous standbys. Redis Cluster (6 nodes) with auto-failover.
- **Event Integrity:** SHA-256 hash chains with Merkle tree verification.
- **CAP Tradeoff:** CP for risk data; AP for telemetry.

### 8.2. Chaos Engineering Framework
- **Targets:** Survive 1000 chaos experiments. RTO < 5s for critical systems.
- **Failure Modes:** Disconnects, Network Splits, Data Corruption, DB Failure, Worker Crashes.

---

## 🔬 9. Research & Statistical Verification
### 9.1. Core Performance Targets (Realistic & Phased)
| Metric | Phase 1 (MVP) | Phase 2 (Stretch) | Priority |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.0 | High |
| **Sortino Ratio** | > 1.5 | > 3.0 | High |
| **Max Drawdown** | < 10.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 1.0% | < 0.1% | **ABSOLUTE** |
| **Execution Cost** | < 15% Returns | < 5% Returns | Critical |

### 9.2. Research Validation Stage Gates
Research → Backtest → Validation → Walk Forward → Incubation (3 months live) → Shadow Trading (6 months) → Production.
- **Constraint:** Minimum 500 trades for statistical claims. Temporal holdout mandatory.

---

## 👥 10. Team, Roles & Operations
**Minimum Viable Team (8 people):**
1. Lead Architect | 2x Backend/Kernel Engineers | 1x Quant Developer | 1x DevOps Engineer | 1x QA/SDET | 1x Risk & Compliance Officer | 1x Operations/Terminal Manager.

**Operational Growth Plan:** Month 0-3 (4 people), Month 3-6 (6 people), Month 6-12 (8 people), Month 12-18 (10 people).

---

## 🏅 11. Institutional Audit & Explainability
- **Format:** Structured JSON with Avro schema validation and HSM-protected ECDSA signatures.
- **Immutability:** Merkle tree hash chains; append-only WORM storage.
- **Retention:** 7 years minimum.
- **Falsifiability:** The platform is designed to be explainable, auditable, measurable, and falsifiable at every level.

---

## 🗺️ 12. Roadmap & Tiered Milestones (V7.1.0)
### 📍 Phase 1: MVP — Logic Proof (Months 0-6)
- [ ] Implement **Modular Monolith Core** on PostgreSQL/Redis.
- [ ] Deploy **XGBoost + LSTM** production ensemble.
- [ ] Build MT5 Adapter and prove logic on single-pair/single-broker.
- [ ] **Kill Criterion:** If Sharpe < 0.5 after 6 months live, pivot or abandon.

### 🚀 Phase 2: FIX & Sovereignty (Months 6-12)
- [ ] Implement **FIX Gateway** for institutional liquidity.
- [ ] Deploy Model Governance Engine and SMART routing.
- [ ] Multi-broker orchestration and conflict detection.

### 🌐 Phase 3: Terminal & Compliance (Months 12-18)
- [ ] Launch **FinCon Terminal** (React/Next.js dashboard).
- [ ] Full MiFID III/Basel audit compliance certification.

### 🏦 Phase 4: Scaling & Capital (Months 18-24)
- [ ] Prime Broker integration and external capital onboarding.
- [ ] Full regulatory licensing.

---

## 📈 13. Economics & Cost Model
**Monthly Burn:** Phase 1 ($42K-$66K) | Phase 2 ($68K-$100K) | Phase 3 ($102K-$170K).
**Breakeven Analysis:** Phase 1 requires ~$5M-7M AUM at 1% fee.

---

## 📜 Appendices
### Appendix A: Regulatory Compliance Matrix
| Regulation | Requirement | Phase |
| :--- | :--- | :--- |
| **MiFID III** | Algorithm ID, Order ratios, Kill switches | 2 |
| **Basel III** | FRTB desk def, backtesting, PLA tests | 3 |
| **GDPR** | Data retention, right to deletion | 1 |

### Appendix B: Detailed Technology Stack
FastAPI, PostgreSQL (streaming replication), Redis Streams (Protobuf), QuestDB, Kafka, ONNX, Docker/Kubernetes.

### Appendix C: Glossary
- **Modular Monolith:** Architecture with clean boundaries within a single deployment unit.
- **A-book/B-book:** Processing method vs. counterparty conflict.
- **VPIN:** Volume-synchronized Probability of Informed Trading.
