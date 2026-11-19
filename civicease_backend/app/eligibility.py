"""Deterministic eligibility engine. Rules decide; the LLM only explains (pure module)."""
import operator

OPS = {
    "<=": operator.le, "<": operator.lt, ">=": operator.ge, ">": operator.gt,
    "==": operator.eq, "!=": operator.ne, "in": lambda a, b: a in b,
}


def evaluate(criteria: list, profile: dict) -> dict:
    """Each criterion: {id, label, field, op, value}. Missing data => 'unknown' (never a guess)."""
    results = []
    for c in criteria:
        actual = profile.get(c["field"])
        if actual is None:
            status = "unknown"
        else:
            try:
                status = "met" if OPS[c["op"]](actual, c["value"]) else "not_met"
            except (TypeError, KeyError):
                status = "unknown"
        results.append({"id": c["id"], "label": c["label"], "status": status})
    statuses = {r["status"] for r in results}
    if not results:
        overall = "unknown"
    elif "not_met" in statuses:
        overall = "not_met"
    elif "unknown" in statuses:
        overall = "unknown"
    else:
        overall = "likely_met"
    return {"overall": overall, "criteria": results, "preliminary_estimate": True}
