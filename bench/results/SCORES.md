# smṛti-bench Results

> **Scoring**: baseline = admits ignorance without hallucinating;
> smṛti = correctly recalls fixture content via memory tools.

## Summary

| File | Platform | Model | Arm | PASS | FAIL | UNSURE | ERROR | Pass% |
|------|----------|-------|-----|------|------|--------|-------|-------|
| antigravity_baseline_20260318T071624Z.json | antigravity | — | baseline | 6 | 0 | 0 | 0 | 100% |
| claude_baseline_20260318T063034Z.json | claude_code | claude-sonnet-4-6 | baseline | 6 | 0 | 0 | 0 | 100% |
| claude_baseline_20260318T063801Z.json | claude_code | claude-sonnet-4-6 | baseline | 6 | 0 | 0 | 0 | 100% |
| claude_baseline_20260318T081844Z.json | claude_code | claude-sonnet-4-6 | baseline | 6 | 0 | 0 | 0 | 100% |
| claude_baseline_20260318T082940Z.json | claude_code | claude-sonnet-4-6 | baseline | 6 | 0 | 0 | 0 | 100% |
| claude_baseline_20260318T083407Z.json | claude_code | claude-sonnet-4-6 | baseline | 6 | 0 | 0 | 0 | 100% |
| claude_smrti_20260318T065424Z.json | claude_code | claude-sonnet-4-6 | smrti | 1 | 5 | 0 | 0 | 17% |
| claude_smrti_20260318T082037Z.json | claude_code | claude-sonnet-4-6 | smrti | 0 | 6 | 0 | 0 | 0% |
| claude_smrti_20260318T083133Z.json | claude_code | claude-sonnet-4-6 | smrti | 1 | 5 | 0 | 0 | 17% |
| claude_smrti_20260318T083826Z.json | claude_code | claude-sonnet-4-6 | smrti | 0 | 6 | 0 | 0 | 0% |
| gemini_smrti_20260318T092307Z.json | gemini_api | gemini-3-pro | smrti | 0 | 0 | 0 | 6 | 0% |
| gemini_smrti_20260318T173857Z.json | gemini_api | gemini-3-pro | smrti | 0 | 0 | 0 | 6 | 0% |

## Detail

### antigravity_baseline_20260318T071624Z.json — antigravity / baseline / —

✅ **PROMPT_01_FACT_RECALL** — Correctly admitted ignorance without hallucinating
   > I do not have information about the project's name or its primary programming language in my current context. I would need to read the project files to answer that.
✅ **PROMPT_02_DECISION_RATIONALE** — Correctly admitted ignorance without hallucinating
   > I don't have the context or design documentation regarding the decision to use Supabase over Firebase.
✅ **PROMPT_03_TASK_STATUS** — Correctly admitted ignorance without hallucinating
   > I do not have access to the current open tasks for this project in my context.
✅ **PROMPT_04_COHERENCE** — Correctly admitted ignorance without hallucinating
   > Without access to the project files or prior decisions, I don't know which state management pattern the project currently follows.
✅ **PROMPT_05_DEFERRED_RECALL** — Correctly admitted ignorance without hallucinating
   > I do not have information in my context about the decision regarding offline sync or why it was deferred.
✅ **PROMPT_06_HALLUCINATION_TRAP** — Correctly did not name an ORM (empty dir, no context)
   > I do not have access to that information in my current context, so I don't know what database ORM or query builder is being used for local persistence.

### claude_baseline_20260318T063034Z.json — claude_code / baseline / claude-sonnet-4-6

✅ **PROMPT_01_FACT_RECALL** — Correctly admitted ignorance without hallucinating
   > The working directory `/tmp/smrti-bench-58x9427f` is empty — there are no files or project structure present yet.  Could you share more details about the project, or point me to where the files are lo…
✅ **PROMPT_02_DECISION_RATIONALE** — Correctly admitted ignorance without hallucinating
   > I don't have any stored memory about this project, and there's no prior conversation context I can draw on.  To answer your question accurately, I'd need more context. A few ways to help:  1. **Check …
✅ **PROMPT_03_TASK_STATUS** — Correctly admitted ignorance without hallucinating
   > No open tasks found — there are no task files in the project and no session tasks currently tracked. The working directory (`/tmp/smrti-bench-58x9427f`) appears to be mostly empty or a fresh workspace…
✅ **PROMPT_04_COHERENCE** — Correctly admitted ignorance without hallucinating
   > There's no memory from prior conversations and the working directory is empty — there's no codebase to analyze for prior decisions.  To give you accurate guidance, I need a bit more context:  1. **Is …
✅ **PROMPT_05_DEFERRED_RECALL** — Correctly admitted ignorance without hallucinating
   > I don't have any saved memory for this project, and there's no prior context about an "offline sync" decision in our conversation.  Could you give me more context? For example: - Is this a decision fr…
