# syntax=docker/dockerfile:1
# Production image for the OrderTrack API (Flask + gunicorn).
# Multi-stage: deps are built in a throwaway stage, runtime is slim + non-root.

# ---- stage 1: build dependencies into an isolated venv ----
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt gunicorn

# ---- stage 2: runtime ----
FROM python:3.12-slim AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8010

WORKDIR /app

# Bring in the prebuilt venv and only the app code we need to run.
COPY --from=builder /opt/venv /opt/venv
COPY app ./app
COPY wsgi.py ./

# Run as an unprivileged user.
RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app
USER app

EXPOSE 8010

# Health check hits the app's health endpoint (mounted at /api/health).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://localhost:8010/api/health').status==200 else 1)"

# gunicorn serves the WSGI `app` object exported by wsgi.py.
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8010", "--access-logfile", "-", "wsgi:app"]
