# Change Request: teradata-sql skill

**Source skill:** `.agents/skills/teradata-sql/SKILL.md`  
**Derived from:** generic source-image build
**Status:** Ready to submit

---

## CR-1: Lossless Source Image Typing

**Insert before `## Validation Checklist`**

**Motivation:** A data product build hit Error 2621 ("bad character in format") when INSERT-SELECT attempted to load VARCHAR staging data into a Domain table that had BYTEINT/DATE columns inferred from the codebook. Regenerating with all-VARCHAR eliminated all cast failures. A second error (3623) occurred when COMPRESS was applied to a PRIMARY INDEX column in the optimized schema.

**Text to add:**

```markdown
## Lossless Source Image Typing

When building a Source Image (faithful staging snapshot of external files), never apply numeric or date type narrowing in the DDL:

- Use `VARCHAR` for all string-like, mixed-content, and date-like columns
- Use `CHAR(n)` only when every value is non-blank and exactly length `n` (n ≤ 32) — this preserves leading zeros without the 2-byte VARCHAR overhead
- Never cast to `DATE`, `INTEGER`, `BYTEINT`, or `FLOAT` at the staging or Domain layer; save type narrowing for the Semantic or Prediction layer
- Do not estimate perm savings from declared VARCHAR widths — Teradata VARCHAR is variable-length on disk (actual data + 2 bytes overhead); storage savings from declared-width reduction are negligible for real data. Actual CHAR + COMPRESS gains on sparse code columns are modest (~10%) and lossless

```sql
-- WRONG (causes Error 2621 on INSERT-SELECT from an all-VARCHAR staging table):
INCDATE  DATE FORMAT 'YY/MM/DD',
OFFCODE  BYTEINT,

-- CORRECT (lossless -- no cast failures, preserves leading zeros and mixed content):
INCDATE  VARCHAR(20),
OFFCODE  VARCHAR(5),
```

`COMPRESS` on low-cardinality or high-blank columns is safe and recommended — but **never COMPRESS a PRIMARY INDEX column** (Error 3623).
```

**Validation checklist additions** (add to the existing checklist at the end of the file):

```markdown
**Source image typing:**
- [ ] No numeric or DATE narrowing in staging-to-domain loads (all VARCHAR unless proven fixed-width)
- [ ] No COMPRESS on PRIMARY INDEX columns
- [ ] CHAR(n) used only when all values are non-blank and exactly length n
```

---

## CR-2: FastLoad Lock Hazards and Recovery

**Insert before `## Validation Checklist`** (after CR-1)

**Motivation:** Two distinct FastLoad errors hit in consecutive build sessions:
- Error 2636 ("table must be empty for FastLoad"): caused by `autocommit=True` (the teradatasql default), which committed each `executemany` batch independently and closed the FastLoad phase. Fix: `con.autocommit = False`.
- Error 2652 ("being Loaded"): caused by killing a FastLoad mid-flight (broken pipe + process kill). The table was unreachable until idle timeout cleared the orphaned session. Fix: DROP+recreate; prefer the batched-autocommit loader.

**Text to add:**

```markdown
## FastLoad Lock Hazards and Recovery

FastLoad (including the `{fn teradata_try_fastload}` escape) operates as a two-phase protocol that holds a table lock for the entire transaction:

- **Set `con.autocommit = False` before calling `executemany`.** With `autocommit=True` (the default) each `executemany` batch commits independently, closing the FastLoad phase and locking the table for the next batch (Error 2636: "table must be empty for FastLoad").
- **Never kill a FastLoad session mid-flight.** A process kill or broken pipe leaves the table in "being Loaded" state (Error 2652). The table cannot be queried or written to until the orphaned session times out (~20 min on trial).
- **Recovery from Error 2652:** Wait for idle timeout, then `DROP TABLE` and recreate. There is no `RELEASE LOCK` for FastLoad locks in Teradata.
- **Prefer batched-autocommit INSERT** on bandwidth-limited or kill-prone environments — it commits every N rows, never holds a FastLoad lock, and resumes from the table's current row count on restart.
```
