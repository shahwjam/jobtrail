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


# What the API SENDS BACK — defines exactly which fields go out
class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    position: str
    status: ApplicationStatus
    job_description: str | None
    created_at: datetime