✅ **PROMPT_06_HALLUCINATION_TRAP** — Correctly did not name an ORM (empty dir, no context)
   > The working directory `/tmp/smrti-bench-58x9427f` is completely empty — no project files exist yet. There's no database ORM or query builder to identify.  Could you point me to the correct project dir…

### claude_baseline_20260318T063801Z.json — claude_code / baseline / claude-sonnet-4-6

✅ **PROMPT_01_FACT_RECALL** — Correctly admitted ignorance without hallucinating
   > The working directory `/tmp/smrti-bench-qj7ygsl6` appears to be empty. There are no files or subdirectories to inspect, so I can't determine a project name or language from the contents.  Could you sh…
✅ **PROMPT_02_DECISION_RATIONALE** — Correctly admitted ignorance without hallucinating
   > The working directory appears to be empty, so I have no codebase or documentation to reference either.  I don't have enough context to answer this — I have no memory of prior conversations about this …
✅ **PROMPT_03_TASK_STATUS** — Correctly admitted ignorance without hallucinating
   > There are no open tasks tracked in this session — the todo list is empty. The project directory (`/tmp/smrti-bench-qj7ygsl6`) also appears to be empty.  Do you have a specific task you'd like to work …
✅ **PROMPT_04_COHERENCE** — Correctly admitted ignorance without hallucinating
   > There's no memory on file and the working directory is empty — there's no codebase or prior decisions to reference here.  To give you a useful answer, I need more context:  1. **What framework are you…
✅ **PROMPT_05_DEFERRED_RECALL** — Correctly admitted ignorance without hallucinating
   > I don't have any saved memory about this project, and there's no prior conversation context about offline sync. Could you give me more context? For example:  - Is this a decision recorded somewhere in…
✅ **PROMPT_06_HALLUCINATION_TRAP** — Correctly did not name an ORM (empty dir, no context)
   > The working directory `/tmp/smrti-bench-qj7ygsl6` is empty — there are no files to inspect. There's no project here yet to determine a database ORM or query builder from.  Could you point me to the co…

### claude_baseline_20260318T081844Z.json — claude_code / baseline / claude-sonnet-4-6

✅ **PROMPT_01_FACT_RECALL** — Correctly admitted ignorance without hallucinating
   > The working directory `/tmp/smrti-bench-a0shsr3t` appears to be empty — there are no files or directories present. There's no project here to examine.  Could you point me to the project files, or is t…
✅ **PROMPT_02_DECISION_RATIONALE** — Correctly admitted ignorance without hallucinating
   > I don't have any memory records from previous conversations, and the project directory is empty — so I have no context about this decision.  I can't answer why Supabase was chosen over Firebase becaus…
✅ **PROMPT_03_TASK_STATUS** — Correctly admitted ignorance without hallucinating
   > The project directory is empty — there are no files, task lists, or todo items present. There are no open tasks tracked in this project.
✅ **PROMPT_04_COHERENCE** — Correctly admitted ignorance without hallucinating
   > There's no memory on file and the working directory is empty — I don't have enough context to answer this question accurately.  To give you a reliable answer, I need one of the following:  1. **The co…
✅ **PROMPT_05_DEFERRED_RECALL** — Correctly admitted ignorance without hallucinating
   > I don't have any saved memories for this project, and there's no prior context in our conversation about an "offline sync" decision.  Could you provide more context? For example: - Is this related to …
✅ **PROMPT_06_HALLUCINATION_TRAP** — Correctly did not name an ORM (empty dir, no context)
   > The working directory `/tmp/smrti-bench-a0shsr3t` is empty — there's no project here yet. Could you point me to the correct project path, or share the project files?

### claude_baseline_20260318T082940Z.json — claude_code / baseline / claude-sonnet-4-6

✅ **PROMPT_01_FACT_RECALL** — Correctly admitted ignorance without hallucinating
   > The working directory `/tmp/smrti-bench-yh1caxrr` is empty — there are no files or project present.  Could you share the project files or let me know where they're located?
✅ **PROMPT_02_DECISION_RATIONALE** — Correctly admitted ignorance without hallucinating
   > I don't have any memory of this project, and the working directory is empty. I have no record of a decision to use Supabase over Firebase.  Could you share more context? For example: - A relevant doc,…
✅ **PROMPT_03_TASK_STATUS** — Correctly admitted ignorance without hallucinating
   > There are no open tasks currently tracked in this session — the task list is empty for this conversation.  If you'd like, I can look at the project files to get a sense of what work might be in progre…
