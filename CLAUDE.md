# CLAUDE.md — Multi-Agent TODO Lab

This repo is the base structure for a **hands-on lab on the multi-agent mental
model**: treat a set of Claude sessions as a specialized engineering team, where
each member has one job and does it deeply. You are the engineering lead.

## What's here

```
prompts/                 # System prompts for each specialist agent
  architect-agent.md
  security-agent.md
  test-agent.md
  reviewer-agent.md
  orchestrator-agent.md
docs/
  architecture.md        # Architect agent's blueprint (pre-seeded sample)
  # security_findings.json, test_plan.md, review.md, action_plan.md  ← created in the lab
backend/                 # Express REST API (Node, ESM) — the app under construction
frontend/                # React + Vite UI
```

## The agent team (the mental model)

| Agent        | One job                                          | Output                      |
| ------------ | ------------------------------------------------ | --------------------------- |
| Architect    | System design only — structure, API, data flows  | `docs/architecture.md`      |
| Security     | OWASP / injection / auth / data exposure only    | `docs/security_findings.json` |
| Test         | Unit + integration + edge/error tests only       | `tests/` + `docs/test_plan.md` |
| Reviewer     | Correctness / readability / perf / maintainability| `docs/review.md`            |
| Orchestrator | Merge all outputs into one prioritized plan      | `docs/action_plan.md`       |

Each Claude session is **one** team member. Run the Architect first (its doc is
the shared contract), then run Security / Test / Reviewer against that doc, then
feed all four outputs into the Orchestrator. Full prompts live in `prompts/`.

**Lane discipline is the whole point:** the Security agent does not suggest
refactors; the Reviewer does not re-do security; the Test agent does not change
the design. Keeping each agent narrow is what makes the outputs trustworthy.

## Tech stack

- **Backend:** Node.js (ESM) + Express. In-memory store (swap for a real DB in the lab).
- **Frontend:** React 18 + Vite.
- **Tests:** Jest + Supertest (backend). The Test agent uses Jest/Pytest syntax.

## Running it

One command from the repo root (npm workspaces + `concurrently`):

```bash
./startup.sh          # install deps if needed, run backend + frontend together
./startup.sh test     # run the backend test suite

# equivalents:
npm install && npm run dev    # both servers
npm run dev:backend           # backend only → http://localhost:3001
npm run dev:frontend          # frontend only → http://localhost:5173
npm test                      # backend tests
```

The frontend dev server proxies `/api/*` to the backend on :3001 (see
`frontend/vite.config.js`), so no CORS setup is needed in dev.

## Conventions for any agent working in this repo

- **Backend layering is strict:** `routes → controllers → services → store`.
  Keep HTTP concerns (req/res, status codes) in controllers; keep business rules
  and validation in services; keep persistence in the store. Services throw typed
  errors (`ValidationError`, `NotFoundError`) that carry a `.status`.
- **ESM everywhere** (`import`/`export`, `"type": "module"`). Use `.js`/`.jsx`.
- **No secrets in code.** Config comes from env vars (`PORT`).
- Match the existing file style; keep comments purposeful, not decorative.

## Suggested lab flow (a feature, end to end with the team)

1. Pick a feature (e.g. "add tags to todos").
2. **Architect** → update `docs/architecture.md`.
3. Implement the change in `backend/` + `frontend/`.
4. **Security**, **Test**, **Reviewer** agents run in parallel against the diff.
5. **Orchestrator** merges their outputs → `docs/action_plan.md`.
6. You (lead) execute the action plan top-to-bottom; re-run tests.
