import json
import time

from app import portal, security, telemetry
from app.config import get_settings


def _call_worker(plan: list) -> list:  # pragma: no cover - needs the worker service
    import httpx
    s = get_settings()
    body = json.dumps({"plan": plan}).encode()
    ts = int(time.time())
    try:
        r = httpx.post(s.worker_url.rstrip("/") + "/run", content=body, timeout=90,
                       headers={"Content-Type": "application/json", "X-Timestamp": str(ts),
                                "X-Signature": security.sign_request(s.worker_secret, ts, body)})
    except httpx.HTTPError:
        raise RuntimeError("worker unreachable")
    if r.status_code == 403:
        raise portal.PortalViolation(r.json().get("detail", "blocked by worker policy"))
    if r.status_code != 200:
        raise RuntimeError(f"worker error {r.status_code}")
    return r.json()["log"]


def run(base_url: str, form: dict) -> list:
    """Plan -> validate (allow-list; no submit/OTP/CAPTCHA) -> sandboxed worker -> pause at Gate 4.
    The worker only ever receives the plan (form values with ID last-4), never documents or keys."""
    s = get_settings()
    plan = portal.build_plan(s.portal_base_url or base_url, form)
    portal.validate_plan(plan, s.allowed_portal_domains)  # API-side check; the worker re-checks (defence in depth)
    if s.worker_url:
        log = _call_worker(plan)
    elif s.use_playwright:
        log = portal.run_playwright(plan)
    else:
        log = portal.run_simulated(plan)
    telemetry.emit("human_gate", gate=4, state="paused", reason="citizen must complete login/OTP/CAPTCHA and submit",
                   worker="separate" if s.worker_url else "in-process")
    return log
