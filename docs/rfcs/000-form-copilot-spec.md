# RFC 000: Form Copilot Specification

**Status:** Historical (superseded by RFC 004)
**Author:** Aaron Johnson
**Created:** 2026-02-05
**Superseded:** 2026-02-20 — form-copilot renamed to smrti (RFC 004)
**Purpose:** Capture what form-copilot was, how it worked, and why it was built this way

> **Note:** This RFC documents the original form-copilot architecture.
> The project was renamed to **smrti** (advaita-smrti) in RFC 004.
> File references (`form_copilot.py`, SQLite-primary storage) reflect
> the state at time of writing. See RFC 004 for current architecture.

---

## What Form Copilot Is

Form Copilot is a collaborative tool for completing multi-section applications and questionnaires. It combines:
- A structured question database with priorities and dependencies
- An interactive menu system for navigating questions
- Claude Code integration for AI-assisted answer drafting
- Export capabilities for multiple formats

**Core insight:** Complex applications (job applications, grant proposals, business plans) benefit from:
1. Breaking the work into prioritized questions
2. Tracking progress across sessions
3. AI collaboration that maintains context
4. Exporting polished results

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    form_copilot.py                       │
│                   (CLI Entry Point)                      │
│         Commands: interactive, export, validate          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   sea_assistant.py                       │
│                (Interactive Menu UI)                     │
│                                                          │
│  [1] Work on priorities    [5] View progress            │
│  [2] Continue where left   [6] Export answers           │
│  [3] Browse sections       [C] Work with Claude         │
│  [4] Jump to question      [Q] Quit                     │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌──────────────────────┐    ┌──────────────────────────┐
│ sea_application_     │    │   Claude Code Session    │
│     helper.py        │    │                          │
│                      │    │  .sea_question_context   │
│  SQLite Database     │    │        ↓                 │
│  - sections          │    │  /form-start             │
│  - questions         │    │  /form-save              │
│  - answers           │    │        ↓                 │
│  - business_dirs     │    │  .sea_answer.md          │
└──────────────────────┘    └──────────────────────────┘
```

---

## Design Decisions

### D1: SQLite for Answer Storage

**Decision:** Store answers in SQLite database per form.

**Alternatives considered:**
- JSON files (simpler, but no querying)
- Markdown files (human-readable, but parsing complex)
- Cloud storage (requires connectivity)

**Rationale:**
- Structured queries (by section, status, priority)
- Transactions prevent corruption
- Single file, portable
- Python stdlib support (no dependencies)

**Trade-offs accepted:**
- Not git-friendly (binary file)
- Harder to manually inspect than JSON/Markdown
- Per-form databases means no cross-form queries

---

### D2: JSON Config for Question Structure

**Decision:** Define questions, sections, and dependencies in JSON config files.

**Alternatives considered:**
- YAML (more readable, extra dependency)
- Database tables (less portable)
- Hardcoded (not reusable)

**Rationale:**
- JSON Schema validation available
- No extra dependencies
- Easy to create new forms from examples
- Shareable as templates

**Schema enforces:**
- Required fields (id, question_text, section)
- Valid types (text, long_text, yes_no, number, choice)
- Priority levels (1-3)
- Dependency references (depends_on)

---

### D3: Subprocess to Claude Code CLI

**Decision:** Launch Claude Code as subprocess, communicate via files.

**Alternatives considered:**
- Claude API directly (more control, more code)
- MCP server (async, complex)
- Embedded agent (tight coupling)

**Rationale:**
- Claude Code already exists and works
- User stays in familiar Claude Code environment
- File-based handoff is simple and debuggable
- No API key management in form-copilot

**Protocol:**
1. Python writes `.sea_question_context.json`
2. Python launches `claude` with initial prompt
3. User works in Claude Code, uses `/form-start`, `/form-save`
4. Claude Code writes `.sea_answer.md`
5. Python reads answer, confirms save with user
6. Python stores in database

**Trade-offs accepted:**
- User must manually exit Claude Code
- No background processing
- Requires Claude Code installed

---

### D4: Priority-Based Workflow

**Decision:** Questions have priority 1-3. Default workflow starts with priority 1.

**Alternatives considered:**
- Strict linear order (inflexible)
- Dependency-only ordering (complex for users)
- No ordering (overwhelming)

**Rationale:**
- Priority 1 = foundational (answer these first, other answers reference them)
- Priority 2 = important (bulk of the application)
- Priority 3 = nice-to-have (if time permits)
- User can override via section browsing or direct jump

---

### D5: Session Logging

**Decision:** Log events to `session_log.json` for analytics and history.

**Events tracked:**
- `claude_session_start` - When user enters Claude collaboration
- `answer_saved` - When answer committed to database
- `notes_added` - When user adds notes without full answer

**Rationale:**
- Understand usage patterns
- Track answer evolution over time
- Debug issues
- Potential for "session replay" feature

---

### D6: Multiple Export Formats

**Decision:** Support JSON, Markdown, Texinfo (→ PDF/HTML).

**Rationale:**
- JSON: Machine-readable, backup
- Markdown: Human-readable, pasteable
- Texinfo: Professional typesetting for formal submissions

**Why Texinfo over LaTeX:**
- Simpler syntax
- Built-in PDF and HTML generation via `makeinfo`
- Good enough for application documents

---

## Component Specifications

### Question Context (`.sea_question_context.json`)

Written by Python before launching Claude:

```json
{
  "question_id": "biz_1",
  "question_text": "What problem does your business solve?",
  "helper_text": "Think about the pain point you address...",
  "section": "Business Overview",
  "priority": 1,
  "current_answer": null,
  "notes": "Some rough thoughts...",
  "related_answers": {
    "biz_2": "We target small business owners..."
  }
}
```

### Answer Output (`.sea_answer.md`)

Written by Claude Code, read by Python:

```markdown
Our business solves the complexity problem in multi-step
applications. Users struggle to maintain context across
dozens of questions spanning multiple sections...
```

No headers, no metadata. Just the answer text.

### Database Schema

```sql
CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,      -- machine name
    title TEXT NOT NULL,     -- display title
    description TEXT
);

