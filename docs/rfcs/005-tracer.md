# RFC 005: Tracer — Session Observation Layer

**Status:** Draft
**Author:** Aaron Johnson + Claude
**Created:** 2026-02-20
**Parent:** RFC 003 (Recursive Context and Complementary Cognition)
**References:** RFC 002, RFC 004

---

## Summary

Add a **tracer** to smrti: a structured record of what happens
during a collaborative session. The tracer captures spans — units
of work performed by either participant (human or model) — and
organizes them into sessions. It is the observational layer that
RFC 003 proposed but did not specify.

The tracer answers: *what happened, who did it, and what did it
touch?*

The existing stores answer *what* (tasks), *why* (decisions), and
*what is true* (facts). The tracer answers *how* — the process by
which those stores were read, written, and connected during live
work.

---

## Motivation

### The gap in the memory layer

smrti has four memory types (RFC 004):

| Type | Records | Example |
|---|---|---|
| Procedural | What needs doing | "Answer Q4: short-term goals" |
| Episodic | What was decided | "Chose Flask over Django because..." |
| Semantic | What is known | "Shelter is on Ainsworth St" |
| Ephemeral | Active scratch | Draft answer in progress |

None of these record *the process itself*. After a session ends,
you can see that Q4 was answered, that a decision was made, that
a fact was created — but not *how the session unfolded*. Which
questions were attempted and abandoned? Which facts were retrieved
but not used? Where did the human redirect the model? Where did
the model surface a connection the human hadn't seen?

RFC 003 proposed contribution tagging (P2) and session dimensions
(P4: momentum, reach, complementarity). Both require observational
data that doesn't exist yet. The tracer generates that data.

### What the tracer is not

- **Not a logger.** Logs are for debugging infrastructure. The
  tracer records cognitive collaboration, not API calls or stack
  traces.

- **Not an audit log.** Audit logs record *who changed what* for
  accountability. The tracer records *how work happened* for
  reflection. They overlap but serve different purposes and
  different audiences.

- **Not surveillance.** The tracer records what each participant
  *contributed*, not how they *behaved*. Time between actions is
  captured for momentum measurement (RFC 003 P4), not for
  monitoring productivity. See Privacy section.

### The witness

In Advaita Vedānta, the *sākṣin* (साक्षिन्) is the witness —
pure awareness that observes experience without altering it. The
tracer is the sākṣin of a session. It watches two minds work
together, records what each contributes, and holds that record
for later reflection.

The philosophical parallel is deliberate. The tool's namesake
tradition distinguishes between the actor (*kartā*), the act
(*kriyā*), and the witness (*sākṣin*). The memory stores hold
the products of action. The tracer holds the witnessing of it.

---

## Design

### Core concepts

**Session.** A bounded unit of collaborative work — one Claude
Code conversation, one interactive menu run, one queen's garden
sequence. Sessions have a start and end. A human may have
multiple sessions per day or one session spanning hours.

**Span.** A unit of work within a session. Spans have a kind
(what type of work), an actor (who did it), a target (what it
touched), and a summary (what happened). Spans can nest: a
decision process is a parent span containing child spans for
each hypothesis, verification, and selection.

**Actor.** Either `human` or `model`. The tracer does not
distinguish between different humans or different models — it
tracks the two participants in the collaboration.

### Span kinds

| Kind | Actor | What it records |
|---|---|---|
| `input` | human | Human provided information, correction, or direction |
| `retrieve` | model | Model pulled data from a memory store |
| `draft` | model | Model composed or structured content |
| `refine` | either | Revision to existing content |
| `decide` | either | Selection among alternatives |
| `connect` | model | Model surfaced a cross-reference or dependency |
| `correct` | human | Human corrected a factual error |
| `redirect` | human | Human changed topic or approach |
| `check` | model | Coherence check or validation |
| `create` | either | New task, decision, or fact created |
| `close` | either | Task completed, decision finalized |

This is not an exhaustive taxonomy — `metadata` carries anything
that doesn't fit. These kinds cover the patterns observed in
actual sessions (RFC 003's queen's garden analysis).

### Relationship to existing stores

The tracer *references* other stores but does not duplicate them.

