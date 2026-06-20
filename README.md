# smrti

> स्मृति — "that which is remembered"

Non-dual memory for structured knowledge elicitation. A
toolkit for completing multi-section applications with AI
collaboration, built around four typed memory stores.

## Memory Types

| Store | File | What it holds |
|---|---|---|
| **Procedural** | `tasks.jsonl` | Questions, dependencies, status |
| **Episodic** | `decisions.jsonl` | Events, choices, rationale |
| **Semantic** | `facts.jsonl` | Stable facts, preferences |
| **Ephemeral** | `ephemeral/` | Session scratch (not persisted) |

JSONL is the source of truth (git-friendly, append-only).
SQLite is a regenerable index for fast queries.

## Install

```bash
pip install advaita-smrti          # core (no dependencies)
pip install advaita-smrti[mcp]     # with MCP server support
```

## Quick Start

```bash
cd my-project
smrti init                  # creates .memory/, .mcp.json, .claude/commands/
# Restart Claude Code — 21 memory tools + 6 slash commands are ready
```

Or use the Python API directly:

```python
from smrti import Memory

mem = Memory(".memory")
task = mem.tasks.create("Answer question", description="...")
mem.tasks.close(task.id)
mem.close()
```

## CLI

```bash
smrti init                  # Set up memory in current project
smrti memory status         # Memory layer summary
smrti memory tasks          # List all tasks
smrti memory rebuild        # Repair index from JSONL
smrti memory compact        # Remove old JSONL versions
smrti --version             # Print version
```

## Create Your Own Config

Paste any application into Claude:

```
Here are questions from my [grant / college app / form].
Create a smrti config JSON with sections, priorities,
and helper text.

[paste questions]
```

Or use `/smrti-config` in Claude Code. Validate with
`python3 validate_config.py`.

## What Makes This Different

Most memory systems start from conversation. smrti starts
from **structured forms**: sections, questions, dependencies,
priorities. This gives it:

- The form itself as procedural memory (no extraction needed)
- Coherence checking across answers
- Dependency-aware ordering
- A clear "done" criterion

Maps to grant applications, clinical intake, legal discovery,
insurance claims — anywhere humans complete complex multi-part
forms with an AI collaborator.

## Bench

Does memory actually help? smṛti-bench runs the same prompt battery
against agents with and without memory tools, across platforms
(Claude Code, Gemini, Antigravity). Scoring uses Answer Set
Programming (clingo) for declarative grading with cross-prompt
coherence and regression detection.

See [RFC 013](docs/rfcs/013-bench-rationale.md) for the full rationale.

## Documentation

- [CONFIG.md](docs/CONFIG.md) — Creating and validating configs
- [WORKFLOW.md](docs/WORKFLOW.md) — CLI, Claude integration, files
- [RFCs](docs/rfcs/) — Architecture decisions and specs

## Inspirations and References

- [beads](https://github.com/steveyegge/beads) — git-backed
  task graphs
- [quint-code](https://github.com/m0n0x41d/quint-code) —
  decision reasoning trails
- [ENGRAM](https://arxiv.org/abs/2511.12960) (Patel & Patel,
  2026) — typed memory stores: episodic, semantic, procedural
- [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564)
  (Hu et al., 2025) — survey and taxonomy
- [Context Engineering: Sessions & Memory](https://www.kaggle.com/whitepaper-context-engineering-sessions-and-memory)
  (Google, 2025) — whitepaper
- [haft](https://github.com/m0n0x41d/haft) — engineering-decisions
  engine; FPF governance substrate with evidence decay and parity
  enforcement (same author as quint-code)
- [FPF — First Principles Framework](https://github.com/ailev/FPF)
  (Anatoly Levenchuk / ailev) — the systems-engineering methodology
  haft is built on
- [OKF — Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
  (Google Cloud, 2026; Apache-2.0) — vendor-neutral Markdown + YAML-frontmatter
  standard for agent knowledge; complements MCP (MCP = tool access,
  OKF = the knowledge itself). Closely mirrors smrti's typed stores.

## See Also

- [Zep](https://github.com/getzep/zep) — temporal knowledge
  graphs for agent memory
- [Letta](https://github.com/letta-ai/letta) — filesystem
  memory that outperforms specialized systems
- [Mem0](https://github.com/mem0ai/mem0) — structured
  summarization and conflict resolution
- [Pinecone](https://www.pinecone.io/) — vector database for
  semantic retrieval
- [nit](https://github.com/asheux/nit) ([nit.tools](https://nit.tools)) —
  Rust terminal-first editor with a pure protocol-layer core and an
  MCP server

## License

Apache 2.0 — see [LICENSE](LICENSE)

---

*advaita-smrti (अद्वैत-स्मृति) — the tool and the thinker
are not separate.*
