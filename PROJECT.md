# ♾️ Project Phoenix - AAT V9.1.0 (The Hardened Sovereign)
## *The Institutional Autonomous Microkernel & Persistence Layer*

### 🏛️ Status: The Hardened Revamp
We have moved beyond "Pragmatic Revamp" into **Hardened Sovereignty**. The architecture now enforces deterministic communication and consistent state management.

✅ **Layer 0:** Data Quality Firewall (Active)
✅ **Layer 9:** Merkle-Chained Audit Ledger (Active)
🟡 **Core Migration:** Zero-Copy Shared Memory & FIX-Native Ingress (V9.1.0 Path)

---

## 👁️ 1. Vision & Mission

**Vision:** To establish the definitive sovereign platform for institutional-grade capital deployment. Project Phoenix prioritizes **Deterministic Execution**, **Strong Consistency**, and **Operational Survivability**.

**Mission:** To maximize risk-adjusted expectancy through a **FIX-Native Architecture**. We treat every signal as a probabilistic hypothesis that must pass a zero-copy, low-latency risk gauntlet.

### 📊 Performance Mandates (Hardened)
| Metric | Reality Target | Hard Limit | Verification |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | > 1.0 | > 2.5 | 12m Walk-Forward |
| **Jitter (P99)** | < 50µs | < 200µs | Shared Memory Profile |
| **Max Drawdown** | < 10.0% | < 5.0% | Hard Equity Firewall |
| **Internal Latency** | < 100µs | < 500µs | Tick-to-Auth |
| **Consistency** | Strong | Absolute | Command-Path Risk |

---

## 📐 2. The Hardened Governance Principles

### A. The Simplicity Budget
Subsystems that increase latency or failure surface without measurable alpha/risk benefit are rejected.

### B. The Command-Path Risk Mandate
Risk checks are never "Eventually Consistent." The Risk Engine sits in the **Synchronous Command Path** of the decision engine. No order can be signed without a real-time, strongly consistent risk approval.

### C. The FIX-Native Priority
Sovereignty is defined by protocol independence. FIX (Financial Information eXchange) is our primary protocol. All broker-specific adapters (MT5, cTrader) are treated as secondary legacy gateways.

---

## 🏗️ 3. Architecture: The Hardened Trinity

V9.1.0 utilizes a **Shared-Memory Polyglot Microkernel**.

- **The Firehose (Rust):** High-speed ingress sidecar using **Zero-Copy Shared Memory** (via Apache Arrow/RingBuffer) to hand off validated ticks to the brain.
- **The Brain (Python/Rust):** A hybrid logic layer. Time-critical risk calculations are migrated to Rust, while strategy logic remains in Python for rapid research iteration.
- **The Persistence Layer (CQRS+ES):**
    - **Command Side:** Strongly consistent state for Risk & Positions.
    - **Read Side:** Eventually consistent state for Analytics, Telemetry, and the FinCon Terminal.
    - **Audit:** Merkle-Chained Event Sourcing in PostgreSQL.

---

## 🛡️ 4. The 10-Layer Hardened Stack

1. **Layer 0: Data Quality Firewall** (Outlier filtering, gap detection).
2. **Layer 1: Market Data Layer** (FIX-Native / Rust Shared Memory).
3. **Layer 2: Liquidity/Toxicity Intelligence** (VPIN / Adverse Selection).
4. **Layer 3: Strategy Layer** (Probabilistic Bayesian Consensus).
5. **Layer 4: Portfolio Construction** (Dynamic Allocation & Netting).
6. **Layer 5: Synchronous Risk Engine** (Strongly Consistent Firewall).
7. **Layer 5.5: Model Governance** (PSI & Drift Detection).
8. **Layer 6: Execution Intelligence** (Smart Order Routing & Jitter Monitor).
9. **Layer 7: Universal Broker Mesh** (FIX Priority with MT5/cTrader fallbacks).
10. **Layer 8: Guided Recovery** (Auto-SafeMode + Human Resume Auth).
11. **Layer 9: Audit & Explainability** (Merkle-Chained Provenance).

---

## 🔬 5. The Phoenix Gauntlet

Mandatory validation includes **Latency Stress Testing** and **Consistency Audits**.
- **L99-A:** Unit Coverage & Code Integrity.
- **L99-B:** HA Replay & Event Consistency.
- **L99-D:** Deterministic Latency Profiling.

---

## 🗺️ 6. Roadmap: The Sovereign Ascent (V9.1.0)

### 📍 Phase 1: The Core Hardening (Current)
- [ ] Implement **Zero-Copy Shared Memory** for Rust-Python communication.
- [ ] Refactor Risk Engine into the **Synchronous Command Path**.
- [ ] Implement **FIX-Native Ingress** prototype.

### 🚀 Phase 2: Intelligence & Mesh
- [ ] Deploy **VPIN Toxicity Engine** (Layer 2).
- [ ] Implement **Guided Recovery Workflow** (Layer 8).
- [ ] Standardize **Merkle-Anchored Event Sourcing**.

### 🌐 Phase 3: The FinCon Terminal
- [ ] Launch **Unified Telemetry Dashboard**.
- [ ] Finalize **Universal Broker Mesh** (MT5/cTrader fallbacks).
