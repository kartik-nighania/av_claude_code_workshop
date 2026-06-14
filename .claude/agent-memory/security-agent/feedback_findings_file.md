---
name: feedback-findings-file-shared
description: docs/security_findings.json is shared across backend and frontend reviews — append, do not overwrite
metadata:
  type: feedback
---

`docs/security_findings.json` is the single convention path for ALL security findings (backend and frontend). When running a scoped review (e.g. frontend-only), APPEND new findings to the existing array rather than overwriting — a prior run's findings live there.

**Why:** The repo convention (CLAUDE.md) names one findings file. The backend review (2026-06-13) wrote 11 findings there; the frontend review then appended 4 (FE-001..FE-004). Overwriting would have destroyed the backend findings.

**How to apply:** Read the file first. If it already has findings out of your scope, keep them and append yours. Use an `id` prefix (e.g. `FE-` for frontend) to keep scopes distinguishable. Flag the merge decision to the user since the schema in the prompt may differ slightly from what's already in the file.
