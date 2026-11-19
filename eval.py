"""Evaluation harness for the roadmap exit criteria:
 - 'Eligibility verdicts match manual labels on the test set'
 - 'Extraction/mismatch detection measured on a synthetic set'
Pure Python (no server needed). Run: python tools/eval.py   (exit code 1 if below the thresholds)"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import docaudit, eligibility  # noqa: E402
from app.seed import SCHEMES  # noqa: E402

THRESHOLD = 1.0  # synthetic set: every case must agree; lower it only with a written reason


def main() -> int:
    cases = json.loads((ROOT / "data" / "eval_cases.json").read_text())
    by_id = {s["id"]: s for s in SCHEMES}
    ok_e, rows = 0, []
    for c in cases["eligibility"]:
        got = eligibility.evaluate(by_id[c["scheme"]]["criteria"], c["profile"])["overall"]
        ok_e += got == c["expected"]
        rows.append(("eligibility", c["scheme"], c["expected"], got, got == c["expected"]))
    ok_d, today = 0, date.today()
    for c in cases["documents"]:
        docs = []
        for i, d in enumerate(c["docs"]):
            f = dict(d["fields"])
            if d["doc_type"] in c["offset_days"]:
                f["valid_until"] = (today + timedelta(days=c["offset_days"][d["doc_type"]])).isoformat()
            docs.append({"id": str(i), "doc_type": d["doc_type"], "fields": f, "confidence": 0.96, "quality": "clear"})
        r = docaudit.build_readiness(c["required"], docs, {}, today)
        got_codes = sorted({f["code"] for f in r["blocking"]})
        good = got_codes == sorted(c["expected_blocking"]) and r["ready"] == c["expected_ready"]
        ok_d += good
        rows.append(("documents", c["name"], c["expected_blocking"], got_codes, good))
    ne, nd = len(cases["eligibility"]), len(cases["documents"])
    for kind, name, exp, got, good in rows:
        print(f"{'PASS' if good else 'FAIL'}  {kind:12} {name}: expected {exp}, got {got}")
    print(f"\neligibility agreement: {ok_e}/{ne} = {ok_e / ne:.0%}")
    print(f"document-audit agreement: {ok_d}/{nd} = {ok_d / nd:.0%}")
    return 0 if min(ok_e / ne, ok_d / nd) >= THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())
