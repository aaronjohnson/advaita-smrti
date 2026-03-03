# smrti-save — Save Current Work

Persist the collaboratively developed answer or work product to structured memory.

## Instructions

1. Identify the task we've been working on (should be `in_progress`)
   - If unclear, call `task_list` with status `in_progress`
2. Take the answer or work product we've developed in this session
3. Call `task_update` with:
   - `description`: the finalized text (clean, no meta-commentary)
   - `status`: "closed" if complete, keep "in_progress" if partial
4. If any new facts emerged during the discussion, call `fact_create`
   to record them (with source set to "session" or more specific)
5. If we made any non-trivial decisions, call `decision_begin` and
   record the reasoning trail
6. Confirm to the user what was saved
7. Call `task_ready` to show what's available next

## Answer Format

The description stored in the task should be the clean answer text —
exactly what would go in the application, document, or deliverable.
No markdown headers, no "Final Answer:" prefix, no meta-commentary.

## Partial Saves

If the user says "save but not done" or "checkpoint":
- Update the description with current draft
- Keep status as `in_progress`
- Note where we left off in the description
