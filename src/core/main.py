# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Event-Driven Microkernel Orchestrator

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import asyncio
import logging
from typing import Dict, Any, Callable, List

# Core & Security
from src.core.auth import create_access_token, get_current_user

# Plugin UI
from src.plugins.ui.portal import router as ui_router

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def emit(self, event_type: str, data: Any):
        if event_type in self.subscribers:
            tasks = [callback(data) for callback in self.subscribers[event_type]]
            await asyncio.gather(*tasks)

app = FastAPI(title="AAT Sovereign Citadel V5.0.0")
bus = EventBus()

# Initialize Global Plugins (Registry)
# In production, these would be dynamically loaded from a plugins folder
from src.plugins.intelligence.engine import intelligence
from src.plugins.execution.risk import risk_plugin
from src.plugins.execution.ingress import run_ingress
from src.plugins.data.aggregator import data_plugin
from src.shared.db.sync_service import sync_service

# Include UI Plugin Router
app.include_router(ui_router)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "admin" and form_data.password == "citadel":
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.on_event("startup")
async def startup_event():
    logging.info("AAT Microkernel V5.0.0 starting...")
    # Start Background Services
    asyncio.create_task(run_ingress())
    await bus.emit("system:startup", {"status": "initializing"})

@app.get("/health")
async def health():
    return {"status": "OK", "version": "5.0.0", "engine": "FastAPI Microkernel"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
