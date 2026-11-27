"""Tests of the evaluation kit itself: if the metrics are wrong, every report is wrong."""
import sys
import unittest
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import qa_config as qc  # noqa: E402
from evalkit import extractors, metrics  # noqa: E402
import run_regression  # noqa: E402
from run_language_eval import wer  # noqa: E402


def labels():
    return pd.read_csv(qc.DATA / "labels.csv", dtype=str, keep_default_na=False)


class Metrics(unittest.TestCase):
    def test_oracle_scores_perfectly(self):
        lab = labels()
        preds = {r["doc_id"]: extractors.oracle(r, b"") for _, r in lab.iterrows()}
        fr = metrics.field_results(lab, preds)
        m = metrics.summarize_fields(fr, lab, preds)
        self.assertEqual(m["field_accuracy"], 1.0)
        self.assertEqual(m["hallucination_rate"], 0.0)
        _, fsum = metrics.finding_metrics(lab, metrics.predicted_findings(lab, preds, date(2026, 11, 20)))
        self.assertEqual(fsum["name_mismatch_recall"], 1.0)
        self.assertEqual(fsum["expiry_recall"], 1.0)

    def test_hallucination_wrong_and_missing_are_distinguished(self):
        lab = labels()
        row = lab[(lab["doc_type"] == "aadhaar") & (lab["condition"] == "missing_field")].iloc[0]   # dob is absent on the document
        pred = extractors.oracle(row, b"")
        pred["fields"]["dob"] = "1990-01-01"                  # invented
        pred["fields"]["name"] = "Someone Else"               # wrong
        del pred["fields"]["id_number"]                       # not read
        fr = metrics.field_results(lab[lab["doc_id"] == row["doc_id"]], {row["doc_id"]: pred}).set_index("field")
        self.assertEqual(fr.loc["dob", "status"], "hallucinated")
        self.assertEqual(fr.loc["name", "status"], "wrong")
        self.assertEqual(fr.loc["id_last4", "status"], "missing")

    def test_noisy_extractor_fails_the_gates(self):
        lab = labels()
        noisy = extractors.make_noisy(3, 0.5)
        preds = {r["doc_id"]: noisy(r, b"") for _, r in lab.iterrows()}
        fr = metrics.field_results(lab, preds)
        m = metrics.summarize_fields(fr, lab, preds)
        m.update(metrics.finding_metrics(lab, metrics.predicted_findings(lab, preds, date(2026, 11, 20)))[1])
        self.assertFalse(all(g["pass"] for g in metrics.gates(m, qc.THRESHOLDS)))
        self.assertGreater(m["ece"], 0.1)                     # overconfident: calibration error must show it

    def test_confident_wrong_answers_raise_ece(self):
        df = pd.DataFrame({"predicted": ["a"] * 10, "status": ["wrong"] * 10, "confidence": [0.95] * 10})
        self.assertAlmostEqual(metrics.ece(df), 0.95, places=2)
        ok = pd.DataFrame({"predicted": ["a"] * 10, "status": ["correct"] * 10, "confidence": [0.95] * 10})
        self.assertAlmostEqual(metrics.ece(ok), 0.05, places=2)

    def test_names_are_compared_strictly(self):
        self.assertNotEqual(metrics.norm("name", "Ram. Kumar"), metrics.norm("name", "Ramesh Kumar"))
        self.assertEqual(metrics.norm("name", " ramesh   KUMAR "), metrics.norm("name", "Ramesh Kumar"))
        self.assertEqual(metrics.norm("id_last4", "9999 0000 1234"), "1234")
        self.assertEqual(metrics.norm("annual_income", "60,000"), 60000)

    def test_wer(self):
        self.assertEqual(wer("a b c d", "a b c d"), 0.0)
        self.assertEqual(wer("a b c d", "a x c d"), 0.25)
        self.assertEqual(wer("a b", ""), 1.0)

    def test_regression_compare_flags_the_right_direction(self):
        base = {"extraction.field_accuracy": 0.95, "extraction.hallucination_rate": 0.01, "eligibility.eligibility_agreement": 1.0}
        cur = {"extraction.field_accuracy": 0.90, "extraction.hallucination_rate": 0.05, "eligibility.eligibility_agreement": 1.0}
        res = {k: r for k, _, _, r in run_regression.compare(base, cur, 0.01)}
        self.assertEqual(res["extraction.field_accuracy"], "REGRESSION")
        self.assertEqual(res["extraction.hallucination_rate"], "REGRESSION")   # higher is worse
        self.assertEqual(res["eligibility.eligibility_agreement"], "same")
        better = {k: r for k, _, _, r in run_regression.compare(base, {"extraction.field_accuracy": 0.99}, 0.01)}
        self.assertEqual(better["extraction.field_accuracy"], "improved")


if __name__ == "__main__":
    unittest.main()
