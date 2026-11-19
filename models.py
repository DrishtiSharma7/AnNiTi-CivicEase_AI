from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def uid() -> str:
    return uuid4().hex


def utcnow() -> datetime:
    """Naive UTC, so SQLite and Postgres behave the same."""
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    id_salt: Mapped[str] = mapped_column(String(64))  # per-user salt for HMAC ID digests
    role: Mapped[str] = mapped_column(String(12), default="citizen")  # citizen | reviewer (least privilege)
    pin_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Argon2id app-lock PIN
    pin_failures: Mapped[int] = mapped_column(Integer, default=0)
    pin_locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Consent(Base):
    __tablename__ = "consents"
    __table_args__ = (UniqueConstraint("user_id", "kind"),)
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(20))  # profile | document_use
    granted: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Profile(Base):
    __tablename__ = "profiles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    language: Mapped[str] = mapped_column(String(10), default="en")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Scheme(Base):
    __tablename__ = "schemes"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    benefit: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(40), default="ALL")
    deadline: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    source_url: Mapped[str] = mapped_column(String(300))
    last_verified: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # set by a human reviewer
    criteria: Mapped[list] = mapped_column(JSON, default=list)
    required_documents: Mapped[list] = mapped_column(JSON, default=list)
    skill: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    pack: Mapped[str] = mapped_column(String(40), default="Central schemes")  # rule pack
    rule_status: Mapped[str] = mapped_column(String(20), default="illustrative_seed")  # illustrative_seed | reviewed
    embedding: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # RAG vector (portable copy)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(100))
    mime: Mapped[str] = mapped_column(String(40))
    size: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    enc_path: Mapped[str] = mapped_column(String(300))
    wrapped_key: Mapped[str] = mapped_column(Text)
    doc_type: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    extracted: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # ID numbers already masked
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    id_masked: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    id_digest: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    audit: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # cached findings, keyed by sha256
    field_confidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    human_review: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)  # requested | resolved
    review_note: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    scheme_id: Mapped[str] = mapped_column(ForeignKey("schemes.id"))
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft|ready|prepared|submitted
    readiness: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    gate3_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    form_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    form_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    prefill_log: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    gate4_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[list] = mapped_column(JSON, default=list)  # citizen-entered status updates
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[str] = mapped_column(String(32))
    actor: Mapped[str] = mapped_column(String(40), index=True)
    action: Mapped[str] = mapped_column(String(60))
    detail: Mapped[str] = mapped_column(Text)  # canonical JSON, PII-redacted
    prev_hash: Mapped[str] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64))


class RulePack(Base):
    """Pipeline: ingest official source -> extract rules -> human reviewer approves -> publish with citation."""
    __tablename__ = "rule_packs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    scheme_id: Mapped[str] = mapped_column(String(64))
    pack: Mapped[str] = mapped_column(String(40))
    source_url: Mapped[str] = mapped_column(String(300))
    source_sha256: Mapped[str] = mapped_column(String(64))
    draft: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(12), default="draft")  # draft | published | rejected
    created_by: Mapped[str] = mapped_column(String(32))
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    review_note: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class UsageCounter(Base):
    """Per-user daily model-call quota (free/limited quotas go far)."""
    __tablename__ = "usage_counters"
    user_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    day: Mapped[str] = mapped_column(String(10), primary_key=True)
    calls: Mapped[int] = mapped_column(Integer, default=0)
