import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app import metrics, retrieval
from app.config import get_settings
from app.db import Base, SessionLocal, engine
from app.errors import ApiError
from app.pii import redact_text
from app.routers import (admin, applications, auth, consent_profile, dashboard, documents, schemes_agents, system,
                         voice)
from app.seed import SCHEMES

log = logging.getLogger("civicease")


class RedactingFilter(logging.Filter):
    """Keep personal data out of logs."""
    def filter(self, record):
        record.msg, record.args = redact_text(record.getMessage())[0], ()
        return True


def _seed(db):
    from app.models import Scheme
    for s in SCHEMES:
        if not db.get(Scheme, s["id"]):
            db.add(Scheme(**s))
    db.commit()
    for sch in db.execute(select(Scheme)).scalars():
        if not sch.embedding:
            retrieval.index_scheme(db, sch)  # RAG store
    db.commit()


async def _purge_loop():
    """Auto-expiry of stored documents, hourly."""
    while True:
        await asyncio.sleep(3600)
        try:
            def run():
                with SessionLocal() as db:
                    documents.purge_expired(db)
            await asyncio.to_thread(run)
        except Exception as e:  # keep the loop alive
            log.error("purge failed: %s", type(e).__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    for h in logging.getLogger().handlers:
        h.addFilter(RedactingFilter())
    logging.getLogger("uvicorn.access").addFilter(RedactingFilter())
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        retrieval.ensure_pgvector(db)
        _seed(db)
        documents.purge_expired(db)
    task = asyncio.create_task(_purge_loop())
    yield
    task.cancel()


app = FastAPI(title="CivicEase AI Backend", version="2.0.0", lifespan=lifespan)
if get_settings().force_https:
    app.add_middleware(HTTPSRedirectMiddleware)  # run uvicorn with --proxy-headers behind a TLS proxy
app.add_middleware(CORSMiddleware, allow_origins=list(get_settings().cors_origins), allow_credentials=False,
                   allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])


@app.middleware("http")
async def observe_and_secure(request: Request, call_next):
    start = time.perf_counter()
    resp = await call_next(request)
    route = request.scope.get("route")
    path = getattr(route, "path", "unmatched")
    metrics.inc("http_requests_total", method=request.method, path=path, status=resp.status_code)
    metrics.inc("http_request_seconds_sum", time.perf_counter() - start, path=path)
    if resp.status_code >= 500:
        metrics.inc("http_errors_total", path=path)
    resp.headers.update({
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
        "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer",
        "Cache-Control": resp.headers.get("Cache-Control", "no-store"),
    })
    return resp


def _err(status: int, code: str, message: str):
    return JSONResponse(status_code=status, content={"ok": False, "data": None, "error": {"code": code, "message": message}})


@app.exception_handler(ApiError)
async def api_error(_, e: ApiError):
    return _err(e.status, e.code, e.message)


@app.exception_handler(RequestValidationError)
async def validation_error(_, e: RequestValidationError):
    # never echo submitted values back (they may contain personal data)
    msg = "; ".join(f"{'.'.join(str(x) for x in err['loc'][1:])}: {err['msg']}" for err in e.errors())
    return _err(422, "VALIDATION_ERROR", msg)


@app.exception_handler(Exception)
async def unhandled(_, e: Exception):
    log.error("unhandled error: %s", type(e).__name__)
    return _err(500, "INTERNAL_ERROR", "Something went wrong. Please try again.")


for r in (system.router, auth.router, consent_profile.router, schemes_agents.router, documents.router,
          applications.router, dashboard.router, voice.router, admin.router):
    app.include_router(r)
