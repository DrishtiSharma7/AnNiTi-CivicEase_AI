---
name: eligibility-router
description: Route a citizen profile to scheme rule packs and return a per-criterion verdict. Use whenever eligibility is requested.
---
# Eligibility router
Inputs: citizen profile (age, income, category, occupation, state), scheme rule pack.
Steps: 1) evaluate each criterion deterministically; 2) missing field => UNKNOWN and ask the citizen;
3) overall = not_met if any not_met, unknown if any unknown, else likely_met.
Output: criteria chips (met / unknown / not_met), source_url, last_verified, `preliminary_estimate: true`.
Never let free-form model text override a rule verdict. Never promise acceptance.
