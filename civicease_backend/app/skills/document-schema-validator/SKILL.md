---
name: document-schema-validator
description: Validate extracted document fields against the required schema for the document type. Use in the Doc Auditor step.
---
# Document schema validator
Inputs: doc_type, extracted fields, confidence, quality.
Steps: 1) unknown type or confidence < 0.6 => UNKNOWN; 2) missing required fields => blocking;
3) expiry in the past => blocking, within 30 days => warning; 4) cross-check names across documents.
Output: findings with severity (blocking | warning | passed | unknown) and a one-line fix each.
Do not echo raw ID numbers; mask to the last 4 digits.
