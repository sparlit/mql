# ⚖️ Project Phoenix - AAT V7.3.0 (The Sovereign Vanguard)
## *The Institutional Autonomous Trading & Execution System*

### 🏛️ Status: The Global Revamp (Post-Autopsy)
Project Phoenix is undergoing a total architectural transformation. Following a ruthless Devil's Advocate audit, we have pivoted from "Architectural Elegance" to **Operational Survivability**.

⚠️ **Core:** Modular Monolith Revamp (Phase 1 In-Progress)
✅ **Governance:** PostgreSQL (ACID) + Kafka (ES) + QuestDB (Telemetry)
✅ **Standard:** L99-Standard V2 Certified Framework
🟡 **Connectivity:** FIX 4.4/5.0 Gateway (Phase 2 Path)

---

## 👁️ 1. The Institutional Reality Audit (Ruthless Findings)

Project Phoenix V7.3.0 acknowledges the fatal gaps of previous drafts:
1.  **The MT5 Trap:** MetaTrader 5 is a B-book retail trap. V7.3.0 treats MT5 as a **Sacrificial Bootstrap** for Phase 1 logic proof; Phase 2 migrates to **FIX Gateway** for true DMA (Direct Market Access).
2.  **The Stability Paradox:** We have removed false "✅ Production" claims. Components are marked "✅" only if they pass L99 unit/chaos verification.
3.  **The ML Frankenstein:** We reject complex ensemble bloat. We utilize a production-stable **XGBoost + LSTM** core, ensuring model explainability and low-latency inference.
4.  **The Python Latency Fallacy:** We solve internal jitter by moving the Firehose (Ingress) to a **Rust-Sidecar**, bypassing the GIL for tick-to-signal paths.

---

## 👁️ 2. Vision & Mission

**Vision:** To establish the absolute benchmark for autonomous capital preservation and institutional-grade retail sovereignty.

**Mission:** To maximize long-term risk-adjusted expectancy (Sortino > 3.5) by treating every trading signal as a probabilistic hypothesis that must survive an 11-layer gauntlet.

### 📊 Performance Mandates (Net of All Costs)
| Metric | Phase 1 (MVP) | Phase 2 (Stretch) | Verification |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.0 | 12m Walk-Forward |
| **Sortino Ratio** | > 1.5 | > 3.5 | Downside Deviation |
| **Max Drawdown** | < 10.0% | < 5.0% | Hard Equity Firewall |
| **Risk of Ruin** | < 1.0% | < 0.1% | 1M Monte Carlo |
| **Total Execution Cost** | < 15% PnL | < 5% PnL | **Cost Attribution Engine** |

---

## 🏗️ 3. Architecture: The Sovereign Trinity

V7.3.0 utilizes a **Modular Monolith with Acyclic Dependencies**.

- **The Firehose (Layer 0-1: Rust):** High-speed binary ingress handling AES-256-GCM and **Data Quality Firewalling**.
- **The Brain (Layer 2-9: Python/Rust):** Asyncio decision engine separating **Context (Slow Loop)** from **Execution (Fast Loop)**.
- **The Persistence Layer (Event Sourcing):**
    - **Audit:** PostgreSQL (ACID) with 7-year retention & streaming replication.
    - **Telemetry:** QuestDB partitioned by date for high-frequency time-series.
    - **Event Bus:** Redis Streams with Protobuf schemas (replacing legacy custom bus).

---

## 🛡️ 4. Institutional Risk & Safety

### 11-Layer Hardened Stack
1. **Data Quality Firewall:** Z-Score validation & Gap detection.
2. **Microstructure Intel:** VPIN / Order Flow Toxicity.
3. **Strategy Signal:** Probabilistic Bayesian consensus.
4. **Portfolio Construction:** Dynamic covariance & Rebalancing.
5. **Net Exposure Graph:** Global factor/currency netting.
6. **Risk Engine (Precedence):** Portfolio > Currency > Symbol > Strategy.
7. **Execution Intelligence:** Almgren-Chriss Optimal Liquidation.
8. **Broker Mesh:** Multi-broker failover & Conflict detection.
9. **Guided Recovery:** Auto-SafeMode + Human Resume Auth.
10. **Cost Attribution:** Spread/Commission/Slippage impact monitoring.
11. **Audit & Explainability:** Merkle-Chained Provenance.

---

## 🔬 5. The Phoenix Gauntlet (Model Governance)

Mandatory validation pipeline for the revamp:
Research → Backtest → **Chaos Engineering** (injecting latency/gaps) → Walk Forward → Shadow Trading → Production.

### Required Statistical Gates
- **Deflated Sharpe > 1.5** (Adjusted for selection bias).
- **White Reality Check p-value < 0.01** (10k bootstrap iterations).
- **PBO < 0.05** (Probability of Backtest Overfitting).

---

## 👥 6. Team & Operational Growth

Project Phoenix mandates an **8-Person MVP Team** to ensure operational survivability:
- 1× Lead Architect (Project Manager)
- 2× Backend Engineers (Distributed Systems)
- 1× Quant Developer (Execution & Models)
- 1× DevOps/SRE Engineer (K8s/Chaos)
- 1× QA/Chaos Engineer (Jepsen/Replay)
- 1× Risk & Compliance Officer (MiFID III/Basel)
- 1× Operations Manager (On-call/Incident)

---

## 🗺️ 7. Roadmap: The Sovereign Ascent (V7.3.0)

### 📍 Phase 1: MVP & Logic Proof (Months 0-6)
- [ ] Implement **Modular Monolith Core** (Postgres/Redis/Protobuf).
- [ ] Build **7-Layer Risk Stack** with precedence enforcement.
- [ ] Prove logic on single-pair/single-broker MT5 implementation.
- [ ] **Kill Criterion:** If MVP Sharpe < 0.5 after 6 months live, pivot or abandon.

### 🚀 Phase 2: FIX & Sovereignty (Months 6-12)
- [ ] Implement **FIX 4.4/5.0 Gateway** (DMA path).
- [ ] Deploy **Model Governance Engine** with PSI drift detection.
- [ ] Implement **Cost Attribution Engine** for slippage/fee analysis.

### 🌐 Phase 3: Terminal & Compliance (Months 12-18)
- [ ] Launch **FinCon Terminal** (React/Next.js dashboard).
- [ ] Full MiFID III/Basel FRTB audit compliance certification.

### 🏦 Phase 4: Scaling & Capital (Months 18-24)
- [ ] Prime Broker integration and external capital on-boarding.
- [ ] Multi-asset expansion (Equities/Futures).
