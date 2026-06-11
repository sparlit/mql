# 🔥 Project Phoenix - AAT V7.1.0 (The Hybrid Revamp)

## The Sovereign Institutional Trading Platform

### Status

✅ Production Core Refactoring (Hybrid Kernel Init)
✅ Governance Layer V2 (Pre-Computed Context)
✅ Universal Broker Abstraction Layer
✅ Order Flow Toxicity Engine Integration

---

## 👁️ 1. Vision & Mission

**Vision:** To architect the world's first **Hybrid High-Frequency Retail Platform**, combining the ease of Python for quantitative research with the raw speed of Rust for execution. We aim to bridge the gap between institutional microstructure analysis and sovereign retail capital deployment.

**Mission:** To maximize risk-adjusted expectancy through **Deterministic Latency** and **Adverse Selection Protection**. We do not predict the future; we react to the present with institutional speed and mathematical discipline.

### Primary Performance Objectives (Dynamic)

| Metric                        | Condition                  | Target   |
| ----------------------------- | -------------------------- | -------- |
| Sharpe Ratio                  | Low Volatility Regime      | > 2.5    |
| Sharpe Ratio                  | High Volatility/Crisis     | > 1.5    |
| Sortino Ratio                 | Global                     | > 3.0    |
| MAR Ratio                     | Global                     | > 2.0    |
| Risk of Ruin                  | Annualized                 | < 0.5%   |
| Max Drawdown                  | Defensive Mode             | < 5%      |
| Max Drawdown                  | Offensive Mode             | < 12%     |
| Execution Latency (Internal)  | Tick-to-Order              | < 100µs   |
| Capital Preservation Priority | Absolute                   | Primary   |

---

## 💎 2. Core Values

- **Sovereignty:** Broker-Agnostic Execution. Your logic, your capital, your choice of counterparty.
- **Determinism:** No Garbage Collection pauses. No blocking I/O. Predictable execution paths.
- **Transparency:** Provenance logging for every nanosecond of decision making.
- **Resilience:** Chaos-native architecture. If a component fails, the system degrades gracefully, it does not crash.
- **Institutional Discipline:** We lose small and win big. We refuse to trade in toxic liquidity conditions.

---

## 🏗️ 3. Architecture (V7.1 Phoenix Hybrid Kernel)

Project Phoenix moves from pure Python to a **Rust-Python Polyglot Microkernel** designed for extreme performance and safety.

### 🧩 System Overview
- **Sovereign Ingress (Rust):** High-speed TCP/TLS Gateway. Handles encryption (AES-256-GCM) and protocol parsing.
- **The Event Bus (Rust):** A lock-free, single-producer multi-consumer (SPMC) ring buffer. Zero-allocation message passing.
- **The Compute Engine (Python):** Asyncio workers for AI inference, Strategy logic, and Portfolio management. Communicates with Rust via shared memory/ZeroMQ.
- **The Persistence Layer (Async):**
    - **Hot Cache:** Redis for immediate state and session data.
    - **Cold Storage:** QuestDB (Time-Series) + PostgreSQL (Relational Audit) replacing SQLite for concurrency.
- **Execution Layer (Rust):** Direct interface to the Universal Broker Adapter (MT5/cTrader/FIX).

### 🛠️ Technical Specifications
- **Core Kernel:** Rust 1.70+ (Tokio Async Runtime).
- **Logic Layer:** Python 3.11+ (PyO3 Bindings).
- **Security:** AES-256-GCM + SHA-384 HMAC. P-521 Curve for Internal Key Exchange.
- **Inference:** ONNX Runtime (C++ bindings) for zero-copy inference.
- **Protocol:** gRPC/Protobuf for internal service communication.

---

## 📈 4. Structural Market Reality & Intelligence

### Order Flow Toxicity Framework
We reject the idea of "Liquidity Prediction" in retail markets. Instead, we operate on **Toxicity Detection**.
* **VPIN (Volume-Synchronized Probability of Informed Trading):** Measures the probability of flow being informed (toxic).
* **Imbalance Ratio:** Real-time bid/ask volume divergence.
* **Microstructure Jitter:** Detection of broker-side quote stuffing or latency arbitrage.

**Rule:** If Toxicity Score > Threshold -> Instantaneously flat (close positions) and disable new entries.

