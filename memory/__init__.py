"""Memory layer for form-copilot.

A pure Python implementation inspired by:
- beads (https://github.com/steveyegge/beads) - git-backed task graphs
- quint-code (https://github.com/m0n0x41d/quint-code) - decision reasoning trails

See docs/rfcs/002-memory-layer-spec.md for full specification.

Usage:
    from memory import Memory

    mem = Memory(".memory")

    # Tasks
    task = mem.tasks.create("Answer question", description="...")
    mem.tasks.close(task.id)

    # Decisions
    decision = mem.decisions.begin("How to frame answer")
    mem.decisions.hypothesize(decision.id, "Option A")
    mem.decisions.decide(decision.id, "h1", rationale="Better fit")

    # Synthesis
    patterns = mem.synthesize.patterns()
"""

import json
from pathlib import Path
from typing import Optional

from .models import Task, Decision, Hypothesis, Pattern, Connection, DecaySummary
from .storage import JsonlStore, IndexDb
from .tasks import TaskStore
from .decisions import DecisionStore
from .synthesis import Synthesizer


__all__ = [
    "Memory",
    "Task",
    "Decision",
    "Hypothesis",
    "Pattern",
    "Connection",
    "DecaySummary",
]


class Memory:
    """Main interface to the memory layer.

    Provides access to:
    - tasks: Task storage and operations
    - decisions: Decision reasoning trails
    - synthesize: Pattern detection and context decay
    """

    def __init__(self, path: str = ".memory", prefix: str = "fc"):
        """Initialize memory layer.

        Args:
            path: Directory for memory storage (default: .memory)
            prefix: ID prefix for tasks (default: fc for form-copilot)
        """
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

        self.prefix = prefix
        self._init_config()

        # Initialize storage
        self._tasks_jsonl = JsonlStore(self.path / "tasks.jsonl")
        self._decisions_jsonl = JsonlStore(self.path / "decisions.jsonl")
        self._index = IndexDb(self.path / "index.db")

        # Initialize stores
        self.tasks = TaskStore(self._tasks_jsonl, self._index, prefix=prefix)
        self.decisions = DecisionStore(self._decisions_jsonl, self._index, prefix="qt")
        self.synthesize = Synthesizer(self.tasks, self.decisions)

    def _init_config(self) -> None:
        """Initialize or load config."""
        config_path = self.path / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                self._config = json.load(f)
        else:
            from datetime import datetime
            self._config = {
                "prefix": self.prefix,
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
            }
            with open(config_path, "w") as f:
                json.dump(self._config, f, indent=2)

    def rebuild_index(self) -> None:
        """Rebuild SQLite index from JSONL files."""
        self._index.rebuild_from_jsonl(self._tasks_jsonl, self._decisions_jsonl)
        # Reload caches
        self.tasks._load_cache()
        self.decisions._load_cache()

    def compact(self) -> None:
        """Compact JSONL files to remove old versions."""
        self.tasks.compact()
        self.decisions.compact()

    def summary(self) -> dict:
        """Get overall summary of memory state."""
        return self.synthesize.summary()

    def close(self) -> None:
        """Close database connections."""
        self._index.close()


def init(path: str = ".memory", prefix: str = "fc") -> Memory:
    """Initialize a new memory layer.

    Convenience function for CLI usage.
    """
    return Memory(path, prefix)
