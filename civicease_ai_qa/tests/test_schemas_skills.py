"""Pins the response shapes the UI and agents rely on, and checks the skills have the required structure."""
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import qa_config as qc  # noqa: E402
from schemas import validate as sv  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class Schemas(unittest.TestCase):
    def test_backend_outputs_match_the_schemas(self):
        from app import docaudit, eligibility, llm
        from app.agents import fixtures
        from app.seed import SCHEMES
        self.assertEqual(sv.validate(llm.UNKNOWN_DOC, "doc_extraction"), [])
        for name in ("ramesh_aadhaar", "ramesh_income", "sunita_aadhaar", "sunita_income"):
            self.assertEqual(sv.validate(fixtures.lookup(name + ".pdf"), "doc_extraction"), [], name)
        for s in SCHEMES:
            self.assertEqual(sv.validate(eligibility.evaluate(s["criteria"], {"age": 61}), "eligibility"), [], s["id"])
        rep = docaudit.build_readiness(["aadhaar", "income_certificate"], [], {}, date(2026, 11, 20))
        self.assertEqual(sv.validate(rep, "readiness"), [])

    def test_validator_catches_real_problems(self):
        bad = {"doc_type": "passport", "fields": {"name": 5, "secret": "x"}, "confidence": 1.5, "quality": "ok"}
        errs = sv.validate(bad, "doc_extraction")
        for needle in ("not in", "expected ['string']", "unexpected field 'secret'", "> maximum"):
            self.assertTrue(any(needle in e for e in errs), (needle, errs))
        self.assertTrue(sv.validate({"overall": "likely_met", "criteria": [], "preliminary_estimate": False}, "eligibility"))


class Skills(unittest.TestCase):
    def test_toolkit_skills_have_required_sections(self):
        r = subprocess.run([sys.executable, str(ROOT / "skills" / "lint_skills.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_prompt_registry_matches_backend(self):
        r = subprocess.run([sys.executable, str(ROOT / "prompts" / "registry.py"), "check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
