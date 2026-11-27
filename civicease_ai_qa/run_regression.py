"""Regression check: run every evaluation, compare with the stored baseline, and say WHAT changed (prompt, model ids,
scheme rules, skills, code) next to WHICH metric moved. Run it whenever prompts, models, rules or APIs change.
  python run_regression.py --update-baseline        # accept the current numbers as the baseline (after review)
  python run_regression.py                          # compare; exit 1 on a regression, 2 if there is no baseline
  python run_regression.py --extractor backend      # live model regression (spends free-tier quota; cached otherwise)"""
import argparse
import hashlib
import json
import sys
from datetime import date

import qa_config as qc

LOWER_IS_BETTER = {"hallucination_rate", "ece", "wrong_rate", "missing_rate", "unknown_rate", "false_likely_met", "wrong_values"}
TRACKED = {
    "extraction": ["field_accuracy", "doc_type_accuracy", "hallucination_rate", "missing_rate", "wrong_rate", "unknown_rate", "ece",
                   "name_mismatch_recall", "name_mismatch_precision", "expiry_recall", "missing_field_recall"],
    "eligibility": ["eligibility_agreement", "false_likely_met"],
    "language": ["language_parse_accuracy", "wrong_values"],
}


def _h(*chunks: bytes) -> str:
    h = hashlib.sha256()
    for c in chunks:
        h.update(c)
    return h.hexdigest()[:12]


def fingerprint() -> dict:
    from app import llm, seed
    from app.config import get_settings
    s, app_dir = get_settings(), qc.BACKEND / "app"
    skill_files = sorted((app_dir / "skills").rglob("SKILL.md")) + sorted((qc.ROOT / "skills").rglob("SKILL.md"))
    code_files = [app_dir / n for n in ("eligibility.py", "docaudit.py", "trust.py", "portal.py", "profile_parse.py", "rules.py")]
    return {
        "prompt_extraction": _h(llm.SCHEMA_HINT.encode()), "prompt_rules": _h(llm.RULES_PROMPT.encode()),
        "models": f"{s.model_flash}|{s.model_lite}|mock={s.use_mock_llm}|escalate={s.escalate_below}",
        "scheme_rules": _h(json.dumps(seed.SCHEMES, sort_keys=True).encode()),
        "skills": _h(*[p.read_bytes() for p in skill_files]),
        "rule_code": _h(*[p.read_bytes() for p in code_files]),
        "dataset": _h((qc.DATA / "labels.csv").read_bytes(), (qc.DATA / "eligibility_cases.csv").read_bytes(), (qc.DATA / "language_cases.csv").read_bytes()),
    }


def collect(extractor: str) -> dict:
    import run_eligibility_eval, run_extraction_eval, run_language_eval
    out = {}
    for name, (m, _) in {"extraction": run_extraction_eval.run(extractor, quiet=True), "eligibility": run_eligibility_eval.run(quiet=True),
                         "language": run_language_eval.run(quiet=True)}.items():
        for k in TRACKED[name]:
            out[f"{name}.{k}"] = float(m[k])
    return out


def compare(base: dict, cur: dict, tol: float) -> list:
    rows = []
    for k, v in cur.items():
        b = base.get(k)
        if b is None:
            rows.append((k, None, v, "new")); continue
        lower = k.split(".")[1] in LOWER_IS_BETTER
        delta = v - b
        worse = (delta > tol) if lower else (delta < -tol)
        better = (delta < -tol) if lower else (delta > tol)
        rows.append((k, b, v, "REGRESSION" if worse else ("improved" if better else "same")))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--extractor", default="oracle", choices=["oracle", "noisy", "backend", "file"])
    ap.add_argument("--update-baseline", action="store_true")
    a = ap.parse_args(argv)
    qc.BASELINES.mkdir(exist_ok=True)
    path = qc.BASELINES / f"baseline_{a.extractor}.json"
    cur, fp = collect(a.extractor), fingerprint()
    if a.update_baseline:
        path.write_text(json.dumps({"date": date.today().isoformat(), "extractor": a.extractor, "fingerprint": fp, "metrics": cur}, indent=2))
        print(f"baseline written -> {path}")
        return 0
    if not path.exists():
        print(f"No baseline at {path}. Review the numbers, then run with --update-baseline.")
        return 2
    base = json.loads(path.read_text())
    rows = compare(base["metrics"], cur, qc.REGRESSION_TOLERANCE)
    changed = [k for k in fp if fp[k] != base["fingerprint"].get(k)]
    lines = [f"# Regression report ({a.extractor}) {date.today()}", "",
             f"Baseline from {base['date']}. Changed since baseline: **{', '.join(changed) or 'nothing'}**", "",
             "| metric | baseline | now | result |", "|---|---|---|---|"]
    lines += [f"| {k} | {'' if b is None else f'{b:.3f}'} | {v:.3f} | {r} |" for k, b, v, r in rows]
    bad = [r for r in rows if r[3] == "REGRESSION"]
    if bad and not changed:
        lines += ["", "Metrics got worse but nothing tracked changed: suspect model non-determinism or a flaky dependency. Re-run before filing a defect."]
    if changed and not bad:
        lines += ["", f"Tracked inputs changed ({', '.join(changed)}) with no metric regression. If the change was intended, run --update-baseline."]
    (qc.REPORTS / "regression_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
