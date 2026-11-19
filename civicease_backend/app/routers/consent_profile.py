from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import audit, telemetry
from app.deps import current_user, get_db, has_consent, rate_limit, require_consent
from app.errors import ok
from app.models import Consent, Profile, User, utcnow
from app.routers.documents import purge_user_documents
from app.schemas import ConsentIn, ProfileIn

router = APIRouter(dependencies=[Depends(rate_limit)], tags=["consent", "profile"])


@router.get("/consents")
def list_consents(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return ok({k: has_consent(db, user.id, k) for k in ("profile", "document_use")})


@router.post("/consents")
def set_consent(body: ConsentIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.execute(select(Consent).where(Consent.user_id == user.id, Consent.kind == body.kind)).scalar_one_or_none()
    if row:
        row.granted, row.updated_at = body.granted, utcnow()
    else:
        db.add(Consent(user_id=user.id, kind=body.kind, granted=body.granted))
    gate = 1 if body.kind == "profile" else 2
    if not body.granted:  # withdrawing consent stops processing and removes the data it covered
        if body.kind == "document_use":
            purge_user_documents(db, user.id)
        elif db.get(Profile, user.id):
            db.delete(db.get(Profile, user.id))
    audit.record(db, user.id, "consent_granted" if body.granted else "consent_revoked", kind=body.kind, gate=gate)
    telemetry.emit("human_gate", gate=gate, state="passed" if body.granted else "revoked", kind=body.kind)
    db.commit()
    return ok({"kind": body.kind, "granted": body.granted,
               "data_removed": (not body.granted)})


@router.get("/profile")
def get_profile(user: User = Depends(require_consent("profile")), db: Session = Depends(get_db)):
    p = db.get(Profile, user.id)
    return ok({"language": p.language, **p.data} if p else {})


@router.put("/profile")
def put_profile(body: ProfileIn, user: User = Depends(require_consent("profile")), db: Session = Depends(get_db)):
    data = body.model_dump(exclude={"language"}, exclude_none=True)
    p = db.get(Profile, user.id)
    if p:
        p.data, p.language, p.updated_at = data, body.language, utcnow()
    else:
        db.add(Profile(user_id=user.id, data=data, language=body.language))
    audit.record(db, user.id, "profile_updated", fields=sorted(data))  # field names only, never values
    db.commit()
    return ok({"language": body.language, **data})
