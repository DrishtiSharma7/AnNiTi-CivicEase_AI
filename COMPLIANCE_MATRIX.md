# Conformance matrix: CivicEase AI proposal vs this backend

Status key: **Done** = implemented and exercised by tests that ran where noted. **Written** = implemented but not
executed in the build sandbox (needs `pip install -r requirements.txt`, then `pytest -q`). **Partial** = some of it.
**Outside** = frontend/ops/people work, not backend code. **Gap** = not implemented.

"Ran" means `tests/test_core.py` (16 tests) and `tools/eval.py` passed in the sandbox. Everything that needs FastAPI,
SQLAlchemy, a database, a model key or a browser is "Written" until you run it.

## Architecture (slide 4)
| Proposal condition | Status | Where |
|---|---|---|
| TB1 Next.js PWA, voice/text/camera UI | Outside | Drishti. Backend gives `/dashboard`, `/voice/*`, uploads |
| TB1 Offline: checklist PDF | Written | `GET /applications/{id}/checklist.pdf` (`pdfgen.py` ran) |
| TB1 Offline: draft cache, text mode | Outside | Client side. Text always works; voice falls back with a clear error |
| TB1 HTTPS + JWT | Written | JWT, HSTS header, HTTPS redirect when `FORCE_HTTPS`; TLS terminates at your proxy |
| TB2 authN/authZ, consent check, upload validation, rate limit, input validation, PII redaction, audit log | Written (crypto, PII, hash chain **Ran**) | `deps.py`, `routers/*`, `pii.py`, `audit.py` |
| TB3 ADK orchestrator, typed task objects | Partial | ADK-**style** orchestrator with typed `AgentTask`/`AgentResult` (`agents/orchestrator.py`). The Google ADK library itself is not used |
| TB3 Agents: Profile, Discovery, Eligibility, Doc Auditor, App Prep, Browser Action, Notification | Written | `agents/`, `profile_parse.py` (**Ran**) |
| TB3 Agent Skills (SKILL.md) load on demand | Written | `skills.py`, `skills/*/SKILL.md` |
| TB3 Browser agent: separate sandboxed worker, allow-listed domains, stops at gates | Written (policy **Ran**) | `worker/main.py`, `Dockerfile.worker`, internal Docker network, HMAC-signed calls, `portal.py` |
| Trust & Compliance guard around every agent output | Done in code, Written in API | `trust.py` (**Ran**); applied to discovery, eligibility, readiness |
| TB4 Postgres + pgvector RAG store | Written | `retrieval.py`; falls back to Python cosine on SQLite |
| TB4 Encrypted private file storage, IDs as salted HMAC digests, hash-chained audit | Written (crypto **Ran**) | `security.py`, `kms.py`, `storage.py`, `hashchain.py` |
| TB5 Gemini: reasoning, vision/OCR, speech-to-text, text-to-speech, embeddings | Written (live path untested) | `llm.py`, `routers/voice.py` |
| TB5 Official sources feed the rule-pack pipeline | Partial | Reviewer pastes official text + URL; no crawler |
| Gemini Live real-time voice | Gap | Optional in the proposal; needs a websocket/client design |
| Gemma on-device/self-hosted | Gap | Optional in the proposal |

## Model strategy (slide 6)
| Condition | Status | Where |
|---|---|---|
| Flash tier for analysis, Flash-Lite for routing/translation/transcription | Written | `llm.py` |
| Cheapest model first, escalate only on low confidence | Written | `_extract_chain` (Flash-Lite, then Flash below `ESCALATE_BELOW_CONFIDENCE`) |
| Rules and OCR checks run as code before any LLM call | Written | `docaudit.py` (**Ran**), `ocr.py` local quality check + local OCR (optional libs) |
| Results cached by SHA-256 | Done in design, Written in API | Per user (a global cache would leak across citizens) |
| Queue with backoff, per-user quotas, compressed images | Partial | Bounded concurrency + backoff retries, `quota.py`, `ocr.compress_image` (needs Pillow). Not a durable job queue |
| Model IDs in one config file | Written | `.env` / `config.py` |
| Quality per Indian language measured, not assumed | Gap | `tools/eval.py` measures eligibility and document audit only; language quality needs native-speaker test sets (Nisha) |

