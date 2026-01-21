# Form Helper - Choose Your Own Adventure

A toolkit for completing complex multi-section applications and questionnaires with AI-assisted collaboration and executive function support.

Originally created for the Oregon Self Employment Assistance (SEA) Program but designed to be adaptable for any form-based application process.

## Philosophy: Choose Your Own Adventure

Remember those books from the 1980s where every decision led somewhere different? This tool embraces that spirit:

- **You drive the journey** - Start anywhere, skip around, come back later
- **Multiple paths to completion** - Work by priority, by section, or by question
- **AI as your co-pilot** - Launch focused Claude Code sessions for any question
- **No wrong moves** - Draft, save notes, mark complete, or skip. Every choice is valid.

## Features

### Core Capabilities (v0.1)
- **SQLite database** - Persistent storage for your answers and notes
- **Progress tracking** - See what's complete, in progress, not started
- **Priority system** - Questions ranked by importance
- **Section organization** - Logical grouping of related questions
- **Helper text** - Guidance for complex questions
- **Notes system** - Capture thoughts separately from official answers
- **Draft mode** - Mark questions to return to later
- **Export** - Save all answers to JSON

### Update 1: Claude Code Integration
- **Collaborative AI sessions** - Launch Claude Code for any question
- **Context passing** - Questions, helper text, and related answers provided automatically
- **Answer capture** - Claude writes final answer to file, you approve before saving
- **CLAUDE.md workflow** - Instructions tell Claude exactly how to help

## Quick Start

```bash
# 1. Run the interactive assistant
python3 sea_assistant.py

# 2. Follow the menu - it's a choose your own adventure!
```

## The Adventure Menu

```
What would you like to do?

  [1] Work on high-priority questions (recommended to start)
  [2] Review business directions
  [3] Browse by section
  [4] View specific question by ID
  [5] Show progress dashboard
  [6] Export answers to file
  [7] Tips for answering questions

  [C] Work with Claude on a question (collaborative AI session)

  [Q] Quit and save
```

## Working with Claude (The Magic)

When you select a question and press `[C]`, the assistant:

1. **Writes context** to `.sea_question_context.json`:
   - Question text and helper hints
   - Your current draft/notes
   - Related answers from the same section

2. **Launches Claude Code** with a prompt about the question

3. **You collaborate** - discuss, refine, iterate

4. **Claude writes** the final answer to `.sea_answer.md`

5. **You approve** - back in the assistant, confirm to save to database

## Files

| File | Purpose |
|------|---------|
| `sea_assistant.py` | Interactive CLI (main interface) |
| `sea_application_helper.py` | Core database and functions |
| `CLAUDE.md` | Instructions for Claude Code sessions |
| `business_direction_analysis.md` | Template for planning your direction |
| `.gitignore` | Excludes database and temp files |

## Customizing for Your Form

The system loads questions from `questions_config.json`. To use a different form:

1. Copy `questions_config.json` to create your own (e.g., `my_form_config.json`)
2. Edit the JSON with your sections and questions
3. Delete any existing `sea_application.db` to start fresh
4. Run the assistant - it will load your new config

### Config File Structure

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

### Question Types
- `long_text` - Multi-line text answer
- `text` - Single line text
- `yes_no` - Yes/No question
- `number` - Numeric answer
- `choice` - Multiple choice (list options in helper_text)

### Priority Levels
- **1** - Most important, do these first
- **2** - Important but can wait
- **3** - Nice to have, do last

### Example Config
The included `questions_config.json` contains the Oregon SEA application as a complete working example.

## Privacy

Your answers stay local:
- Database: `*.db` files (gitignored)
- Exports: `*_answers.json` files (gitignored)
- Session files: `.sea_question_context.json`, `.sea_answer.md` (gitignored)

## Requirements

- Python 3.6+
- No external dependencies (standard library only)
- Claude Code CLI (for AI collaboration feature)

## Version History

- **v0.1** - Initial release: menu-driven interface, database, progress tracking
- **v0.2** - Update 1: Claude Code integration, collaborative AI sessions

## License

MIT - Use freely, modify as needed.

## Why This Exists

Complex applications are hard. They're especially hard with ADHD, autism, or other executive function challenges. This tool:

- Breaks the elephant into bite-sized pieces
- Tracks what you've done and what's left
- Lets you capture thoughts before they escape
- Brings AI into the conversation when you're stuck

You don't have to do this alone.
