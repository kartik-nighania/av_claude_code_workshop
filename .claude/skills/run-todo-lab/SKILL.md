---
name: run-todo-lab
description: Run, start, launch, serve, smoke-test, or screenshot the Multi-Agent TODO Lab app — its Express backend API (:3001) and React/Vite frontend (:5173). Use to boot both servers, exercise the /api/todos CRUD endpoints end-to-end, or capture a screenshot of the running UI.
---

# Run the Multi-Agent TODO Lab

A web app: an **Express REST API** (`backend/`, port **3001**) and a **React +
Vite** frontend (`frontend/`, port **5173**, which proxies `/api/*` → backend).
Store is **in-memory**, seeded with 2 todos on every boot.

The agent path is a single zero-dependency Node driver,
**`.claude/skills/run-todo-lab/driver.mjs`**. It boots the backend, runs a full
CRUD + validation smoke against `/api/todos`, boots the frontend, and
screenshots the live UI with headless Chrome. It uses built-in `fetch` +
`child_process` — no Playwright, no install.

> All paths below are relative to the repo root
> (`/Users/kartik/Documents/analytics_vidhya`). Run commands from there.

## Prerequisites

Node 18+ (tested on v24). Install deps once (idempotent):

```bash
npm install        # or: ./startup.sh install
```

The screenshot step needs a Chrome/Chromium binary. It resolves in order:
`$CHROME_BIN` → the macOS default `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
→ `google-chrome`/`chromium` on `PATH`. On a machine without Chrome, run
`--api-only` (below) or set `CHROME_BIN`.

## Run (agent path) — driver.mjs

Full run: backend CRUD smoke + frontend boot + UI screenshot.

```bash
node .claude/skills/run-todo-lab/driver.mjs
```

Expected: every check prints a green `✓`, ending in `All checks passed.`, and a
screenshot lands at **`docs/screenshots/todo-app.png`** showing the seed todos
plus a `★ added by driver — end-to-end proof` item (the driver POSTs it via the
API, so a populated UI proves the React→Vite-proxy→Express round-trip).

**Always open the screenshot to confirm it rendered** (not a blank/loading
frame) — read `docs/screenshots/todo-app.png`.

Flags to drive one layer in isolation:

```bash
node .claude/skills/run-todo-lab/driver.mjs --api-only        # CRUD smoke only, no browser
node .claude/skills/run-todo-lab/driver.mjs --screenshot-only # boot servers + screenshot only
```

`--api-only` is the fast inner loop for backend/route/service/store changes.

## Direct invocation — poke one endpoint

Boot just the backend and hit it with `curl` (good for a single PR that touches
one route/service):

```bash
npm run dev:backend          # node --watch backend/src/server.js → :3001
curl -s localhost:3001/health
curl -s localhost:3001/api/todos
curl -s -X POST localhost:3001/api/todos -H 'Content-Type: application/json' -d '{"title":"hello"}'
curl -s -X PATCH localhost:3001/api/todos/1/toggle
curl -s -X DELETE -o /dev/null -w '%{http_code}\n' localhost:3001/api/todos/1   # → 204
```

API surface: `GET/POST /api/todos`, `GET/PUT/DELETE /api/todos/:id`,
`PATCH /api/todos/:id/toggle`, `GET /health`.

## Run (human path)

Both servers together, with a browser window you open yourself:

```bash
./startup.sh        # installs deps if needed, then npm run dev
# or: npm run dev    → backend :3001 + frontend :5173 (open http://localhost:5173)
```

Ctrl+C to stop. Headless agents can't see the window — use the driver instead.

## Test

Backend unit/integration suite (Jest + Supertest, 7 tests):

```bash
./startup.sh test    # or: npm test
```

## Gotchas

- **In-memory store resets on every backend restart.** Each boot re-seeds the
  same 2 todos (ids 1 & 2) and ids restart at 3. Anything you add via the API or
  driver vanishes when the backend stops — expected, not a bug. (Visible in the
  screenshot: a fresh backend shows "1 of 2 remaining".)
- **`--virtual-time-budget=6000` on the Chrome screenshot.** `--headless=new`
  usually waits for load on its own, but this flag makes a *populated* UI
  deterministic on a cold/slow first paint, so the fetch resolves before
  capture. Keep it.
- **Ports 3001 / 5173 must be free.** The driver spawns its own backend; if one
  is already running you'll get `EADDRINUSE`. Kill the stray server first
  (`lsof -ti:3001 | xargs kill`).
- **Frontend needs the backend up to show data** — the UI fetches `/api/todos`
  through the Vite proxy. `--screenshot-only` boots the backend too for this
  reason.

## Troubleshooting

- **`npm test` prints `ExperimentalWarning: VM Modules`** — harmless; the suite
  still reports `7 passed`. The flag is in `backend/package.json`'s test script.
- **Screenshot is blank / shows "Loading…"** — backend wasn't reachable from the
  frontend; confirm `curl localhost:3001/health` returns `{"status":"ok"}`, then
  re-run. Raise `--virtual-time-budget` if it persists.
- **`no Chrome/Chromium found`** — set `CHROME_BIN=/path/to/chrome`, or use
  `--api-only` to skip the browser entirely.
