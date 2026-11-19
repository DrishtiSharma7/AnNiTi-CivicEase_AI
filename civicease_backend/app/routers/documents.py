import re
from datetime import timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import audit, telemetry
from app.agents import doc_auditor
from app.config import get_settings
from app.deps import current_user, get_db, rate_limit, require_consent
from app.errors import ApiError, ok
from app.kms import get_kms
from app.models import Document, User, uid, utcnow
from app.schemas import ConfirmFieldIn
from app.security import decrypt_document, derive_key, encrypt_document, sha256_hex, sign_payload, verify_payload
from app.storage import get_storage

router = APIRouter(dependencies=[Depends(rate_limit)], tags=["documents"])
_MAGIC = [(b"%PDF-", "application/pdf"), (b"\x89PNG\r\n\x1a\n", "image/png"), (b"\xff\xd8\xff", "image/jpeg")]


def _sniff(data: bytes):
    return next((m for sig, m in _MAGIC if data.startswith(sig)), None)


def _aad(user_id: str, doc_id: str) -> bytes:
    return f"{user_id}:{doc_id}".encode()  # binds ciphertext to this user and document


def _view(d: Document) -> dict:
    return {"id": d.id, "filename": d.filename, "mime": d.mime, "size": d.size, "sha256": d.sha256,
            "doc_type": d.doc_type, "id_masked": d.id_masked, "quality": d.quality, "confidence": d.confidence,
            "field_confidence": d.field_confidence, "human_review": d.human_review, "review_note": d.review_note,
            "audited": d.audit is not None, "expires_at": d.expires_at.isoformat()}


def _own(db: Session, user: User, doc_id: str) -> Document:
    d = db.get(Document, doc_id)
    if not d or d.user_id != user.id:  # same error for "missing" and "not yours"
        raise ApiError(404, "NOT_FOUND", "Document not found.")
    return d


def _read_verified(d: Document) -> bytes:
    data = decrypt_document(get_storage().get(d.enc_path), d.wrapped_key, get_kms(), _aad(d.user_id, d.id))
    if sha256_hex(data) != d.sha256:  # integrity check before any agent uses the file
        raise ApiError(409, "TAMPERED", "This file failed its integrity check.")
    return data


def purge_user_documents(db: Session, user_id: str) -> int:
    n = 0
    for d in db.execute(select(Document).where(Document.user_id == user_id)).scalars():
        get_storage().delete(d.enc_path)
        db.delete(d)
        n += 1
    return n


def purge_expired(db: Session) -> int:
    n = 0
    for d in db.execute(select(Document).where(Document.expires_at < utcnow())).scalars():
        get_storage().delete(d.enc_path)
        db.delete(d)
        n += 1
    db.commit()
    return n


@router.post("/documents")
def upload(file: UploadFile = File(...), user: User = Depends(require_consent("document_use")),
           db: Session = Depends(get_db)):
    s = get_settings()
    data = file.file.read(s.max_upload_bytes + 1)
    if len(data) > s.max_upload_bytes:
        raise ApiError(413, "TOO_LARGE", f"Files must be under {s.max_upload_bytes // (1024 * 1024)} MB.")
    mime = _sniff(data)
    if not mime:
        raise ApiError(415, "UNSUPPORTED_TYPE", "Upload a PDF, PNG or JPEG file.")
    digest = sha256_hex(data)
    dup = db.execute(select(Document).where(Document.user_id == user.id, Document.sha256 == digest)).scalar_one_or_none()
    if dup:  # same fingerprint: reuse stored file and cached audit
        return ok({**_view(dup), "duplicate": True})
    doc_id = uid()
    blob, wrapped = encrypt_document(data, get_kms(), _aad(user.id, doc_id))
    key = f"{user.id}/{doc_id}.bin"
    get_storage().put(key, blob)
    name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(file.filename or "upload").name)[:80]
    d = Document(id=doc_id, user_id=user.id, filename=name, mime=mime, size=len(data), sha256=digest,
                 enc_path=key, wrapped_key=wrapped, expires_at=utcnow() + timedelta(days=s.doc_retention_days))
    db.add(d)
    audit.record(db, user.id, "document_uploaded", doc_id=doc_id, sha256=digest, size=len(data), mime=mime)
    db.commit()
    return ok({**_view(d), "duplicate": False})


