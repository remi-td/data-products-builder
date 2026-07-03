# AGENTS.md

This file provides guidance to AI coding agents working with code in this repository.

## What This Is

This agentic system automates the creation of AI-Native Data Products on Teradata. It uses design standards as the single source of truth and a three-agent team (Architect, Builder, Reviewer) to orchestrate multi-module data product design and deployment.

## 3-Tier Git Architecture

This framework interacts with three separate Git repositories to isolate reference material, the agentic engine, and output artifacts:

1. **Agentic Framework (Here)**: The primary repo housing the agents, skills, and orchestrator scripts.
2. **Reference Architecture**: The `design-standards/` git submodule serving as the read-only, master source of truth.
3. **User Workspace**: The `workspace/` directory, an independent Git repository containing all generated artifacts (`workspace/src/` and `workspace/docs/`).

## Three-Agent Architecture

Builds follow the **three-man-team** pattern: three agents with distinct roles, strict boundaries, and file-based handoffs. The user is the Project Owner.

```
User (Project Owner)
  │
  ▼
Architect ──brief──▶ Builder ──review-request──▶ Reviewer
  ▲                                                  │
  └──────────────── feedback ────────────────────────┘
```

### Roles

|                     | Architect                 | Builder          | Reviewer             |
| ------------------- | ------------------------- | ---------------- | -------------------- |
| **Role**            | Senior Technical Lead     | Senior Developer | Senior Code Reviewer |
| **Talks to user**   | Yes                       | No               | No                   |
| **Generates SQL**   | No                        | Yes              | No (describes fixes) |
| **Runs tq queries** | Yes (profiling + deploy)  | No               | No                   |
| **Reviews code**    | No                        | Self-review only | Yes                  |
| **Deploys**         | Yes (after user approval) | No               | No                   |

### Skill Assignment

| Skill                 | Architect | Builder | Reviewer |
| --------------------- | --------- | ------- | -------- |
| `data-product-design` | Yes       | Yes     | Yes      |
| `teradata-sql`        | No        | Yes     | Yes      |
| `teradata-query`      | Yes       | No      | No       |
| `dpds-generate`       | Yes       | No      | No       |

### The Brief-Build-Review Cycle

Every deliverable follows this cycle:

1. **Architect writes brief** → `handoff/ARCHITECT-BRIEF.md`
2. **Architect spawns Builder** → Builder reads brief, generates SQL, writes `handoff/REVIEW-REQUEST.md`
3. **Architect spawns Reviewer** → Reviewer reads diff + request, writes `handoff/REVIEW-FEEDBACK.md`
4. **If conditions** → Architect updates brief, re-spawns Builder
5. **If approved** → Architect deploys (with user approval), updates `handoff/BUILD-LOG.md`

## Six-Module Architecture

Each data product is composed of independently deployable modules, each with its own Teradata database (`{ProductName}_{Module}`):

| Module        | Database Pattern       | Purpose                                                                    |
| ------------- | ---------------------- | -------------------------------------------------------------------------- |
| Memory        | `{Name}_Memory`        | Agent state, learning, and design documentation (Documentation Sub-Module) |
| Semantic      | `{Name}_Semantic`      | Metadata layer enabling agent discovery — the "map" of the data product    |
| Domain        | `{Name}_Domain`        | Core business entities — source of truth                                   |
| Observability | `{Name}_Observability` | Event tracking, quality monitoring, lineage                                |
| Search        | `{Name}_Search`        | Vector embeddings and similarity search                                    |
| Prediction    | `{Name}_Prediction`    | Feature store and ML prediction storage                                    |

**Deployment order matters**: Phase 1 (Memory + Semantic) → Phase 2 (Domain + Observability) → Phase 3 (Search + Prediction). Memory and Semantic must exist before any other module deploys.

**Design standards (in `design-standards/design-standards/`) are the master source of truth.** The `design-standards/` directory is a git submodule; the actual `.md` files are one level deeper. When conflicts arise, design standards win.

## Project Structure

```
AGENTS.md                            ← Framework-agnostic project instructions (this file)
.agents/
  agents/                            ← Portable agent definitions (architect, builder, reviewer)
  skills/                            ← Portable agentic skills (tool-agnostic)
  templates/                         ← Requirements, build-process, and handoff templates
    handoff/                         ← Templates for agent-to-agent communication files
design-standards/design-standards/   ← 8 design standard .md files (git submodule, nested path)
scripts/                             ← Deployment, sanitization, and tooling scripts
workspace/src/                       ← Data product source code (per product, per module)
workspace/docs/                      ← Data product documentation and release notes
config/                              ← Connection configurations (gitignored credentials)
handoff/                             ← Runtime handoff files (gitignored, ephemeral per-session)
.claude/                             ← Claude Code config (symlinks to .agents/agents/ and .agents/skills/)
```

