---
name: data-product-build
description: Orchestrate the end-to-end data product building process — from requirements gathering through design, SQL generation, documentation, and deployment. Use when building a new data product or adding modules to an existing one.
user-invocable: true
argument-hint: [product-name]
---

# Data Product Build Orchestrator

You are orchestrating the build of an AI-Native Data Product named **$ARGUMENTS** on Teradata.

## Before You Start

1. Read `design-standards/AI_Native_Data_Product_Master_Design.md` for architecture context
2. Gather requirements using the template in `${CLAUDE_SKILL_DIR}/requirements-template.md`
3. Ask clarifying questions (max 3-4 at a time) before writing anything

## Design Principles

- **Standards first** — start with the module design patterns, customise only when necessary
- **Justify deviations** — every departure from a standard must have a documented reason
- **Agent-native** — agents are primary consumers; every design decision should support autonomous discovery and querying
- **No data duplication** — each module owns its data; other modules join back, never copy
- **Teradata-optimised** — Primary Index choices, co-location, compression, and statistics collection are part of the design, not afterthoughts

## Build Sequence

Work through the deliverables below **in order**. **Stop after each deliverable, present the output, and wait for review before continuing.**

If you have clarifying questions before starting a deliverable, ask them first — group questions so the user is never answering more than 3–4 at a time.

### Deliverable 1 — Requirements & Entity Map

- Confirm the core business entities needed (name, purpose, source system)
- Map each entity to the correct module (Domain, Prediction, Search, etc.)
- Identify relationships between entities
- Flag any scope decisions or ambiguities that need input before design begins
- Note any anticipated deviations from the design standards

*Stop here and wait for review.*

### Deliverable 2 — Logical Data Model

- Entity definitions with key business attributes
- Relationships with cardinality
- ERD as a Mermaid diagram

*Stop here and wait for review.*

### Deliverable 3 — Domain Module Schema

Use the **data-product-design** skill for detailed module design and **teradata-sql** for SQL conventions.

- Production-ready DDL for all Domain entities, reference tables, and relationship tables
- `COMMENT ON TABLE` and `COMMENT ON COLUMN` for every object
- Primary Index selection with justification per table
- Standard views: `{Entity}_Current` for every entity, `{Entity}_Enriched` where appropriate
- Secondary indexes for anticipated query patterns

*Stop here and wait for review.*

### Deliverable 4 — Semantic Module Schema & Seed Data

- DDL for all Semantic tables
- Seed `INSERT` statements for this data product:
  - `data_product_map` — one row per module (DEPLOYED or PLANNED)
  - `entity_metadata` — one row per table across all modules
  - `naming_standard` — full set for this product's conventions
  - `column_metadata` — all PII/sensitive columns at minimum
  - `table_relationship` — every FK and associative relationship
- Confirm `v_relationship_paths` produces valid JOIN syntax for key entity pairs

*Stop here and wait for review.*

### Deliverable 5 — Additional Module Schemas

Repeat for each selected module in this order: **Prediction → Search → Observability → Memory**

For each module:
- Production-ready DDL applying the module design standard
- Standard views
- Representative sample queries demonstrating key use cases
- Semantic module registration (entity_metadata, table_relationship, data_product_map update)

*Stop after each module and wait for review before proceeding to the next.*

### Deliverable 6 — Integration Patterns

- Cross-module join patterns specific to this product
- Data flow narrative (source systems → Domain → other modules)
- Agent consumption sequence: how an agent would discover and query this product end-to-end
- Any integration with other data products

*Stop here and wait for review.*

### Deliverable 7 — Deviations & Implementation Plan

- Standards applied without change (summary)
- Documented deviations with business justification
- Deployment sequence (table creation order, data load order)
- Suggested feedback to the design standards based on lessons from this design

*Final deliverable — present for sign-off.*

## Module Deployment Order

Deploy modules in this order — dependencies are strict:

| Phase | Modules | Why |
|-------|---------|-----|
| 1 | Memory + Semantic | Memory hosts documentation tables; Semantic hosts discovery metadata — both must exist before any other module |
| 2 | Domain + Observability | Domain is the entity foundation; Observability begins monitoring immediately |
| 3 | Search + Prediction | Both require Domain entities to exist first |

## Output Structure

For each data product, create:
```
src/{product-name}/
  {nn}-{module}/          # SQL files per module, numbered by deploy order
    {nn}-{object}.sql     # Individual DDL/DML files
docs/{product-name}/
  requirements.md         # Deliverable 1-2
  design-decisions.md     # Architecture decisions
```

Update `docs/releases.md` when a data product reaches deployment.

Update `docs/lessons-learned.md` with lessons learned from this data product build: these are not learnings related to teh data logic, but to the process of building it, usage of the tools, SQL syntax, etc... 

## Key Rules

- **Design standards are the master source of truth.** Read them from `design-standards/` before starting any module design.
- **Use the data-product-design skill** for each module's detailed design work.
- **Use the teradata-sql skill** when generating or validating SQL.
- **Use the teradata-query skill** to execute SQL against Teradata (ad-hoc checks, deployment, validation).
- **Never modify design standards** unless explicitly authorized.
- Present work for review at every deliverable boundary.
