#!/usr/bin/env python3
"""Build a Teradata SQL Jupyter notebook (.ipynb) from a list of cells.

The Teradata SQL Kernel requires specific notebook metadata. This script
emits a notebook with the correct kernelspec so JupyterLab picks the
`teradatasql` kernel automatically.

Spec file format (JSON):

    {
      "cells": [
        {"type": "md",  "source": "# Title\n\nSome narrative."},
        {"type": "sql", "source": "%var db=mydb, t=mytable"},
        {"type": "sql", "source": "SELECT TOP 10 * FROM ${db}.${t};"}
      ]
    }

`source` may be a string or a list of strings (they will be joined).
`type` is one of: "md" (markdown) or "sql" (Teradata SQL code cell).

Usage:

    python3 build_notebook.py --spec spec.json --out notebook.ipynb
    python3 build_notebook.py --out notebook.ipynb < spec.json
    python3 build_notebook.py --out notebook.ipynb --stdin   # read JSON from stdin

You can also use this module programmatically:

    from build_notebook import build_notebook, md, sql
    build_notebook(
        [md("# Hello"), sql("SELECT 1;")],
        "out.ipynb",
    )
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable


KERNEL_METADATA = {
    "kernelspec": {
        "display_name": "Teradata SQL",
        "language": "Teradata SQL",
        "name": "teradatasql",
    },
    "language_info": {
        "codemirror_mode": "Teradata SQL",
        "file_extension": ".tdrs",
        "mimetype": "application/vnd.teradata.resultset",
        "name": "Teradata SQL",
        "nbconvert_exporter": "",
        "pygments_lexer": "",
        "version": "16.20",
    },
}


def _normalize_source(source) -> list[str]:
    """Accept a string or list-of-strings and return Jupyter-style source lines.

    Jupyter's convention is a list of strings, each ending in '\n' except the
    last. Passing a single string is more ergonomic for humans.
    """
    if isinstance(source, list):
        text = "".join(source)
    elif isinstance(source, str):
        text = source
    else:
        raise TypeError(f"cell source must be str or list[str], got {type(source)!r}")

    if not text:
        return []
    lines = text.splitlines(keepends=True)
    return lines


def md(source) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": _normalize_source(source),
    }


def sql(source) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"vscode": {"languageId": "teradata sql"}},
        "outputs": [],
        "source": _normalize_source(source),
    }


def _cell_from_spec(entry: dict) -> dict:
    t = entry.get("type")
    if t == "md":
        return md(entry["source"])
    if t == "sql":
        return sql(entry["source"])
    raise ValueError(f"unknown cell type: {t!r} (expected 'md' or 'sql')")


def build_notebook(cells: Iterable[dict], out_path: str | Path) -> Path:
    """Write a notebook to `out_path` and return the resolved path.

    `cells` is an iterable of cell dicts produced by `md(...)` / `sql(...)`
    or by `_cell_from_spec`.
    """
    notebook = {
        "cells": list(cells),
        "metadata": KERNEL_METADATA,
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = Path(out_path).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return out


def _load_spec(spec_path: str | None, from_stdin: bool) -> dict:
    if from_stdin or spec_path == "-":
        return json.load(sys.stdin)
    if not spec_path:
        if not sys.stdin.isatty():
            return json.load(sys.stdin)
        raise SystemExit("error: provide --spec PATH, or pipe JSON on stdin, or pass --stdin")
    with open(spec_path, encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("--spec", help="Path to a JSON spec file (or '-' for stdin).")
    p.add_argument("--stdin", action="store_true", help="Read the JSON spec from stdin.")
    p.add_argument("--out", required=True, help="Output .ipynb path.")
    args = p.parse_args(argv)

    spec = _load_spec(args.spec, args.stdin)
    if "cells" not in spec or not isinstance(spec["cells"], list):
        raise SystemExit("error: spec must contain a 'cells' list")

    cells = [_cell_from_spec(c) for c in spec["cells"]]
    out = build_notebook(cells, args.out)
    print(f"Wrote {out} ({len(cells)} cells)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
