import json
import re

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

import models
import prompts
import schemas
from ai_cache import cached_complete
from ai_client import AIClient, get_ai_client
from database import get_db
from rate_limit import SlidingWindowRateLimiter, get_rate_limiter

# All AI endpoints hang off an application: the job description lives on
# the application row, so the client only sends what we don't already have.
router = APIRouter(prefix="/applications/{application_id}", tags=["ai"])


def client_key(request: Request) -> str:
    # Per-IP limiting. Behind a cloud load balancer, uvicorn's
    # --proxy-headers flag (see the Dockerfile) makes this the real client
    # IP from X-Forwarded-For rather than the proxy's address.
    return request.client.host if request.client else "unknown"


def get_application_or_404(application_id: int, db: Session) -> models.Application:
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if not application.job_description:
        # Without a job description there is nothing to tailor to — better to
        # say so than to pay for a generic letter.
        raise HTTPException(status_code=400, detail="Add a job description to this application first")
    return application


@router.post("/cover-letter", response_model=schemas.CoverLetterResponse)
def generate_cover_letter(
    application_id: int,
    request: schemas.CoverLetterRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    ai: AIClient = Depends(get_ai_client),
    limiter: SlidingWindowRateLimiter = Depends(get_rate_limiter),
):
    application = get_application_or_404(application_id, db)

    template = prompts.COVER_LETTER
    prompt = template.render(
        company=application.company,
        position=application.position,
        job_description=application.job_description,
        resume=request.resume_text,
        tone=prompts.COVER_LETTER_TONES[request.tone.value],
    )

    reply, cached = cached_complete(db, ai, limiter, client_key(http_request), template, prompt)
    return schemas.CoverLetterResponse(application_id=application.id, cover_letter=reply, cached=cached)



def parse_match_result(reply: str) -> schemas.MatchResult:
    """Turn Claude's reply into a validated MatchResult.

    We ask for bare JSON, but models sometimes wrap it in a ```json fence
    or add a sentence before it. Grab the outermost {...} and validate it;
    anything still unusable is a 502 (the upstream service misbehaved),
    not a crash and not a made-up score.
    """
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if match is None:
        raise HTTPException(status_code=502, detail="AI returned an unreadable match score")
    try:
        return schemas.MatchResult.model_validate(json.loads(match.group()))
    except (json.JSONDecodeError, ValidationError):
        raise HTTPException(status_code=502, detail="AI returned an unreadable match score")


@router.post("/match-score", response_model=schemas.MatchScoreResponse)
def score_resume_match(
    application_id: int,
    request: schemas.MatchScoreRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    ai: AIClient = Depends(get_ai_client),
    limiter: SlidingWindowRateLimiter = Depends(get_rate_limiter),
):
    application = get_application_or_404(application_id, db)

    template = prompts.RESUME_MATCH
    prompt = template.render(
        company=application.company,
        position=application.position,
        job_description=application.job_description,
        resume=request.resume_text,
    )
    reply, cached = cached_complete(db, ai, limiter, client_key(http_request), template, prompt)
    result = parse_match_result(reply)

    # Upsert: one stored score per application, overwritten on each re-run.
    if application.match is None:
        application.match = models.MatchScore(application_id=application.id, **result.model_dump())
    else:
        for field, value in result.model_dump().items():
            setattr(application.match, field, value)

    db.commit()
    db.refresh(application.match)
    response = schemas.MatchScoreResponse.model_validate(application.match)
    return response.model_copy(update={"cached": cached})


@router.get("/match-score", response_model=schemas.MatchScoreResponse)
def get_resume_match(application_id: int, db: Session = Depends(get_db)):
    score = db.query(models.MatchScore).filter(models.MatchScore.application_id == application_id).first()
    if score is None:
        raise HTTPException(status_code=404, detail="No match score yet for this application")
    return score
