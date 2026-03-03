"""Memory layer for smrti (advaita-smrti).

A pure Python implementation inspired by:
- beads (https://github.com/steveyegge/beads) - git-backed task graphs
- quint-code (https://github.com/m0n0x41d/quint-code) - decision reasoning trails
- ENGRAM (arxiv:2511.12960) - typed memory stores

See docs/rfcs/002-memory-layer-spec.md for full specification.

Usage:
    from smrti import Memory

    mem = Memory(".memory")

    # Tasks
    task = mem.tasks.create("Answer question", description="...")
    mem.tasks.close(task.id)

    # Decisions
    decision = mem.decisions.begin("How to frame answer")
    mem.decisions.hypothesize(decision.id, "Option A")
    mem.decisions.decide(decision.id, "h1", rationale="Better fit")

    # Facts (semantic memory)
    fact = mem.facts.create("Applicant has 10 years experience", source="interview")
    mem.facts.by_section("background")

    # Synthesis
    patterns = mem.synthesize.patterns()
"""

import json
import sys
from pathlib import Path
from typing import Optional

from .models import Task, Decision, Hypothesis, Fact, Pattern, Connection, DecaySummary, CoherenceFinding, CoherenceReport
from .storage import JsonlStore, IndexDb
from .tasks import TaskStore
from .decisions import DecisionStore
from .facts import FactStore
from .synthesis import Synthesizer


class IndexDriftError(Exception):
    """Raised when the SQLite index has drifted from the JSONL source of truth."""
    pass


__all__ = [
    "Memory",
    "IndexDriftError",
    "Task",
    "Decision",
    "Hypothesis",
    "Fact",
    "Pattern",
    "Connection",
    "DecaySummary",
    "CoherenceFinding",
    "CoherenceReport",
]


class Memory:
    """Main interface to the memory layer.

    Provides access to:
    - tasks: Task storage and operations (procedural)
    - decisions: Decision reasoning trails (episodic)
    - facts: Stable knowledge store (semantic)
    - synthesize: Pattern detection and context decay
    """

    def __init__(self, path: str = ".memory", prefix: str = "sm", ignore_drift: bool = False):
        """Initialize memory layer.

        Args:
            path: Directory for memory storage (default: .memory)
            prefix: ID prefix for tasks (default: sm for smrti)
            ignore_drift: If True, skip index drift check (use only for rebuild)
        """
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

        self.prefix = prefix
        self._init_config()

        # Initialize storage
        self._tasks_jsonl = JsonlStore(self.path / "tasks.jsonl")
        self._decisions_jsonl = JsonlStore(self.path / "decisions.jsonl")
        self._facts_jsonl = JsonlStore(self.path / "facts.jsonl")
        self._index = IndexDb(self.path / "index.db")

        # Initialize stores
        self.tasks = TaskStore(self._tasks_jsonl, self._index, prefix=prefix)
        self.decisions = DecisionStore(self._decisions_jsonl, self._index, prefix="qt")
        self.facts = FactStore(self._facts_jsonl, self._index, prefix=prefix)
        self.synthesize = Synthesizer(self.tasks, self.decisions)

        # Detect index drift (hard gate unless explicitly overridden)
        if not ignore_drift:
            self._check_index_drift()

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

    def _check_index_drift(self) -> None:
        """Check if SQLite index has drifted from JSONL source of truth.

        Raises IndexDriftError if drift is detected. This happens when
        records are appended directly to the JSONL files bypassing the
        Memory Python API.
        """
        jsonl_task_count = self._tasks_jsonl.unique_id_count()
        index_task_count = self._index.task_count()

        jsonl_decision_count = self._decisions_jsonl.unique_id_count()
        index_decision_count = self._index.decision_count()

        jsonl_fact_count = self._facts_jsonl.unique_id_count()
        index_fact_count = self._index.fact_count()

        if (jsonl_task_count != index_task_count
                or jsonl_decision_count != index_decision_count
                or jsonl_fact_count != index_fact_count):
            raise IndexDriftError(
                f"\n"
                f"  Index drift detected.\n"
                f"    Tasks:     JSONL has {jsonl_task_count}, index has {index_task_count}\n"
                f"    Decisions: JSONL has {jsonl_decision_count}, index has {index_decision_count}\n"
                f"    Facts:     JSONL has {jsonl_fact_count}, index has {index_fact_count}\n"
                f"\n"
                f"  This typically happens when records are appended directly to\n"
                f"  JSONL files bypassing the Memory Python API. The API writes to\n"
                f"  both JSONL and SQLite together, keeping them in sync.\n"
                f"\n"
                f"  If you need to write JSONL directly (bulk import, migration),\n"
                f"  discuss with the project owner first, then run rebuild after.\n"
                f"\n"
                f"  To repair: smrti memory rebuild\n"
            )

    def rebuild_index(self) -> int:
        """Rebuild SQLite index from JSONL files.

        Returns:
            Number of tasks re-indexed.
        """
        count = self._index.rebuild_from_jsonl(
            self._tasks_jsonl, self._decisions_jsonl, self._facts_jsonl
        )
        # Reload caches
        self.tasks._load_cache()
        self.decisions._load_cache()
        self.facts._load_cache()
        return count

    def compact(self) -> None:
        """Compact JSONL files to remove old versions."""
        self.tasks.compact()
        self.decisions.compact()
        self.facts.compact()

    def summary(self) -> dict:
        """Get overall summary of memory state."""
        return self.synthesize.summary()

    def close(self) -> None:
        """Close database connections."""
        self._index.close()


def init(path: str = ".memory", prefix: str = "sm") -> Memory:
    """Initialize a new memory layer.

    Convenience function for CLI usage.
    """
    return Memory(path, prefix)
