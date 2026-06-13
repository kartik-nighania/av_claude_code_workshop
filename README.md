# Multi-Agent TODO Lab

A complete, runnable **end-to-end TODO app** (React + Vite frontend, Express
backend) plus a set of **specialist agent prompts** — the base structure for a
hands-on lab on the multi-agent mental model.

> Think of it as a specialized engineering team: each Claude session is one team
> member with one job, done deeply. You're the engineering lead.

## Quick start

One command from the repo root boots both servers:

```bash
./startup.sh          # installs deps if needed, then runs backend + frontend
# or, equivalently:
npm install && npm run dev
```

- Backend  → http://localhost:3001
- Frontend → http://localhost:5173  (proxies `/api` to the backend)

Other shortcuts:

```bash
./startup.sh test     # run the backend test suite
npm test              # same, from the root
npm run dev:backend   # backend only
npm run dev:frontend  # frontend only
```

Open http://localhost:5173 — add, complete, and delete todos. The demo works out
of the box with a couple of seeded items.

## What's in the box

- **`backend/`** — Express REST API in clean layers (`routes → controllers →
  services → store`). In-memory store, swappable for a real DB.
- **`frontend/`** — React 18 + Vite UI calling the API.
- **`prompts/`** — five agent system prompts (Architect, Security, Test,
  Reviewer, Orchestrator). See `prompts/README.md`.
- **`docs/architecture.md`** — a pre-seeded Architect blueprint.
- **`CLAUDE.md`** — repo guide + the lab flow.

## The lab

Pick a feature (e.g. tags, due dates, auth) and take it through the team:
Architect → implement → Security + Test + Reviewer (parallel) → Orchestrator
merges into one action plan → you execute it. Full flow in `CLAUDE.md`.
