# RFC 012: smṛti-bench — Rationale and Design

**Status:** Implemented
**Author:** Aaron Johnson
**Created:** 2026-03-18
**Parent:** RFC 004

## Purpose

Document why smṛti-bench exists, what it measures, and how the
scoring system works.

---

## Problem

AI agents start every session from zero. They can read the codebase,
but they have no record of decisions made, rationale behind choices,
task status, or deferred work. When asked "why did we choose
Supabase?", an agent without memory either admits ignorance or
hallucinates a plausible answer.

smrti gives agents persistent structured memory via MCP. But
"persistent memory" is only valuable if it actually improves
responses. smṛti-bench measures whether it does.

## What we test

The bench runs a battery of 6 prompts against a seeded fixture —
a fake Flutter project ("trellis") with facts, decisions, and tasks
stored across smrti's three typed stores.

Each prompt targets a different memory capability:

| Prompt | Tests | Store exercised |
|--------|-------|-----------------|
| PROMPT_01 | Fact recall (project name, language) | Semantic (facts) |
| PROMPT_02 | Decision rationale (why Supabase over Firebase) | Episodic (decisions) |
| PROMPT_03 | Task status (what's open vs closed) | Procedural (tasks) |
| PROMPT_04 | Coherence (consistent with prior decisions) | Episodic (decisions) |
| PROMPT_05 | Deferred recall (why offline sync was deferred) | Episodic (decisions) |
| PROMPT_06 | Hallucination trap (ORM not in memory) | Absence detection |

## Two arms

**Baseline** — agent runs in an empty directory with no memory tools.
Correct behavior: admit ignorance. Pass = no hallucination.

**smrti** — agent has MCP tools connected to the seeded fixture.
Correct behavior: query memory stores and answer accurately.
Pass = expected keywords present, no traps triggered.

## Three platforms

The same battery runs against Claude Code, Gemini (API), and
Antigravity. This tests whether the MCP memory layer works
across different agent platforms, not just one.

## Scoring: ASP (Answer Set Programming)

Python extracts text predicates from each response (keyword
presence, ignorance signals, assertion phrases). Clingo
evaluates declarative rules to derive grades.

Three rule sets:

| File | Scope | Purpose |
|------|-------|---------|
| `scoring.lp` | Per-prompt | Grade derivation + integrity constraints |
| `coherence.lp` | Per-run (all prompts) | Cross-prompt consistency checks |
| `regression.lp` | Cross-run | Detect regressions between consecutive runs |

### Why ASP over Python

The grading logic involves negation ("pass if NOT missing keywords
AND NOT trap triggered AND NOT error"), excuse chains ("hallucination
is excused IF admits ignorance AND no assertions"), and cross-prompt
reasoning ("contradiction if pass on P1 but fail on P2"). These are
natural in ASP and awkward in imperative code. The `.lp` files also
serve as a readable specification of what "correct" means.

## Fixture design

The fixture is intentionally non-trivial:

- Architecture answers (PROMPT_02, PROMPT_04) live **only** in the
  decisions store — not duplicated in facts. The agent must use
  `decision_list` / `decision_get`, not just `fact_search`.
- The deferral rationale (PROMPT_05) lives in a decision with no
  explicit `task_id` link. The task (PROMPT_03) says "deferred to v0.3"
  but not why. Full answer requires cross-store synthesis.
- Noise facts (team conventions, MVP timeline, rate limiting) and
  a noise task (analytics evaluation) test filtering.
- PROMPT_06 tests absence — the ORM fact is intentionally missing.
  Naming any ORM is a hallucination failure.

## What success looks like

- Baseline: 6/6 PASS (never hallucinates project-specific content)
- smrti: 6/6 PASS (recalls accurately from all three stores)
- No coherence warnings (consistent across related prompts)
- No regressions between runs

## Future work

- **Weighted run scores** — `#minimize` to rank runs by quality
  when the prompt battery grows beyond 6
- **UNSURE decomposition** — choice rules to classify ambiguous
  responses instead of a catch-all grade
