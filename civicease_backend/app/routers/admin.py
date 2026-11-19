"""Reviewer-only endpoints (least privilege): the rule-pack pipeline and the human-review queue."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import audit, llm, retrieval, rules
from app.config import get_settings
from app.deps import get_db, rate_limit, require_role
from app.errors import ApiError, ok
from app.models import Document, RulePack, Scheme, User
from app.schemas import IngestIn, ReviewNoteIn
from app.security import sha256_hex
from app.seed import PACKS

router = APIRouter(prefix="/admin", dependencies=[Depends(rate_limit)], tags=["admin"])
reviewer = require_role("reviewer")


def _view(rp: RulePack) -> dict:
    return {"id": rp.id, "scheme_id": rp.scheme_id, "pack": rp.pack, "source_url": rp.source_url, "status": rp.status,
            "draft": rp.draft, "created_by": rp.created_by, "reviewed_by": rp.reviewed_by, "review_note": rp.review_note}


@router.post("/rulepacks/ingest")
def ingest(body: IngestIn, user: User = Depends(reviewer), db: Session = Depends(get_db)):
    """Steps 1-2: ingest an official source, extract a DRAFT rule pack. Nothing is published yet."""
    s = get_settings()
    if not rules.is_official_url(body.source_url, s.official_suffixes):
        raise ApiError(422, "NOT_OFFICIAL_SOURCE", "Source must be an https page on an official government domain.")
    if body.pack not in PACKS:
        raise ApiError(422, "UNKNOWN_PACK", f"Pack must be one of: {', '.join(PACKS)}")
    try:
        draft = llm.extract_rules(body.text)
    except llm.LLMUnavailable:
        raise ApiError(502, "EXTRACTION_UNAVAILABLE", "Rule extraction is unavailable right now.")
    errors = rules.validate_draft(draft)
    if errors:
        raise ApiError(422, "DRAFT_INVALID", "; ".join(errors))
    rp = RulePack(scheme_id=body.scheme_id, pack=body.pack, source_url=body.source_url,
                  source_sha256=sha256_hex(body.text.encode()), draft=draft, created_by=user.id)
    db.add(rp)
    db.flush()
    audit.record(db, user.id, "rulepack_drafted", rulepack_id=rp.id, scheme_id=body.scheme_id, source_url=body.source_url)
    db.commit()
    return ok(_view(rp))


@router.get("/rulepacks")
def list_rulepacks(user: User = Depends(reviewer), db: Session = Depends(get_db)):
    return ok([_view(r) for r in db.execute(select(RulePack).order_by(RulePack.created_at.desc())).scalars()])


@router.post("/rulepacks/{rp_id}/approve")
def approve(rp_id: str, body: ReviewNoteIn, user: User = Depends(reviewer), db: Session = Depends(get_db)):
    """Steps 3-4: a HUMAN reviewer approves; the rule pack is published with its citation and verification date."""
    rp = db.get(RulePack, rp_id)
    if not rp or rp.status != "draft":
        raise ApiError(404, "NOT_FOUND", "No draft rule pack with this id.")
    if rp.created_by == user.id and not get_settings().allow_self_approve:
        raise ApiError(403, "FOUR_EYES", "A different reviewer must approve this rule pack.")
    d = rp.draft
    scheme = db.get(Scheme, rp.scheme_id) or Scheme(id=rp.scheme_id)
    scheme.name, scheme.benefit, scheme.state = d["name"], d.get("benefit", ""), d.get("state", "ALL")
    scheme.deadline, scheme.criteria = d.get("deadline"), d["criteria"]
    scheme.required_documents = d.get("required_documents") or ["aadhaar"]
    scheme.pack, scheme.source_url = rp.pack, rp.source_url
    scheme.last_verified, scheme.rule_status = date.today().isoformat(), "reviewed"
    db.add(scheme)
    db.flush()
    retrieval.index_scheme(db, scheme)
    rp.status, rp.reviewed_by, rp.review_note = "published", user.id, body.note
    audit.record(db, user.id, "rulepack_published", rulepack_id=rp.id, scheme_id=scheme.id, last_verified=scheme.last_verified)
    db.commit()
    return ok(_view(rp))


@router.post("/rulepacks/{rp_id}/reject")
def reject(rp_id: str, body: ReviewNoteIn, user: User = Depends(reviewer), db: Session = Depends(get_db)):
    rp = db.get(RulePack, rp_id)
    if not rp or rp.status != "draft":
        raise ApiError(404, "NOT_FOUND", "No draft rule pack with this id.")
    rp.status, rp.reviewed_by, rp.review_note = "rejected", user.id, body.note
    audit.record(db, user.id, "rulepack_rejected", rulepack_id=rp.id)
    db.commit()
    return ok(_view(rp))


@router.get("/review-queue")
def review_queue(user: User = Depends(reviewer), db: Session = Depends(get_db)):
    """Documents the citizen asked a human to look at. Metadata only: no content, no identity."""
    rows = db.execute(select(Document).where(Document.human_review == "requested")).scalars()
    return ok([{"document_id": d.id, "doc_type": d.doc_type, "quality": d.quality, "confidence": d.confidence,
                "issues": [f["code"] for f in (d.audit or []) if f["severity"] in ("blocking", "unknown")]} for d in rows])


@router.post("/review-queue/{doc_id}/resolve")
def resolve(doc_id: str, body: ReviewNoteIn, user: User = Depends(reviewer), db: Session = Depends(get_db)):
    d = db.get(Document, doc_id)
    if not d or d.human_review != "requested":
        raise ApiError(404, "NOT_FOUND", "No open review request with this id.")
    d.human_review, d.review_note = "resolved", body.note
    audit.record(db, user.id, "human_review_resolved", doc_id=d.id)
    db.commit()
    return ok({"document_id": d.id, "human_review": "resolved"})
