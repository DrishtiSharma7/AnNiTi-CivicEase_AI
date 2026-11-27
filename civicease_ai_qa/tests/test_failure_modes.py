"""Failure-mode tests against the REAL backend code, with the network faked. Covers: model timeout/quota, retry with
backoff, cheapest-model-first escalation, invalid/unreadable model output -> UNKNOWN, PII never sent to a model,
expired/missing/low-confidence documents, unsupported language, daily quota. Runs under pytest or `python tests/run_all.py`."""
import json
import os
import sys
import time
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import qa_config  # noqa: E402,F401

os.environ.update({"USE_MOCK_LLM": "false", "GEMINI_API_KEY": "test-key", "DATABASE_URL": "sqlite://"})
from app.config import get_settings  # noqa: E402

get_settings.cache_clear()
from app import docaudit, llm  # noqa: E402
from datetime import date  # noqa: E402

GOOD = {"doc_type": "aadhaar", "fields": {"name": "A B", "dob": "1990-01-01", "id_number": "9999 0000 1234"},
        "confidence": 0.95, "quality": "clear", "warnings": [], "field_confidence": {}}


def fake_httpx(status=503, raises=None):
    calls = []

    class HTTPError(Exception):
        pass

    def post(url, json=None, headers=None, timeout=None):
        calls.append(url)
        if raises:
            raise raises
        return types.SimpleNamespace(status_code=status, json=lambda: {}, raise_for_status=lambda: None)
    return types.SimpleNamespace(post=post, HTTPError=HTTPError), calls


class RetryAndFallback(unittest.TestCase):
    def test_retries_with_backoff_then_gives_up(self):
        fx, calls = fake_httpx(503)
        sleeps = []
        with mock.patch.dict(sys.modules, {"httpx": fx}), mock.patch.object(llm.time, "sleep", sleeps.append):
            with self.assertRaises(llm.LLMUnavailable):
                llm._post("m", "generateContent", {}, "t")
        self.assertEqual(len(calls), 3)                      # three attempts
        self.assertEqual(sleeps, [0.5, 1.0, 2.0])            # exponential backoff

    def test_timeout_is_retried_like_any_failure(self):
        fx, calls = fake_httpx(raises=TimeoutError("timed out"))
        with mock.patch.dict(sys.modules, {"httpx": fx}), mock.patch.object(llm.time, "sleep", lambda s: None):
            with self.assertRaises(llm.LLMUnavailable):
                llm._post("m", "generateContent", {}, "t")
        self.assertEqual(len(calls), 3)

    def test_quota_error_429_is_retryable_then_unavailable(self):
        fx, calls = fake_httpx(429)
        with mock.patch.dict(sys.modules, {"httpx": fx}), mock.patch.object(llm.time, "sleep", lambda s: None):
            with self.assertRaises(llm.LLMUnavailable):
                llm._post("m", "generateContent", {}, "t")

    def _chain(self, answers):
        s = get_settings()
        seen = []

        def gen(model, parts, task, json_mode=False):
            seen.append(model)
            a = answers[model]
            if isinstance(a, Exception):
                raise a
            return a if isinstance(a, str) else json.dumps(a)
        with mock.patch.object(llm, "_gen", gen):
            return llm._extract_chain([{"text": "x"}], "t"), seen, s

    def test_cheapest_model_first_and_no_escalation_when_confident(self):
        s = get_settings()
        out, seen, _ = self._chain({s.model_lite: GOOD, s.model_flash: GOOD})
        self.assertEqual(seen, [s.model_lite])
        self.assertEqual(out["doc_type"], "aadhaar")

    def test_escalates_to_flash_only_on_low_confidence(self):
        s = get_settings()
        out, seen, _ = self._chain({s.model_lite: {**GOOD, "confidence": 0.4}, s.model_flash: {**GOOD, "confidence": 0.9}})
        self.assertEqual(seen, [s.model_lite, s.model_flash])
        self.assertEqual(out["confidence"], 0.9)

    def test_keeps_lite_result_when_flash_fails(self):
        s = get_settings()
        out, _, _ = self._chain({s.model_lite: {**GOOD, "confidence": 0.5}, s.model_flash: llm.LLMUnavailable("flash")})
        self.assertEqual(out["confidence"], 0.5)

    def test_both_models_down_returns_unknown_not_a_guess(self):
        s = get_settings()
        out, _, _ = self._chain({s.model_lite: llm.LLMUnavailable("a"), s.model_flash: llm.LLMUnavailable("b")})
        self.assertEqual(out["doc_type"], "unknown")
        self.assertEqual(out["confidence"], 0.0)
        self.assertIn("MODEL_UNAVAILABLE", out["warnings"])
        self.assertEqual(out["fields"], {})

    def test_garbage_or_wrong_shaped_output_is_unknown(self):
        s = get_settings()
        for bad in ("not json at all", "[1, 2]", json.dumps({"doc_type": "aadhaar"}), json.dumps({"fields": {}})):
            out, _, _ = self._chain({s.model_lite: bad, s.model_flash: bad})
            self.assertEqual(out["doc_type"], "unknown", bad)

    def test_fenced_json_is_accepted(self):
        s = get_settings()
        fenced = "```json\n" + json.dumps(GOOD) + "\n```"
        out, _, _ = self._chain({s.model_lite: fenced, s.model_flash: fenced})
        self.assertEqual(out["doc_type"], "aadhaar")


