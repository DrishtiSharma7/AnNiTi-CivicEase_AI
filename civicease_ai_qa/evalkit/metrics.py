"""Metrics with pandas/numpy: field accuracy, hallucination, doc-type accuracy, finding precision/recall,
name-mismatch and expiry detection, confidence calibration (ECE), per-condition breakdown."""
from datetime import date

import numpy as np
import pandas as pd

import qa_config  # noqa: F401
from app import docaudit

FIELDS_BY_TYPE = {"aadhaar": ["name", "dob", "id_last4"], "income_certificate": ["name", "annual_income", "valid_until"],
                  "marksheet": ["name", "institution"]}
MONITORED = ["EXPIRED", "EXPIRING_SOON", "NAME_MISMATCH", "MISSING_FIELD", "QUALITY_BLURRY", "QUALITY_CROPPED",
             "LOW_CONFIDENCE", "DOC_TYPE_UNKNOWN"]
DEGRADED = {"blurry", "cropped", "lowres"}


def _blank(v) -> bool:
    return v is None or v == "" or (isinstance(v, float) and np.isnan(v))


def norm(field: str, v):
    if _blank(v):
        return None
    if field == "annual_income":
        try:
            return int(float(str(v).replace(",", "")))
        except ValueError:
            return str(v)
    if field == "id_last4":
        d = "".join(ch for ch in str(v) if ch.isdigit())
        return d[-4:] if d else None
    return " ".join(str(v).split()).casefold()  # strict: punctuation kept, so "Ram. Kumar" != "Ramesh Kumar"


def pred_value(pred: dict, field: str):
    f = pred.get("fields") or {}
    return f.get("id_number") if field == "id_last4" else f.get(field)


def field_results(labels: pd.DataFrame, preds: dict) -> pd.DataFrame:
    rows = []
    for _, r in labels.iterrows():
        p = preds.get(r["doc_id"])
        if p is None:
            continue
        for field in FIELDS_BY_TYPE[r["doc_type"]]:
            exp, got = norm(field, r.get(field)), norm(field, pred_value(p, field))
            if exp is None and got is None:
                status = "absent_ok"
            elif exp is None:
                status = "hallucinated"
            elif got is None:
                status = "missing"
            else:
                status = "correct" if exp == got else "wrong"
            conf = (p.get("field_confidence") or {}).get(field, p.get("confidence", 0.0))
            rows.append({"doc_id": r["doc_id"], "doc_type": r["doc_type"], "condition": r["condition"], "field": field,
                         "expected": exp, "predicted": got, "status": status, "confidence": float(conf or 0.0)})
    return pd.DataFrame(rows)


def ece(df: pd.DataFrame, bins: int = 10) -> float:
    """Expected calibration error over predicted values: confidence should match how often they are right."""
    d = df[df["predicted"].notna()]
    if d.empty:
        return 0.0
    conf, ok = d["confidence"].to_numpy(float), (d["status"] == "correct").to_numpy(float)
    idx = np.minimum((conf * bins).astype(int), bins - 1)
    total = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(conf[m].mean() - ok[m].mean())
    return float(total)


def summarize_fields(fr: pd.DataFrame, labels: pd.DataFrame, preds: dict) -> dict:
    present = fr[fr["status"].isin(["correct", "wrong", "missing"])]
    absent = fr[fr["status"].isin(["absent_ok", "hallucinated"])]
    acc = lambda d: float((d["status"] == "correct").mean()) if len(d) else float("nan")
    dt = [preds[r["doc_id"]].get("doc_type") == r["doc_type"] for _, r in labels.iterrows() if r["doc_id"] in preds]
    unk = [(preds[i].get("doc_type") == "unknown") or float(preds[i].get("confidence") or 0) < docaudit.MIN_CONFIDENCE
           for i in preds]
    return {
        "documents": int(len(preds)), "field_accuracy": acc(present), "missing_rate": float((present["status"] == "missing").mean()) if len(present) else 0.0,
        "wrong_rate": float((present["status"] == "wrong").mean()) if len(present) else 0.0,
        "hallucination_rate": float((absent["status"] == "hallucinated").mean()) if len(absent) else 0.0,
        "doc_type_accuracy": float(np.mean(dt)) if dt else float("nan"), "unknown_rate": float(np.mean(unk)) if unk else 0.0,
        "ece": ece(fr),
        "accuracy_by_field": {k: acc(g) for k, g in present.groupby("field")},
        "accuracy_by_condition": {k: acc(g) for k, g in present.groupby("condition")},
        "accuracy_by_doc_type": {k: acc(g) for k, g in present.groupby("doc_type")},
    }


