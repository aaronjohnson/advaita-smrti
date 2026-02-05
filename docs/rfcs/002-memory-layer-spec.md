# RFC 002: Memory Layer Specification

**Status:** Draft
**Author:** Aaron Johnson
**Created:** 2026-02-05
**Parent:** RFC 001

## Purpose

Document the essential patterns from [beads](https://github.com/steveyegge/beads) and [quint-code](https://github.com/m0n0x41d/quint-code) for pure Python implementation. This spec captures what we need, not everything those tools offer.

---

## Part 1: Task Graph (inspired by beads)

### Core Concepts

**Task**: A unit of work with identity, status, and relationships.

**Identity**: Hash-based IDs avoid merge conflicts in concurrent/multi-session scenarios.
- Format: `{prefix}-{5-char-alphanum}` (e.g., `fc-a1b2c`)
- Prefix configurable per project (default: `fc` for form-copilot)

**Hierarchy**: Tasks can have parent/child relationships.
- Notation: `fc-a1b2c.1` is first child of `fc-a1b2c`
- Enables: epic → task → subtask structures

**Dependencies**: Tasks can block other tasks.
- `blocks`: List of task IDs that cannot start until this completes
- `blocked_by`: List of task IDs that must complete before this starts

**Status**: Lifecycle states.
- `open` → `in_progress` → `closed`
- `archived` (for compacted/decayed tasks)

### Data Model

```python
@dataclass
class Task:
    id: str                      # fc-a1b2c
    title: str                   # Short description
    description: str             # Full content (answers, notes)
    status: str                  # open, in_progress, closed, archived
    parent_id: Optional[str]     # Parent task ID
    blocks: List[str]            # Task IDs this blocks
    blocked_by: List[str]        # Task IDs blocking this
    labels: List[str]            # Freeform tags
    created_at: str              # ISO timestamp
    updated_at: str              # ISO timestamp
    metadata: Dict[str, Any]     # Extensible properties
```

### Storage Format

**Primary**: JSONL file (one task per line, append-friendly)
```
{"id":"fc-a1b2c","title":"...","status":"open",...}
{"id":"fc-d3e4f","title":"...","status":"closed",...}
```

**Location**: `.memory/tasks.jsonl`

**Index**: SQLite cache for queries (regenerable from JSONL)
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT,
    status TEXT,
    parent_id TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE task_labels (task_id TEXT, label TEXT);
CREATE TABLE task_blocks (task_id TEXT, blocks_id TEXT);
```

### Operations

| Operation | Description |
|-----------|-------------|
| `create(title, description, parent_id?, labels?)` | Create task, generate ID |
| `get(id)` | Retrieve single task |
| `update(id, fields)` | Modify task fields |
| `close(id)` | Mark task closed |
| `list(status?, label?, parent_id?)` | Query tasks |
| `ready()` | List tasks with no unresolved blocked_by |
| `block(id, blocks_id)` | Add dependency |
| `unblock(id, blocks_id)` | Remove dependency |
| `children(id)` | List child tasks |
| `history(id)` | List all versions of task |

### ID Generation

```python
import hashlib
import time

def generate_id(prefix: str = "fc") -> str:
    """Generate hash-based task ID."""
    seed = f"{time.time_ns()}{random.random()}"
    hash_bytes = hashlib.sha256(seed.encode()).digest()
    alphanum = base32_encode(hash_bytes)[:5].lower()
    return f"{prefix}-{alphanum}"
```

---

## Part 2: Decision Trails (inspired by quint)

### Core Concepts

**Decision**: A recorded reasoning process for non-trivial choices.

**Hypothesis**: A candidate approach being considered.
- Multiple hypotheses generated before selection
- Each has rationale and confidence score

**Workflow**: Structured reasoning phases.
1. **Abduction** - Generate multiple hypotheses (don't anchor on first idea)
2. **Deduction** - Check logical consistency, constraints
3. **Induction** - Test against evidence, examples
4. **Selection** - Choose hypothesis with rationale

**Audit Trail**: Decisions are queryable later.
- "Why did I choose this framing?"
- "What alternatives did I consider?"

### Data Model

```python
@dataclass
class Hypothesis:
    id: str                      # h1, h2, h3
    description: str             # The approach
    rationale: str               # Why it might work
    confidence: float            # 0.0 - 1.0

@dataclass
class Decision:
    id: str                      # qt-a1b2c
    context: str                 # What we're deciding
    task_id: Optional[str]       # Related task (if any)
    hypotheses: List[Hypothesis] # Options considered
    selected: Optional[str]      # Chosen hypothesis ID
    selection_rationale: str     # Why this choice
    phase: str                   # abduction, deduction, induction, decided
    created_at: str
    decided_at: Optional[str]
```

### Storage Format

**Primary**: JSONL file
```
{"id":"qt-a1b2c","context":"How to frame leadership answer",...}
```

**Location**: `.memory/decisions.jsonl`

### Operations

| Operation | Description |
|-----------|-------------|
| `begin(context, task_id?)` | Start decision, phase=abduction |
| `hypothesize(decision_id, description, rationale)` | Add hypothesis |
| `verify(decision_id)` | Move to deduction phase |
| `test(decision_id)` | Move to induction phase |
| `decide(decision_id, hypothesis_id, rationale)` | Select and close |
| `get(id)` | Retrieve decision |
| `list(task_id?, phase?)` | Query decisions |
| `for_task(task_id)` | All decisions related to task |

---

## Part 3: Synthesis

### Core Concepts

**Synthesis**: Analysis that extracts insights from accumulated tasks and decisions.

**Pattern Detection**: Find recurring themes, gaps, inconsistencies.

**Cross-Reference**: Connect related items across different contexts.

**Decay**: Compress old items while preserving essential insights.

### Operations

| Operation | Input | Output |
|-----------|-------|--------|
| `patterns(label?, since?)` | Filter criteria | List of detected patterns |
| `connections(task_id)` | Single task | Related tasks and decisions |
| `decay(older_than)` | Age threshold | Summary of archived items |

### Synthesis Output Model

```python
@dataclass
class Pattern:
    description: str             # What was detected
    evidence: List[str]          # Task/decision IDs supporting this
    confidence: float            # How strong the pattern is

@dataclass
class Connection:
    source_id: str               # Starting point
    target_id: str               # Connected item
    relationship: str            # How they connect
    strength: float              # Connection strength

@dataclass
class DecaySummary:
    archived_count: int          # Items compressed
    insights: List[str]          # Preserved learnings
    task_ids: List[str]          # What was archived
```

### Synthesis Implementation

Synthesis requires LLM reasoning. Implementation:
1. Load relevant tasks/decisions based on query
2. Format as prompt context
3. Call Claude API (or Claude Code subprocess)
4. Parse structured response
5. Store synthesis results as special task (label: `synthesis`)

---

## Part 4: Storage Layout

```
.memory/
├── tasks.jsonl          # All tasks (append-only log)
├── decisions.jsonl      # All decisions (append-only log)
├── index.db             # SQLite cache (regenerable)
├── config.json          # Prefix, settings
└── archive/
    └── 2026-01/         # Monthly archives after decay
        ├── tasks.jsonl
        └── synthesis.md
```

### Config

```json
{
  "prefix": "fc",
  "version": "1.0",
  "created_at": "2026-02-05T00:00:00Z"
}
```

---

## Part 5: CLI Interface

### Task Commands

```bash
# Create
memory task create "Answer business overview question" --label question --label priority:1

# List
memory task list                    # All open
memory task list --status closed    # Closed only
memory task ready                   # Unblocked tasks

# Update
memory task close fc-a1b2c
memory task block fc-a1b2c fc-d3e4f  # a1b2c blocks d3e4f

# View
memory task show fc-a1b2c
memory task history fc-a1b2c
```

### Decision Commands

```bash
# Start decision
memory decide begin "How to frame technical background" --task fc-a1b2c

# Add hypotheses
memory decide hypo qt-x1y2z "Lead with Intel experience" --confidence 0.7
memory decide hypo qt-x1y2z "Lead with recent AI work" --confidence 0.8

# Complete
memory decide select qt-x1y2z h2 --rationale "AI work is more relevant to this role"

# Query
memory decide show qt-x1y2z
memory decide for-task fc-a1b2c
```

### Synthesis Commands

```bash
# Analyze
memory synthesize patterns --label question
memory synthesize connections fc-a1b2c
memory synthesize decay --older-than 30d
```

---

## Part 6: Python API

```python
from memory import Memory

# Initialize
mem = Memory(".memory")

# Tasks
task = mem.tasks.create("Answer question", description="...", labels=["question"])
mem.tasks.update(task.id, status="in_progress")
ready = mem.tasks.ready()
mem.tasks.close(task.id)

# Decisions
decision = mem.decisions.begin("How to frame answer", task_id=task.id)
mem.decisions.hypothesize(decision.id, "Option A", rationale="...")
mem.decisions.hypothesize(decision.id, "Option B", rationale="...")
mem.decisions.decide(decision.id, "h1", rationale="Better fit")

# Synthesis
patterns = mem.synthesize.patterns(label="question")
connections = mem.synthesize.connections(task.id)
```

---

## Implementation Notes

### Why JSONL + SQLite?

- **JSONL**: Append-only, git-friendly, human-readable, no corruption on crash
- **SQLite**: Fast queries, indexes, but regenerable from JSONL source of truth

### Why Hash IDs?

- No coordination needed between sessions
- No merge conflicts
- Short enough to type/reference

### Git Integration

- `.memory/` is tracked in git
- JSONL files merge cleanly (append-only)
- `index.db` in `.gitignore` (regenerable)

---

## References

- [beads](https://github.com/steveyegge/beads) - Original task graph implementation
- [quint-code](https://github.com/m0n0x41d/quint-code) - Original decision framework
- [First Principles Framework](https://github.com/m0n0x41d/quint-code) - Levenchuk's reasoning model
