# Notebook format — what the Teradata SQL kernel expects

A Teradata SQL notebook is a standard Jupyter `.ipynb` file (JSON) with a specific kernel spec. When in doubt, **use `scripts/build_notebook.py` to emit this structure** rather than hand-writing it.

## Kernel metadata (required)

Every Teradata SQL notebook must have:

```json
"metadata": {
  "kernelspec": {
    "display_name": "Teradata SQL",
    "language": "Teradata SQL",
    "name": "teradatasql"
  },
  "language_info": {
    "codemirror_mode": "Teradata SQL",
    "file_extension": ".tdrs",
    "mimetype": "application/vnd.teradata.resultset",
    "name": "Teradata SQL",
    "nbconvert_exporter": "",
    "pygments_lexer": "",
    "version": "16.20"
  }
}
```

`nbformat` must be `4`. `nbformat_minor` is `5` in current Teradata sample notebooks.

## Cell shapes

### Markdown cell

```json
{
  "cell_type": "markdown",
  "metadata": {},
  "source": ["Multi-line\n", "markdown goes here.\n"]
}
```

`source` may be a list of strings (Jupyter convention) or a single string — both load. The builder script produces the list form.

### Teradata SQL / magic cell

```json
{
  "cell_type": "code",
  "execution_count": null,
  "metadata": {
    "vscode": {
      "languageId": "teradata sql"
    }
  },
  "outputs": [],
  "source": ["%connect prod\n"]
}
```

Notes:
- `outputs` is `[]` for a freshly authored notebook. Execution fills it in.
- `execution_count` is `null` until the cell runs.
- The `vscode.languageId` metadata is what the sample Teradata notebooks carry. It is a hint for VS Code; the Teradata kernel ignores it but the Teradata sample notebooks ship with it, so the builder preserves that convention.
- There is no separate "magic" cell type — magics (`%connect`, `%var`, etc.) go directly in code cells alongside SQL. A single code cell should contain either one magic or one SQL statement (or one SQL batch terminated with `;`), not a mix — mixing makes result-set tracking and `%chart` reuse harder.

## Full minimal example

```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": ["# Hello, Teradata\n"]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {"vscode": {"languageId": "teradata sql"}},
      "outputs": [],
      "source": ["SELECT 1;"]
    }
  ],
  "metadata": {
    "kernelspec": {"display_name": "Teradata SQL", "language": "Teradata SQL", "name": "teradatasql"},
    "language_info": {
      "codemirror_mode": "Teradata SQL",
      "file_extension": ".tdrs",
      "mimetype": "application/vnd.teradata.resultset",
      "name": "Teradata SQL",
      "nbconvert_exporter": "",
      "pygments_lexer": "",
      "version": "16.20"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
```

## Common mistakes

- Wrong kernel name (`sql`, `sqlite`, `python3`). It **must** be `teradatasql`, or JupyterLab won't pick the Teradata kernel.
- Missing `language_info.mimetype`. Teradata result sets won't render.
- Using `"cell_type": "raw"`. The Teradata kernel doesn't treat raw cells specially — always use `markdown` or `code`.
- Putting magics in markdown cells. Magics only run in code cells.
