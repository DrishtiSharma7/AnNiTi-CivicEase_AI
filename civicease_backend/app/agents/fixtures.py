"""Deterministic SYNTHETIC extraction results for the demo (USE_MOCK_LLM=true).
Keyed by file name. All values are dummy data, never real identity details."""
from datetime import date, timedelta


def lookup(filename: str):
    name = filename.lower()
    t = date.today()
    D = lambda days: (t + timedelta(days=days)).isoformat()
    table = {
        "ramesh_aadhaar": {"doc_type": "aadhaar", "fields": {"name": "Ramesh Kumar", "dob": "1964-04-12", "id_number": "9999 8888 7777"}},
        # name spelled "Ramesh Kr." and certificate expired two months ago
        "ramesh_income": {"doc_type": "income_certificate", "fields": {"name": "Ramesh Kr.", "annual_income": 90000, "valid_until": D(-60)}},
        "sunita_aadhaar": {"doc_type": "aadhaar", "fields": {"name": "Sunita Devi", "dob": "1962-08-03", "id_number": "9999 7777 6666"}},
        "sunita_income": {"doc_type": "income_certificate", "fields": {"name": "Sunita Devi", "annual_income": 60000, "valid_until": D(300)}},
    }
    for key, val in table.items():
        if key in name:
            fc = {k: 0.97 for k in val["fields"]}
            if "ramesh_income" in key:
                fc["name"] = 0.88  # abbreviated name read with lower confidence
            return {**val, "field_confidence": fc, "confidence": 0.96, "quality": "clear", "warnings": ["SYNTHETIC DEMO DATA"]}
    return None
