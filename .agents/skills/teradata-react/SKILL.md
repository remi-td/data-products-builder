---
name: teradata-react
description: Scaffold, develop, and deploy a production-shaped React + FastAPI web application backed by Teradata Vantage. Use whenever the user wants to turn data, schemas, or queries into a live, multi-page web app (not a static page or a notebook). Covers project layout, connection pooling, query patterns, theming/branding, security, and Docker / static / local deployment.
user-invocable: true
argument-hint: [project name or feature description]
---

# Teradata React — Full-Stack Data App Skill

You help the user build a **live data application** against Teradata
Vantage using an opinionated React + FastAPI stack. Your job is to
deliver production-shaped output as fast as a notebook framework, by
following the patterns in this skill.

## When to use

- "Build me a web app for these tables / this query."
- "Turn this dashboard sketch into a real app."
- "Add a page that shows X from Teradata."
- "Containerize / deploy this analytic app."
- "Apply our brand to this React+Teradata app."

If the user just wants a single static page with mocked data, this is
overkill — write plain HTML/JS instead.

## Agent Quickstart Checklist

Run through this before writing any code:

1. **Inspect workspace** — does a project directory already exist? What files are already there?
2. **Choose scaffold mode** — see [Scaffold Mode](#scaffold-mode) below.
3. **Resolve DB connection** — in order of preference:
   - Check for a `DATABASE_URI` env var in the shell (`echo $DATABASE_URI`)
   - If using `tq`, run `tq profiles` and prefer an existing working profile
   - Only ask the user for credentials if neither of the above exist
4. **Copy scaffold & populate `.env`** — never start writing feature code without a working connection confirmed.
5. **Run typecheck immediately** after scaffolding: `cd frontend && npx tsc --noEmit`
6. **Verify ports are free** before starting: `lsof -ti :8000 -ti :5173` must return empty (or override with `BACKEND_PORT`/`FRONTEND_PORT`)
7. **Confirm backend health** before testing other endpoints: `curl http://localhost:$BACKEND_PORT/api/health`

## Scaffold Mode

Choose **before** copying any files:

| Request type | Use |
|---|---|
| "dashboard", "analytics", "interactive", "visually compelling" | **Dashboard** — copy `demo/` structure (has `ChartCard`, `Kpi`, `Sidebar`, multi-page layout) |
| "app", "viewer", "CRUD", simple/unspecified | **Minimal** — copy `templates/` (bare working skeleton) |

For a dashboard scaffold: copy `demo/frontend/src/components/` and `demo/frontend/src/pages/` as your starting point, then replace the `dbc.*` queries with your domain data.

## Step 1 — Load references

Before writing any code, read:

1. [references/architecture.md](references/architecture.md) — the shape
   you'll produce.
2. [references/design-guidelines.md](references/design-guidelines.md) —
   project layout, naming, definition of done, anti-patterns.

When you act in a specific area, load the matching deep-dive:

| Task                                          | Read first                                              |
|-----------------------------------------------|---------------------------------------------------------|
| Writing/reviewing backend code                | [references/best-practices-backend.md](references/best-practices-backend.md) |
| Writing/reviewing frontend code               | [references/best-practices-frontend.md](references/best-practices-frontend.md) |
| Auth, secrets, SQL injection review, hardening| [references/security.md](references/security.md)        |
| Applying a customer brand or stylesheet       | [references/styling.md](references/styling.md)          |
| Justifying tech choice vs. Streamlit/Dash/etc.| [references/prior-art.md](references/prior-art.md)      |

## Step 2 — Confirm scope

Ask the user (one message, multiple choice when possible):

1. **Data**: which tables/views/queries should the app expose?
2. **Pages**: how many views, and what does each show?
3. **Branding**: Teradata default, customer stylesheet, or guidelines doc?
4. **Deployment**: local dev only, Docker, or static + remote API?
5. **Auth**: none (sandbox), reverse-proxy, or JWT?

Default to Teradata branding + Docker if the user is unsure.

## Step 3 — Scaffold

Copy the relevant pieces from [templates/](templates/) into the target
directory:

```
templates/backend/   → <project>/backend/
templates/frontend/  → <project>/frontend/
templates/deploy/    → <project>/deploy/
templates/start.sh   → <project>/start.sh   (chmod +x)
```

Then customize:

- `backend/app/settings.py` — confirm env-var names.
- `backend/.env.example` — copy to `.env`, fill credentials. Check for a
  `DATABASE_URI` env var first (see backend best practices); otherwise use
  `CHANGE_ME` placeholders and ask the user — never guess passwords.
- `start.sh` — adjust `BACKEND_PORT` / `FRONTEND_PORT` if the project uses
  non-default ports (e.g., multiple apps on the same machine).
- `frontend/src/theme/brand.css` — apply branding per
  [references/styling.md](references/styling.md).
- `README.md` — write a project-specific one (use
  [templates/README.template.md](templates/README.template.md)).

## Step 4 — Add features one at a time

For each user-requested view, follow this loop:

1. Write the SQL in `backend/app/queries/<resource>.py` as a
   `text("...")` constant + a pure function.
2. Add a Pydantic response model in `backend/app/schemas.py`.
3. Add a thin router in `backend/app/routers/<resource>.py` and
   register it in `main.py`.
4. Add a typed React Query hook in `frontend/src/lib/queries.ts`.
5. Add a page in `frontend/src/pages/<Resource>.tsx`, composed from
   `PageShell`, `DataTable` / `ChartCard`, and the hook.
6. Wire the route in `App.tsx` and add a sidebar link.
7. Smoke test: `uvicorn` + `npm run dev`, open the page, confirm all
   four states (loading / empty / error / success).

Every feature meets the Definition of Done in
[references/design-guidelines.md](references/design-guidelines.md#definition-of-done-per-feature).

## Step 5 — Deploy

Pick the target topology and follow
[templates/deploy/README.md](templates/deploy/README.md):

- **Local dev** — already running from Step 4.
- **Docker** — `docker compose up --build` from `deploy/`.
- **Static + remote API** — `npm run build` → push to GH Pages via the
  included Action; backend container deployed separately.

## Hard rules (apply on every edit)

- **All SQL is parameterized**. Never `f""`, `.format()`, or `+`.
- **Engine is a singleton** with `pool_pre_ping=True` and
  `pool_recycle=1800`. Never instantiate per-request.
- **Routers are thin** (≤20 lines). Logic lives in `queries/`.
- **Pages don't call `fetch`** — they consume hooks from
  `lib/queries.ts`.
- **No hex codes in JSX/CSS** — use Tailwind tokens from `brand.css`.
- **Every chart uses `ChartCard`**. Every data view handles four states.
- **Sync DB calls → sync route functions**. `teradatasqlalchemy` is
  not async.
- **Read-only DB user** unless writes are explicitly required.

If you find yourself wanting to break a rule, stop and re-read the
relevant reference. The rule almost always wins.

## Demo

A working multi-page demo over `dbc.*` views with Teradata branding is
in [demo/](demo/). Use it to:
- show the user what "done" looks like;
- copy patterns when you're unsure how to structure something;
- benchmark performance budgets against a real Teradata.

Run it locally:

```bash
cd demo
cp backend/.env.example backend/.env  # then fill TD_HOST/TD_USER/TD_PASSWORD
docker compose -f deploy/docker-compose.yml up --build
# or, dev mode:
(cd backend && uvicorn app.main:app --reload) &
(cd frontend && npm install && npm run dev)
```
