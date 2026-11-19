"""Append to / verify the hash-chained audit log. Details are PII-redacted before storage."""
import json
import threading

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.hashchain import GENESIS, canonical, compute_hash, verify_chain
from app.models import AuditEvent, utcnow
from app.pii import redact_obj

_lock = threading.Lock()


def record(db: Session, actor: str, action: str, **detail) -> None:
    detail = redact_obj(detail)
    with _lock:  # single-writer chain per process; Postgres advisory lock serialises across instances
        if db.get_bind().dialect.name == "postgresql":
            db.execute(text("SELECT pg_advisory_xact_lock(727274)"))
        last = db.execute(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(1)).scalar_one_or_none()
        prev = last.hash if last else GENESIS
        ts = utcnow().isoformat(timespec="microseconds")
        h = compute_hash(prev, ts, actor, action, detail)
        db.add(AuditEvent(ts=ts, actor=actor, action=action, detail=canonical(detail), prev_hash=prev, hash=h))
        db.flush()


def verify(db: Session) -> dict:
    rows = db.execute(select(AuditEvent).order_by(AuditEvent.id)).scalars().all()
    return verify_chain([{"ts": r.ts, "actor": r.actor, "action": r.action, "detail": json.loads(r.detail),
                          "prev_hash": r.prev_hash, "hash": r.hash} for r in rows])
