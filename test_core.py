"""Pure-module tests: crypto, PII, hash chain, eligibility, document audit, trust guard, portal policy."""
import os
from datetime import date, timedelta

from app import docaudit, eligibility, embedding, hashchain, kms, pdfgen, pii, portal, profile_parse, rules, trust
from app import security as sec

T = date(2026, 11, 17)


def test_envelope_encryption_roundtrip_and_binding():
    k = kms.LocalKMS(os.urandom(32))
    blob, wrapped = sec.encrypt_document(b"hello", k, b"user1:doc1")
    assert sec.decrypt_document(blob, wrapped, k, b"user1:doc1") == b"hello"
    for bad_aad in (b"user2:doc1", b"user1:doc2"):  # bound to user and document
        try:
            sec.decrypt_document(blob, wrapped, k, bad_aad)
            assert False, "AAD binding should fail"
        except Exception:
            pass
    b2, w2 = sec.encrypt_document(b"hello", k, b"user1:doc1")
    assert w2 != wrapped and b2 != blob  # unique data key per encryption


def test_id_digest_is_salted_and_masked():
    a = sec.id_digest("9999 8888 7777", "salt1", "pep")
    assert a == sec.id_digest("999988887777", "salt1", "pep")
    assert a != sec.id_digest("9999 8888 7777", "salt2", "pep")
    assert sec.mask_id("9999 8888 7777") == "********7777"


def test_signed_token_expiry_and_tamper():
    key = sec.derive_key("p", "approval")
    t = sec.sign_payload({"x": 1}, key, 60)
    assert sec.verify_payload(t, key)["x"] == 1
    assert sec.verify_payload(t + "a", key) is None
    assert sec.verify_payload(sec.sign_payload({"x": 1}, key, -1), key) is None
    assert sec.verify_payload(t, sec.derive_key("p", "file-url")) is None


def test_form_hash_changes_when_form_changes():
    assert sec.form_hash({"a": 1}) != sec.form_hash({"a": 2})
    assert sec.form_hash({"a": 1, "b": 2}) == sec.form_hash({"b": 2, "a": 1})


def test_pii_redaction():
    text, counts = pii.redact_text("Aadhaar 9999 8888 7777, PAN ABCDE1234F, call 9876543210, a@b.co")
    assert "9999" not in text and "ABCDE1234F" not in text and "9876543210" not in text
    assert set(counts) == {"AADHAAR", "PAN", "PHONE", "EMAIL"}
    assert pii.redact_obj({"k": ["999988887777"]}) == {"k": ["[AADHAAR_REDACTED]"]}


def test_hash_chain_detects_tampering_and_removal():
    evs, prev = [], hashchain.GENESIS
    for i in range(3):
        d = {"n": i}
        h = hashchain.compute_hash(prev, f"t{i}", "u", "act", d)
        evs.append({"ts": f"t{i}", "actor": "u", "action": "act", "detail": d, "prev_hash": prev, "hash": h})
        prev = h
    assert hashchain.verify_chain(evs)["valid"]
    bad = [dict(e) for e in evs]
    bad[1]["detail"] = {"n": 99}
    assert not hashchain.verify_chain(bad)["valid"]
    assert not hashchain.verify_chain([evs[0], evs[2]])["valid"]


def test_eligibility_unknown_not_guess():
    crit = [{"id": "a", "label": "age", "field": "age", "op": ">=", "value": 60},
            {"id": "i", "label": "inc", "field": "annual_income", "op": "<=", "value": 100000}]
    assert eligibility.evaluate(crit, {"age": 62, "annual_income": 50000})["overall"] == "likely_met"
    assert eligibility.evaluate(crit, {"age": 62})["overall"] == "unknown"
    assert eligibility.evaluate(crit, {"age": 30})["overall"] == "not_met"
    assert eligibility.evaluate(crit, {})["preliminary_estimate"] is True


def _doc(i, t, fields, conf=0.96, q="clear"):
    return {"id": i, "doc_type": t, "fields": fields, "confidence": conf, "quality": q}


def test_persona_a_broken_case():
    docs = [_doc("1", "aadhaar", {"name": "Ramesh Kumar", "dob": "1964-04-12", "id_number": "********7777"}),
            _doc("2", "income_certificate", {"name": "Ramesh Kr.", "annual_income": 90000,
                                              "valid_until": (T - timedelta(days=60)).isoformat()})]
    r = docaudit.build_readiness(["aadhaar", "income_certificate"], docs, {}, T)
    codes = {f["code"] for f in r["blocking"]}
    assert {"EXPIRED", "NAME_MISMATCH"} <= codes and r["ready"] is False


def test_persona_b_clean_case():
    docs = [_doc("1", "aadhaar", {"name": "Sunita Devi", "dob": "1962-08-03", "id_number": "********6666"}),
            _doc("2", "income_certificate", {"name": "Sunita Devi", "annual_income": 60000,
                                              "valid_until": (T + timedelta(days=300)).isoformat()})]
    r = docaudit.build_readiness(["aadhaar", "income_certificate"], docs, {"annual_income": 60000}, T)
    assert r["ready"] and not r["blocking"] and not r["unknown"]


