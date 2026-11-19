"""Minimal Prometheus-style metrics: errors, latency and model usage (cost proxy). Per-process; scrape each instance."""
import threading
from collections import defaultdict

_lock = threading.Lock()
_counters = defaultdict(float)


def inc(name: str, value: float = 1.0, **labels) -> None:
    key = (name, tuple(sorted(labels.items())))
    with _lock:
        _counters[key] += value


def render() -> str:
    lines = []
    with _lock:
        for (name, labels), v in sorted(_counters.items()):
            lab = ",".join(f'{k}="{val}"' for k, val in labels)
            lines.append(f"{name}{{{lab}}} {v}" if lab else f"{name} {v}")
    return "\n".join(lines) + "\n"
