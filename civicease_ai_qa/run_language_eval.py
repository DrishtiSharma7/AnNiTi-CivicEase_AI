"""Language quality, measured not assumed.
 1) Profile-answer understanding (Hindi / English / Hinglish): python run_language_eval.py
 2) Speech-to-text word error rate: fill data/transcripts.csv 'hypothesis' (e.g. from the backend /voice/transcribe or
    AI Studio) and run: python run_language_eval.py --wer data/transcripts.csv
A native-speaker review is still required per language before claiming support (roadmap Phase 4)."""
import argparse
import sys

import numpy as np
import pandas as pd

import qa_config as qc
from evalkit import report


def wer(ref: str, hyp: str) -> float:
    r, h = ref.split(), hyp.split()
    d = np.zeros((len(r) + 1, len(h) + 1), dtype=int)
    d[:, 0], d[0, :] = np.arange(len(r) + 1), np.arange(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return d[len(r), len(h)] / max(len(r), 1)


def run(quiet=False):
    from app import profile_parse
    cases = pd.read_csv(qc.DATA / "language_cases.csv", dtype=str, keep_default_na=False)
    got = []
    for r in cases.itertuples():
        try:
            got.append(str(profile_parse.parse_answer(r.field, r.utterance)))
        except ValueError:
            got.append("REASK")
    cases["got"] = got
    cases["agree"] = cases["got"] == cases["expected"]
    # a wrong value is worse than asking again: a confident WRONG answer silently changes eligibility
    cases["wrong_value"] = (~cases["agree"]) & (cases["got"] != "REASK")
    cases["asked_again_needlessly"] = (~cases["agree"]) & (cases["got"] == "REASK")
    by_lang = cases.groupby("language").agg(cases=("agree", "size"), accuracy=("agree", "mean"),
                                            wrong_values=("wrong_value", "sum"), needless_reasks=("asked_again_needlessly", "sum")).reset_index()
    m = {"cases": int(len(cases)), "language_parse_accuracy": float(cases["agree"].mean()), "wrong_values": int(cases["wrong_value"].sum()),
         "by_language": {r.language: float(r.accuracy) for r in by_lang.itertuples()}}
    g = [{"metric": "language_parse_accuracy", "value": m["language_parse_accuracy"], "rule": f">= {qc.THRESHOLDS['language_parse_accuracy_min']}",
          "pass": m["language_parse_accuracy"] >= qc.THRESHOLDS["language_parse_accuracy_min"]},
         {"metric": "wrong_values", "value": m["wrong_values"], "rule": "== 0", "pass": m["wrong_values"] == 0}]
    path = report.write(qc.REPORTS, "language", "Profile answer understanding by language", m, g,
                        {"by_language": by_lang, "failures": cases[~cases["agree"]]},
                        ["Failures are findings, not noise: each is a gap in the parser or the label. File them in defects/defect_log.csv."])
    if not quiet:
        print(f"cases={m['cases']} accuracy={m['language_parse_accuracy']:.0%} wrong_values={m['wrong_values']} by_language={m['by_language']}")
        for r in g:
            print(("PASS " if r["pass"] else "FAIL ") + f"{r['metric']} {r['value']} {r['rule']}")
        print("report:", path)
    return m, g


def run_wer(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = df[df["hypothesis"].str.strip() != ""]
    if df.empty:
        raise SystemExit("Fill the 'hypothesis' column first.")
    df["wer"] = [wer(r.reference, r.hypothesis) for r in df.itertuples()]
    print(df.groupby("language")["wer"].agg(["count", "mean"]).round(3).to_string())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wer", default="")
    a = ap.parse_args()
    if a.wer:
        run_wer(a.wer)
        sys.exit(0)
    sys.exit(0 if all(r["pass"] for r in run()[1]) else 1)
