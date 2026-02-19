"""Synthesis operations for the memory layer.

Extracts insights from accumulated tasks and decisions.
Pattern detection, cross-references, and context decay.

Note: Full synthesis requires LLM integration.
This module provides the structure; LLM calls can be added later.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from .models import Connection, DecaySummary, Pattern, Task, Decision
from .tasks import TaskStore
from .decisions import DecisionStore


class Synthesizer:
    """Synthesis operations across tasks and decisions."""

    def __init__(self, tasks: TaskStore, decisions: DecisionStore):
        self.tasks = tasks
        self.decisions = decisions

    def patterns(
        self,
        label: Optional[str] = None,
        since: Optional[str] = None,
    ) -> List[Pattern]:
        """Detect patterns across tasks.

        This is a simplified implementation that finds:
        - Recurring labels
        - Common words in titles/descriptions

        For full synthesis, integrate with Claude API.
        """
        # Get relevant tasks
        if label:
            tasks = self.tasks.list(label=label)
        else:
            tasks = self.tasks.all()

        if since:
            since_dt = datetime.fromisoformat(since)
            tasks = [t for t in tasks if datetime.fromisoformat(t.created_at) >= since_dt]

        if not tasks:
            return []

        patterns = []

        # Pattern: Label frequency
        label_counts: dict[str, list[str]] = {}
        for task in tasks:
            for lbl in task.labels:
                if lbl not in label_counts:
                    label_counts[lbl] = []
                label_counts[lbl].append(task.id)

        for lbl, task_ids in label_counts.items():
            if len(task_ids) >= 2:
                patterns.append(Pattern(
                    description=f"Label '{lbl}' appears in {len(task_ids)} tasks",
                    evidence=task_ids,
                    confidence=min(len(task_ids) / len(tasks), 1.0),
                ))

        # Pattern: Status distribution
        status_counts: dict[str, int] = {}
        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1

        closed = status_counts.get("closed", 0)
        total = len(tasks)
        if total > 0:
            completion_rate = closed / total
            patterns.append(Pattern(
                description=f"Completion rate: {closed}/{total} ({completion_rate:.0%})",
                evidence=[t.id for t in tasks if t.status == "closed"],
                confidence=0.9,
            ))

        return patterns

    def connections(self, task_id: str) -> List[Connection]:
        """Find connections for a task.

        Connections include:
        - Direct dependencies (blocks/blocked_by)
        - Same parent (siblings)
        - Related decisions
        - Shared labels
        """
        task = self.tasks.get(task_id)
        if not task:
            return []

        connections = []

        # Connection: Dependencies
        for blocks_id in task.blocks:
            connections.append(Connection(
                source_id=task_id,
                target_id=blocks_id,
                relationship="blocks",
                strength=1.0,
            ))

        for blocked_by_id in task.blocked_by:
            connections.append(Connection(
                source_id=task_id,
                target_id=blocked_by_id,
                relationship="blocked_by",
                strength=1.0,
            ))

        # Connection: Siblings (same parent)
        if task.parent_id:
            siblings = self.tasks.children(task.parent_id)
            for sibling in siblings:
                if sibling.id != task_id:
                    connections.append(Connection(
                        source_id=task_id,
                        target_id=sibling.id,
                        relationship="sibling",
                        strength=0.7,
                    ))

        # Connection: Related decisions
        decisions = self.decisions.for_task(task_id)
        for decision in decisions:
            connections.append(Connection(
                source_id=task_id,
                target_id=decision.id,
                relationship="has_decision",
                strength=0.9,
            ))

        # Connection: Shared labels
        for other_task in self.tasks.all():
            if other_task.id == task_id:
                continue
            shared_labels = set(task.labels) & set(other_task.labels)
            if shared_labels:
                connections.append(Connection(
                    source_id=task_id,
                    target_id=other_task.id,
                    relationship=f"shares_labels:{','.join(shared_labels)}",
                    strength=len(shared_labels) / max(len(task.labels), 1),
                ))

        return connections

    def decay(self, older_than_days: int = 30) -> DecaySummary:
        """Archive old closed tasks and extract insights.

        This is a simplified implementation that:
        - Finds closed tasks older than threshold
        - Archives them (changes status)
        - Returns summary

        For full synthesis with insight extraction, integrate with Claude API.
        """
        threshold = datetime.now() - timedelta(days=older_than_days)
        to_archive = []

        for task in self.tasks.all():
            if task.status != "closed":
                continue
            task_dt = datetime.fromisoformat(task.updated_at)
            if task_dt < threshold:
                to_archive.append(task)

        # Archive tasks
        archived_ids = []
        for task in to_archive:
            self.tasks.archive(task.id)
            archived_ids.append(task.id)

        # Generate basic insights (for full synthesis, use LLM)
        insights = []
        if to_archive:
            # Collect labels from archived tasks
            all_labels = []
            for task in to_archive:
                all_labels.extend(task.labels)
            if all_labels:
                label_summary = ", ".join(set(all_labels))
                insights.append(f"Archived work covered: {label_summary}")

            # Note completion
            insights.append(f"Archived {len(to_archive)} completed tasks")

        return DecaySummary(
            archived_count=len(archived_ids),
            insights=insights,
            task_ids=archived_ids,
        )

    def summary(self) -> dict:
        """Generate overall summary of memory state."""
        tasks = self.tasks.all()
        decisions = self.decisions.all()

        status_counts = {}
        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1

        phase_counts = {}
        for decision in decisions:
            phase_counts[decision.phase] = phase_counts.get(decision.phase, 0) + 1

        return {
            "tasks": {
                "total": len(tasks),
                "by_status": status_counts,
            },
            "decisions": {
                "total": len(decisions),
                "by_phase": phase_counts,
            },
        }
