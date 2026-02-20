"""Task operations for the memory layer.

Inspired by beads: git-backed task tracking with dependency graphs.
"""

import hashlib
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Task
from .storage import IndexDb, JsonlStore


def generate_id(prefix: str = "fc") -> str:
    """Generate hash-based task ID.

    Format: {prefix}-{5-char-alphanum}
    Uses timestamp + random to avoid collisions.
    """
    seed = f"{datetime.now().timestamp()}{random.random()}"
    hash_bytes = hashlib.sha256(seed.encode()).digest()
    # Convert to alphanumeric (base36-ish)
    chars = string.ascii_lowercase + string.digits
    result = ""
    for byte in hash_bytes[:5]:
        result += chars[byte % len(chars)]
    return f"{prefix}-{result}"


class TaskStore:
    """Task storage and operations."""

    def __init__(self, jsonl: JsonlStore, index: IndexDb, prefix: str = "fc"):
        self.jsonl = jsonl
        self.index = index
        self.prefix = prefix
        self._cache: Dict[str, Task] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load all tasks into memory cache."""
        self._cache = {}
        for record in self.jsonl.iterate():
            task = Task.from_dict(record)
            self._cache[task.id] = task

    def create(
        self,
        title: str,
        description: str = "",
        status: str = "open",
        parent_id: Optional[str] = None,
        labels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Create a new task."""
        task = Task(
            id=generate_id(self.prefix),
            title=title,
            description=description,
            status=status,
            parent_id=parent_id,
            labels=labels or [],
            metadata=metadata or {},
        )
        self._save(task)
        return task

    def _save(self, task: Task) -> None:
        """Save task to storage and index."""
        task.updated_at = datetime.now().isoformat()
        self.jsonl.append(task.to_dict())
        self.index.index_task(task.to_dict())
        self._cache[task.id] = task

    def get(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self._cache.get(task_id)

    def update(self, task_id: str, **fields) -> Optional[Task]:
        """Update task fields."""
        task = self.get(task_id)
        if not task:
            return None

        for key, value in fields.items():
            if hasattr(task, key):
                setattr(task, key, value)

        self._save(task)
        return task

    def close(self, task_id: str) -> Optional[Task]:
        """Mark task as closed."""
        return self.update(task_id, status="closed")

    def archive(self, task_id: str) -> Optional[Task]:
        """Mark task as archived (for decay)."""
        return self.update(task_id, status="archived")

    def list(
        self,
        status: Optional[str] = None,
        label: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> List[Task]:
        """Query tasks matching criteria."""
        task_ids = self.index.query_tasks(status=status, label=label, parent_id=parent_id)
        return [self._cache[tid] for tid in task_ids if tid in self._cache]

    def ready(self) -> List[Task]:
        """List tasks with no unresolved blocked_by dependencies."""
        task_ids = self.index.query_ready_tasks()
        return [self._cache[tid] for tid in task_ids if tid in self._cache]

    def block(self, task_id: str, blocks_id: str) -> Optional[Task]:
        """Add dependency: task_id blocks blocks_id."""
        task = self.get(task_id)
        blocked_task = self.get(blocks_id)
        if not task or not blocked_task:
            return None

        if blocks_id not in task.blocks:
            task.blocks.append(blocks_id)
        if task_id not in blocked_task.blocked_by:
            blocked_task.blocked_by.append(task_id)

        self._save(task)
        self._save(blocked_task)
        return task

    def unblock(self, task_id: str, blocks_id: str) -> Optional[Task]:
        """Remove dependency."""
        task = self.get(task_id)
        blocked_task = self.get(blocks_id)
        if not task or not blocked_task:
            return None

        if blocks_id in task.blocks:
            task.blocks.remove(blocks_id)
        if task_id in blocked_task.blocked_by:
            blocked_task.blocked_by.remove(task_id)

        self._save(task)
        self._save(blocked_task)
        return task

    def children(self, task_id: str) -> List[Task]:
        """List child tasks."""
        return self.list(parent_id=task_id)

    def history(self, task_id: str) -> List[Dict[str, Any]]:
        """List all versions of a task from JSONL."""
        versions = []
        for record in self.jsonl.iterate():
            if record.get("id") == task_id:
                versions.append(record)
        return versions

    def all(self) -> List[Task]:
        """Return all tasks."""
        return list(self._cache.values())

    def compact(self) -> None:
        """Compact JSONL file to remove old versions."""
        # Keep only latest version of each task
        self.jsonl.rewrite([t.to_dict() for t in self._cache.values()])
