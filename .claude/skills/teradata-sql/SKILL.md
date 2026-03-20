---
name: teradata-sql
description: Generate and validate Teradata SQL (DDL/DML) following AI-Native Data Product conventions and best practices. Use when writing CREATE TABLE, CREATE VIEW, INSERT, UPDATE statements, or when validating existing SQL against the design standards.
user-invocable: true
---

# Teradata SQL — AI-Native Data Product Conventions

## Mandatory Column Conventions

These conventions apply to ALL SQL generated for AI-Native Data Products. They are non-negotiable.

### Boolean Columns
- Type: `BYTEINT NOT NULL DEFAULT 1` or `DEFAULT 0`
- Prefix: `is_` (e.g. `is_current`, `is_deleted`, `is_active`)
- Filter: `= 1` or `= 0`
- **Never** use `CHAR(1)`, `VARCHAR`, `'Y'`/`'N'`, or `'TRUE'`/`'FALSE'`

### Surrogate Keys
- Type: `BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) NOT NULL`
- Naming: `{table}_key` for surrogate, `{entity}_key` for natural/business key
- Example: `party_id BIGINT NOT NULL` (surrogate), `party_key VARCHAR(50) NOT NULL` (natural)

### Timestamps
- Type: `TIMESTAMP(6) WITH TIME ZONE`
- **Always** include timezone — never bare `TIMESTAMP(6)`
- Store in UTC (`+00:00`)
- Temporal end date: `DATE '9999-12-31'` or `TIMESTAMP '9999-12-31 23:59:59.999999+00:00'`

### Table and View Suffixes
- `_H` — history/temporal table (e.g. `Party_H`)
- `_R` — reference/lookup table (e.g. `Country_R`)
- `_Current` — current-state view (e.g. `Party_Current`)
- `_Enriched` — cross-module enriched view (e.g. `Party_Enriched`)

### Metadata Requirements
- `COMMENT ON TABLE` required on every table and view
- `COMMENT ON COLUMN` required on every column
- Comments must be agent-readable — clear, specific, no jargon without definition

## Temporal Table Rules

### Primary Index
- Temporal tables (bi-temporal, Type 2 SCD, versioned): use `PRIMARY INDEX` (NUPI) — **never** `UNIQUE PRIMARY INDEX`
- Reason: multiple versions exist for the same entity_id
- Non-temporal and reference tables: `UNIQUE PRIMARY INDEX` is acceptable

### Bi-Temporal Column Set (advocated default)
```sql
valid_from_dts        TIMESTAMP(6) WITH TIME ZONE NOT NULL
    COMMENT 'When this version became true in real world',
valid_to_dts          TIMESTAMP(6) WITH TIME ZONE NOT NULL
    DEFAULT TIMESTAMP '9999-12-31 23:59:59.999999+00:00'
    COMMENT 'When this version stopped being true in real world',
transaction_from_dts  TIMESTAMP(6) WITH TIME ZONE NOT NULL
    DEFAULT CURRENT_TIMESTAMP(6)
    COMMENT 'When this version was inserted into database',
transaction_to_dts    TIMESTAMP(6) WITH TIME ZONE NOT NULL
    DEFAULT TIMESTAMP '9999-12-31 23:59:59.999999+00:00'
    COMMENT 'When this version was superseded in database',
is_current            BYTEINT NOT NULL DEFAULT 1
    COMMENT '1 = Current version, 0 = Historical version',
is_deleted            BYTEINT NOT NULL DEFAULT 0
    COMMENT '0 = Active, 1 = Soft deleted'
```

### Current-State View Pattern
```sql
CREATE VIEW {ProductName}_{Module}.{Entity}_Current AS
SELECT {columns}
FROM {ProductName}_{Module}.{Entity}_H
WHERE is_current = 1
  AND is_deleted = 0;

COMMENT ON VIEW {ProductName}_{Module}.{Entity}_Current
AS 'Current active {entity} records — filters is_current=1 AND is_deleted=0';
```

### Version Update Pattern (expire-current → insert-new)
```sql
-- Step 1: Close current version
UPDATE {table}
SET valid_to_dts = CURRENT_TIMESTAMP(6),
    transaction_to_dts = CURRENT_TIMESTAMP(6),
    is_current = 0
WHERE {entity}_id = {id} AND is_current = 1;

-- Step 2: Insert new version
INSERT INTO {table} ({columns})
VALUES ({new_values_with_is_current_1});
```

## Physical Design Guidance

For detailed guidance on PI selection, partitioning, secondary indexes, join indexes, compression, and statistics collection, read `design-standards/Advocated_Data_Management_Standards.md`.

### Quick PI Reference
| Entity Type | Advocated PI | Notes |
|-------------|-------------|-------|
| Core entities (temporal) | `PRIMARY INDEX ({entity}_id)` | NUPI — allows multiple versions |
| Reference data | `UNIQUE PRIMARY INDEX ({code})` | UPI — each code appears once |
| Relationship tables | `PRIMARY INDEX ({parent_id}, {child_id})` | Co-locate with parent |
| Time-series | `PRIMARY INDEX ({entity}_id, {time_col})` | Enable partition elimination |

## Validation Checklist

When reviewing SQL, check for these common errors:
- [ ] No `CHAR(1)` or `VARCHAR` boolean columns
- [ ] No `= 'Y'` or `= 'N'` filter values
- [ ] No `UNIQUE PRIMARY INDEX` on temporal tables
- [ ] All timestamps are `WITH TIME ZONE`
- [ ] All tables and columns have `COMMENT ON` statements
- [ ] `is_` prefix on all boolean columns
- [ ] Temporal end dates use `DATE '9999-12-31'`
- [ ] Views filter on `is_current = 1 AND is_deleted = 0`
