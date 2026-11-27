"""Checks every SKILL.md has the structure Nisha's role requires: front matter (name matches folder, description) and the
sections Required inputs, Validation steps, Output schema, Edge cases, When the result must be UNKNOWN.
  python skills/lint_skills.py            # lints this toolkit's skills and the backend's skills"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import qa_config as qc  # noqa: E402

REQUIRED = ["Required inputs", "Validation steps", "Output schema", "Edge cases", "When the result must be UNKNOWN"]


def lint(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    errs = []
    m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", text)
    if not m:
        return ["missing front matter with name and description"]
    if m.group(1).strip() != path.parent.name:
        errs.append(f"name '{m.group(1)}' does not match folder '{path.parent.name}'")
    if len(m.group(2).strip()) < 30:
        errs.append("description too short to tell the orchestrator when to load it")
    errs += [f"missing section '## {s}'" for s in REQUIRED if f"## {s}" not in text]
    return errs


def main() -> int:
    bad = 0
    for base, strict in ((ROOT / "skills", True), (qc.BACKEND / "app" / "skills", False)):
        for p in sorted(base.rglob("SKILL.md")):
            errs = lint(p)
            tag = "ok  " if not errs else ("FAIL" if strict else "note")
            print(f"{tag} {p.parent.name}/SKILL.md ({'toolkit' if strict else 'backend'})" + ("" if not errs else ": " + "; ".join(errs)))
            bad += bool(errs) and strict
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
