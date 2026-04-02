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

setup-workspace: ## Configure the workspace tracking your tools (usage: make setup-workspace [REMOTE=https://...])
	@if [ ! -d "workspace/.git" ]; then \
		echo "Initializing local workspace..."; \
		mkdir -p workspace/src workspace/docs; \
		cd workspace && git init; \
		if [ ! -f "README.md" ]; then echo "# Data Products Workspace" > README.md; fi; \
		git add . && git commit -m "Initial commit" || true; \
	fi
	@if [ -n "$(REMOTE)" ]; then \
		echo "Adding remote $(REMOTE) to workspace..."; \
		cd workspace && git remote set-url origin $(REMOTE) 2>/dev/null || git remote add origin $(REMOTE); \
	fi
	@echo "Workspace is ready at ./workspace"

setup-claude: ## Set up Claude Code (symlinks + CLAUDE.md)
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
	@echo "Claude Code ready."

setup-cursor: ## Set up Cursor (.cursorrules from AGENTS.md)
	@cp AGENTS.md .cursorrules
	@echo "Generated .cursorrules from AGENTS.md"

setup-codex: ## Set up Codex (no-op, reads AGENTS.md natively)
	@echo "Codex reads AGENTS.md natively — no setup needed."

clean-design-standards: ## Remove cloned design standards
	rm -rf $(DESIGN_STANDARDS_DIR)
