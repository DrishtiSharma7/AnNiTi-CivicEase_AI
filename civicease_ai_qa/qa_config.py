"""Shared settings for Nisha's QA toolkit. Edit thresholds here (and say why in the defect/regression report)."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
BASELINES = ROOT / "baselines"

# The toolkit tests the real backend code. Default: current parent or a sibling folder named civicease_backend.
_default_backend = ROOT.parent if (ROOT.parent / "app").is_dir() else ROOT.parent / "civicease_backend"
BACKEND = Path(os.getenv("CIVICEASE_BACKEND", _default_backend)).resolve()
if not (BACKEND / "app").is_dir():
    raise SystemExit(f"Backend not found at {BACKEND}. Set CIVICEASE_BACKEND=/path/to/civicease_backend")
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
os.environ.setdefault("DATABASE_URL", "sqlite://")        # keep tests off any real database
os.environ.setdefault("USE_MOCK_LLM", "true")              # live runs: set USE_MOCK_LLM=false and GEMINI_API_KEY

# Acceptance gates (proposed starting points; the roadmap says verdicts must match manual labels on the test set).
THRESHOLDS = {
    "field_accuracy_min": 0.90,         # extracted fields equal to the label
    "doc_type_accuracy_min": 0.95,
    "hallucination_rate_max": 0.05,     # a value returned for a field that is absent from the document
    "name_mismatch_recall_min": 0.95,   # a missed mismatch can cause a rejection at the counter
    "name_mismatch_precision_min": 0.90,
    "expiry_recall_min": 1.0,           # an expired certificate must never pass
    "eligibility_agreement_min": 1.0,   # rules are deterministic: every labelled case must agree
    "language_parse_accuracy_min": 0.80,
    "ece_max": 0.15,                    # confidence should roughly equal accuracy
}
REGRESSION_TOLERANCE = 0.01            # a metric may drop by at most this much against the baseline


def load_meta() -> dict:
    return json.loads((DATA / "meta.json").read_text())
