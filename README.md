# Form Copilot

> *Your AI co-pilot for complex paperwork.*

A Choose Your Own Adventure toolkit for completing multi-section applications with Claude Code. Load context, collaborate with AI, capture answers, iterate.

## The Big Idea

Complex forms ask hard questions - questions requiring reflection, specific details, and coherent narratives. This tool provides structure, memory, AI partnership, and iteration.

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
python3 sea_assistant.py
```

First run prompts you to choose a form. Each form gets its own database.

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

## Create Your Own Config

Paste any application into Claude:

```
Here are questions from my [grant / college app / loan form].
Create a form-copilot config JSON with sections, priorities, and helper text.

[paste questions]
```

Or use `/generate-config` in Claude Code. Validate with `python3 validate_config.py`.

See [docs/CONFIG.md](docs/CONFIG.md) for details.

## Documentation

- [CONFIG.md](docs/CONFIG.md) - Creating and validating configs
- [WORKFLOW.md](docs/WORKFLOW.md) - Menu options, Claude integration, files
- [EXAMPLES.md](docs/EXAMPLES.md) - Included example configs

## Requirements

- Python 3.6+ (standard library only)
- [Claude Code CLI](https://docs.anthropic.com/claude-code) for AI features

## License

MIT

---

*Inspired by Choose Your Own Adventure books and the belief that AI collaboration can help people navigate complex processes.*
