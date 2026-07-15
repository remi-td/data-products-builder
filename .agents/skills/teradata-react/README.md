# teradata-react

A Claude skill for scaffolding production-shaped **React + FastAPI** data
applications backed by **Teradata Vantage**. Turns "static Claude-generated
webpages" into "applications running against live data" — without the
ceilings of notebook frameworks.

## Contents

```
SKILL.md                       — skill entry point (what the agent reads first)
references/
  architecture.md              — system shape
  design-guidelines.md         — project layout, naming, definition of done
  best-practices-backend.md    — FastAPI + teradatasqlalchemy patterns
  best-practices-frontend.md   — React + Vite + React Query patterns
  security.md                  — SQL safety, secrets, CORS, auth, rate limit
  styling.md                   — theming, brand tokens, customer overrides
  prior-art.md                 — why this stack vs. Streamlit/Dash/Retool/...
  naming.md                    — why the skill is called "teradata-react"
templates/
  backend/                     — FastAPI skeleton (engine, sessions, queries, routers)
  frontend/                    — Vite + React + TS + Tailwind + React Query skeleton
  deploy/                      — Dockerfiles, docker-compose, GH Pages workflow
  README.template.md           — project README boilerplate
demo/
  backend/  frontend/  deploy/ — runnable multi-page dashboard over dbc.* views
  README.md                    — how to run the demo
assets/                        — Teradata brand assets
```

## Quick start (using the skill)

1. The agent reads [SKILL.md](SKILL.md), then the references it points to.
2. It asks scoping questions (data, pages, branding, deploy, auth).
3. It copies `templates/{backend,frontend,deploy}/` into the target project.
4. It adds features following the feature loop in `SKILL.md` § Step 4.
5. It hands the user a runnable app + `README.md`.

## See it in action

The [demo/](demo/) directory contains a runnable 6-page dashboard over
`dbc.*` system views using Teradata branding. It serves as both
acceptance criteria for the skill ("what does done look like") and a
reference implementation for agents to copy patterns from.

## Stack at a glance

| Layer        | Choice                                                              |
|--------------|---------------------------------------------------------------------|
| Frontend     | React 18 · Vite · TypeScript · Tailwind · React Query · Recharts    |
| Backend      | FastAPI · SQLAlchemy 2 · `teradatasqlalchemy` · Pydantic v2         |
| Database     | Teradata Vantage (any version supported by teradatasqlalchemy)      |
| Deploy       | Docker compose · Static (GH Pages) + remote API · Local dev         |

## Design principles (selected)

- All SQL is parameterized — `text(":name")`, never f-strings.
- Engine is a process-wide singleton with `pool_pre_ping=True`.
- Routers are thin; logic lives in `app/queries/`.
- Pages never call `fetch`; they consume React Query hooks.
- Brand is tokens (CSS variables), not hex codes scattered in JSX.
- Every data view handles loading · error · empty · success.

Full list in [references/design-guidelines.md](references/design-guidelines.md).