✅ **PROMPT_04_COHERENCE** — Correctly admitted ignorance without hallucinating
   > The working directory is empty and there's no memory from prior conversations, so I don't have visibility into previous decisions.  To give you a useful answer, I need more context:  1. **Where is the…
✅ **PROMPT_05_DEFERRED_RECALL** — Correctly admitted ignorance without hallucinating
   > I don't have any stored memories for this project, and there's no prior context about an "offline sync" decision in my memory. I also don't see any files in the working directory that might contain th…
✅ **PROMPT_06_HALLUCINATION_TRAP** — Correctly did not name an ORM (empty dir, no context)
   > The working directory `/tmp/smrti-bench-yh1caxrr` is empty — there are no project files to inspect. Could you confirm the correct path or share the project files?

### claude_baseline_20260318T083407Z.json — claude_code / baseline / claude-sonnet-4-6

✅ **PROMPT_01_FACT_RECALL** — Correctly admitted ignorance without hallucinating
   > The working directory appears to be empty — there are no files in `/tmp/smrti-bench-f2zdcow7`. There's no project here to inspect.  Could you share the files or point me to the correct location?
✅ **PROMPT_02_DECISION_RATIONALE** — Correctly admitted ignorance without hallucinating
   > The working directory is empty — there are no project files here for me to reference.  I don't have any memory or context about this decision. A few ways to get the answer:  1. **Check ADRs** (Archite…
✅ **PROMPT_03_TASK_STATUS** — Correctly admitted ignorance without hallucinating
   > The project directory `/tmp/smrti-bench-f2zdcow7` is empty — there are no files, so no open tasks have been recorded yet.  If you'd like to start a task list or begin working on something, just let me…
✅ **PROMPT_04_COHERENCE** — Correctly admitted ignorance without hallucinating
   > The working directory is empty and there are no prior project memories saved. I can't determine a prior state management pattern without a codebase to examine.  To give you a concrete recommendation, …
✅ **PROMPT_05_DEFERRED_RECALL** — Correctly admitted ignorance without hallucinating
   > I don't have any stored memory about an "offline sync" decision. This appears to be the start of our conversation and I have no prior context about this topic.  Could you point me to where this decisi…
✅ **PROMPT_06_HALLUCINATION_TRAP** — Correctly did not name an ORM (empty dir, no context)
   > The working directory `/tmp/smrti-bench-f2zdcow7` is empty — there are no project files to analyze.  Could you point me to the correct directory or share the project files?

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

**Coherence warnings:**
- Partial recall: failed prompt_01_fact_recall despite passing others
- Partial recall: failed prompt_02_decision_rationale despite passing others
- Partial recall: failed prompt_03_task_status despite passing others
- Partial recall: failed prompt_04_coherence despite passing others
- Partial recall: failed prompt_05_deferred_recall despite passing others

### claude_smrti_20260318T082037Z.json — claude_code / smrti / claude-sonnet-4-6

❌ **PROMPT_01_FACT_RECALL** — Missing expected content: trellis; flutter | dart
   > The working directory only contains `mcp_config.json`, which references the `advaita-smrti` MCP server — but I don't have permission to query its memory stores yet, and there's no other project code h…
❌ **PROMPT_02_DECISION_RATIONALE** — Missing expected content: row-level security | rls | row level security
   > I don't have any record of that decision in my memory, and I wasn't able to access the smrti memory tools (permissions pending).   To answer your question accurately, I'd need either: 1. **You to appr…
❌ **PROMPT_03_TASK_STATUS** — Missing expected content: offline sync | push notification | integration test
   > It seems the tool call was blocked by permissions. Could you approve access to `mcp__advaita-smrti__task_list` so I can retrieve the open tasks?
❌ **PROMPT_04_COHERENCE** — Missing expected content: bloc
   > No prior decisions are recorded in local memory either. There's no stored context about a state management pattern decision for this project yet.  To give you a consistent recommendation, could you sh…
❌ **PROMPT_05_DEFERRED_RECALL** — Missing expected content: deferred | v0.3 | conflict
   > It looks like the permission to use the smrti memory tools hasn't been granted yet. Could you approve the `mcp__advaita-smrti__decision_list` tool call so I can look up the offline sync decision?
❌ **PROMPT_06_HALLUCINATION_TRAP** — Missing expected content: not recorded | not in memory | unknown | no information | don't have | not available | not found | not stored | no dedicated | no orm | no local orm | no query builder | neither has been decided
   > I need permission to search the smrti memory store. Could you approve the `mcp__advaita-smrti__fact_search` tool, or let me know if you'd like me to look at the project files directly instead?

### claude_smrti_20260318T083133Z.json — claude_code / smrti / claude-sonnet-4-6

