"""Tamper-evident audit trail: each entry stores the hash of the previous one (pure module)."""
import hashlib
import json

GENESIS = "0" * 64


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_hash(prev_hash: str, ts: str, actor: str, action: str, detail: dict) -> str:
    body = canonical({"ts": ts, "actor": actor, "action": action, "detail": detail})
    return hashlib.sha256((prev_hash + body).encode()).hexdigest()


def verify_chain(events) -> dict:
    """events: iterable of dicts (ts, actor, action, detail(dict), prev_hash, hash) in order."""
    prev, n = GENESIS, 0
    for e in events:
        if e["prev_hash"] != prev:
            return {"valid": False, "broken_at": n, "reason": "prev_hash mismatch (entry removed or reordered)"}
        if compute_hash(prev, e["ts"], e["actor"], e["action"], e["detail"]) != e["hash"]:
            return {"valid": False, "broken_at": n, "reason": "entry content altered"}
        prev, n = e["hash"], n + 1
    return {"valid": True, "length": n}
