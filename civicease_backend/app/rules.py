"""Rule-pack pipeline helpers (pure): validate drafts, a deterministic mock extractor, official-URL check.
Pipeline: ingest official source -> extract rules (Gemini) -> human reviewer approves -> publish with citation."""
import re
from typing import Optional
from urllib.parse import urlparse

ALLOWED_FIELDS = {"age": "num", "annual_income": "num", "category": "str", "occupation": "str", "state": "str",
                  "gender": "str", "land_holding_hectares": "num", "is_student": "bool"}
OPS = {"<=", "<", ">=", ">", "==", "!=", "in"}
DOC_TYPES = {"aadhaar", "income_certificate", "land_record", "caste_certificate", "marksheet", "ration_card"}
OFFICIAL_SUFFIXES = ("gov.in", "nic.in")


def is_official_url(url: str, extra_suffixes: tuple = ()) -> bool:
    p = urlparse(url)
    host = (p.hostname or "").lower()
    return p.scheme == "https" and any(host == s or host.endswith("." + s) for s in OFFICIAL_SUFFIXES + tuple(extra_suffixes))


def validate_draft(d: dict) -> list:
    errs = []
    if not str(d.get("name", "")).strip():
        errs.append("name is required")
    crit = d.get("criteria")
    if not isinstance(crit, list) or not crit:
        errs.append("at least one criterion is required")
        crit = []
    seen = set()
    for c in crit:
        if not isinstance(c, dict) or {"id", "label", "field", "op", "value"} - set(c):
            errs.append("criterion needs id, label, field, op, value")
            continue
        if c["id"] in seen:
            errs.append(f"duplicate criterion id {c['id']}")
        seen.add(c["id"])
        kind = ALLOWED_FIELDS.get(c["field"])
        if kind is None:
            errs.append(f"field '{c['field']}' is not allowed")
        elif c["op"] not in OPS:
            errs.append(f"operator '{c['op']}' is not allowed")
        elif c["op"] == "in":
            if not isinstance(c["value"], list) or not all(isinstance(v, str) for v in c["value"]):
                errs.append("'in' needs a list of strings")
        elif kind == "num" and (isinstance(c["value"], bool) or not isinstance(c["value"], (int, float))):
            errs.append(f"{c['field']} needs a numeric value")
        elif kind == "bool" and not isinstance(c["value"], bool):
            errs.append(f"{c['field']} needs true/false")
        elif kind == "str" and not isinstance(c["value"], str):
            errs.append(f"{c['field']} needs a string")
    bad_docs = [x for x in d.get("required_documents", []) if x not in DOC_TYPES]
    if bad_docs:
        errs.append(f"unknown document types: {', '.join(bad_docs)}")
    return errs


def _money(num: str, unit: Optional[str]) -> int:
    n = float(num.replace(",", ""))
    if unit and unit.lower() in ("lakh", "lakhs", "lac"):
        n *= 100000
    return int(n)


def mock_extract(text: str) -> dict:
    """Heuristic extractor used when USE_MOCK_LLM=true. Live mode asks Gemini for the same JSON shape."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    low = text.lower()
    criteria, docs = [], ["aadhaar"]
    m = re.search(r"(\d{2})\s*(?:years|yrs)?\s*(?:of age\s*)?(?:or above|and above|or more|\+)", low)
    if m:
        criteria.append({"id": "age", "label": f"Age {m.group(1)} or above", "field": "age", "op": ">=", "value": int(m.group(1))})
    m = re.search(r"income[^.\n]{0,60}?(?:not exceed(?:ing)?|up to|below|less than|under|does not exceed)\D{0,15}?([\d,]+(?:\.\d+)?)\s*(lakhs?|lac)?", low)
    if m:
        v = _money(m.group(1), m.group(2))
        criteria.append({"id": "income", "label": f"Annual income up to Rs {v:,}", "field": "annual_income", "op": "<=", "value": v})
        docs.append("income_certificate")
    if "farmer" in low:
        criteria.append({"id": "occupation", "label": "Occupation is farmer", "field": "occupation", "op": "==", "value": "FARMER"})
        docs.append("land_record")
    if "student" in low:
        criteria.append({"id": "student", "label": "Currently a student", "field": "is_student", "op": "==", "value": True})
        docs.append("marksheet")
    cats = [c for c in ("SC", "ST", "OBC") if re.search(rf"\b{c}\b", text)]
    if cats:
        criteria.append({"id": "category", "label": "Category: " + "/".join(cats), "field": "category", "op": "in", "value": cats})
        docs.append("caste_certificate")
    if re.search(r"\bwom[ae]n\b|\bfemale\b", low):
        criteria.append({"id": "gender", "label": "Woman applicant", "field": "gender", "op": "==", "value": "FEMALE"})
    benefit = next((ln for ln in lines[1:] if re.search(r"benefit|assistance|pension|scholarship|support", ln, re.I)), (lines[1] if len(lines) > 1 else (lines[0] if lines else "")))
    return {"name": lines[0][:200] if lines else "", "benefit": benefit[:300], "state": "ALL", "deadline": None,
            "required_documents": list(dict.fromkeys(docs)), "criteria": criteria}
