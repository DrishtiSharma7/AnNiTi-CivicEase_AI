"""Doc Auditor. Rules and local OCR run as code BEFORE any model call; PII is redacted before text reaches a model;
IDs are masked + HMAC-digested; failures degrade to UNKNOWN and are logged."""
from datetime import date

from app import audit, docaudit, llm, ocr, quota, telemetry
from app.config import get_settings
from app.errors import ApiError
from app.pii import redact_text
from app.profile_parse import parse_number
from app.security import id_digest, mask_id
from app.skills import load_skill

CONFIRMABLE = {"name", "dob", "id_number", "annual_income", "valid_until", "category", "land_holding_hectares", "institution"}


def _store_id(doc, user, raw: str, fields: dict):
    doc.id_masked = mask_id(raw)
    doc.id_digest = id_digest(raw, user.id_salt, get_settings().pepper)
    fields["id_number"] = doc.id_masked  # raw value is never stored or logged
    telemetry.emit("pii_masking", field="id_number", masked=doc.id_masked, algo="HMAC-SHA256+salt",
                   digest_prefix=doc.id_digest[:12])


def _refresh(doc) -> list:
    doc.audit = docaudit.check_document(
        {"id": doc.id, "doc_type": doc.doc_type, "fields": doc.extracted or {}, "confidence": doc.confidence,
         "quality": doc.quality}, date.today())
    return doc.audit


def run(db, user, doc, data: bytes) -> list:
    load_skill("document-schema-validator")
    s = get_settings()
    local_quality = ocr.image_quality(data) if doc.mime.startswith("image/") else None
    text = ocr.extract_text(data, doc.mime) if (s.local_ocr or s.require_local_redaction) else None
    if local_quality == "blurry" and not text:
        ext = llm.unknown_doc("QUALITY_CHECKED_LOCALLY")  # rules first: no model call spent on an unreadable photo
        ext["quality"] = "blurry"
    else:
        quota.consume(db, user.id)
        if text:
            local_id = ocr.find_aadhaar(text)
            ext = llm.extract_from_text(redact_text(text)[0], doc.filename)  # PII redacted before the model call
            if local_id:
                ext.setdefault("fields", {})["id_number"] = local_id
        elif s.require_local_redaction and not s.use_mock_llm:
            ext = llm.unknown_doc("LOCAL_REDACTION_UNAVAILABLE")
        else:
            ext = llm.extract_document(data, doc.mime, doc.filename)
    if local_quality == "blurry":
        ext["quality"] = "blurry"
    if "MODEL_UNAVAILABLE" in (ext.get("warnings") or []):
        telemetry.emit("model_failure", doc=doc.id, outcome="UNKNOWN")
        audit.record(db, user.id, "model_failure", doc_id=doc.id, outcome="UNKNOWN")  # log the failure safely
    fields = dict(ext.get("fields") or {})
    raw_id = fields.pop("id_number", None)
    if raw_id:
        _store_id(doc, user, str(raw_id), fields)
    doc.doc_type, doc.confidence, doc.quality = ext.get("doc_type"), ext.get("confidence"), ext.get("quality")
    doc.extracted, doc.field_confidence = fields, ext.get("field_confidence") or {}
    return _refresh(doc)


def confirm_field(doc, user, field: str, value: str) -> list:
    """'Retake, confirm field or ask a human': the citizen confirms a value; checks run again."""
    fields, fc = dict(doc.extracted or {}), dict(doc.field_confidence or {})
    if field == "doc_type":
        if value not in docaudit.REQUIRED_FIELDS:
            raise ApiError(422, "BAD_VALUE", "Unknown document type.")
        doc.doc_type = value
    elif field in CONFIRMABLE:
        if field == "id_number":
            _store_id(doc, user, value, fields)
        elif field in ("annual_income", "land_holding_hectares"):
            try:
                fields[field] = parse_number(value)
            except ValueError:
                raise ApiError(422, "BAD_VALUE", "Enter a number.")
        else:
            fields[field] = value.strip()[:100]
        fc[field] = 1.0
    else:
        raise ApiError(422, "BAD_FIELD", f"Field '{field}' cannot be confirmed.")
    doc.extracted, doc.field_confidence = fields, fc
    req = docaudit.REQUIRED_FIELDS.get(doc.doc_type, [])
    if req and all(fields.get(f) not in (None, "") and fc.get(f, 0) >= docaudit.MIN_CONFIDENCE for f in req):
        doc.confidence = min(fc[f] for f in req)
    return _refresh(doc)
