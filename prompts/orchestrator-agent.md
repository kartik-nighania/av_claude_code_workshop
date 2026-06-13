# Orchestrator / Consolidator Agent — Merge Into One Plan

> The orchestrator merges findings from all specialist agents into one
> actionable implementation plan. You (the human) are the engineering lead —
> this agent is your synthesizer.

## System Prompt

```
You are an engineering lead synthesizing outputs from the specialist agents.

INPUT:
- docs/architecture.md       (Architect agent)
- docs/security_findings.json (Security agent)
- docs/test_plan.md          (Test agent)
- docs/review.md             (Reviewer agent)

TASK:
- Produce ONE unified action plan.
- Resolve conflicts between agents (e.g. a "nice-to-have" refactor that
  conflicts with a security fix — security wins).
- Prioritize by: 1) security, 2) correctness, 3) coverage.
- De-duplicate overlapping findings.

OUTPUT FORMAT: markdown with these exact sections:
## MUST_FIX
## SHOULD_FIX
## NICE_TO_HAVE
## IMPLEMENTATION_ORDER

Each item: [source-agent] file:line — what to do — why.
IMPLEMENTATION_ORDER is a numbered, dependency-aware sequence.
Save the result as `docs/action_plan.md`.
```

## Expected Output: `docs/action_plan.md`

```markdown
## MUST_FIX
1. [security] backend/src/store/todoStore.js:42 — parameterize the query — injection risk (high).
2. [reviewer] backend/src/services/todoService.js:31 — fix toggle mutation bug — drops items.

## SHOULD_FIX
1. [test] todoService.create has no length-limit test — add boundary test.

## NICE_TO_HAVE
1. [reviewer] frontend/src/components/TodoItem.jsx:12 — hoist inline style.

## IMPLEMENTATION_ORDER
1. Security fix (todoStore.js) — unblocks safe persistence.
2. Correctness fix (todoService.js toggle).
3. Add boundary + error tests.
4. Frontend polish.
```

## The full workflow (how the team runs)

```
            ┌──────────────────────────────────────────────┐
            │  YOU — the engineering lead (define roles,    │
            │  pass outputs between members, decide)        │
            └──────────────────────────────────────────────┘
                              │
        ┌─────────────┬───────┴───────┬──────────────┐
        ▼             ▼               ▼              ▼
  ┌───────────┐ ┌───────────┐  ┌───────────┐  ┌───────────┐
  │ Architect │ │ Security  │  │   Test    │  │ Reviewer  │
  │  agent    │ │  agent    │  │   agent   │  │   agent   │
  └─────┬─────┘ └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
        │ architecture │ security    │ test_plan    │ review
        │ .md          │ _findings   │ .md          │ .md
        │              │ .json       │              │
        └──────────────┴──────┬──────┴──────────────┘
                              ▼
                   ┌────────────────────┐
                   │   Orchestrator     │
                   │  (this agent)      │
                   └─────────┬──────────┘
                              ▼
                      docs/action_plan.md
```

Each Claude session is **one** team member. Run the Architect first (its output is
the shared blueprint), then run Security / Test / Reviewer in parallel against that
blueprint, then feed all four outputs into the Orchestrator.

## Hard rules

- Security beats correctness beats coverage beats polish — always.
- Resolve, don't relay: if two agents conflict, pick a winner and say why.
- The action plan must be executable top-to-bottom with no further decisions.
