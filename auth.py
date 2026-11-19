from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import audit
from app.config import get_settings
from app.deps import auth_rate_limit, current_user, get_db, rate_limit
from app.errors import ApiError, ok
from app.models import Application, AuditEvent, Consent, Document, Profile, User, utcnow
from app.routers import applications as app_router
from app.routers import documents as doc_router
from app.schemas import LoginIn, PinIn, RegisterIn
from app.security import create_access_token, hash_password, new_salt, verify_password
from app.storage import get_storage

router = APIRouter(tags=["auth"])
PIN_MAX_FAILURES, PIN_LOCK_MINUTES = 5, 15


def _token(user: User) -> dict:
    s = get_settings()
    return {"access_token": create_access_token(user.id, s.jwt_secret, s.jwt_expire_minutes), "token_type": "bearer",
            "role": user.role}


@router.post("/auth/register", dependencies=[Depends(auth_rate_limit)])
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    if db.execute(select(User).where(User.email == email)).scalar_one_or_none():
        raise ApiError(409, "EMAIL_TAKEN", "An account with this email already exists.")
    role = "reviewer" if email in get_settings().reviewer_emails else "citizen"
    user = User(email=email, password_hash=hash_password(body.password), id_salt=new_salt(), role=role)
    db.add(user)
    db.flush()
    audit.record(db, user.id, "user_registered", role=role)
    db.commit()
    return ok(_token(user))


@router.post("/auth/login", dependencies=[Depends(auth_rate_limit)])
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == body.email.strip().lower())).scalar_one_or_none()
    if not user or not verify_password(user.password_hash, body.password):
        raise ApiError(401, "BAD_CREDENTIALS", "Email or password is incorrect.")
    audit.record(db, user.id, "login")
    db.commit()
    return ok(_token(user))


@router.get("/auth/me")
def me(user: User = Depends(current_user)):
    return ok({"id": user.id, "email": user.email, "role": user.role, "has_pin": user.pin_hash is not None})


@router.put("/auth/pin", dependencies=[Depends(rate_limit)])
def set_pin(body: PinIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """App-lock PIN, stored with Argon2id."""
    user.pin_hash, user.pin_failures, user.pin_locked_until = hash_password(body.pin), 0, None
    audit.record(db, user.id, "pin_set")
    db.commit()
    return ok({"has_pin": True})


@router.post("/auth/pin/verify", dependencies=[Depends(auth_rate_limit)])
def verify_pin(body: PinIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not user.pin_hash:
        raise ApiError(409, "NO_PIN", "No app-lock PIN is set.")
    if user.pin_locked_until and user.pin_locked_until > utcnow():
        raise ApiError(429, "PIN_LOCKED", "Too many wrong PINs. Try again later.")
    if verify_password(user.pin_hash, body.pin):
        user.pin_failures, user.pin_locked_until = 0, None
        db.commit()
        return ok({"unlocked": True})
    user.pin_failures += 1
    if user.pin_failures >= PIN_MAX_FAILURES:
        user.pin_locked_until, user.pin_failures = utcnow() + timedelta(minutes=PIN_LOCK_MINUTES), 0
        audit.record(db, user.id, "pin_locked")
    db.commit()
    raise ApiError(401, "BAD_PIN", "Incorrect PIN.")


@router.get("/me/export", dependencies=[Depends(rate_limit)])
def export_my_data(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Right of access: everything held about the citizen, in one response."""
    p = db.get(Profile, user.id)
    consents = {c.kind: c.granted for c in db.execute(select(Consent).where(Consent.user_id == user.id)).scalars()}
    docs = [doc_router._view(d) | {"fields": d.extracted, "findings": d.audit}
            for d in db.execute(select(Document).where(Document.user_id == user.id)).scalars()]
    apps = [app_router._view(a, db) for a in db.execute(select(Application).where(Application.user_id == user.id)).scalars()]
    events = [{"ts": e.ts, "action": e.action} for e in
              db.execute(select(AuditEvent).where(AuditEvent.actor == user.id).order_by(AuditEvent.id)).scalars()]
    audit.record(db, user.id, "data_exported")
    db.commit()
    return ok({"email": user.email, "consents": consents, "profile": ({"language": p.language, **p.data} if p else None),
               "documents": docs, "applications": apps, "activity": events})


@router.delete("/me", dependencies=[Depends(rate_limit)])
def delete_account(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Delete-on-request: account, profile, consents, applications, documents and encrypted files.
    Audit entries stay (pseudonymous ids only, no PII) so the hash chain remains verifiable."""
    get_storage().delete_prefix(f"{user.id}/")
    for model in (Document, Application, Consent):
        db.execute(delete(model).where(model.user_id == user.id))
    db.execute(delete(Profile).where(Profile.user_id == user.id))
    audit.record(db, user.id, "account_deleted")
    db.delete(user)
    db.commit()
    return ok({"deleted": True})
