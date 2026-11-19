"""Agent Skills loader. Procedures live in app/skills/<name>/SKILL.md and load on demand."""
from pathlib import Path

from app import telemetry

SKILLS_DIR = Path(__file__).parent / "skills"


def load_skill(name: str) -> str:
    path = SKILLS_DIR / name / "SKILL.md"
    if not path.is_file() or SKILLS_DIR.resolve() not in path.resolve().parents:
        raise FileNotFoundError(f"skill not found: {name}")
    telemetry.emit("skill_loaded", skill=name, file=f"{name}/SKILL.md")
    return path.read_text(encoding="utf-8")
