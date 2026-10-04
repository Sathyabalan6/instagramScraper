#!/usr/bin/env bash
# ==============================================================================
# Checkups Skill Installer
# Compatible with Google Antigravity, Claude Code, Cursor, and local installation
# ==============================================================================

set -e

# Determine the skill directory and name
SKILL_DIR="$(pwd)"
SKILL_NAME="$(basename "$SKILL_DIR")"
PARENT_DIR="$(dirname "$SKILL_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

usage() {
  echo -e "${BOLD}Checkups Skill Installer${NC}"
  echo ""
  echo "Usage: ./install.sh [options]"
  echo ""
  echo "Options:"
  echo "  -t, --target <env>     Target environment: antigravity (default), claude, cursor, local"
  echo "  -d, --dry-run          Simulate installation without copying files"
  echo "  -h, --help             Show this help message"
  echo ""
  echo "Target Directories:"
  echo "  • antigravity: ~/.gemini/config/skills/"
  echo "  • claude:      ~/.claude/skills/"
  echo "  • cursor:      ~/.cursor/skills/"
  echo "  • local:       ../.agents/skills/ (relative to the skill directory)"
  echo ""
  exit 0
}

while [[ "$#" -gt 0 ]]; do
  case $1 in
    -t|--target) TARGET_ENV="$2"; shift ;;
    -d|--dry-run) DRY_RUN=true ;;
    -h|--help) usage ;;
    *) echo -e "${RED}Unknown option: $1${NC}"; usage ;;
  esac
  shift
done

# Resolve destination directory
case $TARGET_ENV in
  antigravity)
    DEST_DIR="$HOME/.gemini/config/skills"
    ;;
  claude)
    DEST_DIR="$HOME/.claude/skills"
    ;;
  cursor)
    DEST_DIR="$HOME/.cursor/skills"
    ;;
  local)
    DEST_DIR="$(dirname "$SKILL_DIR")/.agents/skills"
    ;;
  *)
    echo -e "${RED}Invalid target environment: $TARGET_ENV${NC}"
    exit 1
    ;;
esac

# Make destination directory absolute if it's relative
if [[ "$DEST_DIR" != /* ]]; then
    DEST_DIR="$(pwd)/$DEST_DIR"
fi

# Check if destination is inside the source directory to avoid self-copy
if [[ "$DEST_DIR" == "$SKILL_DIR"* ]]; then
    echo -e "${RED}Error: Installation target is inside the source directory.${NC}"
    echo -e "This can happen when installing to a subdirectory of the skill directory."
    echo -e "Please choose a different target (e.g., use --target antigravity, claude, cursor, or a different local path)."
    exit 1
fi

SRC_PATH="$SKILL_DIR"
TARGET_PATH="$DEST_DIR/$SKILL_NAME"

if [[ "$DRY_RUN" == false ]]; then
    mkdir -p "$DEST_DIR"
fi

if [[ "$DRY_RUN" == true ]]; then
    echo -e "  [${YELLOW}PLAN${NC}] Would install: ${BOLD}$SKILL_NAME${NC} -> $TARGET_PATH"
else
    rm -rf "$TARGET_PATH"
    cp -r "$SRC_PATH" "$TARGET_PATH"
    echo -e "  [${GREEN}INSTALLED${NC}] ${BOLD}$SKILL_NAME${NC}"
fi

echo ""
if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}Dry run completed successfully.${NC}"
else
    echo -e "${GREEN}${BOLD}✔ $SKILL_NAME successfully installed to $DEST_DIR!${NC}"
    echo -e "Your AI coding agent will discover it automatically."
fi
