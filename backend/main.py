from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

import models
from database import engine, get_db

# Create tables from your models if they don't exist yet.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobTrail API")


class ApplicationCreate(BaseModel):
    company: str
    position: str
    status: str = "Applied"
    job_description: str | None = None


@app.get("/")
def read_root():
    return {"status": "ok", "service": "JobTrail API"}


@app.post("/applications", status_code=201)
def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    new_application = models.Application(**application.model_dump())
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application


@app.get("/applications")
def get_applications(db: Session = Depends(get_db)):
    return db.query(models.Application).all()