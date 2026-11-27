"""Pluggable 'extractors': anything that turns one labelled document into the backend's extraction dict
{doc_type, fields, field_confidence, confidence, quality, warnings}.
  oracle   returns the ground truth (checks the harness itself: must score 100%)
  noisy    ground truth with controlled errors (checks the harness CATCHES errors)
  backend  the real backend llm layer (mock mode = fixtures only; live mode = Gemini, uses free-tier quota)
  file     predictions you produced elsewhere, e.g. pasted from Google AI Studio runs (JSON lines)"""
import hashlib
import json
import random
import time
from pathlib import Path

import qa_config  # noqa: F401  (puts the backend on sys.path)

PAD = "9999 0000 "  # the label keeps only the last 4 digits; the extraction dict uses a dummy full number


def truth(row) -> dict:
    fields = {}
    for k in ("name", "dob", "valid_until", "institution"):
        if str(row.get(k, "")) not in ("", "nan"):
            fields[k] = str(row[k])
    if str(row.get("annual_income", "")) not in ("", "nan"):
        fields["annual_income"] = int(float(row["annual_income"]))
    if str(row.get("id_last4", "")) not in ("", "nan"):
        fields["id_number"] = PAD + str(row["id_last4"]).zfill(4)
    return {"doc_type": row["doc_type"], "fields": fields, "field_confidence": {k: 0.99 for k in fields},
            "confidence": 0.99, "quality": row["quality"], "warnings": []}


def oracle(row, data):
    return truth(row)


def make_noisy(seed: int = 1, error_rate: float = 0.25):
    rng = random.Random(seed)

    def noisy(row, data):
        t = truth(row)
        f = t["fields"]
        for k in list(f):
            r = rng.random()
            if r < error_rate * 0.5:      # wrong value, still confident (the dangerous kind)
                v = f[k]
                f[k] = (v + 1) if isinstance(v, int) else (v[:-1] + ("0" if v[-1] != "0" else "1"))
            elif r < error_rate * 0.8:    # field not read
                f.pop(k)
                t["field_confidence"].pop(k, None)
        if rng.random() < error_rate and "dob" not in f and row["doc_type"] == "aadhaar":
            f["dob"] = "1990-01-01"       # hallucinated value for a field the document does not have
            t["field_confidence"]["dob"] = 0.97
        t["confidence"] = 0.95            # overconfident on purpose
        return t
    return noisy


def backend(row, data):
    from app import llm
    return llm.extract_document(data, "image/png", Path(row["file"]).name)


def from_file(path):
    preds = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            preds[d["doc_id"]] = d.get("extraction", d)

    def reader(row, data):
        if row["doc_id"] not in preds:
            raise KeyError(f"no prediction for {row['doc_id']}")
        return preds[row["doc_id"]]
    return reader


def fingerprint() -> str:
    """Identifies prompt + model ids + mode, so cached live predictions are reused only when they are still valid."""
    from app import llm
    from app.config import get_settings
    s = get_settings()
    blob = json.dumps([llm.SCHEMA_HINT, s.model_flash, s.model_lite, s.use_mock_llm, s.escalate_below])
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


class Cache:
    """Predictions on disk so re-running a report does not spend free-tier quota again."""
    def __init__(self, path: Path, fp: str):
        self.path, self.fp, self.data = path, fp, {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                d = json.loads(line)
                if d["fp"] == fp:
                    self.data[d["key"]] = d["extraction"]

    def get(self, key):
        return self.data.get(key)

    def put(self, key, extraction):
        self.data[key] = extraction
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"fp": self.fp, "key": key, "extraction": extraction}) + "\n")


def run_all(labels, root: Path, extractor, cache: Cache = None, sleep: float = 0.0, limit: int = 0) -> dict:
    preds, calls = {}, 0
    for _, row in labels.iterrows():
        if limit and calls >= limit:
            break
        data = (root / row["file"]).read_bytes()
        key = f"{row['doc_id']}:{hashlib.sha256(data).hexdigest()[:12]}"
        ext = cache.get(key) if cache else None
        if ext is None:
            ext = extractor(row, data)
            calls += 1
            if cache:
                cache.put(key, ext)
            if sleep:
                time.sleep(sleep)  # stay under free-tier requests-per-minute limits
        preds[row["doc_id"]] = ext
    return preds


def get(name: str, seed: int = 1, error_rate: float = 0.25, path: str = ""):
    if name == "oracle":
        return oracle
    if name == "noisy":
        return make_noisy(seed, error_rate)
    if name == "backend":
        return backend
    if name == "file":
        return from_file(path)
    raise SystemExit(f"unknown extractor {name}")
