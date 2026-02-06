# Form Copilot

> *Your AI co-pilot for complex paperwork.*

A toolkit for completing multi-section applications with AI collaboration. Load context, collaborate, capture answers, iterate. Two ways to work: directly in a Claude Code session (the queen's garden), or through the interactive Python menu.

## The Big Idea

Complex forms ask hard questions - questions requiring reflection, specific details, and coherent narratives. This tool provides structure, memory, AI partnership, and iteration.

## Two Ways to Work

### The Queen's Garden (preferred)

Work directly in a Claude Code session. Claude reads the config, presents questions, discusses answers collaboratively, banks context notes for later questions, and saves directly to the memory layer. No intermediary scripts needed.

```bash
# Start a Claude Code session in your project directory, then:
# 1. Claude reads the config to know all questions
# 2. You pick questions to work on (by priority, section, or interest)
# 3. Discuss and draft answers together
# 4. Claude saves to the memory layer
# 5. Context notes from earlier answers surface at relevant questions
# 6. Export when ready
```

This workflow proved itself completing 49/49 Oregon SEA questions in a single session. Context flows naturally between questions, and banked notes ensure coherent narrative across the entire application.

**Why it works:** The Python menu was designed to shuttle context between you and Claude via JSON files. But if you're already in a Claude session, the shuttling is unnecessary. Claude can hold the full picture - your config, your answers so far, your context notes - and be a genuine thought partner rather than a subprocess.

### The Interactive Menu (alternative)

The Python menu provides a standalone, structured workflow for anyone who prefers step-by-step guidance or isn't using Claude Code:

```bash
python3 form_copilot.py                # Interactive mode
python3 form_copilot.py list           # See available configs
python3 form_copilot.py status         # Check progress
```

Press `[C]` on any question to launch a Claude Code session with context auto-loaded. When you're done, Claude writes to `.sea_answer.md`, and the menu saves it to the database.

| Command | Purpose |
|---------|---------|
| `/form-start` | Read question context, begin discussion |
| `/form-save` | Write final answer to file |
| `/generate-config` | Create a config from pasted questions |
| `/export-docs` | Export to Markdown/Texinfo/PDF |

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

## Export

Three formats, three purposes:

```bash
# From memory layer (preferred):
python3 export_docs.py --memory .memory --config config.json                    # markdown
python3 export_docs.py --memory .memory --config config.json --format texinfo   # texinfo
python3 export_docs.py --memory .memory --config config.json --format latex     # tufte PDF

# Legacy SQLite:
python3 export_docs.py form.db
python3 export_docs.py form.db --format texinfo
python3 export_docs.py form.db --format latex
```

| Format | Purpose | Output |
|--------|---------|--------|
| **Markdown** | Lingua franca for AI tools and GitHub | `.md` |
| **Texinfo** | Structured multi-format (PDF, HTML, Info) | `.texi` |
| **LaTeX** | Tufte margin notes for review and comprehension | `.pdf` |

The LaTeX export uses the `tufte-handout` class to produce Robert Greene / 48 Laws of Power style margin notes with helper hints, priority badges, and clickable cross-references between questions.

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
- **Context notes** - Bank insights from one question for use in later questions

```bash
python3 form_copilot.py memory status     # See memory summary
python3 form_copilot.py memory patterns   # Find themes across answers
```

Storage: JSONL source of truth (git-friendly) + SQLite index (fast queries). SQLite answer storage is deprecated in favor of the memory layer.

See [RFC 002](docs/rfcs/002-memory-layer-spec.md) for the full specification.

## Documentation

- [CONFIG.md](docs/CONFIG.md) - Creating and validating configs
- [WORKFLOW.md](docs/WORKFLOW.md) - Menu options, Claude integration, files
- [EXAMPLES.md](docs/EXAMPLES.md) - Included example configs
- [CHANGELOG.md](CHANGELOG.md) - Version history (Alice in Wonderland themed)
- [RFCs](docs/rfcs/) - Architecture decisions and specifications

## Requirements

- Python 3.6+ (standard library only)
- [Claude Code CLI](https://docs.anthropic.com/claude-code) for AI features (queen's garden workflow)
- `texlive-latex-extra` for LaTeX/PDF export (optional)

## License

MIT

---

*Inspired by Choose Your Own Adventure books, Alice in Wonderland, and the belief that AI collaboration can help people navigate complex processes.*
