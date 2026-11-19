"""Seed scheme rule packs. ILLUSTRATIVE ONLY: a human reviewer must verify each rule against the
official source and set last_verified before these are shown as verified (see README)."""

SCHEMES = [
    {
        "id": "pm-kisan", "pack": "Agricultural welfare", "name": "PM-KISAN (farmer income support)",
        "benefit": "Income support for farmer families, paid in instalments (verify current amount).",
        "state": "ALL", "deadline": None, "source_url": "https://pmkisan.gov.in/",
        "required_documents": ["aadhaar", "land_record"], "skill": "scheme-pm-kisan",
        "criteria": [
            {"id": "occupation", "label": "Occupation is farmer", "field": "occupation", "op": "==", "value": "FARMER"},
            {"id": "land", "label": "Owns cultivable land", "field": "land_holding_hectares", "op": ">", "value": 0},
        ],
    },
    {
        "id": "pm-jay", "pack": "Healthcare benefits", "name": "Ayushman Bharat PM-JAY (health cover)",
        "benefit": "Hospital cover for eligible families (verify current cover and eligibility list).",
        "state": "ALL", "deadline": None, "source_url": "https://pmjay.gov.in/",
        "required_documents": ["aadhaar", "income_certificate"], "skill": None,
        "criteria": [
            {"id": "income", "label": "Annual income up to Rs 2,50,000 (ILLUSTRATIVE)", "field": "annual_income", "op": "<=", "value": 250000},
        ],
    },
    {
        "id": "post-matric-scholarship", "pack": "Scholarships", "name": "Post-matric scholarship",
        "benefit": "Tuition and maintenance support for eligible students (verify per state).",
        "state": "ALL", "deadline": None, "source_url": "https://scholarships.gov.in/",
        "required_documents": ["aadhaar", "income_certificate", "marksheet"], "skill": None,
        "criteria": [
            {"id": "student", "label": "Currently a student", "field": "is_student", "op": "==", "value": True},
            {"id": "income", "label": "Annual income up to Rs 2,50,000 (ILLUSTRATIVE)", "field": "annual_income", "op": "<=", "value": 250000},
        ],
    },
    {
        "id": "old-age-pension", "pack": "Central schemes", "name": "Old-age pension",
        "benefit": "Monthly pension for senior citizens (amount and rules vary by state).",
        "state": "ALL", "deadline": None, "source_url": "https://nsap.nic.in/",
        "required_documents": ["aadhaar", "income_certificate"], "skill": None,
        "criteria": [
            {"id": "age", "label": "Age 60 or above", "field": "age", "op": ">=", "value": 60},
            {"id": "income", "label": "Annual income up to Rs 1,00,000 (ILLUSTRATIVE)", "field": "annual_income", "op": "<=", "value": 100000},
        ],
    },
    {
        "id": "maternity-benefit", "pack": "Women and child welfare", "name": "Maternity benefit (illustrative)",
        "benefit": "Cash support for eligible women during pregnancy (verify current rules).",
        "state": "ALL", "deadline": None, "source_url": "https://wcd.nic.in/",
        "required_documents": ["aadhaar"], "skill": None,
        "criteria": [
            {"id": "gender", "label": "Woman applicant", "field": "gender", "op": "==", "value": "FEMALE"},
            {"id": "age", "label": "Age 19 or above (ILLUSTRATIVE)", "field": "age", "op": ">=", "value": 19},
        ],
    },
    {
        "id": "skill-training", "pack": "Employment and skills", "name": "Skill training scheme (illustrative)",
        "benefit": "Short-term skill training with certification (verify current rules).",
        "state": "ALL", "deadline": None, "source_url": "https://www.msde.gov.in/",
        "required_documents": ["aadhaar"], "skill": None,
        "criteria": [
            {"id": "age", "label": "Age 15 or above (ILLUSTRATIVE)", "field": "age", "op": ">=", "value": 15},
            {"id": "age_max", "label": "Age 45 or below (ILLUSTRATIVE)", "field": "age", "op": "<=", "value": 45},
        ],
    },
]

PACKS = ["Central schemes", "State schemes", "Scholarships", "Healthcare benefits", "Agricultural welfare",
         "Women and child welfare", "Employment and skills"]
