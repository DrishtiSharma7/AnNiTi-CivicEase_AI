from datetime import date, timedelta

from sqlalchemy import select

from app.docaudit import EXPIRY_WARN_DAYS, parse_date
from app.models import Application, Document, Scheme


def run(db, user_id: str) -> dict:
    today, reminders = date.today(), []
    for doc in db.execute(select(Document).where(Document.user_id == user_id)).scalars():
        vu = parse_date((doc.extracted or {}).get("valid_until"))
        if vu and vu <= today + timedelta(days=EXPIRY_WARN_DAYS):
            reminders.append({"type": "document_expiry", "document_id": doc.id, "doc_type": doc.doc_type,
                              "date": vu.isoformat(), "expired": vu < today})
    for app in db.execute(select(Application).where(Application.user_id == user_id)).scalars():
        sch = db.get(Scheme, app.scheme_id)
        d = parse_date(sch.deadline) if sch else None
        if d and app.status != "submitted":
            reminders.append({"type": "scheme_deadline", "application_id": app.id, "scheme": sch.name, "date": d.isoformat()})
    reminders.sort(key=lambda r: r["date"])
    return {"reminders": reminders, "next_deadline": next((r for r in reminders if r["type"] == "scheme_deadline"), None)}
