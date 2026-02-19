# Creating Your Own Form Config

Want to use form-copilot for a different application? Create your own config file.

## Let Claude Build It

The fastest way to create a config: paste your application into Claude and ask it to generate one.

**Works with anything:**
- PDF applications (copy/paste the text)
- Web forms (paste the URL or screenshot)
- Paper forms (type or photograph the questions)
- Grant RFPs, job applications, visa forms, surveys...

**Example prompt:**
```
Here are the questions from my [grant application / college supplement / business loan form].
Create a form-copilot config JSON file with:
- Logical sections grouping related questions
- Priority 1 for foundational questions, 2-3 for others
- Helpful helper_text for complex questions
- Question types (text, long_text, yes_no, number, choice)

[paste your questions here]
```

Or use the `/generate-config` command in Claude Code - it knows the schema.

Claude will generate a complete config file. Save it to `examples/my_form_config.json`, run `python3 validate_config.py` to check it, and you're ready to go.

## Quick Start: Copy and Modify

Prefer to start from an existing example:

```bash
# Start from an example
cp examples/college_app_config.json examples/my_form_config.json

# Edit with your questions
nano examples/my_form_config.json  # or your preferred editor

# Run - it will appear in the form selection menu
python3 sea_assistant.py
```

## Step-by-Step Guide

1. **Identify your sections** - Group related questions (e.g., "Personal Info", "Experience", "Goals")
2. **List all questions** - Copy them exactly as they appear on the form
3. **Assign priorities** - Which questions are foundational? Which depend on others?
4. **Add helper text** - What guidance would help you (or others) answer well?
5. **Save in examples/** - Files matching `*_config.json` appear in the menu

## Config File Structure

```json
{
  "form_name": "Your Application Name",
  "form_description": "Description of the form",
  "version": "1.0",
  "sections": [
    {"id": 1, "name": "section_key", "title": "Section Title", "description": "..."}
  ],
  "questions": [
    {
      "id": "1",
      "section_id": 1,
      "question_text": "Your question here?",
      "question_type": "long_text",
      "priority": 1,
      "depends_on": null,
      "helper_text": "Guidance for answering"
    }
  ],
  "business_directions": [
    {"name": "Direction 1", "description": "..."}
  ]
}
```

## Question Types

| Type | Description |
|------|-------------|
| `long_text` | Multi-line text answer (default) |
| `text` | Single line text |
| `yes_no` | Yes/No question |
| `number` | Numeric answer |
| `choice` | Multiple choice (list options in helper_text) |

## Priority Levels

| Priority | Meaning |
|----------|---------|
| **1** | Most important, do these first |
| **2** | Important but can wait |
| **3** | Nice to have, do last |

## Tips for Good Configs

- **Helper text matters** - Write hints you wish someone had given you
- **Use question dependencies** - If Q2 only matters when Q1 is "Yes", set `depends_on`
- **Be specific in IDs** - Use `1a`, `1b` for sub-questions
- **business_directions is optional** - Only include if your form has multiple paths
- **Test your config** - Run the validator before using

## Validating Your Config

The project includes validation tools to catch common mistakes:

```bash
# Validate a single config
python3 validate_config.py examples/my_form_config.json

# Validate all configs in examples/
python3 validate_config.py --all
```

The validator checks:
- Required fields (`form_name`, `sections`, `questions`)
- Unique question and section IDs
- Valid `section_id` references (questions point to existing sections)
- Valid `depends_on` references (dependencies point to existing questions)
- Section ID gaps (warns if IDs skip numbers)
- Valid priority values (1, 2, or 3)
- Valid question types (`text`, `long_text`, `yes_no`, `number`, `choice`)

A JSON Schema (`config_schema.json`) is also available for IDE validation and autocomplete.

## Sharing Configs

Created a config for a common application? Consider contributing it:
1. Remove any personal information from helper text
2. Test that it works from a fresh start
3. Submit a pull request to add it to `examples/`
