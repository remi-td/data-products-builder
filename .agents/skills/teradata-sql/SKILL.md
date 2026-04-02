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
- **Always** include timezone -- never bare `TIMESTAMP(6)`
- Store in UTC (`+00:00`)
- Temporal end date: `DATE '9999-12-31'` or `TIMESTAMP '9999-12-31 23:59:59.999999+00:00'`

### Table and View Suffixes
- `_H` -- history/temporal table (e.g. `Party_H`)
- `_R` -- reference/lookup table (e.g. `Country_R`)
- `_Current` -- current-state view (e.g. `Party_Current`)
- `_Enriched` -- cross-module enriched view (e.g. `Party_Enriched`)

### Metadata Requirements
- `COMMENT ON TABLE` required on every table and view
- `COMMENT ON COLUMN` required on every column -- as **separate statements** after CREATE TABLE
- Comments must be agent-readable -- clear, specific, no jargon without definition
- **Never** use inline `COMMENT` inside CREATE TABLE column definitions -- Teradata does not support this syntax

## Teradata DDL Syntax Rules

These are Teradata-specific syntax rules. Violating them causes hard errors.

### PRIMARY INDEX placement
- PRIMARY INDEX and UNIQUE PRIMARY INDEX must appear **AFTER** the closing `)` of the column list, never inside it.

```sql
-- CORRECT:
CREATE TABLE Example (
    col1 BIGINT NOT NULL,
    col2 VARCHAR(50)
)
PRIMARY INDEX (col1);

-- WRONG (error 3706/3707):
CREATE TABLE Example (
    col1 BIGINT NOT NULL,
    col2 VARCHAR(50),
    PRIMARY INDEX (col1)
);
```

### No inline COMMENT in column definitions
- Teradata does not support `COMMENT 'text'` on column definitions inside CREATE TABLE.
- Use separate `COMMENT ON COLUMN` statements after the table is created.

```sql
-- CORRECT:
CREATE TABLE Example (
    col1 VARCHAR(50) NOT NULL
)
PRIMARY INDEX (col1);

COMMENT ON COLUMN Example.col1 IS 'Description here';

-- WRONG (error 3706):
CREATE TABLE Example (
    col1 VARCHAR(50) NOT NULL
        COMMENT 'Description here'
)
PRIMARY INDEX (col1);
```

### No ORDER BY in view definitions
- Teradata does not allow ORDER BY in view subqueries.
- Sorting must be done by the consuming query, not the view.

```sql
-- CORRECT:
REPLACE VIEW Example_View AS
SELECT col1, col2 FROM Example;

-- WRONG (error 3706):
REPLACE VIEW Example_View AS
SELECT col1, col2 FROM Example
ORDER BY col1;
```

### No trailing comma before closing parenthesis

```sql
-- CORRECT:
CREATE TABLE Example (
    col1 BIGINT NOT NULL,
    col2 VARCHAR(50)    -- no trailing comma on last column
)
PRIMARY INDEX (col1);

-- WRONG (syntax error):
CREATE TABLE Example (
    col1 BIGINT NOT NULL,
    col2 VARCHAR(50),   -- trailing comma causes error
)
PRIMARY INDEX (col1);
```

### Secondary Index syntax
- Teradata does NOT use standard ANSI `CREATE INDEX name ON table (column)` syntax.
- Correct Teradata syntax: `CREATE INDEX (column) ON database.table;`
- Named indexes are not supported in this basic form.

```sql
-- CORRECT (Teradata):
CREATE INDEX (customer_key) ON RetailSales_Domain.Customer_H;
CREATE INDEX (is_current, is_deleted) ON RetailSales_Domain.Customer_H;

-- WRONG (ANSI -- causes error 3706 on Teradata):
CREATE INDEX idx_customer_key ON RetailSales_Domain.Customer_H (customer_key);
```

### Reserved word conflicts in table aliases
- Teradata reserves certain short identifiers. The alias `cm` causes "expected something between ',' and the 'cm' keyword" errors.
- **Prefer single-letter aliases** (`c`, `e`, `o`, `p`, `f`) or longer descriptive aliases that avoid collisions.

```sql
-- CORRECT:
SELECT e.entity_name, c.column_name
FROM entity_metadata e
INNER JOIN column_metadata c ON c.table_name = e.table_name;

-- WRONG (cm is reserved):
SELECT em.entity_name, cm.column_name
FROM entity_metadata em
INNER JOIN column_metadata cm ON cm.table_name = em.table_name;
```

