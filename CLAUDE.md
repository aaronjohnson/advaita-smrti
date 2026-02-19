# Form Helper - Claude Code Integration

This project helps complete multi-section applications and questionnaires through collaborative AI sessions.

## Workflow: Answering Questions

When working on questions, Claude Code reads context from `.sea_question_context.json` and writes the final answer to `.sea_answer.md`.

### Context File Structure (`.sea_question_context.json`)
```json
{
  "question_id": "1",
  "question_text": "What is the nature of your business?",
  "helper_text": "Think about: What problem do you solve?",
  "section": "Business Overview",
  "priority": 1,
  "current_answer": null,
  "notes": null,
  "related_answers": {}
}
```

### Collaboration Process
1. Read the context file to understand the question
2. Discuss with the user to gather their thoughts and experiences
3. Help craft a compelling, specific answer
4. When the user says "done" or "save", write the final answer to `.sea_answer.md`

### Answer Guidelines
- Be specific, not generic
- Use concrete numbers, dates, and examples where possible
- Draw on the user's actual experience and expertise
- Keep answers concise but complete
- Show "you've thought about this" - anticipate follow-up questions
- Match the tone appropriate for the application (professional, thorough)

### Writing the Final Answer
When the user indicates they're done, write ONLY the answer text to `.sea_answer.md`:
- No markdown headers or formatting beyond what the answer needs
- No "Final Answer:" prefix
- Just the clean answer text ready to paste into the application

## Database
- SQLite database: `sea_application.db`
- Use `sea_application_helper.py` for programmatic access
- The Python assistant handles saving answers to the database

## Background Context
The applicant will provide their background during the session. Pay attention to:
- Relevant professional experience
- Education and certifications
- Specific skills that apply to their business
- Personal circumstances that affect their planning

## Working Style
- Ask clarifying questions before drafting
- Offer 2-3 approaches when there are meaningful choices
- Help the user think through implications
- Be encouraging but honest about gaps or areas needing work
- Suggest concrete next steps when appropriate

## Session Flow
1. **Start**: Read the question context, summarize what we're working on
2. **Explore**: Ask what the user's thoughts are, what they want to convey
3. **Draft**: Propose an initial answer based on discussion
4. **Refine**: Iterate based on feedback
5. **Finalize**: When user says "done"/"save"/"looks good", write to `.sea_answer.md`
