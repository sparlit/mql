# 🛠️ Project Phoenix: The "Gods Engineer" Revamp Checklist

## 🏗️ 1. ARCHITECTURE & PERSISTENCE (THE FOUNDATION)
- [ ] **DataHub HA Implementation:**
    - [ ] Set up Raft-based consensus for Primary/Secondary DataHub.
    - [ ] Implement `sovereign_event_journal.db` for Event Sourcing.
- [ ] **Merkle-Audit Ledger:**
    - [ ] Create hashing service for decision provenance.
    - [ ] Integrate Merkle root anchoring in `sovereign_audit.db`.
- [ ] **Rust-Ingress Sidecar (Phase 1.5):**
    - [ ] Move AES decryption from Python to high-performance Rust/C++ module.
    - [ ] Implement Z-Score Outlier filtering on the firehose.

## 🛡️ 2. INSTITUTIONAL RISK (THE FIREWALL)
- [ ] **Exposure Graph Engine:**
    - [ ] Implement Vectorized Currency Risk calculation (Layer 4).
    - [ ] Create dynamic covariance tensor for portfolio scaling (Layer 5).
- [ ] **Broker Health Engine:**
    - [ ] Track Slippage Tiers and Fill Latency per symbol.
    - [ ] Implement automatic Risk-Scaling multiplier based on Broker Score.
- [ ] **Gravity Dead-Man Switch:**
    - [ ] Create heartbeat watchdog between MT5 EA and Python Core.
    - [ ] Script the "Safe Mode" emergency procedure (Tighten SL, Cancel Pendings).

## 🧠 3. INTELLIGENCE & GOVERNANCE (THE BRAIN)
- [ ] **Model Governance Engine (Layer 5.5):**
    - [ ] Implement Population Stability Index (PSI) monitoring.
    - [ ] Create "Shadow Mode" promotion path for Champion-Challenger testing.
- [ ] **Bayesian Liquidity Inference:**
    - [ ] Refactor SMC logic into probabilistic Liquidity Priors.
    - [ ] Integrate Volume Profile Convergence as a validation filter.
- [ ] **Oracle Mesh:**
    - [ ] Build consensus-based Macro Engine (Bloomberg + Investing + ForexFactory).
    - [ ] Implement "Consensus Veto" for High-Impact events.

## 📊 4. UI & TELEMETRY (THE GLASS COCKPIT)
- [ ] **FinCon Terminal (Next.js):**
    - [ ] Design real-time institutional dashboard.
    - [ ] Integrate Web-Socket telemetry for <10ms UI updates.
- [ ] **L99 Automation:**
    - [ ] Script the "Phoenix Gauntlet" validation pipeline (DSR, PBO, Monte Carlo).

## 🩺 5. CONTINUOUS MAINTENANCE
- [ ] 100% FOSS Compliance audit.
- [ ] Periodic Merkle Ledger verification.
- [ ] Stress-test "Chaos Engineering" suite (Network Split simulation).
