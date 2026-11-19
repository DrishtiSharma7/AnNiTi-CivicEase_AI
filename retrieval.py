"""RAG store over scheme rules: embeddings (Gemini, or hashed offline), pgvector when available, else Python cosine.
Similarity finds candidate schemes; it is never presented as proof of eligibility."""
import re

from sqlalchemy import select, text

from app import embedding, llm
from app.config import get_settings
from app.models import Scheme


def scheme_text(s: Scheme) -> str:
    return f"{s.name}. {s.benefit}. {s.pack}. " + " ".join(c["label"] for c in (s.criteria or []))


def _pg(db) -> bool:
    return get_settings().use_pgvector and db.get_bind().dialect.name == "postgresql"


def ensure_pgvector(db) -> None:  # pragma: no cover - needs Postgres + pgvector
    if _pg(db):
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.execute(text(f"ALTER TABLE schemes ADD COLUMN IF NOT EXISTS embedding_vec vector({get_settings().embed_dim})"))
        db.commit()


def index_scheme(db, s: Scheme) -> None:
    try:
        s.embedding = llm.embed(scheme_text(s))
    except llm.LLMUnavailable:
        s.embedding = None
    if s.embedding and _pg(db):  # pragma: no cover
        db.execute(text("UPDATE schemes SET embedding_vec = CAST(:v AS vector) WHERE id = :id"),
                   {"v": "[" + ",".join(str(x) for x in s.embedding) + "]", "id": s.id})


def _keyword(db, query: str, k: int) -> list:
    toks = set(re.findall(r"\w+", query.lower()))
    scored = []
    for s in db.execute(select(Scheme)).scalars():
        hay = set(re.findall(r"\w+", scheme_text(s).lower()))
        scored.append((len(toks & hay) / (len(toks) or 1), s))
    return [(s, sc) for sc, s in sorted(scored, key=lambda x: -x[0])[:k] if sc > 0]


def search(db, query: str, k: int = 5) -> list:
    """Returns [(Scheme, score)] best first."""
    try:
        q = llm.embed(query)
    except llm.LLMUnavailable:
        return _keyword(db, query, k)
    if _pg(db):  # pragma: no cover
        vec = "[" + ",".join(str(x) for x in q) + "]"
        rows = db.execute(text("SELECT id, 1 - (embedding_vec <=> CAST(:v AS vector)) AS score FROM schemes "
                               "WHERE embedding_vec IS NOT NULL ORDER BY embedding_vec <=> CAST(:v AS vector) LIMIT :k"),
                          {"v": vec, "k": k}).all()
        return [(db.get(Scheme, r.id), float(r.score)) for r in rows]
    out = [(s, embedding.cosine(q, s.embedding)) for s in db.execute(select(Scheme)).scalars()
           if s.embedding and len(s.embedding) == len(q)]
    out = [(s, sc) for s, sc in sorted(out, key=lambda x: -x[1])[:k] if sc > 0]
    return out or _keyword(db, query, k)
