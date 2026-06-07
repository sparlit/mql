# 🌌 Autonomous AutoTrader (AAT) V4.1.0: Sovereign Citadel

Autonomous AutoTrader (AAT) is a high-performance, 100% FOSS hybrid trading system. V4.1.0 "Sovereign Citadel" introduces the **MT5-Primary Ingress** and **Symmetric Heartbeat**, eliminating retail data latency and ensuring total execution autonomy.

---

## 🏗️ Sovereign Citadel Evolutions

### 1. MT5-Primary Ingress
The system no longer relies on 3rd party APIs for its primary analysis. The EA pushes real-time OHLC data (M1-D1) directly to the Python brain, ensuring 100% price parity.

### 2. Symmetric 10s Heartbeat
A hardened safety loop. Both MQL5 and Python monitor each other on a strict 10s window. Any failure triggers an immediate capital protection sequence (Emergency BE).

### 3. Glass Cockpit UI
A professional 3-tab dashboard (Health, Analytics, Settings) designed to manage high-density telemetry without visual noise.

---

## 🛠️ Installation & Setup (Tactical Guide)

### Prerequisites
- MetaTrader 5 Terminal (Build 4000+).
- Python 3.10+.
- SharedMemory.dll (Now with Atomic Mutex support).

### 💻 Fast-Start Execution
1. **Initialize Engine**:
   ```powershell
   .\run_engine.bat
   ```
2. **Deploy EA**:
   - Attach `Scalper_v4_0_0.mq5` (V4.1.0 logic embedded) to any chart.
   - Verify **STABLE** status on the **HEALTH** tab.

---

## 📁 Repository Structure
- `MQL5/`: Expert Advisors and atomic libraries.
- `Python/V3_1_0/`: Sovereign inference engine and risk manager.
- `db/`: `aat_trading.db` containing the **DevEvolution** logic audit.
- `L99_CERTIFICATION.md`: Verification manual and stress-test guide.

---

## 🏅 Certification
- **Zero-Stub Certified**: 100% production-ready, self-training logic.
- **Author**: Simon Peter
