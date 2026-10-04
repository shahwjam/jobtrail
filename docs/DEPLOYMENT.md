# Deploying JobTrail

JobTrail deploys to [Render](https://render.com) from `render.yaml` (a "Blueprint"): one Postgres database, the FastAPI backend as a Docker web service, and the React frontend as a static site. Everything fits in Render's free tier.

## Before you start

- The code is merged to `main` on GitHub.
- You have an Anthropic API key from [console.anthropic.com](https://console.anthropic.com). Set a monthly spend limit there too — it's a public demo.

## 1. Create the Blueprint

1. Sign in to Render with GitHub.
2. **New → Blueprint**, pick the `jobtrail` repo, branch `main`.
3. Render reads `render.yaml` and lists `jobtrail-db`, `jobtrail-api` and `jobtrail-web`. It asks for the `sync: false` values:

| Variable | Service | Value |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | jobtrail-api | your `sk-ant-...` key |
| `CORS_ORIGINS` | jobtrail-api | `https://jobtrail-web.onrender.com` |
| `VITE_API_URL` | jobtrail-web | `https://jobtrail-api.onrender.com` |

Render URLs are `https://<service-name>.onrender.com`. If a name was taken, Render adds a suffix — check the real URLs on each service's page after the first deploy, then fix the two URL variables (step 3).

4. **Apply**. The database comes up first, then the API (Docker build, ~3–5 min), then the site.

## 2. Check it works

- `https://jobtrail-api.onrender.com/` → `{"status":"ok","service":"JobTrail API"}`
- `https://jobtrail-api.onrender.com/docs` → interactive API docs
- `https://jobtrail-web.onrender.com` → the dashboard; add an application, paste a job description, open **AI tools**.

## 3. If something's wrong

| Symptom | Cause / fix |
| --- | --- |
| Dashboard says "Couldn't load applications: Failed to fetch" | Browser console shows a CORS error → `CORS_ORIGINS` on the API must exactly match the site URL (scheme included, no trailing slash). Save → the API redeploys. |
| Site calls `localhost:8000` | `VITE_API_URL` was wrong or empty at build time. It is baked into the bundle, so after fixing it trigger **Manual Deploy → Clear build cache & deploy** on `jobtrail-web`. |
| AI buttons return 503 "not configured" | `ANTHROPIC_API_KEY` missing on `jobtrail-api`. |
| AI buttons return 502 | Key invalid or out of credit — the real reason is in the `jobtrail-api` logs. |
| First request takes ~50s | Free web services sleep after 15 min idle. Open the API URL a minute before a demo. |

## Free-tier limits worth knowing

- Free web services spin down when idle (cold start on the next request).
- Render's free Postgres expires after a limited period unless upgraded — check Render's current free-tier terms, and don't keep data there you can't lose.
- Rate limiting is in-memory per process — correct for one free instance. The DB-backed daily cap (`AI_DAILY_LIMIT`) still holds across restarts.

## Other hosts

The backend image (`backend/Dockerfile`) binds `$PORT`, so it runs unchanged on Railway or Fly.io; set the same environment variables there. The frontend Dockerfile serves the built site with nginx on `$PORT` for hosts without a static-site product.
