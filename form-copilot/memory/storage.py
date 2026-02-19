"""Storage layer for JSONL files and SQLite index.

JSONL is the source of truth (git-friendly, append-only).
SQLite is a regenerable cache for fast queries.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional


class JsonlStore:
    """Append-only JSONL file storage."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: Dict[str, Any]) -> None:
        """Append a record to the JSONL file."""
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def read_all(self) -> List[Dict[str, Any]]:
        """Read all records from the JSONL file."""
        if not self.path.exists():
            return []
        records = []
        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records

    def iterate(self) -> Iterator[Dict[str, Any]]:
        """Iterate over records without loading all into memory."""
        if not self.path.exists():
            return
        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def rewrite(self, records: List[Dict[str, Any]]) -> None:
        """Rewrite the entire file (for compaction/updates)."""
        with open(self.path, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")


class IndexDb:
    """SQLite index for fast queries. Regenerable from JSONL."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables if they don't exist."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                status TEXT,
                parent_id TEXT,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS task_labels (
                task_id TEXT,
                label TEXT,
                PRIMARY KEY (task_id, label)
            );

            CREATE TABLE IF NOT EXISTS task_blocks (
                task_id TEXT,
                blocks_id TEXT,
                PRIMARY KEY (task_id, blocks_id)
            );

            CREATE TABLE IF NOT EXISTS task_blocked_by (
                task_id TEXT,
                blocked_by_id TEXT,
                PRIMARY KEY (task_id, blocked_by_id)
            );

            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                context TEXT,
                task_id TEXT,
                phase TEXT,
                selected TEXT,
                selection_rationale TEXT,
                created_at TEXT,
                decided_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_id);
            CREATE INDEX IF NOT EXISTS idx_decisions_task ON decisions(task_id);
            CREATE INDEX IF NOT EXISTS idx_decisions_phase ON decisions(phase);
        """)
        self.conn.commit()

    def index_task(self, task: Dict[str, Any]) -> None:
        """Index a task for fast queries."""
        self.conn.execute("""
            INSERT OR REPLACE INTO tasks (id, title, description, status, parent_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task["id"],
            task["title"],
            task.get("description", ""),
            task.get("status", "open"),
            task.get("parent_id"),
            task.get("created_at"),
            task.get("updated_at"),
        ))

        # Clear and re-add labels
        self.conn.execute("DELETE FROM task_labels WHERE task_id = ?", (task["id"],))
        for label in task.get("labels", []):
            self.conn.execute(
                "INSERT OR IGNORE INTO task_labels (task_id, label) VALUES (?, ?)",
                (task["id"], label)
            )

        # Clear and re-add blocks
        self.conn.execute("DELETE FROM task_blocks WHERE task_id = ?", (task["id"],))
        for blocks_id in task.get("blocks", []):
            self.conn.execute(
                "INSERT OR IGNORE INTO task_blocks (task_id, blocks_id) VALUES (?, ?)",
                (task["id"], blocks_id)
            )

        # Clear and re-add blocked_by
        self.conn.execute("DELETE FROM task_blocked_by WHERE task_id = ?", (task["id"],))
        for blocked_by_id in task.get("blocked_by", []):
            self.conn.execute(
                "INSERT OR IGNORE INTO task_blocked_by (task_id, blocked_by_id) VALUES (?, ?)",
                (task["id"], blocked_by_id)
            )

        self.conn.commit()

    def index_decision(self, decision: Dict[str, Any]) -> None:
        """Index a decision for fast queries."""
        self.conn.execute("""
            INSERT OR REPLACE INTO decisions
            (id, context, task_id, phase, selected, selection_rationale, created_at, decided_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision["id"],
            decision["context"],
            decision.get("task_id"),
            decision.get("phase", "abduction"),
            decision.get("selected"),
            decision.get("selection_rationale", ""),
            decision.get("created_at"),
            decision.get("decided_at"),
        ))
        self.conn.commit()

    def query_tasks(
        self,
        status: Optional[str] = None,
        label: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> List[str]:
        """Query task IDs matching criteria."""
        query = "SELECT DISTINCT t.id FROM tasks t"
        conditions = []
        params = []

        if label:
            query += " JOIN task_labels tl ON t.id = tl.task_id"
            conditions.append("tl.label = ?")
            params.append(label)

        if status:
            conditions.append("t.status = ?")
            params.append(status)

        if parent_id:
            conditions.append("t.parent_id = ?")
            params.append(parent_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor = self.conn.execute(query, params)
        return [row["id"] for row in cursor.fetchall()]

    def query_ready_tasks(self) -> List[str]:
        """Find tasks with no unresolved blocked_by dependencies."""
        # Tasks that are open and have no open blockers
        cursor = self.conn.execute("""
            SELECT t.id FROM tasks t
            WHERE t.status = 'open'
            AND NOT EXISTS (
                SELECT 1 FROM task_blocked_by tb
                JOIN tasks blocker ON tb.blocked_by_id = blocker.id
                WHERE tb.task_id = t.id AND blocker.status != 'closed'
            )
        """)
        return [row["id"] for row in cursor.fetchall()]

    def query_decisions(
        self,
        task_id: Optional[str] = None,
        phase: Optional[str] = None,
    ) -> List[str]:
        """Query decision IDs matching criteria."""
        query = "SELECT id FROM decisions"
        conditions = []
        params = []

        if task_id:
            conditions.append("task_id = ?")
            params.append(task_id)

        if phase:
            conditions.append("phase = ?")
            params.append(phase)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor = self.conn.execute(query, params)
        return [row["id"] for row in cursor.fetchall()]

    def rebuild_from_jsonl(self, tasks_store: JsonlStore, decisions_store: JsonlStore) -> None:
        """Rebuild index from JSONL files."""
        # Clear existing data
        self.conn.executescript("""
            DELETE FROM tasks;
            DELETE FROM task_labels;
            DELETE FROM task_blocks;
            DELETE FROM task_blocked_by;
            DELETE FROM decisions;
        """)

        # Re-index tasks (keep latest version of each)
        tasks_by_id = {}
        for record in tasks_store.iterate():
            tasks_by_id[record["id"]] = record
        for task in tasks_by_id.values():
            self.index_task(task)

        # Re-index decisions (keep latest version of each)
        decisions_by_id = {}
        for record in decisions_store.iterate():
            decisions_by_id[record["id"]] = record
        for decision in decisions_by_id.values():
            self.index_decision(decision)

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
