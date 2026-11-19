"""End-to-end API tests (need the packages in requirements.txt). Run: pytest -q"""
PDF = b"%PDF-1.4 synthetic demo"


def consent(client, h, kind, granted=True):
    assert client.post("/consents", json={"kind": kind, "granted": granted}, headers=h).status_code == 200


def upload(client, h, name, salt=b""):
    r = client.post("/documents", files={"file": (name, PDF + salt, "application/pdf")}, headers=h)
    assert r.status_code == 200, r.text
    return r.json()["data"]["id"]


def test_auth_required_and_consent_gates(client, auth):
    assert client.get("/profile").status_code == 401
    assert client.get("/profile", headers=auth).json()["error"]["code"] == "CONSENT_REQUIRED"
    r = client.post("/documents", files={"file": ("a.pdf", PDF, "application/pdf")}, headers=auth)
    assert r.json()["error"]["code"] == "CONSENT_REQUIRED"


def test_upload_validation(client, auth):
    consent(client, auth, "document_use")
    bad = client.post("/documents", files={"file": ("x.pdf", b"not a pdf", "application/pdf")}, headers=auth)
    assert bad.status_code == 415


def test_persona_a_blocked_then_persona_b_full_flow(client, auth):
    consent(client, auth, "profile")
    consent(client, auth, "document_use")
    client.put("/profile", json={"language": "hi", "age": 62, "annual_income": 60000}, headers=auth)
    disc = client.get("/agents/discover", headers=auth).json()["data"]["schemes"]
    assert any(s["scheme_id"] == "old-age-pension" for s in disc)
    assert all(s["preliminary_estimate"] and "source_url" in s for s in disc)

    # Persona B (clean) -> ready -> all gates -> submit
    for name in ("sunita_aadhaar.pdf", "sunita_income.pdf"):
        doc_id = upload(client, auth, name, salt=name.encode())
        a = client.post(f"/documents/{doc_id}/audit", headers=auth).json()["data"]
        assert "id_number" not in str(a) or "********" in str(a)
    app_id = client.post("/applications", json={"scheme_id": "old-age-pension"}, headers=auth).json()["data"]["id"]
    base = f"/applications/{app_id}"
    # gates cannot be skipped
    assert client.post(f"{base}/prepare", headers=auth).json()["error"]["code"] == "GATE3_REQUIRED"
    rep = client.post(f"{base}/readiness", headers=auth).json()["data"]
    assert rep["ready"] is True
    assert client.post(f"{base}/gates/3/approve", json={"confirm": True}, headers=auth).status_code == 200
    prep = client.post(f"{base}/prepare", headers=auth).json()["data"]
    assert prep["form"]["name"] == "Sunita Devi" and prep["form"]["id_last4"] == "6666"
    assert client.post(f"{base}/approval-token", headers=auth).json()["error"]["code"] == "GATES_INCOMPLETE"
    pre = client.post(f"{base}/prefill", headers=auth).json()["data"]["log"]
    assert pre[-1]["action"] == "handoff" and pre[-1]["gate"] == 4
    assert client.post(f"{base}/gates/4/complete", json={"confirm": True}, headers=auth).status_code == 200
    tok = client.post(f"{base}/approval-token", headers=auth).json()["data"]["approval_token"]
    # editing the form after approval invalidates the token
    client.patch(f"{base}/form", json={"fields": {"state": "BIHAR"}}, headers=auth)
    stale = client.post(f"{base}/submit", json={"approval_token": tok, "confirm": True}, headers=auth)
    assert stale.json()["error"]["code"] == "APPROVAL_INVALID"
    # redo gate 4 + token, then submit
    client.post(f"{base}/prefill", headers=auth)
    client.post(f"{base}/gates/4/complete", json={"confirm": True}, headers=auth)
    tok2 = client.post(f"{base}/approval-token", headers=auth).json()["data"]["approval_token"]
    done = client.post(f"{base}/submit", json={"approval_token": tok2, "confirm": True}, headers=auth)
    assert done.json()["data"]["status"] == "submitted"
    assert client.get("/audit/verify", headers=auth).json()["data"]["valid"] is True
    kinds = {e["kind"] for e in client.get("/judge/telemetry", headers=auth).json()["data"]}
    assert {"skill_loaded", "pii_masking", "human_gate", "model_routing"} <= kinds


