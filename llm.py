"""Model access. USE_MOCK_LLM=true replays deterministic synthetic results (clearly labelled mock).
Live: cheapest model first (Flash-Lite), escalate to Flash only on low confidence; retry with backoff;
if everything fails return UNKNOWN (never a guess). Concurrency is bounded and every call is counted."""
import base64
import io
import json
import threading
import time
import wave

from app import embedding, metrics, ocr, rules, telemetry
from app.agents import fixtures
from app.config import get_settings
from app.pii import redact_text

UNKNOWN_DOC = {"doc_type": "unknown", "fields": {}, "field_confidence": {}, "confidence": 0.0, "quality": "unknown",
               "warnings": ["Could not read this document reliably."]}

SCHEMA_HINT = (
    "Return ONLY JSON with keys: doc_type (one of aadhaar, income_certificate, land_record, caste_certificate, "
    "marksheet, ration_card, unknown), fields (name, dob YYYY-MM-DD, id_number, annual_income number, valid_until "
    "YYYY-MM-DD, category, land_holding_hectares number, institution; omit what is absent), field_confidence "
    "(0-1 per field), confidence 0-1, quality (clear|blurry|cropped), warnings (list). Do not guess missing values."
)
RULES_PROMPT = (
    "Extract eligibility rules from this official scheme text. Return ONLY JSON: {name, benefit, state, deadline "
    "(YYYY-MM-DD or null), required_documents (subset of aadhaar, income_certificate, land_record, caste_certificate, "
    "marksheet, ration_card), criteria: [{id, label, field, op, value}]} where field is one of age, annual_income, "
    "category, occupation, state, gender, land_holding_hectares, is_student and op is one of <=, <, >=, >, ==, !=, in. "
    "Use uppercase strings for categories. Include only rules stated in the text."
)


class LLMUnavailable(Exception):
    pass


_sem = None
_sem_lock = threading.Lock()


def _semaphore():
    global _sem
    with _sem_lock:
        if _sem is None:
            _sem = threading.BoundedSemaphore(get_settings().llm_max_concurrent)
        return _sem


def _post(model: str, op: str, body: dict, task: str, retries: int = 3) -> dict:
    """One bounded, counted, retried call to the Gemini REST API."""
    import httpx
    s = get_settings()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{op}"
    for attempt in range(retries):
        try:
            with _semaphore():
                metrics.inc("llm_calls_total", model=model, task=task)
                r = httpx.post(url, json=body, headers={"x-goog-api-key": s.gemini_api_key}, timeout=45)
            if r.status_code in (429, 500, 502, 503, 504):
                raise httpx.HTTPError(f"retryable {r.status_code}")
            r.raise_for_status()
            return r.json()
        except Exception:
            metrics.inc("llm_failures_total", model=model, task=task)
            time.sleep(0.5 * (2 ** attempt))
    raise LLMUnavailable(model)


def _text(resp: dict) -> str:
    return resp["candidates"][0]["content"]["parts"][0]["text"]


