"""Hand-labelled eligibility cases. The EXPECTED column is written by a person from the rule text in the seed
(not computed by the engine), so a disagreement means either a rule bug or a labelling mistake: look at both.
Rules (from app/seed.py, ILLUSTRATIVE): pm-kisan occupation==FARMER & land>0 | pm-jay income<=250000 |
post-matric-scholarship is_student & income<=250000 | old-age-pension age>=60 & income<=100000 |
maternity-benefit gender==FEMALE & age>=19 | skill-training 15<=age<=45.
overall = not_met if any criterion is not met, else unknown if any is unknown, else likely_met."""
import csv
import json
from pathlib import Path

CASES = [
    # (scheme, profile, expected, why)
    ("pm-kisan", {"occupation": "FARMER", "land_holding_hectares": 2.0}, "likely_met", "both criteria met"),
    ("pm-kisan", {"occupation": "FARMER", "land_holding_hectares": 0}, "not_met", "land must be > 0"),
    ("pm-kisan", {"occupation": "FARMER"}, "unknown", "land missing"),
    ("pm-kisan", {"occupation": "STUDENT", "land_holding_hectares": 1.0}, "not_met", "not a farmer"),
    ("pm-kisan", {"land_holding_hectares": 1.0}, "unknown", "occupation missing"),
    ("pm-kisan", {}, "unknown", "nothing known"),
    ("pm-jay", {"annual_income": 250000}, "likely_met", "boundary: limit is inclusive"),
    ("pm-jay", {"annual_income": 250001}, "not_met", "boundary: one rupee over"),
    ("pm-jay", {"annual_income": 0}, "likely_met", "zero income is valid"),
    ("pm-jay", {}, "unknown", "income missing"),
    ("pm-jay", {"annual_income": None}, "unknown", "explicit null is unknown, not zero"),
    ("post-matric-scholarship", {"is_student": True, "annual_income": 250000}, "likely_met", "boundary met"),
    ("post-matric-scholarship", {"is_student": False, "annual_income": 100000}, "not_met", "not a student"),
    ("post-matric-scholarship", {"is_student": True}, "unknown", "income missing"),
    ("post-matric-scholarship", {"is_student": False}, "not_met", "a failed rule beats an unknown one"),
    ("post-matric-scholarship", {"annual_income": 300000}, "not_met", "income too high even though student is unknown"),
    ("old-age-pension", {"age": 60, "annual_income": 100000}, "likely_met", "both boundaries inclusive"),
    ("old-age-pension", {"age": 59, "annual_income": 100000}, "not_met", "boundary: one year short"),
    ("old-age-pension", {"age": 60, "annual_income": 100001}, "not_met", "boundary: one rupee over"),
    ("old-age-pension", {"age": 75}, "unknown", "income missing"),
    ("old-age-pension", {"annual_income": 50000}, "unknown", "age missing"),
    ("old-age-pension", {"age": 30}, "not_met", "age fails, income unknown"),
    ("old-age-pension", {"age": "62", "annual_income": 50000}, "unknown", "age typed as text: never guess"),
    ("maternity-benefit", {"gender": "FEMALE", "age": 19}, "likely_met", "boundary met"),
    ("maternity-benefit", {"gender": "FEMALE", "age": 18}, "not_met", "boundary: one year short"),
    ("maternity-benefit", {"gender": "MALE", "age": 30}, "not_met", "gender rule"),
    ("maternity-benefit", {"gender": "FEMALE"}, "unknown", "age missing"),
    ("skill-training", {"age": 15}, "likely_met", "lower boundary"),
    ("skill-training", {"age": 45}, "likely_met", "upper boundary"),
    ("skill-training", {"age": 46}, "not_met", "above upper boundary"),
    ("skill-training", {"age": 14}, "not_met", "below lower boundary"),
    ("skill-training", {}, "unknown", "age missing"),
]

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "eligibility_cases.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "scheme_id", "profile_json", "expected", "why"])
        for i, (s, p, e, why) in enumerate(CASES, 1):
            w.writerow([f"E{i:02d}", s, json.dumps(p), e, why])
    print(f"wrote {len(CASES)} cases -> {out}")
