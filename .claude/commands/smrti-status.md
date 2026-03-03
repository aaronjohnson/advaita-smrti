# smrti-status — Check Progress

Show the current state of all memory stores.

## Instructions

1. Call `memory_summary` for the overview (task counts by status,
   decision counts by phase)
2. Call `task_list` with status `in_progress` to show active work
3. Call `task_list` with status `open` to show pending items
4. Call `coherence_check` to surface any structural issues
   (dependency violations, gaps, completeness)

## Output Format

Present a clean summary:

```
MEMORY STATUS
=============
Tasks:  X open · Y in progress · Z closed
Decisions: A pending · B decided
Facts: N recorded

ACTIVE WORK
-----------
[list in_progress tasks with IDs]

READY NEXT
----------
[list open tasks with no blockers]

ISSUES
------
[any coherence findings, or "None"]
```

## Optional Filters

If the user asks about a specific section or label:
- Call `task_list` with the label filter
- Call `coherence_check` with the section filter
- Show section-specific completeness
