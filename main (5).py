"""Separate, sandboxed browser worker. Run it in its own container with NO database, NO storage and NO model keys.
Accepts only HMAC-signed plans from the API, re-validates them against its own allow-list, never submits."""
import asyncio
import json
import os

from fastapi import FastAPI, Header, HTTPException, Request

from app import portal
from app.security import verify_request

app = FastAPI(title="CivicEase browser worker")
SECRET = os.getenv("WORKER_SHARED_SECRET", "")
ALLOWED = tuple(x.strip() for x in os.getenv("ALLOWED_PORTAL_DOMAINS", "localhost").split(",") if x.strip())
USE_PLAYWRIGHT = os.getenv("USE_PLAYWRIGHT", "false").lower() in ("1", "true", "yes")


@app.get("/health")
def health():
    return {"status": "up"}


@app.post("/run")
async def run(request: Request, x_timestamp: str = Header(...), x_signature: str = Header(...)):
    body = await request.body()
    try:
        ok = bool(SECRET) and verify_request(SECRET, int(x_timestamp), body, x_signature)
    except ValueError:
        ok = False
    if not ok:
        raise HTTPException(401, "bad signature")
    plan = json.loads(body)["plan"]
    try:
        portal.validate_plan(plan, ALLOWED)
    except portal.PortalViolation as e:
        raise HTTPException(403, str(e))
    log = await asyncio.to_thread(portal.run_playwright if USE_PLAYWRIGHT else portal.run_simulated, plan)
    return {"log": log}