```
┌─────────────────────────────────────────────┐
│  Session sm-s-abc12                         │
│                                             │
│  span 1: retrieve  → task sm-7k2m4          │
│  span 2: input     → "budget and timeline"  │
│  span 3: draft     → answer for sm-7k2m4    │
│  span 4: connect   → sm-7k2m4 ↔ sm-9p3q1   │
│  span 5: correct   → "not $X, $Y"          │
│  span 6: refine    → updated answer          │
│  span 7: create    → fact sm-f-r8t2w         │
│  span 8: close     → task sm-7k2m4 closed   │
│                                             │
└─────────────────────────────────────────────┘
```

The session tells a story. The spans are the sentences. The
existing stores hold the nouns (tasks, decisions, facts). The
tracer holds the verbs.

---

## Data Model

### Session

```python
@dataclass
class Session:
    id: str                       # sm-s-xxxxx
    started_at: str               # ISO timestamp
    ended_at: Optional[str]       # ISO timestamp (null while active)
    mode: str                     # "garden" (continuous) or "wood" (per-question)
    summary: str                  # Post-session summary (generated at close)
    spans_count: int              # Number of spans in session
    tasks_touched: List[str]      # Task IDs read or written
    decisions_touched: List[str]  # Decision IDs read or written
    facts_touched: List[str]      # Fact IDs read or written
    metadata: Dict[str, Any]      # Extensible
```

### Span

```python
@dataclass
class Span:
    id: str                       # sm-t-xxxxx (t for trace)
    session_id: str               # Parent session
    kind: str                     # See span kinds table
    actor: str                    # "human" or "model"
    target: str                   # What was acted on (ID, path, or free text)
    summary: str                  # Brief description
    parent_span_id: Optional[str] # For nesting (nullable)
    seq: int                      # Ordering within session
    created_at: str               # ISO timestamp
    metadata: Dict[str, Any]      # Extensible (duration_ms, confidence, etc.)
```

### IDs

- Sessions: `sm-s-xxxxx` (s for session)
- Spans: `sm-t-xxxxx` (t for trace)

Following the existing convention of prefix + type marker +
5-char alphanumeric (RFC 004: `sm-f-xxxxx` for facts).

---

## Storage

### JSONL: `traces.jsonl`

Append-only, like the other stores. Each line is either a session
record or a span record, distinguished by the ID prefix (`sm-s-`
vs `sm-t-`).

```jsonl
{"id":"sm-s-abc12","started_at":"2026-02-20T09:00:00Z","mode":"garden","metadata":{}}
{"id":"sm-t-def34","session_id":"sm-s-abc12","kind":"retrieve","actor":"model","target":"sm-7k2m4","summary":"Loaded Q4 context","seq":1,"created_at":"2026-02-20T09:00:05Z","metadata":{}}
{"id":"sm-t-ghi56","session_id":"sm-s-abc12","kind":"input","actor":"human","target":"sm-7k2m4","summary":"Provided budget figure and timeline","seq":2,"created_at":"2026-02-20T09:01:30Z","metadata":{}}
```

