from sqlalchemy import select

from app import eligibility, llm
from app.models import Scheme
from app.skills import load_skill

_RANK = {"likely_met": 0, "unknown": 1, "not_met": 2}


def card(scheme: Scheme, verdict: dict, language: str) -> dict:
    c = [r["status"] for r in verdict["criteria"]]
    return {
        "scheme_id": scheme.id, "name": scheme.name, "benefit": scheme.benefit, "deadline": scheme.deadline,
        "pack": scheme.pack, "source_url": scheme.source_url, "last_verified": scheme.last_verified,
        "verification_status": "verified" if scheme.last_verified else "unverified_seed", "rule_status": scheme.rule_status,
        "overall": verdict["overall"], "criteria": verdict["criteria"], "preliminary_estimate": True,
        "explanation": llm.explain(scheme.name, c.count("met"), c.count("unknown"), c.count("not_met"), language),
    }


def run(db, profile: dict, language: str) -> dict:
    load_skill("eligibility-router")
    cards = []
    for s in db.execute(select(Scheme)).scalars():
        v = eligibility.evaluate(s.criteria, profile)
        if v["overall"] != "not_met":  # hide schemes the citizen clearly does not qualify for
            cards.append((v["overall"], card(s, v, language)))
    cards.sort(key=lambda x: _RANK[x[0]])
    return {"schemes": [c for _, c in cards]}
