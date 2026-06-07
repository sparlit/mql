# 🛰️ AAT V5.0.0: Sovereign Citadel (Distributed Microkernel)

AAT V5.0.0 is an institutional-grade, 100% FOSS hybrid trading system rebuilt from the ground up on a **FastAPI Microkernel** with **Event-Driven Decoupling**.

---

## 🏛️ New Architecture (V5.0.0)

- **Core Orchestrator**: FastAPI-based asynchronous microkernel.
- **Event Bus**: Internal pub-sub system for zero-coupling between analysis and execution.
- **Intelligence**: INT8 Quantized ONNX models for low-latency CPU inference (i3/4GB RAM optimized).
- **Hybrid Sync**: Local SQLite state with background reconciliation to remote QuestDB.
- **Terminal Agnostic**: Abstracted ingress layers for MT5, FIX, or CCXT.

---

## 🚀 Quick Start (Production)

### 1. Environment Setup (Windows/Linux)
```bash
# Recommended: Python 3.10+
pip install fastapi uvicorn onnxruntime transformers torch pandas numpy xgboost faiss-cpu jinja2
```

### 2. Initialize the Citadel
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python src/core/main.py
```
Visit `http://127.0.0.1:8000` to view the **Sovereign Dashboard**.

### 3. Deploy MetaTrader 5 EA
- Copy `MQL5/Experts/V4_1_2/Scalper_v4_1_2.mq5` to your MT5 folder.
- Ensure the EA is configured to connect to `127.0.0.1:4444`.

---

## 🎖️ Certification
- **Zero-Stub Certified**: All ML models use production loaders. No random-noise training failovers.
- **Microkernel Compliant**: All features (Risk, Intelligence, UI) are hot-swappable plugins.
- **Hardware Optimized**: CPU-bound INT8 quantization for old hardware.
