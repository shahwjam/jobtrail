from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


# A fixed set of valid statuses — this is what kills "status": "no"
class ApplicationStatus(str, Enum):
    applied = "Applied"
    interview = "Interview"
    offer = "Offer"
    rejected = "Rejected"


# What a client may SEND when creating an application
class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    status: ApplicationStatus = ApplicationStatus.applied
    job_description: str | None = None


# What a client may SEND when editing an application — every field is
# optional so a client can PATCH just the one field that changed
class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=200)
    position: str | None = Field(default=None, min_length=1, max_length=200)
    status: ApplicationStatus | None = None
    job_description: str | None = None


# What the API SENDS BACK — defines exactly which fields go out
class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    position: str
    status: ApplicationStatus
    job_description: str | None
    created_at: datetime
    match_score: int | None = None


# === AI features ===

# The resume is sent with each AI request rather than stored — users may
# keep several resume versions and we don't need to hold that data.
# Keys must match prompts.COVER_LETTER_TONES
class CoverLetterTone(str, Enum):
    professional = "professional"
    enthusiastic = "enthusiastic"
    concise = "concise"


class CoverLetterRequest(BaseModel):
    resume_text: str = Field(min_length=50, max_length=20000)
    tone: CoverLetterTone = CoverLetterTone.professional


class CoverLetterResponse(BaseModel):
    application_id: int
    cover_letter: str


class MatchScoreRequest(BaseModel):
    resume_text: str = Field(min_length=50, max_length=20000)


# Also used to validate Claude's JSON reply before it's saved — a model
# that answers "score": 140 or forgets a field is caught here, not in the UI.
class MatchResult(BaseModel):
    score: int = Field(ge=0, le=100)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    summary: str | None = None


class MatchScoreResponse(MatchResult):
    model_config = ConfigDict(from_attributes=True)

    application_id: int
    updated_at: datetime | None = None
