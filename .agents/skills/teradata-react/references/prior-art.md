# Prior Art: Data Apps over Analytic Databases

This survey informs the architectural choices in `architecture.md`. Read it
when deciding *whether* the React-on-Teradata pattern fits the user's need,
or when comparing trade-offs.

## Categories of "data app" tooling

### 1. Pure-Python notebook-style frameworks
- **Streamlit** — Python script → reactive UI. Excellent prototyping;
  weaker for multi-user, custom layouts, branded UX, complex state.
- **Dash (Plotly)** — Flask + React under the hood; declarative callbacks.
  More flexible than Streamlit but its component model is Plotly-flavored.
- **Gradio** — ML demo-first; not a fit for analytic dashboards.
- **Panel / Voila** — niche; tied to the HoloViz / Jupyter stacks.

### 2. Low-code dashboarding (BI)
- **Tableau / Power BI / Looker / Superset / Metabase** — drag-drop
  dashboards. Strong for canonical analytics, weak for bespoke workflows,
  custom layouts, embedded apps, or anything beyond a chart grid.

### 3. SQL-first app frameworks
- **Evidence.dev** — SQL + markdown → static analytic site. Strong for
  reports; weak for interactive write-back or session-stateful apps.
- **Observable Framework** — similar: SQL + JS notebooks compiled to a
  static site.

### 4. Internal-tool builders
- **Retool / Appsmith / Tooljet** — drag-drop CRUD apps. Faster for forms
  over a DB; weaker for analytic visualizations and bespoke styling.

### 5. Full custom (this skill's territory)
- **React/Vue/Svelte + REST/GraphQL API + DB driver**.
  Maximum flexibility — production-grade UX, full branding control,
  embeddable, deployable anywhere. Higher floor of effort, which this
  skill exists to flatten.

## Why this skill?

A coding agent can scaffold a full custom stack in minutes, removing the
classic "build vs. low-code" trade-off:

| Need                        | Low-code (Streamlit/Retool) | This skill (React+FastAPI) |
|-----------------------------|-----------------------------|----------------------------|
| Bespoke layout / branding   | Limited                     | First-class                |
| Production hosting          | Constrained                 | Anywhere (static + API)    |
| Multi-page nav, deep links  | Awkward                     | Native (React Router)      |
| Heavy client interaction    | Re-runs whole script        | Component-local state      |
| Reusable component library  | Minimal                     | Tailwind + shadcn/Recharts |
| Embeddable in another app   | Painful                     | Standard `<iframe>`/SPA    |
| Time-to-first-chart by hand | Minutes                     | Hours                      |
| Time-to-first-chart by agent| Minutes                     | Minutes                    |

The asymmetry an agent erases is the bottom row. With templates and clear
patterns, an agent produces production-shaped output as fast as a
notebook framework — without inheriting their ceilings.

## What competitors get right (and we copy)

- **Streamlit**: instant feedback loop. We mirror this with `npm run dev`
  + `uvicorn --reload`.
- **Evidence.dev**: SQL lives next to the chart. We keep each query in a
  named module under `backend/app/queries/` and reference it from the
  frontend by endpoint name.
- **Retool**: opinionated table/form components. We standardize on shadcn
  + Recharts so agents don't reinvent.
- **Superset**: cached query results. We use FastAPI response caching +
  React Query staleTime.
