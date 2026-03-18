# RFC 007: Python Packaging and Repo Layout

**Status:** Concept
**Author:** Aaron Johnson
**Created:** 2026-02-20
**Parent:** [RFC 004](004-smrti-rename-and-typed-memory.md)
**Trigger:** When PyPI publishing or RFC 006 (web interface) forces it

## Purpose

Reorganize the repository into a standard Python package
layout. Consolidate loose top-level files to push the
rendered README above the fold on GitHub. Separate library
code from application code.

---

## Problem

The current top level has ~20 visible entries. GitHub
renders the file listing before the README, pushing it
below the fold. More importantly, the layout conflates
three concerns:

1. **Library** (`memory/`) — the reusable memory layer
2. **Application** (`sea_application_helper.py`,
   `sea_assistant.py`) — SEA-grant-specific code
3. **Tooling** (`validate_config.py`, `export_docs.py`,
   `migrate_to_memory.py`) — utility scripts

These should be separate.

---

## Current layout (20 rows)

```
.claude/
.github/
docs/
examples/
hooks/
memory/
tests/
business_direction_analysis.md
CHANGELOG.md
CLAUDE.md
config_schema.json
export_docs.py
LICENSE
migrate_to_memory.py
README.md
sea_application_helper.py
sea_assistant.py
smrti.py
validate_config.py
.gitignore
```

## Proposed layout (6 rows)

```
advaita-smrti/
├── smrti/                  # Python package
│   ├── __init__.py         # re-exports from memory
│   ├── __main__.py         # python -m smrti
│   ├── cli.py              # was smrti.py
│   ├── memory/             # unchanged internals
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── storage.py
│   │   ├── tasks.py
│   │   ├── decisions.py
│   │   ├── facts.py
│   │   └── synthesis.py
│   ├── tools/              # utility scripts
│   │   ├── validate.py     # was validate_config.py
│   │   ├── export.py       # was export_docs.py
│   │   └── migrate.py      # was migrate_to_memory.py
│   └── apps/               # application code
│       ├── helper.py       # was sea_application_helper.py
│       └── assistant.py    # was sea_assistant.py
├── tests/
├── docs/
│   ├── rfcs/
│   ├── examples/           # was examples/ (configs)
│   ├── CONFIG.md
│   ├── WORKFLOW.md
│   └── EXAMPLES.md
├── LICENSE
├── README.md
├── pyproject.toml
└── .gitignore
```

GitHub shows 6 entries before README:
`smrti/`, `tests/`, `docs/`, `LICENSE`, `README.md`, `.gitignore`

---

## What moves where

| Current | Proposed | Why |
|---|---|---|
| `memory/` | `smrti/memory/` | Inside the package |
| `smrti.py` | `smrti/cli.py` + `__main__.py` | Standard entry point |
| `sea_application_helper.py` | `smrti/apps/helper.py` | Application, not library |
| `sea_assistant.py` | `smrti/apps/assistant.py` | Application, not library |
| `validate_config.py` | `smrti/tools/validate.py` | Utility |
| `export_docs.py` | `smrti/tools/export.py` | Utility |
| `migrate_to_memory.py` | `smrti/tools/migrate.py` | One-time script |
| `config_schema.json` | `docs/config_schema.json` | Reference doc |
| `business_direction_analysis.md` | `docs/examples/` | Template |
| `examples/` | `docs/examples/` | Configs are docs by example |
| `CHANGELOG.md` | `docs/CHANGELOG.md` | History |
| `hooks/` | `.github/hooks/` | Convention |

## What stays

| File | Why |
|---|---|
| `README.md` | Required at root |
| `LICENSE` | Required at root |
| `CLAUDE.md` | Claude Code reads it from root |
| `.gitignore` | Required at root |
| `pyproject.toml` | New — replaces implicit setup |

---

## Packaging

### pyproject.toml

```toml
[project]
name = "advaita-smrti"
version = "0.5.0"
description = "Non-dual memory for structured knowledge elicitation"
license = "Apache-2.0"
requires-python = ">=3.6"
dependencies = []

[project.scripts]
smrti = "smrti.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Zero dependencies. `pip install advaita-smrti` gives
you the `smrti` command.

### PyPI name

`smrti` is taken (trivial package, 0.0.1 from 2019).
`advaita-smrti` is available. Use that.

---

## Import changes

```python
# Before
from memory import Memory
from memory.models import Task, Fact

# After
from smrti.memory import Memory
from smrti.memory.models import Task, Fact

# Or via package re-export
from smrti import Memory, Fact
```

All internal imports within `smrti/memory/` stay relative
(no change). Only external consumers and tests change.

---

## Migration

### What breaks

- Every `from memory import ...` in tests
- Every `from sea_application_helper import ...`
- `sys.path.insert(0, ...)` hacks in test files
- CI workflow paths
- Subtree prefix in day-shelter-kiosk (stays
  `advaita-smrti/` but internal paths change)
- CLAUDE.md code examples

### Migration steps

1. Create `smrti/` package with `__init__.py`
2. Move `memory/` into `smrti/memory/`
3. Move utility and application files
4. Add `pyproject.toml`
5. Update all imports (grep + sed)
6. Update tests (remove sys.path hacks, use package imports)
7. Update CI to install package (`pip install -e .`)
8. Update CLAUDE.md examples
9. Run full test suite
10. Pull into day-shelter-kiosk subtree

### Estimated touch count

~30 files. Same scale as the RFC 004 rename.

---

## Open questions

1. **`sea_*` rename** — `helper.py` and `assistant.py`
   are generic enough. Or should they stay SEA-prefixed
   until there's a second application?
2. **`apps/` vs. `examples/`** — is the SEA application
   an example of using smrti, or a first-class app?
3. **Namespace package?** — should `smrti.memory` be
   importable standalone, or only through the top-level
   `smrti` package?
4. **When to do this** — before or after RFC 006 (web
   interface)? The web interface will add more files
   to the repo. Better to have the layout clean first.

---

## Decision: not yet

This RFC exists to capture the plan. Implementation is
deferred until one of:
- PyPI publishing is needed
- RFC 006 (web interface) adds enough files to force it
- The top-level clutter becomes actively painful

The current layout works. It's just not pretty.
