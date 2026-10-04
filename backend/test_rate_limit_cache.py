from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

import ai_cache
import config
import models
import prompts
from conftest import TestingSessionLocal
from rate_limit import SlidingWindowRateLimiter
from test_ai import MATCH_REPLY, RESUME, make_application


def cover_letter(client, application_id, resume=RESUME):
    return client.post(f"/applications/{application_id}/cover-letter", json={"resume_text": resume})


# === Caching ===

def test_identical_request_is_served_from_cache(client, fake_ai):
    application = make_application(client)

    first = cover_letter(client, application["id"])
    second = cover_letter(client, application["id"])

    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert second.json()["cover_letter"] == first.json()["cover_letter"]
    assert len(fake_ai.calls) == 1   # paid for once


def test_different_resume_is_a_cache_miss(client, fake_ai):
    application = make_application(client)
    cover_letter(client, application["id"])
    cover_letter(client, application["id"], resume=RESUME + " Also knows Docker.")
    assert len(fake_ai.calls) == 2


def test_editing_job_description_is_a_cache_miss(client, fake_ai):
    application = make_application(client)
    cover_letter(client, application["id"])
    client.patch(f"/applications/{application['id']}", json={"job_description": "Now we want Go."})
    cover_letter(client, application["id"])
    assert len(fake_ai.calls) == 2


def test_match_score_cached_too(client, fake_ai):
    fake_ai.reply = MATCH_REPLY
    application = make_application(client)
    path = f"/applications/{application['id']}/match-score"

    client.post(path, json={"resume_text": RESUME})
    second = client.post(path, json={"resume_text": RESUME})

    assert second.status_code == 200
    assert second.json()["cached"] is True
    assert second.json()["score"] == 80
    assert len(fake_ai.calls) == 1


def test_expired_cache_entry_is_refreshed(client, fake_ai):
    application = make_application(client)
    cover_letter(client, application["id"])

    # Age the cached row past the TTL
    db = TestingSessionLocal()
    entry = db.query(models.AIResponse).one()
    entry.created_at = datetime.now(timezone.utc) - timedelta(hours=config.AI_CACHE_TTL_HOURS + 1)
    db.commit()
    db.close()

    response = cover_letter(client, application["id"])
    assert response.json()["cached"] is False
    assert len(fake_ai.calls) == 2


def test_cache_key_changes_with_template_version():
    bumped = prompts.PromptTemplate(**{**prompts.COVER_LETTER.__dict__, "version": prompts.COVER_LETTER.version + 1})
    assert ai_cache.make_cache_key(prompts.COVER_LETTER, "m", "p") != ai_cache.make_cache_key(bumped, "m", "p")


def test_cache_key_changes_with_model():
    assert ai_cache.make_cache_key(prompts.COVER_LETTER, "a", "p") != ai_cache.make_cache_key(prompts.COVER_LETTER, "b", "p")


# === Rate limiting ===

def test_rate_limit_returns_429_with_retry_after(client, fake_ai, limiter):
    limiter.limit = 2
    application = make_application(client)

    assert cover_letter(client, application["id"], RESUME + " 1").status_code == 200
    assert cover_letter(client, application["id"], RESUME + " 2").status_code == 200
    blocked = cover_letter(client, application["id"], RESUME + " 3")

    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0
    assert len(fake_ai.calls) == 2   # the blocked request never reached Claude


def test_cache_hits_are_not_rate_limited(client, fake_ai, limiter):
    limiter.limit = 1
    application = make_application(client)

    cover_letter(client, application["id"])            # uses the only slot
    repeat = cover_letter(client, application["id"])   # cached — still allowed

    assert repeat.status_code == 200
    assert repeat.json()["cached"] is True


def test_daily_budget_blocks_across_clients(client, fake_ai, monkeypatch):
    monkeypatch.setattr(config, "AI_DAILY_LIMIT", 1)
    application = make_application(client)

    assert cover_letter(client, application["id"], RESUME + " a").status_code == 200
    blocked = cover_letter(client, application["id"], RESUME + " b")

    assert blocked.status_code == 429
    assert "Daily" in blocked.json()["detail"]


def test_sliding_window_frees_slots_as_time_passes():
    now = [1000.0]
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=60, clock=lambda: now[0])

    limiter.check("ip")
    now[0] += 30
    limiter.check("ip")
    with pytest.raises(HTTPException) as blocked:
        limiter.check("ip")
    assert blocked.value.headers["Retry-After"] == "30"   # first hit expires in 30s

    now[0] += 31   # first hit has slid out of the window
    limiter.check("ip")


def test_limits_are_per_client():
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60)
    limiter.check("1.1.1.1")
    limiter.check("2.2.2.2")   # different client, own budget
    with pytest.raises(HTTPException):
        limiter.check("1.1.1.1")
