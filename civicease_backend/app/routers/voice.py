"""Voice in/out: speech-to-text (Flash-Lite) and text-to-speech (read-aloud). Typing always remains available (text mode)."""
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import llm, quota
from app.deps import current_user, get_db, rate_limit
from app.errors import ApiError, ok
from app.models import User
from app.schemas import SpeakIn

router = APIRouter(prefix="/voice", dependencies=[Depends(rate_limit)], tags=["voice"])
MAX_AUDIO = 2 * 1024 * 1024


@router.post("/transcribe")
def transcribe(audio: UploadFile = File(...), language: str = Form("en"), user: User = Depends(current_user),
               db: Session = Depends(get_db)):
    if not (audio.content_type or "").startswith("audio/"):
        raise ApiError(415, "UNSUPPORTED_TYPE", "Send an audio file.")
    data = audio.file.read(MAX_AUDIO + 1)
    if len(data) > MAX_AUDIO:
        raise ApiError(413, "TOO_LARGE", "Audio must be under 2 MB.")
    quota.consume(db, user.id)
    try:
        text = llm.transcribe(data, audio.content_type, language[:10])
    except llm.LLMUnavailable:
        raise ApiError(502, "VOICE_UNAVAILABLE", "Voice is unavailable right now. Please type your message.")
    db.commit()
    return ok({"text": text, "language": language[:10]})  # transcript is returned, never logged


@router.post("/speak")
def speak(body: SpeakIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    quota.consume(db, user.id)
    try:
        audio = llm.speak(body.text, body.language)
    except (llm.LLMUnavailable, KeyError):
        raise ApiError(502, "VOICE_UNAVAILABLE", "Read-aloud is unavailable right now.")
    db.commit()
    return Response(audio, media_type="audio/wav", headers={"Cache-Control": "no-store"})
