# Changelog

All notable changes to Form Copilot are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Commit messages follow an Alice in Wonderland theme.

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

### Commits

- `Down the rabbit hole` - RFC 001 proposes integration
- `Curiouser and curiouser` - Memory layer implementation
- `Through the looking glass` - RFC 000 baseline spec
- `Drink me` - Dual-write integration
- `Eat me` - CLI commands (growing the interface)
- `Off with their heads` - Memory becomes primary
- `Begin at the beginning` - Tests and future notes
- `I can't go back to yesterday` - Synthesis and migration

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
| 0.2.0 | 2026-02-05 | Down the Rabbit Hole | Memory layer refactor |
| 0.1.0 | 2026-01-27 | Initial Release | Core functionality |
