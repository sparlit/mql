# ⚖️ Project Phoenix - AAT V7.1.0 (The Rebuilt Sovereign)
## *The Institutional Trading Platform Re-Make*

### 🏛️ Status: The V7.1.0 Pivot
The project has undergone a "Ruthless Autopsy" and is being rebuilt as a **Modular Monolith** with clean boundaries. We have discarded architectural vanity in favor of **Operational Excellence**.

✅ **Core Integrity:** Modular Monolith Architecture (Phased Implementation)
✅ **Governance:** PostgreSQL-ACID Persistence (Replacing SQLite)
🟡 **Execution:** MT5 (Phase 1 MVP) → FIX Gateway (Phase 2 Sovereign)
🟡 **Intelligence:** XGBoost + LSTM Ensemble (Simplified)

---

## 👁️ 1. The Institutional Reality Audit

Project Phoenix V7.1.0 is built on the ruins of over-ambitious drafts. We acknowledge these brutal truths:

1.  **MT5 is a Retail Trap:** B-book brokers conflict with client success. Phase 1 proves logic on MT5; Phase 2 migrates to **FIX Gateway** for true institutional liquidity.
2.  **SQLite is not for Audit:** Institutional compliance requires ACID-compliant, replicated storage. **PostgreSQL** is now the mandatory governance store.
3.  **Custom Event Buses Deadlock:** The legacy `bus.py` is deprecated. **Redis Streams** with consumer groups and **Protobuf** schemas provide the production backbone.
4.  **The ML Frankenstein is Dead:** Removed FinBERT/FAISS/RL bloat. Simplified to **XGBoost + LSTM** for production stability.
5.  **Compliance is not an Add-on:** MiFID III, Basel FRTB, and GDPR audit trails are built into the core hashing chains from Day 1.

---

## 👁️ 2. Vision & Mission

**Vision:** To democratize institutional-grade trading through a transparent, auditable, and resilient platform that prioritizes capital preservation above all else.

**Mission:** Project Phoenix maximizes long-term risk-adjusted expectancy while maintaining strict capital preservation through disciplined governance and execution.

### 📊 Performance Targets (Realistic & Phased)
| Metric | Phase 1 (MVP) | Phase 2 (Stretch) | Priority |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.0 | High |
| **Sortino Ratio** | > 1.5 | > 3.0 | High |
| **Max Drawdown** | < 10.0% | < 5.0% | **ABSOLUTE** |
| **Risk of Ruin** | < 1.0% | < 0.1% | **ABSOLUTE** |
| **Execution Cost** | < 15% Returns | < 5% Returns | Critical |

---

## 🏗️ 3. Architecture: The Rebuilt Microkernel

The V7.1.0 revamp moves from an over-engineered microkernel to a **Modular Monolith with Clean Boundaries**.

### 🧩 System Overview
- **Sovereign Ingress:** AES-256-GCM Secure Gateway with FIX protocol priority in Phase 2.
- **Persistence Layer:** PostgreSQL (ACID Governance) + QuestDB (High-frequency telemetry) + Redis Cluster (Hot State).
- **Event Bus:** Redis Streams with **Protocol Buffers (Protobuf)** for type-safe message passing and schema validation via Buf Registry.
- **Decision Engine:** Split into **Context Loop** (Slow/Governance) and **Execution Loop** (Fast/Signal).

---

## 🛡️ 4. Institutional Risk & Kill Switches

### 7-Layer Risk Stack (Explicit Precedence)
Precedence: **Portfolio > Currency > Symbol > Strategy > Trade > Broker > Infrastructure.**
Any layer may independently veto. Pre-trade Monte Carlo simulation is mandatory.

### 4-Level Kill Switch Hierarchy
1.  **Level 1 (Strategy):** Halt specific strategy on volatility/drawdown breach.
2.  **Level 2 (Symbol):** Freeze symbol on extreme spread or data gap.
3.  **Level 3 (Global):** Flatten all positions and disable entry.
4.  **Level 4 (Infrastructure):** Safe-Mode disconnect on heartbeat failure or audit corruption.

---

## 👥 5. Team & Operational Growth

A 4-person team is insufficient for an institutional build. Phoenix mandates an **8-Person MVP Team**:
- 1× Lead Architect
- 2× Backend/Kernel Engineers
- 1× Quant Developer (XGB/LSTM)
- 1× DevOps Engineer (K8s/HA/CI)
- 1× QA/SDET (Chaos/Replay)
- 1× Risk & Compliance Officer
- 1× Operations/Terminal Manager

---

## 🗺️ 6. Roadmap: The Sovereign Ascent (V7.1.0)

### 📍 Phase 1: MVP & Logic Proof (Months 0-6)
- [ ] Implement **Modular Monolith Core** on PostgreSQL/Redis.
- [ ] Deploy **XGBoost + LSTM** production ensemble.
- [ ] Prove logic on single-pair/single-broker MT5 implementation.
- [ ] **Kill Criterion:** If Sharpe < 0.5 after 6 months live, pivot or abandon.

### 🚀 Phase 2: FIX & Sovereignty (Months 6-12)
- [ ] Implement **FIX Gateway** for institutional liquidity.
- [ ] Deploy **Model Governance Engine** with drift detection.
- [ ] Multi-broker orchestration and conflict detection.

### 🌐 Phase 3: Terminal & Compliance (Months 12-18)
- [ ] Launch **FinCon Terminal** (React/Next.js dashboard).
- [ ] Full MiFID III/Basel audit compliance certification.

### 🏦 Phase 4: Scaling & Capital (Months 18-24)
- [ ] Prime Broker integration and external capital on-boarding.
- [ ] Full regulatory licensing.

---
*The platform is designed to be explainable, auditable, measurable, and falsifiable at every level.*
