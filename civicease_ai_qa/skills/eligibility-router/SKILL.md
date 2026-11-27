---
name: eligibility-router
description: Route a citizen profile to a scheme's rule pack and return a per-criterion verdict with source and verification date. Use whenever eligibility is requested.
---
# Eligibility router

## Required inputs
- `profile` fields the citizen consented to share (age, annual_income, category, occupation, state, gender, land_holding_hectares, is_student)
- the scheme rule pack: criteria `{id, label, field, op, value}`, `source_url`, `last_verified`

## Validation steps
1. Evaluate each criterion deterministically with the operator in the rule pack. The model never decides a verdict.
2. A missing, null or wrongly typed profile value makes that criterion `unknown`. Never default it to zero or false.
3. Overall: `not_met` if any criterion is not met; otherwise `unknown` if any is unknown; otherwise `likely_met`.
4. Attach `source_url` and `last_verified`. If the rule pack has not been verified by a human reviewer, say so on the card.

## Output schema
`{overall, criteria: [{id, label, status}], preliminary_estimate: true}` plus the scheme citation. See `schemas/eligibility.schema.json`.

## Edge cases
- Boundaries are inclusive for `<=` and `>=`: age 60 meets "age >= 60".
- A failed criterion outweighs an unknown one: tell the citizen early that they do not qualify.
- Several state-specific variants of a scheme: evaluate only the variant for the citizen's state; if the state is unknown the result is `unknown`.

## When the result must be UNKNOWN
Any required profile field is missing or malformed and no criterion has failed. Ask the citizen for the missing field and explain why it is needed. Always label the result a preliminary estimate; never promise acceptance.