### Institutional Decision Framework (V2 Optimized)
We split the decision engine into **Slow Context (Pre-Computed)** and **Fast Execution (Reactive)**.

**Slow Loop (1-sec Interval):**
1. Market Regime Identification (HMM Markov Chains)
2. Macro Event Assessment (Economic Calendar integration)
3. Portfolio Exposure Assessment (Graph Engine)
4. Strategy Qualification (Model Confidence)
*Output:** A "Trading Permission Ticket" valid for (N) seconds.

**Fast Loop (Tick-Driven, Sub-100µs):**
1. **Liquidity/Toxicity Check** (Real-time)
2. **Risk Check** (Dynamic Limits)
3. **Execution Authorization** (Sign Ticket)
4. **Order Dispatch**

### Market Regime Engine V3
Uses Hidden Markov Models (HMM) to determine:
- Volatility State (Low/Med/High)
- Trend State (Trend/Range/Reversal)
- Liquidity State (Toxic/Clean)

---

## 🧠 5. Model Governance & AI (Layer 5.5)

### Model Governance Engine
- **Drift Detection:** Population Stability Index (PSI) calculated on live features.
- **Shadow Mode:** New models run in parallel to production (taking no trades) to track live performance.
- **Circuit Breakers:** If a model predicts "Long" but price drops > 0.2% within 10s, the model is instantaneously disabled for 24 hours.

### Machine Learning Architecture V3
- **XGBoost/LightGBM:** Trained offline in Python, exported to ONNX, executed in Rust.
- **Online Learning:** River (Python library) for Hoeffding Adaptive Trees running directly on the tick stream for feature extraction.

---

## 🛡️ 6. Institutional Risk Architecture V3

### Multi-Layer Risk Stack (Reactive)
- Layer 1: **Execution Risk** (Latency check - if order takes > 200ms, abort).
- Layer 2: **Symbol Risk** (Volatility shrink/expansion).
- Layer 3: **Currency Correlation** (Net exposure calc).
- Layer 4: **Drawdown Velocity** (If DD drops from 2% to 4% in 1 min -> Global Halt).

### Kill Switch Hierarchy (Automated)
- Level 1: Model/Strategy Halt (Soft)
- Level 2: Broker Isolation (Disconnect from one broker, keep others active)
- Level 3: Global Liquidation (Close all, Flatten)
- Level 4: Core Dump & Halt (System instability detected)

---

## 🛰️ 7. Reliability & Resilience

### DataHub High Availability Architecture
**Hot-Standby Redundancy.**
- Primary instance writes to Redis Stream.
- Secondary instance reads from Redis Stream.
- If Primary heartbeat fails > 5s, Secondary takes over IP address (Virtual IP) and mounts the state.

### Chaos Engineering Framework
Automated "Game Days" in Paper Trading:
- Randomly kill the Python process (Rust maintains order safety).
- Inject 500ms network delay.
- Corrupt feed data (Negative prices, Spikes).

---

## 🔬 8. Research & Verification

### L99 Certification Framework V3
- **L99-A (Code):** Must pass `clippy` (Rust linter) and `ruff` (Python linter) with zero warnings.
- **L99-B (Latency):** P99 Latency < 200µs.
- **L99-C (Reality):** Walk-forward analysis must show > 0.05 expectancy per trade.

---

## 🗺️ 10. Roadmap: The Sovereign Ascent (V7.1)

### 📍 Phase 1: The Hybrid Kernel (Current)
- [ ] **Port Event Bus to Rust:** Implement lock-free ring buffer.
- [ ] **Create PyO3 Bindings:** Bridge Python Strategy Logic to Rust Bus.
- [ ] **Universal Broker Interface:** Abstract MT5 commands to generic traits.
- [ ] **Migrate Encryption:** Upgrade to AES-256-GCM in Rust.

### 🚀 Phase 2: Toxicity & Speed
- [ ] **Implement VPIN/Toxicity Engine:** Real-time adverse selection detection.
- [ ] **Slow/Fast Loop Separation:** Refactor decision engine for dual-path execution.
- [ ] **Redis Integration:** Replace SQLite with Redis/Postgres combo.

### 🌐 Phase 3: The FinCon Terminal & Scale
- [ ] Launch **"FinCon Terminal"**: React/Next.js dashboard connecting via WebSockets to Rust Core.
- [ ] **Multi-Broker Deployment:** Run concurrent instances on different brokers simultaneously.
