# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Institutional Monitoring Portal (Glass Cockpit)

import time
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.shared.utils.state_coordinator import coordinator
from src.core.auth import get_current_user, User

router = APIRouter()
templates = Jinja2Templates(directory="src/plugins/ui/templates")

START_TIME = time.time()

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    uptime_sec = int(time.time() - START_TIME)
    uptime_str = f"{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m {uptime_sec % 60}s"

    stats = {
        "heartbeat": "STABLE",
        "latency": coordinator.get_state("latency") or "0.8ms",
        "uptime": uptime_str,
        "active_symbols": coordinator.get_state("active_symbols") or [
            {"name": "EURUSD", "signal": "SMC_BUY", "conf": 82, "vsa": "+4"},
            {"name": "XAUUSD", "signal": "NEUTRAL", "conf": 45, "vsa": "-1"}
        ],
        "recent_logs": coordinator.get_state("audit_trail") or [
            {"time": time.strftime("%H:%M:%S"), "cat": "CORE", "msg": "Sovereign Citadel V5.0.0 Engaged"}
        ]
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"stats": stats})

@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, user: User = Depends(get_current_user)):
    if "admin" not in user.roles:
        return HTMLResponse("Unauthorized", status_code=403)
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"stats": {"mode": "ADMIN"}})
