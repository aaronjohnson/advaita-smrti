# Start Working on Form Question

Read the current question context and begin a collaborative session.

## Instructions

1. Read `.sea_question_context.json` to understand the question
2. Summarize for the user:
   - Question ID and section
   - The question text
   - Any helper hints
   - Current draft (if any)
   - Related answers from same section (if any)
3. Ask the user what thoughts or experiences they want to incorporate
4. Begin collaborative discussion to craft the answer

## Guidelines

- Be specific, not generic
- Draw on user's actual experience
- Use concrete numbers, dates, examples where possible
- Keep answers concise but complete
- Anticipate follow-up questions the reviewer might have

When the user says "done", "save", or "looks good", use `/form-save` to write the final answer.
