# Architecture — TODO Service

> This is a sample Architect-agent output, pre-seeded so the lab has a blueprint
> on day 0. In the hands-on session, regenerate or extend it with the Architect
> agent (see `prompts/architect-agent.md`).

## Module Structure

```
backend/
  src/
    server.js              # entry point — binds app to a port
    app.js                 # express wiring + error middleware
    routes/todoRoutes.js   # /api/todos route table
    controllers/           # HTTP layer (req/res → service calls)
      todoController.js
    services/              # business logic + validation (no HTTP here)
      todoService.js
    store/                 # persistence (swappable; in-memory for the demo)
      todoStore.js
  tests/todos.test.js      # integration tests (supertest + jest)

frontend/
  src/
    main.jsx               # React entry
    App.jsx                # state container + data fetching
    api.js                 # fetch client for /api/todos
    components/
      AddTodo.jsx
      TodoList.jsx
      TodoItem.jsx
    styles.css
```

## Data Model

| Field       | Type    | Constraints                          |
| ----------- | ------- | ------------------------------------ |
| `id`        | integer | auto-increment, unique               |
| `title`     | string  | required, trimmed, ≤ 280 chars       |
| `completed` | boolean | defaults to `false`                  |
| `createdAt` | string  | ISO-8601 timestamp, set on insert    |

## API Surface

Base path: `/api/todos`

| Method | Path                | Request body            | Success         | Errors           |
| ------ | ------------------- | ----------------------- | --------------- | ---------------- |
| GET    | `/`                 | —                       | 200 `Todo[]`    | —                |
| POST   | `/`                 | `{ title }`             | 201 `Todo`      | 400              |
| GET    | `/:id`              | —                       | 200 `Todo`      | 400, 404         |
| PUT    | `/:id`              | `{ title?, completed? }`| 200 `Todo`      | 400, 404         |
| PATCH  | `/:id/toggle`       | —                       | 200 `Todo`      | 400, 404         |
| DELETE | `/:id`              | —                       | 204             | 400, 404         |

Plus `GET /health` → `{ status: "ok" }`.

## Data Flows

```
Request → app.js (json parse) → todoRoutes → todoController
        → todoService (validation + rules) → todoStore (persistence)
        → back up the stack → JSON response
Errors thrown in any layer carry `.status` and are mapped by app.js middleware.
```

## External Dependencies

- Backend: `express`, `cors`; dev: `jest`, `supertest`.
- Frontend: `react`, `react-dom`; dev: `vite`, `@vitejs/plugin-react`.
- Env: `PORT` (backend, default 3001). Frontend dev server proxies `/api` → :3001.

## Error Boundaries

| Failure                     | Where         | Surfaced as           |
| --------------------------- | ------------- | --------------------- |
| Missing/blank title         | todoService   | 400 `title is required` |
| Title too long (>280)       | todoService   | 400                   |
| Unknown id                  | todoService   | 404 `Todo not found`  |
| Non-integer id              | todoController| 400 `invalid id`      |
| Unmatched route             | app.js        | 404 `Not found`       |
| Unexpected error            | app.js        | 500 (logged)          |

## Open Questions (for the lab)

- Persistence: swap in-memory store for SQLite/Postgres?
- Auth: do todos belong to a user? (currently global)
- Tags / due dates / priority — candidate features to build with the agent team.
