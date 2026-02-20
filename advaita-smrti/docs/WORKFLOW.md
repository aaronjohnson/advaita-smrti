# Workflow Guide

How to use smrti day-to-day.

## Command Line Interface

The main entry point is `smrti.py`:

```bash
# Interactive mode (default)
smrti.py
smrti.py --db myform.db --config myconfig.json

# Quick commands
smrti.py list                    # Show available configs and databases
smrti.py status                  # Show progress summary
smrti.py validate config.json    # Validate a config file
smrti.py validate --all          # Validate all configs

# Export
smrti.py export pdf              # Export to PDF
smrti.py export html             # Export to HTML
smrti.py export markdown         # Export to Markdown
smrti.py export texinfo          # Export to Texinfo source
smrti.py export json             # Export answers as JSON

# With specific database
smrti.py export pdf --db ../other/form.db --config examples/myconfig.json
```

## The Adventure Menu

```
What would you like to do?

  [1] Work on high-priority questions (recommended to start)
  [2] Review business directions (if configured)
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

Menu options adapt to your form - items like "business directions" only appear when configured.

## Working with Claude

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

### Claude Commands

Once in a Claude Code session, you can use these commands:

| Command | Purpose |
|---------|---------|
| `/form-start` | Read the question context and begin discussion |
| `/form-save` | Write the finalized answer to `.sea_answer.md` |
| `/form-status` | Check current question and any pending answer |
| `/generate-config` | Generate a new config from pasted questions |
| `/export-docs` | Export to Markdown/Texinfo, build PDF |

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

View your session history (menu option 8) to:
- See how your thinking evolved over time
- Track which questions needed the most iteration
- Understand your own working patterns

## Files

| File | Purpose |
|------|---------|
| `sea_assistant.py` | Interactive CLI (main interface) |
| `sea_application_helper.py` | Core database and functions |
| `CLAUDE.md` | Instructions for Claude Code sessions |
| `validate_config.py` | Config validation script |
| `config_schema.json` | JSON Schema for IDE validation |
| `export_docs.py` | Export to Markdown/Texinfo, combine databases |

**Generated on first run:**

| File | Purpose |
|------|---------|
| `questions_config.json` | Active form (copied from your selection) |
| `*.db` | Database for each form (stores your answers) |
| `session_log.json` | Your session history |

## Exporting Your Work

Menu option [6] exports your answers in multiple formats:

| Format | Use Case |
|--------|----------|
| **JSON** | Data backup, transfer between systems |
| **Markdown** | Review on GitHub, share with others, simple editing |
| **Texinfo** | Professional PDF, HTML, or Info output |

### Texinfo Output

After exporting to texinfo, build your preferred format:

```bash
makeinfo --pdf form_export.texi     # PDF (requires TeX)
makeinfo --html form_export.texi    # HTML website
makeinfo form_export.texi           # Info format (Emacs/terminal)
```

### Combining Multiple Forms

Use `export_docs.py` for advanced exports:

```bash
# Export all databases to markdown
python3 export_docs.py --all

# Combine multiple forms into one PDF-ready document
python3 export_docs.py --all --combine --format texinfo

# Export specific databases
python3 export_docs.py college.db scholarship.db --combine
```

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
  - The `claude` command must be available in your PATH
  - Test with: `claude --version`
  - If Claude isn't in your PATH, the `[C]` option will show an error but the tool still works for manual answers
