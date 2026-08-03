#!/bin/bash
# smrti status line for Claude Code
#
# Shows aggregate memory counts in the status bar.
# Receives session JSON on stdin, outputs one line of text.
#
# Configure in ~/.claude/settings.json:
#   "statusLine": {
#     "type": "command",
#     "command": "advaita-smrti/statusline.sh"
#   }
#
# Or project-level .claude/settings.local.json for per-project use.

input=$(cat)

# Parse session info from stdin
MODEL=$(echo "$input" | jq -r '.model.display_name // "Claude"')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

# Find memory directory — check project dir first, then cwd
PROJECT_DIR=$(echo "$input" | jq -r '.workspace.project_dir // empty')
MEMORY_DB=""

for candidate in "$PROJECT_DIR/.memory/index.db" ".memory/index.db"; do
    if [ -f "$candidate" ]; then
        MEMORY_DB="$candidate"
        break
    fi
done

# Build output
if [ -n "$MEMORY_DB" ] && command -v sqlite3 &>/dev/null; then
    # Query all counts in one call
    COUNTS=$(sqlite3 "$MEMORY_DB" "
        SELECT
            (SELECT COUNT(*) FROM tasks WHERE status = 'open'),
            (SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'),
            (SELECT COUNT(*) FROM tasks WHERE status = 'closed'),
            (SELECT COUNT(*) FROM facts),
            (SELECT COUNT(*) FROM decisions WHERE decided_at IS NOT NULL),
            (SELECT COUNT(*) FROM decisions WHERE decided_at IS NULL)
    " 2>/dev/null)

    if [ -n "$COUNTS" ]; then
        IFS='|' read -r OPEN WIP CLOSED FACTS DECIDED PENDING <<< "$COUNTS"

        # Build smrti segment
        SMRTI="smrti"

        # Tasks — show non-zero states
        TASK_PARTS=""
        [ "$OPEN" -gt 0 ] 2>/dev/null && TASK_PARTS="${TASK_PARTS}${OPEN} open"
        [ "$WIP" -gt 0 ] 2>/dev/null && {
            [ -n "$TASK_PARTS" ] && TASK_PARTS="${TASK_PARTS} · "
            TASK_PARTS="${TASK_PARTS}${WIP} active"
        }
        [ "$CLOSED" -gt 0 ] 2>/dev/null && {
            [ -n "$TASK_PARTS" ] && TASK_PARTS="${TASK_PARTS} · "
            TASK_PARTS="${TASK_PARTS}${CLOSED} done"
        }

        [ -n "$TASK_PARTS" ] && SMRTI="$SMRTI  ◇ $TASK_PARTS"

        # Facts
        [ "$FACTS" -gt 0 ] 2>/dev/null && SMRTI="$SMRTI  ◆ ${FACTS}f"

        # Decisions
        [ "$DECIDED" -gt 0 ] 2>/dev/null && SMRTI="$SMRTI  ⊙ ${DECIDED}d"
        [ "$PENDING" -gt 0 ] 2>/dev/null && SMRTI="$SMRTI  ○ ${PENDING}?"

        echo "$SMRTI  │  $MODEL ${PCT}%"
    else
        echo "smrti  │  $MODEL ${PCT}%"
    fi
else
    echo "$MODEL ${PCT}%"
fi
