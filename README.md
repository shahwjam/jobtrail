# JobTrail

> An AI-powered job application tracker that helps job seekers manage applications, contacts, and interview stages — with AI-generated cover letters and resume-fit scoring.

JobTrail is a full-stack web application that solves a problem every job seeker knows: losing track of where you applied, who you spoke with, and what stage each application is in. It pairs a clean tracking interface with an AI layer (powered by the Claude API) that drafts cover letters and scores how well a resume fits a job description.

## Tech Stack

- **Frontend:** React (Vite)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **AI:** Claude API
- **DevOps:** Docker

## Project Structure

```
jobtrail/
├── frontend/    # React + Vite single-page app
├── backend/     # FastAPI REST API
├── db/          # PostgreSQL schema
└── README.md
```

## Getting Started

### Prerequisites

- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (v18 or newer) and npm
- [Python](https://www.python.org/) (3.10 or newer)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/jobtrail.git
cd jobtrail
```

### 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at http://localhost:5173

### 3. Backend setup

In a second terminal:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at http://127.0.0.1:8000
Interactive API docs: http://127.0.0.1:8000/docs

### 4. Database

The PostgreSQL schema lives in `db/schema.sql`. Database setup and integration arrive in Sprint 2.

## Roadmap

- [x] Sprint 1 — Project setup (repo, frontend, backend, schema, docs)
- [ ] Sprint 2 — Core backend REST API
- [ ] Sprint 3 — Frontend dashboard & integration
- [ ] Sprint 4 — AI features (cover letters, resume scoring)
- [ ] Sprint 5 — Docker & deployment

---

Built by **Shahwan ALchomer** as a full-stack engineering project.