def test_missing_document_and_low_confidence():
    r = docaudit.build_readiness(["aadhaar", "income_certificate"],
                                 [_doc("1", "aadhaar", {"name": "A", "dob": "1990-01-01", "id_number": "1"}, conf=0.3)], {}, T)
    assert any(f["code"] == "MISSING_DOCUMENT" for f in r["blocking"])
    assert any(f["code"] == "LOW_CONFIDENCE" for f in r["unknown"]) and not r["ready"]


def test_trust_guard():
    assert trust.guard({"m": "Your application will be approved"}, "x")["status"] == "blocked_by_trust_guard"
    assert trust.guard({"m": "It does not guarantee acceptance"}, "x") == {"m": "It does not guarantee acceptance"}
    assert trust.guard({"m": "we bypass the OTP"}, "x")["status"] == "blocked_by_trust_guard"
    card = {"scheme_id": "s", "source_url": "u", "preliminary_estimate": True}  # last_verified key missing
    assert trust.guard({"schemes": [card]}, "scheme_match")["status"] == "blocked_by_trust_guard"
    assert "REDACTED" in trust.guard({"m": "id 999988887777"}, "x")["m"]


def test_portal_policy():
    ok_plan = portal.build_plan("http://localhost:8000", {"name": "A"})
    portal.validate_plan(ok_plan, ("localhost",))
    for bad in ([{"action": "click", "selector": "#x"}],
                [{"action": "goto", "url": "https://evil.example/"}],
                [{"action": "next", "selector": "#submit-btn"}],
                [{"action": "fill", "selector": "[name=captcha]", "value": "1"}]):
        try:
            portal.validate_plan(bad, ("localhost",))
            assert False, bad
        except portal.PortalViolation:
            pass
    assert portal.run_simulated(ok_plan)[-1]["gate"] == 4


def test_request_signing_for_worker():
    ts = int(__import__("time").time())
    sig = sec.sign_request("secret", ts, b"{}")
    assert sec.verify_request("secret", ts, b"{}", sig)
    assert not sec.verify_request("secret", ts, b"{ }", sig)
    assert not sec.verify_request("other", ts, b"{}", sig)
    assert not sec.verify_request("secret", ts - 600, b"{}", sec.sign_request("secret", ts - 600, b"{}"))


def test_profile_intake_parsing_and_never_guessing():
    assert profile_parse.parse_number("2.5 lakh") == 250000
    assert profile_parse.parse_number("\u0967\u0968,\u0966\u0966\u0966") == 12000  # Devanagari digits
    assert profile_parse.parse_answer("occupation", "\u092e\u0948\u0902 \u0915\u093f\u0938\u093e\u0928 \u0939\u0942\u0901") == "FARMER"
    for field, bad in (("age", "very old"), ("age", "500"), ("category", "purple")):
        try:
            profile_parse.parse_answer(field, bad)
            assert False, (field, bad)
        except ValueError:
            pass
    d = profile_parse.apply_answer({}, "occupation", "student")
    assert d["is_student"] is True
    assert profile_parse.next_question({"age": 30, "occupation": "FARMER", "annual_income": 1, "category": "SC",
                                        "state": "BIHAR", "gender": "MALE"})["field"] == "land_holding_hectares"
    skipped = profile_parse.apply_answer({}, "age", "skip")
    assert profile_parse.next_question(skipped)["field"] == "occupation"
    assert "\u0909\u092e\u094d\u0930" in profile_parse.next_question({}, "hi")["question"]


def test_rule_pack_validation_and_official_sources():
    draft = rules.mock_extract("Old Age Pension\nMonthly pension.\nAged 60 years or above; family income should not exceed Rs 1,00,000.")
    assert rules.validate_draft(draft) == []
    assert {c["field"] for c in draft["criteria"]} == {"age", "annual_income"}
    bad = {"name": "x", "criteria": [{"id": "a", "label": "l", "field": "password", "op": "==", "value": "1"}]}
    assert rules.validate_draft(bad)
    assert rules.validate_draft({"name": "x", "criteria": [{"id": "a", "label": "l", "field": "age", "op": "exec", "value": 1}]})
    assert rules.is_official_url("https://nsap.nic.in/page")
    assert not rules.is_official_url("https://evil.example/gov.in")
    assert not rules.is_official_url("http://nsap.nic.in/page")
    assert not rules.is_official_url("https://gov.in.evil.example/")


def test_checklist_pdf_and_embeddings():
    pdf = pdfgen.build_pdf(["Checklist (a)", "[x] aadhaar"] + [f"line {i}" for i in range(80)])
    assert pdf.startswith(b"%PDF-1.4") and pdf.rstrip().endswith(b"%%EOF")
    a, b, c = (embedding.hashed_embedding(t) for t in ("old age pension senior", "pension senior citizens", "farmer land crop"))
    assert embedding.cosine(a, b) > embedding.cosine(a, c)
