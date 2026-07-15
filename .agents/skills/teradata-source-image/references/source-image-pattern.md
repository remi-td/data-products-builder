# Teradata Source Image Pattern Reference

The **Source Image** is a foundational pattern in the Raw/Staging zone of a data lakehouse. It represents a persistent, standardized "gold" copy of an external source entity, mirroring its structure while isolating downstream processes from source extraction methods.

## Core Concepts

1. **Staging vs. Source Image**:
   - **Staging**: An ephemeral table populated by ingestion tools (e.g. replication, bulk loads, streaming ingestion). Contains technical transport columns, duplicate rows, and potentially out-of-order logs.
   - **Source Image**: A persistent table containing cleaned, typed, and deduplicated source records. It is the single source of truth for all downstream historical models.

2. **History Management (SCD Type 2)**:
   - Tracks changes to record values over time.
   - Uses Teradata's native `PERIOD(TIMESTAMP(6))` data type to define when a row was valid.
   - Leverages native temporal operators (`OVERLAPS`, `CONTAINS`, `P_INTERSECT`) for high-performance period manipulation.

## Temporal SQL Engine Flow

The historization pattern handles incoming batches incrementally using three staging steps (implemented via volatile tables):

### Step 1: Deduplication (`hist_prep_1`)
Resolves conflicts where the incoming batch contains multiple changes for the same primary key at the same timestamp.
- **Open-Ended (`use_valid_to = 'N'`)**: Uses `PERIOD(valid_from, '9999-12-31 23:59:59.999999' (timestamp))` to initialize the validity period.
- **Closed-Ended (`use_valid_to = 'Y'`)**: Uses `PERIOD(valid_from, valid_to)` as provided by the source.
- Uses `QUALIFY RANK() OVER (PARTITION BY key_cols, valid_from ORDER BY [valid_to DESC,] value_cols) = 1` to ensure unique keys per change timestamp.

### Step 2: Overlap Adjustment (`hist_prep_2`)
Unions the incoming source changes with target slices that need adjustment.
- Recalculates validity periods using the window function `LEAD(begin(valid_period)) OVER (PARTITION BY key_cols ORDER BY begin(valid_period))`.
- Crunches overlaps:
  - If a source record starts at the same time as a target record, the target record is overwritten.
  - If a source record starts after a target record starts but before it ends, the target record is shortened.
  - **Closed-ended only**: If a source record is completely contained within a target record, the target record is split into a left slice and a right slice.

### Step 3: Compaction (`hist_prep_3`)
Uses the built-in Teradata table operator `TD_SYSFNLIB.TD_NORMALIZE_MEET` to combine consecutive slices that have identical values.
- Reduces table size by merging records where no tracked columns changed.
- Requires passing key/value columns into `NEW VARIANT_TYPE()`, defining the return structure, and specifying `HASH BY` and `LOCAL ORDER BY` to distribute processing across Teradata AMPs.

### Step 4: Transactional Apply
1. Discards no-op records (records where the period and all tracked column values exactly match existing target records).
2. Deletes overlapping records from the target table.
3. Inserts all normalized, modified, and new records from `hist_prep_3`.

---

## Reference SQL Examples

Here are the complete generated SQL scripts for both open-ended and closed-ended history tracks.

### Example A: Open-Ended History Track (Valid From only)

