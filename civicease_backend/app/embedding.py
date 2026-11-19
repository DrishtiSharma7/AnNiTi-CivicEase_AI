"""Deterministic hashed bag-of-words embeddings (mock/offline mode) and cosine similarity (pure)."""
import hashlib
import math
import re


def hashed_embedding(text: str, dim: int = 256) -> list:
    vec = [0.0] * dim
    for tok in re.findall(r"\w+", text.lower()):
        h = hashlib.sha256(tok.encode()).digest()
        idx = int.from_bytes(h[:4], "big") % dim
        vec[idx] += 1.0 if h[4] % 2 == 0 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list, b: list) -> float:
    return sum(x * y for x, y in zip(a, b))