CREATE TABLE questions (
    id TEXT PRIMARY KEY,     -- e.g., "biz_1"
    section_id INTEGER,
    question_text TEXT NOT NULL,
    question_type TEXT DEFAULT 'text',
    priority INTEGER DEFAULT 3,
    depends_on TEXT,         -- comma-separated question IDs
    helper_text TEXT,
    FOREIGN KEY (section_id) REFERENCES sections(id)
);

CREATE TABLE answers (
    question_id TEXT PRIMARY KEY,
    answer_text TEXT,
    notes TEXT,              -- user's working notes
    last_updated TEXT,       -- ISO timestamp
    status TEXT DEFAULT 'not_started',
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE business_directions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    selected INTEGER DEFAULT 0,
    created_at TEXT
);
```

### Config Schema (Simplified)

```json
{
  "form_name": "Oregon SEA Application",
  "form_id": "oregon_sea",
  "sections": [
    {
      "name": "business_overview",
      "title": "Business Overview",
      "questions": [
        {
          "id": "biz_1",
          "question_text": "What problem does your business solve?",
          "question_type": "long_text",
          "priority": 1,
          "helper_text": "Think about..."
        }
      ]
    }
  ]
}
```

---

## Invariants

Properties that must always hold:

1. **Every question has a unique ID** within a config
2. **Answer status is one of:** `not_started`, `in_progress`, `complete`
3. **Priority is 1, 2, or 3** (1 = highest)
4. **depends_on references existing question IDs**
5. **Database and config stay in sync** (questions table mirrors config)
6. **Claude session files are ephemeral** (deleted or overwritten each session)

---

## Extension Points

Where the architecture anticipates change:

1. **New question types** - Add to schema, update UI rendering
2. **New export formats** - Add exporter function, register in CLI
3. **New storage backends** - Replace `sea_application_helper.py` (RFC 001/002)
4. **New AI integrations** - Replace Claude subprocess with different agent
5. **Business directions** - Optional feature, can be extended or removed

---

## Known Limitations

1. **Single-user** - No collaboration features
2. **Local-only** - No sync, cloud backup
3. **Sequential Claude sessions** - Can't run multiple in parallel
4. **No undo** - Answers overwrite, history only in session_log
5. **English-only** - No i18n support
6. **No encryption** - Answers stored in plaintext

---

## Relationship to RFCs

| RFC | Relationship |
|-----|--------------|
| 000 (this) | Baseline specification (historical) |
| 001 | Proposes replacing storage with beads/quint patterns |
| 002 | Specifies pure Python memory layer |
| 003 | Recursive context and complementary cognition |
| 004 | Rename to smrti, typed memory stores (supersedes this RFC) |
| 005 | Ephemeral store |

---

## Glossary

| Term | Meaning |
|------|---------|
| **Form** | A complete application/questionnaire (config + database) |
| **Section** | Logical grouping of questions |
| **Question** | Single prompt requiring user response |
| **Answer** | User's response to a question |
| **Priority** | Importance ranking (1=foundational, 3=optional) |
| **Helper text** | Guidance shown to user for difficult questions |
| **Business direction** | Optional: different paths through same form |
| **SEA** | Self-Employment Assistance (original use case: Oregon SEA program) |

---

## Version History

| Date | Change |
|------|--------|
| 2026-02-05 | Initial specification (retroactive documentation) |

---

## Meta

This specification was written after the fact, reconstructing decisions from code and usage. Future decisions should be documented as they're made, using the memory layer's decision trail feature.

The self-referential nature is intentional: form-copilot helps complete complex multi-section documents; this specification is a complex multi-section document about form-copilot.
