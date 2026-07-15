#!/usr/bin/env python3
"""Generate the four starter templates shipped with this skill.

Run from the skill root:
    python3 scripts/_build_templates.py
"""

from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_notebook import build_notebook, md, sql  # noqa: E402

TEMPLATES = HERE.parent / "templates"


def connection_block(title: str) -> list[dict]:
    """Standard opening block: title, connection parameters, connect."""
    return [
        md(f"# {title}\n\n"
           "This notebook uses the **Teradata SQL Kernel**. Execute cells with **Shift+Enter**.\n"),
        md("## 1. Configure your connection\n\n"
           "Replace the placeholders below with your Teradata Vantage system details, then run the cells in order."),
        sql("%var systemName=<Vantage-system>, user=<user-name>, host=<host-or-IP>, db=<database>"),
        sql("%addconnect name=${systemName}, user=${user}, host=${host}"),
        sql("%connect ${systemName}"),
        sql("DATABASE ${db};"),
    ]


def teardown_block(tables: list[str]) -> list[dict]:
    drops = "\n".join(f"DROP TABLE {t};" for t in tables)
    return [
        md("## Cleanup\n\nDrop any demo tables created above. These statements error if the table doesn't exist — that's expected."),
        sql(drops),
    ]


def build_eda():
    cells = connection_block("Exploratory Data Analysis — Teradata Vantage")
    cells += [
        md("## 2. Pick a table to explore\n\nSet `${schema}` and `${table}` to the object you want to investigate."),
        sql("%var schema=<schema>, table=<table>"),
        md("### Row count & sample\n\nStart by getting a feel for size and shape."),
        sql("SELECT COUNT(*) AS row_count FROM ${schema}.${table};"),
        sql("SELECT TOP 10 * FROM ${schema}.${table};"),
        md("### Column types\n\nPull the column metadata from DBC."),
        sql("SELECT ColumnName, ColumnType, ColumnLength, Nullable\n"
            "FROM DBC.ColumnsV\n"
            "WHERE DatabaseName = '${schema}' AND TableName = '${table}'\n"
            "ORDER BY ColumnId;"),
        md("### Null & distinct profile\n\nEdit the column list to match columns of interest."),
        sql("SELECT\n"
            "  COUNT(*)                                AS rows_total,\n"
            "  COUNT(DISTINCT <col1>)                  AS distinct_col1,\n"
            "  SUM(CASE WHEN <col1> IS NULL THEN 1 ELSE 0 END) AS nulls_col1\n"
            "FROM ${schema}.${table};"),
        md("### Distribution\n\nReplace `<dimension>` and `<measure>` with appropriate columns, then visualize with `%chart`."),
        sql("SELECT <dimension>, SUM(<measure>) AS total_measure\n"
            "FROM ${schema}.${table}\n"
            "GROUP BY <dimension>\n"
            "ORDER BY total_measure DESC;"),
        sql("%chart <dimension>, total_measure, title=Distribution by dimension"),
        md("### Save next-step questions\n\nUse this markdown cell to record hypotheses to follow up on — this is what makes an EDA notebook durable."),
        md("- [ ] Hypothesis 1: ...\n- [ ] Hypothesis 2: ...\n- [ ] Hypothesis 3: ..."),
    ]
    build_notebook(cells, TEMPLATES / "eda.ipynb")


def build_teaching():
    cells = connection_block("Teaching: <concept> in Teradata")
    cells += [
        md("## 2. What you'll learn\n\n"
           "By the end of this notebook you will:\n"
           "- Understand **what** `<concept>` is and **why** it matters on Teradata.\n"
           "- Recognize when to use it vs. alternatives.\n"
           "- Be able to modify and re-run the examples below.\n"),
        md("## 3. Setup: create a small teaching dataset\n\n"
           "We use a tiny table so you can focus on the concept, not the data."),
        sql("DROP TABLE teach_demo;"),
        sql("CREATE MULTISET TABLE teach_demo (\n"
            "  id     INTEGER NOT NULL,\n"
            "  region VARCHAR(20),\n"
            "  amount DECIMAL(10,2)\n"
            ") NO PRIMARY INDEX;"),
        sql("INSERT INTO teach_demo VALUES (1, 'North',  120.00);\n"
            "INSERT INTO teach_demo VALUES (2, 'North',   80.00);\n"
            "INSERT INTO teach_demo VALUES (3, 'South',  200.00);\n"
            "INSERT INTO teach_demo VALUES (4, 'South',   50.00);\n"
            "INSERT INTO teach_demo VALUES (5, 'East',   300.00);"),
        md("## 4. The concept, step by step\n\n"
           "### Step 1 — <first idea>\n\n"
           "Explain the first idea in one short paragraph. Then show it:"),
        sql("-- demonstrate the first idea\nSELECT * FROM teach_demo ORDER BY id;"),
        md("### Step 2 — <second idea>\n\n"
           "Build on step 1. Point out what changed and *why*."),
        sql("-- demonstrate the second idea\nSELECT region, SUM(amount) AS total FROM teach_demo GROUP BY region ORDER BY total DESC;"),
        md("### Step 3 — visualize\n\nUse `%chart` to make the result intuitive."),
        sql("%chart region, total, title=Totals by region"),
        md("## 5. Try it yourself\n\nEdit the cell below and re-run. Suggested exercises:\n"
           "1. Add a `HAVING` clause to filter regions with totals above 150.\n"
           "2. Switch the chart `mark=point` or `mark=line`.\n"
           "3. Add a new row with `INSERT` and observe how the aggregate shifts."),
        sql("-- your turn\nSELECT region, SUM(amount) AS total\nFROM teach_demo\nGROUP BY region;"),
    ]
    cells += teardown_block(["teach_demo"])
    build_notebook(cells, TEMPLATES / "teaching.ipynb")


