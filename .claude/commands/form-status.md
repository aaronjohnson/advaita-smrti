# Check Form Question Status

Show the current question context and any existing draft.

## Instructions

1. Check if `.sea_question_context.json` exists
2. If yes, display:
   - Question ID and section
   - Question text
   - Helper hints (if any)
   - Current draft (if any)
   - Notes (if any)
   - Priority level
3. If no context file exists, inform the user:
   - They need to launch a question session from the Python assistant
   - Run `python3 sea_assistant.py` and select a question with `[C]`

4. Check if `.sea_answer.md` exists and show its contents if present

## Output Format

```
CURRENT QUESTION
================
ID: [question_id]
Section: [section_name]
Priority: [1-3]

Question:
[question_text]

Hint: [helper_text if any]

Current Draft: [draft or "None"]
Notes: [notes or "None"]

Pending Answer: [contents of .sea_answer.md if exists, or "None"]
```
