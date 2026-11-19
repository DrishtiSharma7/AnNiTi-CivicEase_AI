from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import audit, eligibility, profile_parse, retrieval, trust
from app.agents import discovery, orchestrator
from app.deps import current_user, get_db, has_consent, rate_limit, require_consent
from app.errors import ApiError, ok
from app.models import Profile, Scheme, User
from app.schemas import ChatIn, ProfileAnswerIn
from app.seed import PACKS
from app.skills import load_skill

router = APIRouter(dependencies=[Depends(rate_limit)], tags=["schemes", "agents"])


def _public(s: Scheme) -> dict:
    return {"id": s.id, "name": s.name, "pack": s.pack, "benefit": s.benefit, "state": s.state, "deadline": s.deadline,
            "source_url": s.source_url, "last_verified": s.last_verified,
            "verification_status": "verified" if s.last_verified else "unverified_seed", "rule_status": s.rule_status,
            "required_documents": s.required_documents}


@router.get("/schemes/packs")
def packs():
    return ok(PACKS)


@router.get("/schemes")
def list_schemes(state: Optional[str] = None, pack: Optional[str] = None, q: Optional[str] = None,
                 db: Session = Depends(get_db)):
    """q = semantic search over the RAG store. Similarity finds candidates; it does not prove eligibility."""
    if q:
        hits = retrieval.search(db, q[:200])
        return ok({"results": [{**_public(s), "match_score": round(sc, 3)} for s, sc in hits],
                   "note": "Match score shows topical similarity only, not eligibility."})
    stmt = select(Scheme)
    if pack:
        stmt = stmt.where(Scheme.pack == pack)
    if state:
        stmt = stmt.where(Scheme.state.in_([state.upper(), "ALL"]))
    return ok({"results": [_public(s) for s in db.execute(stmt).scalars()]})


@router.get("/schemes/{scheme_id}")
def get_scheme(scheme_id: str, db: Session = Depends(get_db)):
    s = db.get(Scheme, scheme_id)
    if not s:
        raise ApiError(404, "NOT_FOUND", "Scheme not found.")
    return ok(_public(s))


@router.get("/agents/profile/next")
def profile_next(user: User = Depends(require_consent("profile")), db: Session = Depends(get_db)):
    """Profile agent: one short question at a time, with a 'why am I asked this?' text."""
    p = db.get(Profile, user.id)
    q = profile_parse.next_question(p.data if p else {}, p.language if p else "en")
    return ok(q or {"done": True})


@router.post("/agents/profile/answer")
def profile_answer(body: ProfileAnswerIn, user: User = Depends(require_consent("profile")),
                   db: Session = Depends(get_db)):
    p = db.get(Profile, user.id)
    if not p:
        p = Profile(user_id=user.id, data={}, language="en")
        db.add(p)
    try:
        p.data = profile_parse.apply_answer(p.data, body.field, body.answer)
    except KeyError:
        raise ApiError(422, "UNKNOWN_FIELD", "That question is not part of the profile.")
    except ValueError:
        raise ApiError(422, "ANSWER_NOT_UNDERSTOOD", "I did not understand that. Please answer again.")  # never guess
    audit.record(db, user.id, "profile_answered", field=body.field)  # field name only
    db.commit()
    return ok(profile_parse.next_question(p.data, p.language) or {"done": True})


@router.post("/agents/chat")
def chat(body: ChatIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = db.get(Profile, user.id)
    out = orchestrator.handle(db, user, p.data if p else {}, has_consent(db, user.id, "profile"), body.message, body.language)
    audit.record(db, user.id, "agent_routed", agent=out["result"]["agent"])
    db.commit()
    return ok(out)


@router.get("/agents/discover")
def discover(user: User = Depends(require_consent("profile")), db: Session = Depends(get_db)):
    p = db.get(Profile, user.id)
    if not p or not p.data:
        raise ApiError(422, "PROFILE_INCOMPLETE", "Complete your profile first.")
    return ok(trust.guard(discovery.run(db, p.data, p.language), "scheme_match"))


@router.get("/agents/eligibility/{scheme_id}")
def check_eligibility(scheme_id: str, user: User = Depends(require_consent("profile")), db: Session = Depends(get_db)):
    s, p = db.get(Scheme, scheme_id), db.get(Profile, user.id)
    if not s:
        raise ApiError(404, "NOT_FOUND", "Scheme not found.")
    load_skill("eligibility-router")
    if s.skill:
        load_skill(s.skill)
    verdict = eligibility.evaluate(s.criteria, p.data if p else {})
    card = discovery.card(s, verdict, p.language if p else "en")
    return ok(trust.guard(card, "eligibility"))
