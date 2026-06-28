# Sample prompts for the repository


## Architecture MD file
MEDIUM EFFORT

```
For this task only read the folder here av_session_7_2
Do this task fast

Generate:
1. System architecture diagram (ASCII)
2. Data flow: request → service → DB
3. List of every endpoint with HTTP method
4. Identify missing features vs prod
5. Propose the implementation plan for this capstone

Save summary to docs/ARCHITECTURE.md
```


## Claude.md file
MEDIUM EFFORT

```
For this task only read the folder here av_session_7_2
Do this task fast

Generate a CLAUDE.md for this repo.

Include:
1. Project overview & tech stack
2. How to run locally
3. Coding conventions used
4. What Claude is allowed to generate
5. What requires human review
6. Known limitations of this codebase
7. How to run tests
```


## JWT Auth
MEDIUM EFFORT

```
For this task only read the folder here av_session_7_2
Do this task fast

Add JWT authentication to OrderTrack API.

Requirements:

- POST /auth/login → returns access token
- POST /auth/register → creates new user
- @require_auth decorator for protected routes
- Token expiry: 24 hours
- Passwords hashed with bcrypt
- No plaintext passwords ever logged
- User model: id, email, hashed_password

Apply to: /api/orders, /api/products

Also create a single UI for login and registration.
Show the registered name on top of user.

Leave /health unprotected
```


## Pytest Testing
MEDIUM EFFORT

```
For this task only read the folder here av_session_7_2
Do this task fast

Write a complete pytest test suite for OrderTrack API. Requirements:

- Cover all CRUD endpoints (orders, products, customers)
- Cover auth: login, register, token expiry, invalid token
- Coverage target: ≥ 80%
- Mock the DB with SQLite in-memory
- Use pytest fixtures for client/user
- Include negative cases (400, 401, 404)
- Save to tests/ directory
```


## CI Integration
MEDIUM EFFORT

```
For this task create a file in the github/workflow folder on parent called: test-cicd.yaml
Do this task fast

On PR creation on main branch, CI should do:
Job 1: lint
  Command: flake8 + black --check on app/ and tests/
  Needs: —

Job 2: test
  Command: pytest with --cov-fail-under=50
  Needs: lint

Job 3: security
  Command: bandit -r app/ + safety check -r requirements.txt
  Needs: lint

Job 4: ai-skills
  Command: Run official Claude code security-audit GH action, block merge on CRITICAL found
  Needs: test, security

Github secret already present for Claude code: CLAUDE_CODE_OAUTH_TOKEN
```


## Docker compose
MEDIUM EFFORT

```
For this task only read the folder here av_session_7_2
Do this task fast

Task:
- Generate a production Dockerfile (multi-stage, non-root, health check at /health) and docker-compose.yml for OrderTrack API with 4 services: api, frontend, db (postgres:15-alpine), cache (redis:7-alpine)
- Also generate .env.example with all required vars and also the actual .env file with all the real values.
Save all 3 files to this folder here av_session_7_2
```


## PR creation addition
MEDIUM EFFORT

```
Do this task fast

I've completed all capstone features. 
Push all my work to GitHub and create a PR.

Branch: feature/capstone-complete
Target: main

PR title: "feat: capstone — auth, tests, CI, Docker, CD"

PR body must include:-
- Summary of all changes
- List of AI-generated files
- Test coverage result
- Security audit result
- Any breaking changes
```