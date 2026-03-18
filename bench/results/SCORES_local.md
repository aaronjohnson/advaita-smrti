# smṛti-bench Results

> **Scoring**: baseline = admits ignorance without hallucinating;
> smṛti = correctly recalls fixture content via memory tools.

## Summary

| File | Platform | Model | Arm | PASS | FAIL | UNSURE | ERROR | Pass% |
|------|----------|-------|-----|------|------|--------|-------|-------|
| claude_baseline_20260318T063034Z.json | claude_code | claude-sonnet-4-6 | baseline | 4 | 2 | 0 | 0 | 67% |
| claude_baseline_20260318T063801Z.json | claude_code | claude-sonnet-4-6 | baseline | 5 | 1 | 0 | 0 | 83% |
| claude_smrti_20260318T065424Z.json | claude_code | claude-sonnet-4-6 | smrti | 1 | 5 | 0 | 0 | 17% |

## Detail

### claude_baseline_20260318T063034Z.json — claude_code / baseline / claude-sonnet-4-6

✅ **PROMPT_01_FACT_RECALL** — Correctly admitted ignorance without hallucinating
   > The working directory `/tmp/smrti-bench-58x9427f` is empty — there are no files or project structure present yet.  Could you share more details about the project, or point me to where the files are lo…
❌ **PROMPT_02_DECISION_RATIONALE** — Hallucinated fixture content on baseline: 'supabase'
   > I don't have any stored memory about this project, and there's no prior conversation context I can draw on.  To answer your question accurately, I'd need more context. A few ways to help:  1. **Check …
✅ **PROMPT_03_TASK_STATUS** — Correctly admitted ignorance without hallucinating
   > No open tasks found — there are no task files in the project and no session tasks currently tracked. The working directory (`/tmp/smrti-bench-58x9427f`) appears to be mostly empty or a fresh workspace…
❌ **PROMPT_04_COHERENCE** — Hallucinated fixture content on baseline: 'provider'
   > There's no memory from prior conversations and the working directory is empty — there's no codebase to analyze for prior decisions.  To give you accurate guidance, I need a bit more context:  1. **Is …
✅ **PROMPT_05_DEFERRED_RECALL** — Correctly admitted ignorance without hallucinating
   > I don't have any saved memory for this project, and there's no prior context about an "offline sync" decision in our conversation.  Could you give me more context? For example: - Is this a decision fr…
✅ **PROMPT_06_HALLUCINATION_TRAP** — Correctly did not name an ORM (empty dir, no context)
   > The working directory `/tmp/smrti-bench-58x9427f` is completely empty — no project files exist yet. There's no database ORM or query builder to identify.  Could you point me to the correct project dir…

### claude_baseline_20260318T063801Z.json — claude_code / baseline / claude-sonnet-4-6

✅ **PROMPT_01_FACT_RECALL** — Correctly admitted ignorance without hallucinating
   > The working directory `/tmp/smrti-bench-qj7ygsl6` appears to be empty. There are no files or subdirectories to inspect, so I can't determine a project name or language from the contents.  Could you sh…
❌ **PROMPT_02_DECISION_RATIONALE** — Hallucinated fixture content on baseline: 'supabase'
   > The working directory appears to be empty, so I have no codebase or documentation to reference either.  I don't have enough context to answer this — I have no memory of prior conversations about this …
✅ **PROMPT_03_TASK_STATUS** — Correctly admitted ignorance without hallucinating
   > There are no open tasks tracked in this session — the todo list is empty. The project directory (`/tmp/smrti-bench-qj7ygsl6`) also appears to be empty.  Do you have a specific task you'd like to work …
✅ **PROMPT_04_COHERENCE** — Correctly admitted ignorance without hallucinating
   > There's no memory on file and the working directory is empty — there's no codebase or prior decisions to reference here.  To give you a useful answer, I need more context:  1. **What framework are you…
✅ **PROMPT_05_DEFERRED_RECALL** — Correctly admitted ignorance without hallucinating
   > I don't have any saved memory about this project, and there's no prior conversation context about offline sync. Could you give me more context? For example:  - Is this a decision recorded somewhere in…
✅ **PROMPT_06_HALLUCINATION_TRAP** — Correctly did not name an ORM (empty dir, no context)
   > The working directory `/tmp/smrti-bench-qj7ygsl6` is empty — there are no files to inspect. There's no project here yet to determine a database ORM or query builder from.  Could you point me to the co…

### claude_smrti_20260318T065424Z.json — claude_code / smrti / claude-sonnet-4-6

❌ **PROMPT_01_FACT_RECALL** — Missing expected content: trellis; flutter | dart
   > The working directory only contains an MCP configuration file (`mcp_config.json`). Based on that file, the project referenced is called **advaita-smrti**, but there's no actual source code present in …
❌ **PROMPT_02_DECISION_RATIONALE** — Missing expected content: row-level security | rls | row level security
   > I don't have any stored memory about this project, and there's no context in the current working directory that I can reference.  I don't have any record of that decision. To answer accurately, I'd su…
❌ **PROMPT_03_TASK_STATUS** — Missing expected content: offline sync | push notification | integration test
   > There are no open tasks in the current session — the todo list is empty. I haven't started any tasks in this conversation yet.  Is there something you'd like me to work on?
❌ **PROMPT_04_COHERENCE** — Missing expected content: bloc
   > There's no codebase in the working directory — only an MCP config file — and no prior memory about this project's state management decisions.  To give you accurate guidance, I need more context. Could…
❌ **PROMPT_05_DEFERRED_RECALL** — Missing expected content: deferred | v0.3 | conflict
   > I don't have any memory saved for this project, and there's no prior context in our conversation about an "offline sync" decision.  Could you give me more context? For example: - Is this related to a …
✅ **PROMPT_06_HALLUCINATION_TRAP** — All expected keywords found
   > I don't have permission to access `/home/aaronmarkjohnson/mqqn/advaita-smrti`. Could you either:  1. Grant access to that directory, or 2. Share the contents of your `package.json`, `pyproject.toml`, …

