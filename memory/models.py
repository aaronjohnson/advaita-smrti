"""Data models for the memory layer.

Based on RFC 002: Memory Layer Specification.
Inspired by beads (task graphs) and quint (decision trails).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    """A unit of work with identity, status, and relationships."""

    id: str
    title: str
    description: str = ""
    status: str = "open"  # open, in_progress, closed, archived
    parent_id: Optional[str] = None
    blocks: List[str] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "parent_id": self.parent_id,
            "blocks": self.blocks,
            "blocked_by": self.blocked_by,
            "labels": self.labels,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "open"),
            parent_id=data.get("parent_id"),
            blocks=data.get("blocks", []),
            blocked_by=data.get("blocked_by", []),
            labels=data.get("labels", []),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Hypothesis:
    """A candidate approach being considered in a decision."""

    id: str  # h1, h2, h3
    description: str
    rationale: str = ""
    confidence: float = 0.5  # 0.0 - 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "rationale": self.rationale,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hypothesis":
        return cls(
            id=data["id"],
            description=data["description"],
            rationale=data.get("rationale", ""),
            confidence=data.get("confidence", 0.5),
        )


@dataclass
class Decision:
    """A recorded reasoning process for non-trivial choices."""

    id: str
    context: str  # What we're deciding
    task_id: Optional[str] = None
    hypotheses: List[Hypothesis] = field(default_factory=list)
    selected: Optional[str] = None  # Chosen hypothesis ID
    selection_rationale: str = ""
    phase: str = "abduction"  # abduction, deduction, induction, decided
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    decided_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "context": self.context,
            "task_id": self.task_id,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "selected": self.selected,
            "selection_rationale": self.selection_rationale,
            "phase": self.phase,
            "created_at": self.created_at,
            "decided_at": self.decided_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Decision":
        return cls(
            id=data["id"],
            context=data["context"],
            task_id=data.get("task_id"),
            hypotheses=[Hypothesis.from_dict(h) for h in data.get("hypotheses", [])],
            selected=data.get("selected"),
            selection_rationale=data.get("selection_rationale", ""),
            phase=data.get("phase", "abduction"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            decided_at=data.get("decided_at"),
        )


@dataclass
class Pattern:
    """A detected pattern from synthesis."""

    description: str
    evidence: List[str] = field(default_factory=list)  # Task/decision IDs
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }


@dataclass
class Connection:
    """A discovered connection between items."""

    source_id: str
    target_id: str
    relationship: str
    strength: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship": self.relationship,
            "strength": self.strength,
        }


@dataclass
class DecaySummary:
    """Summary of decayed/archived items."""

    archived_count: int
    insights: List[str] = field(default_factory=list)
    task_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "archived_count": self.archived_count,
            "insights": self.insights,
            "task_ids": self.task_ids,
        }


@dataclass
class CoherenceFinding:
    """A single finding from a coherence check."""

    severity: str  # "error", "warning", "info"
    category: str  # "dependency", "gap", "cross_reference"
    message: str
    task_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "task_ids": self.task_ids,
        }


@dataclass
class CoherenceReport:
    """Results of a coherence check across a set of tasks."""

    section: str  # Section name or "all"
    findings: List[CoherenceFinding] = field(default_factory=list)
    tasks_checked: int = 0
    tasks_complete: int = 0
    tasks_with_dependencies: int = 0
    unresolved_dependencies: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section": self.section,
            "findings": [f.to_dict() for f in self.findings],
            "tasks_checked": self.tasks_checked,
            "tasks_complete": self.tasks_complete,
            "tasks_with_dependencies": self.tasks_with_dependencies,
            "unresolved_dependencies": self.unresolved_dependencies,
        }

    @property
    def has_errors(self) -> bool:
        return any(f.severity == "error" for f in self.findings)

    @property
    def has_warnings(self) -> bool:
        return any(f.severity == "warning" for f in self.findings)