def _json(text: str):
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`").removeprefix("json").strip()
    return json.loads(t)


def _gen(model: str, parts: list, task: str, json_mode: bool = False) -> str:
    body = {"contents": [{"parts": parts}]}
    if json_mode:
        body["generationConfig"] = {"responseMimeType": "application/json"}
    return _text(_post(model, "generateContent", body, task))


def _unknown(warning: str) -> dict:
    out = json.loads(json.dumps(UNKNOWN_DOC))
    out["warnings"].append(warning)
    return out


unknown_doc = _unknown


def _valid(out) -> bool:
    return isinstance(out, dict) and isinstance(out.get("fields"), dict) and "doc_type" in out


def _extract_chain(parts: list, task: str) -> dict:
    """Cheapest model first; escalate only on low confidence; UNKNOWN when nothing works."""
    s, best = get_settings(), None
    for model in (s.model_lite, s.model_flash):
        telemetry.emit("model_routing", model=model, task=task, mock=False)
        try:
            out = _json(_gen(model, parts, task, json_mode=True))
        except (LLMUnavailable, ValueError, KeyError, IndexError):
            continue
        if not _valid(out):
            continue
        out["confidence"] = float(out.get("confidence") or 0.0)
        out.setdefault("quality", "unknown")
        out.setdefault("warnings", [])
        out.setdefault("field_confidence", {})
        if best is None or out["confidence"] > best["confidence"]:
            best = out
        if out["confidence"] >= s.escalate_below:
            break
    return best or _unknown("MODEL_UNAVAILABLE")


def extract_document(data: bytes, mime: str, filename: str) -> dict:
    """Vision/OCR extraction from the file itself (used when local OCR is unavailable)."""
    if get_settings().use_mock_llm:
        telemetry.emit("model_routing", model="mock", task="document_audit", mock=True)
        return fixtures.lookup(filename) or dict(UNKNOWN_DOC)
    data, mime = ocr.compress_image(data, mime)
    parts = [{"text": SCHEMA_HINT}, {"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}}]
    return _extract_chain(parts, "document_audit")


def extract_from_text(redacted_text: str, filename: str) -> dict:
    """Extraction from locally OCR'd text. PII was redacted BEFORE this call."""
    if get_settings().use_mock_llm:
        telemetry.emit("model_routing", model="mock", task="document_audit_text", mock=True)
        return fixtures.lookup(filename) or dict(UNKNOWN_DOC)
    return _extract_chain([{"text": SCHEMA_HINT + "\n\nDOCUMENT TEXT:\n" + redacted_text}], "document_audit_text")


def extract_rules(text: str) -> dict:
    """Rule-pack pipeline step 2. Output is only a DRAFT; a human reviewer must approve it."""
    s = get_settings()
    if s.use_mock_llm:
        telemetry.emit("model_routing", model="mock", task="rule_extraction", mock=True)
        return rules.mock_extract(text)
    telemetry.emit("model_routing", model=s.model_flash, task="rule_extraction", mock=False)
    try:
        return _json(_gen(s.model_flash, [{"text": RULES_PROMPT + "\n\nTEXT:\n" + text}], "rule_extraction", True))
    except (LLMUnavailable, ValueError, KeyError, IndexError):
        raise LLMUnavailable("rule_extraction")


def explain(scheme_name: str, met: int, unknown: int, not_met: int, language: str) -> str:
    s = get_settings()
    hi = language.lower().startswith("hi")
    template = (
        f"{scheme_name}: {met} शर्तें पूरी, {unknown} की जानकारी चाहिए। यह केवल प्रारंभिक अनुमान है।" if hi else
        f"{scheme_name}: {met} criteria met, {unknown} need more information. This is a preliminary estimate only."
    )
    if s.use_mock_llm or not s.gemini_api_key:
        telemetry.emit("model_routing", model="mock" if s.use_mock_llm else "template", task="explain_scheme", mock=s.use_mock_llm)
        return template
    prompt = redact_text(
        f"Explain in simple {language}, in two sentences, why '{scheme_name}' may fit a citizen: {met} criteria met, "
        f"{unknown} unknown, {not_met} not met. Say it is a preliminary estimate. Do not promise approval.")[0]
    telemetry.emit("model_routing", model=s.model_lite, task="explain_scheme", mock=False)
    try:
        return _gen(s.model_lite, [{"text": prompt}], "explain_scheme")
    except LLMUnavailable:
        return template


def translate(text: str, language: str) -> str:
    s = get_settings()
    if s.use_mock_llm or not s.gemini_api_key:
        return text
    telemetry.emit("model_routing", model=s.model_lite, task="translate", mock=False)
    try:
        return _gen(s.model_lite, [{"text": redact_text(f"Translate to {language}. Return only the translation:\n{text}")[0]}], "translate")
    except LLMUnavailable:
        return text


def embed(text: str) -> list:
    """Embedding for the RAG store. Raises LLMUnavailable so callers can fall back to keyword search."""
    s = get_settings()
    if s.use_mock_llm or not s.gemini_api_key:
        return embedding.hashed_embedding(text, s.embed_dim)
    body = {"content": {"parts": [{"text": text}]}, "outputDimensionality": s.embed_dim}
    try:
        return _post(s.model_embed, "embedContent", body, "embed")["embedding"]["values"]
    except (KeyError, LLMUnavailable):
        raise LLMUnavailable("embed")


def transcribe(audio: bytes, mime: str, language: str) -> str:
    """Speech-to-text with the Flash-Lite tier."""
    s = get_settings()
    if s.use_mock_llm:
        telemetry.emit("model_routing", model="mock", task="transcribe", mock=True)
        return "[mock transcript]"
    telemetry.emit("model_routing", model=s.model_lite, task="transcribe", mock=False)
    parts = [{"text": f"Transcribe this speech exactly in its spoken language ({language}). Return only the transcript."},
             {"inline_data": {"mime_type": mime, "data": base64.b64encode(audio).decode()}}]
    return _gen(s.model_lite, parts, "transcribe").strip()


def _wav(pcm: bytes, rate: int = 24000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


def speak(text: str, language: str) -> bytes:
    """Text-to-speech (read-aloud). Returns WAV bytes."""
    s = get_settings()
    if s.use_mock_llm:
        telemetry.emit("model_routing", model="mock", task="tts", mock=True)
        return _wav(b"\x00\x00" * 12000)
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}}}
    telemetry.emit("model_routing", model=s.model_tts, task="tts", mock=False)
    resp = _post(s.model_tts, "generateContent", body, "tts")
    return _wav(base64.b64decode(resp["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]))
