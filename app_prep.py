from app.security import form_hash

FORM_FIELDS = ("name", "dob", "state", "annual_income", "id_last4")


def build_form(profile: dict, docs: list) -> dict:
    """Pre-fill from the profile and audited documents. IDs appear only as the last 4 characters."""
    form: dict = {}
    for d in docs:
        f = d.extracted or {}
        if d.doc_type == "aadhaar":
            form.setdefault("name", f.get("name"))
            form.setdefault("dob", f.get("dob"))
            if f.get("id_number"):
                form["id_last4"] = str(f["id_number"])[-4:]
        elif d.doc_type == "income_certificate":
            form.setdefault("name", f.get("name"))
            form["annual_income"] = f.get("annual_income")
    if profile.get("state"):
        form["state"] = profile["state"]
    return {k: v for k, v in form.items() if k in FORM_FIELDS and v is not None}


def checklist(required: list, docs: list) -> list:
    have = {d.doc_type for d in docs}
    return [{"document": r, "uploaded": r in have} for r in required]


def hash_of(form: dict) -> str:
    return form_hash(form)
