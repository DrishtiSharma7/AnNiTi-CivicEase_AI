from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import SessionLocal
from app.errors import ApiError
from app.models import Consent, User
from app.ratelimit import get_limiter
from app.security import decode_access_token

bearer = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    if not get_limiter().allow(f"api:{ip}", get_settings().rate_limit_per_minute):
        raise ApiError(429, "RATE_LIMITED", "Too many requests. Please slow down.")


def auth_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    if not get_limiter().allow(f"auth:{ip}", get_settings().auth_rate_limit_per_minute):
        raise ApiError(429, "RATE_LIMITED", "Too many attempts. Please wait a minute.")


def current_user(cred: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not cred:
        raise ApiError(401, "UNAUTHENTICATED", "Sign in to continue.")
    sub = decode_access_token(cred.credentials, get_settings().jwt_secret)
    user = db.get(User, sub) if sub else None
    if not user:
        raise ApiError(401, "UNAUTHENTICATED", "Your session is invalid or expired.")
    return user


def has_consent(db: Session, user_id: str, kind: str) -> bool:
    c = db.execute(select(Consent).where(Consent.user_id == user_id, Consent.kind == kind)).scalar_one_or_none()
    return bool(c and c.granted)


def require_consent(kind: str):
    """Gate 1 (profile) and Gate 2 (document_use): no consent, no processing."""
    def dep(user: User = Depends(current_user), db: Session = Depends(get_db)) -> User:
        if not has_consent(db, user.id, kind):
            raise ApiError(403, "CONSENT_REQUIRED", f"Consent '{kind}' is required before this step.")
        return user
    return dep


def require_role(role: str):
    """Least privilege: reviewer-only endpoints (rule-pack approval, human-review queue)."""
    def dep(user: User = Depends(current_user)) -> User:
        if user.role != role:
            raise ApiError(403, "FORBIDDEN", "You do not have access to this resource.")
        return user
    return dep
