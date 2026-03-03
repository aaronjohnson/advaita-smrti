"""smrti MCP server -- exposes the Memory API as Claude Code tools.

Usage (Claude Code .mcp.json):
    {
      "mcpServers": {
        "smrti": {
          "command": "smrti-mcp",
          "args": ["--memory-path", ".memory"]
        }
      }
    }
"""

import argparse
from typing import Optional

from mcp.server.fastmcp import FastMCP

from smrti import Memory

# --- server setup -----------------------------------------------------------

mcp = FastMCP("smrti", instructions=(
    "smrti provides structured project memory with three stores: "
    "tasks (procedural), decisions (episodic), and facts (semantic). "
    "Use these tools to read and write project knowledge that persists "
    "across sessions."
))

_mem: Optional[Memory] = None


def get_mem() -> Memory:
    global _mem
    if _mem is None:
        _mem = Memory(_memory_path)
    return _mem


def _fmt_task(task) -> str:
    """Format a single task for human reading."""
    icon = {"open": "[ ]", "in_progress": "[~]", "closed": "[x]", "archived": "[.]"}.get(task.status, "[?]")
    lines = [f"{icon} {task.id}: {task.title}"]
    if task.description:
        desc = task.description if len(task.description) <= 200 else task.description[:200] + "..."
        lines.append(f"    {desc}")
    parts = []
    if task.labels:
        parts.append(f"labels: {', '.join(task.labels)}")
    if task.parent_id:
        parts.append(f"parent: {task.parent_id}")
    if task.blocks:
        parts.append(f"blocks: {', '.join(task.blocks)}")
    if task.blocked_by:
        parts.append(f"blocked by: {', '.join(task.blocked_by)}")
    if parts:
        lines.append(f"    {' | '.join(parts)}")
    return "\n".join(lines)


def _fmt_decision(decision) -> str:
    """Format a single decision for human reading."""
    icon = {"abduction": "(?)", "deduction": "(>)", "induction": "(~)", "decided": "(*)"}.get(decision.phase, "(?)")
    lines = [f"{icon} {decision.id}: {decision.context}"]
    lines.append(f"    phase: {decision.phase}")
    if decision.task_id:
        lines.append(f"    task: {decision.task_id}")
    for h in decision.hypotheses:
        sel = " << SELECTED" if decision.selected == h.id else ""
        lines.append(f"    {h.id}. {h.description} (confidence: {h.confidence}){sel}")
        if h.rationale:
            lines.append(f"        rationale: {h.rationale}")
    if decision.selected and decision.selection_rationale:
        lines.append(f"    decision rationale: {decision.selection_rationale}")
    return "\n".join(lines)


def _fmt_fact(fact) -> str:
    """Format a single fact for human reading."""
    lines = [f"{fact.id}: {fact.fact}"]
    parts = []
    if fact.source:
        parts.append(f"source: {fact.source}")
    if fact.section:
        parts.append(f"section: {fact.section}")
    if fact.confidence < 1.0:
        parts.append(f"confidence: {fact.confidence}")
    if fact.labels:
        parts.append(f"labels: {', '.join(fact.labels)}")
    if fact.supersedes:
        parts.append(f"supersedes: {fact.supersedes}")
    if parts:
        lines.append(f"    {' | '.join(parts)}")
    return "\n".join(lines)


def _fmt_pattern(pattern) -> str:
    """Format a pattern for human reading."""
    conf = int(pattern.confidence * 10)
    bar = "#" * conf + "." * (10 - conf)
    line = f"[{bar}] {pattern.description}"
    if pattern.evidence:
        line += f"\n    evidence: {', '.join(pattern.evidence[:5])}"
    return line


def _fmt_connection(conn) -> str:
    """Format a connection for human reading."""
    return f"{conn.source_id} --{conn.relationship}--> {conn.target_id} (strength: {conn.strength})"


def _fmt_coherence(report) -> str:
    """Format a coherence report for human reading."""
    lines = [f"Coherence: {report.section} ({report.tasks_checked} checked, {report.tasks_complete} complete)"]
    if report.unresolved_dependencies:
        lines.append(f"Unresolved dependencies: {report.unresolved_dependencies}")
    if not report.findings:
        lines.append("No issues found.")
    for f in report.findings:
        icon = {"error": "!!", "warning": "!", "info": "-"}.get(f.severity, "-")
        lines.append(f"  {icon} [{f.category}] {f.message}")
    return "\n".join(lines)


# --- summary -----------------------------------------------------------------

