#!/usr/bin/env bash
#
# startup.sh — one command to boot the multi-agent TODO lab.
#   ./startup.sh          install deps (if needed) and run backend + frontend
#   ./startup.sh test     run the backend test suite and exit
#   ./startup.sh install  install dependencies and exit
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BACKEND_PORT="${PORT:-3001}"
FRONTEND_PORT=5173

info()  { printf "\033[1;34m▸ %s\033[0m\n" "$1"; }
ok()    { printf "\033[1;32m✓ %s\033[0m\n" "$1"; }

ensure_deps() {
  if [ ! -d node_modules ] || [ ! -d backend/node_modules ] || [ ! -d frontend/node_modules ]; then
    info "Installing dependencies (npm workspaces)…"
    npm install
    ok "Dependencies installed"
  else
    ok "Dependencies already present"
  fi
}

case "${1:-dev}" in
  install)
    ensure_deps
    ;;

  test)
    ensure_deps
    info "Running backend tests…"
    npm test
    ;;

  dev|"")
    ensure_deps
    info "Backend  → http://localhost:${BACKEND_PORT}"
    info "Frontend → http://localhost:${FRONTEND_PORT}"
    echo
    ok "Starting both servers (Ctrl+C to stop)…"
    npm run dev
    ;;

  *)
    echo "Usage: ./startup.sh [dev|test|install]"
    exit 1
    ;;
esac
