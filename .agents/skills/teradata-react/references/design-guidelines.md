# Design Guidelines & Standards

This is the contract every app produced by this skill follows. Treat
items as **must** unless marked *should*.

## Project layout

```
my-app/
├── backend/
│   ├── app/
│   │   ├── main.py                FastAPI app + CORS + router mount
│   │   ├── settings.py            Pydantic settings (.env)
│   │   ├── schemas.py             Pydantic response models
│   │   ├── cache.py               TTL cache helpers
│   │   ├── db/
│   │   │   ├── engine.py          singleton engine + pool
│   │   │   └── session.py         get_db dependency
│   │   ├── queries/               one file per resource — pure SQL
│   │   └── routers/               one file per resource — thin HTTP
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── lib/{api,queries}.ts
│   │   ├── components/            reusable UI
│   │   ├── pages/                 one per route
│   │   ├── theme/brand.css        tokens
│   │   ├── App.tsx                router + shell
│   │   └── main.tsx               entry, theme imports
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── deploy/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── github-pages.yml           GH Actions for static deploy
├── start.sh                       single-command dev launcher (backend + frontend)
└── README.md
```

## Naming

- **Endpoints** are kebab-case plural under `/api/`: `/api/tables`,
  `/api/disk-space`, `/api/top-users`.
- **Query modules** match resource singular: `queries/table.py`,
  `queries/disk_space.py`.
- **React hooks** are `useThing()` returning `UseQueryResult`. Hook
  name encodes the endpoint, not the page that uses it:
  `useTablesByDatabase`, not `useTablesForTablesPage`.
- **Components** are PascalCase: `DataTable`, `ChartCard`, `PageShell`.
- **Pages** end in `Page` only if disambiguation needed; default is
  bare: `Tables.tsx`, `Users.tsx`.

## API contract

- All endpoints return JSON. Errors include `{ "detail": "..." }`.
- Status codes: 200 OK, 400 bad input, 404 not found, 422 validation,
  503 DB down. Never 500 with a stack trace to the client.
- Lists are returned as **JSON arrays**, not envelopes. Pagination uses
  query params + `Link`/`X-Next-Cursor` headers when needed.
- Timestamps are **ISO 8601 strings in UTC**. The frontend formats for
  display.

## Frontend rules

- Every page handles **loading, error, empty, success** states.
- Every fetch goes through a React Query hook in `lib/queries.ts`.
- Every chart goes through `ChartCard`.
- No raw hex in components — use tokens via Tailwind classes.
- No `any` in TypeScript. Response types declared next to hooks.

## Backend rules

- Routers are ≤20 lines. Logic in `queries/`.
- All SQL is in `text(...)` constants at module top, with `:named`
  params. Zero string concatenation.
- Engine created once, pooled, `pool_pre_ping=True`.
- Read-only DB user unless the app explicitly writes.
- Logs include query name, param keys, elapsed ms, row count.

## Performance budgets

| Metric                                  | Budget         |
|-----------------------------------------|----------------|
| Initial JS bundle (gzipped)             | < 200 KB       |
| Per-route chunk (gzipped)               | < 80 KB        |
| First chart visible on cached load      | < 1.5 s        |
| P95 backend latency (simple list query) | < 500 ms       |
| Pool size (default)                     | 5 + 5 overflow |

If budgets are exceeded, document why in the project README.

## Definition of done (per feature)

A feature is shippable when:
1. Backend query has a `text()` constant + parameterized call.
2. Pydantic response model exists in `schemas.py`.
3. Router is registered in `main.py`.
4. Frontend hook in `lib/queries.ts` with typed return.
5. Page renders loading / error / empty / success states.
6. Manual smoke: open the route in `npm run dev` against `uvicorn`.
7. README "Pages" table updated with the new route.

## Anti-patterns (reject in review)

- ❌ SQL built with f-strings.
- ❌ Hex codes in JSX.
- ❌ Routers that call SQLAlchemy directly.
- ❌ Pages with `fetch(...)` calls.
- ❌ `useEffect` for data fetching (use React Query).
- ❌ `async def` route + sync DB call.
- ❌ Inline Recharts without `ChartCard`.
- ❌ MUI/Chakra/Ant added alongside Tailwind.
- ❌ Engine created per-request.
- ❌ `uvicorn --app-dir` in launch scripts (changes `sys.path` but not CWD; `.env` won't load — use `(cd "$BACKEND" && uvicorn ...)` instead).
- ❌ Guessing credentials (password = username, password = project name). Check `DATABASE_URI` env var first; otherwise use `CHANGE_ME` placeholders and ask.
