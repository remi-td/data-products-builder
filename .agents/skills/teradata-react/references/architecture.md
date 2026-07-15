# Architecture

## Shape

```
┌──────────────────────┐   HTTPS/JSON   ┌──────────────────────┐   teradatasql   ┌────────────┐
│  React SPA (Vite)    │ ─────────────▶ │  FastAPI backend     │ ─────────────▶  │  Teradata  │
│  TS · Tailwind ·     │                │  teradatasqlalchemy  │                 │  Vantage   │
│  React Query · Router│ ◀───────────── │  Pydantic responses  │ ◀─────────────  │            │
└──────────────────────┘                └──────────────────────┘                 └────────────┘
        static hosting                       container / VM                          existing
        (any CDN, GH Pages)                  (Docker, ECS, k8s)                      cluster
```

**Two clean halves, one API contract.** The frontend never talks SQL.
The backend never serves HTML. Each can be replaced independently.

## Components

### Backend (`backend/app/`)

| Module        | Role                                                       |
|---------------|------------------------------------------------------------|
| `main.py`     | FastAPI app, CORS, router registration                     |
| `settings.py` | Pydantic Settings, reads `.env` (host, user, secret, etc.) |
| `db/engine.py`| SQLAlchemy engine singleton + pool config                  |
| `db/session.py`| `get_db` FastAPI dependency yielding a session            |
| `queries/`    | One file per logical query — pure SQLAlchemy/text          |
| `routers/`    | One file per resource — thin HTTP layer over `queries/`    |
| `schemas.py`  | Pydantic response models                                   |
| `cache.py`    | In-process TTL cache (or Redis) for hot queries            |

**Rule:** routers are thin (≤20 lines). Logic lives in `queries/`. This
keeps SQL reviewable in isolation and makes the backend trivially
testable without HTTP.

### Frontend (`frontend/src/`)

| Folder         | Role                                                      |
|----------------|-----------------------------------------------------------|
| `lib/api.ts`   | Typed fetch wrapper, base URL from `VITE_API_URL`         |
| `lib/queries.ts`| React Query hooks — one per backend endpoint             |
| `components/`  | Reusable UI (Card, DataTable, ChartCard, KPI, ...)        |
| `pages/`       | One file per route, composes components + hooks           |
| `theme/`       | Tailwind config, brand tokens, optional user stylesheet   |
| `App.tsx`      | Router + layout shell (sidebar/topbar)                    |

**Rule:** pages never call `fetch` directly. They consume hooks from
`lib/queries.ts`. This centralizes caching, retries, and error handling.

## Data flow (one round trip)

1. User opens `/tables`.
2. `pages/Tables.tsx` calls `useTablesByDatabase(filter)`.
3. Hook `GET /api/tables?database=DBC` (cached 60s in React Query).
4. Router `routers/tables.py` calls `queries.tables.list_by_database(db, ...)`.
5. Query runs parameterized SQLAlchemy `text(...)` on a pooled connection.
6. Response: Pydantic-validated JSON.
7. React renders with skeleton → data → optional error boundary.

## Cross-cutting principles

- **Never inline SQL in routers.** It hides the schema and breaks tests.
- **All SQL is parameterized.** No f-strings, no `+` concatenation. See
  `security.md`.
- **Engine is a process-wide singleton** with a sized pool. See
  `best-practices-backend.md` → "Connection pooling".
- **Read-only by default.** The backend exposes a read-only role unless
  the app explicitly needs writes; then a separate write-scoped router.
- **Cache aggressively at the edge.** TTL on the server, `staleTime` on
  the client. Teradata round-trips dominate latency.
- **Pagination is required** for any endpoint that could return >1k rows.
- **The frontend can run standalone** against the deployed API (GitHub
  Pages + Cloud Run for example). Don't couple build and deploy.

## Deployment topologies

The skill supports three, and they share the same source tree:

1. **Local dev** — `uvicorn` + `vite` with `VITE_API_URL=http://localhost:8000`.
2. **Docker compose** — `frontend` + `backend` + optional `nginx`.
3. **Static + remote API** — `npm run build` → GitHub Pages / Netlify /
   S3 + CloudFront; backend on Cloud Run / Fly / ECS / on-prem.

The `.env.example` and `templates/deploy/` cover all three with minimal
divergence.
