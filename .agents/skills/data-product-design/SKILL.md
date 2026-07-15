---
name: data-product-design
description: Design individual modules of an AI-Native Data Product by strictly applying the Teradata design standards. Use when designing a specific module (Domain, Semantic, Search, Prediction, Observability, Memory) or when needing architecture guidance.
user-invocable: true
argument-hint: [module-name]
---

# Data Product Module Design

You are designing the **{{arguments}}** module of an AI-Native Data Product on Teradata.

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

   > **Semantic seed data completeness:** When designing the Semantic module, entity_metadata must register entities from **ALL** modules in the data product (Memory, Semantic, AND Domain), not just the module being designed. This is easy to miss — verify that every table across every module has an entity_metadata row.

4. **Present work for review** before proceeding.

## Consistency Checks

Before writing any DDL, verify across all design standards:
- Boolean flags use `BYTEINT NOT NULL DEFAULT 1/0` -- never `CHAR(1)`
- Boolean columns use the `is_` prefix
- Filter values use `= 1` or `= 0` -- never `= 'Y'` or `= 'N'`
- Temporal tables use non-unique `PRIMARY INDEX` -- never `UNIQUE PRIMARY INDEX`

**Stop and report any inconsistencies before proceeding.** List the table name, column name, current definition, and corrected definition.

## Teradata DDL Syntax (mandatory)

These are hard Teradata syntax rules. The **teradata-sql** prompt has full details, but the critical ones are:

1. **PRIMARY INDEX goes AFTER the closing `)` of the column list** -- never inside it
2. **No inline COMMENT in CREATE TABLE** -- use separate `COMMENT ON COLUMN` statements
3. **No ORDER BY in view definitions** -- Teradata does not allow it
4. **No trailing comma before closing `)`** in CREATE TABLE
5. **ASCII only** -- no em dashes, smart quotes, or arrows. Run `scripts/sanitize-sql.sh` before deployment

## Documentation Capture Protocol

Every module must generate these INSERTs into `{ProductName}_Memory`:
- 1x Module_Registry INSERT
- Min. 3x Design_Decision INSERTs (ID format: `DD-{MODULE}-{NNN}`)
- 1x Change_Log INSERT (ID format: `CL-{MODULE}-{NNN}`)
- Min. 3x Business_Glossary INSERTs
- Min. 1x Query_Cookbook INSERT (ID format: `QC-{MODULE}-{NNN}`)

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

## Profiling Fallback for Wide Tables

Live SQL profiling of wide tables (300+ columns × 10M+ rows) commonly times out or causes AMP contention on trial and bandwidth-limited environments. When profiling stalls:

1. **Enumerate-size heuristic:** If the source codebook lists fewer than 30 distinct enumerated values for a column, infer `BYTEINT` or `SMALLINT`. If it lists a date-like label (e.g. "incident date", "date of birth"), infer `VARCHAR(8)` or `VARCHAR(10)`.
2. **Fallback default:** Use `VARCHAR(1000) CHARACTER SET LATIN` for all columns where the codebook is ambiguous or unavailable. This is always safe — no cast failures, preserves leading zeros and mixed content.
3. **Never block a build on profiling.** Generate DDL from the lossless fallback, document the decision in `Memory.Design_Decision`, and profile in the background after deployment. Type narrowing can be applied in a later Semantic or Prediction layer.
4. **Separate profiling from DDL deployment.** Never run profiling queries on the critical path while staging loads are in flight — they compete for the same AMP resources and can cause both to time out.

## Key Constraints

- Design standards in `design-standards/` are the master source of truth
- Use the teradata-sql prompt for SQL conventions and validation
- Never modify design standards unless explicitly authorized
- When conflicts arise between any source and the design standards, the design standards win
