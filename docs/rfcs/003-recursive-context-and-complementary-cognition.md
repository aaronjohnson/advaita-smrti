# RFC 003: Recursive Context and Complementary Cognition

**Status:** Partially Implemented (v0.4.0)
**Author:** Aaron Johnson + Claude
**Created:** 2026-02-05
**Implemented:** 2026-02-17 (P1, P3); P2, P4 deferred
**References:** Zhang, Kraska, Khattab. "Recursive Language Models." arXiv:2512.24601v2, Jan 2026.
**Parent:** RFC 002 (Memory Layer Spec)

## Implementation Status

| Proposal | Status | Notes |
|----------|--------|-------|
| P1: Dependency graph | Implemented (PR #4) | `blocks`/`blocked_by` wired from config `depends_on` |
| P2: Contribution tagging | Not implemented | Deferred — build when session instrumentation is needed |
| P3: Coherence checks | Implemented (PR #4) | Section-scoped checks, finding categories, `CoherenceReport` model |
| P4: Session dimensions | Not implemented | Deferred — momentum/reach/complementarity metrics not yet needed |

---

---

## Summary

This RFC asks whether the Recursive Language Models (RLM) paper offers
anything genuinely useful to form-copilot, or whether it's an interesting
paper about a different problem. The honest answer: **some of it fits
perfectly, some of it is a stretch, and the most interesting part isn't
in the paper at all** --- it's the question of what exactly happens
between two minds when they sit down to answer hard questions together.

We propose three things:

1. **Activate the dependency graph** that already exists in the memory layer
2. **Instrument complementary cognition** --- not machine metrics, but a
   record of which mind contributed what
3. **Recognize that the interactive menu's sub-sessions are already
   sub-LM calls** --- RLM gives us vocabulary for what we built

*The ideas in this RFC are inspired by the RLM paper. Where we draw
on their concepts --- dependency graphs, recursive decomposition,
periodic synthesis --- we cite the source.*

---

## Motivation: What the Paper Actually Says

RLM (Zhang et al., 2026) addresses **context rot** --- the degradation
that occurs when you stuff too much text into a language model's context
window. Their solution: don't. Instead, store context as a variable in a
REPL environment and let the model programmatically interact with it,
recursively decomposing problems into sub-problems.

Key claims:

- RAG breaks down on multi-hop reasoning (retrieving document A is
  useless unless you already understand document B)
- Treating work as a dependency graph enables parallel solving and
  explicit information flow
- A small model with RLM scaffolding outperforms a large model running
  blind (RLM + GPT-5-mini beats vanilla GPT-5 by 34%)
- Scaffolding alone is insufficient --- learned optimization is essential

The paper's mental model shift: **documents are dependency graphs, not
storybooks.** Don't read start-to-finish. Map the structure, identify
what depends on what, solve leaves first, synthesize upward.

---

## What Already Fits (We Built This Without Knowing)

The memory layer (RFC 002) is already an RLM-style environment:

```
┌──────────────────────────────────────────────────┐
│  RLM Concept              Form Copilot Analog    │
├──────────────────────────────────────────────────┤
│  Context as variable  →   tasks.jsonl            │
│  REPL sandbox         →   Claude Code session    │
│  Sub-LM results       →   Context notes          │
│  Recursive calls      →   Queen's garden loop    │
│  Dependency DAG        →   blocks/blocked_by      │
│                            (fields exist, unused) │
└──────────────────────────────────────────────────┘
```

The queen's garden session that completed 49/49 questions *was* an RLM
in practice. The model never held all 49 answers in its context window.
It held the current question, retrieved relevant context notes from the
JSONL, composed an answer, banked new context, and moved on. Context
lived outside the window as a programmatic object.

The difference: we did this by hand. RLM proposes the model should
decide its own decomposition strategy. For form-copilot, the *human*
decides. That's not a limitation --- it's the point.

### Parallel Evolution

Form-copilot v0.1.0 shipped January 27, 2026. The RLM paper hit arXiv
late December 2025 (v2: January 28, 2026). Neither knew about the
other. Same pressure (context limits degrade quality over long
sessions), same solution (structured resets with persistent external
memory), different domains.

The Python interactive menu --- launching a fresh Claude session per
question with scoped context, getting an answer, piping it back ---
was built to add structure at natural points where the context window
could be reset. That IS the RLM architecture: root process, scoped
recursive calls, results returned to parent. The vocabulary came
later; the instinct came first.

### Hard Wipe vs. Compaction: An Open Question

The queen's garden (one continuous session, 49 questions) hit context
compaction. The system compressed earlier messages to make room. By
question 40-something, details from question 6 were no longer in
active memory --- they had to be retrieved from the JSONL.

The wood approach (fresh session per question) would give each answer
a clean context window with only:

- The question and its helper text
- Answered dependencies (from memory layer)
- Relevant context notes (from memory layer)
- Nothing else

No compaction needed. No context rot. The RLM paper's core claim is
that small focused windows with structured retrieval beat one giant
window with everything in it.

**Trade-off:** The queen's garden produces more *connected* answers
(creative leaps between questions, lateral associations). The wood
produces more *consistent* answers (no rot, no compaction artifacts).
A hybrid --- queen's garden in bursts of 5-8 related questions, hard
reset between bursts, coherence check at each boundary --- may be
the best of both.

This is testable. Same questions, both approaches, compare coherence
and contradiction rates. Future work.

---

## What Doesn't Fit (And Why That's Fine)

### Recursive sub-LM calls

RLM spawns isolated child language model instances to process subsets
of data. Form-copilot's interactive menu *already does this* --- press
`[C]` on a question and it launches a Claude Code sub-session with
scoped context, gets an answer, and pipes it back to the parent menu.
That IS the RLM pattern: root process → scoped sub-call → result
returned to parent.

The queen's garden collapses this into a single session (no sub-calls,
one continuous conversation). The wood preserves the recursive
structure. Both are valid --- they serve different modes of thinking.

**Decision:** Recognize the interactive menu as an existing sub-LM
architecture (inspired by what RLM formalizes). Don't add sub-calls
to the queen's garden --- its value is continuity of conversation.

### Automatic decomposition

RLM lets the model decide how to break down the problem. But the user
already knows their form. They know that the financial section is
stressful and should come after they've built momentum on the business
overview. They know that Q4 (goals) and Q5 (vision) should be
consecutive because the thinking flows. Overriding this with automatic
decomposition would remove the human's agency, which is the opposite
of what we're doing.

**Decision:** The human chooses the order. The system can *suggest* an
order based on dependencies, but never impose one.

### Benchmark-style accuracy metrics

The paper measures accuracy on OOLONG and BrowseComp-Plus benchmarks.
Form-copilot has no ground truth --- there is no "correct" answer to
"What is the nature of your business?"

But the absence of accuracy does not mean the absence of measurable
progress. There is **completion** (how many questions answered, how
many dependencies resolved). There is **awareness** (does the user
understand their own situation better after answering Q15 than
before?). There is **progress** (are later answers more specific,
more grounded, more connected to earlier ones than the first few?).

These aren't benchmarks. They're closer to what therapy measures:
not whether the patient gave the "right" answer, but whether the
process moved them forward.

**Decision:** Don't measure correctness. Measure completion,
awareness, and coherence as dimensions of progress.

---

## What's Genuinely Interesting: Complementary Cognition

The question that matters isn't "can we make the machine faster?" It's
"what is each mind actually doing in this collaboration?"

During the queen's garden session, a pattern emerged that has nothing
to do with RLM and everything to do with how two different kinds of
thinking complement each other:

### What the human brings

- **Domain knowledge**: The correct company name, not the model's
  approximation. The actual job title, the real department. The
  specific, lived details that make an answer authentic vs. generic.

- **Judgment calls**: "Don't list that as a strength --- I've
  struggled with it." The values and self-knowledge that determine
  what's honest vs. what merely sounds good.

- **Creative leaps**: Lateral connections between industries, people,
  and experiences that a model wouldn't make because they come from
  a life lived, not a corpus searched.

- **Emotional truth**: The material that transforms a form answer
  from competent to compelling. No model generates this.

### What the model brings

- **Holding the thread**: When dozens of questions span financial
  details, competitive analysis, marketing budgets, and personal
  history, the human mind can't hold all of it simultaneously. The
  model can --- not in its context window (that's the whole point
  of the memory layer) but through systematic retrieval: "You
  mentioned this person in Q22 --- should we reference that
  relationship in Q31?"

- **Structural coherence**: Making sure the expenses question and
  the cash flow question don't contradict each other. Noticing that
  a budget in one section is too low relative to the targets in
  another. Cross-referencing that's tedious for a human but trivial
  for a machine with structured data.

- **Articulation**: The human speaks in fragments and associations.
  The model hears the scattered pieces and drafts a coherent
  paragraph that the human can then correct, refine, or reject.

- **Patient retrieval**: "What did I say about insurance four
  questions ago?" The model doesn't forget, doesn't get bored,
  doesn't lose the thread when attention wanders. This is not
  intelligence --- it's a complementary capability. A prosthetic
  for working memory.

### Neurodivergent-Friendly by Design

Form-copilot works well for minds that operate in bursts, make
lateral leaps, and lose the thread of what they said three questions
ago. The traditional approach --- sit down, read all questions,
answer them linearly, maintain consistency --- assumes a kind of
sustained sequential attention that not everyone has.

The queen's garden workflow works because:

- **No forced order.** Work on what interests you. The memory layer
  catches the dependencies you skip over.
- **Context notes as external working memory.** You have a thought
  about Q31 while answering Q6? Bank it. It'll be there when you
  get to Q31.
- **The model as a gentle checkpoint.** "You mentioned a budget
  increase --- should the expenses question reflect that?" The model
  being *consistent* complements a mind that's better at divergent
  than convergent thinking.

The wood where things have no names works because:

- **Solo pace.** No conversation partner means no social energy drain.
  Just you and the questions, at whatever speed feels right.
- **Structure without surveillance.** The menu tracks progress without
  judgment. Come back after a week. It remembers where you were.

This isn't in the RLM paper. But it's the actual value proposition
of form-copilot, and any metrics we collect should measure whether
this complementary relationship is working.

### Interbeing, Not Autonomy

There is a concept in Zen Buddhism --- *non-duality* (*advaita* in
Sanskrit, *not-two*). Thich Nhat Hanh coined the word **interbeing**:
the flower contains the rain, the soil, the sun. Not metaphorically.
Actually. The parts are not separate from the whole.

Applied here: a collaboratively-written answer isn't "the human's" or
"the model's." It's what emerged from the collaboration. The human
brought the concept and the corrections. The model brought structure
and cross-references. The answer is neither mind alone.

So much of the conversation around generative AI is framed as autonomy
and replacement --- will AI take jobs, will it think for itself, should
we fear it. Form-copilot proposes a different frame: **two kinds of
thinking, not separate, producing something neither could alone.** A
thinking journal that two minds wrote together, stored in a format
that outlives both the session and the model.

The memory layer makes this durable. Not just the answers, but (with
the additions proposed here) the record of *how the thinking happened*
--- who contributed what, where coherence emerged, where it broke down.
A journal of interbeing.

### Beyond Forms: The Socratic Extension

A config doesn't have to come from a government application. The
dependency graph and recursive structure could serve open-ended
questions: "What should I do with my life?" "What does my business
actually solve?"

The system could generate sub-questions (Socratic method, therapeutic
framing, structured reflection) and arrange them as a dependency
graph. Answer the leaves, synthesize upward. This is RLM's recursive
decomposition applied not to documents but to *self-knowledge*.

This is noted here as a direction, not a proposal. It would require
a different kind of config --- one generated collaboratively rather
than extracted from a form. But the architecture supports it today.

---

## Proposal: What to Actually Build

### P1: Activate the Dependency Graph

The memory layer has `blocks` and `blocked_by` fields on every task.
They are empty across all 63 tasks in the current dataset. This is
the single most valuable idea from the RLM paper: **make the structure
explicit.**

```
Q1 (business nature)
├── Q4 (6-12 month goals)
│   └── Q5 (2-3 year vision)
├── Q6 (qualifications)
│   └── Q29 (competitive advantage)
├── Q22a (target market)
│   ├── Q22b (customer acquisition)
│   └── Q23a (pricing)
└── Q15 (income sources)
    ├── Q16 (monthly expenses)
    └── Q17 (cash flow)
```

**Implementation:** When loading a config, optionally include a
`depends_on` field per question. The queen's garden workflow can
use this to suggest order ("Q4 depends on Q1 --- want to do Q1
first?") without enforcing it. The wood can display a readiness
indicator: `[R]` for ready (all dependencies answered), `[B]` for
blocked (upstream answers missing).

**Not proposed:** Automatic dependency inference. The human or the
config author defines dependencies. The system respects them.

### P2: Contribution Tagging

Record, per answer, what each participant contributed. Not as a
score --- as a log.

```jsonl
{
  "id": "fc-abc12",
  "title": "Q:4 - Short-term goals",
  "metadata": {
    "contributions": {
      "human": [
        "core business concept",
        "key partnership identified",
        "revenue framing preference",
        "factual correction on company name"
      ],
      "model": [
        "structured answer from scattered input",
        "cross-referenced startup costs question",
        "surfaced context note from Q1",
        "flagged budget inconsistency"
      ]
    }
  }
}
```

**Why:** This is the data that answers "how does my mind work?" Over
a full application, you can see: when does the human provide raw
material vs. editorial judgment? When does the model retrieve vs.
synthesize? Are there sections where the human does almost everything
(emotional questions, risks) vs. sections where the model does the
heavy lifting (financial consistency, cross-references)?

**Collection:** At save time, the model logs a brief contribution
summary. No extra prompting needed --- the model already knows what
it did and what the human provided, because it just had the
conversation.

### P3: Coherence Checks (Inspired by RLM Periodic Synthesis)

A **section boundary pause**: after completing the last question in a
section (e.g., finishing Q19 closes "Financial Due Diligence"), the
system runs a coherence check before moving on. Not after every N
answers --- after each *section*, which is the natural unit of
completeness.

What it looks like in practice:

```
── Section complete: Financial Due Diligence (5/5) ──

Coherence check:

  ● Monthly expenses question says $X. Cash flow question assumes
    $Y. These reference different time periods. Intentional?

  ● Income sources mention a recurring cost not reflected in
    startup costs. Should it be added?

  ● Strong thread: three answers in this section reference the
    same life transition. This could anchor the financial narrative.

  Continue to next section? [Y/n/fix]
```

The check is **blocking** --- it pauses the flow and asks the human
to acknowledge or act. This is metacognition: the process reflecting
on itself in motion. The human can:

- **Continue** (the inconsistency is intentional or minor)
- **Fix** (go back and revise an answer)
- **Note** (bank a context note for later sections)

The coherence check results are saved to the memory layer as a
`coherence-check` task type, making them durable. Come back in a
year, and you can see not just the answers but the moments where
the process paused and noticed something.

Implementation: use the synthesis module's `patterns()` and
`connections()` functions, scoped to the just-completed section
plus any cross-section dependencies.

### P4: Session Dimensions (Three Metrics, Not Thirty)

If we must have numbers, keep it to three that actually mean something:

**Dimension 1: Momentum**
- *What it measures:* Is the session flowing or stalling?
- *Signal:* Time between answer saves, excluding idle periods
- *Unit:* Minutes per answer (rolling average)
- *Useful because:* A sudden increase means something is blocking ---
  a hard question, a contradiction, confusion about what's being asked.
  The system could notice and offer help.

**Dimension 2: Reach**
- *What it measures:* How connected is the answer graph?
- *Signal:* Context notes created, cross-references made, dependency
  edges traversed
- *Unit:* Edges per node (graph density)
- *Useful because:* A high-reach session produces a coherent narrative.
  A low-reach session produces 49 independent answers that don't talk
  to each other. This is the thing that distinguishes form-copilot
  from "paste each question into ChatGPT separately."

**Dimension 3: Complementarity**
- *What it measures:* Are both minds contributing, or is one carrying?
- *Signal:* Contribution tags from P2, aggregated per section
- *Unit:* Ratio of human-originated to model-originated elements
- *Useful because:* If the model is doing everything, the answers
  will be generic. If the human is doing everything, the memory layer
  isn't earning its keep. The sweet spot is balanced contribution
  where each mind does what it's good at.

---

## What This Is Not

This is not an agent framework. Form-copilot does not autonomously
complete forms. It does not optimize for speed. It does not replace
human judgment with machine inference.

The RLM paper solves the problem of making machines handle more
context. Form-copilot solves the problem of making humans handle
hard questions. The memory layer is the bridge: it gives the machine
persistence and gives the human a safety net.

Adopting RLM wholesale would mean treating the form as a computation
to be optimized. That misses the point. The 49-question session
worked because a person sat with hard questions, said honest things,
got gentle pushback, revised their thinking, and produced something
that sounds like them. The model helped. The memory layer helped.
But the value was in the thinking, not the throughput.

---

## Success Criteria

This proposal succeeds if:

1. **Dependency graph is useful in practice.** When a new user loads
   a config with dependencies, the suggested order feels natural, not
   arbitrary. The `[B]`/`[R]` indicators in the wood help rather than
   annoy.

2. **Contribution logs reveal something interesting.** After a full
   session, reading the contribution summary teaches the user something
   about their own thinking patterns they didn't already know.

3. **Coherence checks catch real problems.** At least one contradiction
   or orphaned reference is caught during a session that the user would
   not have noticed on their own.

4. **Three metrics, not thirty.** We resist the urge to instrument
   everything. Momentum, reach, and complementarity tell the story.
   If they don't, we have the wrong three --- not too few.

---

## Alternatives Considered

### A1: Full RLM adoption (recursive sub-calls, automatic decomposition)

Rejected. Form-copilot is a conversation tool, not a computation
engine. Spawning sub-LM instances to process form sections in parallel
is technically cool and spiritually wrong. The user wants a thought
partner, not a distributed system.

### A2: No RLM adoption (paper is interesting but irrelevant)

Rejected, but only barely. Most of the paper *is* irrelevant to our
use case. But the dependency graph activation and periodic synthesis
are genuine improvements that we should have built already. The paper
gave us the vocabulary and the inspiration.

### A3: Pure machine metrics (tokens/answer, questions/hour, API cost)

Rejected. These measure the machine's efficiency, not the
collaboration's quality. A session that takes 4 hours and produces
deeply honest answers is better than one that takes 1 hour and
produces generic ones. Optimizing for throughput would optimize for
the wrong thing.

### A4: Full cognitive profiling (detailed executive function metrics)

Rejected on privacy and scope grounds. Recording "time spent
unfocused" or "attention shifts per question" crosses from useful
self-knowledge into surveillance. Contribution tagging is the right
level of granularity: what each mind *did*, not how each mind
*behaved*.

---

## Trade-offs Accepted

- **Dependency graphs add upfront work.** Someone has to define
  question dependencies in the config. For a large application (40+
  questions), this is maybe 30 minutes of thought. For a quick 10-
  question form, it's probably not worth it. We make it optional.

- **Contribution tagging is subjective.** The model's summary of "what
  it contributed" is its own assessment, not ground truth. This is
  acceptable because the purpose is reflection, not measurement.

- **Three metrics means missing things.** Momentum, reach, and
  complementarity don't capture everything. They don't capture answer
  quality, emotional difficulty, or the user's satisfaction. That's
  intentional --- those things resist quantification, and pretending
  otherwise would produce misleading numbers.

---

## Implementation Path

| Phase | Work | Touches |
|-------|------|---------|
| 1 | Add optional `depends_on` to config schema | `validate_config.py`, `CONFIG.md` |
| 2 | Wire `depends_on` → `blocks`/`blocked_by` at task creation | `memory/tasks.py` |
| 3 | Add `[R]`/`[B]` readiness indicators to interactive menu | `form_copilot.py` |
| 4 | Add `contributions` field to task metadata at save time | queen's garden workflow |
| 5 | Add periodic coherence check (every 5 answers) | `memory/synthesis.py` |
| 6 | Add `metrics.jsonl` for momentum/reach/complementarity | `memory/` module |
| 7 | Update example configs with question dependencies | `examples/` |

---

## References

- Zhang, Kraska, Khattab. "Recursive Language Models." arXiv:2512.24601v2. Jan 2026.
- RFC 000: Form Copilot Baseline Specification
- RFC 002: Memory Layer Specification
- Prime Intellect. "Recursive Language Models: The Paradigm of 2026."
- Carroll, Lewis. *Through the Looking-Glass*. Chapter III: "Looking-Glass Insects" (the wood where things have no names).

---

*"Would you tell me, please, which way I ought to go from here?"
"That depends a good deal on where you want to get to," said the Cat.*

*This RFC says: we know where we want to get to. It's not faster
throughput or deeper recursion. It's a better understanding of what
happens when two very different kinds of minds sit down with hard
questions and try to answer them honestly.*
