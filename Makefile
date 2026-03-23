DESIGN_STANDARDS_REPO := https://github.com/NathanG-TD/ai-native-data-products.git
DESIGN_STANDARDS_DIR  := design-standards

.PHONY: setup setup-claude setup-cursor setup-codex setup-design-standards clean-design-standards help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-25s %s\n", $$1, $$2}'

setup: setup-design-standards setup-claude ## Full setup (design standards + Claude Code)

setup-design-standards: ## Clone design standards from upstream
	@if [ -d "$(DESIGN_STANDARDS_DIR)/.git" ]; then \
		echo "Updating design standards..."; \
		git -C $(DESIGN_STANDARDS_DIR) pull --ff-only; \
	else \
		echo "Cloning design standards..."; \
		rm -rf $(DESIGN_STANDARDS_DIR); \
		git clone $(DESIGN_STANDARDS_REPO) $(DESIGN_STANDARDS_DIR); \
	fi

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
	@if [ ! -f .claude/CLAUDE.md ]; then \
		echo '@../AGENTS.md' > .claude/CLAUDE.md; \
		echo "  Created .claude/CLAUDE.md"; \
	else \
		echo "  .claude/CLAUDE.md already exists"; \
	fi
	@echo "Claude Code ready."

setup-cursor: ## Set up Cursor (.cursorrules from AGENTS.md)
	@cp AGENTS.md .cursorrules
	@echo "Generated .cursorrules from AGENTS.md"

setup-codex: ## Set up Codex (no-op, reads AGENTS.md natively)
	@echo "Codex reads AGENTS.md natively — no setup needed."

clean-design-standards: ## Remove cloned design standards
	rm -rf $(DESIGN_STANDARDS_DIR)
