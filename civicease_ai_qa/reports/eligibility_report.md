# Eligibility agreement

> Labels are hand-written (synth/make_eligibility_cases.py). A disagreement can be a rule bug or a labelling error.

## Acceptance gates

| metric | value | rule | pass |
|---|---|---|---|
| eligibility_agreement | 1.000 | >= 1.0 | True |
| false_likely_met | 0 | == 0 | True |
| never_guesses_on_missing | True | is True | True |

## Confusion Matrix

| expected | likely_met | unknown | not_met |
|---|---|---|---|
| likely_met | 8 | 0 | 0 |
| unknown | 0 | 11 | 0 |
| not_met | 0 | 0 | 13 |

## Disagreements

_none_
