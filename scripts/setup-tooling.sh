#!/usr/bin/env bash
# setup-tooling.sh — Generate tool-specific configurations from .agents/
#
# Usage:
#   scripts/setup-tooling.sh --claude    # Validate Claude Code setup
#   scripts/setup-tooling.sh --cursor    # Generate .cursorrules
#   scripts/setup-tooling.sh --codex     # Info for Codex (reads AGENTS.md natively)
#   scripts/setup-tooling.sh --all       # All of the above
#   scripts/setup-tooling.sh             # Show help

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

setup_claude() {
    echo ""
    echo "=== Claude Code ==="

    local errors=0

    if [[ -f "$PROJECT_ROOT/.claude/CLAUDE.md" ]]; then
        ok "CLAUDE.md exists"
    else
        fail "Missing .claude/CLAUDE.md"
        errors=$((errors + 1))
    fi

    # Check that CLAUDE.md imports AGENTS.md
    if grep -q '@../AGENTS.md' "$PROJECT_ROOT/.claude/CLAUDE.md" 2>/dev/null; then
        ok "CLAUDE.md imports AGENTS.md"
    else
        warn "CLAUDE.md does not import AGENTS.md — add '@../AGENTS.md' to it"
    fi

    # Check skills live in .agents/skills/ and are symlinked
    local skill_count=0
    for skill_dir in "$PROJECT_ROOT"/.agents/skills/*/; do
        if [[ -f "${skill_dir}SKILL.md" ]]; then
            skill_count=$((skill_count + 1))
        fi
    done
    ok "$skill_count skills found in .agents/skills/"

    # Check .claude/skills symlink
    if [[ -L "$PROJECT_ROOT/.claude/skills" ]]; then
        ok ".claude/skills is a symlink to .agents/skills"
    elif [[ -d "$PROJECT_ROOT/.claude/skills" ]]; then
        warn ".claude/skills is a directory, not a symlink — run: ln -sf ../.agents/skills .claude/skills"
    else
        warn "Missing .claude/skills symlink — run: ln -sf ../.agents/skills .claude/skills"
    fi

    if [[ $errors -eq 0 ]]; then
        ok "Claude Code setup is valid"
    else
        fail "$errors issues found"
    fi
}

setup_cursor() {
    echo ""
    echo "=== Cursor ==="

    local output="$PROJECT_ROOT/.cursorrules"

    # Generate .cursorrules from AGENTS.md
    if [[ -f "$PROJECT_ROOT/AGENTS.md" ]]; then
        cp "$PROJECT_ROOT/AGENTS.md" "$output"
        ok "Generated .cursorrules from AGENTS.md"
        echo "    Cursor will load this as project-level instructions."
        echo "    To add prompts, paste content from .agents/prompts/ into Cursor's context."
    else
        fail "AGENTS.md not found — cannot generate .cursorrules"
    fi
}

setup_codex() {
    echo ""
    echo "=== Codex / OpenAI ==="

    if [[ -f "$PROJECT_ROOT/AGENTS.md" ]]; then
        ok "AGENTS.md exists — Codex reads it natively"
        echo "    No additional setup needed."
        echo "    Reference .agents/prompts/ files as context when needed."
    else
        fail "AGENTS.md not found"
    fi
}

show_help() {
    echo "setup-tooling.sh — Generate tool-specific configs from AGENTS.md"
    echo ""
    echo "Usage:"
    echo "  scripts/setup-tooling.sh --claude    Validate Claude Code setup"
    echo "  scripts/setup-tooling.sh --cursor    Generate .cursorrules"
    echo "  scripts/setup-tooling.sh --codex     Info for Codex"
    echo "  scripts/setup-tooling.sh --all       All of the above"
    echo ""
    echo "This project uses AGENTS.md as the framework-agnostic source of truth."
    echo "Portable prompts live in .agents/prompts/."
    echo "Tool-specific wrappers are generated or maintained in tool directories (.claude/, etc.)."
}

if [[ $# -eq 0 ]]; then
    show_help
    exit 0
fi

for arg in "$@"; do
    case "$arg" in
        --claude) setup_claude ;;
        --cursor) setup_cursor ;;
        --codex)  setup_codex ;;
        --all)
            setup_claude
            setup_cursor
            setup_codex
            ;;
        --help|-h) show_help ;;
        *)
            fail "Unknown option: $arg"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

echo ""
ok "Done."