## User flow and product (slides 8-9)
| Condition | Status |
|---|---|
| Six steps, a control at each | Written |
| Five human gates (profile consent, document consent, approve readiness, citizen login/OTP/CAPTCHA, citizen final submit) | Written |
| Failure chain: retry with backoff, lighter model, UNKNOWN, log the failure | Written (`llm.py`, `doc_auditor.py` logs `model_failure`). Order is Flash-Lite first, then Flash, to honour "cheapest first" |
| Dashboard cards: recommended schemes, documents needing attention, next deadline, applications in progress | Written (`GET /dashboard`) |
| Chat: language tag, "why am I asked this?", quick replies, read-aloud | Written (`/agents/chat`, `/agents/profile/*`, `/voice/speak`) |
| Document verification: type, quality badge, per-field confidence, Expired / Name mismatch / Low confidence flags, retake, confirm field, ask a human | Written (`/documents/{id}/audit`, `confirm-field`, `ask-human`; re-upload = retake) |
| Scheme cards: benefit, "Preliminary estimate", criteria chips, deadline, source + last verified | Written |
| Readiness report: blocking / warning / passed with one-line fixes; no guarantee | Written (**Ran** for the logic) |
| Tracking: Draft, Ready, Submitted by you, status updates (official only, otherwise manual), reminders, renewals | Partial: citizen-entered status only; no official status feed exists to connect |

## Security and privacy (slide 10)
| Condition | Status |
|---|---|
| HTTPS/TLS with HSTS; service-to-service calls authenticated; signed expiring file URLs | Written (**Ran**: signing). Worker calls use HMAC with timestamp |
| AES-256 envelope encryption, unique data key per user and document, wrapped by managed KMS, never stored beside data | Written (**Ran** with LocalKMS). Cloud KMS (`KMS_MODE=gcp`) and GCS storage are untested. Ciphertext is bound to user+document via AAD |
| Auto-expiry | Written (hourly purge + at startup) |
| SHA-256 fingerprint: tamper, duplicates, cache key, verified before use | Written |
| IDs masked (last 4) + salted HMAC-SHA256 digest | Written (**Ran**) |
| PII redacted before LLM calls | Partial: always for text/prompts. For images, only with `LOCAL_OCR=true` (local OCR, redact, send text). Otherwise the image goes to the model; set `REQUIRE_LOCAL_REDACTION=true` to forbid that |
| Signed human approval token bound to the exact form hash | Written (**Ran**) |
| Tamper-evident hash-chained audit trail | Written (**Ran**) |
| Least-privilege access | Written: citizen and reviewer roles; reviewer-only admin routes |
| Argon2id for the app-lock PIN | Written (`/auth/pin`, lockout after 5 failures) |
| Sandboxed browser agent with domain allow-list | Written |
| No CAPTCHA/OTP bypass, no forgery claims, no acceptance guarantees | Written (**Ran**: guard, portal policy) |
| Consent-first, minimal data, delete-on-request | Written: strict schemas, `DELETE /me`, `GET /me/export`, consent withdrawal deletes the data it covered |
| Aligned with DPDP Act 2023 / Rules 2025 | Design goal only. This is not a legal review |

## Differentiation, business, roadmap (slides 11-13)
| Condition | Status |
|---|---|
| New scheme = ingest official source, extract rules (Gemini), human reviewer approves, publish with citation | Written (`/admin/rulepacks/*`, official `gov.in`/`nic.in` only, four-eyes in production) |
| Rule packs: Central, State, Scholarships, Healthcare, Agricultural, Women and child, Employment | Written (`pack` field, `GET /schemes?pack=`) |
| Every recommendation shows criteria, source and verification date | Done in code (**Ran**), seed schemes show "unverified" until a reviewer publishes |
| Stateless API and agent services that autoscale | Partial: JWT, GCS storage, Redis rate limiter, Postgres advisory lock. Telemetry and metrics are per process |
| Semantic search with pgvector | Written |
| Model routing, caching, per-user quotas | Written |
| Monitoring for errors, latency, cost | Partial: `/metrics` (requests, errors, latency sums, model calls as a cost proxy). No token-cost accounting |
| MVP exit: profile to ranked schemes in under 3 minutes | Outside: a UX timing you must measure with users |
| MVP exit: extraction accuracy measured on a synthetic set | Partial: `tools/eval.py` measures the rule checks; accuracy of real Gemini extraction needs labelled synthetic documents |
| Phase 2 exit: verdicts match manual labels; every answer carries a citation | Ran: 10/10 eligibility and 5/5 document cases agree (`tools/eval.py`); scheme outputs are blocked by the guard if they lack source/last_verified |
| Phase 3 demo: mock portal pre-fill with all five gates | Written (`/mock-portal/form`, `/prefill`) |
| Partnerships, pilots, traction numbers | Outside, and not claimed |
