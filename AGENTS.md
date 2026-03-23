# AGENTS.md

This file provides guidance to AI coding agents working with code in this repository.

## What This Is

This agentic system automates the creation of AI-Native Data Products on Teradata. It uses design standards as the single source of truth and agentic prompts to orchestrate multi-module data product design and deployment.

## Architecture

**Six-module architecture** — each data product is composed of independently deployable modules, each with its own Teradata database (`{ProductName}_{Module}`):

| Module | Database Pattern | Purpose |
|--------|-----------------|---------|
| Memory | `{Name}_Memory` | Agent state, learning, and design documentation (Documentation Sub-Module) |
| Semantic | `{Name}_Semantic` | Metadata layer enabling agent discovery — the "map" of the data product |
| Domain | `{Name}_Domain` | Core business entities — source of truth |
| Observability | `{Name}_Observability` | Event tracking, quality monitoring, lineage |
| Search | `{Name}_Search` | Vector embeddings and similarity search |
| Prediction | `{Name}_Prediction` | Feature store and ML prediction storage |

**Deployment order matters**: Phase 1 (Memory + Semantic) → Phase 2 (Domain + Observability) → Phase 3 (Search + Prediction). Memory and Semantic must exist before any other module deploys.

**Design standards (in `design-standards/design-standards/`) are the master source of truth.** The `design-standards/` directory is a git submodule; the actual `.md` files are one level deeper. Prompts and generated artifacts are derived from them — never edited independently. When conflicts arise, design standards win.

## Project Structure

```
AGENTS.md                            ← Framework-agnostic project instructions (this file)
.agents/prompts/                     ← Portable agentic prompts (tool-agnostic)
.agents/skills/                      ← Portable agentic skills (tool-agnostic)
design-standards/design-standards/   ← 8 design standard .md files (git submodule, nested path)
scripts/                             ← Deployment, sanitization, and tooling scripts
src/                                 ← Data product source code (per product, per module)
docs/                                ← Data product documentation and release notes
config/                              ← Connection configurations (gitignored credentials)
.claude/                             ← Claude Code specific config (thin wrappers, symlinks to .agents/skills/)
```

## Key Prompts

Reusable agentic prompts live in `.agents/prompts/`. These are tool-agnostic — each AI coding tool can consume them via its own integration mechanism.

- **data-product-build** — Orchestrates the full build process from requirements to deployment.
- **data-product-design** — Designs a data product module by applying design standards strictly.
- **teradata-sql** — Generates and validates Teradata SQL (DDL/DML).
- **teradata-query** — Executes Teradata queries via the tq CLI tool.
- **data-product-use** — Guides agents consuming an existing data product via Semantic discovery.

## Key Workflows

**Designing a new data product**: Use the `data-product-build` prompt — it follows a 7-deliverable sequence (requirements → logical model → module schemas → integration → deployment plan), stopping for review after each.

## Teradata SQL Conventions (from design standards)

- Boolean columns: `BYTEINT NOT NULL DEFAULT 1/0` with `is_` prefix — never `CHAR(1)`, never `= 'Y'`/`= 'N'`
- Surrogate keys: `BIGINT GENERATED ALWAYS AS IDENTITY`, named `{table}_key`
- Timestamps: `TIMESTAMP(6) WITH TIME ZONE`
- Temporal end date: `DATE '9999-12-31'`
- Table suffixes: `_H` (history), `_R` (reference), `_Current` (view), `_Enriched` (view)
- Temporal tables use non-unique `PRIMARY INDEX` — never `UNIQUE PRIMARY INDEX`
- `COMMENT ON TABLE` and `COMMENT ON COLUMN` required on all objects

## Project Rules

- Always present work for review before proceeding to the next step.
- Always use the data-product-build prompt to orchestrate the data product building process.
- Never modify the design standards unless explicitly authorized by the user.
- Use the design standards as the most authoritative source of truth to resolve conflicts.
