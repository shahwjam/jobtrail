from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="JobTrail API")

# --- Temporary in-memory store (replaced by PostgreSQL in TASK-007) ---
applications = []
next_id = 1


# --- Minimal request model: the shape of data we accept on create.
#     You'll build this out into full validation schemas in TASK-008. ---
class ApplicationCreate(BaseModel):
    company: str
    position: str
    status: str = "Applied"
    job_description: str | None = None


@app.get("/")
def read_root():
    return {"status": "ok", "service": "JobTrail API"}


@app.post("/applications", status_code=201)
def create_application(application: ApplicationCreate):
    global next_id
    new_application = {
        "id": next_id,
        "company": application.company,
        "position": application.position,
        "status": application.status,
        "job_description": application.job_description,
    }
    applications.append(new_application)
    next_id += 1
    return new_application


@app.get("/applications")
def get_applications():
    return applications
