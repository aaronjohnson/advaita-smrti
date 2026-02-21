# Pratītya-Pramāṇa

**Measuring the Token Economics of Collaborative Memory
in AI-Human Work**

*A reproducible framework for evaluating how structured
external memory affects the efficiency and quality of
AI-human collaboration*

**Status:** Proposal
**Created:** 2026-02-21

---

## Abstract (draft, ~150 words)

We present *pratītya-pramāṇa*, a measurement framework for
studying how structured external memory affects the token
economics and output quality of AI-human collaborative work.
Existing benchmarks (SWE-bench, HumanEval) evaluate autonomous
task completion; existing memory systems (ENGRAM, Mem0, Zep)
report retrieval quality or cost savings for their own
implementations. No published framework measures the *process*
of collaboration — how token consumption, contribution
distribution, and coherence change as memory capabilities
are progressively enabled.

We define six experimental conditions (avasthās) ranging from
no external memory to full typed memory with coherence checking
and dependency-aware retrieval. Using smrti as a reference
implementation, we instrument collaborative sessions with
span-level tracing and per-API-call token accounting. We
report token economy (ECU per quality-point) across conditions
for a fixed question set, establishing baselines for future
comparison across memory systems, models, and task domains.

---

## The Gap

| System | What it measures | What it misses |
|--------|-----------------|----------------|
| SWE-bench | Did the agent complete the task? | Collaboration process |
| ENGRAM | Retrieval quality across store types | Token economics, human contribution |
| Mem0 | Latency and cost (own system only) | Controlled comparison methodology |
| Lumer et al. | Caching impact (infrastructure) | Cognitive impact on collaboration |
| Hemmer CTP | Complementarity potential/effect | Operationalization with trace data |
| Vaccaro | When combos beat individuals | Under what *memory* configurations |

Nobody measures: *How does the process of collaboration change
as you add structured external memory?*

---

## What Is Novel

The measurement methodology — not the memory system.

The paper's contribution is the **pramāṇa** (valid means of
knowing): the harness, the ablation design, the metrics, the
export format. smrti is the reference implementation. Any
memory system could be plugged into the same harness.

This makes the paper composable:
- Amplifies ENGRAM by measuring its impact on collaboration
- Amplifies Mem0 by providing controlled comparison methodology
- Amplifies Hemmer's CTP by operationalizing it with span-level
  trace data from actual AI-human sessions
- Amplifies Vaccaro's finding by asking: under what memory
  configurations do human-AI combos outperform individuals?

---

## Experimental Design

### Six Avasthās (Conditions)

| ID | Condition | Memory configuration |
|----|-----------|---------------------|
| C0 | Baseline | No smrti — all context in prompt |
| C1 | Procedural only | Tasks store enabled |
| C2 | Procedural + episodic | Tasks + decisions |
| C3 | All persistent stores | Tasks + decisions + facts |
| C4 | + Coherence checking | C3 + cross-answer validation |
| C5 | Full | C4 + dependency graph retrieval |

### Metrics

- **Saṃcaya** (token accumulation): input, output, cache-read,
  cache-creation tokens per API call
- **Artha** (economy): ECU per quality-point — normalized cost
  adjusted for output quality
- **Complementarity**: human/model contribution ratio per session
  (from span actor attribution)
- **Momentum**: spans per unit time (flow indicator)
- **Reach**: fraction of question set touched per session

### Controls

- Fixed question set (same questions across all conditions)
- Fixed ordering (deterministic question sequence)
- Same model and temperature across conditions
- Quality assessed by independent rubric (blind to condition)

---

## Data We Need

1. **Question set.** 15–20 questions from a structured
   application domain (e.g., grant narrative, clinical intake).
   Must be complex enough that memory configuration matters.

2. **Baseline sessions.** At least 3 sessions per condition
   (18 total minimum) to establish variance.

3. **Quality rubric.** 4–5 dimensions scored 1–5 by a human
   rater blind to condition. Dimensions: completeness,
   specificity, coherence, actionability, integration.

4. **Token accounting.** Per-API-call usage data from the
   Anthropic response `usage` object.

---

## Paper Structure

1. **Introduction** — the gap (nobody measures collaboration
   process as a function of memory configuration)
2. **Related work** — memory systems, token efficiency,
   complementarity theory
3. **Framework** — pramāṇa design, metrics, ablation avasthās
4. **Reference implementation** — smrti (brief, not the focus)
5. **Experiment** — one question set, 6 conditions, results
6. **Discussion** — what the data shows, limitations,
   generalizability
7. **Conclusion** — the framework is the contribution

---

## Target Venues

- arXiv pre-print first (establish priority)
- NeurIPS Workshop on Foundation Model Agents
- CHI (human-computer interaction — the interbeing angle fits)
- AAAI Workshop on AI-Assisted Decision Making

---

## What Makes It Durable

Specific tools (smrti, ENGRAM, Mem0) will evolve and be
replaced. A well-designed pramāṇa for studying AI-human
collaboration efficiency is useful regardless of which memory
system you're evaluating. The paper ages like a benchmark
paper, not like a system paper.

---

## Bibliography

See `../bibliography.bib` — shared across all papers in
this research program.
