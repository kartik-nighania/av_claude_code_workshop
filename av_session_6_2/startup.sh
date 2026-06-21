#!/usr/bin/env bash
# Launch the HealthTrack stack (frontend + api + Postgres + Redis) and stay open.
#   UI  -> http://localhost:3000
#   API -> http://localhost:8000
#
#   ./startup.sh        build + start, wait until healthy, then stream logs.
#                       Press Ctrl+C (or close the terminal) to run
#                       `docker compose down` automatically.
#   ./startup.sh down   stop and remove containers + volumes (clean slate).
set -euo pipefail

cd "$(dirname "$0")"

if [ "${1:-}" = "down" ]; then
  docker compose down -v
  exit 0
fi

LOGS_PID=""

# Tear the stack down on Ctrl+C, SIGTERM, terminal close (SIGHUP), or normal exit.
cleanup() {
  trap - INT TERM HUP EXIT          # disarm so this runs only once
  echo
  echo "Stopping — docker compose down..."
  [ -n "$LOGS_PID" ] && kill "$LOGS_PID" 2>/dev/null || true
  docker compose down
  exit 0
}
trap cleanup INT TERM HUP EXIT

# A .env (real values, gitignored) is required; seed it from the committed example.
if [ ! -f .env ]; then
  echo "No .env found — creating one from .env.example (edit secrets before production)."
  cp .env.example .env
fi

# wait_healthy <service-name> : block until the service reports healthy.
wait_healthy() {
  local svc="$1" cid status
  cid="$(docker compose ps -q "$svc")"
  echo -n "Waiting for '$svc' to become healthy"
  for _ in $(seq 1 90); do
    status="$(docker inspect -f '{{.State.Health.Status}}' "$cid" 2>/dev/null || echo starting)"
    case "$status" in
      healthy)   echo " — healthy."; return 0 ;;
      unhealthy) echo " — unhealthy!"; docker compose logs "$svc" | tail -30; return 1 ;;
    esac
    echo -n "."
    sleep 2
  done
  echo " — timed out."
  docker compose ps
  docker compose logs "$svc" | tail -30
  return 1
}

echo "Building images..."
docker compose build

echo "Starting frontend + api + db + cache..."
docker compose up -d

wait_healthy api
wait_healthy frontend

echo
echo "HealthTrack is up:"
echo "  UI     : http://localhost:3000"
echo "  API    : http://localhost:8000"
echo "  health : curl http://localhost:8000/health"
echo
echo "Streaming logs — press Ctrl+C (or close this window) to stop and tear down."
echo "----------------------------------------------------------------------"

# Stay open by streaming logs. `wait` is interruptible by the trap above, so a
# Ctrl+C cleanly triggers cleanup() -> docker compose down.
docker compose logs -f &
LOGS_PID=$!
wait "$LOGS_PID"
