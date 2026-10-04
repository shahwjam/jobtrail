import math
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException

import config


class SlidingWindowRateLimiter:
    """Allows at most `limit` hits per `window_seconds`, per client key.

    Each client gets a queue of hit timestamps. On every check we drop the
    timestamps that have slid out of the window, then count what's left.
    Unlike a fixed "per clock hour" counter, a client can't burst 2x the
    limit by straddling the hour boundary.

    It lives in process memory: simple and fast, but each server process
    keeps its own counts and they reset on restart. That's fine for a
    single-instance deploy; the DB-backed daily cap in ai_cache.py is the
    backstop that holds across processes. Many instances would move this
    into Redis.
    """

    def __init__(self, limit: int, window_seconds: int, clock=time.monotonic):
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()  # FastAPI runs sync endpoints in a thread pool

    def check(self, key: str) -> None:
        """Record a hit for `key`, or raise 429 if it's over the limit."""
        with self._lock:
            now = self._clock()
            hits = self._hits[key]
            while hits and hits[0] <= now - self.window_seconds:
                hits.popleft()

            if len(hits) >= self.limit:
                # Tell the client exactly when its oldest hit expires.
                retry_after = math.ceil(hits[0] + self.window_seconds - now)
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many AI requests — try again in {retry_after} seconds",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


ai_rate_limiter = SlidingWindowRateLimiter(
    limit=config.AI_RATE_LIMIT, window_seconds=config.AI_RATE_LIMIT_WINDOW_SECONDS
)


def get_rate_limiter() -> SlidingWindowRateLimiter:
    return ai_rate_limiter
