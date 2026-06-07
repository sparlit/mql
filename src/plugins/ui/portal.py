# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Monitoring Portal Plugin

import time
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.shared.utils.state_coordinator import coordinator

router = APIRouter()
templates = Jinja2Templates(directory="src/plugins/ui/templates")

# Mock data for demonstration until StateCoordinator is fully hooked
START_TIME = time.time()

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    uptime_sec = int(time.time() - START_TIME)
    uptime_str = f"{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m {uptime_sec % 60}s"

    stats = {
        "heartbeat": "STABLE",
        "latency": coordinator.get_state("latency") or "1.2ms",
        "uptime": uptime_str,
        "active_symbols": [
            {"name": "EURUSD", "signal": "BUY", "conf": 82, "vsa": "+4"},
            {"name": "GBPUSD", "signal": "NEUTRAL", "conf": 12, "vsa": "0"}
        ],
        "recent_logs": [
            {"time": "12:01:04", "cat": "RISK", "msg": "Lot size calculated for EURUSD: 0.12"},
            {"time": "12:00:55", "cat": "INTEL", "msg": "XGBoost consensus reached for EURUSD: BULLISH"},
            {"time": "12:00:30", "cat": "DATA", "msg": "Fetched 5 news events from ForexFactory"}
        ]
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"stats": stats})
