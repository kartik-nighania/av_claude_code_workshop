#!/usr/bin/env bash
#
# startup.sh — boot the whole OrderTrack stack locally:
#   1. ensure Postgres + Redis run as background Docker containers (start if not)
#   2. install + run the Flask backend  (http://localhost:8010)
#   3. install + run the React frontend (http://localhost:5173)
#
# No docker-compose: the two data stores are plain `docker run` containers.
# Ctrl-C stops the backend and frontend (the DB containers keep running).

set -euo pipefail
cd "$(dirname "$0")"

# ---- config ---------------------------------------------------------------
PG_CONTAINER="ordertrack-postgres"
REDIS_CONTAINER="ordertrack-redis"
PG_IMAGE="postgres:15-alpine"
REDIS_IMAGE="redis:7-alpine"

PG_USER="ordertrack"
PG_PASSWORD="ordertrack"
PG_DB="ordertrack"
PG_PORT="5432"
REDIS_PORT="6379"

export DATABASE_URL="postgresql://${PG_USER}:${PG_PASSWORD}@localhost:${PG_PORT}/${PG_DB}"
export REDIS_URL="redis://localhost:${REDIS_PORT}/0"
export PORT="8010"

# ---- helpers --------------------------------------------------------------
# ensure_container <name> <image> <docker run args...>
ensure_container() {
  local name="$1"; local image="$2"; shift 2
  if docker ps --format '{{.Names}}' | grep -qx "$name"; then
    echo "✓ $name already running"
  elif docker ps -a --format '{{.Names}}' | grep -qx "$name"; then
    echo "→ starting existing container $name"
    docker start "$name" >/dev/null
  else
    echo "→ creating container $name ($image)"
    docker run -d --name "$name" "$@" "$image" >/dev/null
  fi
}

# ---- 1. data stores -------------------------------------------------------
if ! docker info >/dev/null 2>&1; then
  echo "Docker doesn't appear to be running. Start Docker Desktop and retry." >&2
  exit 1
fi

ensure_container "$PG_CONTAINER" "$PG_IMAGE" \
  -p "${PG_PORT}:5432" \
  -e POSTGRES_USER="$PG_USER" \
  -e POSTGRES_PASSWORD="$PG_PASSWORD" \
  -e POSTGRES_DB="$PG_DB"

ensure_container "$REDIS_CONTAINER" "$REDIS_IMAGE" \
  -p "${REDIS_PORT}:6379"

echo -n "→ waiting for Postgres to accept connections"
until docker exec "$PG_CONTAINER" pg_isready -U "$PG_USER" >/dev/null 2>&1; do
  echo -n "."
  sleep 1
done
echo " ready"

# ---- 2. backend -----------------------------------------------------------
if [ ! -d ".venv" ]; then
  echo "→ creating Python virtualenv (.venv)"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
echo "→ installing backend dependencies"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "→ starting Flask backend on :${PORT}"
python wsgi.py &
BACKEND_PID=$!

# ---- 3. frontend ----------------------------------------------------------
pushd frontend >/dev/null
if [ ! -d "node_modules" ]; then
  echo "→ installing frontend dependencies"
  npm install --silent
fi
echo "→ starting React frontend on :5173"
npm run dev &
FRONTEND_PID=$!
popd >/dev/null

# ---- teardown -------------------------------------------------------------
cleanup() {
  echo
  echo "→ stopping backend ($BACKEND_PID) and frontend ($FRONTEND_PID)"
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  echo "  (DB containers $PG_CONTAINER / $REDIS_CONTAINER left running)"
}
trap cleanup EXIT INT TERM

echo
echo "OrderTrack is up:"
echo "  • API      http://localhost:${PORT}/api/health"
echo "  • Frontend http://localhost:5173"
echo "  Press Ctrl-C to stop."
wait