@router.get("/documents")
def list_docs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return ok([_view(d) for d in db.execute(select(Document).where(Document.user_id == user.id)).scalars()])


@router.get("/documents/{doc_id}")
def get_doc(doc_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    d = _own(db, user, doc_id)
    return ok({**_view(d), "fields": d.extracted, "findings": d.audit})


@router.post("/documents/{doc_id}/audit")
def audit_doc(doc_id: str, user: User = Depends(require_consent("document_use")), db: Session = Depends(get_db)):
    d = _own(db, user, doc_id)
    if d.audit is not None:  # cache keyed by the document's SHA-256: no repeat model call
        telemetry.emit("cache_hit", sha256_prefix=d.sha256[:12])
        return ok({**_view(d), "findings": d.audit, "cached": True})
    findings = doc_auditor.run(db, user, d, _read_verified(d))
    audit.record(db, user.id, "document_audited", doc_id=d.id, doc_type=d.doc_type,
                 blocking=sum(f["severity"] == "blocking" for f in findings))
    db.commit()
    return ok({**_view(d), "findings": findings, "cached": False})


@router.post("/documents/{doc_id}/confirm-field")
def confirm_field(doc_id: str, body: ConfirmFieldIn, user: User = Depends(require_consent("document_use")),
                  db: Session = Depends(get_db)):
    """Citizen confirms or corrects one field (the 'confirm field' action); checks run again."""
    d = _own(db, user, doc_id)
    if d.audit is None:
        raise ApiError(409, "NOT_AUDITED", "Audit this document first.")
    findings = doc_auditor.confirm_field(d, user, body.field, body.value)
    audit.record(db, user.id, "field_confirmed", doc_id=d.id, field=body.field)  # field name only
    db.commit()
    return ok({**_view(d), "fields": d.extracted, "findings": findings})


@router.post("/documents/{doc_id}/ask-human")
def ask_human(doc_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    d = _own(db, user, doc_id)
    d.human_review, d.review_note = "requested", None
    audit.record(db, user.id, "human_review_requested", doc_id=d.id)
    db.commit()
    return ok({"human_review": d.human_review})


@router.get("/documents/{doc_id}/link")
def signed_link(doc_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    d = _own(db, user, doc_id)
    s = get_settings()
    token = sign_payload({"doc": d.id, "usr": user.id}, derive_key(s.pepper, "file-url"), s.signed_url_ttl)
    audit.record(db, user.id, "file_link_issued", doc_id=d.id)
    db.commit()
    return ok({"url": f"/files/{token}", "expires_in": s.signed_url_ttl})


@router.get("/files/{token}")
def download(token: str, db: Session = Depends(get_db)):
    s = get_settings()
    claims = verify_payload(token, derive_key(s.pepper, "file-url"))
    d = db.get(Document, claims["doc"]) if claims else None
    if not d or d.user_id != claims["usr"]:
        raise ApiError(403, "LINK_INVALID", "This link is invalid or has expired.")
    return Response(_read_verified(d), media_type=d.mime,
                    headers={"Content-Disposition": f'attachment; filename="{d.filename}"', "Cache-Control": "no-store"})


@router.delete("/documents/{doc_id}")
def delete_doc(doc_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    d = _own(db, user, doc_id)
    get_storage().delete(d.enc_path)
    db.delete(d)
    audit.record(db, user.id, "document_deleted", doc_id=doc_id)
    db.commit()
    return ok({"deleted": True})
