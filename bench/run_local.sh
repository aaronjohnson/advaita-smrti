#!/usr/bin/env bash
# bench/run_local.sh
#
# Run the Claude bench arms locally against your Max subscription.
# Gemini runs in GitHub Actions (see .github/workflows/bench.yml).
# Antigravity runs manually — fill in bench/results/antigravity_*_TEMPLATE.json
#
# Usage:
#   ./bench/run_local.sh              # run all local arms
#   ./bench/run_local.sh --arm baseline
#   ./bench/run_local.sh --arm smrti
#   ./bench/run_local.sh --score-only # score existing results without running
#
# Requirements:
#   - claude CLI in PATH and logged in (claude login)
#   - pip install "advaita-smrti[mcp]"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$REPO_ROOT/bench/results"
RUN_CLAUDE="$REPO_ROOT/bench/run_claude.py"
SCORE="$REPO_ROOT/bench/score.py"

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Colour

ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "${RED}✗${NC} $*"; }

# ── Parse args ────────────────────────────────────────────────────────────────
ARM=""
SCORE_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --arm)        ARM="$2"; shift 2 ;;
    --score-only) SCORE_ONLY=true;  shift ;;
    *)            err "Unknown argument: $1"; exit 1 ;;
  esac
done

# ── Preflight checks ──────────────────────────────────────────────────────────
echo ""
echo "smṛti-bench — local run"
echo "═══════════════════════"

if ! command -v claude &>/dev/null; then
  err "'claude' CLI not found. Install Claude Code and run 'claude login'."
  exit 1
fi
ok "claude CLI found: $(claude --version 2>/dev/null || echo 'version unknown')"

if ! command -v smrti-mcp &>/dev/null; then
  warn "'smrti-mcp' not found. smṛti arm will fail."
  warn "Run: pip install 'advaita-smrti[mcp]'"
else
  ok "smrti-mcp found"
fi

if ! command -v python3 &>/dev/null; then
  err "python3 not found."
  exit 1
fi

mkdir -p "$RESULTS_DIR"

# ── Score-only mode ───────────────────────────────────────────────────────────
if $SCORE_ONLY; then
  echo ""
  echo "Scoring existing results..."
  python3 "$SCORE" "$RESULTS_DIR" --format markdown
  exit 0
fi

# ── Run arms ──────────────────────────────────────────────────────────────────
run_arm() {
  local arm="$1"
  echo ""
  echo "── Running Claude Code arm: $arm ────────────────────────────────────"
  if python3 "$RUN_CLAUDE" --arm "$arm" --out "$RESULTS_DIR"; then
    ok "Arm '$arm' complete"
  else
    err "Arm '$arm' failed — check output above"
    return 1
  fi
}

if [[ -n "$ARM" ]]; then
  run_arm "$ARM"
else
  run_arm baseline
  run_arm smrti
fi

# ── Score ─────────────────────────────────────────────────────────────────────
echo ""
echo "── Scoring all results ──────────────────────────────────────────────────"
python3 "$SCORE" "$RESULTS_DIR" --format markdown | tee "$RESULTS_DIR/SCORES_local.md"
python3 "$SCORE" "$RESULTS_DIR" --format json > "$RESULTS_DIR/scores_local.json"
ok "Scores written to bench/results/SCORES_local.md"

# ── Offer to commit ───────────────────────────────────────────────────────────
echo ""
echo "── Commit results? ──────────────────────────────────────────────────────"
read -rp "Commit and push bench/results/ to origin/sutra? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  cd "$REPO_ROOT"
  git add bench/results/
  TIMESTAMP=$(date -u +%Y-%m-%dT%H:%MZ)
  git commit -m "bench: local claude arms ${TIMESTAMP}"
  git push origin sutra
  ok "Pushed — GitHub Action will rescore and include Gemini results."
else
  warn "Results not committed. Run 'git add bench/results/ && git commit' when ready."
fi

echo ""
ok "Done."
