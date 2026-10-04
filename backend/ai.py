from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from ai_client import AIClient, get_ai_client
from database import get_db

# All AI endpoints hang off an application: the job description lives on
# the application row, so the client only sends what we don't already have.
router = APIRouter(prefix="/applications/{application_id}", tags=["ai"])


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
    db: Session = Depends(get_db),
    ai: AIClient = Depends(get_ai_client),
):
    application = get_application_or_404(application_id, db)

    system = "You are a career coach who writes concise, specific cover letters."
    prompt = (
        f"Write a cover letter for the {application.position} role at {application.company}.\n\n"
        f"Job description:\n{application.job_description}\n\n"
        f"Candidate resume:\n{request.resume_text}\n\n"
        "Keep it under 350 words. Only claim experience that appears in the resume."
    )

    return schemas.CoverLetterResponse(application_id=application.id, cover_letter=ai.complete(system, prompt))
