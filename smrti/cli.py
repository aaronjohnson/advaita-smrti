"""smrti CLI — command-line interface for structured memory.

Usage:
    smrti init                  # Initialize memory in current project
    smrti memory status         # Memory layer summary
    smrti memory tasks          # List all tasks
    smrti memory rebuild        # Repair index from JSONL
    smrti --version             # Print version
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

from smrti import __version__, Memory, IndexDriftError


def cmd_init(args):
    """Initialize smrti in the current project."""
    memory_path = Path(args.memory_path)
    mcp_json_path = Path(".mcp.json")
    commands_dir = Path(".claude/commands")

    created = []

    # 1. Create .memory/ directory
    if not memory_path.exists():
        mem = Memory(str(memory_path))
        mem.close()
        created.append(str(memory_path) + "/")
    else:
        print(f"  {memory_path}/ already exists, skipping")

    # 2. Write or merge .mcp.json
    smrti_entry = {
        "command": "smrti-mcp",
        "args": ["--memory-path", str(memory_path)],
    }

    if mcp_json_path.exists():
        with open(mcp_json_path) as f:
            mcp_config = json.load(f)
        if "smrti" not in mcp_config.get("mcpServers", {}):
            mcp_config.setdefault("mcpServers", {})["smrti"] = smrti_entry
            with open(mcp_json_path, "w") as f:
                json.dump(mcp_config, f, indent=2)
                f.write("\n")
            created.append(".mcp.json (updated)")
        else:
            print("  .mcp.json already has smrti entry, skipping")
    else:
        mcp_config = {"mcpServers": {"smrti": smrti_entry}}
        with open(mcp_json_path, "w") as f:
            json.dump(mcp_config, f, indent=2)
            f.write("\n")
        created.append(".mcp.json")

    # 3. Copy slash commands
    commands_dir.mkdir(parents=True, exist_ok=True)
    try:
        import importlib.resources as pkg_resources
        # Python 3.9+: use files()
        if hasattr(pkg_resources, "files"):
            commands_pkg = pkg_resources.files("smrti.commands")
            for item in commands_pkg.iterdir():
                if item.name.endswith(".md"):
                    dest = commands_dir / item.name
                    if not dest.exists():
                        dest.write_text(item.read_text())
                        created.append(str(dest))
                    else:
                        print(f"  {dest} already exists, skipping")
        else:
            # Fallback for Python 3.7-3.8
            _copy_commands_fallback(commands_dir, created)
    except Exception:
        _copy_commands_fallback(commands_dir, created)

    if created:
        print(f"\nsmrti initialized ({len(created)} files):")
        for path in created:
            print(f"  + {path}")
    else:
        print("\nsmrti already initialized, nothing to do.")

    print("\nRestart Claude Code to pick up the MCP server and slash commands.")


def _copy_commands_fallback(commands_dir, created):
    """Copy commands from package data using file path fallback."""
    pkg_dir = Path(__file__).parent / "commands"
    if pkg_dir.exists():
        for md_file in pkg_dir.glob("*.md"):
            dest = commands_dir / md_file.name
            if not dest.exists():
                shutil.copy2(md_file, dest)
                created.append(str(dest))


def cmd_memory(args):
    """Memory layer operations."""
    memory_path = args.memory_path or ".memory"

    # rebuild and compact need ignore_drift since they fix it
    skip_drift = args.memory_command in ("rebuild", "compact")

    try:
        memory = Memory(memory_path, ignore_drift=skip_drift)
    except IndexDriftError as e:
        print(f"\n{e}", file=sys.stderr)
        sys.exit(1)

    if args.memory_command == "status":
        summary = memory.summary()
        print(f"\n{'=' * 50}")
        print("  Memory Layer Status")
        print(f"{'=' * 50}")
        print(f"\nPath: {memory_path}")
        print(f"\nTasks: {summary['tasks']['total']}")
        if summary["tasks"]["by_status"]:
            for status, count in summary["tasks"]["by_status"].items():
                print(f"  - {status}: {count}")
        print(f"\nDecisions: {summary['decisions']['total']}")
        if summary["decisions"]["by_phase"]:
            for phase, count in summary["decisions"]["by_phase"].items():
                print(f"  - {phase}: {count}")
        print()

    elif args.memory_command == "tasks":
        tasks = memory.tasks.all()
        if not tasks:
            print("No tasks in memory")
        else:
            print(f"\n{'=' * 60}")
            print(f"  Tasks ({len(tasks)} total)")
            print(f"{'=' * 60}\n")
            for task in tasks:
                status_icon = {
                    "open": "o",
                    "in_progress": "~",
                    "closed": "*",
                    "archived": ".",
                }.get(task.status, "?")
                print(f"{status_icon} {task.id}: {task.title}")
                if task.labels:
                    print(f"    labels: {', '.join(task.labels)}")
                if args.verbose and task.description:
                    desc = (
                        task.description[:100] + "..."
                        if len(task.description) > 100
                        else task.description
                    )
                    print(f"    {desc}")
            print()

    elif args.memory_command == "decisions":
        decisions = memory.decisions.all()
        if not decisions:
            print("No decisions in memory")
        else:
            print(f"\n{'=' * 60}")
            print(f"  Decisions ({len(decisions)} total)")
            print(f"{'=' * 60}\n")
            for decision in decisions:
                phase_icon = {
                    "abduction": "?",
                    "deduction": ">",
                    "induction": "~",
                    "decided": "*",
                }.get(decision.phase, "?")
                print(f"{phase_icon} {decision.id}: {decision.context}")
                print(
                    f"    phase: {decision.phase}, hypotheses: {len(decision.hypotheses)}"
                )
                if decision.selected:
                    print(f"    selected: {decision.selected}")
            print()

    elif args.memory_command == "patterns":
        patterns = memory.synthesize.patterns(label=args.label)
        if not patterns:
            print("No patterns detected")
        else:
            print(f"\n{'=' * 60}")
            print(f"  Patterns ({len(patterns)} detected)")
            print(f"{'=' * 60}\n")
            for pattern in patterns:
                conf = int(pattern.confidence * 10)
                confidence_bar = "#" * conf + "." * (10 - conf)
                print(f"[{confidence_bar}] {pattern.description}")
                if args.verbose and pattern.evidence:
                    print(f"    evidence: {', '.join(pattern.evidence[:5])}")
            print()

    elif args.memory_command == "decide":
        if not args.context:
            print("Error: --context required for starting a decision")
            sys.exit(1)
        decision = memory.decisions.begin(args.context, task_id=args.task_id)
        print(f"Decision started: {decision.id}")
        print(f"Context: {decision.context}")
        print(f"Phase: {decision.phase}")
        print("\nNext: Add hypotheses with 'smrti memory hypo'")

    elif args.memory_command == "hypo":
        if not args.decision_id or not args.description:
            print("Error: --decision and --description required")
            sys.exit(1)
        decision = memory.decisions.hypothesize(
            args.decision_id,
            args.description,
            rationale=args.rationale or "",
            confidence=args.confidence or 0.5,
        )
        if decision:
            print(f"Hypothesis added to {decision.id}")
            print(f"Total hypotheses: {len(decision.hypotheses)}")
        else:
            print(f"Error: Decision {args.decision_id} not found")

    elif args.memory_command == "select":
        if not args.decision_id or not args.hypothesis_id:
            print("Error: --decision and --hypothesis required")
            sys.exit(1)
        decision = memory.decisions.decide(
            args.decision_id,
            args.hypothesis_id,
            rationale=args.rationale or "",
        )
        if decision:
            print(f"Decision {decision.id}: selected {decision.selected}")
            print(f"Rationale: {decision.selection_rationale}")
        else:
            print("Error: Could not select hypothesis")

    elif args.memory_command == "rebuild":
        count = memory.rebuild_index()
        print(f"Index rebuilt from JSONL: {count} tasks re-indexed.")

    elif args.memory_command == "compact":
        memory.compact()
        summary = memory.summary()
        print(
            f"JSONL compacted. Tasks: {summary['tasks']['total']}, "
            f"Decisions: {summary['decisions']['total']}"
        )

    memory.close()


def main():
    parser = argparse.ArgumentParser(
        description="smrti -- non-dual memory for structured knowledge elicitation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
    %(prog)s init                               # Set up memory in current project
    %(prog)s memory status                      # Memory layer summary
    %(prog)s memory tasks                       # List all tasks
    %(prog)s memory rebuild                     # Repair index from JSONL
""",
    )

    parser.add_argument(
        "--version", "-V", action="version", version=f"smrti {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    init_parser = subparsers.add_parser(
        "init", help="Initialize smrti in the current project"
    )
    init_parser.add_argument(
        "--memory-path",
        "-m",
        default=".memory",
        help="Memory directory path (default: .memory)",
    )

    # memory command
    memory_parser = subparsers.add_parser("memory", help="Memory layer operations")
    memory_parser.add_argument(
        "memory_command",
        choices=[
            "status",
            "tasks",
            "decisions",
            "patterns",
            "decide",
            "hypo",
            "select",
            "rebuild",
            "compact",
        ],
        help="Memory operation",
    )
    memory_parser.add_argument(
        "--memory-path",
        "-m",
        metavar="PATH",
        default=".memory",
        help="Memory directory path (default: .memory)",
    )
    memory_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    memory_parser.add_argument(
        "--label", "-l", metavar="LABEL", help="Filter by label (for patterns)"
    )
    memory_parser.add_argument(
        "--context", metavar="TEXT", help="Decision context (for decide)"
    )
    memory_parser.add_argument(
        "--task-id", "-t", metavar="ID", help="Related task ID (for decide)"
    )
    memory_parser.add_argument(
        "--decision-id",
        "--decision",
        metavar="ID",
        help="Decision ID (for hypo, select)",
    )
    memory_parser.add_argument(
        "--hypothesis-id",
        "--hypothesis",
        metavar="ID",
        help="Hypothesis ID (for select)",
    )
    memory_parser.add_argument(
        "--description", metavar="TEXT", help="Hypothesis description (for hypo)"
    )
    memory_parser.add_argument(
        "--rationale", metavar="TEXT", help="Rationale (for hypo, select)"
    )
    memory_parser.add_argument(
        "--confidence", type=float, metavar="N", help="Confidence 0.0-1.0 (for hypo)"
    )

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "memory":
        cmd_memory(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