class PrivacyAndLanguage(unittest.TestCase):
    def test_personal_numbers_never_reach_the_model_prompt(self):
        sent = []
        with mock.patch.object(llm, "_gen", lambda model, parts, task, json_mode=False: sent.append(parts[0]["text"]) or "ok"):
            llm.explain("Scheme for 999988887777 holder ABCDE1234F", 1, 1, 0, "hi")
        text = " ".join(sent)
        self.assertNotIn("999988887777", text)
        self.assertNotIn("ABCDE1234F", text)

    def test_unsupported_language_still_gets_a_safe_preliminary_answer(self):
        with mock.patch.object(llm, "_gen", side_effect=llm.LLMUnavailable("down")):
            out = llm.explain("Pension", 1, 1, 0, "ta")  # Tamil: not a tested language
        self.assertIn("preliminary estimate", out)

    def test_profile_agent_reasks_instead_of_guessing(self):
        from app import profile_parse
        for field, text in (("age", "not a number"), ("category", "purple"), ("annual_income", "pata nahi")):
            with self.assertRaises(ValueError):
                profile_parse.parse_answer(field, text)


class DocumentFailureCases(unittest.TestCase):
    T = date(2026, 11, 20)

    def doc(self, **kw):
        d = {"id": "d1", "doc_type": "income_certificate", "confidence": 0.95, "quality": "clear",
             "fields": {"name": "A B", "annual_income": 1, "valid_until": "2027-06-01"}}
        d.update(kw)
        return d

    def codes(self, d):
        return {f["code"]: f["severity"] for f in docaudit.check_document(d, self.T)}

    def test_expired_certificate_blocks(self):
        d = self.doc(); d["fields"]["valid_until"] = "2026-11-19"
        self.assertEqual(self.codes(d)["EXPIRED"], "blocking")

    def test_expiry_day_itself_is_still_valid(self):
        d = self.doc(); d["fields"]["valid_until"] = "2026-11-20"
        self.assertNotIn("EXPIRED", self.codes(d))

    def test_expiring_within_30_days_warns(self):
        d = self.doc(); d["fields"]["valid_until"] = "2026-12-10"
        self.assertEqual(self.codes(d)["EXPIRING_SOON"], "warning")

    def test_unreadable_date_is_unknown_not_valid(self):
        d = self.doc(); d["fields"]["valid_until"] = "last march"
        self.assertEqual(self.codes(d)["DATE_UNREADABLE"], "unknown")

    def test_missing_required_field_blocks(self):
        d = self.doc(); del d["fields"]["annual_income"]
        self.assertEqual(self.codes(d)["MISSING_FIELD"], "blocking")

    def test_low_confidence_is_unknown(self):
        self.assertEqual(self.codes(self.doc(confidence=0.3))["LOW_CONFIDENCE"], "unknown")

    def test_unreadable_upload_is_unknown_type(self):
        self.assertEqual(self.codes({"id": "x", "doc_type": "unknown", "fields": {}, "confidence": 0.0})["DOC_TYPE_UNKNOWN"], "unknown")

    def test_abbreviated_name_is_a_mismatch_but_honorific_is_not(self):
        a = {"id": "a", "doc_type": "aadhaar", "fields": {"name": "Ramesh Kumar"}}
        for other, expect in (("Ramesh Kr.", True), ("Shri Ramesh Kumar", False), ("ramesh  kumar", False), ("Ramesh Kumar Singh", True)):
            b = {"id": "b", "doc_type": "income_certificate", "fields": {"name": other}}
            got = any(f["code"] == "NAME_MISMATCH" for f in docaudit.cross_check_names([a, b]))
            self.assertEqual(got, expect, other)

    # DEFECT D007 FIXED: sharpness ratio implemented in app/ocr.py
    def test_backend_blur_detector_flags_blurred_synthetic_documents(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        from app import ocr
        for f in sorted((qa_config.DATA / "documents").glob("*_blurry.png"))[:3]:
            self.assertEqual(ocr.image_quality(f.read_bytes()), "blurry", f.name)

    def test_backend_blur_detector_does_not_flag_clear_documents(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        from app import ocr
        for f in sorted((qa_config.DATA / "documents").glob("*_clear.png"))[:3]:
            self.assertEqual(ocr.image_quality(f.read_bytes()), "clear", f.name)

    def test_proposed_sharpness_ratio_separates_the_synthetic_set(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        from evalkit import blur
        for f in (qa_config.DATA / "documents").glob("*.png"):
            img = Image.open(f)
            expect_blurry = f.name.endswith(("_blurry.png", "_lowres.png"))
            self.assertEqual(blur.looks_blurry(img), expect_blurry, f.name)


class DailyQuota(unittest.TestCase):
    def test_quota_exceeded_is_a_clear_429(self):
        try:
            import sqlalchemy  # noqa: F401
        except ImportError:
            self.skipTest("SQLAlchemy not installed (pip install -r the backend's requirements.txt)")
        from app import quota
        from app.db import Base, SessionLocal, engine
        from app.errors import ApiError
        Base.metadata.create_all(engine)
        with SessionLocal() as db:
            limit = get_settings().llm_daily_quota
            quota.consume(db, "u-quota", limit)
            with self.assertRaises(ApiError) as cm:
                quota.consume(db, "u-quota", 1)
            self.assertEqual((cm.exception.status, cm.exception.code), (429, "QUOTA_EXCEEDED"))


if __name__ == "__main__":
    unittest.main()