def predicted_findings(labels: pd.DataFrame, preds: dict, today: date) -> pd.DataFrame:
    """Runs the backend's deterministic checks on the PREDICTED fields (the same code the product runs)."""
    docs, out = {}, []
    for _, r in labels.iterrows():
        p = preds.get(r["doc_id"])
        if p is None:
            continue
        docs[r["doc_id"]] = {"id": r["doc_id"], "doc_type": p.get("doc_type"), "fields": dict(p.get("fields") or {}),
                             "confidence": p.get("confidence"), "quality": p.get("quality")}
    for d in docs.values():
        out += [(d["id"], f["code"]) for f in docaudit.check_document(d, today)]
    for pid, g in labels.groupby("person_id"):
        grp = [docs[i] for i in g["doc_id"] if i in docs]
        out += [(f["doc_id"], f["code"]) for f in docaudit.cross_check_names(grp) if f["doc_id"]]
    return pd.DataFrame(out, columns=["doc_id", "code"]).drop_duplicates()


def finding_metrics(labels: pd.DataFrame, found: pd.DataFrame) -> tuple:
    exp = {(r["doc_id"], c) for _, r in labels.iterrows() for c in str(r["expected_findings"]).split("|") if c and c != "nan"}
    cond = dict(zip(labels["doc_id"], labels["condition"]))
    got = {(r.doc_id, r.code) for r in found.itertuples() if r.code in MONITORED}
    got = {(d, c) for d, c in got if not (c in ("LOW_CONFIDENCE", "DOC_TYPE_UNKNOWN") and cond.get(d) in DEGRADED)}
    rows = []
    for code in MONITORED:
        tp = len({x for x in exp & got if x[1] == code})
        fp = len({x for x in got - exp if x[1] == code})
        fn = len({x for x in exp - got if x[1] == code})
        p, r = (tp / (tp + fp) if tp + fp else float("nan")), (tp / (tp + fn) if tp + fn else float("nan"))
        f1 = 2 * p * r / (p + r) if tp and p == p and r == r and (p + r) else (0.0 if tp + fp + fn else float("nan"))
        rows.append({"code": code, "tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": r, "f1": f1})
    t = pd.DataFrame(rows)
    get = lambda c, k: float(t.loc[t["code"] == c, k].iloc[0])
    summary = {"name_mismatch_precision": get("NAME_MISMATCH", "precision"), "name_mismatch_recall": get("NAME_MISMATCH", "recall"),
               "expiry_recall": get("EXPIRED", "recall"), "expiry_precision": get("EXPIRED", "precision"),
               "missing_field_recall": get("MISSING_FIELD", "recall")}
    return t, summary


def gates(metrics: dict, th: dict) -> list:
    spec = [("field_accuracy", ">=", "field_accuracy_min"), ("doc_type_accuracy", ">=", "doc_type_accuracy_min"),
            ("hallucination_rate", "<=", "hallucination_rate_max"), ("name_mismatch_recall", ">=", "name_mismatch_recall_min"),
            ("name_mismatch_precision", ">=", "name_mismatch_precision_min"), ("expiry_recall", ">=", "expiry_recall_min"),
            ("ece", "<=", "ece_max")]
    out = []
    for m, op, key in spec:
        v = metrics.get(m)
        passed = v is not None and v == v and (v >= th[key] if op == ">=" else v <= th[key])
        out.append({"metric": m, "value": v, "rule": f"{op} {th[key]}", "pass": bool(passed)})
    return out
