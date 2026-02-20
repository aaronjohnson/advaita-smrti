"""Fact operations for the memory layer — the semantic store.

Stores stable facts, preferences, and constraints extracted
from conversations, site visits, and documents.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import Fact
from .storage import IndexDb, JsonlStore
from .tasks import generate_id


class FactStore:
    """Fact storage and operations."""

    def __init__(self, jsonl: JsonlStore, index: IndexDb, prefix: str = "sm"):
        self.jsonl = jsonl
        self.index = index
        self.prefix = prefix
        self._cache: Dict[str, Fact] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load all facts into memory cache."""
        self._cache = {}
        for record in self.jsonl.iterate():
            fact = Fact.from_dict(record)
            self._cache[fact.id] = fact

    def create(
        self,
        fact: str,
        source: str = "",
        section: str = "",
        confidence: float = 1.0,
        labels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Fact:
        """Create a new fact."""
        f = Fact(
            id=generate_id(f"{self.prefix}-f"),
            fact=fact,
            source=source,
            section=section,
            confidence=confidence,
            labels=labels or [],
            metadata=metadata or {},
        )
        self._save(f)
        return f

    def _save(self, fact: Fact) -> None:
        """Save fact to storage and index."""
        fact.updated_at = datetime.now().isoformat()
        self.jsonl.append(fact.to_dict())
        self.index.index_fact(fact.to_dict())
        self._cache[fact.id] = fact

    def get(self, fact_id: str) -> Optional[Fact]:
        """Retrieve a fact by ID."""
        return self._cache.get(fact_id)

    def update(self, fact_id: str, **fields) -> Optional[Fact]:
        """Update fact fields.

        If 'fact' text is changed, creates a supersedes chain.
        """
        existing = self.get(fact_id)
        if not existing:
            return None

        # If the fact text itself is changing, create a new version
        if "fact" in fields and fields["fact"] != existing.fact:
            new_fact = self.create(
                fact=fields.pop("fact"),
                source=fields.pop("source", existing.source),
                section=fields.pop("section", existing.section),
                confidence=fields.pop("confidence", existing.confidence),
                labels=fields.pop("labels", existing.labels[:]),
                metadata=fields.pop("metadata", dict(existing.metadata)),
            )
            new_fact.supersedes = fact_id
            self._save(new_fact)
            return new_fact

        # Otherwise update in place
        for key, value in fields.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        self._save(existing)
        return existing

    def all(self) -> List[Fact]:
        """Return all current facts (excluding superseded)."""
        superseded_ids = {f.supersedes for f in self._cache.values() if f.supersedes}
        return [f for f in self._cache.values() if f.id not in superseded_ids]

    def all_including_superseded(self) -> List[Fact]:
        """Return all facts including superseded versions."""
        return list(self._cache.values())

    def by_section(self, section: str) -> List[Fact]:
        """Query facts by section."""
        superseded_ids = {f.supersedes for f in self._cache.values() if f.supersedes}
        return [
            f for f in self._cache.values()
            if f.section == section and f.id not in superseded_ids
        ]

    def by_label(self, label: str) -> List[Fact]:
        """Query facts by label."""
        superseded_ids = {f.supersedes for f in self._cache.values() if f.supersedes}
        return [
            f for f in self._cache.values()
            if label in f.labels and f.id not in superseded_ids
        ]

    def search(self, term: str) -> List[Fact]:
        """Substring search across fact text."""
        term_lower = term.lower()
        superseded_ids = {f.supersedes for f in self._cache.values() if f.supersedes}
        return [
            f for f in self._cache.values()
            if term_lower in f.fact.lower() and f.id not in superseded_ids
        ]

    def compact(self) -> None:
        """Compact JSONL file to remove old versions."""
        self.jsonl.rewrite([f.to_dict() for f in self._cache.values()])
