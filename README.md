# AI-Native Data Product Builder

An agentic framework for building AI-Native Data Products on Teradata. Uses the [AI-Native Data Product Design Standards](https://github.com/NathanG-TD/ai-native-data-products) as the single source of truth and agentic prompts to orchestrate multi-module data product design and deployment.

## 3-Tier Git Architecture

This framework functions as an orchestrator across three cleanly-separated Git repositories:
1. **Agentic Framework (Here)**: The primary repo housing the agent prompts, skills, and orchestrator scripts.
2. **Reference Architecture**: The `design-standards/` git submodule serving as the read-only, master source of truth.
3. **User Workspace**: The `workspace/` directory, initialized dynamically as an independent Git repository that tracks your generated data products (`workspace/src/` and `workspace/docs/`).

## Framework-Agnostic Design

This repo is tool-agnostic. It follows the [AGENTS.md](https://github.com/anthropics/agents-md) and [Agent Skills](https://agentskills.io) open standards so you can use your preferred AI coding tool:

| Tool | Setup |
|------|-------|
| **Claude Code** | `make setup` |
| **Cursor** | `make setup-design-standards && make setup-cursor` |
| **Codex** | `make setup-design-standards` (reads `AGENTS.md` natively) |
| **Other** | Read `AGENTS.md` for project context; reference `.agents/prompts/` for agentic workflows |

## Project Structure

```
AGENTS.md                ← Framework-agnostic project instructions
.agents/
  prompts/               ← Portable agentic prompts (tool-agnostic)
  skills/                ← Skill wrappers (frontmatter + import from prompts)
design-standards/        ← 8 design standard docs (cloned — master source of truth)
scripts/                 ← Deployment, sanitization, and tooling scripts
workspace/src/           ← Produced data product source code (per product, per module)
workspace/docs/          ← Produced data product documentation and release notes
config/                  ← Connection configurations for your specific project
Makefile                 ← Setup automation
```

## Tool customisation
We provide a Makefile (see next section) to setup the project for different AI coding tools.
For example, for Claude Code, you get:
```
.claude/                 ← Claude Code specific (symlinks + pointer to AGENTS.md)
.claude/CLAUDE.md        ← Simply "@../AGENTS.md"
```

## Getting Started

```bash
# 1. Clone this repo
git clone <this-repo-url> && cd ai-native-data-products

# 2. Full setup (clones design standards, configures tool, and initializes local workspace)
# Optionally, link the workspace to a remote data-products repository:
make setup [REMOTE=https://github.com/your-org/data-products.git]

# Use these if you are not using Claude Code:
# make setup-cursor
# make setup-codex

# 3. Build a data product
# In Claude Code:  /data-product-build [product-name]
# In other tools:  reference .agents/prompts/data-product-build.md
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make setup [REMOTE=...]` | Full setup: clone design standards + configure Claude Code + init local workspace (with optional remote) |
| `make setup-design-standards` | Clone or update design standards from upstream |
| `make setup-claude` | Create `.claude/` symlinks and CLAUDE.md pointer |
| `make setup-cursor` | Generate `.cursorrules` from AGENTS.md |
| `make setup-codex` | No-op (Codex reads AGENTS.md natively) |
| `make setup-workspace` | Initializes `workspace/` or sets up a remote for tracking generated files |
| `make clean-design-standards` | Remove cloned design standards |
| `make help` | Show all targets |

## Agentic Prompts

Portable prompts in `.agents/prompts/`:

| Prompt | Purpose |
|--------|---------|
| `data-product-build.md` | End-to-end build orchestration (7-deliverable sequence) |
| `data-product-design.md` | Individual module design applying design standards |
| `data-product-use.md` | Discover and query a deployed data product |
| `teradata-sql.md` | SQL generation & validation conventions |
| `teradata-query.md` | Query execution via the tq CLI tool |