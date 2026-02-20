"""Synthesis operations for the memory layer.

Extracts insights from accumulated tasks and decisions.
Pattern detection, cross-references, and context decay.

Note: Full synthesis requires LLM integration.
This module provides the structure; LLM calls can be added later.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from .models import Connection, CoherenceFinding, CoherenceReport, DecaySummary, Pattern, Task, Decision
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

    def coherence_check(
        self,
        section: Optional[str] = None,
        question_tasks_only: bool = True,
    ) -> CoherenceReport:
        """Check coherence across tasks in a section or globally.

        Structural checks (no LLM required):
        - Dependency violations: task answered but its dependency is not
        - Gap detection: open tasks that block answered tasks
        - Status inconsistency: closed task with open dependencies
        - Orphan detection: tasks with missing dependency targets
        - Section completeness: how complete is the section

        Args:
            section: Section label to filter (e.g., "section:Data and Reporting").
                     If None, checks all tasks.
            question_tasks_only: If True, only check tasks with question_id metadata.
        """
        # Gather relevant tasks
        all_tasks = self.tasks.all()

        if question_tasks_only:
            all_tasks = [t for t in all_tasks if t.metadata.get('question_id')]

        if section:
            tasks = [t for t in all_tasks if
                     f"section:{section}" in t.labels or
                     t.metadata.get('section') == section]
        else:
            tasks = all_tasks

        report = CoherenceReport(
            section=section or "all",
            tasks_checked=len(tasks),
            tasks_complete=sum(1 for t in tasks if t.status == "closed"),
        )

        if not tasks:
            return report

        # Build lookup: question_id -> task
        qid_to_task = {}
        for t in all_tasks:
            qid = t.metadata.get('question_id')
            if qid:
                qid_to_task[qid] = t

        # Check 1: Dependency violations
        # A task is answered (closed/in_progress) but its blocked_by tasks are still open
        for task in tasks:
            if task.status in ("closed", "in_progress") and task.blocked_by:
                for blocker_id in task.blocked_by:
                    blocker = self.tasks.get(blocker_id)
                    if blocker and blocker.status == "open":
                        report.findings.append(CoherenceFinding(
                            severity="warning",
                            category="dependency",
                            message=f"Task '{task.title}' is {task.status} but depends on "
                                    f"'{blocker.title}' which is still open",
                            task_ids=[task.id, blocker_id],
                        ))
                        report.unresolved_dependencies += 1

        # Check 2: Gap detection using config depends_on metadata
        # If a task has a config-level depends_on, check if that dependency is answered
        for task in tasks:
            depends_on_qid = task.metadata.get('depends_on')
            if not depends_on_qid:
                continue

            report.tasks_with_dependencies += 1
            dep_task = qid_to_task.get(depends_on_qid)

            if not dep_task:
                report.findings.append(CoherenceFinding(
                    severity="error",
                    category="dependency",
                    message=f"Task '{task.title}' depends on question {depends_on_qid} "
                            f"which has no corresponding task",
                    task_ids=[task.id],
                ))
            elif task.status == "closed" and dep_task.status == "open":
                report.findings.append(CoherenceFinding(
                    severity="warning",
                    category="dependency",
                    message=f"Q{task.metadata.get('question_id')} is complete but "
                            f"depends on Q{depends_on_qid} which is unanswered",
                    task_ids=[task.id, dep_task.id],
                ))
            elif task.status in ("closed", "in_progress") and dep_task.status == "open":
                report.findings.append(CoherenceFinding(
                    severity="info",
                    category="gap",
                    message=f"Q{task.metadata.get('question_id')} has work but "
                            f"its dependency Q{depends_on_qid} is unanswered — "
                            f"revisit after completing Q{depends_on_qid}",
                    task_ids=[task.id, dep_task.id],
                ))

        # Check 3: Section completeness
        if section:
            total = len(tasks)
            closed = sum(1 for t in tasks if t.status == "closed")
            in_progress = sum(1 for t in tasks if t.status == "in_progress")
            open_count = sum(1 for t in tasks if t.status == "open")

            if closed == total and total > 0:
                report.findings.append(CoherenceFinding(
                    severity="info",
                    category="completeness",
                    message=f"Section '{section}' is complete ({total}/{total})",
                    task_ids=[t.id for t in tasks],
                ))
            elif open_count > 0:
                open_qids = [t.metadata.get('question_id', '?') for t in tasks if t.status == "open"]
                report.findings.append(CoherenceFinding(
                    severity="info",
                    category="completeness",
                    message=f"Section '{section}': {closed} complete, {in_progress} in progress, "
                            f"{open_count} not started (Q{', Q'.join(open_qids)})",
                    task_ids=[t.id for t in tasks if t.status == "open"],
                ))

        # Check 4: Cross-reference opportunities
        # Find tasks in the same section that reference the same terms
        # (simple keyword overlap in descriptions)
        answered_tasks = [t for t in tasks if t.status in ("closed", "in_progress")
                          and t.description and len(t.description) > 50]
        if len(answered_tasks) >= 2:
            for i, t1 in enumerate(answered_tasks):
                for t2 in answered_tasks[i + 1:]:
                    shared = self._find_shared_terms(t1.description, t2.description)
                    if shared:
                        q1 = t1.metadata.get('question_id', '?')
                        q2 = t2.metadata.get('question_id', '?')
                        report.findings.append(CoherenceFinding(
                            severity="info",
                            category="cross_reference",
                            message=f"Q{q1} and Q{q2} both reference: {', '.join(shared[:5])}. "
                                    f"Verify consistency.",
                            task_ids=[t1.id, t2.id],
                        ))

        return report

    def _find_shared_terms(self, text1: str, text2: str, min_length: int = 5) -> list:
        """Find significant shared terms between two texts."""
        stop_words = {
            'about', 'after', 'again', 'being', 'between', 'could', 'daily',
            'does', 'during', 'each', 'first', 'from', 'have', 'their',
            'them', 'then', 'there', 'these', 'they', 'this', 'through',
            'what', 'when', 'where', 'which', 'while', 'will', 'with',
            'would', 'answer', 'question', 'helper', 'status', 'should',
        }
        words1 = {w.lower().strip('.,;:()[]"\'') for w in text1.split()
                   if len(w) >= min_length}
        words2 = {w.lower().strip('.,;:()[]"\'') for w in text2.split()
                   if len(w) >= min_length}
        shared = (words1 & words2) - stop_words
        return sorted(shared)[:10]

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
