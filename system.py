import json

from fastapi import APIRouter, Depends, Header
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

import hmac

from app import audit, metrics, telemetry
from app.config import get_settings
from app.deps import current_user, get_db
from app.errors import ApiError, ok
from app.models import AuditEvent, User

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    s = get_settings()
    return ok({"status": "up", "mock_llm": s.use_mock_llm, "env": s.env})


@router.get("/audit/verify")
def verify_audit(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return ok(audit.verify(db))


@router.get("/audit/events")
def my_events(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.execute(select(AuditEvent).where(AuditEvent.actor == user.id).order_by(AuditEvent.id.desc()).limit(50)).scalars()
    return ok([{"ts": r.ts, "action": r.action, "detail": json.loads(r.detail), "hash": r.hash} for r in rows])


@router.get("/judge/telemetry")
def judge(user: User = Depends(current_user)):
    """Judge Mode: model routing, skill loading, PII masking and human gates. Contains no raw personal data."""
    if not get_settings().judge_mode:
        raise ApiError(404, "NOT_FOUND", "Not found.")
    return ok(telemetry.snapshot())


@router.get("/metrics", response_class=PlainTextResponse)
def prometheus(x_metrics_token: str = Header(default="")):
    """Errors, latency and model usage (cost proxy). Disabled unless METRICS_TOKEN is set."""
    token = get_settings().metrics_token
    if not token or not hmac.compare_digest(token, x_metrics_token):
        raise ApiError(404, "NOT_FOUND", "Not found.")
    return metrics.render()


_PORTAL = """<!doctype html><html><head><meta charset="utf-8"><title>Mock Scheme Portal (SYNTHETIC)</title></head>
<body><h1>Mock Scheme Portal - demo only</h1><p>SYNTHETIC DEMO PORTAL. Not a government site.</p>
<form onsubmit="return false">
<label>Name <input name="name"></label><br><label>Date of birth <input name="dob"></label><br>
<label>State <input name="state"></label><br><label>Annual income <input name="annual_income"></label><br>
<label>ID (last 4) <input name="id_last4"></label><br>
<button id="continue" type="button">Continue</button>
<p>Login, OTP and CAPTCHA are completed by the citizen. The assistant never presses Submit.</p>
<button id="final-action" type="button">Submit</button>
</form></body></html>"""


@router.get("/mock-portal/form", response_class=HTMLResponse)
def mock_portal():
    return _PORTAL
