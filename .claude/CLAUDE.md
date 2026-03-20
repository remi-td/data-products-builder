# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

This agentic system automates the creation of AI-Native Data Products on Teradata. Design standards are the single source of truth — skills and generated artifacts are derived from them and never edited independently.

## Project Structure

```
design-standards/        ← 8 design standard docs (master source of truth)
.claude/skills/          ← Claude Code skills (data-product-build, data-product-design, teradata-sql, teradata-query, data-product-use)
.claude/agents/          ← Claude Code agents
src/                     ← data product source code (per product, per module)
docs/                    ← data product documentation and release notes
config/                  ← configurations
scripts/                 ← tools for running/orchestrating builds
```

## Skills

- **data-product-build** (`/data-product-build [product-name]`): Orchestrates the full build process from requirements to deployment. Start here when building a new data product.
- **data-product-design** (`/data-product-design [module-name]`): Designs individual modules by strictly applying design standards. Contains architecture reference (six modules, deployment order, integration patterns).
- **teradata-sql** (`/teradata-sql`): Generates and validates Teradata SQL. Contains all DDL/DML conventions (boolean columns, surrogate keys, timestamps, temporal patterns, PI selection).
- **teradata-query** (`/teradata-query [query or sql-file]`): Installs, configures, and runs the tq CLI tool for executing Teradata queries — ad-hoc during development or batch execution during deployment.
- **data-product-use** (`/data-product-use [product-name]`): Guides agents consuming a deployed data product via Semantic module discovery.

## Project Rules

- Always present work for review before proceeding to the next step.
- Always use the data-product-build skill to orchestrate the data product building process.
- Never modify the design standards unless explicitly authorized by the user.
- Use the design standards as the most authoritative source of truth to resolve conflicts.
