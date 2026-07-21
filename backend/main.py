from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobTrail API")

# Lets the Vite dev server (a different origin) call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ok", "service": "JobTrail API"}


@app.post("/applications", response_model=schemas.ApplicationResponse, status_code=201)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    new_application = models.Application(**application.model_dump())
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application


@app.get("/applications", response_model=list[schemas.ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    return db.query(models.Application).all()