### Cross-database view permissions
- Views referencing tables in another database require `GRANT SELECT ... WITH GRANT OPTION` from the source database to the target database.
- This must be done **before** creating the view.

```sql
-- Grant Prediction database access to read Domain tables
GRANT SELECT ON RetailSales_Domain TO RetailSales_Prediction WITH GRANT OPTION;
```

### ASCII only in all SQL
- Teradata rejects non-ASCII characters with error **6706: untranslatable character**.
- LLM-generated text commonly introduces: em dashes, en dashes, smart quotes, arrows.
- **Always** use ASCII equivalents: `--` not em-dash, `'` not smart quotes, `->` not arrows.
- Run `scripts/sanitize-sql.sh` on generated SQL files before execution.

## Temporal Table Rules

### Primary Index
- Temporal tables (bi-temporal, Type 2 SCD, versioned): use `PRIMARY INDEX` (NUPI) -- **never** `UNIQUE PRIMARY INDEX`
- Reason: multiple versions exist for the same entity_id
- Non-temporal and reference tables: `UNIQUE PRIMARY INDEX` is acceptable

### Bi-Temporal Column Set (advocated default)
```sql
-- Column definitions (inside CREATE TABLE):
valid_from_dts        TIMESTAMP(6) WITH TIME ZONE NOT NULL,
valid_to_dts          TIMESTAMP(6) WITH TIME ZONE NOT NULL
    DEFAULT TIMESTAMP '9999-12-31 23:59:59.999999+00:00',
transaction_from_dts  TIMESTAMP(6) WITH TIME ZONE NOT NULL
    DEFAULT CURRENT_TIMESTAMP(6),
transaction_to_dts    TIMESTAMP(6) WITH TIME ZONE NOT NULL
    DEFAULT TIMESTAMP '9999-12-31 23:59:59.999999+00:00',
is_current            BYTEINT NOT NULL DEFAULT 1,
is_deleted            BYTEINT NOT NULL DEFAULT 0

-- COMMENT ON COLUMN statements (after CREATE TABLE):
COMMENT ON COLUMN {table}.valid_from_dts IS 'When this version became true in real world';
COMMENT ON COLUMN {table}.valid_to_dts IS 'When this version stopped being true in real world';
COMMENT ON COLUMN {table}.transaction_from_dts IS 'When this version was inserted into database';
COMMENT ON COLUMN {table}.transaction_to_dts IS 'When this version was superseded in database';
COMMENT ON COLUMN {table}.is_current IS '1 = Current version, 0 = Historical version';
COMMENT ON COLUMN {table}.is_deleted IS '0 = Active, 1 = Soft deleted';
```

### Current-State View Pattern
```sql
REPLACE VIEW {ProductName}_{Module}.{Entity}_Current AS
SELECT {columns}
FROM {ProductName}_{Module}.{Entity}_H
WHERE is_current = 1
  AND is_deleted = 0;

COMMENT ON VIEW {ProductName}_{Module}.{Entity}_Current
AS 'Current active {entity} records -- filters is_current=1 AND is_deleted=0';
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

**Column conventions:**
- [ ] No `CHAR(1)` or `VARCHAR` boolean columns
- [ ] No `= 'Y'` or `= 'N'` filter values
- [ ] `is_` prefix on all boolean columns
- [ ] All timestamps are `WITH TIME ZONE`
- [ ] Temporal end dates use `DATE '9999-12-31'`
- [ ] No `UNIQUE PRIMARY INDEX` on temporal tables

**Teradata DDL syntax:**
- [ ] PRIMARY INDEX is outside the column list (after closing `)`)
- [ ] No inline `COMMENT` in CREATE TABLE column definitions
- [ ] No trailing comma before closing `)` in CREATE TABLE
- [ ] No `ORDER BY` in view definitions
- [ ] All text is ASCII only -- no em dashes, smart quotes, or arrows
- [ ] Secondary indexes use `CREATE INDEX (col) ON table` syntax (not ANSI)
- [ ] No `cm` table alias (reserved word) -- use `c` instead
- [ ] Cross-database views have GRANT SELECT WITH GRANT OPTION

**Metadata:**
- [ ] All tables and columns have `COMMENT ON` statements (as separate statements)
- [ ] Views filter on `is_current = 1 AND is_deleted = 0`

