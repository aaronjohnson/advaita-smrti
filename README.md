# Form Copilot

> *Your AI co-pilot for complex paperwork.*

A Choose Your Own Adventure toolkit for completing multi-section applications with Claude Code. Load context, collaborate with AI, capture answers, iterate.

## The Big Idea

Complex forms ask hard questions - questions requiring reflection, specific details, and coherent narratives. This tool provides structure, memory, AI partnership, and iteration.

## Why Not Just Ralph Wiggum?

If you're familiar with [Ralph Wiggum loops](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) - the "keep trying until done" pattern - you might wonder why form completion needs something different.

**Ralph Wiggum** excels at greenfield tasks with clear completion criteria: build a REST API, get tests passing, generate code. The loop reads files, sees what exists, tries again. No explicit memory needed.

**Form Copilot** handles a different problem: complex questions where *why* matters as much as *what*. Your answer to "What problem does your business solve?" might inform "Describe your competitive advantage" - and you need to remember your reasoning, not just the text.

| | Ralph Wiggum | Form Copilot |
|---|---|---|
| Memory | Files + git | Explicit task/decision store |
| Reasoning | Implicit in code | Decision trails with hypotheses |
| Sessions | One long loop | Multi-session with synthesis |
| Completion | `<promise>DONE</promise>` | Task status + dependencies |
| Best for | "Make tests pass" | "Help me think through this" |

*In Simpsons terms: Ralph runs into the wall until there's a hole. Lisa keeps a journal of which walls are load-bearing.*

*In Alice terms: Ralph drinks the bottle to see what happens. The Memory layer is the White Queen, remembering "things that happened the week after next."*

## Use Cases

| Application Type | Example |
|-----------------|---------|
| **Self-Employment Programs** | Oregon SEA, state business grants |
| **College Applications** | Common App, UC apps, supplements |
| **Research Grants** | NSF, NIH, private foundations |
| **Immigration** | I-485, N-400, visa applications |
| **Business Loans** | SBA loans, bank applications |
| **Fellowships** | Fulbright, Rhodes, professional fellowships |

Four [example configs](docs/EXAMPLES.md) included. Or create your own from any source.

## Quick Start

```bash
python3 form_copilot.py                # Interactive mode
python3 form_copilot.py list           # See available configs
python3 form_copilot.py status         # Check progress
python3 form_copilot.py export pdf     # Export to PDF
```

First run prompts you to choose a form. Each form gets its own database.

Export to **Markdown**, **Texinfo**, **HTML**, or **PDF**. Combine multiple forms into one document.

## The Magic: Claude Collaboration

Press `[C]` on any question to launch a Claude Code session:

1. Context auto-loaded (question, hints, related answers)
2. Collaborate with Claude to craft your answer
3. Claude writes to `.sea_answer.md`
4. You approve, it saves to database

**The pattern:** load context → dialog → capture → iterate

### Claude Commands

| Command | Purpose |
|---------|---------|
| `/form-start` | Read question context, begin discussion |
| `/form-save` | Write final answer to file |
| `/generate-config` | Create a config from pasted questions |
| `/export-docs` | Export to Markdown/Texinfo/PDF |

## Create Your Own Config

Paste any application into Claude:

```
Here are questions from my [grant / college app / loan form].
Create a form-copilot config JSON with sections, priorities, and helper text.

[paste questions]
```

Or use `/generate-config` in Claude Code. Validate with `python3 validate_config.py`.

See [docs/CONFIG.md](docs/CONFIG.md) for details.

## Memory Layer

Form Copilot includes a memory layer inspired by [beads](https://github.com/steveyegge/beads) and [quint-code](https://github.com/m0n0x41d/quint-code):

- **Tasks** - Track answers with hash-based IDs, labels, dependencies
- **Decisions** - Record reasoning trails (hypotheses considered, why you chose one)
- **Synthesis** - Detect patterns across accumulated answers

```bash
python3 form_copilot.py memory status     # See memory summary
python3 form_copilot.py memory patterns   # Find themes across answers
```

Storage: JSONL source of truth (git-friendly) + SQLite index (fast queries).

See [RFC 002](docs/rfcs/002-memory-layer-spec.md) for the full specification.

## Documentation

- [CONFIG.md](docs/CONFIG.md) - Creating and validating configs
- [WORKFLOW.md](docs/WORKFLOW.md) - Menu options, Claude integration, files
- [EXAMPLES.md](docs/EXAMPLES.md) - Included example configs
- [RFCs](docs/rfcs/) - Architecture decisions and specifications

## Requirements

- Python 3.6+ (standard library only)
- [Claude Code CLI](https://docs.anthropic.com/claude-code) for AI features

## License

MIT

---

*Inspired by Choose Your Own Adventure books and the belief that AI collaboration can help people navigate complex processes.*