def test_persona_a_is_blocked(client, auth):
    consent(client, auth, "profile")
    consent(client, auth, "document_use")
    client.put("/profile", json={"age": 62, "annual_income": 90000}, headers=auth)
    for name in ("ramesh_aadhaar.pdf", "ramesh_income.pdf"):
        client.post(f"/documents/{upload(client, auth, name, salt=name.encode())}/audit", headers=auth)
    app_id = client.post("/applications", json={"scheme_id": "old-age-pension"}, headers=auth).json()["data"]["id"]
    rep = client.post(f"/applications/{app_id}/readiness", headers=auth).json()["data"]
    codes = {f["code"] for f in rep["blocking"]}
    assert {"EXPIRED", "NAME_MISMATCH"} <= codes and rep["ready"] is False
    r = client.post(f"/applications/{app_id}/gates/3/approve", json={"confirm": True}, headers=auth)
    assert r.json()["error"]["code"] == "NOT_READY"


def test_cross_user_isolation_and_delete(client, auth):
    consent(client, auth, "document_use")
    doc_id = upload(client, auth, "sunita_aadhaar.pdf")
    other = client.post("/auth/register", json={"email": "other@example.com", "password": "another-long-pass"})
    h2 = {"Authorization": "Bearer " + other.json()["data"]["access_token"]}
    assert client.get(f"/documents/{doc_id}", headers=h2).status_code == 404
    link = client.get(f"/documents/{doc_id}/link", headers=auth).json()["data"]["url"]
    assert client.get(link).content == PDF
    assert client.delete("/me", headers=auth).status_code == 200
    assert client.get("/auth/me", headers=auth).status_code == 401
    assert client.get("/audit/verify", headers=h2).json()["data"]["valid"] is True


def test_chat_routes_and_asks_for_consent(client, auth):
    r = client.post("/agents/chat", json={"message": "which scheme can I get?"}, headers=auth).json()["data"]
    assert r["result"]["status"] == "needs_consent" and r["result"]["human_gate"] == 1


# ---- additions for the proposal's remaining conditions -------------------------------------
OFFICIAL = "https://nsap.nic.in/scheme/pension"
PENSION_TEXT = ("Test Pension Scheme\nMonthly pension for senior citizens.\n"
                "Applicants must be aged 60 years or above and family income should not exceed Rs 1,00,000.")


def test_profile_agent_asks_one_question_at_a_time_and_never_guesses(client, auth):
    consent(client, auth, "profile")
    q = client.get("/agents/profile/next", headers=auth).json()["data"]
    assert q["field"] == "age" and q["why"]
    bad = client.post("/agents/profile/answer", json={"field": "age", "answer": "very old"}, headers=auth)
    assert bad.json()["error"]["code"] == "ANSWER_NOT_UNDERSTOOD"
    nxt = client.post("/agents/profile/answer", json={"field": "age", "answer": "62"}, headers=auth).json()["data"]
    assert nxt["field"] == "occupation"
    chat = client.post("/agents/chat", json={"message": "which scheme can I get?", "language": "hi"}, headers=auth).json()["data"]
    assert chat["result"]["language"] == "hi" and chat["result"]["status"] in ("ok", "needs_info")


def test_withdrawing_consent_removes_data(client, auth):
    consent(client, auth, "profile")
    consent(client, auth, "document_use")
    client.put("/profile", json={"age": 62}, headers=auth)
    upload(client, auth, "sunita_aadhaar.pdf")
    consent(client, auth, "document_use", granted=False)
    consent(client, auth, "document_use", granted=True)
    assert client.get("/documents", headers=auth).json()["data"] == []
    consent(client, auth, "profile", granted=False)
    consent(client, auth, "profile", granted=True)
    assert client.get("/profile", headers=auth).json()["data"] == {}


def test_confirm_field_and_ask_human_and_review_queue(client, auth, reviewer):
    consent(client, auth, "document_use")
    doc_id = upload(client, auth, "blurry_unknown.pdf")  # not a persona file -> UNKNOWN in mock mode
    r = client.post(f"/documents/{doc_id}/audit", headers=auth).json()["data"]
    assert any(f["severity"] == "unknown" for f in r["findings"])
    client.post(f"/documents/{doc_id}/confirm-field", json={"field": "doc_type", "value": "aadhaar"}, headers=auth)
    for f, v in (("name", "Asha Devi"), ("dob", "2001-02-03"), ("id_number", "9999 8888 7777")):
        out = client.post(f"/documents/{doc_id}/confirm-field", json={"field": f, "value": v}, headers=auth).json()["data"]
    assert out["fields"]["id_number"] == "********7777"
    assert not [x for x in out["findings"] if x["severity"] in ("blocking", "unknown")]
    assert client.post(f"/documents/{doc_id}/ask-human", headers=auth).json()["data"]["human_review"] == "requested"
    q = client.get("/admin/review-queue", headers=reviewer).json()["data"]
    assert any(i["document_id"] == doc_id for i in q) and "name" not in str(q)
    assert client.get("/admin/review-queue", headers=auth).json()["error"]["code"] == "FORBIDDEN"
    client.post(f"/admin/review-queue/{doc_id}/resolve", json={"note": "looks fine"}, headers=reviewer)
    assert client.get(f"/documents/{doc_id}", headers=auth).json()["data"]["human_review"] == "resolved"


