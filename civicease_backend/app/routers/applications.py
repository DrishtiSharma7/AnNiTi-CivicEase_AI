"""Application preparation with the five human gates:
1 profile consent | 2 document-use consent | 3 approve readiness report |
4 citizen does login/OTP/CAPTCHA | 5 citizen performs FINAL SUBMIT (signed approval token)."""
from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import audit, docaudit, telemetry, trust
from app.agents import app_prep, browser_action, notification
from app.config import get_settings
from app.deps import current_user, get_db, has_consent, rate_limit, require_consent
from app.errors import ApiError, ok
from app.models import Application, Document, Profile, Scheme, User, utcnow
from app.pdfgen import build_pdf
from app.portal import PortalViolation
from app.schemas import ApplicationIn, ConfirmIn, FormPatchIn, StatusIn, SubmitIn
from app.security import derive_key, sign_payload, verify_payload

router = APIRouter(dependencies=[Depends(rate_limit)], tags=["applications"])


def _own(db: Session, user: User, app_id: str) -> Application:
    a = db.get(Application, app_id)
    if not a or a.user_id != user.id:
        raise ApiError(404, "NOT_FOUND", "Application not found.")
    return a


def _view(a: Application, db: Session) -> dict:
    return {
        "id": a.id, "scheme_id": a.scheme_id, "status": a.status, "readiness": a.readiness,
        "form": a.form_data, "form_hash": a.form_hash, "notes": a.notes,
        "gates": {"1_profile_consent": has_consent(db, a.user_id, "profile"),
                  "2_document_consent": has_consent(db, a.user_id, "document_use"),
                  "3_readiness_approved": a.gate3_at is not None,
                  "4_login_otp_captcha_done_by_citizen": a.gate4_at is not None,
                  "5_final_submit_by_citizen": a.submitted_at is not None},
        "timeline": ["draft", "ready", "prepared", "submitted"],
    }


def _need(cond: bool, code: str, msg: str):
    if not cond:
        raise ApiError(409, code, msg)


def _reset_after_form_change(a: Application):
    a.gate4_at, a.prefill_log = None, None


@router.post("/applications")
def create(body: ApplicationIn, user: User = Depends(require_consent("profile")), db: Session = Depends(get_db)):
    if not db.get(Scheme, body.scheme_id):
        raise ApiError(404, "NOT_FOUND", "Scheme not found.")
    a = Application(user_id=user.id, scheme_id=body.scheme_id)
    db.add(a)
    db.flush()
    audit.record(db, user.id, "application_created", application_id=a.id, scheme_id=body.scheme_id)
    db.commit()
    return ok(_view(a, db))


