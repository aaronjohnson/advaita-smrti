# Changelog

All notable changes to Form Copilot are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Commit messages follow an Alice in Wonderland theme.

---

## [0.5.0] - 2026-03-02 - "The Cheshire Cat's Grin"

> "We're all mad here. I'm mad. You're mad."
> "How do you know I'm mad?" said Alice.
> "You must be," said the Cat, "or you wouldn't have come here."

The Cat's grin remains after the Cat has gone. smrti is now an installable
package — the memory persists wherever you `pip install` it, independent
of any particular checkout.

### Added

- **PyPI packaging** — `pip install advaita-smrti` (or `advaita-smrti[mcp]`)
  - `smrti/` installable package with all memory modules
  - `pyproject.toml` with hatchling build system
  - Two console_scripts entry points: `smrti`, `smrti-mcp`
  - Bundled slash commands delivered by `smrti init`

- **`smrti init` command** — one-step project setup
  - Creates `.memory/`, `.mcp.json`, `.claude/commands/`
  - Merges into existing `.mcp.json` if present
  - Copies 6 slash commands from package data

- **`decisions.record()` convenience method** (closes #7)
  - Record already-made decisions in one call
  - `decision_record` MCP tool for the same workflow

- **Human-readable MCP output** — all 22 tools return formatted text
  instead of raw JSON. Cleaner in the tool result accordion and
  easier for Claude to interpret in conversation.

- **`python -m smrti`** — module execution support

### Changed

- **Import path** — `from smrti import Memory` (canonical)
- **`memory/` is now a deprecation shim** — `from memory import Memory`
  still works with a `DeprecationWarning`
- **`mcp_server.py`** delegates to `smrti.mcp:main` with deprecation warning
- **Test imports** updated to `from smrti import ...`
- **CLI** — `smrti memory status|tasks|decisions|patterns|rebuild|compact`
- **MCP server** invoked as `smrti-mcp` (installed entry point)
- **CLAUDE.md / README.md** — updated setup instructions and import examples

### Closed

- #7 — Convenience method for recording already-decided decisions
- #8 — Add search/query method to facts store (already existed)
- #9 — CLI for quick queries without dropping to Python

---

## [0.4.0] - 2026-02-19 - "The Looking-Glass Insects"

> "Of course they answer to their names?" the Gnat remarked carelessly.
> "I never knew them to do it."

Index drift detection: the memory layer now notices when JSONL and SQLite fall out of sync, and tells you why and how to fix it. Like the Looking-Glass insects that don't answer to their names, records written outside the API don't register in the index.

### Added

- **Index drift detection** — `Memory()` init checks JSONL unique IDs against SQLite row count. Raises `IndexDriftError` with an explanation if they differ.
- **`ignore_drift` parameter** — `Memory(ignore_drift=True)` bypasses the check for rebuild operations.
- **`form_copilot.py memory rebuild`** — CLI command to repair the SQLite index from JSONL source of truth.
- **`form_copilot.py memory compact`** — CLI command to remove old JSONL versions.
- **`JsonlStore.unique_id_count()`** — count unique IDs without loading all data.
- **`IndexDb.task_count()` / `decision_count()`** — fast row counts from SQLite.
- **3 new tests** — drift detection, drift override, and rebuild-after-drift.
- **CLAUDE.md guidance** — documents the Memory Python API and explains when/why to use it over direct JSONL writes.
- **README section** — complementary use of form-copilot memory with Claude Code's MEMORY.md.

### Changed

- `rebuild_from_jsonl()` and `rebuild_index()` now return the count of tasks re-indexed.

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
| 0.5.0 | 2026-03-02 | The Cheshire Cat's Grin | PyPI packaging, `smrti init`, human-readable MCP |
| 0.4.0 | 2026-02-19 | The Looking-Glass Insects | Index drift detection |
| 0.3.0 | 2026-02-05 | The Queen's Garden | LaTeX export, memory-first exports, queen's garden workflow |
| 0.2.0 | 2026-02-05 | Down the Rabbit Hole | Memory layer refactor |
| 0.1.0 | 2026-01-27 | Initial Release | Core functionality |
