"""Central settings. Secrets come from the environment, never from source control."""
import base64
import hashlib
import os
from dataclasses import dataclass
from functools import lru_cache

_DEV_SECRET = "dev-only-change-me"


def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def _list(name: str, default: str) -> tuple:
    return tuple(x.strip().lower() if name.endswith("EMAILS") else x.strip()
                 for x in os.getenv(name, default).split(",") if x.strip())


@dataclass(frozen=True)
class Settings:
    env: str
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int
    pepper: str
    master_key: bytes
    kms_mode: str
    gcp_kms_key: str
    storage_backend: str
    storage_dir: str
    gcs_bucket: str
    max_upload_bytes: int
    rate_limit_per_minute: int
    auth_rate_limit_per_minute: int
    redis_url: str
    doc_retention_days: int
    use_mock_llm: bool
    gemini_api_key: str
    model_flash: str
    model_lite: str
    model_embed: str
    model_tts: str
    embed_dim: int
    llm_daily_quota: int
    llm_max_concurrent: int
    escalate_below: float
    local_ocr: bool
    require_local_redaction: bool
    use_pgvector: bool
    allowed_portal_domains: tuple
    portal_base_url: str
    use_playwright: bool
    worker_url: str
    worker_secret: str
    judge_mode: bool
    metrics_token: str
    force_https: bool
    cors_origins: tuple
    reviewer_emails: tuple
    allow_self_approve: bool
    official_suffixes: tuple
    signed_url_ttl: int = 300
    approval_ttl: int = 600


@lru_cache
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "dev")
    prod = env == "production"
    jwt_secret = os.getenv("JWT_SECRET", _DEV_SECRET)
    pepper = os.getenv("PEPPER", _DEV_SECRET)
    mk = os.getenv("MASTER_KEY_B64", "")
    kms_mode = os.getenv("KMS_MODE", "local")
    master_key = base64.b64decode(mk) if mk else hashlib.sha256(b"dev-master-key").digest()
    if prod and (_DEV_SECRET in (jwt_secret, pepper) or (kms_mode == "local" and not mk)):
        raise RuntimeError("Set JWT_SECRET, PEPPER and MASTER_KEY_B64 (or KMS_MODE=gcp) in production.")
    if len(master_key) != 32:
        raise RuntimeError("MASTER_KEY_B64 must decode to exactly 32 bytes.")
    return Settings(
        env=env,
        database_url=os.getenv("DATABASE_URL", "sqlite:///./civicease.db"),
        jwt_secret=jwt_secret,
        jwt_expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "60")),
        pepper=pepper,
        master_key=master_key,
        kms_mode=kms_mode,
        gcp_kms_key=os.getenv("GCP_KMS_KEY", ""),
        storage_backend=os.getenv("STORAGE_BACKEND", "local"),
        storage_dir=os.getenv("STORAGE_DIR", "./storage"),
        gcs_bucket=os.getenv("GCS_BUCKET", ""),
        max_upload_bytes=int(float(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        auth_rate_limit_per_minute=int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "10")),
        redis_url=os.getenv("REDIS_URL", ""),
        doc_retention_days=int(os.getenv("DOC_RETENTION_DAYS", "30")),
        use_mock_llm=_bool("USE_MOCK_LLM", "true"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        model_flash=os.getenv("MODEL_FLASH", "gemini-2.5-flash"),
        model_lite=os.getenv("MODEL_LITE", "gemini-2.5-flash-lite"),
        model_embed=os.getenv("MODEL_EMBED", "gemini-embedding-001"),
        model_tts=os.getenv("MODEL_TTS", "gemini-2.5-flash-preview-tts"),
        embed_dim=int(os.getenv("EMBED_DIM", "256")),
        llm_daily_quota=int(os.getenv("LLM_DAILY_QUOTA_PER_USER", "30")),
        llm_max_concurrent=int(os.getenv("LLM_MAX_CONCURRENT", "4")),
        escalate_below=float(os.getenv("ESCALATE_BELOW_CONFIDENCE", "0.75")),
        local_ocr=_bool("LOCAL_OCR", "false"),
        require_local_redaction=_bool("REQUIRE_LOCAL_REDACTION", "false"),
        use_pgvector=_bool("USE_PGVECTOR", "false"),
        allowed_portal_domains=_list("ALLOWED_PORTAL_DOMAINS", "localhost,127.0.0.1"),
        portal_base_url=os.getenv("PORTAL_BASE_URL", ""),
        use_playwright=_bool("USE_PLAYWRIGHT", "false"),
        worker_url=os.getenv("WORKER_URL", ""),
        worker_secret=os.getenv("WORKER_SHARED_SECRET", _DEV_SECRET),
        judge_mode=_bool("JUDGE_MODE", "true"),
        metrics_token=os.getenv("METRICS_TOKEN", ""),
        force_https=_bool("FORCE_HTTPS", "true" if prod else "false"),
        cors_origins=_list("CORS_ORIGINS", "http://localhost:3000"),
        reviewer_emails=_list("REVIEWER_EMAILS", ""),
        allow_self_approve=_bool("ALLOW_SELF_APPROVE", "false" if prod else "true"),
        official_suffixes=_list("OFFICIAL_DOMAIN_SUFFIXES", ""),
    )
