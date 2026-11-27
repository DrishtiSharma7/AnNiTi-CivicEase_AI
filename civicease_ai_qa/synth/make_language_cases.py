"""Hand-labelled answers a citizen might give to the Profile agent, in Hindi, English and Hinglish.
EXPECTED is what a human would take the answer to mean; REASK means the system should ask again (never guess)."""
import csv
from pathlib import Path

CASES = [
    # field, utterance, language, expected
    ("age", "62", "en", "62"), ("age", "62 साल", "hi", "62"), ("age", "५५", "hi", "55"), ("age", "I am 40 years old", "en", "40"),
    ("age", "बासठ", "hi", "62"), ("age", "sixty two", "en", "62"), ("age", "500", "en", "REASK"), ("age", "very old", "en", "REASK"),
    ("annual_income", "₹60,000", "en", "60000"), ("annual_income", "60 हजार", "hi", "60000"), ("annual_income", "2.5 lakh", "en", "250000"),
    ("annual_income", "ढाई लाख", "hi", "250000"), ("annual_income", "1 lakh", "en", "100000"), ("annual_income", "५० हज़ार", "hi", "50000"),
    ("annual_income", "kuch nahi", "hi", "REASK"), ("annual_income", "pata nahi", "hi", "REASK"),
    ("occupation", "kisan", "hi", "FARMER"), ("occupation", "मैं किसान हूँ", "hi", "FARMER"), ("occupation", "student", "en", "STUDENT"),
    ("occupation", "छात्र", "hi", "STUDENT"), ("occupation", "mazdoor", "hi", "DAILY_WAGE"), ("occupation", "मजदूर", "hi", "DAILY_WAGE"),
    ("occupation", "I run a small shop", "en", "SELF_EMPLOYED"), ("occupation", "nokri", "hi", "SALARIED"),
    ("category", "sc", "en", "SC"), ("category", "OBC", "en", "OBC"), ("category", "सामान्य", "hi", "GENERAL"),
    ("category", "general category", "en", "GENERAL"), ("category", "scheduled caste", "en", "SC"), ("category", "purple", "en", "REASK"),
    ("state", "Bihar", "en", "BIHAR"), ("state", "बिहार", "hi", "बिहार"), ("state", "x", "en", "REASK"),
    ("gender", "महिला", "hi", "FEMALE"), ("gender", "female", "en", "FEMALE"), ("gender", "aurat", "hi", "FEMALE"),
]
if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "language_cases.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "field", "utterance", "language", "expected"])
        for i, row in enumerate(CASES, 1):
            w.writerow([f"L{i:02d}", *row])
    print(f"wrote {len(CASES)} cases -> {out}")
