from datetime import date

from sqlalchemy.orm import Session

from app import metrics
from app.config import get_settings
from app.errors import ApiError
from app.models import UsageCounter


def consume(db: Session, user_id: str, n: int = 1) -> None:
    """Per-user daily quota for live model calls. Mock mode is free."""
    s = get_settings()
    if s.use_mock_llm:
        return
    day = date.today().isoformat()
    row = db.get(UsageCounter, (user_id, day))
    if row is None:
        row = UsageCounter(user_id=user_id, day=day, calls=0)
        db.add(row)
    if row.calls + n > s.llm_daily_quota:
        metrics.inc("quota_rejections_total")
        raise ApiError(429, "QUOTA_EXCEEDED", "Daily limit for AI checks reached. Please try again tomorrow.")
    row.calls += n
    db.flush()
