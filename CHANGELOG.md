# Changelog

All notable changes to Form Copilot are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Commit messages follow an Alice in Wonderland theme.

---

## [0.3.0] - 2026-02-05 - "The Queen's Garden"

> "I could tell you my adventures---beginning from this morning," said Alice a little timidly:
> "but it's no use going back to yesterday, because I was a different person then."

The queen's garden session: 49/49 SEA questions answered in a single Claude Code session, proving the "queen's garden" workflow where Claude IS the copilot with no Python intermediary. LaTeX export with Tufte margin notes, all formats from memory layer.

### Added

- **LaTeX export with Tufte margin notes** (`export_docs.py --format latex`)
  - Robert Greene / 48 Laws of Power style layout
  - Wide right margins with helper hints, priority badges, clickable cross-references
  - `tufte-handout` document class with `hyperref` internal links
  - Automatic PDF compilation via `pdflatex` (two-pass for link resolution)
  - `--no-pdf` flag for `.tex` source only

- **All export formats from memory layer** (`--memory` + `--config` flags)
  - Markdown: `--format markdown --memory .memory --config config.json`
  - Texinfo: `--format texinfo --memory .memory --config config.json`
  - LaTeX: `--format latex --memory .memory --config config.json`
  - No SQLite required for any export path

- **Context note pattern** for cross-question reference
  - Bank context as open tasks with `context-note` label
  - Pull relevant notes when reaching tagged questions
  - Enables coherent narrative across 49 questions

### Changed

- **SQLite helper deprecated** - import is now optional/lazy
  - Memory layer is the primary and preferred storage
  - SQLite path still works for legacy databases
  - All new features target memory layer first

### Proved

- **Queen's garden workflow** - Claude session as the copilot
  - Skip `sea_assistant.py` entirely
  - Read config, show questions, discuss, save to memory directly
  - Context notes banked during discussion surface at relevant questions
  - 49/49 questions completed in one session

### Commits

- `Through the looking-glass` - LaTeX export with Tufte margin notes
- `Curiouser and curiouser` - All export formats from memory layer

---

## [0.2.0] - 2026-02-05 - "Down the Rabbit Hole"

> "But I don't want to go among mad people," Alice remarked.
> "Oh, you can't help that," said the Cat: "we're all mad here."

A major refactor introducing a memory layer inspired by [beads](https://github.com/steveyegge/beads) and [quint-code](https://github.com/m0n0x41d/quint-code).

### Added

- **Memory layer** (`memory/` module)
  - Task storage with hash-based IDs, labels, dependencies
  - Decision trails with hypothesis tracking
  - Pattern synthesis for insights across answers
  - JSONL source of truth + SQLite index cache

- **RFC documentation** (`docs/rfcs/`)
  - RFC 000: Form Copilot baseline specification
  - RFC 001: Beads/Quint integration proposal
  - RFC 002: Memory layer specification

- **CLI commands** (`form_copilot.py memory`)
  - `memory status` - Show memory layer summary
  - `memory tasks` - List all tasks
  - `memory decisions` - List decision trails
  - `memory patterns` - Run pattern synthesis
  - `memory decide` - Start a decision
  - `memory hypo` - Add hypothesis
  - `memory select` - Choose hypothesis

- **Interactive menu** (`sea_assistant.py`)
  - `[P] Patterns` - Synthesize insights from answers
  - Decision trail creation from menu

- **Migration tool** (`migrate_to_memory.py`)
  - Migrate existing SQLite answers to memory layer
  - Dry-run mode for preview
  - Preserves question IDs, status, notes, timestamps

- **Tests** (`tests/test_memory.py`)
  - 30 tests covering memory layer operations

### Changed

- **Storage architecture**
  - Answers now stored in Memory layer (primary)
  - SQLite remains for config cache (questions/sections)
  - SQLite answers table optional (`SQLITE_ENABLED=False`)

- **SEAApplicationHelper**
  - Writes to Memory layer first
  - Reads answers from Memory, falls back to SQLite
  - New methods: `get_memory_summary()`, `synthesize_patterns()`

### Security

- `.memory/` added to `.gitignore` - personal answers never committed to public repo
- Pre-commit hook (`hooks/pre-commit`) - blocks commits containing personal data
  - Install: `ln -sf ../../hooks/pre-commit .git/hooks/pre-commit`

### Commits

- `Down the rabbit hole` - RFC 001 proposes integration
- `Curiouser and curiouser` - Memory layer implementation
- `Through the looking glass` - RFC 000 baseline spec
- `Drink me` - Dual-write integration
- `Eat me` - CLI commands (growing the interface)
- `Off with their heads` - Memory becomes primary
- `Begin at the beginning` - Tests and future notes
- `I can't go back to yesterday` - Synthesis and migration
- `We're all mad here` - Protect personal data from git
- `A stitch in time` - Pre-commit hook for defense in depth

---

## [0.1.0] - 2026-01-27 - Initial Release

### Added

- Interactive menu system for form completion
- Claude Code integration for AI-assisted answers
- SQLite storage for questions, sections, answers
- Multiple export formats (JSON, Markdown, Texinfo, PDF, HTML)
- Config validation with JSON Schema
- Session logging and history
- Example configs (Oregon SEA, College App, Creative Grant, Product Concept)
- Test suite (76 tests)

### Features

- Priority-based workflow (work on important questions first)
- Business direction support (multiple paths through same form)
- Helper text for difficult questions
- Progress dashboard with section breakdown
- Form switching between different configs

---

## Version History Summary

| Version | Date | Codename | Focus |
|---------|------|----------|-------|
| 0.3.0 | 2026-02-05 | The Queen's Garden | LaTeX export, memory-first exports, queen's garden workflow |
| 0.2.0 | 2026-02-05 | Down the Rabbit Hole | Memory layer refactor |
| 0.1.0 | 2026-01-27 | Initial Release | Core functionality |