```sql
-- Compiled Source Image History Load SQL
-- Source Table: source_t
-- Target Table: target_t
-- Mode: Open-ended (valid_from only)

-- Step 0: Clean up and recreate volatile staging tables
BEGIN TRANSACTION;

DROP TABLE hist_prep_1;
DROP TABLE hist_prep_2;
DROP TABLE hist_prep_3;

CREATE VOLATILE SET TABLE hist_prep_1 AS target_t WITH NO DATA ON COMMIT PRESERVE ROWS;
CREATE VOLATILE SET TABLE hist_prep_2 AS target_t WITH NO DATA ON COMMIT PRESERVE ROWS;
CREATE VOLATILE SET TABLE hist_prep_3 AS target_t WITH NO DATA ON COMMIT PRESERVE ROWS;

-- Step 1: Deduplicate incoming source rows and resolve conflicts
INSERT INTO hist_prep_1 (
    PK
    , Valid_per
    , Value_txt
)
SELECT 
    PK
    , PERIOD(Valid_from, '9999-12-31 23:59:59.999999' (timestamp))
    , Value_txt
FROM source_t
QUALIFY RANK() OVER (
    PARTITION BY PK, Valid_from 
    ORDER BY Value_txt
) = 1;

-- Step 2: Adjust overlapping slices and construct history timelines
INSERT INTO hist_prep_2 (
    PK
    , Valid_per
    , Value_txt
)
SELECT 
    PK
    , PERIOD(
        BEGIN(Valid_per) 
        , COALESCE(
            LEAD(BEGIN(Valid_per)) OVER (PARTITION BY PK ORDER BY BEGIN(Valid_per)), 
            ('9999-12-31 23:59:59.999999' (timestamp))
        )
    ) AS new_Valid_per
    , Value_txt
FROM 
(
    SELECT 
        s.PK,
        s.Valid_per,
        s.Value_txt,
        'S' as origin 
    FROM hist_prep_1 s
    UNION
    SELECT 
        t.PK,
        t.Valid_per,
        t.Value_txt,
        'T' as origin 
    FROM target_t t
    WHERE EXISTS
    (
        SELECT 1 
        FROM hist_prep_1 s 
        WHERE s.PK = t.PK 
        AND s.Valid_per OVERLAPS t.Valid_per
    )
    AND NOT EXISTS
    (
        SELECT 1 
        FROM hist_prep_1 s 
        WHERE s.PK = t.PK 
        AND (
            BEGIN(s.Valid_per) = BEGIN(t.Valid_per)
        )
    )
) a
QUALIFY (new_Valid_per <> a.Valid_per) OR origin = 'S';

-- Step 3: Compact contiguous slices with identical values (history compaction)
INSERT INTO hist_prep_3 (
    PK
    , Valid_per
    , Value_txt
)
SELECT 
    PK
    , Valid_per
    , Value_txt
FROM TABLE 
(
    TD_SYSFNLIB.TD_NORMALIZE_MEET
    (
        NEW VARIANT_TYPE(
            subtbl.PK, subtbl.Value_txt
        ), 
        subtbl.Valid_per
    )
    RETURNS (
        PK integer, Value_txt varchar(1000), Valid_per PERIOD(TIMESTAMP(6))
    )
    HASH BY PK
    LOCAL ORDER BY PK, Value_txt, Valid_per
)     
AS DT(
    PK, Value_txt, Valid_per
);

-- Step 4: Discard no-op updates (where target exactly matches prepared output)
DELETE FROM hist_prep_3 t
WHERE EXISTS
(
    SELECT 1 FROM target_t s 
    WHERE s.PK = t.PK 
    AND s.Valid_per = t.Valid_per
    AND (s.Value_txt = t.Value_txt OR (s.Value_txt IS NULL AND t.Value_txt IS NULL))
);

-- Step 5: Delete overlapped records from target and apply new/updated history
DELETE FROM target_t t
WHERE EXISTS
(
    SELECT 1 FROM hist_prep_3 s 
    WHERE s.PK = t.PK 
    AND s.Valid_per OVERLAPS t.Valid_per
);

INSERT INTO target_t (
    PK
    , Valid_per
    , Value_txt
)
SELECT 
    PK
    , Valid_per
    , Value_txt
FROM hist_prep_3;

COMMIT WORK;
```

### Example B: Closed-Ended History Track (Valid From and Valid To)

