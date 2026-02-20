# Generate Form Config

Create a smrti configuration file from user-provided questions.

## Instructions

When the user provides questions (from a PDF, web form, paper form, grant RFP, etc.), generate a complete `smrti` config JSON file.

## Process

1. **Ask for context** if not provided:
   - What type of application is this? (grant, college app, business loan, etc.)
   - Any specific sections or groupings already apparent?

2. **Analyze the questions** and:
   - Group into logical sections (3-8 sections typical)
   - Assign section IDs starting from 1
   - Assign question IDs (use "1", "2", "2a", "2b" style for sub-questions)
   - Determine priorities (1 = foundational, 2 = important, 3 = nice-to-have)
   - Identify dependencies (depends_on) where answers build on each other
   - Write helpful helper_text for complex questions

3. **Generate the config** following this schema:

```json
{
  "form_name": "Application Name",
  "form_description": "Brief description",
  "version": "1.0",
  "sections": [
    {
      "id": 1,
      "name": "snake_case_name",
      "title": "Display Title",
      "description": "What this section covers"
    }
  ],
  "questions": [
    {
      "id": "1",
      "section_id": 1,
      "question_text": "The actual question?",
      "question_type": "long_text",
      "priority": 1,
      "depends_on": null,
      "helper_text": "Guidance for answering well"
    }
  ],
  "business_directions": []
}
```

## Question Types

- `long_text` - Multi-paragraph responses (essays, explanations) - DEFAULT
- `text` - Single line (names, titles, short answers)
- `yes_no` - Binary questions
- `number` - Numeric values (budgets, counts, years)
- `choice` - Multiple choice (list options in helper_text)

## Priority Guidelines

- **Priority 1**: Questions that inform other answers, foundational context
- **Priority 2**: Important questions, core content
- **Priority 3**: Supplementary, optional, or detail questions

## Helper Text Tips

Write helper_text as if coaching someone through the question:
- What makes a strong answer?
- What specific details to include?
- Common mistakes to avoid?
- Word count guidance if applicable?

## Output

1. Present the generated JSON
2. Save to `examples/[name]_config.json` when user approves
3. Remind user to validate: `python3 validate_config.py examples/[name]_config.json`

## Example Section Names

- `personal_info`, `background`, `experience`
- `project_description`, `goals`, `objectives`
- `budget`, `timeline`, `resources`
- `impact`, `outcomes`, `evaluation`
- `qualifications`, `team`, `references`
