# RFC 005: Ephemeral Store

**Status:** Draft
**Author:** Aaron Johnson
**Created:** 2026-02-19
**Parent:** [RFC 004](004-smrti-rename-and-typed-memory.md)

## Purpose

Define the ephemeral memory store — session-scoped scratch
space that bridges the gap between an AI agent's conversation
context and smrti's durable stores.

---

## Problem

When Claude Code works on a smrti project, two memory systems
operate independently:

1. **Anthropic's session context** — task tracking, conversation
   history, tool results. Ephemeral by design: gone when the
   session ends or the context window compresses.

2. **smrti's durable stores** — tasks.jsonl (procedural),
   decisions.jsonl (episodic), facts.jsonl (semantic). Persistent,
   git-backed, survive across sessions.

The gap: valuable session state that isn't yet ready for a durable
store has nowhere to land. Draft answers, working hypotheses,
partial extractions, scratch calculations — these either live only
in the agent's context (lost on session end) or get prematurely
committed to a durable store (polluting it with noise).

---

## Proposal

### The ephemeral/ directory

```
.memory/
├── tasks.jsonl        # procedural (durable)
├── decisions.jsonl    # episodic (durable)
├── facts.jsonl        # semantic (durable)
├── index.db           # regenerable cache
├── config.json
└── ephemeral/         # session scratch (not persisted)
    ├── session.json   # current session metadata
    ├── scratch.md     # freeform working notes
    └── staging/       # items being prepared for durable stores
```

### What goes in ephemeral/

| Content | Example | Destination after triage |
|---|---|---|
| Draft answers | Half-written response to Q3 | tasks.jsonl (when finalized) |
| Working hypotheses | "Maybe the revenue model is subscription" | decisions.jsonl (if worth recording) |
| Extracted candidates | Facts noticed but not yet verified | facts.jsonl (if confirmed) |
| Session metadata | Start time, questions touched, agent ID | Discarded or logged |
| Scratch notes | Calculations, comparisons, outlines | Discarded |

### Lifecycle

1. **Session start** — create `ephemeral/session.json` with
   timestamp and session ID
2. **During session** — agent writes scratch files as needed.
   No schema enforced. Plain text, JSON, markdown — whatever
   the agent finds useful.
3. **Triage** — before session end, the agent (or human) reviews
   ephemeral/ and promotes anything worth keeping into the
   appropriate durable store via the Python API.
4. **Session end** — `ephemeral/` is cleared. The .gitignore
   already excludes it.

### Not persisted

The ephemeral directory is:
- Listed in `.gitignore` (never committed)
- Cleared on session start (previous session's scratch is gone)
- Not backed by SQLite (no index, no drift detection)
- Not included in `smrti.py memory rebuild` or `compact`

This is intentional. Ephemeral memory is disposable by definition.

---

## Overlap with Anthropic session tools

Anthropic's built-in `TaskCreate`/`TaskUpdate` tools serve a
similar purpose: tracking work items within a single conversation.
They are ephemeral — gone when the session ends.

### Where they differ

| Aspect | Anthropic session tools | smrti ephemeral/ |
|---|---|---|
| Scope | Conversation context | File system |
| Survives context compression | No | Yes (until session end) |
| Structured | Yes (task model) | No (freeform) |
| Accessible to human | Only via agent | Directly readable files |
| Promotable to durable store | Manual (agent must extract) | Direct (files are right there) |

### The bridge value

The key insight: Anthropic's tools track *agent work*, while
smrti's ephemeral store holds *domain knowledge in progress*.

A session where the agent answers 5 application questions might
use Anthropic's task tools to track "answer Q1, Q2, Q3..."
while using ephemeral/ to hold:
- Draft text for Q3 that the human hasn't reviewed yet
- A fact extracted from the Q1 discussion that applies to Q5
- A note that Q2 and Q4 have contradictory assumptions

These are different concerns. The agent's work tracker doesn't
need to persist. The domain scratch does — at least until triage.

### Future: automatic triage

A natural extension (not in this RFC): at session end, the
agent could automatically scan ephemeral/ and propose
promotions:

```
Session ending. Found in ephemeral/:
  - scratch.md: 3 candidate facts identified
  - staging/q3-draft.md: draft answer for Q3

Promote to durable stores?
  [1] Extract facts to facts.jsonl
  [2] Save Q3 draft to tasks.jsonl
  [3] Discard all
  [4] Review individually
```

This bridges the two systems without coupling them.

---

## Implementation

### Phase 1 (minimal)

- Create `ephemeral/` directory on Memory init
- Add `.gitignore` entry for `ephemeral/`
- Add `Memory.ephemeral_path` property
- Add `Memory.clear_ephemeral()` method
- No schema, no models, no SQLite

### Phase 2 (session awareness)

- `session.json` with start time, session ID
- `Memory.start_session()` / `Memory.end_session()`
- Automatic clear on new session start

### Phase 3 (triage helpers)

- `Memory.promote_fact(path)` — read file, create fact
- `Memory.promote_draft(path, task_id)` — attach to task
- CLI: `smrti.py memory triage`

---

## Open questions

1. Should ephemeral/ contents survive across sessions if
   the human explicitly asks? (A "pin" mechanism?)
2. Should there be a TTL — auto-clear after N hours even
   without a new session?
3. Is `staging/` a useful sub-convention or over-engineering
   for Phase 1?

---

## References

- RFC 004: smrti rename and typed memory (parent)
- ENGRAM (arxiv:2511.12960) — procedural memory as working buffer
- Google Context Engineering whitepaper — session management
- Letta — filesystem memory that outperforms specialized systems