```sql
-- Compiled Source Image History Load SQL
-- Source Table: source_t
-- Target Table: target_t
-- Mode: Closed-ended (valid_to tracking)

-- Step 0: Clean up and recreate volatile staging tables
BEGIN TRANSACTION;

DROP TABLE hist_prep_1;
DROP TABLE hist_prep_2;
DROP TABLE hist_prep_3;

CREATE VOLATILE SET TABLE hist_prep_1 AS target_t WITH NO DATA ON COMMIT PRESERVE ROWS;
CREATE VOLATILE SET TABLE hist_prep_2 AS target_t WITH NO DATA ON COMMIT PRESERVE ROWS;
CREATE VOLATILE SET TABLE hist_prep_3 AS target_t WITH NO DATA ON COMMIT PRESERVE ROWS;

-- Step 1: Deduplicate incoming source rows and resolve conflicts
INSERT INTO hist_prep_1 (
    PK
    , Valid_per
    , Value_txt
)
SELECT 
    PK
    , PERIOD(Valid_from, Valid_to (timestamp))
    , Value_txt
FROM source_t
QUALIFY RANK() OVER (
    PARTITION BY PK, Valid_from 
    ORDER BY Valid_to DESC, Value_txt
) = 1;

-- Step 2: Adjust overlapping slices and construct history timelines
INSERT INTO hist_prep_2 (
    PK
    , Valid_per
    , Value_txt
)
SELECT 
    PK
    , PERIOD(
        BEGIN(Valid_per) 
        , COALESCE(
            LEAD(BEGIN(Valid_per)) OVER (PARTITION BY PK ORDER BY BEGIN(Valid_per)), 
            ('9999-12-31 23:59:59.999999' (timestamp))
        )
    )
    P_INTERSECT Valid_per AS new_Valid_per
    , Value_txt
FROM 
(
    SELECT 
        s.PK,
        s.Valid_per,
        s.Value_txt,
        'S' as origin 
    FROM hist_prep_1 s
    UNION
    SELECT 
        t.PK,
        t.Valid_per,
        t.Value_txt,
        'T' as origin 
    FROM target_t t
    WHERE EXISTS
    (
        SELECT 1 
        FROM hist_prep_1 s 
        WHERE s.PK = t.PK 
        AND s.Valid_per OVERLAPS t.Valid_per
    )
    AND NOT EXISTS
    (
        SELECT 1 
        FROM hist_prep_1 s 
        WHERE s.PK = t.PK 
        AND (
            BEGIN(s.Valid_per) = BEGIN(t.Valid_per)
            OR s.Valid_per CONTAINS t.Valid_per
        )
    )
    UNION ALL
    SELECT 
        t.PK,
        PERIOD(
            END(s.Valid_per) 
            , END(t.Valid_per)
        ) as Valid_per,
        t.Value_txt,
        'T' as origin
    FROM target_t t
    JOIN hist_prep_1 s 
        ON s.PK = t.PK 
        AND t.Valid_per CONTAINS s.Valid_per
        AND END(s.Valid_per) < END(t.Valid_per)
) a
QUALIFY (new_Valid_per <> a.Valid_per) OR origin = 'S';

-- Step 3: Compact contiguous slices with identical values (history compaction)
INSERT INTO hist_prep_3 (
    PK
    , Valid_per
    , Value_txt
)
SELECT 
    PK
    , Valid_per
    , Value_txt
FROM TABLE 
(
    TD_SYSFNLIB.TD_NORMALIZE_MEET
    (
        NEW VARIANT_TYPE(
            subtbl.PK, subtbl.Value_txt
        ), 
        subtbl.Valid_per
    )
    RETURNS (
        PK integer, Value_txt varchar(1000), Valid_per PERIOD(TIMESTAMP(6))
    )
    HASH BY PK
    LOCAL ORDER BY PK, Value_txt, Valid_per
)     
AS DT(
    PK, Value_txt, Valid_per
);

-- Step 4: Discard no-op updates (where target exactly matches prepared output)
DELETE FROM hist_prep_3 t
WHERE EXISTS
(
    SELECT 1 FROM target_t s 
    WHERE s.PK = t.PK 
    AND s.Valid_per = t.Valid_per
    AND (s.Value_txt = t.Value_txt OR (s.Value_txt IS NULL AND t.Value_txt IS NULL))
);

-- Step 5: Delete overlapped records from target and apply new/updated history
DELETE FROM target_t t
WHERE EXISTS
(
    SELECT 1 FROM hist_prep_3 s 
    WHERE s.PK = t.PK 
    AND s.Valid_per OVERLAPS t.Valid_per
);

INSERT INTO target_t (
    PK
    , Valid_per
    , Value_txt
)
SELECT 
    PK
    , Valid_per
    , Value_txt
FROM hist_prep_3;

COMMIT WORK;
```
