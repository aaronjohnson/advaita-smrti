# RFC 001: Beads, Quint, and Synthesis Integration

**Status:** Implemented (v0.3.0)
**Author:** Aaron Johnson
**Created:** 2026-02-05
**Implemented:** 2026-02-05
**Branch:** `rfc/beads-quint-synthesis`

## Decisions (resolved during implementation)

1. **Beads/quint as inspiration, not dependency.** RFC 002 implemented
   the patterns in pure Python rather than depending on beads CLI or
   quint MCP server. Same concepts (task graphs, decision trails,
   synthesis), zero external dependencies.

2. **SQLite kept as regenerable index**, not removed. JSONL is the
   source of truth; SQLite provides fast queries. This is better than
   either "SQLite only" (not git-friendly) or "JSONL only" (slow queries).

3. **Sections as labels, not beads.** Questions use labels
   (`section:business_overview`) rather than a parent task hierarchy.
   Simpler, works well enough.

4. **Synthesis runs in-process**, not via Claude API calls. Pattern
   detection and coherence checks use Python logic over the task/decision
   data, not LLM prompts. LLM-powered synthesis can be added later.

---

## Summary

Replace form-copilot's direct SQLite storage with a layered memory architecture using [beads](https://github.com/steveyegge/beads) for task/answer tracking, [quint-code](https://github.com/m0n0x41d/quint-code) for decision reasoning trails, and a new synthesis layer that extracts insights across accumulated context.

## Motivation

Current form-copilot stores answers in SQLite and events in `session_log.json`. This works but misses opportunities:

1. **No dependency graph** - Questions have `depends_on` in config but answers don't track relationships
2. **No reasoning trails** - We know *what* was answered but not *why* that framing was chosen
3. **No synthesis** - Completed answers accumulate but don't connect into insights
4. **Session-bound context** - Each Claude session starts fresh; learnings don't compound

## Design Principles

- **Integrate, don't reimplement** - beads and quint are mature tools; use them
- **Synthesis over summarization** - Compression should surface patterns, not just shorten text
- **Git-native** - All state survives in version control
- **Agent-friendly** - Structure enables Claude to reason across sessions

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   form-copilot                       │
├─────────────────────────────────────────────────────┤
│  Interface Layer (existing)                         │
│  - sea_assistant.py menu system                     │
│  - .claude/commands/ for Claude Code                │
├─────────────────────────────────────────────────────┤
│  Synthesis Layer (new)                              │
│  - Pattern detection across completed work          │
│  - Cross-reference discovery                        │
│  - Context decay with insight preservation          │
├─────────────────────────────────────────────────────┤
│  Storage Layer (refactored)                         │
│  - beads (.beads/) - questions, answers, deps       │
│  - quint (.quint/) - decision reasoning trails      │
│  - SQLite removed as primary store                  │
└─────────────────────────────────────────────────────┘
```

## Beads Integration

### Mapping

| Current (SQLite) | Beads Equivalent |
|------------------|------------------|
| `questions` table | Config-driven (unchanged) |
| `answers` table | `bd create` with answer as description |
| `answers.status` | Bead status (open/in_progress/closed) |
| `answers.notes` | Bead comments |
| `depends_on` | `bd block` relationships |
| Progress queries | `bd ready`, `bd list --status` |

### Task Hierarchy

```
Form (epic)
└── Section (task)
    └── Question (subtask)
        └── Answer iterations (comments/history)
```

### Example Flow

```bash
# Initialize form as beads project
bd init

# Create section
bd create "Section: Business Overview" --label section

# Create question under section
bd create "What problem does your business solve?" \
  --parent bd-a1b2 \
  --label question \
  --label priority:1

# Save answer
bd comment bd-a1b2.1 "Answer: We reduce complexity in..."
bd close bd-a1b2.1
```

## Quint Integration

### Decision Points

Not every answer needs a decision trail. Track reasoning when:
- Choosing between multiple valid framings
- Making trade-offs (brevity vs completeness)
- Connecting answer to external context (resume, other applications)

### Example

```bash
# Before finalizing an answer
/q1-hypothesize
# H1: Lead with technical depth
# H2: Lead with business impact
# H3: Lead with personal narrative

/q2-verify
# Checking against: role requirements, company culture, section context

/q5-decide
# Selected H2: Business impact framing matches startup audience
```

### Storage

Decisions persist in `.quint/` directory, queryable later:
- "Why did I frame the leadership answer around delegation?"
- "What trade-offs did I consider for the technical question?"

## Synthesis Layer

### Purpose

Transform accumulated answers and decisions into actionable insights.

### Operations

**1. Pattern Detection**
```
synthesize patterns

Output:
- Theme "systems thinking" appears in 4/7 answers
- Gap: No answers reference quantitative achievements
- Consistency: All technical answers mention integration work
```

**2. Cross-Reference Discovery**
```
synthesize connections --question bd-a3f8

Output:
- Answer bd-a3f8 (leadership) aligns with decision qt-002
- Related closed bead bd-a2c1 covers same ground differently
- Consider consolidating framing
```

**3. Context Decay**
```
synthesize decay --older-than 30d

Output:
- Compressing 12 closed beads from January
- Preserved insights:
  - "Integration expertise" is core positioning
  - Passed on roles requiring deep ML specialization
- Raw answers archived, summaries active
```

### Implementation

Synthesis runs Claude against beads/quint data:
1. Load relevant beads (by label, status, date)
2. Load related quint decisions
3. Prompt Claude for pattern/connection/decay analysis
4. Store synthesis as new bead with `--label synthesis`

## Migration Path

### Phase 1: Beads for New Work
- Install beads CLI
- Add `bd` commands alongside existing SQLite
- New answers go to both stores
- Validate beads captures everything needed

### Phase 2: Quint for Decisions
- Install quint MCP server
- Add `/q*` commands to Claude workflow
- Track decisions on complex questions only
- Build decision query patterns

### Phase 3: Synthesis Commands
- Implement `form-copilot synthesize` subcommand
- Pattern detection first (most immediately useful)
- Cross-reference and decay follow

### Phase 4: SQLite Removal
- Migrate historical answers to beads
- Remove SQLite code paths
- Update documentation

## Open Questions

1. **Beads hierarchy depth** - Should sections be beads or just labels?
2. **Quint granularity** - Decision trail per question or per session?
3. **Synthesis storage** - Separate beads repo or same as answers?
4. **Offline operation** - Both tools work offline; any edge cases?

## Success Criteria

- [ ] New answers stored in beads, queryable via `bd`
- [ ] At least one decision trail captured in quint
- [ ] `synthesize patterns` returns meaningful output
- [ ] No regression in existing menu workflow
- [ ] SQLite fully removed (Phase 4)

## References

- [beads](https://github.com/steveyegge/beads) - Git-backed task tracking for agents
- [quint-code](https://github.com/m0n0x41d/quint-code) - Structured reasoning framework
- [gastown](https://github.com/steveyegge/gastown) - Multi-agent orchestration using beads
- [Craft Agents](https://newsletter.pragmaticengineer.com/p/ai-first-makeover-craft) - Custom Claude Agent SDK implementation
