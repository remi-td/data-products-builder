# Change Request: teradata-source-image skill

**Source skill:** `.agents/skills/teradata-source-image/SKILL.md`  
**Derived from:** generic source-image build
**Status:** Ready to submit

---

## CR-1: Batched-Autocommit Loader (Prefer over FastLoad on Flaky Connections)

**Insert before `## Hard Rules`**

**Motivation:** In the redeployment session, the process harness killed the background FastLoad mid-flight, and a 10-minute foreground timeout killed a retry. Both left `stg_arrestee` in Error 2652 "being Loaded" state. The fix was to DROP+recreate the table and switch to a batched-autocommit loader that commits every 10K rows and resumes from the target's current row count. This pattern should be the default recommendation for trial and bandwidth-limited environments.

**Text to add:**

```markdown
## Batched-Autocommit Loader (Prefer over FastLoad on Flaky Connections)

On environments where connections may drop mid-flight (trial instances, VPN tunnels, bandwidth-limited networks), prefer the **batched-autocommit INSERT** pattern over FastLoad:

| Concern | FastLoad (`{fn teradata_try_fastload}`) | Batched-Autocommit INSERT |
|---------|----------------------------------------|--------------------------|
| Mid-flight kill | Orphans table lock (Error 2652) | Commits every N rows — safe to interrupt |
| Resumability | None — must DROP+recreate table | `SELECT COUNT(*)` from target, skip that many source rows |
| Throughput | Higher (ML protocol) | Lower but acceptable for ≤ 1 MB/s wire |
| FastLoad slot requirement | Yes | None |

When using the batched-autocommit pattern, always:
1. Open one connection **per entity** (not shared across entities)
2. Set `autocommit = True` — each `executemany` batch is its own committed transaction
3. On restart, `SELECT COUNT(*)` from the target table, then skip that many leading rows from the source file

Reference implementation: `workspace/src/{product-name}/scripts/load_staging_resume.py`
```

---

## CR-2: Column Count Derivation — Always Read the File Header

**Insert before `## Hard Rules`** (after CR-1)

**Motivation:** The redeployment brief stated 268/269 columns for Arrestee/Offender. The actual TSV file headers showed 363/381. DDL generated from the wrong count produced a column mismatch on INSERT-SELECT. Additionally, the RTK shell proxy that wraps CLI commands in this project corrupts the output of `wc -l`, `head -N`, `awk`, and `cut` on large files — Python must be used instead.

**Text to add:**

```markdown
## Column Count Derivation — Always Read the File Header

Never assume column counts from codebooks, data dictionaries, or architect briefs. Column counts must always be derived from the **actual source file header**:

```python
with open(tsv_path, encoding="latin-1") as fh:
    header = fh.readline().rstrip("\r\n").split("\t")
ncols = len(header)
```

Codebook counts frequently reflect a schema version that differs from the actual extract. For example, in one data product build, the brief stated 268/269 columns for certain staging tables; the actual TSV headers showed 363/381. DDL generated from the wrong count fails on INSERT-SELECT with a column mismatch error.

**Important:** Do not use shell tools (`wc -l`, `head -N`, `awk`, `cut`) on large TSV files when the RTK shell proxy is active — it corrupts multi-line output. Use Python for all header inspection and row counting on data files.
```
