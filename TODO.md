# 🛠️ Project Phoenix: The "Gods Engineer" Revamp Checklist (V9.0.0)

> **Status:** Critical Path Engineering
> **Mantra:** Deliver working core before perfection.

## 🏗️ EPIC 1: ARCHITECTURAL DEBT & PERFORMANCE
- [ ] **Dependency Audit:**
    - [ ] Audit all Python imports for circular dependencies; refactor to explicit contracts.
    - [ ] Profile `MQL5-Python` bridge latency; identify jitter bottlenecks.
- [ ] **Hybrid Kernel Init:**
    - [ ] Set up Rust crate for AES-256-GCM Ingress (Layer 1).
    - [ ] Implement lock-free RingBuffer for the "Fast Loop" internal bus.

## 💾 EPIC 2: EVENT SOURCING & PERSISTENCE
- [ ] **DataHub HA Implementation:**
    - [ ] Implement persistent Event Journal for all incoming ticks/signals.
    - [ ] Build Snapshotting mechanism for fast state recovery.
    - [ ] Implement the Replay Engine for historical state reconstruction.
- [ ] **DB Migration:**
    - [ ] Migrate Audit Ledger to PostgreSQL for high-concurrency governance.
    - [ ] Optimize QuestDB for high-frequency telemetry.

## 🛡️ EPIC 3: INSTITUTIONAL RISK & DATA QUALITY
- [ ] **Data Quality Firewall (Layer 0):**
    - [ ] Implement Z-Score outlier filtering and gap detection in the Rust ingress.
- [ ] **Exposure Graph (Layer 4):**
    - [ ] Build vectorized currency risk enforcement (Portfolio-wide netting).
- [ ] **Risk Stack V2 (Layer 5):**
    - [ ] Implement "Drawdown Velocity" halts and "Gravity" Dead-Man switch.

## 🧠 EPIC 4: GOVERNANCE & TOXICITY
- [ ] **Order Flow Toxicity (Layer 2):**
    - [ ] Implement VPIN (Volume-Synchronized Probability of Informed Trading).
- [ ] **Model Governance (Layer 5.5):**
    - [ ] Build PSI (Population Stability Index) drift detector.
    - [ ] Implement "Shadow Mode" promotion path for Champion-Challenger logic.

## 📊 EPIC 5: TELEMETRY & OPERATIONS
- [ ] **Monitoring Baseline:**
    - [ ] Export system health to Prometheus/Grafana (Core dashboard).
- [ ] **L99 Certification:**
    - [ ] Automate DSR (Deflated Sharpe Ratio) and PBO (Probability of Overfitting) gates.

## 🩺 CONTINUOUS MAINTENANCE
- [ ] Post-trade review rituals (Weekly performance audit).
- [ ] Chaos Engineering "Game Days" (Injecting latency/disconnects).
