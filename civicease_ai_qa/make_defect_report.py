"""Turns the latest evaluation failures into defect drafts with reproduction steps (append the ones you confirm to
defects/defect_log.csv). Run the evaluations first:  python make_defect_report.py"""
import pandas as pd

import qa_config as qc


def block(title, df, cols, steps):
    if not df.empty:
        yield f"### {title} ({len(df)})"
        yield f"Reproduce: `{steps}`"
        yield ""
        for _, r in df.iterrows():
            yield "- " + ", ".join(f"{c}={r[c]}" for c in cols)
        yield ""


def main():
    out = ["# Defect drafts (from the latest evaluation reports)", "",
           "Each item needs a human decision: rule or code bug, labelling mistake, or accepted limitation.", ""]
    for name, cols, title, steps in [
        ("eligibility_disagreements", ["case_id", "scheme_id", "profile_json", "expected", "got", "why"], "Eligibility disagreements", "python run_eligibility_eval.py"),
        ("language_failures", ["case_id", "field", "utterance", "expected", "got"], "Language understanding failures", "python run_language_eval.py"),
    ]:
        p = qc.REPORTS / f"{name.split('_')[0]}_{name.split('_', 1)[1]}.csv"
        if p.exists():
            out += list(block(title, pd.read_csv(p, dtype=str, keep_default_na=False), cols, steps))
    for p in sorted(qc.REPORTS.glob("extraction_*_field_errors.csv")):
        ex = p.name.split("_")[1]
        df = pd.read_csv(p, dtype=str, keep_default_na=False)
        out += list(block(f"Extraction errors ({ex})", df.head(40), ["doc_id", "field", "expected", "predicted", "status", "confidence"],
                          f"python run_extraction_eval.py --extractor {ex}   (documents are under data/documents/)"))
    (qc.REPORTS / "defect_drafts.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out[:25]), "\n...\nwritten to reports/defect_drafts.md")


if __name__ == "__main__":
    main()
