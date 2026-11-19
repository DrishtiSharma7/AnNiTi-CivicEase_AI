from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import trust
from app.agents import discovery, notification
from app.deps import current_user, get_db, has_consent, rate_limit
from app.errors import ok
from app.models import Application, Document, Profile, User

router = APIRouter(dependencies=[Depends(rate_limit)], tags=["dashboard"])


@router.get("/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Home screen: recommended schemes, documents needing attention, next deadline, applications in progress."""
    p = db.get(Profile, user.id)
    recommended = []
    if p and p.data and has_consent(db, user.id, "profile"):
        recommended = trust.guard(discovery.run(db, p.data, p.language), "scheme_match").get("schemes", [])[:3]
    attention = []
    for d in db.execute(select(Document).where(Document.user_id == user.id)).scalars():
        issues = [f["code"] for f in (d.audit or []) if f["severity"] in ("blocking", "unknown")]
        if issues or d.audit is None:
            attention.append({"document_id": d.id, "doc_type": d.doc_type, "issues": issues or ["NOT_AUDITED_YET"]})
    n = notification.run(db, user.id)
    apps = db.execute(select(Application).where(Application.user_id == user.id, Application.status != "submitted")).scalars()
    return ok({"language": p.language if p else "en", "recommended_schemes": recommended,
               "documents_needing_attention": attention, "next_deadline": n["next_deadline"],
               "reminders": n["reminders"],
               "applications_in_progress": [{"id": a.id, "scheme_id": a.scheme_id, "status": a.status} for a in apps]})
