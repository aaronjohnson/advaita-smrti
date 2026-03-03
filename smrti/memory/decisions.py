"""Decision operations for the memory layer.

Inspired by quint: structured reasoning trails with hypothesis tracking.
"""

from datetime import datetime
from typing import List, Optional, Sequence

from .models import Decision, Hypothesis
from .storage import IndexDb, JsonlStore
from .tasks import generate_id


class DecisionStore:
    """Decision storage and operations."""

    def __init__(self, jsonl: JsonlStore, index: IndexDb, prefix: str = "qt"):
        self.jsonl = jsonl
        self.index = index
        self.prefix = prefix
        self._cache: dict[str, Decision] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load all decisions into memory cache."""
        self._cache = {}
        for record in self.jsonl.iterate():
            decision = Decision.from_dict(record)
            self._cache[decision.id] = decision

    def _save(self, decision: Decision) -> None:
        """Save decision to storage and index."""
        self.jsonl.append(decision.to_dict())
        self.index.index_decision(decision.to_dict())
        self._cache[decision.id] = decision

    def begin(self, context: str, task_id: Optional[str] = None) -> Decision:
        """Start a new decision process."""
        decision = Decision(
            id=generate_id(self.prefix),
            context=context,
            task_id=task_id,
            phase="abduction",
        )
        self._save(decision)
        return decision

    def get(self, decision_id: str) -> Optional[Decision]:
        """Retrieve a decision by ID."""
        return self._cache.get(decision_id)

    def hypothesize(
        self,
        decision_id: str,
        description: str,
        rationale: str = "",
        confidence: float = 0.5,
    ) -> Optional[Decision]:
        """Add a hypothesis to a decision."""
        decision = self.get(decision_id)
        if not decision:
            return None

        # Generate hypothesis ID (h1, h2, h3, ...)
        hypo_num = len(decision.hypotheses) + 1
        hypothesis = Hypothesis(
            id=f"h{hypo_num}",
            description=description,
            rationale=rationale,
            confidence=confidence,
        )
        decision.hypotheses.append(hypothesis)
        self._save(decision)
        return decision

    def verify(self, decision_id: str) -> Optional[Decision]:
        """Move decision to deduction phase."""
        decision = self.get(decision_id)
        if not decision:
            return None
        decision.phase = "deduction"
        self._save(decision)
        return decision

    def test(self, decision_id: str) -> Optional[Decision]:
        """Move decision to induction phase."""
        decision = self.get(decision_id)
        if not decision:
            return None
        decision.phase = "induction"
        self._save(decision)
        return decision

    def decide(
        self,
        decision_id: str,
        hypothesis_id: str,
        rationale: str = "",
    ) -> Optional[Decision]:
        """Select a hypothesis and close the decision."""
        decision = self.get(decision_id)
        if not decision:
            return None

        # Verify hypothesis exists
        hypo_ids = [h.id for h in decision.hypotheses]
        if hypothesis_id not in hypo_ids:
            return None

        decision.selected = hypothesis_id
        decision.selection_rationale = rationale
        decision.phase = "decided"
        decision.decided_at = datetime.now().isoformat()
        self._save(decision)
        return decision

    def record(
        self,
        context: str,
        selected: str,
        alternatives: Sequence[str] = (),
        rationale: str = "",
        task_id: Optional[str] = None,
    ) -> Decision:
        """Record a decision that has already been made.

        Convenience method for capturing decisions after the fact.
        Internally calls begin/hypothesize/decide but presents a
        single semantic action.

        Args:
            context: What was being decided.
            selected: The chosen option (description text).
            alternatives: Other options that were considered.
            rationale: Why this option was chosen.
            task_id: Optional related task ID.

        Returns:
            The completed Decision with phase="decided".
        """
        decision = self.begin(context, task_id=task_id)

        # Add the selected option first (h1)
        self.hypothesize(decision.id, selected, confidence=1.0)

        # Add alternatives
        for alt in alternatives:
            self.hypothesize(decision.id, alt)

        # Select h1 (the chosen option)
        self.decide(decision.id, "h1", rationale=rationale)

        return self.get(decision.id)

    def list(
        self,
        task_id: Optional[str] = None,
        phase: Optional[str] = None,
    ) -> List[Decision]:
        """Query decisions matching criteria."""
        decision_ids = self.index.query_decisions(task_id=task_id, phase=phase)
        return [self._cache[did] for did in decision_ids if did in self._cache]

    def for_task(self, task_id: str) -> List[Decision]:
        """Get all decisions related to a task."""
        return self.list(task_id=task_id)

    def all(self) -> List[Decision]:
        """Return all decisions."""
        return list(self._cache.values())

    def compact(self) -> None:
        """Compact JSONL file to remove old versions."""
        self.jsonl.rewrite([d.to_dict() for d in self._cache.values()])