@mcp.tool()
def memory_summary() -> str:
    """Get an overview of all memory stores -- task counts by status, decision counts by phase."""
    s = get_mem().summary()
    lines = [f"Tasks: {s['tasks']['total']}"]
    for status, count in s["tasks"].get("by_status", {}).items():
        lines.append(f"  {status}: {count}")
    lines.append(f"Decisions: {s['decisions']['total']}")
    for phase, count in s["decisions"].get("by_phase", {}).items():
        lines.append(f"  {phase}: {count}")
    return "\n".join(lines)


# --- tasks -------------------------------------------------------------------

@mcp.tool()
def task_list(status: Optional[str] = None, label: Optional[str] = None) -> str:
    """List tasks, optionally filtered by status (open/in_progress/closed/archived) or label."""
    tasks = get_mem().tasks.list(status=status, label=label)
    if not tasks:
        return "No tasks found."
    return f"{len(tasks)} tasks:\n\n" + "\n\n".join(_fmt_task(t) for t in tasks)


@mcp.tool()
def task_get(task_id: str) -> str:
    """Get a single task by ID. Returns full details including description, labels, metadata."""
    task = get_mem().tasks.get(task_id)
    if not task:
        return f"Error: Task {task_id} not found."
    return _fmt_task(task)


@mcp.tool()
def task_create(title: str, description: str = "", status: str = "open",
                labels: Optional[str] = None, parent_id: Optional[str] = None) -> str:
    """Create a new task. Labels is a comma-separated string (e.g. 'section:Data,priority:1')."""
    label_list = [l.strip() for l in labels.split(",")] if labels else None
    task = get_mem().tasks.create(
        title=title, description=description, status=status,
        labels=label_list, parent_id=parent_id,
    )
    return f"Created:\n{_fmt_task(task)}"


@mcp.tool()
def task_update(task_id: str, title: Optional[str] = None, description: Optional[str] = None,
                status: Optional[str] = None, labels: Optional[str] = None) -> str:
    """Update a task. Only provided fields are changed. Labels replaces the full list."""
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    if description is not None:
        kwargs["description"] = description
    if status is not None:
        kwargs["status"] = status
    if labels is not None:
        kwargs["labels"] = [l.strip() for l in labels.split(",")]
    task = get_mem().tasks.update(task_id, **kwargs)
    if not task:
        return f"Error: Task {task_id} not found."
    return f"Updated:\n{_fmt_task(task)}"


@mcp.tool()
def task_close(task_id: str) -> str:
    """Close a task (mark as complete)."""
    task = get_mem().tasks.close(task_id)
    if not task:
        return f"Error: Task {task_id} not found."
    return f"Closed:\n{_fmt_task(task)}"


@mcp.tool()
def task_ready() -> str:
    """List tasks that are ready to work on (no unresolved blockers)."""
    tasks = get_mem().tasks.ready()
    if not tasks:
        return "No tasks ready (all have unresolved blockers or none are open)."
    return f"{len(tasks)} ready:\n\n" + "\n\n".join(_fmt_task(t) for t in tasks)


@mcp.tool()
def task_block(task_id: str, blocks_id: str) -> str:
    """Mark that task_id blocks blocks_id (blocks_id cannot proceed until task_id is done)."""
    task = get_mem().tasks.block(task_id, blocks_id)
    if not task:
        return f"Error: Task {task_id} not found."
    return f"{task_id} now blocks {blocks_id}.\n{_fmt_task(task)}"


# --- decisions ---------------------------------------------------------------

@mcp.tool()
def decision_list(task_id: Optional[str] = None, phase: Optional[str] = None) -> str:
    """List decisions, optionally filtered by related task_id or phase (abduction/deduction/induction/decided)."""
    decisions = get_mem().decisions.list(task_id=task_id, phase=phase)
    if not decisions:
        return "No decisions found."
    return f"{len(decisions)} decisions:\n\n" + "\n\n".join(_fmt_decision(d) for d in decisions)


@mcp.tool()
def decision_get(decision_id: str) -> str:
    """Get a single decision with all its hypotheses and selection rationale."""
    decision = get_mem().decisions.get(decision_id)
    if not decision:
        return f"Error: Decision {decision_id} not found."
    return _fmt_decision(decision)


@mcp.tool()
def decision_begin(context: str, task_id: Optional[str] = None) -> str:
    """Start a new decision process. Context describes what we're deciding."""
    decision = get_mem().decisions.begin(context, task_id=task_id)
    return f"Decision started:\n{_fmt_decision(decision)}"


@mcp.tool()
def decision_record(context: str, selected: str, alternatives: Optional[str] = None,
                    rationale: str = "", task_id: Optional[str] = None) -> str:
    """Record an already-made decision in one step. Alternatives is a comma-separated string."""
    alt_list = [a.strip() for a in alternatives.split(",")] if alternatives else []
    decision = get_mem().decisions.record(
        context=context, selected=selected, alternatives=alt_list,
        rationale=rationale, task_id=task_id,
    )
    return f"Recorded:\n{_fmt_decision(decision)}"


