"""Response cache for Claude calls, stored in Postgres.

The same application + resume + prompt always produces the same request,
so there's no reason to pay for it (or wait ~5s for it) twice. Before
calling Claude we hash everything that shapes the request; if a fresh row
with that hash exists, we return it instead.

Rate limits apply only on a cache miss — re-opening a result you already
generated is free and never blocked.
"""

import hashlib
import json
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import config
import models
from ai_client import AIClient
from prompts import PromptTemplate
from rate_limit import SlidingWindowRateLimiter


def make_cache_key(template: PromptTemplate, model: str, prompt: str) -> str:
    # The template version is part of the key, so editing a prompt (and
    # bumping its version) automatically stops serving answers to the old one.
    # The rendered prompt already contains the job description and resume.
    payload = json.dumps(
        {
            "template": template.name,
            "version": template.version,
            "model": model,
            "system": template.system,
            "prompt": prompt,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    # SQLite (used in tests) hands back naive datetimes; Postgres returns aware ones.
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def cached_complete(
    db: Session,
    ai: AIClient,
    limiter: SlidingWindowRateLimiter,
    client_key: str,
    template: PromptTemplate,
    prompt: str,
) -> tuple[str, bool]:
    """Return (reply_text, was_cached)."""
    model = getattr(ai, "model", "unknown")
    key = make_cache_key(template, model, prompt)

    entry = db.query(models.AIResponse).filter(models.AIResponse.cache_key == key).first()
    if entry is not None:
        age = _utcnow() - _as_utc(entry.created_at)
        if age < timedelta(hours=config.AI_CACHE_TTL_HOURS):
            return entry.response, True
        # Expired — drop it and fetch a fresh answer below.
        db.delete(entry)
        db.commit()

    # Cache miss: this will cost a real API call, so the limits apply now.
    limiter.check(client_key)
    _check_daily_budget(db)

    reply = ai.complete(template.system, prompt)

    db.add(
        models.AIResponse(
            cache_key=key,
            template_name=template.name,
            template_version=template.version,
            model=model,
            response=reply,
        )
    )
    try:
        db.commit()
    except IntegrityError:
        # Two identical requests raced and the other one saved first. Its
        # row is just as good; keep our reply and move on.
        db.rollback()
    return reply, False


def _check_daily_budget(db: Session) -> None:
    """A global cap on real API calls per 24h, across every client.

    Every miss writes one ai_responses row, so counting recent rows counts
    recent paid calls — and because it lives in the database it holds across
    server restarts and multiple processes, unlike the in-memory limiter.
    It protects the API bill if the per-client limit is dodged (e.g. by
    rotating IP addresses) on a public demo.
    """
    since = _utcnow() - timedelta(hours=24)
    recent_calls = db.query(models.AIResponse).filter(models.AIResponse.created_at >= since).count()
    if recent_calls >= config.AI_DAILY_LIMIT:
        raise HTTPException(status_code=429, detail="Daily AI usage limit reached — try again tomorrow")
