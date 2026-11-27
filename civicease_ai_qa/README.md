# Nisha's AI/ML and QA toolkit for CivicEase AI

Everything in Nisha's workstream from the Team AnNiTi docs: synthetic labelled test data, evaluation of document
extraction and eligibility, failure-mode and regression tests, prompt records, response schemas, Agent Skills and a defect log.
It tests the **real backend code** (`civicease_backend`), so put the two folders side by side (or set `CIVICEASE_BACKEND`).

## Quick start
```bash
pip install -r requirements.txt
python tests/run_all.py                 # 35 tests (pytest -q works too)
python run_extraction_eval.py --extractor oracle     # harness self-check: must score 100%
python run_eligibility_eval.py          # 32 hand-labelled cases
python run_language_eval.py             # Hindi / English / Hinglish answers to the Profile agent
python run_regression.py                # compare with baselines/, say what changed
python make_defect_report.py            # failures -> defect drafts with reproduction steps
```
Regenerate data (optional): `python synth/make_dataset.py`, `synth/make_eligibility_cases.py`, `synth/make_language_cases.py`.

## Measuring the real model (Gemini)
```bash
export USE_MOCK_LLM=false GEMINI_API_KEY=...        # in the backend's environment
python run_extraction_eval.py --extractor backend --sleep 4 --limit 20
```
- `--sleep` keeps you under free-tier requests per minute; `--limit` caps calls per run; results are **cached** in `reports/cache_backend.jsonl`
  (keyed by file hash, prompt and model ids), so re-running a report costs nothing. Free-tier limits change: check your AI Studio console.
- The data is **synthetic only**. Google can use free-tier requests to improve its products, so never send real citizen documents on the free tier.
- Prompts tried in Google AI Studio: save outputs as JSON lines `{"doc_id": "P01_aadhaar", "extraction": {...same shape as the backend...}}`
  and score them with `--extractor file --predictions yours.jsonl`.
- In mock mode the backend only knows the four demo personas, so `--extractor backend` scores low there. That says nothing about Gemini.

## What maps to your role
| Role item | Where |
|---|---|
| Clean, structured test datasets; synthetic, identifiers masked | `synth/make_dataset.py` -> `data/labels.csv` + `data/documents/*.png` (watermarked, dummy IDs, labels keep last 4 only) |
| Pandas/NumPy: expected vs predicted, summaries | `evalkit/metrics.py` (field accuracy, hallucination, calibration/ECE, per-condition, finding precision/recall) |
| Document understanding via Gemini, structured output | `evalkit/extractors.py` (`backend`, `file`), `schemas/doc_extraction.schema.json` |
| Do not let model text replace deterministic rules | the findings are computed by the backend's own `docaudit.py` on the predicted fields |
| Model roles (Flash-Lite first, Flash on low confidence) | `tests/test_failure_modes.py` pins the order |
| AI Studio prompt records | `prompts/registry.py` (+ `registry.csv`): version, hash, model, test category, accuracy, observed errors; drift check against the backend |
| Agent Skills with inputs, validation steps, output schema, edge cases, UNKNOWN rules | `skills/*/SKILL.md` + `skills/lint_skills.py` (copy the two folders into `backend/app/skills/`) |
| Labelled test set; extraction accuracy, mismatch detection, eligibility agreement | `run_extraction_eval.py`, `run_eligibility_eval.py` |
| Missing data, low confidence, unreadable, expired, timeouts, quota, unsupported languages | `tests/test_failure_modes.py`, `run_language_eval.py` |
| Verify the fallback chain (retry with backoff, lighter model, UNKNOWN, log) | `tests/test_failure_modes.py` |
| Regression checks after prompt/model/rule/API changes; defect reports | `run_regression.py`, `defects/defect_log.csv`, `make_defect_report.py` |

## First findings (already in `defects/defect_log.csv`)
- **D007 (High):** the backend's local blur check never fires (fixed threshold; blurred pages score ~300, clear ones 1800-2800).
  Proposed fix in `evalkit/blur.py` separates the synthetic set cleanly (clear 4.5-5.1, blurred 1.0, threshold 2.0). Its test is marked `expectedFailure`; remove the marker when Aanchal fixes it.
- **D001-D006:** the Profile agent re-asks for number words ("sixty two", "बासठ"), "ढाई लाख", Latin-script Hindi ("mazdoor", "nokri"), "scheduled caste", "aurat". Language accuracy is 78%, below the 80% gate, with **0 wrong values** (it asks again instead of guessing, which is the safe failure).
- Eligibility: 32/32 hand-labelled cases agree, including boundaries, missing data, nulls and wrongly typed values.

## Working agreements
- Change a prompt: edit the file in `prompts/`, `python prompts/registry.py new <id> <version> "<what changed>"`, update the backend constant, run `run_regression.py`, review, then `--update-baseline`.
- Thresholds live in `qa_config.py`; if you lower one, write why in the regression report.
- Hand-off deliverables: tested utilities and skills (`evalkit/`, `skills/`), response schemas (`schemas/`), prompt records (`prompts/registry.csv`), labelled test cases (`data/`), evaluation results (`reports/`), regression and defect report (`reports/regression_report.md`, `defects/`).

## Limits to know about
- Ran here: all 35 tests (with Python's unittest runner, not pytest) and every evaluation in oracle/noisy/mock modes. **Never run here:** live Gemini calls, so no real model accuracy number exists yet; `tests/test_failure_modes.py::DailyQuota` is skipped without SQLAlchemy.
- The documents are rendered images, not photos. Add real phone-camera variations (glare, skew, shadows, folds) before trusting accuracy on field conditions.
- The eligibility and language labels were drafted by the assistant from the seed rules and should be reviewed by you; the seed rules are themselves illustrative and unverified.
- Language quality needs native-speaker review; `data/transcripts.csv` is a template for word-error-rate measurement and has no audio yet.
- If the team moves to Vertex AI (the deck's stack), the harness still works: it measures through the backend `llm` layer. Swap the transport in `app/llm.py::_post`, then run `run_regression.py --extractor backend`.
