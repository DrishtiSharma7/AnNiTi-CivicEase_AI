"""'Judge Mode' event buffer: model routing, skill loading, PII masking, human gates.
Never put raw personal data in an event."""
import time
from collections import deque

_BUFFER: deque = deque(maxlen=300)


def emit(event: str, /, **data) -> None:
    _BUFFER.append({"t": round(time.time(), 3), "kind": event, **data})


def snapshot(limit: int = 100) -> list:
    return list(_BUFFER)[-limit:]


def clear() -> None:
    _BUFFER.clear()
