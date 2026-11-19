"""Trust & Compliance guard: runs around every agent output before it is shown or acted on (pure module)."""
import re

from app.pii import redact_obj

_FORBIDDEN = [
    (re.compile(r"(?<!not )(?<!no )\bguarantee[sd]?\b", re.I), "guarantee language"),
    (re.compile(r"\b(will|is certain to) be (approved|accepted|sanctioned)\b", re.I), "acceptance promise"),
    (re.compile(r"\b100\s?%\s?(sure|certain|approved|eligible)\b", re.I), "certainty claim"),
    (re.compile(r"\b(bypass|skip|automate)\w*\s+(the\s+)?(otp|captcha)\b", re.I), "OTP/CAPTCHA bypass"),
    (re.compile(r"\bsubmit(ted)?\s+(on your behalf|for you)\b", re.I), "autonomous submission"),
]


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _strings(v)


def guard(result: dict, kind: str) -> dict:
    """Returns the (PII-redacted) result, or a blocked result listing violations."""
    violations = []
    for s in _strings(result):
        for rx, label in _FORBIDDEN:
            if rx.search(s):
                violations.append(label)
    if kind in ("scheme_match", "eligibility"):
        for card in result.get("schemes", [result] if "scheme_id" in result else []):
            if "source_url" not in card or "last_verified" not in card:
                violations.append("scheme output without source/last_verified")
            if card.get("preliminary_estimate") is not True:
                violations.append("eligibility not marked preliminary")
    if violations:
        return {"status": "blocked_by_trust_guard", "violations": sorted(set(violations))}
    return redact_obj(result)
