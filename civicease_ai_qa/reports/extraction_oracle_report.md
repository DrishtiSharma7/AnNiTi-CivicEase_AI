# Extraction and audit evaluation (oracle)

> extractor=oracle; documents=48; reference date=2026-11-20; SYNTHETIC data only

## Acceptance gates

| metric | value | rule | pass |
|---|---|---|---|
| field_accuracy | 1.000 | >= 0.9 | True |
| doc_type_accuracy | 1.000 | >= 0.95 | True |
| hallucination_rate | 0.000 | <= 0.05 | True |
| name_mismatch_recall | 1.000 | >= 0.95 | True |
| name_mismatch_precision | 1.000 | >= 0.9 | True |
| expiry_recall | 1.000 | >= 1.0 | True |
| ece | 0.010 | <= 0.15 | True |

## Field Errors

_none_

## By Condition

| condition | field_accuracy |
|---|---|
| blurry | 1.000 |
| clear | 1.000 |
| cropped | 1.000 |
| expired | 1.000 |
| expiring_soon | 1.000 |
| lowres | 1.000 |
| missing_field | 1.000 |
| name_mismatch | 1.000 |

## Finding Metrics

| code | tp | fp | fn | precision | recall | f1 |
|---|---|---|---|---|---|---|
| EXPIRED | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| EXPIRING_SOON | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| NAME_MISMATCH | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| MISSING_FIELD | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| QUALITY_BLURRY | 12 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| QUALITY_CROPPED | 6 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| LOW_CONFIDENCE | 0 | 0 | 0 | nan | nan | nan |
| DOC_TYPE_UNKNOWN | 0 | 0 | 0 | nan | nan | nan |
