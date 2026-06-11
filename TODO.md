# 🛠️ Project Phoenix: Engineering TODO (V7.1 Revamp)

> **Status:** Critical Path Engineering
> **Focus:** Hybrid Kernel Implementation & Rust Integration

## 🎯 Quarter 1: The Kernel Rewrite (Foundational)

### 1.1. Rust Environment Setup
- [ ] Initialize Rust project workspace (`phoenix-core`, `phoenix-bridge`).
- [ ] Set up `Cargo.toml` with dependencies: `tokio`, `pyo3`, `ring` (crypto), `crossbeam` (channels).
- [ ] Configure `maturin` for Python-Rust binding compilation.

### 1.2. Lock-Free Event Bus (Rust)
- [ ] Design and implement `RingBuffer` struct in Rust.
- [ ] Implement `EventPublisher` and `EventSubscriber` traits.
- [ ] **Constraint:** Ensure zero memory allocation in the publish path.
- [ ] Write unit tests for buffer overrun protection.

### 1.3. Security Layer Upgrade
- [ ] Deprecate AES-256-CBC implementation.
- [ ] Implement AES-256-GCM encryption module in Rust.
- [ ] Create `SecureGateway` struct to handle incoming TCP connections.
- [ ] Add HMAC-SHA384 signature verification for all internal messages.

### 1.4. Python-Rust Bridge (PyO3)
- [ ] Create Python module `phoenix_bridge`.
- [ ] Expose `bus.publish(event_bytes)` and `bus.subscribe(callback)` to Python.
- [ ] Implement `from_python` / `to_python` data serialization (using Cap'n Proto or MsgPack, avoid JSON).

---

## ⚙️ Quarter 2: The Abstraction & Persistence

### 2.1. Universal Broker Interface
- [ ] Define Rust Trait `BrokerAdapter` (methods: `connect`, `subscribe_ticks`, `place_order`, `close_position`).
- [ ] Implement `MT5Adapter` wrapping existing MT5 calls (via inter-process or DLL calls).
- [ ] Mock Broker Adapter for Chaos Testing (Simulates latency, drops, re-quotes).

### 2.2. Database Migration Strategy
- [ ] Set up PostgreSQL cluster for Audit/Relational data.
- [ ] Set up Redis Cluster for Hot State/Caching.
- [ ] Write DB Abstraction Layer in Rust to talk to Redis/Postgres asynchronously.
- [ ] Migrate existing SQLite schema to PostgreSQL.
- [ ] **Task:** Remove SQLite dependency from production build.

### 2.3. The "Slow Loop" Context Engine
- [ ] Create Python Asyncio worker `ContextManager`.
- [ ] Implement Regime Detection logic (HMM) inside `ContextManager`.
- [ ] Logic: `ContextManager` calculates "Trading Ticket" and pushes to Rust Bus.

---

## 🚀 Quarter 3: The "Fast Loop" & Toxicity

### 3.1. Order Flow Toxicity (Rust)
- [ ] Implement rolling window calculations in Rust for:
    - [ ] VPIN (Volume-Synchronized PIN)
    - [ ] Imbalance Ratio
- [ ] Logic: If `Toxicity > LIMIT`, send `POISON_PILL` event to Rust Bus (triggers immediate exit).

### 3.2. Execution Engine (Rust)
- [ ] Implement `ExecutionEngine` in Rust listening to the Bus.
- [ ] Logic: Consumes `Signal` events, checks `Toxicity`, checks `Risk`, calls `BrokerAdapter`.
- [ ] Implement `Atomic` counters for Position sizing (Thread-safe).

### 3.3. ONNX Runtime Integration
- [ ] Embed ONNX Runtime C-API in Rust.
- [ ] Create model loader: Load `.onnx` files (XGBoost/Transformers) into Rust memory.
- [ ] Implement inference function taking `f32` array (features) -> returning prediction.

---

## 🛡️ Quarter 4: Resilience & UI

### 4.1. Chaos Engineering Framework
- [ ] Build `ChaosMonkey` service.
- [ ] Implement scenarios: `RandomKill`, `LatencySpike`, `BitFlip`.
- [ ] Integrate into CI/CD pipeline (Must pass Chaos Test to merge).

### 4.2. FinCon Terminal V2
- [ ] Set up Next.js project structure.
- [ ] Implement WebSocket connection to Rust Gateway (via Tungstenite).
- [ ] Design "Glass Cockpit" Dashboard:
    - [ ] Real-time PnL gauge.
    - [ ] Toxicity Meter.
    - [ ] Regime Indicator.
    - [ ] Live Order Flow depth chart.

### 4.3. L99 Certification Automation
- [ ] Write Python scripts for automatic CSCV/Deflated Sharpe calculation on commits.
- [ ] Dockerize the entire stack (Rust Core + Python Workers + DBs) for one-click deployment.

---

## 📝 Engineering Debt & Cleanup

- [ ] Refactor all legacy `src/shared/utils/bus.py` code (mark as deprecated).
- [ ] Remove all `print()` statements, replace with `tracing` crate (Rust) and `structlog` (Python).
- [ ] Standardize Error Handling: Use `anyhow` (Rust) and custom exceptions (Python).
