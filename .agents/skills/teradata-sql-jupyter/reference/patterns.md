# Patterns — recipes for common notebook types

Guidance on how to *structure* a notebook for each use case. Start from the matching template in `templates/`, then adapt.

---

## Exploratory Data Analysis (EDA)

**Template:** `templates/eda.ipynb`

**Goal:** build understanding of an unfamiliar dataset and leave a durable record of what you learned.

Structure:

1. **Connection block** (standard).
2. **Target selection** — `%var schema=..., table=...`.
3. **Shape** — row count, `SELECT TOP 10`, column metadata from `DBC.ColumnsV`.
4. **Profile** — nulls, distinct counts, min/max/avg on numeric columns.
5. **Distributions** — grouped aggregates + `%chart` for each axis of interest.
6. **Findings** — a markdown cell with a bullet list of *"what we now know"* and *"open questions"*.

Do:
- Name result sets you'll revisit via `%table <id>` rather than re-running large queries.
- Keep SQL cells small — one query per cell — so `%chart` can re-use the most recent result set without surprise.
- End with a markdown summary. An EDA notebook is a report, not just a scratchpad.

Don't:
- Embed findings only in comments. Put conclusions in markdown so a reader can skim.
- Run `SELECT *` on a large table without a `TOP N`.

---

## Teaching a concept

**Template:** `templates/teaching.ipynb`

**Goal:** teach one concept well, with runnable examples the learner can modify.

Structure:

1. **Connection block.**
2. **Learning objectives** — 3 concrete bullets.
3. **Setup** — a tiny, hand-crafted table the reader can understand at a glance (≤ 10 rows).
4. **Concept, step by step** — each step is a markdown cell (the *why*) followed by one SQL cell (the *what*). Build complexity gradually.
5. **Try it yourself** — 2–3 editable challenges.
6. **Cleanup** — drop the demo table.

Do:
- Use a toy dataset. Real-world schemas distract from the concept being taught.
- Name tables with a `teach_` or `_demo` prefix so they're obviously disposable.
- Show one idea per cell. If a cell does three things, split it.

Don't:
- Reuse production tables for teaching. Cleanup is brittle and the learner may not have access.
- Over-narrate. A short sentence per step is usually enough when paired with a runnable example.

---

## Product / feature demo

**Template:** `templates/demo.ipynb`

**Goal:** a short, on-stage-friendly walkthrough that always works and finishes in ~5 minutes.

Structure:

1. **Connection block.**
2. **What this demo shows** — one paragraph.
3. **Setup** — create minimal objects. Include `DROP` first so reruns work.
4. **The "wow" cell** — the single most compelling query. Build everything around this.
5. **Variations** — 1–2 alternate angles to handle audience questions.
6. **Closing slide** — one-sentence takeaway and a link to next steps.
7. **Cleanup** — drop all demo objects.

Do:
- Rehearse it. Every cell should run successfully top-to-bottom.
- Make the `%chart` calls explicit about `mark=` and `title=` — on-screen visuals matter.
- Keep result sets small. Charts of 1M points are a distraction.

Don't:
- Depend on external data downloads mid-demo. Inline `INSERT` statements are fine for a demo.
- Use real customer names or credentials anywhere.

---

## Interactive user guide

**Template:** `templates/user-guide.ipynb`

**Goal:** a runnable reference that users read *and* execute to learn a feature.

Structure:

1. **Connection block.**
2. **How to use this guide** — tells the reader how to engage (run top-to-bottom first, then edit "Try it" cells).
3. **Prerequisites check** — cells that confirm the user has what they need (right role, database exists, feature enabled).
4. **Chapters** — one per sub-topic. Each chapter has: concept paragraph → basic example → "Try it" editable cell.
5. **Reference card** — copy-paste-ready snippets summarizing the syntax.
6. **Further reading** — links to docs and the community forum.

Do:
- Make "Try it" cells self-contained — they should run even if the reader skipped earlier chapters.
- Include a "reset" cell (drop/recreate teaching tables) so a reader can restart cleanly.

Don't:
- Chain dependencies across chapters without marking it. If Chapter 3 needs Chapter 2's table, say so in markdown.
- Hide the interesting SQL inside a stored procedure. The point is to teach SQL, not abstract it.

---

## Shared guidelines

- **Connections at the top.** Every notebook opens with `%var → %addconnect → %connect → DATABASE ${db}`.
- **Parameterize with `%var`.** If a value might change per reader, make it a variable.
- **Magics over hand-rolled SQL.** `%dataload`, `%chart`, `%table` exist for a reason.
- **Idempotent setup.** Include `DROP TABLE` before `CREATE`; add a comment that the first-run error is expected.
- **Cleanup at the bottom.** Demo and teaching notebooks should leave no residue.
- **No credentials in cells.** Use placeholders inside `%var`; let `%connect` prompt for passwords.
- **Results stay out of the file in templates.** Templates ship with empty `outputs`. Captured outputs from a real run are fine in delivered notebooks but make the file noisy in source control.
