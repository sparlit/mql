# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Event-Driven Microkernel Orchestrator

import os
import json
import logging
import asyncio
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any

# Core Components
from src.shared.utils.bus import bus
from src.core.auth import create_access_token, get_current_user

# Load Vault for credentials
VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "vault.json")
with open(VAULT_PATH, "r") as f:
    vault = json.load(f)

app = FastAPI(title="AAT Sovereign Citadel V5.0.0")

# Lazy imports to avoid initialization before bus is ready
from src.plugins.intelligence.engine import intelligence
from src.plugins.execution.risk import risk_plugin
from src.plugins.execution.ingress import run_ingress
from src.plugins.data.aggregator import data_plugin
from src.shared.db.sync_service import sync_service
from src.plugins.ui.portal import router as ui_router

app.include_router(ui_router)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == vault["ADMIN_USERNAME"] and form_data.password == vault["ADMIN_PASSWORD"]:
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.on_event("startup")
async def startup_event():
    logging.info("AAT Microkernel V5.0.0 starting...")
    # Start Background Ingress Service
    asyncio.create_task(run_ingress())
    await bus.emit("system:startup", {"status": "initializing"})

@app.get("/health")
async def health():
    return {"status": "OK", "version": "5.0.0", "engine": "FastAPI Microkernel"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