@router.get("/applications")
def list_apps(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return ok([_view(a, db) for a in db.execute(select(Application).where(Application.user_id == user.id)).scalars()])


@router.get("/applications/{app_id}")
def get_app(app_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return ok(_view(_own(db, user, app_id), db))


@router.post("/applications/{app_id}/readiness")
def readiness(app_id: str, user: User = Depends(require_consent("document_use")), db: Session = Depends(get_db)):
    a = _own(db, user, app_id)
    scheme = db.get(Scheme, a.scheme_id)
    docs = db.execute(select(Document).where(Document.user_id == user.id)).scalars().all()
    pending = [d.id for d in docs if d.audit is None]
    _need(not pending, "DOCUMENTS_NOT_AUDITED", f"Audit these documents first: {', '.join(pending)}")
    p = db.get(Profile, user.id)
    report = docaudit.build_readiness(
        scheme.required_documents,
        [{"id": d.id, "doc_type": d.doc_type, "fields": d.extracted or {}, "confidence": d.confidence, "quality": d.quality}
         for d in docs],
        p.data if p else {}, date.today())
    report = trust.guard(report, "readiness")  # Trust & Compliance guard around every agent output
    if report.get("status") == "blocked_by_trust_guard":
        raise ApiError(502, "TRUST_GUARD", "The report was withheld by the compliance guard.")
    a.readiness, a.gate3_at = report, None  # any new report must be approved again
    audit.record(db, user.id, "readiness_computed", application_id=a.id, ready=report["ready"],
                 blocking=len(report["blocking"]), warnings=len(report["warning"]))
    db.commit()
    return ok(report)


@router.post("/applications/{app_id}/gates/3/approve")
def approve_readiness(app_id: str, body: ConfirmIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = _own(db, user, app_id)
    _need(body.confirm, "CONFIRMATION_REQUIRED", "Set confirm=true to approve the readiness report.")
    _need(a.readiness is not None, "NO_READINESS_REPORT", "Generate the readiness report first.")
    _need(a.readiness["ready"], "NOT_READY", "Fix the blocking or unknown items before approving.")
    a.gate3_at, a.status = utcnow(), "ready"
    audit.record(db, user.id, "gate3_readiness_approved", application_id=a.id, gate=3)
    telemetry.emit("human_gate", gate=3, state="passed")
    db.commit()
    return ok(_view(a, db))


@router.post("/applications/{app_id}/prepare")
def prepare(app_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = _own(db, user, app_id)
    _need(a.gate3_at is not None, "GATE3_REQUIRED", "Approve the readiness report first (Gate 3).")
    docs = db.execute(select(Document).where(Document.user_id == user.id)).scalars().all()
    p, scheme = db.get(Profile, user.id), db.get(Scheme, a.scheme_id)
    a.form_data = app_prep.build_form(p.data if p else {}, docs)
    a.form_hash = app_prep.hash_of(a.form_data)
    _reset_after_form_change(a)
    a.status = "prepared"
    audit.record(db, user.id, "application_prepared", application_id=a.id, form_hash=a.form_hash)
    db.commit()
    return ok({"form": a.form_data, "form_hash": a.form_hash, "checklist": app_prep.checklist(scheme.required_documents, docs)})


@router.patch("/applications/{app_id}/form")
def edit_form(app_id: str, body: FormPatchIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = _own(db, user, app_id)
    _need(a.form_data is not None, "NOT_PREPARED", "Prepare the application first.")
    bad = [k for k in body.fields if k not in app_prep.FORM_FIELDS]
    if bad:
        raise ApiError(422, "UNKNOWN_FIELD", f"Unknown form fields: {', '.join(bad)}")
    a.form_data = {**a.form_data, **body.fields}
    a.form_hash = app_prep.hash_of(a.form_data)
    _reset_after_form_change(a)  # editing invalidates Gate 4 and any issued approval token
    audit.record(db, user.id, "form_edited", application_id=a.id, fields=sorted(body.fields), form_hash=a.form_hash)
    db.commit()
    return ok({"form": a.form_data, "form_hash": a.form_hash})


@router.post("/applications/{app_id}/prefill")
def prefill(app_id: str, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = _own(db, user, app_id)
    _need(a.gate3_at is not None and a.form_data is not None, "NOT_PREPARED", "Complete Gate 3 and prepare the form first.")
    try:
        a.prefill_log = browser_action.run(str(request.base_url).rstrip("/"), a.form_data)
    except RuntimeError:
        raise ApiError(502, "WORKER_UNAVAILABLE", "The browser worker is unavailable. Try again later.")
    except PortalViolation as e:
        audit.record(db, user.id, "browser_action_blocked", application_id=a.id, reason=str(e))
        db.commit()
        raise ApiError(403, "PORTAL_POLICY", f"Blocked by portal safety policy: {e}")
    audit.record(db, user.id, "browser_prefill_done", application_id=a.id, steps=len(a.prefill_log))
    db.commit()
    return ok({"log": a.prefill_log, "next": "Gate 4: log in and complete OTP/CAPTCHA yourself, then confirm."})


@router.post("/applications/{app_id}/gates/4/complete")
def gate4(app_id: str, body: ConfirmIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = _own(db, user, app_id)
    _need(body.confirm, "CONFIRMATION_REQUIRED", "Confirm that you completed login/OTP/CAPTCHA yourself.")
    _need(a.prefill_log is not None, "PREFILL_REQUIRED", "Run the assisted pre-fill first.")
    a.gate4_at = utcnow()
    audit.record(db, user.id, "gate4_citizen_login_done", application_id=a.id, gate=4)
    telemetry.emit("human_gate", gate=4, state="passed")
    db.commit()
    return ok(_view(a, db))


@router.post("/applications/{app_id}/approval-token")
def approval_token(app_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a, s = _own(db, user, app_id), get_settings()
    _need(a.gate3_at is not None and a.gate4_at is not None and a.form_hash, "GATES_INCOMPLETE",
          "Gates 3 and 4 must be completed first.")
    _need(has_consent(db, user.id, "profile") and has_consent(db, user.id, "document_use"), "CONSENT_REQUIRED",
          "Both consents must still be active.")
    token = sign_payload({"usr": user.id, "app": a.id, "fh": a.form_hash}, derive_key(s.pepper, "approval"), s.approval_ttl)
    audit.record(db, user.id, "approval_token_issued", application_id=a.id, form_hash=a.form_hash)
    db.commit()
    return ok({"approval_token": token, "expires_in": s.approval_ttl, "bound_to_form_hash": a.form_hash})


@router.post("/applications/{app_id}/submit")
def submit(app_id: str, body: SubmitIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Records Gate 5: the citizen's own final Submit. No token, no submit. The system never submits to a portal."""
    a, s = _own(db, user, app_id), get_settings()
    _need(body.confirm, "CONFIRMATION_REQUIRED", "Set confirm=true: you are submitting this application yourself.")
    claims = verify_payload(body.approval_token, derive_key(s.pepper, "approval"))
    if not claims or claims.get("usr") != user.id or claims.get("app") != a.id or claims.get("fh") != a.form_hash:
        raise ApiError(403, "APPROVAL_INVALID", "Approval token is invalid, expired, or the form changed after approval.")
    _need(a.submitted_at is None, "ALREADY_SUBMITTED", "This application was already marked as submitted.")
    a.submitted_at, a.status = utcnow(), "submitted"
    audit.record(db, user.id, "gate5_final_submit_by_citizen", application_id=a.id, form_hash=a.form_hash, gate=5)
    telemetry.emit("human_gate", gate=5, state="passed")
    db.commit()
    return ok({"status": "submitted", "message": "Recorded as submitted by you. CivicEase never submits on your behalf."})


@router.post("/applications/{app_id}/status")
def add_status(app_id: str, body: StatusIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Citizen-entered status update (official status feeds only where an official API exists)."""
    a = _own(db, user, app_id)
    _need(a.submitted_at is not None, "NOT_SUBMITTED", "Status updates start after submission.")
    a.notes = [*a.notes, {"status": body.status, "note": body.note, "source": "citizen", "at": utcnow().isoformat()}]
    audit.record(db, user.id, "status_note_added", application_id=a.id, status=body.status)
    db.commit()
    return ok(_view(a, db))


@router.get("/notifications")
def notifications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return ok(notification.run(db, user.id))


@router.get("/applications/{app_id}/checklist.pdf")
def checklist_pdf(app_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Offline checklist PDF (works without a connection once downloaded)."""
    a = _own(db, user, app_id)
    scheme = db.get(Scheme, a.scheme_id)
    have = {d.doc_type for d in db.execute(select(Document).where(Document.user_id == user.id)).scalars()}
    lines = ["CivicEase AI - Application checklist", "", f"Scheme: {scheme.name}", f"Source: {scheme.source_url}",
             f"Last verified: {scheme.last_verified or 'NOT VERIFIED (illustrative seed)'}", "", "Documents to carry:"]
    lines += [f"[{'x' if t in have else ' '}] {t.replace('_', ' ')}" for t in scheme.required_documents]
    if a.readiness:
        todo = a.readiness["blocking"] + a.readiness["unknown"] + a.readiness["warning"]
        if todo:
            lines += ["", "Fix before you apply:"] + [f"- {f['message']} Fix: {f['fix']}" for f in todo]
    lines += ["", "This is a preliminary checklist. It does not guarantee acceptance of your application.",
              "You log in, complete OTP/CAPTCHA and press Submit yourself."]
    return Response(build_pdf(lines), media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="checklist.pdf"', "Cache-Control": "no-store"})
