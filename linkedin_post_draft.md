# LinkedIn Post Series: AI-Assisted Field Discovery → Development

## Post 1: "Beginning" (publish as beta development starts)

**Working title:** Using Claude Code as a field research partner

**Core narrative:** After a site visit at a day center for people experiencing homelessness, used form-copilot + Claude Code to process field notes through a structured discovery questionnaire — 43 questions, cross-referencing requirements, flagging gaps, and triaging what's answered vs. deferred. Turned a meeting's worth of notes into a specification draft and follow-up emails in the same session.

**Key points:**
- The meeting was human. The structured processing happened after, with the AI as a thinking partner to organize and cross-reference what was learned.
- Two memory systems working together: Claude Code's built-in MEMORY.md (brief, curated, auto-loaded each session) and a structured JSONL audit trail (detailed, append-only, queryable via SQLite index). One is the index card on the dashboard. The other is the filing cabinet.
- Discovery notes feed directly into development. No "translate field notes into tickets" step. The structured data IS the backlog.
- The system carries context across sessions. Next time I open the project, it knows where we left off, what's deferred, and to whom.

**Tone:** Practitioner sharing a workflow, not a product pitch. Specific enough to be useful. Honest about what worked.

**Open questions to revisit before publishing:**
- How much project detail is appropriate? (Client is a nonprofit, be respectful)
- Include form-copilot as an open source tool mention?
- Screenshots or just narrative?

---

## Post 2: "Middle/End" (publish after deployment or significant milestone)

**Working title:** What changed, what didn't work, and what surprised us

**Themes to track during development (update this list as we go):**
- [ ] Did MEMORY.md stay useful or get stale? Did we need to prune it?
- [ ] Did the JSONL audit trail matter? Did we ever go back to it?
- [ ] Did the SQLite index stay in sync or drift? Was it worth maintaining?
- [ ] Was the beta harness (DEPLOY_ENV build flag) clean in practice?
- [ ] Did the pip-installable package model work for Pi deployment?
- [ ] Did Express Pros engage with GitHub Issues?
- [ ] Did CC and staff actually use the beta to give feedback?
- [ ] What got descoped? What got added that we didn't anticipate?
- [ ] Funniest moment?
- [ ] Most valuable thing the AI did that a human wouldn't have?
- [ ] Most annoying thing the AI did?

**Format:** Honest retrospective. "Here's what I said would happen, here's what actually happened."

---

## Series arc
Post 1 sets expectations. Post 2 holds itself accountable. The combination is more credible than either alone.
