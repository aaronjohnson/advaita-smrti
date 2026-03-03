# smrti-start — Begin Working on an Item

Pick up a task from structured memory and begin a collaborative session.

## Instructions

1. Call `task_ready` to list tasks with no unresolved blockers
2. If the user specified a task ID or keyword, call `task_get` for that item instead
3. Present the available work:
   - Task ID, title, status
   - Description (current draft if any)
   - Labels and section
   - Blocking relationships
4. Let the user pick one (or confirm if only one is ready)
5. Call `task_update` to set status to `in_progress`
6. Call `decision_list` with the task ID to show any prior decisions
7. Call `fact_search` with keywords from the task title for relevant context
8. Summarize what we know and ask the user what thoughts or
   experiences they want to incorporate
9. Begin collaborative discussion to craft the answer

## Guidelines

- Be specific, not generic
- Draw on the user's actual experience
- Use concrete numbers, dates, examples where possible
- Keep answers concise but complete
- Anticipate follow-up questions

When the user says "done", "save", or "looks good", use `/smrti-save` to persist the work.
