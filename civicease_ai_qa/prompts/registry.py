"""Prompt records for Google AI Studio experiments and the production prompts. One row per prompt VERSION and per
test run, so improvements can be measured. Commands:
  python prompts/registry.py check                 # prompt files vs registry vs backend constants (drift = failure)
  python prompts/registry.py new <prompt_id> <version> "<what changed>"   # register a new prompt version (after editing the file)
  python prompts/registry.py log <prompt_id> <version> <model> <test_category> <accuracy> "<observed errors>"   # one AI Studio test run"""
import csv
import hashlib
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import qa_config  # noqa: E402,F401

REG = ROOT / "prompts" / "registry.csv"
COLS = ["kind", "prompt_id", "version", "sha256", "date", "model", "test_category", "accuracy", "observed_errors", "notes"]
FILES = {"document_extraction": ("document_extraction_v{}.txt", "SCHEMA_HINT"), "rule_extraction": ("rule_extraction_v{}.txt", "RULES_PROMPT")}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").strip().encode()).hexdigest()[:16]


def rows():
    return list(csv.DictReader(open(REG, encoding="utf-8"))) if REG.exists() else []


def append(row: dict):
    new = not REG.exists()
    with open(REG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerow({c: row.get(c, "") for c in COLS})


def latest(prompt_id: str):
    v = [r for r in rows() if r["kind"] == "version" and r["prompt_id"] == prompt_id]
    return max(v, key=lambda r: int(r["version"])) if v else None


def check() -> int:
    from app import llm
    bad = 0
    for pid, (pattern, const) in FILES.items():
        lat = latest(pid)
        if not lat:
            print(f"FAIL {pid}: not registered"); bad += 1; continue
        path = ROOT / "prompts" / pattern.format(lat["version"])
        if sha(path) != lat["sha256"]:
            print(f"FAIL {pid}: file changed without a new registry version (register it with 'new')"); bad += 1
        if getattr(llm, const).strip() != path.read_text(encoding="utf-8").strip():
            print(f"FAIL {pid}: backend {const} differs from {path.name}. Update one, bump the version, re-run regression"); bad += 1
        else:
            print(f"ok   {pid} v{lat['version']} matches the backend")
    return 1 if bad else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        sys.exit(check())
    if cmd == "new":
        pid, ver, note = sys.argv[2], sys.argv[3], sys.argv[4]
        path = ROOT / "prompts" / FILES[pid][0].format(ver)
        append({"kind": "version", "prompt_id": pid, "version": ver, "sha256": sha(path), "date": date.today().isoformat(), "notes": note})
    elif cmd == "log":
        _, _, pid, ver, model, cat, acc, err = sys.argv
        append({"kind": "run", "prompt_id": pid, "version": ver, "date": date.today().isoformat(), "model": model, "test_category": cat,
                "accuracy": acc, "observed_errors": err})
    print("registry updated")
