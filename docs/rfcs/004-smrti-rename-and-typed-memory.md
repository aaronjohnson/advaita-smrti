# RFC 004: smrti — Rename and Typed Memory

**Status:** Draft
**Author:** Aaron Johnson
**Created:** 2026-02-19
**Parent:** RFC 002

## Purpose

Rename form-copilot to **smrti** (स्मृति, Sanskrit: "memory,
remembered tradition") and restructure the memory layer around
four typed stores: episodic, semantic, procedural, and
ephemeral. The
repository becomes **advaita-smrti** (अद्वैत-स्मृति, "non-dual
memory").

This RFC covers:
1. The rename (files, imports, CLI, branch, docs)
2. Adding semantic (facts) and ephemeral (working) stores
3. Adopting a typed memory taxonomy from ENGRAM and the
   Google survey paper
4. What we keep, what we drop, what changes

---

## Motivation

### Why rename

"Form copilot" describes the original scope — helping fill out
multi-section applications. The tool has grown beyond that into
a general memory layer for structured knowledge elicitation.
The name should reflect what it is, not what it started as.

**smrti** means "that which is remembered" — the body of
remembered tradition in Hindu philosophy, as distinct from
shruti ("that which is heard," revealed knowledge). The tool
captures what the human remembers and knows, structures it,
and makes it retrievable. The name fits.

**advaita** means "non-dual." The tool and the thinker are not
separate. The repository name advaita-smrti carries the
philosophy; the CLI and package name smrti stays short for
daily use.

### Why typed memory

The ENGRAM paper (Patel & Patel, 2026) demonstrates that
separating memory into typed stores — episodic, semantic,
procedural — and retrieving from each independently before
merging outperforms systems that dump everything into one
store. Typed separation reduces competition at retrieval time.

Our current memory layer has two stores:
- `tasks.jsonl` — procedural (questions, dependencies, status)
- `decisions.jsonl` — episodic (what happened, choices made)

The missing type is **semantic** — stable facts, preferences,
and constraints extracted from conversations and site visits.
Today these live scattered across task descriptions, CLAUDE.md,
or the human's own notes. A dedicated facts store surfaces
them at retrieval time without competing against procedural or
episodic items.

### What makes this different

Every system in the memory literature — ENGRAM, Mem0, Zep,
Letta, MemOS — starts from **conversation** as input. We
start from **structured forms**: sections, questions,
dependencies, priorities. This gives us properties they lack:

- The form itself is the procedural memory (no extraction needed)
- Coherence checking across answers is built in
- Dependency ordering constrains the retrieval problem
- There is a clear "done" criterion

This maps to clinical intake, grant applications, legal
discovery, insurance claims — anywhere humans complete complex
multi-part forms with an AI collaborator.

---

## Part 1: The Rename

### Files

| Before | After |
|---|---|
| `form_copilot.py` | `smrti.py` |
| repo: `form-copilot` | repo: `advaita-smrti` |
| branch: `queens-garden` | TBD (drop Alice in Wonderland theme) |
| prefix: `fc` | prefix: `sm` |

### Imports

```python
# Before
from memory import Memory

# After (unchanged — the memory/ package name stays)
from memory import Memory
```

The `memory/` package is internal and does not need renaming.
External-facing changes are the CLI entry point and repo name.

### CLI

```bash
# Before
python3 form_copilot.py memory rebuild
python3 form_copilot.py status

# After
python3 smrti.py memory rebuild
python3 smrti.py status
```

### Default branch

The `queens-garden` branch name comes from the Alice in
Wonderland theme. A new name is needed. Options TBD — could
be `main`, could be Sanskrit-themed. Decision deferred to
implementation.

### What stays

- `memory/` package directory and all its modules
- `sea_application_helper.py` (the SEA form helper)
- `sea_assistant.py` (interactive assistant)
- `examples/`, `tests/`, `docs/`
- JSONL + SQLite storage architecture
- All existing tests (updated imports only)

### What gets removed or renamed

- All string references to "form-copilot" and "form_copilot"
- The Alice in Wonderland release names in CHANGELOG.md
- `business_direction_analysis.md` (stale, pre-rename context)

---

## Part 2: Typed Memory Stores

### Taxonomy

Combines ENGRAM's typed stores (Patel & Patel, 2026) with the
working memory concept from the Google survey (Hu et al., 2025).

| Type | What it stores | Persisted | Current analog |
|---|---|---|---|
| **Procedural** | Tasks, workflows, deps | yes, `tasks.jsonl` | existing |
| **Episodic** | Events, decisions, cases | yes, `decisions.jsonl` | existing |
| **Semantic** | Stable facts, preferences | yes, `facts.jsonl` | *missing* |
| **Ephemeral** | Active session workspace | no, `ephemeral/` | implicit (context files) |

### New: Semantic Store (`facts.jsonl`)

A new JSONL file and corresponding SQLite index table for
extracted facts.

```python
@dataclass
class Fact:
    id: str              # sm-f-xxxxx
    fact: str            # "Business registered in Oregon"
    source: str          # "application_q3"
    section: str         # Optional section grouping
    confidence: float    # 0.0-1.0
    labels: List[str]    # Freeform tags
    supersedes: str      # ID of fact this replaces (if updated)
    created_at: str      # ISO timestamp
    updated_at: str      # ISO timestamp
    metadata: dict       # Extensible
```

#### API

```python
mem = Memory(".memory")

# Create
fact = mem.facts.create(
    "Business registered in Oregon",
    source="application_q3",
    section="legal",
)

# Update (creates new version, marks old as superseded)
mem.facts.update(fact.id, fact="Business registered in Oregon since 2024")

# Query
facts = mem.facts.by_section("legal")
facts = mem.facts.by_label("requirement")
facts = mem.facts.search("oregon")  # substring match

# All
all_facts = mem.facts.all()
```

#### SQLite index additions

```sql
CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    fact TEXT,
    source TEXT,
    section TEXT,
    confidence REAL,
    supersedes TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS fact_labels (
    fact_id TEXT,
    label TEXT,
    PRIMARY KEY (fact_id, label)
);

CREATE INDEX IF NOT EXISTS idx_facts_section ON facts(section);
CREATE INDEX IF NOT EXISTS idx_facts_source ON facts(source);
```

#### Drift detection

The existing drift detection extends to cover facts:

```
Tasks:     JSONL has N, index has M
Decisions: JSONL has N, index has M
Facts:     JSONL has N, index has M
```

### New: Ephemeral Store (`ephemeral/`)

The ephemeral store holds transient state for the active
session. It is not appended to JSONL — it lives in a
directory that is cleared or rolled into episodic memory
when the session ends.

#### What goes here

- **Active question context** — the current question being
  worked on, related answers pulled from other stores, notes
  in progress. Currently `.sea_question_context.json`.
- **Draft state** — the answer being composed. Currently
  `.sea_answer.md`.
- **Session scratch** — what's been discussed this session,
  intermediate reasoning, temporary notes.
- **Retrieved context** — facts, tasks, and decisions pulled
  from the persistent stores for the current task.

#### Lifecycle

```
session start  → ephemeral/ created (or cleared)
during session → files written and read freely
session end    → option to:
                   (a) discard (default)
                   (b) promote to episodic (save as decision)
                   (c) extract facts to semantic store
```

#### Structure

```
ephemeral/
  context.json      # Current question/task context
  draft.md          # Answer or artifact in progress
  retrieved/        # Cached retrievals from other stores
    facts.json      # Relevant facts for current task
    tasks.json      # Related tasks
    decisions.json  # Related prior decisions
```

#### Why "ephemeral" not "working"

The Google survey calls this "working memory." We call it
**ephemeral** to emphasize that it is not persisted by
default. The cognitive science term "working memory" implies
a fixed-capacity buffer; our ephemeral store is simply
session-scoped scratch space with no capacity constraint.
The name also avoids confusion with a directory name
suggesting permanence — it is explicitly temporary.

### Coherence checking additions

The existing `coherence_check()` gains a new category:

- **fact_conflict**: Two facts in the same section contradict
  each other (e.g., two different addresses)
- **fact_staleness**: A fact's source is older than a threshold
  and may need re-verification

### What we defer

- **Vector embeddings / cosine similarity** — our dataset is
  small enough for exact match and substring search. Embeddings
  can be added later without changing the store schema (the
  ENGRAM embedding field is optional).
- **LLM-powered router** — ENGRAM uses an LLM call to classify
  each incoming utterance into memory types. For now, routing
  is human-directed (the user or Claude explicitly calls
  `facts.create()` vs `tasks.create()` vs `decisions.begin()`).
  A router can be added as a convenience layer later.
- **Cross-type retrieval merging** — ENGRAM merges top-k from
  each store at query time. We don't need this yet because our
  queries are type-specific (show me all facts, show me ready
  tasks). When we add a natural-language query interface, this
  becomes relevant.
- **Temporal decay for facts** — facts don't decay the same way
  tasks do. A fact is true until superseded. The `supersedes`
  field handles versioning without decay.

---

## Part 3: Documentation

### README rewrite

The README becomes succinct and forward-looking:

1. One paragraph: what smrti is
2. The four memory types (table)
3. Quick-start (install, configure, run)
4. CLI reference
5. Inspirations and references:
   - beads — git-backed task graphs (original inspiration)
   - quint-code — decision reasoning trails (original inspiration)
   - ENGRAM (arxiv 2511.12960) — typed memory stores
   - Memory in the Age of AI Agents (arxiv 2512.13564) — survey/taxonomy
   - Google/Kaggle: Context Engineering: Sessions & Memory
6. See also: Zep, Letta, Mem0, Pinecone (landscape context)

Drop: project evolution history, Alice in Wonderland references,
lengthy CHANGELOG prose.

### CLAUDE.md update

Update the memory layer section to reflect four stores and
the `smrti.py` entry point.

### CHANGELOG

Start fresh with v0.5.0 or v1.0.0 for the rename. Previous
history preserved in git.

---

## References

- Patel, D. & Patel, S. (2026). ENGRAM: Effective, Lightweight
  Memory Orchestration for Conversational Agents.
  arXiv:2511.12960.
- Hu, Y. et al. (2025). Memory in the Age of AI Agents: A
  Survey. arXiv:2512.13564.
- Google. (2025). Context Engineering: Sessions & Memory.
  Kaggle whitepaper.
- Yegge, S. beads — git-backed task graphs.
  github.com/steveyegge/beads.
- quint-code — decision reasoning trails.
  github.com/m0n0x41d/quint-code.

## Open Questions

1. **Default branch name** — drop `queens-garden`. Options:
   `main`, or a Sanskrit term. Suggestions welcome.
2. **Version number** — v0.5.0 (incremental) or v1.0.0
   (the rename is a milestone)?
3. **sea_application_helper.py / sea_assistant.py** — these
   names are SEA-grant-specific. Rename to generic names in
   this pass, or defer?
4. **PyPI name** — `smrti` is taken (screen manager, 0.0.1).
   Alternatives: `advaita-smrti`, `py-smrti`. Or defer until
   we actually publish.
