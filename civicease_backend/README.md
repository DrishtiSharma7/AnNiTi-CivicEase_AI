# CivicEase AI backend

FastAPI backend built to the Team AnNiTi submission: API and security layer, consent and the five human gates,
agent orchestration, rule-pack pipeline, voice, encrypted storage, audit trail and a sandboxed browser worker.

**Read `COMPLIANCE_MATRIX.md` first.** It lists every condition in the proposal and says honestly which are done,
written-but-not-run, partial, outside the backend, or not implemented.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # edit secrets
uvicorn app.main:app --reload     # http://localhost:8000/docs
pytest -q                         # API flow tests (need the packages above)
python tools/eval.py              # eligibility + document-audit agreement on the labelled cases
```
Docker: `docker compose up --build` starts the API, PostgreSQL with pgvector, and the browser worker on an internal-only network.

## Layout
| Path | What |
|---|---|
| `app/routers/` | auth, consent/profile, schemes + agents, documents, applications (gates), dashboard, voice, admin, system |
| `app/agents/` | orchestrator, discovery, doc auditor, app prep, browser action, notification |
| `app/security.py`, `kms.py`, `storage.py` | Argon2id, JWT, envelope encryption, HMAC digests and tokens, KMS and object storage |
| `app/eligibility.py`, `docaudit.py`, `trust.py`, `portal.py`, `rules.py`, `profile_parse.py` | deterministic rules and policy (pure, unit-tested) |
| `app/llm.py`, `ocr.py`, `retrieval.py`, `quota.py` | model access, local OCR, RAG search, per-user quotas |
| `worker/` + `Dockerfile.worker` | separate Playwright worker (no DB, no keys) |
| `API_CONTRACT.md` | endpoints, response shapes, TypeScript types for Drishti and Nisha |
| `tools/eval.py`, `data/eval_cases.json` | roadmap exit-criteria checks |

## Demo walkthrough (mock mode, no key needed)
1. Register, grant both consents, answer the profile questions (`/agents/profile/next`) or `PUT /profile` (age 62, annual_income 60000).
2. Upload `ramesh_aadhaar.pdf` and `ramesh_income.pdf` (any file starting with `%PDF-`; the name selects the synthetic persona), audit both, create an application for `old-age-pension`, call `/readiness`: blocking `NAME_MISMATCH` and `EXPIRED`.
3. Repeat with `sunita_*.pdf`: green report, Gate 3, prepare, prefill (pauses at Gate 4), Gate 4, approval token, submit.
4. Watch `GET /judge/telemetry`: model routing, skill loading, PII masking, human gates.
5. Reviewer flow: set `REVIEWER_EMAILS`, register that account, `POST /admin/rulepacks/ingest` with a `gov.in`/`nic.in` URL and pasted text, approve with a second reviewer.

## Read before the live round
- **Not run in the build sandbox:** everything that needs FastAPI, SQLAlchemy, a database, a Gemini key, Redis, Cloud KMS/GCS, Tesseract, Playwright or pgvector. The pure logic (crypto, PII, hash chain, eligibility, document audit, trust guard, portal policy, profile parsing, rule validation, PDF, embeddings) passes `tests/test_core.py`, and `tools/eval.py` passes 15/15. Run `pytest -q` and expect a few small fixes in the API layer.
- Scheme rules in `app/seed.py` are an illustrative seed (`verification_status: unverified_seed`). Publish them through the reviewer pipeline, or edit them against official sources, before calling them verified.
- Not implemented: Google ADK library itself (the orchestrator is ADK-style), Gemini Live, Gemma, per-language quality measurement, official status feeds, a durable job queue.
- Raw document images reach the model unless `LOCAL_OCR=true` (needs Tesseract) or you set `REQUIRE_LOCAL_REDACTION=true`.
- Extracted names and dates sit in the database unencrypted (IDs are masked); add column encryption if you need it. DPDP alignment is a design goal, not legal advice.
