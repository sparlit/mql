# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Monitoring Portal Plugin

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from src.shared.utils.state_coordinator import coordinator

router = APIRouter()
os.makedirs("src/plugins/ui/templates", exist_ok=True)
templates = Jinja2Templates(directory="src/plugins/ui/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Fetch real-time telemetry from StateCoordinator
    stats = {
        "heartbeat": "STABLE",
        "latency": coordinator.get_state("latency") or "0.0ms",
        "active_symbols": coordinator.get_state("symbols") or [],
        "version": "5.0.0"
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"stats": stats})