def build_demo():
    cells = connection_block("Demo: <feature name>")
    cells += [
        md("## 2. What this demo shows\n\n"
           "A short, on-stage friendly demonstration of **<feature>**. Total runtime should stay under ~5 minutes of cell execution."),
        md("## 3. Setup\n\nCreate the minimal objects needed for the demo."),
        sql("DROP TABLE demo_sales;"),
        sql("CREATE MULTISET TABLE demo_sales (\n"
            "  store_id INTEGER,\n"
            "  sale_dt  DATE,\n"
            "  amount   DECIMAL(10,2)\n"
            ") NO PRIMARY INDEX;"),
        sql("INSERT INTO demo_sales VALUES (1, DATE '2025-01-01', 120.00);\n"
            "INSERT INTO demo_sales VALUES (1, DATE '2025-01-02',  80.00);\n"
            "INSERT INTO demo_sales VALUES (2, DATE '2025-01-01', 200.00);\n"
            "INSERT INTO demo_sales VALUES (2, DATE '2025-01-02', 150.00);\n"
            "INSERT INTO demo_sales VALUES (3, DATE '2025-01-01',  90.00);"),
        md("## 4. The 'wow' moment\n\nShow the single most compelling query. Keep it short — this is the screenshot-worthy cell."),
        sql("SELECT store_id, SUM(amount) AS total_sales\n"
            "FROM demo_sales\n"
            "GROUP BY store_id\n"
            "ORDER BY total_sales DESC;"),
        sql("%chart store_id, total_sales, title=Total Sales by Store, mark=bar"),
        md("## 5. Variation — different angle\n\nSame data, different lens — useful for answering 'what about X?' from the audience."),
        sql("SELECT sale_dt, SUM(amount) AS daily_sales\n"
            "FROM demo_sales\n"
            "GROUP BY sale_dt\n"
            "ORDER BY sale_dt;"),
        sql("%chart sale_dt, daily_sales, title=Sales by Day, mark=line, typex=t"),
        md("## 6. Closing slide\n\nOne-sentence takeaway. Link to next steps:\n"
           "- Docs: https://docs.teradata.com/\n"
           "- Try the `eda.ipynb` template to go deeper on your own data."),
    ]
    cells += teardown_block(["demo_sales"])
    build_notebook(cells, TEMPLATES / "demo.ipynb")


def build_user_guide():
    cells = connection_block("<Feature> — Interactive User Guide")
    cells += [
        md("## 2. How to use this guide\n\n"
           "- Each section has a short explanation followed by a runnable SQL cell.\n"
           "- Run cells top-to-bottom the first time through.\n"
           "- The 'Try it' cells are meant to be edited — change values and re-run."),
        md("## 3. Before you start\n\nMake sure your connected user has permission to create tables in `${db}`."),
        sql("SELECT CURRENT_USER, DATABASE;"),
        md("## 4. Chapter 1 — <topic>\n\n"
           "Explain the first chapter's concept in 2–3 sentences. State the problem it solves."),
        md("### 4.1 Basic usage"),
        sql("-- minimal working example\nSELECT 1 AS hello_world;"),
        md("### 4.2 Try it yourself\n\nEdit the literal below, then re-run."),
        sql("-- edit me\nSELECT '<your-value-here>' AS my_value;"),
        md("## 5. Chapter 2 — <topic>\n\nBuild on chapter 1."),
        sql("-- chapter 2 example"),
        md("## 6. Reference card\n\nA copy-paste-friendly summary of the syntax covered above.\n\n"
           "```sql\n-- paste-ready snippets\n```"),
        md("## 7. Further reading\n\n- Teradata docs: https://docs.teradata.com/\n- Community: https://community.teradata.com/"),
    ]
    build_notebook(cells, TEMPLATES / "user-guide.ipynb")


def main() -> int:
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    build_eda()
    build_teaching()
    build_demo()
    build_user_guide()
    print(f"Templates written to {TEMPLATES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
