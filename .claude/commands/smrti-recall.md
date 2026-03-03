# smrti-recall — Pull Context from Memory

Query structured memory for context relevant to the current work.
Use this before starting a task, making a decision, or when you
need to remember what's been established.

## Instructions

1. Identify what context is needed:
   - If the user mentions a topic, use it as the search term
   - If starting general work, pull a broad summary

2. Query across all stores:
   - `memory_summary` — overall state
   - `fact_search` with relevant keywords — what we know
   - `fact_list` by section — grouped knowledge
   - `decision_list` — what's been decided and why
   - `task_list` with status filters — what's done, what's active

3. For a specific task:
   - `task_get` — full details
   - `connections` — related tasks, decisions, shared labels
   - `decision_list` filtered by task_id — reasoning history

4. Synthesize into a brief context paragraph:
   - What's been established (facts)
   - What's been decided (decisions + rationale)
   - What's in progress and what's blocked
   - Any coherence issues to be aware of

## When to Use

- Beginning of a session ("what were we working on?")
- Before making a decision ("what do we already know about X?")
- Switching between tasks ("remind me about Y")
- After a break ("catch me up")

## Output

Keep the summary concise — 1-3 paragraphs. Link to specific
IDs so the user can drill deeper if needed.
