"""Document extraction + audit evaluation.
  python run_extraction_eval.py --extractor oracle            # harness self-check (must be 100%)
  python run_extraction_eval.py --extractor noisy             # harness catches injected errors
  python run_extraction_eval.py --extractor backend           # real backend (mock mode = fixtures; live = Gemini)
  USE_MOCK_LLM=false GEMINI_API_KEY=... python run_extraction_eval.py --extractor backend --sleep 4 --limit 20
  python run_extraction_eval.py --extractor file --predictions my_ai_studio_runs.jsonl"""
import argparse
import sys
from datetime import date

import pandas as pd

import qa_config as qc
from evalkit import extractors, metrics, report


def run(extractor_name="oracle", seed=1, error_rate=0.25, predictions="", sleep=0.0, limit=0, quiet=False):
    labels = pd.read_csv(qc.DATA / "labels.csv", dtype=str, keep_default_na=False)
    today = date.fromisoformat(qc.load_meta()["reference_date"])
    ex = extractors.get(extractor_name, seed, error_rate, predictions)
    cache = extractors.Cache(qc.REPORTS / f"cache_{extractor_name}.jsonl", extractors.fingerprint()) if extractor_name in ("backend", "file") else None
    qc.REPORTS.mkdir(exist_ok=True)
    preds = extractors.run_all(labels, qc.DATA, ex, cache, sleep, limit)
    labels = labels[labels["doc_id"].isin(preds)]
    fr = metrics.field_results(labels, preds)
    m = metrics.summarize_fields(fr, labels, preds)
    found = metrics.predicted_findings(labels, preds, today)
    ft, fsum = metrics.finding_metrics(labels, found)
    m.update(fsum)
    g = metrics.gates(m, qc.THRESHOLDS)
    errors = fr[fr["status"].isin(["wrong", "missing", "hallucinated"])]
    cond = pd.DataFrame([{"condition": k, "field_accuracy": v} for k, v in m["accuracy_by_condition"].items()])
    notes = [f"extractor={extractor_name}; documents={m['documents']}; reference date={today}; SYNTHETIC data only"]
    from app.config import get_settings
    if extractor_name == "backend" and get_settings().use_mock_llm:
        notes.append("Backend is in MOCK mode: it only knows the four demo personas, so low scores here say nothing about Gemini. "
                     "Set USE_MOCK_LLM=false and GEMINI_API_KEY for a real measurement.")
    path = report.write(qc.REPORTS, f"extraction_{extractor_name}", f"Extraction and audit evaluation ({extractor_name})", m, g,
                        {"field_errors": errors, "by_condition": cond, "finding_metrics": ft}, notes)
    if not quiet:
        print(f"documents={m['documents']}  field_accuracy={m['field_accuracy']:.3f}  hallucination={m['hallucination_rate']:.3f}  "
              f"name_mismatch recall/precision={m['name_mismatch_recall']:.2f}/{m['name_mismatch_precision']:.2f}  "
              f"expiry_recall={m['expiry_recall']:.2f}  ece={m['ece']:.3f}")
        for r in g:
            print(("PASS " if r["pass"] else "FAIL ") + f"{r['metric']} {r['value']} {r['rule']}")
        print("report:", path)
    return m, g


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--extractor", default="oracle", choices=["oracle", "noisy", "backend", "file"])
    ap.add_argument("--predictions", default="")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--error-rate", type=float, default=0.25)
    ap.add_argument("--sleep", type=float, default=0.0, help="seconds between live calls (free-tier rate limits)")
    ap.add_argument("--limit", type=int, default=0, help="max live calls this run (cached results are free)")
    a = ap.parse_args(argv)
    _, g = run(a.extractor, a.seed, a.error_rate, a.predictions, a.sleep, a.limit)
    return 0 if all(r["pass"] for r in g) else 1


if __name__ == "__main__":
    sys.exit(main())
