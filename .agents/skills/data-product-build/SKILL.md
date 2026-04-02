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
2. Gather requirements using the template in `.agents/skills/data-product-build/templates/requirements-template.md`
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

Use the **data-product-design** skill for detailed module design and **teradata-sql** skill for SQL conventions.

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
- Data flow narrative (source systems -> Domain -> other modules)
- Agent consumption sequence: how an agent would discover and query this product end-to-end
- Any integration with other data products
- Standards applied without change (summary)
- Documented deviations with business justification
- Deployment sequence (table creation order, data load order)
- Update `docs/releases.md` and `docs/lessons-learned.md`

### Deliverable 8 — Build Process Analysis

After the data product is deployed and validated, generate a build process analysis document using the template at `.agents/skills/data-product-build/templates/build-process-template.md`. Save it to `docs/{product-name}/build-process.md`.

This document is for technical reviewers and captures:

- **What was built** -- artifact inventory (databases, tables, views, features, indexes, documentation records)
- **How it was built** -- Mermaid diagrams showing agent orchestration, deployment sequence with error locations, data lineage, and semantic discovery graph. **Mermaid syntax rules**: (1) subgraph IDs must be simple identifiers with no spaces or colons -- use `subgraph P0[Phase 0 - Setup]` not `subgraph "Phase 0: Setup"`; (2) edge labels must have NO space between arrow and pipe -- use `-->|label|` not `--> |label|`; (3) node labels must not contain special characters like `!!`, unescaped quotes, or colons; (4) use hyphens instead of colons in labels
- **Skill and tool usage** -- which skills were explicitly invoked vs applied implicitly, tool call counts by phase, and the detailed call flow tree
- **Errors and fixes** -- every deployment error, root cause, fix applied, and whether it was codified back into a skill
- **Process timeline** -- effort distribution across discovery, generation, deployment, documentation, and skill optimization
- **Improvement opportunities** -- actionable recommendations for process and tooling (not data logic)

This deliverable also includes updating skills with any new lessons learned during the build (Teradata syntax issues, deployment gotchas, tool usage patterns). If errors occurred that are not yet covered by the `teradata-sql` or `teradata-query` skills, add them.

## Module Deployment Order

Deploy modules in this order — dependencies are strict:

| Phase | Modules | Why |
|-------|---------|-----|
| 1 | Memory + Semantic | Memory hosts documentation tables; Semantic hosts discovery metadata — both must exist before any other module |
| 2 | Domain + Observability | Domain is the entity foundation; Observability begins monitoring immediately |
| 3 | Search + Prediction | Both require Domain entities to exist first |

### Deployment Execution Rules

1. **Create all databases first** -- one `CREATE DATABASE` per module, all can run in parallel.
2. **Grant cross-database permissions immediately after creating databases** -- any module whose views reference another module's tables needs `GRANT SELECT ON source_db TO target_db WITH GRANT OPTION`. Do this before deploying any SQL.
3. **Sanitize all SQL files** before execution: `scripts/sanitize-sql.sh src/{product-name}/**/*.sql`
4. **Deploy sequentially within each phase** -- tables must complete before views, views before seed data, seed data before documentation. Never run dependent files in parallel or in the background.
5. **Verify data counts** after each phase completes -- query `_Current` views and reference tables.
6. **Use REPLACE VIEW** (not CREATE VIEW) when redeploying to handle "already exists" errors gracefully.

### Deployment File Execution Sequence

Execute files in numbered order within each module, modules in phase order. Use the **teradata-query** skill to run each file.

```
Phase 1 — Memory + Semantic (must complete before Phase 2):
  src/{product}/01-memory/01-tables.sql
  src/{product}/01-memory/02-views.sql
  src/{product}/01-memory/03-documentation.sql
  src/{product}/02-semantic/01-tables.sql
  src/{product}/02-semantic/02-views.sql
  src/{product}/02-semantic/03-seed-data.sql
  src/{product}/02-semantic/04-documentation.sql

Phase 2 — Domain + Observability (must complete before Phase 3):
  src/{product}/03-domain/01-tables.sql
  src/{product}/03-domain/02-views.sql
  src/{product}/03-domain/03-indexes.sql
  src/{product}/03-domain/04-reference-data.sql    (includes data load from source)
  src/{product}/03-domain/05-documentation.sql

Phase 3 — Search + Prediction:
  src/{product}/04-prediction/01-tables.sql
  src/{product}/04-prediction/02-views.sql
  src/{product}/04-prediction/03-feature-load.sql   (computes features from Domain)
  src/{product}/04-prediction/04-documentation.sql
```

### Post-Deployment Validation

After each phase, verify the deployment:

```sql
-- After Phase 1: Confirm Semantic module registry
SELECT module_name, database_name, deployment_status
FROM {Product}_Semantic.data_product_map WHERE is_active = 1;

-- After Phase 2: Confirm Domain data loaded
SELECT 'entity_name' AS entity, COUNT(*) AS cnt FROM {Product}_Domain.{Entity}_Current;

-- After Phase 3: Confirm features computed
SELECT COUNT(*) FROM {Product}_Prediction.v_customer_segmentation_current;

-- End-to-end: Test multi-hop path discovery
SELECT hop_count, path_tables, path_joins
FROM {Product}_Semantic.v_relationship_paths
WHERE source_table = '{TableA}' AND target_table = '{TableB}'
ORDER BY hop_count;
```

## Output Structure

For each data product, create:
```
src/{product-name}/
  {nn}-{module}/          # SQL files per module, numbered by deploy order
    {nn}-{object}.sql     # Individual DDL/DML files
docs/{product-name}/
  requirements.md         # Deliverable 1-2
  design-decisions.md     # Architecture decisions
  build-process.md        # Deliverable 8 — build process analysis (from template)
```

The build process template is at `.agents/skills/data-product-build/templates/build-process-template.md`.

Update `docs/releases.md` when a data product reaches deployment.

Update `docs/lessons-learned.md` with lessons learned from this data product build: these are not learnings related to the data logic, but to the process of building it, usage of the tools, SQL syntax, etc...

## Key Rules

- **Design standards are the master source of truth.** Read them from `design-standards/` before starting any module design.
- **Use the data-product-design prompt** for each module's detailed design work.
- **Use the teradata-sql prompt** when generating or validating SQL.
- **Use the teradata-query prompt** to execute SQL against Teradata (ad-hoc checks, deployment, validation).
- **Never modify design standards** unless explicitly authorized.
- Present work for review at every deliverable boundary.
