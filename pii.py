"""PII detection/redaction. Run before any text goes to a model or a log (pure module)."""
import re
from typing import Any, Tuple

_PATTERNS = [
    ("AADHAAR", re.compile(r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")),
    ("PAN", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")),
    ("PHONE", re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)")),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
]


def redact_text(text: str) -> Tuple[str, dict]:
    counts: dict = {}
    for label, rx in _PATTERNS:
        text, n = rx.subn(f"[{label}_REDACTED]", text)
        if n:
            counts[label] = n
    return text, counts


def redact_obj(obj: Any) -> Any:
    """Recursively redact every string inside dicts/lists."""
    if isinstance(obj, str):
        return redact_text(obj)[0]
    if isinstance(obj, dict):
        return {k: redact_obj(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [redact_obj(v) for v in obj]
    return obj
