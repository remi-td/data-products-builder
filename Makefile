DESIGN_STANDARDS_REPO := https://github.com/NathanG-TD/ai-native-data-products.git
DESIGN_STANDARDS_DIR  := design-standards

.PHONY: setup setup-claude setup-cursor setup-codex setup-design-standards setup-workspace clean-design-standards help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-25s %s\n", $$1, $$2}'

setup: setup-design-standards setup-claude setup-workspace ## Full setup (design standards + Claude Code + workspace)

setup-design-standards: ## Clone design standards from upstream
	@if [ -d "$(DESIGN_STANDARDS_DIR)/.git" ]; then \
		echo "Updating design standards..."; \
		git -C $(DESIGN_STANDARDS_DIR) pull --ff-only; \
	else \
		echo "Cloning design standards..."; \
		rm -rf $(DESIGN_STANDARDS_DIR); \
		git clone $(DESIGN_STANDARDS_REPO) $(DESIGN_STANDARDS_DIR); \
	fi

setup-workspace: ## Configure workspace (usage: make setup-workspace [WORKSPACE_REPO=https://...])
	@URL="$(WORKSPACE_REPO)"; \
	if [ -z "$$URL" ]; then URL="$(REMOTE)"; fi; \
	if [ ! -d "workspace" ]; then \
		if [ -n "$$URL" ]; then \
			echo "Cloning workspace repository from $$URL..."; \
			git clone "$$URL" workspace; \
		else \
			echo "Initializing local workspace..."; \
			mkdir -p workspace/src workspace/docs; \
			cd workspace && git init; \
			if [ ! -f "README.md" ]; then echo "# Data Products Workspace" > README.md; fi; \
			git add . && git commit -m "Initial commit" || true; \
		fi; \
	elif [ ! -d "workspace/.git" ]; then \
		echo "Initializing git repository in existing workspace directory..."; \
		cd workspace && git init; \
		if [ -n "$$URL" ]; then git remote add origin "$$URL"; fi; \
	elif [ -n "$$URL" ]; then \
		echo "Setting remote $$URL in workspace..."; \
		cd workspace && git remote set-url origin "$$URL" 2>/dev/null || git remote add origin "$$URL"; \
	fi
	@echo "Workspace is ready at ./workspace"

setup-claude: ## Set up Claude Code (symlinks + CLAUDE.md + handoff dir)
	@mkdir -p .claude
	@if [ -L .claude/skills ]; then \
		echo "  .claude/skills symlink already exists"; \
	elif [ -d .claude/skills ]; then \
		echo "  WARNING: .claude/skills is a real directory, replacing with symlink"; \
		rm -rf .claude/skills; \
		ln -s ../.agents/skills .claude/skills; \
	else \
		ln -s ../.agents/skills .claude/skills; \
	fi
	@echo "  .claude/skills -> .agents/skills"
	@if [ -L .claude/agents ]; then \
		echo "  .claude/agents symlink already exists"; \
	elif [ -d .claude/agents ]; then \
		echo "  WARNING: .claude/agents is a real directory, replacing with symlink"; \
		rm -rf .claude/agents; \
		ln -s ../.agents/agents .claude/agents; \
	else \
		ln -s ../.agents/agents .claude/agents; \
	fi
	@echo "  .claude/agents -> .agents/agents"
	@if [ ! -f CLAUDE.md ]; then \
		echo '@AGENTS.md' > CLAUDE.md; \
		echo "  Created CLAUDE.md at root"; \
	else \
		echo "  CLAUDE.md already exists at root"; \
	fi
	@if [ ! -f .claudeignore ]; then \
		echo ".agents/" > .claudeignore; \
		echo "  Created .claudeignore to prevent double-scanning of .agents/"; \
	else \
		if ! grep -q "^.agents/" .claudeignore; then \
			echo ".agents/" >> .claudeignore; \
			echo "  Added .agents/ to .claudeignore"; \
		fi \
	fi
	@mkdir -p handoff
	@echo "  handoff/ directory ready"
	@echo "Claude Code ready."

setup-cursor: ## Set up Cursor (.cursorrules from AGENTS.md)
	@cp AGENTS.md .cursorrules
	@echo "Generated .cursorrules from AGENTS.md"

setup-codex: ## Set up Codex (no-op, reads AGENTS.md natively)
	@echo "Codex reads AGENTS.md natively — no setup needed."

clean-design-standards: ## Remove cloned design standards
	rm -rf $(DESIGN_STANDARDS_DIR)
