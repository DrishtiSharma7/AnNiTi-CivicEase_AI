"""Conversational profile intake (pure). A few simple questions, each with a 'why am I asked this?' text.
Answers are parsed deterministically; anything unclear is asked again, never guessed."""
import re
from typing import Optional

DEVANAGARI = str.maketrans("०१२३४५६७८९", "0123456789")
YES = {"yes", "y", "haan", "han", "ha", "हाँ", "हां", "हा", "जी", "true"}
NO = {"no", "n", "nahi", "nahin", "नहीं", "नही", "false"}
SKIP = {"skip", "pass", "छोड़ें", "छोड़", "पता नहीं"}
SYNONYMS = {
    "FARMER": ["farmer", "kisan", "किसान", "खेती"], "STUDENT": ["student", "छात्र", "छात्रा", "विद्यार्थी"],
    "DAILY_WAGE": ["daily wage", "labour", "labor", "मजदूर", "दिहाड़ी"], "SELF_EMPLOYED": ["self employed", "self-employed", "business", "दुकान", "व्यापार"],
    "SALARIED": ["salaried", "job", "नौकरी"], "HOMEMAKER": ["homemaker", "housewife", "गृहिणी"],
    "UNEMPLOYED": ["unemployed", "बेरोजगार"], "OTHER": ["other", "अन्य"],
    "FEMALE": ["female", "woman", "महिला", "स्त्री"], "MALE": ["male", "man", "पुरुष"],
    "GENERAL": ["general", "सामान्य"], "OBC": ["obc"], "SC": ["sc"], "ST": ["st"], "EWS": ["ews"],
}

QUESTIONS = [
    {"field": "age", "type": "int", "min": 0, "max": 120,
     "q": {"en": "How old are you?", "hi": "आपकी उम्र कितनी है?"},
     "why": {"en": "Many schemes, such as pensions and scholarships, have age limits.", "hi": "पेंशन और छात्रवृत्ति जैसी कई योजनाओं में उम्र की सीमा होती है।"}},
    {"field": "occupation", "type": "choice", "choices": ["FARMER", "STUDENT", "DAILY_WAGE", "SELF_EMPLOYED", "SALARIED", "HOMEMAKER", "UNEMPLOYED", "OTHER"],
     "q": {"en": "What best describes your work?", "hi": "आप क्या काम करते हैं?"},
     "why": {"en": "Some schemes are only for farmers, students or workers.", "hi": "कुछ योजनाएँ केवल किसानों, छात्रों या श्रमिकों के लिए हैं।"}},
    {"field": "annual_income", "type": "int", "min": 0, "max": 10**9,
     "q": {"en": "What is your family's total income in a year (in rupees)?", "hi": "आपके परिवार की सालाना आमदनी कितनी है (रुपये में)?"},
     "why": {"en": "Many schemes have an income limit.", "hi": "कई योजनाओं में आय की सीमा होती है।"}},
    {"field": "category", "type": "choice", "choices": ["GENERAL", "OBC", "SC", "ST", "EWS"],
     "q": {"en": "Which category do you belong to?", "hi": "आप किस श्रेणी से हैं?"},
     "why": {"en": "Some benefits are reserved for specific categories.", "hi": "कुछ लाभ विशेष श्रेणियों के लिए आरक्षित हैं।"}},
    {"field": "state", "type": "text", "max_len": 40,
     "q": {"en": "Which state do you live in?", "hi": "आप किस राज्य में रहते हैं?"},
     "why": {"en": "Many schemes are run by state governments.", "hi": "कई योजनाएँ राज्य सरकारें चलाती हैं।"}},
    {"field": "gender", "type": "choice", "choices": ["FEMALE", "MALE", "OTHER"], "optional": True,
     "q": {"en": "What is your gender? (optional)", "hi": "आपका लिंग क्या है? (वैकल्पिक)"},
     "why": {"en": "A few schemes are only for women.", "hi": "कुछ योजनाएँ केवल महिलाओं के लिए हैं।"}},
    {"field": "land_holding_hectares", "type": "float", "min": 0, "max": 10000, "only_if": ("occupation", "FARMER"),
     "q": {"en": "How much farmland do you own, in hectares?", "hi": "आपके पास कितने हेक्टेयर खेत है?"},
     "why": {"en": "Farmer schemes depend on land ownership.", "hi": "किसान योजनाएँ ज़मीन के स्वामित्व पर निर्भर करती हैं।"}},
]
_BY_FIELD = {q["field"]: q for q in QUESTIONS}


def parse_number(text: str) -> float:
    t = text.translate(DEVANAGARI).lower().replace(",", "").replace("₹", "").replace("rs.", "").replace("rs", "")
    m = re.search(r"(\d+(?:\.\d+)?)", t)
    if not m:
        raise ValueError("no number found")
    n = float(m.group(1))
    if re.search(r"lakh|lac|लाख", t):
        n *= 100000
    elif re.search(r"\bk\b|thousand|हज़ार|हजार", t):
        n *= 1000
    return n


def _choice(q: dict, text: str) -> str:
    t = text.strip().lower()
    for c in q["choices"]:
        if t == c.lower().replace("_", " ") or t == c.lower():
            return c
    for c in q["choices"]:
        if any(re.search(rf"(?<!\w){re.escape(w)}(?!\w)", t) for w in SYNONYMS.get(c, [])):
            return c
    raise ValueError("choice not understood")


def parse_answer(field: str, text: str):
    q = _BY_FIELD[field]
    if q["type"] in ("int", "float"):
        n = parse_number(text)
        if not (q["min"] <= n <= q["max"]):
            raise ValueError("out of range")
        return int(round(n)) if q["type"] == "int" else n
    if q["type"] == "choice":
        return _choice(q, text)
    v = re.sub(r"\s+", " ", text.strip())[: q["max_len"]]
    if len(v) < 2:
        raise ValueError("too short")
    return v.upper()


def is_skip(text: str) -> bool:
    return text.strip().lower() in SKIP


def _applicable(q: dict, data: dict) -> bool:
    cond = q.get("only_if")
    return not cond or data.get(cond[0]) == cond[1]


def next_question(data: dict, language: str = "en") -> Optional[dict]:
    lang = "hi" if language.lower().startswith("hi") else "en"
    skipped = set(data.get("_skipped", []))
    for q in QUESTIONS:
        if q["field"] in data or q["field"] in skipped or not _applicable(q, data):
            continue
        return {"field": q["field"], "question": q["q"][lang], "why": q["why"][lang], "language": lang,
                "type": q["type"], "quick_replies": q.get("choices", []), "optional": bool(q.get("optional"))}
    return None


def apply_answer(data: dict, field: str, text: str) -> dict:
    """Returns a new profile dict. Raises ValueError (re-ask) or KeyError (unknown field)."""
    new = dict(data)
    if field not in _BY_FIELD:
        raise KeyError(field)
    if is_skip(text):
        new["_skipped"] = sorted(set(new.get("_skipped", [])) | {field})
        return new
    new[field] = parse_answer(field, text)
    if field == "occupation":
        new["is_student"] = new[field] == "STUDENT"
    return new
