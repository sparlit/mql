# 🛰️ AAT V5.0.0: Sovereign Citadel (Institutional Microkernel)

Autonomous AutoTrader (AAT) V5.0.0 is the world's most robust, 100% FOSS institutional hybrid trading system. It synergizes the deterministic precision of **MetaTrader 5 (MQL5)** with an advanced **Python FastAPI Microkernel Intelligence Stack**.

This "Sovereign Citadel" release establishes a new benchmark for autonomous capital protection, high-performance execution, and AI-driven market analysis on consumer-grade hardware (i3/i5, 4-8GB RAM).

---

## 🏛️ Architecture: Sovereign Microkernel
AAT V5.0.0 is built on an **Event-Driven Asynchronous Hybrid Microkernel**. This architecture ensures zero-coupling between data ingestion, institutional intelligence, and trade execution.

- **Orchestrator (`src/core/main.py`)**: Asynchronous event loop managing plugin lifecycle and Hardened RBAC.
- **Sovereign Log (`db/sovereign_audit.db`)**: Automated chronological audit trail from code commit to execution.
- **Intelligence Plugin (`src/plugins/intelligence/engine.py`)**: Institutional SMC (Order Blocks, Liquidity Grabs) + XGBoost Ensemble.
- **Risk Plugin (`src/plugins/execution/risk.py`)**: Institutional ATR-based lot sizing with real-time equity protection.
- **Sovereign Ingress (`src/plugins/execution/ingress.py`)**: Bidirectional AES-256-CBC encrypted socket gateway for MT5.

---

## 🚀 Installation & Setup (Step-by-Step)

### 📋 Prerequisites
- **Python 3.10 or 3.11** (Recommended).
- **MetaTrader 5 Terminal** (Windows required for EA execution).

### 💻 1. Unified Installation (Cross-Platform)
The easiest way to install is using the Sovereign Universal Installer:

```bash
# Clone and Enter
git clone https://github.com/sparlit/mql.git
cd mql

# Run the Universal Installer
python aat_install.py
```

### 🔐 2. Configuration (`src/vault.json`)
Before starting, update your institutional vault with strong credentials.

```json
{
  "MASTER_KEY": "YOUR_32_CHAR_AES_KEY",
  "ADMIN_USERNAME": "your_user",
  "ADMIN_PASSWORD": "your_secure_password",
  "JWT_SECRET": "your_hex_secret"
}
```

### 🧠 3. Start the Sovereign Engine
```bash
# Windows
scripts\run_engine.bat

# Linux/macOS
source .venv/bin/activate
export PYTHONPATH=.
python src/core/main.py
```

Visit `http://127.0.0.1:8000` to access the **Glass Cockpit Dashboard**.

---

## 📈 4. Deploy MetaTrader 5 Expert Advisor

### **File Deployment**
1.  **Expert Advisor**: Copy `MQL5/Experts/AAT_Sovereign_EA.mq5` to your MT5 `MQL5/Experts/` folder.
2.  **Includes**: Copy all files from `MQL5/Include/` to your MT5 `MQL5/Include/` folder.

### **EA Inputs**
- `InpMasterKey`: Must match `MASTER_KEY` in `src/vault.json`.
- `InpEngineHost`: `127.0.0.1`
- `InpEnginePort`: `4444`

---

## 🩺 5. Sovereign Verification

```bash
# Run unified core tests
python -m pytest tests/
```

---

## 🎖️ Certification & Compliance
- **Zero-Stub Certified**: 100% production-ready logic, no placeholders.
- **Institutional SMC**: Native Order Block and Liquidity Grab detection.
- **Hardware Optimized**: Optimized for i3/4GB hardware.
- **FOSS Sovereign**: 100% Free and Open Source under GNU GPL v3.