def test_rule_pack_pipeline_needs_official_source_and_second_reviewer(client, reviewer):
    body = {"source_url": OFFICIAL, "text": PENSION_TEXT, "pack": "Central schemes", "scheme_id": "test-pension"}
    assert client.post("/admin/rulepacks/ingest", json={**body, "source_url": "https://evil.example/x"}, headers=reviewer).status_code == 422
    rp = client.post("/admin/rulepacks/ingest", json=body, headers=reviewer).json()["data"]
    assert rp["status"] == "draft"
    assert client.get("/schemes/test-pension").status_code == 404  # nothing published yet
    assert client.post(f"/admin/rulepacks/{rp['id']}/approve", json={}, headers=reviewer).json()["error"]["code"] == "FOUR_EYES"
    r2 = client.post("/auth/register", json={"email": "second@example.com", "password": "correct-horse-battery"})
    if r2.status_code == 409:
        r2 = client.post("/auth/login", json={"email": "second@example.com", "password": "correct-horse-battery"})
    h2 = {"Authorization": "Bearer " + r2.json()["data"]["access_token"]}
    assert client.post(f"/admin/rulepacks/{rp['id']}/approve", json={"note": "checked vs source"}, headers=h2).status_code == 200
    s = client.get("/schemes/test-pension").json()["data"]
    assert s["verification_status"] == "verified" and s["last_verified"] and s["source_url"] == OFFICIAL


def test_scheme_search_filters_and_packs(client):
    hits = client.get("/schemes", params={"q": "pension for senior citizens"}).json()["data"]
    assert hits["results"] and "not eligibility" in hits["note"]
    assert all(s["pack"] == "Healthcare benefits" for s in client.get("/schemes", params={"pack": "Healthcare benefits"}).json()["data"]["results"])
    assert "Scholarships" in client.get("/schemes/packs").json()["data"]


def test_pin_export_dashboard_checklist_voice_metrics(client, auth):
    assert client.put("/auth/pin", json={"pin": "1234"}, headers=auth).status_code == 200
    assert client.post("/auth/pin/verify", json={"pin": "1234"}, headers=auth).json()["data"]["unlocked"] is True
    for _ in range(5):
        client.post("/auth/pin/verify", json={"pin": "0000"}, headers=auth)
    assert client.post("/auth/pin/verify", json={"pin": "1234"}, headers=auth).json()["error"]["code"] == "PIN_LOCKED"
    consent(client, auth, "profile")
    consent(client, auth, "document_use")
    client.put("/profile", json={"age": 62, "annual_income": 60000}, headers=auth)
    assert client.get("/dashboard", headers=auth).json()["data"]["recommended_schemes"]
    app_id = client.post("/applications", json={"scheme_id": "old-age-pension"}, headers=auth).json()["data"]["id"]
    pdf = client.get(f"/applications/{app_id}/checklist.pdf", headers=auth)
    assert pdf.content.startswith(b"%PDF") and pdf.headers["content-type"] == "application/pdf"
    exp = client.get("/me/export", headers=auth).json()["data"]
    assert exp["profile"]["age"] == 62 and exp["applications"]
    wav = client.post("/voice/speak", json={"text": "hello", "language": "en"}, headers=auth)
    assert wav.content[:4] == b"RIFF"
    tr = client.post("/voice/transcribe", files={"audio": ("a.wav", b"RIFF....", "audio/wav")}, data={"language": "hi"}, headers=auth)
    assert tr.json()["data"]["text"]
    assert client.get("/metrics").status_code == 404
    m = client.get("/metrics", headers={"X-Metrics-Token": "test-metrics"})
    assert m.status_code == 200 and "http_requests_total" in m.text
