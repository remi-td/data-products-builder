# Teradata React — Demo App

A small multi-page dashboard built with this skill's templates. It runs
against any Teradata Vantage cluster — the demo reads only `dbc.*`
system views, which every Teradata user can SELECT against.

## Pages

| Route        | What it shows                                            | Endpoint                     |
|--------------|----------------------------------------------------------|------------------------------|
| `/`          | KPIs (DB/table/user counts, total perm) + top-10 bar chart| `GET /api/overview`, `/api/space/by-database` |
| `/databases` | Top 200 databases by allocated perm, with spool/temp     | `GET /api/databases`         |
| `/tables`    | Tables/views in a chosen database, with name filter      | `GET /api/tables?database=…` |
| `/users`     | Recently created users                                    | `GET /api/users`             |
| `/space`     | Current vs. max perm per database (chart + table)         | `GET /api/space/by-database` |
| `/health`    | Liveness check                                            | `GET /api/health`            |

## Run it

### Local dev

```bash
cp backend/.env.example backend/.env
# edit backend/.env — fill TD_HOST, TD_USER, TD_PASSWORD

# terminal 1
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# terminal 2
cd frontend
npm install
npm run dev          # http://localhost:5173
```

### Docker

```bash
cp backend/.env.example backend/.env   # then fill credentials
docker compose -f deploy/docker-compose.yml up --build
# http://localhost:8080
```

## What this demo demonstrates

- **Project layout** — backend / frontend / deploy split matches
  `templates/`.
- **Patterns** — every page handles loading/error/empty/success via
  `StateGate`; every chart wraps Recharts in `ChartCard`; every fetch
  flows through React Query hooks in `lib/queries.ts`.
- **Branding** — Teradata orange (`#FF5F02`) and navy (`#00233C`)
  applied via CSS variables; Inter font; official logo PNG in the
  sidebar. Swap `theme/brand.css` to re-skin for a customer.
- **Safety** — all SQL parameterized; engine singleton with pool
  pre-ping; read-only access pattern (no writes).
- **Performance** — server-side TTL cache on read-mostly endpoints
  (`overview`, `databases`, `users`, `space`); React Query 60s
  staleTime on the client; chart data trimmed server-side.

## Required permissions

The demo's read-only user needs:

```sql
GRANT SELECT ON dbc.DatabasesV TO td_react_demo;
GRANT SELECT ON dbc.TablesV    TO td_react_demo;
GRANT SELECT ON dbc.UsersV     TO td_react_demo;
GRANT SELECT ON dbc.DiskSpaceV TO td_react_demo;
```

Many Teradata sites grant these by default to all users.
