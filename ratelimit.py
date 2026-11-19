"""Rate limiting. In-memory sliding window by default; Redis (REDIS_URL) for stateless multi-instance deployments."""
import threading
import time
from collections import defaultdict, deque


class SlidingWindow:
    def __init__(self):
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window: int = 60) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            return True

    def reset(self):
        with self._lock:
            self._hits.clear()


class RedisWindow:  # pragma: no cover - needs a Redis server
    def __init__(self, url: str):
        import redis
        self.r = redis.Redis.from_url(url)

    def allow(self, key: str, limit: int, window: int = 60) -> bool:
        bucket = f"rl:{key}:{int(time.time() // window)}"
        n = self.r.incr(bucket)
        if n == 1:
            self.r.expire(bucket, window + 1)
        return n <= limit

    def reset(self):
        pass


_limiter = None


def get_limiter():
    global _limiter
    if _limiter is None:
        from app.config import get_settings
        url = get_settings().redis_url
        _limiter = RedisWindow(url) if url else SlidingWindow()
    return _limiter
