"""Eligibility agreement against hand-labelled cases (the roadmap's 'verdicts match manual labels' exit criterion).
  python run_eligibility_eval.py"""
import json
import sys

import pandas as pd

import qa_config as qc
from evalkit import report


def run(quiet=False):
    from app import eligibility
    from app.seed import SCHEMES
    crit = {s["id"]: s["criteria"] for s in SCHEMES}
    cases = pd.read_csv(qc.DATA / "eligibility_cases.csv", dtype=str, keep_default_na=False)
    got = [eligibility.evaluate(crit[r.scheme_id], json.loads(r.profile_json))["overall"] for r in cases.itertuples()]
    cases["got"] = got
    cases["agree"] = cases["got"] == cases["expected"]
    labels = ["likely_met", "unknown", "not_met"]
    confusion = pd.crosstab(cases["expected"], cases["got"]).reindex(index=labels, columns=labels, fill_value=0).reset_index()
    # the dangerous error: telling someone they likely qualify when the labels say they do not (or data is missing)
    false_pos = int(((cases["got"] == "likely_met") & (cases["expected"] != "likely_met")).sum())
    m = {"cases": int(len(cases)), "eligibility_agreement": float(cases["agree"].mean()), "false_likely_met": false_pos,
         "never_guesses_on_missing": bool(cases.loc[cases["why"].str.contains("missing|text|null"), "got"].ne("likely_met").all())}
    g = [{"metric": "eligibility_agreement", "value": m["eligibility_agreement"], "rule": f">= {qc.THRESHOLDS['eligibility_agreement_min']}",
          "pass": m["eligibility_agreement"] >= qc.THRESHOLDS["eligibility_agreement_min"]},
         {"metric": "false_likely_met", "value": false_pos, "rule": "== 0", "pass": false_pos == 0},
         {"metric": "never_guesses_on_missing", "value": m["never_guesses_on_missing"], "rule": "is True", "pass": m["never_guesses_on_missing"]}]
    path = report.write(qc.REPORTS, "eligibility", "Eligibility agreement", m, g,
                        {"confusion_matrix": confusion, "disagreements": cases[~cases["agree"]]},
                        ["Labels are hand-written (synth/make_eligibility_cases.py). A disagreement can be a rule bug or a labelling error."])
    if not quiet:
        print(f"cases={m['cases']} agreement={m['eligibility_agreement']:.0%} false_likely_met={false_pos}")
        for r in g:
            print(("PASS " if r["pass"] else "FAIL ") + f"{r['metric']} {r['value']} {r['rule']}")
        print("report:", path)
    return m, g


if __name__ == "__main__":
    sys.exit(0 if all(r["pass"] for r in run()[1]) else 1)
