# Stage 1: Builder — install deps into an isolated prefix for a clean copy.
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# Stage 2: Runtime — slim, non-root, only deps + app code.
FROM python:3.11-slim AS runtime
WORKDIR /app

# curl is required by the HEALTHCHECK below (the slim base ships without it).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/deps /app/deps
ENV PYTHONPATH=/app/deps
ENV FLASK_APP=app

COPY app/ ./app/

RUN useradd -m appuser && chown -R appuser /app
USER appuser

HEALTHCHECK CMD curl -f http://localhost:8000/health

EXPOSE 8000
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
