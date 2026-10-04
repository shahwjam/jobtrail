import os

from dotenv import load_dotenv

# Reads backend/.env (if it exists) into the process environment, so local
# dev can keep secrets out of the code. In Docker / the cloud, the platform
# sets real environment variables instead and there is no .env file.
load_dotenv()

# Default matches a Homebrew Postgres on a Mac: your username, no password.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://localhost/jobtrail")

# Some hosts (Render, Heroku) hand out "postgres://..." URLs, which
# SQLAlchemy 2.x no longer accepts — normalize them to the psycopg2 dialect.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

# Comma-separated list of browser origins allowed to call the API.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

# Claude API. The key is never committed — set it in backend/.env locally.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1024"))

# Protects the Claude bill. Only real API calls count — cache hits are free.
AI_RATE_LIMIT = int(os.getenv("AI_RATE_LIMIT", "10"))  # per client...
AI_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("AI_RATE_LIMIT_WINDOW_SECONDS", "3600"))  # ...per hour
AI_DAILY_LIMIT = int(os.getenv("AI_DAILY_LIMIT", "200"))  # across all clients, per 24h
AI_CACHE_TTL_HOURS = int(os.getenv("AI_CACHE_TTL_HOURS", "168"))  # one week
