# Demo script (~5 minutes)

A walkthrough for interviews or a final presentation. Open the live app, `/docs`, and the repo in three tabs. If it's on Render's free tier, open the API URL a minute early so it isn't cold-starting.

## 1. The problem (30s)

Job hunting means dozens of applications across spreadsheets and inboxes, and tailoring every cover letter by hand. JobTrail keeps them in one pipeline and uses Claude for the repetitive writing and screening.

## 2. Core app (1 min)

- Add an application, paste a real job posting into the description.
- Edit it to move it from Applied → Interview; the card changes columns.
- Point out: the form validates on the client, and Pydantic re-validates on the server (try `"status": "no"` in `/docs` → 422).

## 3. AI features (2 min)

- Open **AI tools**, paste a resume, click **Score resume match** → score, matched and missing keywords. The score now shows on the card.
- **Generate cover letter** with a tone. Note it only uses experience from the resume.
- Click generate again → "served from cache, no new API call". Explain the cache key: template version + model + full prompt.

## 4. Engineering decisions (1 min)

Pick two or three, depending on the audience:

- Prompt injection: postings are wrapped in tags and treated as data.
- Validating LLM output: bad JSON → 502, never a fabricated score.
- Rate limiting: sliding window per client, only on cache misses; DB-backed daily cap as a backstop. Trade-off: in-memory limiter is per-process — Redis next.
- Testability: Claude client is a FastAPI dependency; 39 tests run with a fake, no API cost.

## 5. Infrastructure (30s)

`docker compose up` runs Postgres, API, and frontend with healthchecks. Production is a Render Blueprint (`render.yaml`): one file, no secrets in Git.

## Likely questions

- **Why cache in Postgres, not Redis?** It's already there, one less service to run, and the cache table doubles as a usage log for the daily cap. Redis would win for hot, high-volume keys.
- **How would you add auth?** Users table, hashed passwords or OAuth, JWT/session middleware, then a `user_id` foreign key on applications and every query filtered by it.
- **What breaks at scale?** In-memory rate limits across instances, synchronous AI calls holding worker threads (move to async or a job queue), and `create_all` instead of real migrations.
