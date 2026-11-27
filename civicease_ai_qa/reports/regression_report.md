# Regression report (oracle) 2026-11-20

Baseline from 2026-11-20. Changed since baseline: **scheme_rules, skills, rule_code**

| metric | baseline | now | result |
|---|---|---|---|
| extraction.field_accuracy | 1.000 | 1.000 | same |
| extraction.doc_type_accuracy | 1.000 | 1.000 | same |
| extraction.hallucination_rate | 0.000 | 0.000 | same |
| extraction.missing_rate | 0.000 | 0.000 | same |
| extraction.wrong_rate | 0.000 | 0.000 | same |
| extraction.unknown_rate | 0.000 | 0.000 | same |
| extraction.ece | 0.010 | 0.010 | same |
| extraction.name_mismatch_recall | 1.000 | 1.000 | same |
| extraction.name_mismatch_precision | 1.000 | 1.000 | same |
| extraction.expiry_recall | 1.000 | 1.000 | same |
| extraction.missing_field_recall | 1.000 | 1.000 | same |
| eligibility.eligibility_agreement | 1.000 | 1.000 | same |
| eligibility.false_likely_met | 0.000 | 0.000 | same |
| language.language_parse_accuracy | 0.778 | 1.000 | improved |
| language.wrong_values | 0.000 | 0.000 | same |

Tracked inputs changed (scheme_rules, skills, rule_code) with no metric regression. If the change was intended, run --update-baseline.