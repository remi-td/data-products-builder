---
name: data-product-design
description: Design individual modules of an AI-Native Data Product by strictly applying the Teradata design standards. Use when designing a specific module (Domain, Semantic, Search, Prediction, Observability, Memory) or when needing architecture guidance.
user-invocable: true
argument-hint: [module-name]
---

# Data Product Module Design

You are designing the **$ARGUMENTS** module of an AI-Native Data Product on Teradata.

## Architecture

Each data product is composed of six independently deployable modules, each with its own Teradata database (`{ProductName}_{Module}`):

| Module | Database Pattern | Purpose |
|--------|-----------------|---------|
| Memory | `{Name}_Memory` | Agent state, learning, and design documentation (Documentation Sub-Module) |
| Semantic | `{Name}_Semantic` | Metadata layer enabling agent discovery — the "map" of the data product |
| Domain | `{Name}_Domain` | Core business entities — source of truth |
| Observability | `{Name}_Observability` | Event tracking, quality monitoring, lineage |
| Search | `{Name}_Search` | Vector embeddings and similarity search |
| Prediction | `{Name}_Prediction` | Feature store and ML prediction storage |

### Deployment Order (strict)

Phase 1: Memory + Semantic → Phase 2: Domain + Observability → Phase 3: Search + Prediction

### Cross-Module Integration Patterns

- **Join-Back**: All modules JOIN to Domain (no data duplication). Teradata co-location makes this efficient.
- **Enhancement**: Modules progressively enhance Domain entities (Search adds embeddings, Prediction adds features, Semantic adds metadata).
- **Feedback Loop**: Observability → Memory → Feature Store → Prediction (closed-loop learning).

## Design Workflow

1. **Read the relevant design standard** from `design-standards/`:
   - `AI_Native_Data_Product_Master_Design.md` — always read first
   - `Domain_Module_Design_Standard.md`
   - `Semantic_Module_Design_Standard.md`
   - `Search_Module_Design_Standard.md`
   - `Prediction_Module_Design_Standard.md`
   - `Observability_Module_Design_Standard.md`
   - `Memory_Module_Design_Standard.md`
   - `Advocated_Data_Management_Standards.md` — recommended practices

2. **Apply the standard strictly.** Customize only where business requirements demand it. Document any deviations with justification.

3. **For each module, produce:**
   - Production-ready DDL (CREATE TABLE, CREATE VIEW)
   - `COMMENT ON TABLE` and `COMMENT ON COLUMN` for every object
   - Primary Index selection with justification
   - Standard views (`{Entity}_Current`, `{Entity}_Enriched` where appropriate)
   - Semantic module registration INSERTs (entity_metadata, column_metadata, table_relationship, data_product_map)
   - Documentation capture INSERTs into `{ProductName}_Memory` (Module_Registry, Design_Decision, Business_Glossary, Query_Cookbook, Change_Log)

4. **Present work for review** before proceeding.

## Consistency Checks

Before writing any DDL, verify across all design standards:
- Boolean flags use `BYTEINT NOT NULL DEFAULT 1/0` — never `CHAR(1)`
- Boolean columns use the `is_` prefix
- Filter values use `= 1` or `= 0` — never `= 'Y'` or `= 'N'`
- Temporal tables use non-unique `PRIMARY INDEX` — never `UNIQUE PRIMARY INDEX`

**Stop and report any inconsistencies before proceeding.** List the table name, column name, current definition, and corrected definition.

## Documentation Capture Protocol

Every module must generate these INSERTs into `{ProductName}_Memory`:
- 1× Module_Registry INSERT
- Min. 3× Design_Decision INSERTs (ID format: `DD-{MODULE}-{NNN}`)
- 1× Change_Log INSERT (ID format: `CL-{MODULE}-{NNN}`)
- Min. 3× Business_Glossary INSERTs
- Min. 1× Query_Cookbook INSERT (ID format: `QC-{MODULE}-{NNN}`)

Temporal field defaults: `valid_from = CURRENT_DATE`, `valid_to = DATE '9999-12-31'`, `is_current = 1`, `is_active = 1`

Output file: last numbered file in each module directory (e.g. `01-domain/05-documentation.sql`)

### Documentation Capture ID Prefixes

| Module | Decision ID | Change Log | Query Cookbook | Impl. Note |
|--------|------------|------------|----------------|------------|
| Domain | DD-DOMAIN- | CL-DOMAIN- | QC-DOMAIN- | IN-DOMAIN- |
| Semantic | DD-SEMANTIC- | CL-SEMANTIC- | QC-SEMANTIC- | IN-SEMANTIC- |
| Search | DD-SEARCH- | CL-SEARCH- | QC-SEARCH- | IN-SEARCH- |
| Prediction | DD-PREDICTION- | CL-PREDICTION- | QC-PREDICTION- | IN-PREDICTION- |
| Observability | DD-OBSERVABILITY- | CL-OBSERVABILITY- | QC-OBSERVABILITY- | IN-OBSERVABILITY- |
| Memory | DD-MEMORY- | CL-MEMORY- | QC-MEMORY- | IN-MEMORY- |

## Key Constraints

- Design standards in `design-standards/` are the master source of truth
- Use the teradata-sql skill for SQL conventions and validation
- Never modify design standards unless explicitly authorized
- When conflicts arise between any source and the design standards, the design standards win
