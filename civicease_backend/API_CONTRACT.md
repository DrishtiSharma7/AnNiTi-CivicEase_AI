# CivicEase AI: API contract (Aanchal's hand-off to Drishti and Nisha)

Base URL `http://localhost:8000`. Interactive docs: `/docs`. Auth: `Authorization: Bearer <JWT>`.

## Response envelope (every endpoint)
```json
{"ok": true,  "data": { }, "error": null}
{"ok": false, "data": null, "error": {"code": "CONSENT_REQUIRED", "message": "..."}}
```
Extra error codes: `QUOTA_EXCEEDED` 429, `PIN_LOCKED` 429, `ANSWER_NOT_UNDERSTOOD` 422, `FORBIDDEN` 403, `FOUR_EYES` 403, `NOT_OFFICIAL_SOURCE` 422, `WORKER_UNAVAILABLE` 502, `VOICE_UNAVAILABLE` 502.

Error codes: `UNAUTHENTICATED` 401, `CONSENT_REQUIRED` 403, `NOT_FOUND` 404, `VALIDATION_ERROR` 422,
`RATE_LIMITED` 429, `TOO_LARGE` 413, `UNSUPPORTED_TYPE` 415, `TAMPERED` 409, gate errors 409
(`GATE3_REQUIRED`, `NOT_READY`, `GATES_INCOMPLETE`, `PREFILL_REQUIRED`), `APPROVAL_INVALID` 403, `PORTAL_POLICY` 403.

## Endpoints
| Method + path | Needs | Purpose |
|---|---|---|
| GET /health | none | liveness, mock/live flag |
| GET /dashboard | login | recommended schemes, documents needing attention, next deadline, applications in progress |
| PUT /auth/pin, POST /auth/pin/verify | login | Argon2id app-lock PIN (lockout after 5 wrong tries) |
| GET /me/export | login | right of access: all data held about the citizen |
| POST /auth/register, /auth/login | none | returns `access_token` |
| GET /auth/me | login | current user |
| DELETE /me | login | delete-on-request (account, files, data) |
| GET/POST /consents | login | `{kind: profile\|document_use, granted}` = **Gate 1 / Gate 2** |
| GET/PUT /profile | Gate 1 | minimal profile (age, annual_income, category, occupation, state, is_student, land_holding_hectares, language) |
| GET /schemes?state=&pack=&q= | none | catalogue (`results`); `q` = semantic search (match score is similarity, not eligibility) |
| GET /schemes/packs, /schemes/{id} | none | rule packs; one scheme with `source_url`, `last_verified`, `verification_status` |
| GET /agents/profile/next, POST /agents/profile/answer `{field, answer}` | Gate 1 | Profile agent: one question at a time with `why`; unclear answers are re-asked, never guessed |
| POST /agents/chat | login | orchestrator routes `{message, language}` to an agent; returns typed task + result |
| GET /agents/discover | Gate 1 | ranked scheme cards (criteria chips, preliminary estimate, source) |
| GET /agents/eligibility/{scheme_id} | Gate 1 | one scheme verdict per criterion |
| POST /documents (multipart `file`) | Gate 2 | PDF/PNG/JPEG, magic-byte checked, SHA-256, AES-256-GCM encrypted |
| GET /documents, /documents/{id} | login | metadata, masked fields, findings |
| POST /documents/{id}/audit | Gate 2 | Doc Auditor: findings (blocking/warning/passed/unknown + one-line fix); cached by SHA-256 |
| GET /documents/{id}/link -> GET /files/{token} | login | signed, expiring download URL |
| POST /documents/{id}/confirm-field `{field, value}` | Gate 2 | citizen confirms/corrects a field; checks re-run |
| POST /documents/{id}/ask-human | login | flags the document for a human reviewer |
| DELETE /documents/{id} | login | remove file + record |
| POST /applications `{scheme_id}` | Gate 1 | create application |
| POST /applications/{id}/readiness | Gate 2 | readiness report (all docs must be audited) |
| POST /applications/{id}/gates/3/approve `{confirm:true}` | login | **Gate 3**; refused if blocking/unknown items remain |
| POST /applications/{id}/prepare | Gate 3 | pre-filled form, checklist, `form_hash` |
| PATCH /applications/{id}/form `{fields:{}}` | login | citizen edits form; invalidates Gate 4 and tokens |
| POST /applications/{id}/prefill | Gate 3 | Browser Action agent (allow-listed, never submits); pauses at Gate 4 |
| POST /applications/{id}/gates/4/complete `{confirm:true}` | login | **Gate 4**: citizen did login/OTP/CAPTCHA |
| POST /applications/{id}/approval-token | Gates 3+4 | HMAC-signed, time-bound token bound to `form_hash` |
| POST /applications/{id}/submit `{approval_token, confirm:true}` | token | **Gate 5**: records the citizen's own final submit |
| POST /applications/{id}/status | submitted | citizen-entered status update |
| GET /applications/{id}/checklist.pdf | login | offline checklist PDF |
| GET /notifications | login | expiring documents and scheme deadlines |
| POST /voice/transcribe (multipart `audio`, `language`), POST /voice/speak `{text, language}` | login | speech-to-text and read-aloud (WAV) |
| POST /admin/rulepacks/ingest, GET /admin/rulepacks, POST /admin/rulepacks/{id}/approve or /reject | reviewer | rule-pack pipeline: official source -> draft -> human approval -> publish |
| GET /admin/review-queue, POST /admin/review-queue/{doc_id}/resolve | reviewer | documents citizens asked a human to check (metadata only) |
| GET /metrics | `X-Metrics-Token` | Prometheus-style errors, latency, model usage |
| GET /audit/verify, /audit/events | login | hash-chain verification, own events |
| GET /judge/telemetry | login + `JUDGE_MODE` | model routing, skill loading, PII masking, human gates |
| GET /mock-portal/form | none | synthetic portal used by the Playwright/mock worker |

## Agent task contract (typed)
```json
{"task":   {"agent": "profile|discovery|eligibility|doc_auditor|app_prep|browser_action|notification",
            "user_id": "...", "language": "hi", "payload": {}},
 "result": {"agent": "...", "status": "ok|needs_consent|needs_info|handoff", "language": "hi", "data": {}, "human_gate": 1}}
```

## Finding shape (Doc Auditor / readiness)
`{"code":"EXPIRED","severity":"blocking","message":"...","fix":"Obtain a fresh certificate...","doc_id":"..."}`

## Frontend TypeScript types (suggested)
```ts
type Severity = "blocking" | "warning" | "passed" | "unknown";
interface Finding { code: string; severity: Severity; message: string; fix: string; doc_id?: string }
interface Criterion { id: string; label: string; status: "met" | "unknown" | "not_met" }
interface SchemeCard { scheme_id: string; name: string; benefit: string; deadline: string | null; source_url: string;
  last_verified: string | null; verification_status: "verified" | "unverified_seed"; overall: string;
  criteria: Criterion[]; preliminary_estimate: true; explanation: string }
interface Readiness { blocking: Finding[]; warning: Finding[]; passed: Finding[]; unknown: Finding[]; ready: boolean; disclaimer: string }
```