## Skills

Reusable agentic skills live in `.agents/skills/`. These are tool-agnostic — each AI coding tool can consume them via its own integration mechanism.

- **data-product-design** — Module architecture, design standards, documentation capture protocol.
- **teradata-sql** — Teradata DDL/DML syntax rules, conventions, and 27-item validation checklist.
- **teradata-query** — tq CLI tool for executing queries against Teradata.
- **dpds-generate** — Generates a living Open Data Mesh DPDS 1.0.0 descriptor document by querying the product's Semantic and Memory modules.

## Agents

Agent definitions live in `.agents/agents/`. Each AI coding tool projects these into its own config (e.g., Claude Code symlinks `.claude/agents/` → `.agents/agents/`).

- **architect** — Senior Technical Lead. Gathers requirements, writes briefs, profiles sources (via tq), orchestrates Builder and Reviewer, owns deployment. Invoke with `@architect` or `claude --agent architect`.
- **builder** — Senior Developer. Generates Teradata SQL and documentation exactly as specified in the Architect's brief. Never talks to the user. Never executes queries.
- **reviewer** — Senior Code Reviewer. Validates Builder output against design standards, SQL conventions, and the brief. Binary judgments only (APPROVED / CONDITIONS / REJECTED). Never rewrites code.

## Handoff Protocol

Agents communicate through structured files in `handoff/` (gitignored, ephemeral). Templates live in `.agents/templates/handoff/`.

| File                    | Written By | Read By             | Purpose                                         |
| ----------------------- | ---------- | ------------------- | ----------------------------------------------- |
| `ARCHITECT-BRIEF.md`    | Architect  | Builder, Reviewer   | Task spec, constraints, acceptance criteria     |
| `REVIEW-REQUEST.md`     | Builder    | Reviewer, Architect | Files changed, self-review answers              |
| `REVIEW-FEEDBACK.md`    | Reviewer   | Architect, Builder  | Findings, conditions, verdict                   |
| `BUILD-LOG.md`          | Architect  | All                 | Cumulative record of deliverables and decisions |
| `SESSION-CHECKPOINT.md` | Architect  | All                 | Session state for resuming across conversations |

## Build Workflow

The Architect drives an 8-deliverable sequence. Each deliverable goes through the Brief-Build-Review cycle.

| #   | Deliverable                       | Architect                    | Builder                    | Reviewer              |
| --- | --------------------------------- | ---------------------------- | -------------------------- | --------------------- |
| 1   | Requirements & Entity Map         | Gather, confirm              | —                          | —                     |
| 2   | Logical Data Model                | Write brief                  | Generate ERD               | —                     |
| 2.5 | Source Profiling                  | Run tq queries               | —                          | —                     |
| 3   | Memory Module Schema              | Brief                        | Generate DDL/views/INSERTs | Validate              |
| 4   | Semantic Module Schema            | Brief + seed specs           | Generate DDL/views/seeds   | Validate              |
| 5   | Domain Module Schema              | Brief + profiling            | Generate DDL/views/indexes | Validate              |
| 6   | Additional Modules                | Brief per module             | Generate per module        | Validate per module   |
| 7   | Integration & Docs                | Brief patterns               | Generate docs + joins      | Validate completeness |
| 7.5 | Create DPDS Descriptor (Optional) | Invoke `dpds-generate` skill | —                          | —                     |
| 8   | Build Process Analysis            | Brief + template             | Generate from template     | —                     |

### Deliverable 7.5 — Create DPDS Descriptor (Optional)

If the customer is using Open Data Mesh or requires DPDS-compliant descriptors,
run the `dpds-generate` skill after Deliverable 7 is complete and the data product is deployed. 

The Architect runs this directly — no Builder or Reviewer cycle is needed as the output is derived entirely from live metadata. 

Output: `workspace/docs/{product-name}/dpds-descriptor.json`. 

This prompt can also be re-run independently at any time to refresh the descriptor after product changes.

### Deliverable 8 — Build Process Analysis (MANDATORY)

**This deliverable CANNOT be skipped.** It is the formal closing step of every build. Even if the user says "go all the way" or "proceed without stopping", Deliverable 8 must still be generated before the build is considered complete.

After the data product is deployed and validated, generate a build process analysis document using the template at `.agents/templates/build-process-template.md`. Save it to `workspace/docs/{product-name}/build-process.md`.

This document is for technical reviewers and captures:

- **What was built** — artifact inventory (databases, tables, views, features, indexes, documentation records)
- **How it was built** — Mermaid diagrams showing agent orchestration, deployment sequence with error locations, data lineage, and semantic discovery graph. **Mermaid syntax rules**: (1) subgraph IDs must be simple identifiers with no spaces or colons — use `subgraph P0[Phase 0 - Setup]` not `subgraph "Phase 0: Setup"`; (2) edge labels must have NO space between arrow and pipe — use `-->|label|` not `--> |label|`; (3) node labels must not contain special characters like `!!`, unescaped quotes, or colons; (4) use hyphens instead of colons in labels
- **Skill and tool usage** — which skills were explicitly invoked vs applied implicitly, tool call counts by phase, and the detailed call flow tree
- **Errors and fixes** — every deployment error, root cause, fix applied, and whether it was codified back into a skill
- **Process timeline** — effort distribution across discovery, generation, deployment, documentation, and skill optimization
- **Improvement opportunities** — actionable recommendations for process and tooling (not data logic)

This deliverable also includes updating skills with any new lessons learned during the build (Teradata syntax issues, deployment gotchas, tool usage patterns). If errors occurred that are not yet covered by the `teradata-sql` or `teradata-query` skills, add them.

## Deployment Execution Rules

1. **Create all databases first** — one `CREATE DATABASE` per module, all can run in parallel.
2. **Grant cross-database permissions immediately after creating databases** — any module whose views reference another module's tables needs `GRANT SELECT ON source_db TO target_db WITH GRANT OPTION`. Do this before deploying any SQL.
3. **Sanitize all SQL files** before execution: `scripts/sanitize-sql.sh workspace/src/{product-name}/**/*.sql`
4. **Deploy sequentially within each phase** — tables must complete before views, views before seed data, seed data before documentation. Never run dependent files in parallel or in the background.
5. **Verify data counts** after each phase completes — query `_Current` views and reference tables.
6. **Use REPLACE VIEW** (not CREATE VIEW) when redeploying to handle "already exists" errors gracefully.

### Deployment File Execution Sequence

Execute files in numbered order within each module, modules in phase order. Use the **teradata-query** skill to run each file.

```
Phase 1 — Memory + Semantic (must complete before Phase 2):
  workspace/src/{product}/01-memory/01-tables.sql
  workspace/src/{product}/01-memory/02-views.sql
  workspace/src/{product}/01-memory/03-documentation.sql
  workspace/src/{product}/02-semantic/01-tables.sql
  workspace/src/{product}/02-semantic/02-views.sql
  workspace/src/{product}/02-semantic/03-seed-data.sql
  workspace/src/{product}/02-semantic/04-documentation.sql

Phase 2 — Domain + Observability (must complete before Phase 3):
  workspace/src/{product}/03-domain/01-tables.sql
  workspace/src/{product}/03-domain/02-views.sql
  workspace/src/{product}/03-domain/03-indexes.sql
  workspace/src/{product}/03-domain/04-reference-data.sql
  workspace/src/{product}/03-domain/05-documentation.sql

Phase 3 — Search + Prediction (if in scope):
  workspace/src/{product}/04-search/01-tables.sql
  ...
  workspace/src/{product}/05-prediction/01-tables.sql
  ...
```

### Post-Deployment Validation

After each phase, verify the deployment:

```sql
-- After Phase 1: Confirm Semantic module registry
SELECT module_name, database_name, deployment_status
FROM {Product}_Semantic.data_product_map WHERE is_active = 1;

-- After Phase 2: Confirm Domain data loaded
SELECT 'entity_name' AS entity, COUNT(*) AS cnt FROM {Product}_Domain.{Entity}_Current;

-- End-to-end: Test multi-hop path discovery
SELECT hop_count, path_tables, path_joins
FROM {Product}_Semantic.v_relationship_paths
WHERE source_table = '{TableA}' AND target_table = '{TableB}'
ORDER BY hop_count;
```

## Output Structure

For each data product, create:

```
workspace/src/{product-name}/
  {nn}-{module}/          # SQL files per module, numbered by deploy order
    {nn}-{object}.sql     # Individual DDL/DML files
workspace/docs/{product-name}/
  requirements.md         # Deliverable 1-2
  design-decisions.md     # Architecture decisions
  build-process.md        # Deliverable 8 — build process analysis (MANDATORY)
```

Update `workspace/docs/releases.md` and `workspace/docs/lessons-learned.md` when a data product reaches deployment.

## Project Rules

- **Three-agent workflow**: Always use the Architect agent to orchestrate builds. It spawns Builder and Reviewer as needed.
- **Design standards win**: They are the master source of truth. Never modify them unless explicitly authorized.
- **Scope lock**: Out-of-scope items go to BUILD-LOG.md Known Gaps — not into the current deliverable.
- **Nothing deploys without user approval**: Architect confirms environment and gets explicit go-ahead.
- **Source profiling before SQL**: Never generate Domain SQL without profiling source tables first.
- **File-based handoffs**: Agents communicate via `handoff/` files, not conversation.