### SQLite index additions

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT,
    ended_at TEXT,
    mode TEXT,
    summary TEXT,
    spans_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS spans (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    kind TEXT,
    actor TEXT,
    target TEXT,
    summary TEXT,
    parent_span_id TEXT,
    seq INTEGER,
    created_at TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS session_refs (
    session_id TEXT,
    ref_id TEXT,
    ref_type TEXT,  -- "task", "decision", "fact"
    PRIMARY KEY (session_id, ref_id)
);

CREATE INDEX IF NOT EXISTS idx_spans_session ON spans(session_id);
CREATE INDEX IF NOT EXISTS idx_spans_kind ON spans(kind);
CREATE INDEX IF NOT EXISTS idx_spans_actor ON spans(actor);
CREATE INDEX IF NOT EXISTS idx_spans_target ON spans(target);
CREATE INDEX IF NOT EXISTS idx_session_refs_ref ON session_refs(ref_id);
```

### Drift detection

Extends the existing pattern:

```
Tasks:     JSONL has N, index has M
Decisions: JSONL has N, index has M
Facts:     JSONL has N, index has M
Traces:    JSONL has N sessions + M spans, index has N + M
```

### Size management

Traces grow faster than other stores — a productive session
might generate 50–200 spans. Mitigation:

1. **Compaction.** `mem.traces.compact()` deduplicates the JSONL,
   same as other stores.

2. **Summarization.** At session close, generate a session summary
   and store it on the Session record. Individual spans can be
   queried when needed but the summary serves most review cases.

3. **Archival.** Sessions older than a configurable threshold
   (default: 90 days) can be archived — their spans are removed
   from the index, the session record keeps its summary. Span
   data remains in the JSONL for forensic recovery.

---

## API

### TracerStore

```python
mem = Memory(".memory", trace=True)

# --- Session lifecycle ---

session = mem.traces.begin(mode="garden")

mem.traces.span(
    session_id=session.id,
    kind="retrieve",
    actor="model",
    target="sm-7k2m4",
    summary="Loaded Q4 context and dependencies",
)

mem.traces.span(
    session_id=session.id,
    kind="input",
    actor="human",
    target="sm-7k2m4",
    summary="Provided budget figure: recurring cost",
)

# Nested spans
parent = mem.traces.span(
    session_id=session.id,
    kind="decide",
    actor="model",
    target="qt-abc12",
    summary="Evaluating framework options",
)
mem.traces.span(
    session_id=session.id,
    kind="draft",
    actor="model",
    target="qt-abc12",
    summary="Drafted hypothesis: Flask for speed",
    parent_span_id=parent.id,
)

mem.traces.end(session.id, summary="Completed Q4, created 2 facts")

# --- Queries ---

session = mem.traces.get_session(session_id)
spans = mem.traces.spans(session_id)
spans = mem.traces.spans(session_id, kind="input")
spans = mem.traces.spans(session_id, actor="human")
sessions = mem.traces.sessions(since="2026-02-01")
sessions = mem.traces.sessions(mode="garden")

# Timeline for a single target across sessions
timeline = mem.traces.timeline(target="sm-7k2m4")

# --- Derived metrics (RFC 003 P4) ---

metrics = mem.traces.metrics(session_id)
# Returns: { momentum: float, reach: float, complementarity: float }

# --- Maintenance ---

mem.traces.compact()
mem.traces.archive(older_than_days=90)
```

### Metrics derivation

The three metrics from RFC 003 P4 are computed from trace data:

**Momentum.** Average time between consecutive spans, excluding
gaps longer than a threshold (default: 5 minutes, indicating the
human stepped away). Measured in seconds per span. Lower is
faster, but fast is not better — momentum is a flow indicator,
not a productivity score.

**Reach.** Unique targets referenced across spans, divided by
total available tasks in the active config. A session that touches
15 of 49 questions has a reach of 0.31. Cross-references
(spans where `kind=connect`) are weighted higher because they
represent the integration work that distinguishes collaborative
answering from isolated answering.

**Complementarity.** Ratio of human-originated spans to
model-originated spans, reported as a pair. A session with 40%
human / 60% model is `(0.4, 0.6)`. Extreme ratios suggest one
participant is carrying — the interpretation depends on context
(a financial section may legitimately need more model retrieval;
a personal narrative section may be mostly human input).

### Integration with synthesis

The synthesis module gains access to trace data:

```python
# Pattern detection across sessions
patterns = mem.synthesize.session_patterns(since="2026-02-01")
# "Human corrections cluster around financial questions"
# "Model retrievals peak at section boundaries"

# Complementarity across sessions
comp = mem.synthesize.complementarity(session_id)
# { human_ratio: 0.45, model_ratio: 0.55, by_kind: {...} }
```

---

## Session Lifecycle

### Automatic instrumentation

When an interactive workflow runs, the tracer starts a session
automatically. Key events are instrumented at the call sites:

```python
# In the interactive assistant
session = mem.traces.begin(mode="garden")

# When context is loaded
mem.traces.span(session.id, "retrieve", "model", task_id,
                "Loaded context")

# When the human speaks
mem.traces.span(session.id, "input", "human", task_id,
                "User provided budget details")

# When the model drafts
mem.traces.span(session.id, "draft", "model", task_id,
                "Drafted answer incorporating new data")

# When coherence check runs
mem.traces.span(session.id, "check", "model", section,
                "Section coherence check: 2 findings")

# At session end
mem.traces.end(session.id, summary=model_generated_summary)
```

### Manual instrumentation

For users integrating smrti as a library, tracing is opt-in:

```python
mem = Memory(".memory", trace=True)    # Enable tracing
mem = Memory(".memory", trace=False)   # Disable (default)
```

When tracing is disabled, `mem.traces` is a no-op stub. All
`span()` and `begin()`/`end()` calls succeed silently and
return None. No performance cost when disabled.

---

## CLI

### `smrti.py memory traces`

```bash
# List recent sessions
smrti.py memory traces
#   sm-s-abc12  2026-02-20 09:00  garden  42 spans  "Completed Q4, created 2 facts"
#   sm-s-def34  2026-02-19 14:30  wood    18 spans  "Answered Q15-Q17 financial section"

# Show spans for a session
smrti.py memory traces sm-s-abc12
#   1  09:00:05  model   retrieve  sm-7k2m4   Loaded Q4 context
#   2  09:01:30  human   input     sm-7k2m4   Provided budget figure
#   3  09:02:15  model   draft     sm-7k2m4   Drafted answer
#   ...

# Filter by actor
smrti.py memory traces sm-s-abc12 --actor human

# Filter by kind
smrti.py memory traces sm-s-abc12 --kind connect

# Session metrics
smrti.py memory traces sm-s-abc12 --metrics
#   momentum:         45s/span
#   reach:            0.31 (15/49)
#   complementarity:  0.40 human / 0.60 model

# Timeline for a target across sessions
smrti.py memory traces --target sm-7k2m4
```

---

## Privacy

### What the tracer records

- **Span summaries** are brief descriptions of what happened,
  not transcripts. "User provided budget figure" is a span.
  The actual number lives in the task answer, not the trace.

- **Actor attribution** records *which* participant, not *what
  they said*. The trace says "human corrected a fact" — the
  corrected fact lives in `facts.jsonl`.

- **Timing** (via `created_at` on each span) enables momentum
  calculation. It does not record idle time, keystrokes, or
  attention metrics. The gap between spans is implicit; the
  tracer does not interpret it.

### What the tracer does NOT record

- Raw conversation text
- Keystrokes, mouse movements, or attention signals
- Time between spans as an explicit "idle" metric
- Model confidence scores or token probabilities
- PII beyond what the user explicitly provides as summaries

### Data locality

Traces follow the same locality rules as the rest of smrti:
stored in `.memory/traces.jsonl`, never transmitted to external
services. The file may be gitignored in deployments where trace
data is considered sensitive.

---

## Saṃcaya — Token Accounting

### Motivation

The tracer (§Design) records *what happened*. Token accounting
records *what it cost*. Together they answer: how efficiently
did the collaboration proceed?

The existing stores and the tracer capture the *shape* of
work. Token accounting captures the *weight*. Without it, we
can say "the model drafted 12 answers" but not "at what cost
in tokens, and how did caching affect that cost?"

### Data model: ApiCall

Every Anthropic API call made during a traced session is
recorded:

```python
@dataclass
class ApiCall:
    id: str                          # sm-a-xxxxx
    session_id: str                  # links to tracer session
    span_id: Optional[str]           # links to tracer span
    task_id: Optional[str]           # what question was being worked on
    section: Optional[str]           # section grouping
    condition_id: Optional[str]      # experimental condition (harness mode)

    # From Anthropic usage object
    input_tokens: int                # prompt tokens (after cache)
    output_tokens: int               # output tokens (includes thinking)
    cache_creation_input_tokens: int
    cache_read_input_tokens: int

    # Derived
    total_input_tokens: int          # sum of all input categories
    effective_cost_units: float      # normalized cost (configurable ratios)

    model: str
    created_at: str
    seq: int                         # ordering within session
    metadata: dict
```

### IDs

`sm-a-xxxxx` (a for api call). Follows the existing convention.

### Effective Cost Units (ECU)

Different token types cost differently. ECU normalizes them
into a single comparable number using configurable ratios:

```
ECU = (input_tokens × r_input)
    + (output_tokens × r_output)
    + (cache_creation_input_tokens × r_cache_create)
    + (cache_read_input_tokens × r_cache_read)
```

Default ratios (based on Anthropic Sonnet pricing, normalized
so `r_input = 1.0`):

| Token type | Default ratio | Why |
|------------|--------------|-----|
| `r_input` | 1.0 | baseline |
| `r_output` | 5.0 | output costs ~5× input |
| `r_cache_create` | 1.25 | 25% surcharge over input |
| `r_cache_read` | 0.1 | 90% discount from input |

Ratios are stored in harness config and can be adjusted per
model. ECU is unit-free — it is a *relative* cost measure for
comparison across conditions, not an absolute dollar figure.

### Storage

**JSONL:** `apicalls.jsonl` — append-only, same pattern as
all other stores.

**SQLite index:**

```sql
CREATE TABLE IF NOT EXISTS apicalls (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    span_id TEXT,
    task_id TEXT,
    section TEXT,
    condition_id TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cache_creation_input_tokens INTEGER,
    cache_read_input_tokens INTEGER,
    total_input_tokens INTEGER,
    effective_cost_units REAL,
    model TEXT,
    created_at TEXT,
    seq INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_apicalls_session
    ON apicalls(session_id);
CREATE INDEX IF NOT EXISTS idx_apicalls_task
    ON apicalls(task_id);
CREATE INDEX IF NOT EXISTS idx_apicalls_condition
    ON apicalls(condition_id);
CREATE INDEX IF NOT EXISTS idx_apicalls_section
    ON apicalls(section);
```

### Accumulation boundaries

Accumulators are *queries*, not stored objects. Token totals
are computed on demand via SQL `GROUP BY`:

```sql
-- Per task
SELECT task_id, SUM(effective_cost_units) AS ecu,
       SUM(total_input_tokens) AS input,
       SUM(output_tokens) AS output
FROM apicalls WHERE session_id = ? GROUP BY task_id;

-- Per section
SELECT section, SUM(effective_cost_units) AS ecu
FROM apicalls WHERE session_id = ? GROUP BY section;

-- Per condition (cross-session, for harness)
SELECT condition_id, SUM(effective_cost_units) AS ecu,
       COUNT(*) AS api_calls
FROM apicalls GROUP BY condition_id;
```

### Key design decisions

- Record at the API call level, accumulate on demand
- No separate accumulator records — keep storage simple
- ECU normalizes across token types for fair comparison
- Opt-in: only active when `trace=True` on Memory init
- No new dependencies: `sqlite3` + stdlib only

---

## Pramāṇa — Measurement Harness

### Purpose

A controlled experiment mode for comparing collaboration
efficiency across memory configurations. The harness runs the
same question set under different avasthās (conditions) and
records everything needed for analysis.

### Six Avasthās (Experimental Conditions)

| ID | Name | Memory configuration |
|----|------|---------------------|
| C0 | Baseline | No smrti — all context in prompt |
| C1 | Procedural | Tasks store only |
| C2 | Proc + Episodic | Tasks + decisions |
| C3 | All stores | Tasks + decisions + facts |
| C4 | + Coherence | C3 + cross-answer validation |
| C5 | Full | C4 + dependency-aware retrieval |

The conditions form an ablation study: each adds one
capability to the previous. This isolates the marginal
contribution of each memory type.

### InstrumentedClient

A wrapper around the Anthropic client that intercepts API
responses and records token usage:

```python
class InstrumentedClient:
    """Wraps anthropic.Client to record token usage."""

    def __init__(self, client, tracer, session_id, condition_id=None):
        self.client = client
        self.tracer = tracer
        self.session_id = session_id
        self.condition_id = condition_id

    def messages_create(self, **kwargs):
        response = self.client.messages.create(**kwargs)
        self.tracer.record_api_call(
            session_id=self.session_id,
            usage=response.usage,
            model=response.model,
            condition_id=self.condition_id,
            metadata={"task_id": kwargs.get("metadata", {}).get("task_id")},
        )
        return response
```

No subclassing, no monkey-patching. The instrumented client
is composed, not inherited. Consumer code passes it where
it would pass the raw client.

### Harness config

```json
{
  "harness": {
    "conditions": ["C0", "C1", "C2", "C3", "C4", "C5"],
    "question_set": "questions_harness.json",
    "ordering": "fixed",
    "seed_data": {
      "facts": "seed/facts.jsonl",
      "decisions": "seed/decisions.jsonl"
    },
    "cost_ratios": {
      "r_input": 1.0,
      "r_output": 5.0,
      "r_cache_create": 1.25,
      "r_cache_read": 0.1
    },
    "model": "claude-sonnet-4-6",
    "temperature": 0.0
  }
}
```

### Harness runner

```python
class HarnessRunner:
    """Runs a question set under a single avasthā."""

    def __init__(self, config, condition_id, memory_path):
        self.config = config
        self.condition_id = condition_id
        self.mem = self._init_memory(condition_id, memory_path)

    def _init_memory(self, condition_id, path):
        """Configure memory stores per condition."""
        if condition_id == "C0":
            return None  # no memory
        mem = Memory(path, trace=True)
        # C1: only tasks; C2: tasks + decisions; etc.
        # Store availability controlled by condition
        return mem

    def run(self, questions):
        session = self.mem.traces.begin(
            mode="wood",
            metadata={"condition": self.condition_id}
        )
        for q in questions:
            self._answer_question(session, q)
        self.mem.traces.end(session.id)
```

### Key constraint

No new dependencies. Pure Python + stdlib + sqlite3. The
harness is part of smrti, not a separate tool.

---

## Vivecana — Export and Analysis

### Purpose

Export trace and token data in analysis-ready formats for
pandas, R, or any statistics tool.

### Export formats

**CSV:** One row per API call, with session, task, section,
condition, and all token fields. Ready for `pd.read_csv()`.

```csv
api_call_id,session_id,condition_id,task_id,section,input_tokens,output_tokens,cache_creation,cache_read,total_input,ecu,model,created_at
sm-a-abc12,sm-s-def34,C3,sm-7k2m4,financial,1200,450,0,800,2000,3650.0,claude-sonnet-4-6,2026-02-21T10:00:00Z
```

**JSON:** Nested structure with session-level summaries and
per-task breakdowns. For programmatic consumption.

```json
{
  "export_version": "1.0",
  "conditions": {
    "C3": {
      "sessions": 3,
      "total_ecu": 45200.0,
      "total_api_calls": 127,
      "tasks": {
        "sm-7k2m4": {
          "ecu": 3650.0,
          "api_calls": 8,
          "quality_score": null
        }
      }
    }
  }
}
```

### CLI

```bash
# Export all trace + token data as CSV
smrti.py harness export --format csv > results.csv

# Export summaries per condition
smrti.py harness export --format json --summary > summary.json

# Export a single session
smrti.py harness export --session sm-s-abc12 --format csv
```

### Quality scores

Quality is assessed externally (human rater, blind to
condition) and merged into the export:

```bash
# Import quality scores from a rubric file
smrti.py harness quality-import rubric_scores.csv

# rubric_scores.csv format:
# task_id,condition_id,completeness,specificity,coherence,actionability,integration
# sm-7k2m4,C3,4,5,3,4,5
```

Once imported, artha (ECU per quality-point) can be computed.

---

## Artha — Economy Metric

### The fourth dimension

RFC 003 P4 proposed three session metrics: momentum, reach,
and complementarity. Token accounting enables a fourth:

**Economy (artha).** ECU per quality-point — how many
effective cost units does it take to produce one unit of
assessed quality?

```
artha = total_ecu / mean_quality_score
```

Lower artha means more efficient collaboration: less token
spend per unit of quality. The metric is meaningful only when
comparing across conditions with the same question set and
quality rubric.

### Interpretation

| artha | Interpretation |
|-------|---------------|
| Low, stable | Efficient collaboration. Memory is working. |
| High, declining across conditions | Memory is reducing cost progressively. |
| Low C0, rising with memory | Memory adds overhead without quality gain. |
| High everywhere | Hard question set or inefficient model usage. |

Artha is not a standalone score. It is comparative — it
answers: *does adding this memory capability improve the
cost-quality ratio?*

### The four dimensions together

| Metric | Question it answers | Source |
|--------|-------------------|--------|
| Momentum | How fast is the session flowing? | Span timestamps |
| Reach | How much of the question set was touched? | Span targets |
| Complementarity | Who contributed what? | Span actors |
| Economy (artha) | How efficient is the collaboration? | Token accounting + quality rubric |

---

## Research Protocol

### Quality rubric

Five dimensions, each scored 1–5 by a human rater blind to
experimental condition:

| Dimension | 1 (low) | 5 (high) |
|-----------|---------|----------|
| Completeness | Major gaps | All parts addressed |
| Specificity | Generic, no details | Concrete numbers, dates, examples |
| Coherence | Contradicts other answers | Consistent across section |
| Actionability | Vague intentions | Clear next steps |
| Integration | Ignores related questions | References and builds on related answers |

Mean quality score = arithmetic mean of the five dimensions.

### Statistical plan

- **Primary comparison:** ECU across C0–C5 for the same
  question set
- **Secondary comparison:** Quality scores across conditions
- **Derived:** Artha (ECU/quality) across conditions
- **Minimum sessions:** 3 per condition (18 total) for
  variance estimation
- **Analysis:** Paired comparison (same questions across
  conditions eliminates question-difficulty confound)
- **Reporting:** Effect sizes with confidence intervals;
  no p-value thresholds without pre-registration

### Threats to validity

- **Internal:** Model behavior may vary across runs even at
  temperature 0 (sampling is not fully deterministic)
- **Construct:** ECU is a proxy for cost, not actual cost
  (ratios are approximate)
- **External:** Results from one question set / one domain
  may not generalize
- **Rater bias:** Single rater introduces subjectivity;
  mitigated by blind-to-condition scoring

---

## Sanskrit Lexicon

Terms used in this RFC and their philosophical grounding:

| Sanskrit | Devanagari | Meaning | Maps to |
|----------|------------|---------|---------|
| kartā | कर्तृ | the doer, agent | Actor (human or model) |
| kriyā | क्रिया | the act, deed | Span (unit of work) |
| sākṣin | साक्षिन् | the witness | Tracer itself |
| saṃcaya | संचय | accumulation, gathering | Token accumulator |
| pramāṇa | प्रमाण | valid means of knowledge | Measurement harness |
| artha | अर्थ | purpose, economy | Economy metric (ECU/quality) |
| satra | सत्र | session, prolonged ceremony | Session |
| avasthā | अवस्था | state, condition | Experimental condition |
| vivecana | विवेचन | discernment, analysis | Export/analysis |
| pratītya | प्रतीत्य | in dependence on | Interbeing (co-arising) |
| sahaja | सहज | co-born, arising together | Interbeing (short form) |

The naming follows Advaita Vedānta's analysis of action
(kartā–kriyā–sākṣin) and Indian epistemology's theory of
valid knowledge (pramāṇa). See `docs/papers/bibliography.bib`
entries `deutsch1969advaita` and `mohanty2000classical`.

---

## Implementation Path

| Phase | Work | Touches |
|-------|------|---------|
| 1 | `Span` and `Session` dataclasses | `memory/models.py` |
| 2 | `TracerStore` with begin/span/end/query | `memory/traces.py` (new) |
| 3 | JSONL + SQLite storage for traces | `memory/storage.py` |
| 4 | `Memory.__init__` gains `trace=` flag, wires TracerStore | `memory/__init__.py` |
| 5 | CLI: `smrti.py memory traces` | `smrti.py` |
| 6 | Metrics derivation (momentum, reach, complementarity) | `memory/traces.py` |
| 7 | `ApiCall` dataclass and saṃcaya storage | `memory/models.py`, `memory/traces.py` |
| 8 | `InstrumentedClient` wrapper | `memory/instrument.py` (new) |
| 9 | ECU computation and accumulation queries | `memory/traces.py` |
| 10 | Pramāṇa harness runner and config | `memory/harness.py` (new) |
| 11 | Vivecana export (CSV/JSON) and quality import | `memory/export.py` (new), `smrti.py` |
| 12 | Synthesis integration (session_patterns, complementarity) | `memory/synthesis.py` |
| 13 | Archival and compaction | `memory/traces.py` |
| 14 | Instrument interactive workflows | consumer code (not in library) |

Phases 1–5 are the tracer MVP. Phases 6 adds session metrics.
Phases 7–9 add token accounting (saṃcaya). Phases 10–11 add
the measurement harness (pramāṇa) and export (vivecana).
Phases 12–13 are refinements. Phase 14 is consumer-side.

---

## Alternatives Considered

### A1: OpenTelemetry-based tracing

Rejected. OpenTelemetry is designed for distributed systems
with network hops, sampling rates, and collector infrastructure.
smrti traces are local, append-only, and human-readable. The
conceptual model (spans, nesting) is borrowed; the implementation
is not.

### A2: Traces as task metadata

Rejected. Stuffing span data into task `metadata` fields would
couple trace granularity to task granularity. A single question
might generate 20 spans across retrieval, drafting, correction,
and finalization. This is too much for a metadata dict and loses
the temporal ordering that makes traces useful.

### A3: Separate JSONL per session

Considered. One file per session (e.g., `traces/sm-s-abc12.jsonl`)
would make archival trivial — delete the file. But it breaks the
single-file pattern that makes `git diff` and drift detection
simple. A single `traces.jsonl` with archival via index removal
preserves the pattern.

### A4: No tracer — derive process from diffs

Considered. In theory, you could reconstruct a session by looking
at git diffs on the JSONL files: what tasks changed, what decisions
were created, what facts were added. In practice, this misses
everything that *didn't* result in a write: retrievals that informed
thinking, corrections that were verbal, redirections that changed
approach. The interesting part of a session is often what was
considered but not persisted.

---

## Trade-offs Accepted

- **Write amplification.** Every interesting event in a session
  becomes a JSONL append. A 50-question session might generate
  200+ spans plus the session record. Acceptable because JSONL
  appends are cheap (no seek, no lock) and compaction handles
  deduplication from updates.

- **Summary subjectivity.** Session summaries and span descriptions
  are model-generated. They are the model's perspective on what
  happened, not ground truth. This parallels the contribution
  tagging trade-off from RFC 003: the purpose is reflection,
  not measurement.

- **Opt-in default.** Tracing is off by default (`trace=False`).
  Users who don't know about tracing don't get it. The alternative
  — on by default — would generate JSONL data that confuses users
  who haven't read this RFC. Opt-in is the safer default; it can
  be flipped once the feature is proven.

- **No real-time dashboard.** The tracer records events after the
  fact. There is no live span viewer. The value is in post-session
  review, not live monitoring.

---

## Open Questions

1. **Span granularity.** How fine-grained should automatic
   instrumentation be? Every tool call? Every paragraph drafted?
   Every fact retrieved? The answer probably depends on the
   consumer — the library should make it easy to emit spans at
   any granularity and let the consumer decide.

2. **Cross-session spans.** If a task is worked on across three
   sessions, should there be a way to trace the full history of
   that task across sessions? The `target` field enables this
   (query all spans where `target=sm-7k2m4`), but a dedicated
   `timeline()` query is proposed above. Is it sufficient?

3. **Trace export format.** Should traces be exportable to a
   standard format (Chrome trace JSON, Perfetto) for
   visualization? Interesting but not MVP.

4. **Human span recording.** How does the human's contribution
   get recorded? In the queen's garden (continuous conversation),
   the model observes human input and can emit spans. In the wood
   (separate sessions), human input may not be visible to the
   tracer. This may require explicit human span calls in some
   workflows.

5. **Archival threshold.** 90 days is arbitrary. Should archival
   be configurable per deployment? Should it be based on span
   count rather than time? Both?

---

## References

Internal:
- RFC 002: Memory Layer Specification
- RFC 003: Recursive Context and Complementary Cognition
- RFC 004: smrti — Rename and Typed Memory

Memory systems:
- Patel, D. & Patel, S. (2026). ENGRAM: Typed memory stores.
  arXiv:2511.12960.
- Mem0 Team (2025). Mem0: Production-ready AI agents with
  long-term memory. arXiv:2504.19413.
- Packer et al. (2024). MemGPT: LLMs as operating systems.
  arXiv:2310.08560.

Token efficiency:
- Han et al. (2025). TALE: Token-budget-aware reasoning.
  arXiv:2502.07404.
- Anthropic (2024). Prompt caching with Claude.
  docs.anthropic.com.

Complementarity:
- Hemmer et al. (2024). Complementary team performance.
  ACM Computing Surveys.
- Vaccaro et al. (2024). When combinations of humans and AI
  are useful. Nature Human Behaviour.

Philosophical grounding:
- Deutsch, E. (1969). Advaita Vedānta: A Philosophical
  Reconstruction. (sākṣin, kartā, kriyā)
- Mohanty, J.N. (2000). Classical Indian Philosophy.
  (pramāṇa theory)
- Hanh, T.N. (1998). Interbeing. (pratītyasamutpāda)

Infrastructure (conceptual inspiration, not adopted):
- OpenTelemetry Specification: opentelemetry.io/docs/specs/otel/

Full bibliography: `docs/papers/bibliography.bib`

---

*"The witness is not the actor. It is that which remains when
the acting stops — the unchanging light by which the changes
are seen."*

*This RFC proposes a witness for collaborative cognition. Not
to judge the process — to remember it.*
