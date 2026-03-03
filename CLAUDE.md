# smrti — Claude Code Integration

smrti (स्मृति) is structured project memory for collaborative
AI sessions. It handles any multi-step work: applications,
project planning, retrospectives, questionnaires, onboarding.

Repository: advaita-smrti (अद्वैत-स्मृति, "non-dual memory")

## MCP Server

smrti exposes its memory layer as an MCP server. When configured,
21 tools are available in every Claude Code session — no imports,
no bridge files.

### Setup

```bash
pip install advaita-smrti[mcp]
cd my-project
smrti init    # creates .memory/, .mcp.json, .claude/commands/
```

Or manually add to `.mcp.json`:

```json
{
  "mcpServers": {
    "smrti": {
      "command": "smrti-mcp",
      "args": ["--memory-path", ".memory"]
    }
  }
}
```

### Tools

| Category | Tools |
|----------|-------|
| Tasks | `task_list`, `task_get`, `task_create`, `task_update`, `task_close`, `task_ready`, `task_block` |
| Decisions | `decision_list`, `decision_get`, `decision_begin`, `decision_hypothesize`, `decision_decide` |
| Facts | `fact_list`, `fact_search`, `fact_create`, `fact_update` |
| Synthesis | `memory_summary`, `coherence_check`, `patterns`, `connections` |
| Maintenance | `rebuild_index` |

## Commands

Slash commands orchestrate the MCP tools into workflows:

| Command | Purpose |
|---------|---------|
| `/smrti-start` | Pick up a task, load context, begin work |
| `/smrti-save` | Persist work to memory |
| `/smrti-status` | Show progress across all stores |
| `/smrti-recall` | Pull relevant context from memory |
| `/smrti-config` | Generate config from new questions/tasks |
| `/smrti-export` | Export completed work to documents |

Commands live in `.claude/commands/` and are auto-discovered.

## Memory Layer

Three typed stores (see RFC 004):

| Store | File | What it holds |
|---|---|---|
| Procedural | `tasks.jsonl` | Work items, dependencies, status |
| Episodic | `decisions.jsonl` | Choices, hypotheses, rationale |
| Semantic | `facts.jsonl` | Stable facts, preferences |

**JSONL is source of truth.** SQLite index is regenerable.

Never write JSONL directly — the MCP tools and Python API
keep JSONL and SQLite in sync. Direct writes cause index
drift. If you must bypass, run `rebuild_index` after.

### Python API (when MCP isn't available)

```python
from smrti import Memory
mem = Memory(".memory")

# Tasks (procedural)
task = mem.tasks.create("Title", description="...")
mem.tasks.update(task.id, status="closed", description="Updated answer")

# Decisions (episodic)
decision = mem.decisions.begin("Context")
mem.decisions.hypothesize(decision.id, "Option A")
mem.decisions.decide(decision.id, "h1", rationale="Why")

# Facts (semantic)
mem.facts.create("Key insight", source="session")

mem.close()
```

## Working Style

- Ask clarifying questions before drafting
- Offer 2-3 approaches when there are meaningful choices
- Help the user think through implications
- Be encouraging but honest about gaps
- Suggest concrete next steps

## Session Flow

1. **Recall**: `/smrti-recall` or `/smrti-status` — what do we know?
2. **Start**: `/smrti-start` — pick a task, load context
3. **Explore**: discuss, gather the user's thoughts
4. **Draft**: propose an answer or work product
5. **Refine**: iterate based on feedback
6. **Save**: `/smrti-save` — persist to memory

## Legacy Bridge (deprecated)

The old pattern used bridge files between `sea_assistant.py`
and Claude Code:
- `.sea_question_context.json` — context written by Python CLI
- `.sea_answer.md` — answer written by Claude

This still works for backward compatibility but the MCP path
is preferred. See `docs/WORKFLOW.md` for details.
