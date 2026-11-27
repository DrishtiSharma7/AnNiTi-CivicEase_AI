---
name: document-schema-validator
description: Validate fields extracted from a citizen document against the schema for its document type and return audit findings. Use in the Doc Auditor step, after extraction and before any readiness report.
---
# Document schema validator

## Required inputs
- `doc_type` (aadhaar, income_certificate, land_record, caste_certificate, marksheet, ration_card, unknown)
- `fields` extracted by OCR/vision (ID numbers already masked to the last 4 digits)
- `confidence` (0-1), `field_confidence` (0-1 per field), `quality` (clear, blurry, cropped, unknown)
- `today` (date used for expiry; never the model's own idea of the date)

## Validation steps
1. If `doc_type` is unknown, stop: result is UNKNOWN (ask the citizen to retake or choose the type).
2. If `confidence` < 0.6, add LOW_CONFIDENCE (UNKNOWN). Blurry or cropped quality adds a warning with a retake fix.
3. Every required field for the type must be present (aadhaar: name, dob, id_number; income_certificate: name, annual_income, valid_until; land_record: name, land_holding_hectares; caste_certificate: name, category; marksheet: name, institution; ration_card: name). A missing field is blocking.
4. `valid_until` before `today` is blocking (EXPIRED); within 30 days is a warning (EXPIRING_SOON); an unreadable date is UNKNOWN.
5. Cross-check names across the citizen's documents against the Aadhaar name after removing honorifics (Shri, Smt, Dr, ...). Any other difference, including abbreviations such as "Kr.", is a blocking NAME_MISMATCH.

## Output schema
List of findings `{code, severity, message, fix, doc_id}` where severity is blocking, warning, passed or unknown, and every finding carries a one-line fix. See `schemas/readiness.schema.json`.

## Edge cases
- Name written in Devanagari on one document and Latin on another: do not transliterate. Return UNKNOWN and ask the citizen to confirm.
- Two documents with different valid dates for the same certificate: use the document the citizen confirmed; otherwise UNKNOWN.
- Income stated as a range or in words: UNKNOWN, ask the citizen to confirm the number.
- A date in the future for a date of birth: UNKNOWN.

## When the result must be UNKNOWN
Unknown type, low confidence, unreadable dates, conflicting values, a model timeout or quota error, or any field the model could not read. Never fill a gap with a guess and never present UNKNOWN as passed. Log the failure without personal data.
