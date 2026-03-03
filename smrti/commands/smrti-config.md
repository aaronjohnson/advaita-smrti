# smrti-config — Generate Configuration

Create a smrti configuration file from user-provided questions, tasks,
or any structured multi-step work.

## Instructions

1. **Ask for context** if not provided:
   - What type of work is this? (grant application, project plan,
     retrospective, questionnaire, onboarding checklist, etc.)
   - Any sections or groupings already apparent?

2. **Analyze the items** and:
   - Group into logical sections (3-8 sections typical)
   - Assign section IDs starting from 1
   - Assign item IDs ("1", "2", "2a", "2b" for sub-items)
   - Determine priorities (1=foundational, 2=important, 3=supplementary)
   - Identify dependencies where answers build on each other
   - Write helpful helper_text for complex items

3. **Generate the config**:

```json
{
  "form_name": "Project Name",
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
      "question_text": "The item or question text",
      "question_type": "long_text",
      "priority": 1,
      "depends_on": null,
      "helper_text": "Guidance for completing this well"
    }
  ]
}
```

4. **Load into memory** when the user approves:
   - For each question, call `task_create` with:
     - title: `Q{id}: {question_text}` (truncated)
     - labels: `section:{section_name}`, `priority:{n}`
     - metadata: `{"question_id": "...", "section": "...", "depends_on": ...}`
   - Record any dependency relationships with `task_block`

## Item Types

- `long_text` — multi-paragraph (essays, explanations) — DEFAULT
- `text` — single line (names, titles, short answers)
- `yes_no` — binary
- `number` — numeric (budgets, counts, years)
- `choice` — multiple choice (list options in helper_text)

## Priority Guidelines

- **1**: Foundational — informs other answers
- **2**: Core content — important but independent
- **3**: Supplementary — detail or optional

## Output

1. Present the generated JSON for review
2. Save to `examples/{name}_config.json` when approved
3. Offer to validate: `python3 advaita-smrti/validate_config.py examples/{name}_config.json`
4. Offer to load into memory via MCP tools
