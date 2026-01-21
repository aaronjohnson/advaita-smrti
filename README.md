# Form Helper - Choose Your Own Adventure

> *Your AI co-pilot for complex paperwork.*

A toolkit for completing complex multi-section applications and questionnaires. Load context, collaborate with AI, capture answers, iterate. A reusable pattern for human-AI collaboration on thoughtful written work.

## The Big Idea

Complex forms ask hard questions. Questions that require reflection, specific details, and coherent narratives across sections. This tool provides:

1. **Structure** - Break overwhelming forms into manageable pieces
2. **Memory** - Track your progress, save drafts, capture notes
3. **Partnership** - Bring AI into focused conversations when you need help
4. **Iteration** - Refine answers over time, see your thinking evolve

## Philosophy: Choose Your Own Adventure

Remember those books from the 1980s where every decision led somewhere different? This tool embraces that spirit:

- **You drive the journey** - Start anywhere, skip around, come back later
- **Multiple paths to completion** - Work by priority, by section, or by question
- **AI as your co-pilot** - Launch focused Claude Code sessions for any question
- **No wrong moves** - Draft, save notes, mark complete, or skip. Every choice is valid.

## Use Cases

This pattern works for any complex application requiring thoughtful written responses:

| Application Type | Example | Why It's Hard |
|-----------------|---------|---------------|
| **Self-Employment Programs** | Oregon SEA, state business grants | Business planning, financial projections, market analysis |
| **College Applications** | Common App, UC apps, supplements | Personal essays, activity descriptions, "why this school" |
| **Research Grants** | NSF, NIH, private foundations | Specific aims, broader impacts, budget justification |
| **Financial Aid** | FAFSA, CSS Profile | Complex financial details, family circumstances |
| **Immigration** | I-485, N-400, visa applications | Detailed personal history, travel records, employment |
| **Business Loans** | SBA loans, bank applications | Business plans, projections, collateral documentation |
| **Fellowships** | Fulbright, Rhodes, professional fellowships | Personal statements, research proposals, leadership narratives |

Two example configs are included in `examples/` - copy one to `questions_config.json` to get started.

## Features

### Core Capabilities
- **SQLite database** - Persistent storage for your answers and notes
- **Progress tracking** - See what's complete, in progress, not started
- **Priority system** - Questions ranked by importance (tackle high-priority first)
- **Section organization** - Logical grouping of related questions
- **Helper text** - Guidance for complex questions
- **Notes system** - Capture thoughts separately from official answers
- **Draft mode** - Mark questions to return to later
- **Export** - Save all answers to JSON
- **Session logging** - Track your journey through the application

### Claude Code Integration
- **Collaborative AI sessions** - Launch Claude Code for any question
- **Context passing** - Questions, helper text, and related answers provided automatically
- **Answer capture** - Claude writes final answer to file, you approve before saving
- **CLAUDE.md workflow** - Instructions tell Claude exactly how to help

## Quick Start

```bash
# Run the interactive assistant
python3 sea_assistant.py

# First run? You'll be prompted to choose a form:
#   [1] Oregon SEA Application (49 questions)
#   [2] College Application Essays (17 questions)
#   [C] Create a new custom form
```

Each form gets its own database - switch between forms anytime from the menu.

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
  [8] View session history
  [9] Switch to different form

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

This is the core pattern: **load context → collaborative dialog → capture output → iterate**

## Session Logging

The tool logs your journey through the application:

```json
{
  "timestamp": "2025-01-21T14:30:00",
  "event": "claude_session_start",
  "question_id": "1",
  "had_draft": true
}
```

View your session history to:
- See how your thinking evolved over time
- Track which questions needed the most iteration
- Understand your own working patterns

## Files

| File | Purpose |
|------|---------|
| `sea_assistant.py` | Interactive CLI (main interface) |
| `sea_application_helper.py` | Core database and functions |
| `CLAUDE.md` | Instructions for Claude Code sessions |
| `business_direction_analysis.md` | Template for planning your direction |
| `.gitignore` | Excludes database and temp files |

**Generated on first run:**
| `questions_config.json` | Active form (copied from your selection in examples/) |
| `*.db` | Database for each form (stores your answers) |
| `session_log.json` | Your session history |

### Example Configs

| File | Questions | Use Case |
|------|-----------|----------|
| `examples/oregon_sea_config.json` | 49 | Self-employment assistance, business planning |
| `examples/college_app_config.json` | 17 | College essays, Common App, supplementals |

To use an example:
```bash
cp examples/college_app_config.json questions_config.json
python3 sea_assistant.py
```

## Creating Your Own Form

Want to use this for a different application? Create your own config file.

### Quick Start: Copy and Modify

```bash
# Start from an example
cp examples/college_app_config.json examples/my_form_config.json

# Edit with your questions
nano examples/my_form_config.json  # or your preferred editor

# Run - it will appear in the form selection menu
python3 sea_assistant.py
```

### Step-by-Step Guide

1. **Identify your sections** - Group related questions (e.g., "Personal Info", "Experience", "Goals")
2. **List all questions** - Copy them exactly as they appear on the form
3. **Assign priorities** - Which questions are foundational? Which depend on others?
4. **Add helper text** - What guidance would help you (or others) answer well?
5. **Save in examples/** - Files matching `*_config.json` appear in the menu

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

### Tips for Good Configs

- **Helper text matters** - Write hints you wish someone had given you
- **Use question dependencies** - If Q2 only matters when Q1 is "Yes", set `depends_on`
- **Be specific in IDs** - Use `1a`, `1b` for sub-questions
- **business_directions is optional** - Only include if your form has multiple paths
- **Test your config** - Run through a few questions to check the flow

### Sharing Configs

Created a config for a common application? Consider contributing it:
1. Remove any personal information from helper text
2. Test that it works from a fresh start
3. Submit a pull request to add it to `examples/`

## Privacy

Your answers stay local:
- Database: `*.db` files (gitignored)
- Exports: `*_answers.json` files (gitignored)
- Session files: `.sea_question_context.json`, `.sea_answer.md` (gitignored)
- Session logs: `session_log.json` (gitignored)

## Requirements

- **Python 3.6+** - No external dependencies (standard library only)
- **Claude Code CLI** - For AI collaboration feature
  - Install: See [Claude Code documentation](https://docs.anthropic.com/claude-code)
  - The `claude` command must be available in the same shell where you run `python3 sea_assistant.py`
  - Test with: `claude --version`
  - If Claude isn't in your PATH, the `[C]` option will show an error but the tool still works for manual answers

## Version History

- **v0.1** - Initial release: menu-driven interface, database, progress tracking
- **v0.2** - Claude Code integration, collaborative AI sessions
- **v0.3** - Session logging, use case documentation, config-driven forms
- **v0.4** - First-run config selection, form switching, separate databases per form

## License

MIT - Use freely, modify as needed.

## Why This Exists

Complex applications are overwhelming. Dozens of questions across multiple sections, each requiring specific details and coherent narratives. It's easy to lose track, forget what you've done, and feel paralyzed by the scope.

This tool helps anyone who:
- Finds large forms overwhelming
- Benefits from breaking big tasks into small steps
- Wants AI assistance without losing control of the process
- Needs to track progress across multiple sessions

**You don't have to do this alone.**

---

*Inspired by Choose Your Own Adventure books (1980s) and the belief that thoughtful AI collaboration can help people navigate complex processes.*
