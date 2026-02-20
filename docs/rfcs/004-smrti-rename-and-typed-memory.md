# RFC 004: smrti — Rename and Typed Memory

**Status:** Draft
**Author:** Aaron Johnson
**Created:** 2026-02-19
**Parent:** RFC 002

## Purpose

Rename form-copilot to **smrti** (स्मृति, Sanskrit: "memory,
remembered tradition") and restructure the memory layer around
three typed stores: episodic, semantic, and procedural. The
repository becomes **advaita-smrti** (अद्वैत-स्मृति, "non-dual
memory").

This RFC covers:
1. The rename (files, imports, CLI, branch, docs)
2. Adding a semantic (facts) store alongside existing stores
3. Adopting ENGRAM's typed memory taxonomy
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

### Taxonomy (from ENGRAM)

| Type | What it stores | Schema | Current analog |
|---|---|---|---|
| **Episodic** | Events in time | (title, summary, timestamp) | `decisions.jsonl` |
| **Semantic** | Stable facts | (fact, timestamp, source) | *missing* |
| **Procedural** | Tasks and workflows | (title, status, deps) | `tasks.jsonl` |

### New: Semantic Store (`facts.jsonl`)

A new JSONL file and corresponding SQLite index table for
extracted facts.

```python
@dataclass
class Fact:
    id: str              # sm-f-xxxxx
    fact: str            # "Shelter is on Ainsworth St"
    source: str          # "site_visit_2026-02-19"
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
    "Shelter is on Ainsworth St",
    source="site_visit_2026-02-19",
    section="Location",
)

# Update (creates new version, marks old as superseded)
mem.facts.update(fact.id, fact="Shelter is at 211 NE Ainsworth")

# Query
facts = mem.facts.by_section("Location")
facts = mem.facts.by_label("hardware")
facts = mem.facts.search("ainsworth")  # substring match

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
2. The three memory types (table)
3. Quick-start (install, configure, run)
4. CLI reference
5. References section:
   - ENGRAM (arxiv 2511.12960)
   - Google/Kaggle: Context Engineering: Sessions & Memory
   - beads, quint-code (original inspirations)
6. See also: Zep, Letta, Mem0 (landscape context)

Drop: project evolution history, Alice in Wonderland references,
lengthy CHANGELOG prose.

### CLAUDE.md update

Update the memory layer section to reflect three stores and
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