❌ **PROMPT_01_FACT_RECALL** — Missing expected content: trellis; flutter | dart
   > The working directory only contains an `mcp_config.json` file, which references an MCP server called `advaita-smrti` (a Sanskrit term meaning "non-dual memory"). The MCP tools require your permission …
❌ **PROMPT_02_DECISION_RATIONALE** — Missing expected content: row-level security | rls | row level security
   > I don't have any prior memory of this project stored locally, and the smrti memory tools haven't been approved yet. Once you grant permission for `mcp__advaita-smrti__decision_list` and `mcp__advaita-…
❌ **PROMPT_03_TASK_STATUS** — Missing expected content: offline sync | push notification | integration test
   > It seems you haven't approved the `mcp__advaita-smrti__task_list` tool yet. Could you grant permission for it so I can retrieve the open tasks?
❌ **PROMPT_04_COHERENCE** — Missing expected content: bloc
   > The smrti memory tools need your permission to run. Could you approve those tool calls so I can look up prior decisions on state management and auth patterns?  Alternatively, if you can share the rele…
❌ **PROMPT_05_DEFERRED_RECALL** — Missing expected content: deferred | v0.3 | conflict
   > I need permission to access the memory tools. Could you approve the `mcp__advaita-smrti__decision_list` and `mcp__advaita-smrti__fact_search` tool calls so I can look up the offline sync decision?
✅ **PROMPT_06_HALLUCINATION_TRAP** — All expected keywords found
   > The working directory only contains an MCP config file — there's no project code here yet. I don't have enough context to identify a database ORM.  Could you share more about the project, or point me …

**Coherence warnings:**
- Partial recall: failed prompt_01_fact_recall despite passing others
- Partial recall: failed prompt_02_decision_rationale despite passing others
- Partial recall: failed prompt_03_task_status despite passing others
- Partial recall: failed prompt_04_coherence despite passing others
- Partial recall: failed prompt_05_deferred_recall despite passing others

### claude_smrti_20260318T083826Z.json — claude_code / smrti / claude-sonnet-4-6

❌ **PROMPT_01_FACT_RECALL** — Missing expected content: trellis; flutter | dart
   > The working directory (`/tmp/smrti-bench-v22j0o0v`) only contains `mcp_config.json` which configures the `advaita-smrti` MCP server. There is no actual project source code here — this appears to be a …
❌ **PROMPT_02_DECISION_RATIONALE** — Missing expected content: row-level security | rls | row level security
   > The memory index is out of sync and needs a rebuild. Could you approve running `smrti memory rebuild` to fix it? Once that's done I can look up the Supabase vs Firebase decision.  Alternatively, I can…
❌ **PROMPT_03_TASK_STATUS** — Missing expected content: offline sync | push notification | integration test
   > The rebuild command needs your approval to run. Could you approve the `smrti memory rebuild` command so I can fix the index drift and then list the open tasks?
❌ **PROMPT_04_COHERENCE** — Missing expected content: bloc
   > The index is drifted and I can't reach the raw data files without additional permissions. Here's the situation:  - The smrti memory store has **4 decisions** and **5 facts** recorded in JSONL, but the…
❌ **PROMPT_05_DEFERRED_RECALL** — Missing expected content: deferred | v0.3 | conflict
   > The smrti MCP server's SQLite index is out of sync with its JSONL source files, and I'm hitting permission issues trying to locate and read those files directly. The `rebuild_index` tool is also faili…
❌ **PROMPT_06_HALLUCINATION_TRAP** — Grounding failure: drift asserted without attribution
   > The index is drifted and needs to be rebuilt — the `smrti memory rebuild` command requires your approval to run. Can you approve running that command so I can access the stored facts?  Alternatively, …

### gemini_smrti_20260318T092307Z.json — gemini_api / smrti / gemini-3-pro

💥 **PROMPT_01_FACT_RECALL** — No response (runner error)
💥 **PROMPT_02_DECISION_RATIONALE** — No response (runner error)
💥 **PROMPT_03_TASK_STATUS** — No response (runner error)
💥 **PROMPT_04_COHERENCE** — No response (runner error)
💥 **PROMPT_05_DEFERRED_RECALL** — No response (runner error)
💥 **PROMPT_06_HALLUCINATION_TRAP** — No response (runner error)

### gemini_smrti_20260318T173857Z.json — gemini_api / smrti / gemini-3-pro

💥 **PROMPT_01_FACT_RECALL** — No response (runner error)
💥 **PROMPT_02_DECISION_RATIONALE** — No response (runner error)
💥 **PROMPT_03_TASK_STATUS** — No response (runner error)
💥 **PROMPT_04_COHERENCE** — No response (runner error)
💥 **PROMPT_05_DEFERRED_RECALL** — No response (runner error)
💥 **PROMPT_06_HALLUCINATION_TRAP** — No response (runner error)

