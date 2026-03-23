---
name: data-product-build
description: Orchestrate the end-to-end data product building process — from requirements gathering through design, SQL generation, documentation, and deployment. Use when building a new data product or adding modules to an existing one.
user-invocable: true
argument-hint: [product-name]
---

# Data Product Build Orchestrator

You are orchestrating the build of an AI-Native Data Product named **{{arguments}}** on Teradata.

## Before You Start

1. Read `design-standards/AI_Native_Data_Product_Master_Design.md` for architecture context
2. Gather requirements using the template in `.agents/prompts/templates/requirements-template.md`
3. Ask clarifying questions (max 3-4 at a time) before writing anything

## Design Principles

- **Standards first** — start with the module design patterns, customise only when necessary
- **Justify deviations** — every departure from a standard must have a documented reason
- **Agent-native** — agents are primary consumers; every design decision should support autonomous discovery and querying
- **No data duplication** — each module owns its data; other modules join back, never copy
- **Teradata-optimised** — Primary Index choices, co-location, compression, and statistics collection are part of the design, not afterthoughts

## Build Sequence

Work through the deliverables below **in order**. The design order follows deployment order so that each module's documentation INSERTs can target tables that already exist.

**Review gates:** Present each deliverable for review before continuing. If the user indicates they want continuous execution (e.g. "go ahead", "go all the way"), skip review gates and complete all remaining deliverables in one pass.

If you have clarifying questions before starting a deliverable, ask them first — group questions so the user is never answering more than 3-4 at a time.

### Deliverable 1 — Requirements & Entity Map

- Confirm the core business entities needed (name, purpose, source system)
- Map each entity to the correct module (Domain, Prediction, Search, etc.)
- Identify relationships between entities
- Flag any scope decisions or ambiguities that need input before design begins
- Note any anticipated deviations from the design standards

### Deliverable 2 — Logical Data Model

- Entity definitions with key business attributes
- Relationships with cardinality
- ERD as a Mermaid diagram

### Deliverable 3 — Memory Module Schema

Memory must be designed and deployed first — all other modules write documentation INSERTs here.

- Production-ready DDL for runtime memory tables (agent_session, agent_interaction, learned_strategy, user_preference, discovered_pattern)
- Documentation Sub-Module tables (Module_Registry, Design_Decision, Business_Glossary, Query_Cookbook, Implementation_Note, Change_Log)
- Standard views (v_interactions_summary, v_Current_Decisions, v_Module_Registry_Current, v_Glossary_Active, v_Cookbook_Active, v_Issues_Open, v_Change_History)
- Self-documentation INSERTs (Memory registers itself in its own tables)

### Deliverable 4 — Semantic Module Schema & Seed Data

- DDL for all Semantic tables (data_product_map, entity_metadata, column_metadata, table_relationship, naming_standard)
- Required views (v_entity_catalog, v_entity_schema, v_relationship_paths)
- Seed `INSERT` statements for this data product:
  - `data_product_map` — one row per module (DEPLOYED or PLANNED)
  - `entity_metadata` — one row per table across **ALL** modules (Domain, Semantic, AND Memory). Do not forget to register Memory module entities.
  - `naming_standard` — full set for this product's conventions
  - `column_metadata` — all PII/sensitive columns at minimum
  - `table_relationship` — every FK and associative relationship
- Confirm `v_relationship_paths` produces valid JOIN syntax for key entity pairs
- Documentation capture INSERTs into Memory

### Deliverable 5 — Domain Module Schema

Use the **data-product-design** prompt for detailed module design and **teradata-sql** for SQL conventions.

- Production-ready DDL for all Domain entities, reference tables, and relationship tables
- `COMMENT ON TABLE` and `COMMENT ON COLUMN` for every object
- Primary Index selection with justification per table
- Standard views: `{Entity}_Current` for every entity, `{Entity}_Enriched` where appropriate
- Secondary indexes for anticipated query patterns
- Reference data seed INSERTs
- Documentation capture INSERTs into Memory

### Deliverable 6 — Additional Module Schemas (if selected)

Repeat for each additional selected module: **Observability → Search → Prediction**

For each module:
- Production-ready DDL applying the module design standard
- Standard views
- Representative sample queries demonstrating key use cases
- Semantic module registration (entity_metadata, table_relationship, data_product_map update)
- Documentation capture INSERTs into Memory

### Deliverable 7 — Integration Patterns & Documentation

- Cross-module join patterns specific to this product
- Data flow narrative (source systems → Domain → other modules)
- Agent consumption sequence: how an agent would discover and query this product end-to-end
- Any integration with other data products
- Standards applied without change (summary)
- Documented deviations with business justification
- Deployment sequence (table creation order, data load order)
- Update `docs/releases.md` and `docs/lessons-learned.md`

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

Update `docs/lessons-learned.md` with lessons learned from this data product build: these are not learnings related to the data logic, but to the process of building it, usage of the tools, SQL syntax, etc...

## Key Rules

- **Design standards are the master source of truth.** Read them from `design-standards/` before starting any module design.
- **Use the data-product-design prompt** for each module's detailed design work.
- **Use the teradata-sql prompt** when generating or validating SQL.
- **Use the teradata-query prompt** to execute SQL against Teradata (ad-hoc checks, deployment, validation).
- **Never modify design standards** unless explicitly authorized.
- Present work for review at every deliverable boundary.
