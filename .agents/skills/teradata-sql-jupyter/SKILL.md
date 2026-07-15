---
name: teradata-sql-jupyter
description: Use when the task involves authoring, modifying, or running Teradata SQL Jupyter notebooks (.ipynb with the `teradatasql` kernel) — including exploratory data analysis, teaching database concepts, product demos, interactive SQL user guides, or helping a user install / configure the Teradata Jupyter SQL extensions.
---

You are authoring a Teradata SQL Jupyter notebook (or helping a user install the extensions that run one). These notebooks use the **Teradata SQL Kernel** (`kernelspec.name = "teradatasql"`), which accepts SQL statements directly and a rich set of `%magic` commands (`%connect`, `%var`, `%chart`, `%dataload`, `%history`, `%table`, …).

## When to use this skill

- The user asks for a Teradata notebook, EDA notebook against Vantage, SQL demo, or interactive tutorial.
- The user wants to teach / document a Teradata feature with runnable SQL cells.
- The user wants help installing, configuring, or launching the Teradata Jupyter SQL extensions.
- The user wants to convert an existing analysis, markdown doc, or plain SQL script into a `.ipynb` with the Teradata SQL kernel.

## How to produce a notebook

**Do not hand-write notebook JSON.** Use the helper script — it guarantees a valid kernel spec and cell structure:

```bash
python3 scripts/build_notebook.py --out path/to/notebook.ipynb --spec path/to/spec.json
```

Two ways to drive it:

1. **Copy a template** from `templates/` that matches the use case, then edit cell sources with the `Edit` tool. Templates available:
   - `templates/eda.ipynb` — exploratory data analysis skeleton
   - `templates/teaching.ipynb` — concept-teaching skeleton with explainer markdown between SQL cells
   - `templates/demo.ipynb` — product/feature demo with setup → show → teardown
   - `templates/user-guide.ipynb` — interactive runnable user guide

2. **Build from scratch** with `scripts/build_notebook.py`. Write a small JSON spec listing cells in order, each `{"type": "md" | "sql", "source": "..."}`, and run the script. See the script docstring for the exact schema.

## Authoring rules (important)

1. **Start every notebook with a connection block.** Use `%var` to parameterize system/user/host/db, then `%addconnect` and `%connect`. Use `${var}` substitution elsewhere. See `reference/magics.md` for exact syntax.
2. **Alternate markdown and SQL cells** — a short markdown cell explaining *why*, followed by a SQL/magic cell. For teaching and user guides, keep each SQL cell focused on one concept.
3. **Prefer magics over ad-hoc SQL** when a magic exists: `%dataload` for CSV ingest, `%chart` for visualization, `%table <id>` to re-display a past result set. Never hand-code chart rendering.
4. **Make notebooks idempotent** when they create objects: wrap with `DROP TABLE` (acknowledge it errors the first run) or `DROP TABLE IF EXISTS` where supported, and include a teardown section at the end.
5. **Do not embed credentials.** Leave `<placeholders>` inside `%var` and instruct the user to replace them, or use a `%addconnect` that prompts.
6. **Kernel metadata must be exact.** `name: "teradatasql"`, `display_name: "Teradata SQL"`, `language: "Teradata SQL"`. The builder script sets this correctly.

## Progressive references

Load these only when needed — they are not required upfront:

- `reference/magics.md` — complete magic command reference (connections, variables, data load, history, chart, help, snippets)
- `reference/notebook-format.md` — the exact JSON shape the Teradata SQL kernel expects
- `reference/connections.md` — connection parameters, auth mechanisms (TD2, LDAP, KRB5, BROWSER, TDNEGO), SSL modes
- `reference/patterns.md` — recipes for EDA / teaching / demo / user-guide notebooks
- `reference/installation.md` — install the SQL kernel + JupyterLab extensions, Docker image path, first-run checks

## When the user wants to install / run the extensions

Go to `reference/installation.md`. It covers the two supported paths (Docker image vs. pip install into an existing JupyterLab), the post-install verification steps, and the most common failure modes (kernel not showing up, Navigator sidebar missing, connection manager empty).

## Executing cells

This skill authors notebooks; it does not execute them. If the user wants to *run* cells, tell them to open the `.ipynb` in JupyterLab with the Teradata extensions installed, or (for a headless test) run:

```bash
jupyter nbconvert --to notebook --execute path/to/notebook.ipynb --ExecutePreprocessor.kernel_name=teradatasql
```

This requires an active Teradata connection defined in the user's environment.