@mcp.tool()
def decision_hypothesize(decision_id: str, description: str,
                         rationale: str = "", confidence: float = 0.5) -> str:
    """Add a hypothesis (candidate option) to a decision."""
    decision = get_mem().decisions.hypothesize(
        decision_id, description, rationale=rationale, confidence=confidence,
    )
    if not decision:
        return f"Error: Decision {decision_id} not found."
    return f"Hypothesis added ({len(decision.hypotheses)} total):\n{_fmt_decision(decision)}"


@mcp.tool()
def decision_decide(decision_id: str, hypothesis_id: str, rationale: str = "") -> str:
    """Select a hypothesis as the final decision. hypothesis_id is like 'h1', 'h2', etc."""
    decision = get_mem().decisions.decide(decision_id, hypothesis_id, rationale=rationale)
    if not decision:
        return f"Error: Decision {decision_id} not found."
    return f"Decided:\n{_fmt_decision(decision)}"


# --- facts -------------------------------------------------------------------

@mcp.tool()
def fact_create(fact: str, source: str = "", section: str = "",
                confidence: float = 1.0, labels: Optional[str] = None) -> str:
    """Record a stable fact. Source is where the fact came from. Section groups related facts."""
    label_list = [l.strip() for l in labels.split(",")] if labels else None
    f = get_mem().facts.create(
        fact=fact, source=source, section=section,
        confidence=confidence, labels=label_list,
    )
    return f"Recorded:\n{_fmt_fact(f)}"


@mcp.tool()
def fact_search(term: str) -> str:
    """Search facts by keyword."""
    facts = get_mem().facts.search(term)
    if not facts:
        return f"No facts matching '{term}'."
    return f"{len(facts)} facts matching '{term}':\n\n" + "\n\n".join(_fmt_fact(f) for f in facts)


@mcp.tool()
def fact_list(section: Optional[str] = None, label: Optional[str] = None) -> str:
    """List all current facts, optionally filtered by section or label."""
    mem = get_mem()
    if section:
        facts = mem.facts.by_section(section)
    elif label:
        facts = mem.facts.by_label(label)
    else:
        facts = mem.facts.all()
    if not facts:
        return "No facts found."
    return f"{len(facts)} facts:\n\n" + "\n\n".join(_fmt_fact(f) for f in facts)


@mcp.tool()
def fact_update(fact_id: str, fact: Optional[str] = None,
                source: Optional[str] = None, confidence: Optional[float] = None) -> str:
    """Update a fact. If fact text changes, creates a supersedes chain for history."""
    kwargs = {}
    if fact is not None:
        kwargs["fact"] = fact
    if source is not None:
        kwargs["source"] = source
    if confidence is not None:
        kwargs["confidence"] = confidence
    f = get_mem().facts.update(fact_id, **kwargs)
    if not f:
        return f"Error: Fact {fact_id} not found."
    return f"Updated:\n{_fmt_fact(f)}"


# --- synthesis ---------------------------------------------------------------

@mcp.tool()
def coherence_check(section: Optional[str] = None) -> str:
    """Check structural coherence -- dependency violations, gaps, completeness."""
    report = get_mem().synthesize.coherence_check(section=section)
    return _fmt_coherence(report)


@mcp.tool()
def patterns(label: Optional[str] = None) -> str:
    """Detect patterns across tasks -- label frequency, completion rates."""
    pats = get_mem().synthesize.patterns(label=label)
    if not pats:
        return "No patterns detected."
    return f"{len(pats)} patterns:\n\n" + "\n\n".join(_fmt_pattern(p) for p in pats)


@mcp.tool()
def connections(task_id: str) -> str:
    """Find all connections for a task -- dependencies, siblings, shared labels, related decisions."""
    conns = get_mem().synthesize.connections(task_id)
    if not conns:
        return f"No connections found for {task_id}."
    return f"{len(conns)} connections for {task_id}:\n\n" + "\n".join(_fmt_connection(c) for c in conns)


# --- maintenance -------------------------------------------------------------

@mcp.tool()
def rebuild_index() -> str:
    """Rebuild the SQLite index from JSONL source files. Use after manual JSONL edits."""
    count = get_mem().rebuild_index()
    return f"Index rebuilt: {count} records re-indexed."


# --- main --------------------------------------------------------------------

_memory_path = ".memory"


def main():
    global _memory_path

    parser = argparse.ArgumentParser(description="smrti MCP server")
    parser.add_argument("--memory-path", default=".memory",
                        help="Path to memory directory (default: .memory)")
    args = parser.parse_args()
    _memory_path = args.memory_path

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
