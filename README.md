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

## Quick Start

```bash
# Clone
git clone https://github.com/aaronjohnson/advaita-smrti.git
cd advaita-smrti

# Interactive mode
python3 smrti.py

# Or work directly in a Claude Code session (preferred)
# Claude reads the config, presents questions, saves to memory
```

No dependencies beyond Python 3.6+ standard library.

## CLI

```bash
smrti.py                    # Interactive mode
smrti.py list               # Available configs and databases
smrti.py status             # Progress summary
smrti.py validate cfg.json  # Validate a config file

smrti.py export markdown    # Export answers
smrti.py export pdf         # Export to PDF (requires texinfo)

smrti.py memory status      # Memory layer summary
smrti.py memory rebuild     # Repair index from JSONL
smrti.py memory compact     # Remove old JSONL versions
```

## Create Your Own Config

Paste any application into Claude:

```
Here are questions from my [grant / college app / form].
Create a smrti config JSON with sections, priorities,
and helper text.

[paste questions]
```

Or use `/generate-config` in Claude Code. Validate with
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

## See Also

- [Zep](https://github.com/getzep/zep) — temporal knowledge
  graphs for agent memory
- [Letta](https://github.com/letta-ai/letta) — filesystem
  memory that outperforms specialized systems
- [Mem0](https://github.com/mem0ai/mem0) — structured
  summarization and conflict resolution
- [Pinecone](https://www.pinecone.io/) — vector database for
  semantic retrieval

## License

MIT

---

*advaita-smrti (अद्वैत-स्मृति) — the tool and the thinker
are not separate.*
