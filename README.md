# JobTrail

AI-Powered Job Application Tracker — track applications, contacts, and interview stages, with an AI layer for cover letters and resume-fit scoring.

## Stack

React (Vite) · FastAPI · PostgreSQL · SQLAlchemy · Docker · Claude API

## Features

- Dashboard with applications grouped into a status pipeline (Applied → Interview → Offer → Rejected)
- Create and edit applications through a validated form
- REST API with Pydantic request/response validation
- Loading and error states, with an error boundary around the app

## Setup

### Prerequisites

- Python 3.13+
- Node 18+
- PostgreSQL running locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

createdb jobtrail   # only needed once

uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

## Tests

```bash
cd backend
source .venv/bin/activate
pytest
```
