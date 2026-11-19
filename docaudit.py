"""Deterministic document checks: expiry, missing fields, name/number mismatch, readiness (pure module).
Severities: blocking | warning | passed | unknown. Every finding carries a one-line fix."""
import re
from datetime import date, timedelta
from typing import Optional

REQUIRED_FIELDS = {
    "aadhaar": ["name", "dob", "id_number"],
    "income_certificate": ["name", "annual_income", "valid_until"],
    "land_record": ["name", "land_holding_hectares"],
    "caste_certificate": ["name", "category"],
    "marksheet": ["name", "institution"],
    "ration_card": ["name"],
}
HONORIFICS = {"shri", "smt", "mr", "mrs", "ms", "dr", "kumari", "sri", "shrimati"}
MIN_CONFIDENCE = 0.6
EXPIRY_WARN_DAYS = 30


def finding(code, severity, message, fix="", doc_id=None):
    return {"code": code, "severity": severity, "message": message, "fix": fix, "doc_id": doc_id}


def parse_date(s) -> Optional[date]:
    try:
        return date.fromisoformat(str(s))
    except (ValueError, TypeError):
        return None


def normalize_name(name: str) -> str:
    tokens = re.sub(r"[^\w\s]", "", str(name).lower()).split()
    return " ".join(t for t in tokens if t not in HONORIFICS)


def check_document(doc: dict, today: date) -> list:
    """doc: {id, doc_type, fields, confidence, quality}"""
    out, did = [], doc.get("id")
    dtype, fields = doc.get("doc_type"), doc.get("fields") or {}
    if dtype not in REQUIRED_FIELDS:
        return [finding("DOC_TYPE_UNKNOWN", "unknown", "Could not identify this document type.",
                        "Retake the photo or choose the document type manually.", did)]
    if (doc.get("confidence") or 0) < MIN_CONFIDENCE:
        out.append(finding("LOW_CONFIDENCE", "unknown", f"The {dtype} could not be read with enough confidence.",
                           "Retake the photo in good light, flat and fully in frame.", did))
    q = doc.get("quality")
    if q in ("blurry", "cropped"):
        out.append(finding(f"QUALITY_{q.upper()}", "warning", f"The {dtype} photo looks {q}.",
                           "Retake the photo so all four edges and text are sharp.", did))
    missing = [f for f in REQUIRED_FIELDS[dtype] if fields.get(f) in (None, "")]
    for f in missing:
        out.append(finding("MISSING_FIELD", "blocking", f"'{f}' is missing on the {dtype}.",
                           "Confirm this field manually or upload a complete document.", did))
    vu = parse_date(fields.get("valid_until"))
    if "valid_until" in REQUIRED_FIELDS[dtype] and fields.get("valid_until") and vu is None:
        out.append(finding("DATE_UNREADABLE", "unknown", "The expiry date could not be read.",
                           "Confirm the expiry date manually.", did))
    elif vu is not None:
        if vu < today:
            out.append(finding("EXPIRED", "blocking", f"The {dtype} expired on {vu.isoformat()}.",
                               "Obtain a fresh certificate before applying.", did))
        elif vu <= today + timedelta(days=EXPIRY_WARN_DAYS):
            out.append(finding("EXPIRING_SOON", "warning", f"The {dtype} expires on {vu.isoformat()}.",
                               "Renew it soon, before the application is processed.", did))
        else:
            out.append(finding("NOT_EXPIRED", "passed", f"The {dtype} is within its validity period.", "", did))
    if not missing and (doc.get("confidence") or 0) >= MIN_CONFIDENCE:
        out.append(finding("FIELDS_PRESENT", "passed", f"All required fields were found on the {dtype}.", "", did))
    return out


def cross_check_names(docs: list) -> list:
    named = [(d, d["fields"]["name"]) for d in docs if (d.get("fields") or {}).get("name")]
    if len(named) < 2:
        return []
    ref_doc = next((x for x in named if x[0].get("doc_type") == "aadhaar"), named[0])
    ref_norm, out, ok = normalize_name(ref_doc[1]), [], True
    for d, nm in named:
        if d is ref_doc[0]:
            continue
        if normalize_name(nm) != ref_norm:
            ok = False
            out.append(finding("NAME_MISMATCH", "blocking",
                               f"Name '{nm}' on the {d['doc_type']} does not match '{ref_doc[1]}' on the {ref_doc[0]['doc_type']}.",
                               "Get the certificate corrected, or attach a name-correction affidavit.", d.get("id")))
    if ok:
        out.append(finding("NAMES_CONSISTENT", "passed", "Names match across all uploaded documents.", ""))
    return out


def build_readiness(required_types: list, docs: list, profile: dict, today: date) -> dict:
    findings = []
    have = {d.get("doc_type") for d in docs}
    for t in required_types:
        if t not in have:
            findings.append(finding("MISSING_DOCUMENT", "blocking", f"Required document not uploaded: {t}.",
                                    f"Upload your {t.replace('_', ' ')}."))
    relevant = [d for d in docs if d.get("doc_type") in required_types or d.get("doc_type") not in REQUIRED_FIELDS]
    for d in relevant:
        findings += check_document(d, today)
    findings += cross_check_names([d for d in relevant if d.get("doc_type") in REQUIRED_FIELDS])
    inc_doc = next((d for d in relevant if d.get("doc_type") == "income_certificate"), None)
    p_inc, d_inc = profile.get("annual_income"), ((inc_doc or {}).get("fields") or {}).get("annual_income")
    if isinstance(p_inc, (int, float)) and isinstance(d_inc, (int, float)) and d_inc > 0:
        if abs(p_inc - d_inc) / d_inc > 0.10:
            findings.append(finding("INCOME_MISMATCH", "warning",
                                    "Income in your profile differs from the income certificate by more than 10%.",
                                    "Correct your profile or confirm which figure is right."))
    buckets = {s: [f for f in findings if f["severity"] == s] for s in ("blocking", "warning", "passed", "unknown")}
    return {
        **buckets,
        "ready": not buckets["blocking"] and not buckets["unknown"],
        "disclaimer": "Readiness is a preliminary check. It does not guarantee acceptance of your application.",
    }
