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

The included example is the Oregon SEA application - swap in your own `questions_config.json` for any form.

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
| `questions_config.json` | Form definition (swap for your form) |
| `business_direction_analysis.md` | Template for planning your direction |
| `.gitignore` | Excludes database and temp files |

## Customizing for Your Form

The system loads questions from `questions_config.json`. To use a different form:

1. Copy `questions_config.json` to create your own
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

## Privacy

Your answers stay local:
- Database: `*.db` files (gitignored)
- Exports: `*_answers.json` files (gitignored)
- Session files: `.sea_question_context.json`, `.sea_answer.md` (gitignored)
- Session logs: `session_log.json` (gitignored)

## Requirements

- Python 3.6+
- No external dependencies (standard library only)
- Claude Code CLI (for AI collaboration feature)

## Version History

- **v0.1** - Initial release: menu-driven interface, database, progress tracking
- **v0.2** - Claude Code integration, collaborative AI sessions
- **v0.3** - Session logging, use case documentation, config-driven forms

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
