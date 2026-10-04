# JobTrail API — production image
#
# Build:  docker build -t jobtrail-backend ./backend
# Run:    docker run -p 8000:8000 -e DATABASE_URL=... -e ANTHROPIC_API_KEY=... jobtrail-backend

# slim = Debian without the extras: ~150 MB instead of ~1 GB for the full
# image. psycopg2-binary ships its own libpq, so no compilers are needed.
FROM python:3.13-slim

# Don't write .pyc files into the image; flush logs straight to stdout so
# `docker logs` and the cloud dashboard show them immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy ONLY requirements first. Docker caches each layer, so as long as
# requirements.txt is unchanged, editing code skips the slow pip install.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Never run as root inside the container — if the app is ever exploited,
# the attacker gets an unprivileged user, not root.
RUN useradd --create-home --uid 1000 appuser
USER appuser

# Cloud hosts (Render, Railway, Fly) tell the app which port to bind via
# $PORT; default to 8000 locally. --proxy-headers trusts X-Forwarded-For
# from the platform's load balancer, so the rate limiter sees real client
# IPs instead of the proxy's.
ENV PORT=8000
EXPOSE 8000

# Lets Docker (and docker compose depends_on) know when the API is actually up.
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"PORT\"]}/')" || exit 1

# Shell form so $PORT is expanded at runtime; exec replaces the shell so
# uvicorn receives Docker's stop signal (SIGTERM) and shuts down cleanly.
CMD exec uvicorn main:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips="*"
