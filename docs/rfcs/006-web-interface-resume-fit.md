# RFC 006: Web Interface — Resume Fit and Honest Discovery

**Status:** Concept
**Author:** Aaron Johnson
**Created:** 2026-02-20
**Parent:** RFC 004, RFC 005

## Purpose

Extend smrti beyond Claude Code and Python API to a
public-facing web interface. A visitor pastes a job
description; the system returns an honest assessment of
fit against the host's resume/experience, drawn from
smrti's semantic store.

---

## Problem

Today, smrti's knowledge is only accessible through:
- Claude Code sessions (developer tooling)
- Python API (`from memory import Memory`)

A recruiter, hiring manager, or company contact who has
received an application has no way to explore the
candidate's fit without scheduling a call. The candidate
has no way to pre-qualify opportunities without reading
every job description manually.

The gap: **no self-service discovery layer** between
"received a resume" and "scheduled a meeting."

---

## Proposal

### The visitor experience

1. Visitor arrives at a personal/professional site
2. Pastes a job description into a text box (or uploads PDF)
3. System computes fit against the host's experience
4. Returns:
   - **Fit likelihood** (high / moderate / low / unclear)
   - **Relevant experience** — tailored list drawn from
     facts store, honest, not fabricated
   - **Gaps or uncertainties** — areas where the fit is
     unclear, with follow-up questions the visitor could
     ask to clarify
   - **Work preferences** — full-time vs. contract vs.
     retainer, and what the host is currently open to
5. If fit is good: **call to action** to schedule an
   appointment to discuss a project or role
6. If fit is low: honest about it. Sets expectations.
   May suggest adjacent roles or referrals.

### What it is NOT

- Not a chatbot. One input, one structured response.
- Not a hallucination engine. Every claim traces to a
  fact in the semantic store with source attribution.
- Not a generic AI resume tool. It represents ONE person's
  actual experience, preferences, and constraints.

---

## How smrti fits

smrti becomes the **knowledge backend**:

```
┌─────────────────────────────────┐
│  Web UI (visitor-facing)        │
│  - Paste job description        │
│  - View fit assessment          │
│  - Schedule if good fit         │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  Fit Engine                     │
│  - Parse job requirements       │
│  - Query facts by section/label │
│  - Match requirements to facts  │
│  - Score fit, surface gaps      │
│  - Generate honest response     │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  smrti semantic store           │
│  facts.jsonl — skills, history, │
│  preferences, constraints       │
│  Curated by host, not generated │
└─────────────────────────────────┘
```

### Facts as the source of truth

The fit engine only claims what the facts store contains.
Example facts:

```
"10 years Python experience" (source: resume, confidence: 1.0)
"Led team of 5 on kiosk project" (source: portfolio, confidence: 1.0)
"Familiar with React, not expert" (source: self-assessment, confidence: 0.7)
"Prefers contract/retainer over full-time" (source: preference, confidence: 0.9)
"Open to full-time for the right fit" (source: preference, confidence: 0.6)
```

The response references these facts. The visitor sees
evidence, not claims. Low-confidence facts surface as
"may be relevant, worth discussing" rather than assertions.

### Work preference signaling

The facts store holds explicit preference facts:

| Preference | Signal |
|---|---|
| Contract (project-based) | Preferred — strongest fit |
| Retainer | Open — good for ongoing needs |
| Full-time | Selective — depends on role/culture |
| Remote | Required / preferred / flexible |
| Location | Constraints if any |

These shape the call to action. A recruiter filling a
full-time role sees "open to full-time for the right fit"
with an invitation to discuss. A company with a 3-month
project sees "this is the sweet spot" with a direct
scheduling link.

---

## Interfaces

### Option A: Static site + API

- Simple HTML/JS frontend (no framework needed)
- API endpoint that accepts job description text
- LLM call to parse requirements and match against facts
- Response rendered as structured HTML

### Option B: MCP server

- smrti exposed as an MCP tool
- Any MCP-compatible client can query fit
- Web UI is one client; Claude Desktop is another
- Richer interaction possible (follow-up questions)

### Option C: Both

- MCP server as the core interface
- Web UI as a thin client over MCP
- Claude Code sessions also use MCP for fact queries

Decision deferred to implementation.

---

## Tone and honesty

The system's voice should be:
- **Honest** — "I don't have deep experience in X" is
  a valid and valuable response
- **Specific** — "I led a 5-person team on a kiosk
  project for a day center" not "experienced team leader"
- **Curious** — when fit is unclear, ask the visitor
  what they're actually looking for rather than guessing
- **Respectful of the visitor's time** — if fit is low,
  say so early. Don't waste a meeting on a mismatch.

This is the advaita principle in practice: the interface
and the person are not separate. The system speaks as
the host would speak, with the host's actual knowledge
and the host's actual limitations.

---

## Prior art and references

- Nate B. Jones — ideas on AI-powered professional
  presence and self-service discovery (YouTube, potential
  subscription for deeper dive)
- Damian Galarza — context engineering and memory for
  AI agents (YouTube)
- Personal CRM / portfolio tools that do static
  presentation but not interactive fit assessment

---

## Open questions

1. **Privacy** — job descriptions pasted by visitors may
   contain confidential information. How do we handle
   data retention? Process and discard? Log for the host?
2. **Rate limiting** — prevent abuse without requiring
   login
3. **Fact curation** — who maintains the facts store?
   Host manually? Semi-automated from resume/portfolio?
4. **LLM dependency** — the fit engine needs an LLM for
   parsing and matching. Which provider? Cost per query?
   Can we do a first-pass with keyword matching and only
   escalate to LLM for ambiguous cases?
5. **Scheduling integration** — Calendly? Cal.com? Simple
   email link?
6. **Scope of v1** — is the MVP just the text box and
   fit response, or does it include the scheduling CTA?

---

## Relationship to other RFCs

- **RFC 004** — the semantic (facts) store is the
  knowledge backend for this interface
- **RFC 005** — ephemeral store could hold visitor
  session state during a fit assessment
- **RFC 003** — complementary cognition: the visitor
  brings the job context, the system brings the
  candidate knowledge. Neither has the full picture alone.
