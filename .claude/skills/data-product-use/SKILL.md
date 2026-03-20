---
name: data-product-use
description: Guide agents consuming an existing AI-Native Data Product via autonomous Semantic module discovery. Use when querying, exploring, or integrating with a deployed data product.
user-invocable: true
argument-hint: [product-name]
---

# Consuming an AI-Native Data Product

You are discovering and querying the **$ARGUMENTS** data product on Teradata.

## Discovery Protocol

AI-Native Data Products are self-describing. The Semantic module is the entry point for autonomous discovery.

### Step 1 — Locate the Semantic Module

Convention: `{ProductName}_Semantic`

```sql
SELECT DatabaseName
FROM DBC.DatabasesV
WHERE DatabaseName = '${ARGUMENTS}_Semantic';
```

### Step 2 — Discover Deployed Modules

```sql
SELECT module_name, database_name, primary_tables, primary_views, deployment_status
FROM ${ARGUMENTS}_Semantic.data_product_map
WHERE is_active = 1
ORDER BY module_name;
```

This tells you which modules are deployed, where they live, key tables, and the naming pattern used.

### Step 3 — Explore Entities

```sql
-- What tables exist in each module?
SELECT entity_name, module_name, table_name, view_name, natural_key_column
FROM ${ARGUMENTS}_Semantic.entity_metadata
WHERE is_active = 1;

-- What do columns mean? (especially PII/sensitive)
SELECT table_name, column_name, business_description, is_pii, data_classification
FROM ${ARGUMENTS}_Semantic.column_metadata
WHERE table_name = '{table_of_interest}';
```

### Step 4 — Learn Relationships (how to JOIN)

```sql
-- Direct relationships
SELECT relationship_name, source_table, target_table,
       source_column, target_column, cardinality
FROM ${ARGUMENTS}_Semantic.table_relationship
WHERE is_active = 1;

-- Multi-hop paths (discover indirect joins)
SELECT hop_count, path_tables, path_joins
FROM ${ARGUMENTS}_Semantic.v_relationship_paths
WHERE source_table = '{from_table}'
  AND target_table = '{to_table}'
ORDER BY hop_count;
```

### Step 5 — Generate Queries

Now you have enough metadata to write correct SQL. Key patterns:

```sql
-- Current state of any entity
SELECT * FROM ${ARGUMENTS}_{Module}.{Entity}_Current;

-- Or equivalently:
SELECT * FROM ${ARGUMENTS}_{Module}.{Entity}_H
WHERE is_current = 1 AND is_deleted = 0;

-- Cross-module join (e.g. Domain + Prediction)
SELECT d.*, p.feature_value
FROM ${ARGUMENTS}_Domain.{Entity}_H d
JOIN ${ARGUMENTS}_Prediction.{entity}_features p
  ON p.{entity}_id = d.{entity}_id
WHERE d.is_current = 1 AND p.is_current = 1;
```

## What Each Module Stores

Modules store minimal data — all join back to Domain for full content:

| Module | Stores | Does NOT store |
|--------|--------|---------------|
| Domain | Business data (customers, products, transactions) | — |
| Prediction | Engineered features, model scores | Raw domain values |
| Search | Vector embeddings + entity keys | Entity content (join to Domain) |
| Memory | Agent state, sessions, table-level references | Instance-level keys |
| Observability | Events, metrics, aggregate counts | Instance data |
| Semantic | Metadata about all other modules | Business data |

## Key Principles

- **Entity = Table** (not a row). "Party" entity = `Party_H` table.
- **No data duplication** across modules. All modules JOIN back to Domain via foreign keys.
- **Use views** (`_Current`, `_Enriched`) for simplified access.
- **Temporal queries**: filter `is_current = 1 AND is_deleted = 0` for current state; use temporal range queries for historical.
- **Table references in metadata**: Memory and Observability use VARCHAR comma-separated table lists (format: `'Domain.Party_H, Prediction.customer_features'`). Query with `LIKE '%Party_H%'`.

## Consulting Documentation

The data product documents itself in `{ProductName}_Memory`:

```sql
-- Business glossary (what do terms mean?)
SELECT term, definition, module_name
FROM ${ARGUMENTS}_Memory.Business_Glossary
WHERE is_current = 1;

-- Proven query patterns
SELECT query_name, description, sql_template, use_case
FROM ${ARGUMENTS}_Memory.Query_Cookbook
WHERE is_current = 1;

-- Design decisions (why was it built this way?)
SELECT decision_id, title, decision, rationale
FROM ${ARGUMENTS}_Memory.Design_Decision
WHERE is_current = 1;
```

## Error Handling

- If `data_product_map` doesn't exist → data product may not follow AI-Native standards; fall back to `DBC.TablesV`
- If Semantic database doesn't exist → may use single-database approach with prefixes; look for `S_entity_metadata`, `S_table_relationship`
- If module shows `deployment_status = 'PLANNED'` → not yet deployed, skip it
