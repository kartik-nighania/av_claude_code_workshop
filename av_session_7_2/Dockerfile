# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# OrderTrack API — production image (multi-stage, non-root, gunicorn).
# ---------------------------------------------------------------------------

# ---- Stage 1: builder — install deps into an isolated prefix --------------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
COPY requirements.txt .

# Install runtime deps + gunicorn into /install (copied into the final stage).
RUN pip install --prefix=/install -r requirements.txt gunicorn==23.0.0

# ---- Stage 2: runtime — slim, non-root ------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8010

# Copy installed packages from the builder.
COPY --from=builder /install /usr/local

# Create an unprivileged user and run as it.
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY app/ ./app/
COPY wsgi.py ./
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8010

# Container health: hit the API's health endpoint (200 = healthy).
# NOTE: the real route is /api/health (the health blueprint is mounted at /api).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8010/api/health', timeout=4).status==200 else 1)"

# Production WSGI server. 2 workers × 4 threads is a sane small-box default.
CMD ["gunicorn", "--bind", "0.0.0.0:8010", "--workers", "2", "--threads", "4", "--timeout", "60", "wsgi:app"]
