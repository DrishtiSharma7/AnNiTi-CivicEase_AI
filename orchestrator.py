"""ADK-style orchestrator: routes a citizen request to a specialist agent via typed task objects.
The Google ADK runtime can replace route()/handle() later; the task/result contracts stay the same."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app import profile_parse, telemetry, trust
from app.agents import discovery, notification
from app.config import get_settings


class AgentName(str, Enum):
    profile = "profile"
    discovery = "discovery"
    eligibility = "eligibility"
    doc_auditor = "doc_auditor"
    app_prep = "app_prep"
    browser_action = "browser_action"
    notification = "notification"


class AgentTask(BaseModel):
    agent: AgentName
    user_id: str
    language: str = "en"
    payload: dict = {}


class AgentResult(BaseModel):
    agent: AgentName
    status: str                       # ok | needs_consent | needs_info | handoff
    language: str = "en"              # language tag shown on the chat bubble
    data: dict = {}
    human_gate: Optional[int] = None  # 1..5 when a human decision is required next


_KEYWORDS = [
    (AgentName.doc_auditor, ("document", "upload", "certificate", "aadhaar", "photo", "दस्तावेज")),
    (AgentName.app_prep, ("apply", "application", "form", "fill", "आवेदन")),
    (AgentName.notification, ("status", "deadline", "remind", "track", "स्थिति")),
    (AgentName.eligibility, ("eligible", "qualify", "can i get", "पात्र")),
]
_MSG = {
    "consent": {"en": "I need your permission to use a few profile details before matching schemes.",
                "hi": "योजनाएँ खोजने से पहले मुझे आपकी कुछ जानकारी इस्तेमाल करने की अनुमति चाहिए।"},
    "upload": {"en": "Upload a photo or PDF of your document. Document-use consent comes first.",
               "hi": "अपने दस्तावेज़ की फोटो या PDF अपलोड करें। पहले दस्तावेज़-उपयोग की अनुमति चाहिए।"},
    "apply": {"en": "Create an application for a scheme, then follow the readiness steps.",
              "hi": "किसी योजना के लिए आवेदन बनाएँ, फिर तैयारी के चरण पूरे करें।"},
}


def route(message: str) -> AgentName:
    m = message.lower()
    for agent, words in _KEYWORDS:
        if any(w in m for w in words):
            return agent
    return AgentName.discovery


def handle(db, user, profile: dict, has_profile_consent: bool, message: str, language: str) -> dict:
    s = get_settings()
    lang = "hi" if language.lower().startswith("hi") else "en"
    agent = route(message)
    telemetry.emit("model_routing", model="mock" if s.use_mock_llm else s.model_lite, task="intent_routing",
                   routed_to=agent.value, mock=s.use_mock_llm)
    task = AgentTask(agent=agent, user_id=user.id, language=language)
    R = lambda **kw: AgentResult(agent=kw.pop("agent", agent), language=lang, **kw)
    if agent in (AgentName.discovery, AgentName.eligibility):
        if not has_profile_consent:
            telemetry.emit("human_gate", gate=1, state="waiting", reason="profile consent")
            res = R(status="needs_consent", human_gate=1, data={"message": _MSG["consent"][lang]})
        else:
            nxt = profile_parse.next_question(profile, language)
            if not profile and nxt:  # nothing known yet: the Profile agent asks the first simple question
                res = R(agent=AgentName.profile, status="needs_info", data={"next_question": nxt})
            else:
                data = trust.guard(discovery.run(db, profile, language), "scheme_match")
                if nxt and "schemes" in data:
                    data["next_question"] = nxt  # keep asking: unknown criteria become known
                res = R(status="ok", data=data)
    elif agent == AgentName.notification:
        res = R(status="ok", data=notification.run(db, user.id))
    elif agent == AgentName.doc_auditor:
        res = R(status="ok", human_gate=2, data={"message": _MSG["upload"][lang], "endpoint": "POST /documents"})
    else:
        res = R(status="ok", data={"message": _MSG["apply"][lang], "endpoint": "POST /applications"})
    return {"task": task.model_dump(mode="json"), "result": res.model_dump(mode="json")}
