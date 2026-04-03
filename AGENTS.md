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

| | Architect | Builder | Reviewer |
|---|-----------|---------|----------|
| **Role** | Senior Technical Lead | Senior Developer | Senior Code Reviewer |
| **Talks to user** | Yes | No | No |
| **Generates SQL** | No | Yes | No (describes fixes) |
| **Runs tq queries** | Yes (profiling + deploy) | No | No |
| **Reviews code** | No | Self-review only | Yes |
| **Deploys** | Yes (after user approval) | No | No |

### Skill Assignment

| Skill | Architect | Builder | Reviewer |
|-------|-----------|---------|----------|
| `data-product-design` | Yes | Yes | Yes |
| `teradata-sql` | No | Yes | Yes |
| `teradata-query` | Yes | No | No |

### The Brief-Build-Review Cycle

Every deliverable follows this cycle:

1. **Architect writes brief** → `handoff/ARCHITECT-BRIEF.md`
2. **Architect spawns Builder** → Builder reads brief, generates SQL, writes `handoff/REVIEW-REQUEST.md`
3. **Architect spawns Reviewer** → Reviewer reads diff + request, writes `handoff/REVIEW-FEEDBACK.md`
4. **If conditions** → Architect updates brief, re-spawns Builder
5. **If approved** → Architect deploys (with user approval), updates `handoff/BUILD-LOG.md`

## Six-Module Architecture

Each data product is composed of independently deployable modules, each with its own Teradata database (`{ProductName}_{Module}`):

| Module | Database Pattern | Purpose |
|--------|-----------------|---------|
| Memory | `{Name}_Memory` | Agent state, learning, and design documentation (Documentation Sub-Module) |
| Semantic | `{Name}_Semantic` | Metadata layer enabling agent discovery — the "map" of the data product |
| Domain | `{Name}_Domain` | Core business entities — source of truth |
| Observability | `{Name}_Observability` | Event tracking, quality monitoring, lineage |
| Search | `{Name}_Search` | Vector embeddings and similarity search |
| Prediction | `{Name}_Prediction` | Feature store and ML prediction storage |

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

## Agents

Agent definitions live in `.agents/agents/`. Each AI coding tool projects these into its own config (e.g., Claude Code symlinks `.claude/agents/` → `.agents/agents/`).

- **architect** — Senior Technical Lead. Gathers requirements, writes briefs, profiles sources (via tq), orchestrates Builder and Reviewer, owns deployment. Invoke with `@architect` or `claude --agent architect`.
- **builder** — Senior Developer. Generates Teradata SQL and documentation exactly as specified in the Architect's brief. Never talks to the user. Never executes queries.
- **reviewer** — Senior Code Reviewer. Validates Builder output against design standards, SQL conventions, and the brief. Binary judgments only (APPROVED / CONDITIONS / REJECTED). Never rewrites code.

## Handoff Protocol

Agents communicate through structured files in `handoff/` (gitignored, ephemeral). Templates live in `.agents/templates/handoff/`.

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `ARCHITECT-BRIEF.md` | Architect | Builder, Reviewer | Task spec, constraints, acceptance criteria |
| `REVIEW-REQUEST.md` | Builder | Reviewer, Architect | Files changed, self-review answers |
| `REVIEW-FEEDBACK.md` | Reviewer | Architect, Builder | Findings, conditions, verdict |
| `BUILD-LOG.md` | Architect | All | Cumulative record of deliverables and decisions |
| `SESSION-CHECKPOINT.md` | Architect | All | Session state for resuming across conversations |

## Build Workflow

The Architect drives an 8-deliverable sequence. Each deliverable goes through the Brief-Build-Review cycle.

| # | Deliverable | Architect | Builder | Reviewer |
|---|-------------|-----------|---------|----------|
| 1 | Requirements & Entity Map | Gather, confirm | — | — |
| 2 | Logical Data Model | Write brief | Generate ERD | — |
| 2.5 | Source Profiling | Run tq queries | — | — |
| 3 | Memory Module Schema | Brief | Generate DDL/views/INSERTs | Validate |
| 4 | Semantic Module Schema | Brief + seed specs | Generate DDL/views/seeds | Validate |
| 5 | Domain Module Schema | Brief + profiling | Generate DDL/views/indexes | Validate |
| 6 | Additional Modules | Brief per module | Generate per module | Validate per module |
| 7 | Integration & Docs | Brief patterns | Generate docs + joins | Validate completeness |
| 8 | Build Process Analysis | Brief + template | Generate from template | — |

## Project Rules

- **Three-agent workflow**: Always use the Architect agent to orchestrate builds. It spawns Builder and Reviewer as needed.
- **Design standards win**: They are the master source of truth. Never modify them unless explicitly authorized.
- **Scope lock**: Out-of-scope items go to BUILD-LOG.md Known Gaps — not into the current deliverable.
- **Nothing deploys without user approval**: Architect confirms environment and gets explicit go-ahead.
- **Source profiling before SQL**: Never generate Domain SQL without profiling source tables first.
- **File-based handoffs**: Agents communicate via `handoff/` files, not conversation.
