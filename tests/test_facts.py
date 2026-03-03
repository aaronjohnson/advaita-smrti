#!/usr/bin/env python3
"""Tests for the semantic (facts) memory store."""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from smrti import Memory, Fact


class TestFactOperations(unittest.TestCase):
    """Test fact CRUD operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, ".memory")
        self.mem = Memory(self.memory_path)

    def tearDown(self):
        self.mem.close()
        shutil.rmtree(self.temp_dir)

    def test_create_fact(self):
        """Can create a fact."""
        fact = self.mem.facts.create("Applicant has 10 years experience")
        self.assertIsNotNone(fact.id)
        self.assertTrue(fact.id.startswith("sm-f"))
        self.assertEqual(fact.fact, "Applicant has 10 years experience")
        self.assertEqual(fact.confidence, 1.0)

    def test_create_fact_with_source(self):
        """Can create a fact with source attribution."""
        fact = self.mem.facts.create(
            "Business registered in Oregon",
            source="SEA application Q3",
        )
        self.assertEqual(fact.source, "SEA application Q3")

    def test_create_fact_with_section(self):
        """Can create a fact with section grouping."""
        fact = self.mem.facts.create(
            "Primary skill is web development",
            section="skills",
        )
        self.assertEqual(fact.section, "skills")

    def test_create_fact_with_labels(self):
        """Can create a fact with labels."""
        fact = self.mem.facts.create(
            "Prefers remote work",
            labels=["preference", "work-style"],
        )
        self.assertIn("preference", fact.labels)
        self.assertIn("work-style", fact.labels)

    def test_create_fact_with_confidence(self):
        """Can create a fact with custom confidence."""
        fact = self.mem.facts.create(
            "Might qualify for veteran benefits",
            confidence=0.6,
        )
        self.assertEqual(fact.confidence, 0.6)

    def test_create_fact_with_metadata(self):
        """Can create a fact with metadata."""
        fact = self.mem.facts.create(
            "Annual revenue target is $50k",
            metadata={"question_id": "q4"},
        )
        self.assertEqual(fact.metadata["question_id"], "q4")

    def test_get_fact(self):
        """Can retrieve a fact by ID."""
        fact = self.mem.facts.create("Test fact")
        retrieved = self.mem.facts.get(fact.id)
        self.assertEqual(retrieved.id, fact.id)
        self.assertEqual(retrieved.fact, "Test fact")

    def test_get_nonexistent_fact(self):
        """Getting nonexistent fact returns None."""
        result = self.mem.facts.get("nonexistent-id")
        self.assertIsNone(result)

    def test_update_metadata(self):
        """Can update non-text fields in place."""
        fact = self.mem.facts.create("Original fact", confidence=0.5)
        updated = self.mem.facts.update(fact.id, confidence=0.9)
        self.assertEqual(updated.id, fact.id)
        self.assertEqual(updated.confidence, 0.9)
        self.assertEqual(updated.fact, "Original fact")

    def test_update_text_creates_supersedes(self):
        """Changing fact text creates a new fact that supersedes the old."""
        original = self.mem.facts.create("Revenue is $30k/year")
        updated = self.mem.facts.update(original.id, fact="Revenue is $50k/year")

        # New fact should have different ID
        self.assertNotEqual(updated.id, original.id)
        self.assertEqual(updated.fact, "Revenue is $50k/year")
        self.assertEqual(updated.supersedes, original.id)

    def test_all_excludes_superseded(self):
        """all() excludes superseded facts."""
        f1 = self.mem.facts.create("Version 1")
        f2 = self.mem.facts.update(f1.id, fact="Version 2")

        all_facts = self.mem.facts.all()
        all_ids = [f.id for f in all_facts]
        self.assertIn(f2.id, all_ids)
        self.assertNotIn(f1.id, all_ids)

    def test_all_including_superseded(self):
        """all_including_superseded() returns everything."""
        f1 = self.mem.facts.create("Version 1")
        f2 = self.mem.facts.update(f1.id, fact="Version 2")

        all_facts = self.mem.facts.all_including_superseded()
        all_ids = [f.id for f in all_facts]
        self.assertIn(f1.id, all_ids)
        self.assertIn(f2.id, all_ids)

    def test_list_all_facts(self):
        """Can list all current facts."""
        self.mem.facts.create("Fact 1")
        self.mem.facts.create("Fact 2")
        self.mem.facts.create("Fact 3")
        all_facts = self.mem.facts.all()
        self.assertEqual(len(all_facts), 3)


class TestFactQueries(unittest.TestCase):
    """Test fact querying operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, ".memory")
        self.mem = Memory(self.memory_path)
        # Seed facts
        self.mem.facts.create("Has business license", section="legal", labels=["requirement"])
        self.mem.facts.create("Oregon resident", section="background", labels=["requirement"])
        self.mem.facts.create("Prefers consulting", section="goals", labels=["preference"])
        self.mem.facts.create("Web dev experience", section="skills")

    def tearDown(self):
        self.mem.close()
        shutil.rmtree(self.temp_dir)

    def test_by_section(self):
        """Can query facts by section."""
        legal = self.mem.facts.by_section("legal")
        self.assertEqual(len(legal), 1)
        self.assertEqual(legal[0].fact, "Has business license")

    def test_by_label(self):
        """Can query facts by label."""
        reqs = self.mem.facts.by_label("requirement")
        self.assertEqual(len(reqs), 2)

    def test_search(self):
        """Can substring search across fact text."""
        results = self.mem.facts.search("experience")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].fact, "Web dev experience")

    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results = self.mem.facts.search("OREGON")
        self.assertEqual(len(results), 1)


class TestFactPersistence(unittest.TestCase):
    """Test that facts persist across Memory instances."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, ".memory")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_facts_persist(self):
        """Facts persist after closing and reopening."""
        mem1 = Memory(self.memory_path)
        fact = mem1.facts.create("Persistent fact", source="test")
        fact_id = fact.id
        mem1.close()

        mem2 = Memory(self.memory_path)
        retrieved = mem2.facts.get(fact_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.fact, "Persistent fact")
        self.assertEqual(retrieved.source, "test")
        mem2.close()

    def test_facts_survive_rebuild(self):
        """Facts survive index rebuild."""
        mem1 = Memory(self.memory_path)
        mem1.facts.create("Fact 1")
        mem1.facts.create("Fact 2")
        mem1.close()

        # Delete index
        index_path = os.path.join(self.memory_path, "index.db")
        os.remove(index_path)

        # Reopen and rebuild
        mem2 = Memory(self.memory_path, ignore_drift=True)
        mem2.rebuild_index()
        all_facts = mem2.facts.all()
        self.assertEqual(len(all_facts), 2)
        mem2.close()

    def test_facts_drift_detection(self):
        """Direct JSONL writes to facts.jsonl cause IndexDriftError."""
        from smrti import IndexDriftError

        mem1 = Memory(self.memory_path)
        mem1.facts.create("Fact via API")
        mem1.close()

        # Bypass API: append directly to JSONL
        jsonl_path = os.path.join(self.memory_path, "facts.jsonl")
        with open(jsonl_path, "a") as f:
            f.write(json.dumps({
                "id": "rogue-fact-001",
                "fact": "Written outside API",
                "source": "",
                "section": "",
                "confidence": 1.0,
                "labels": [],
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
            }) + "\n")

        with self.assertRaises(IndexDriftError):
            Memory(self.memory_path)

    def test_compact_facts(self):
        """Compact removes old JSONL versions of facts."""
        mem = Memory(self.memory_path)
        f1 = mem.facts.create("Version 1")
        mem.facts.update(f1.id, confidence=0.5)
        mem.facts.update(f1.id, confidence=0.9)

        # JSONL should have 3 lines (create + 2 updates)
        jsonl_path = os.path.join(self.memory_path, "facts.jsonl")
        with open(jsonl_path) as f:
            lines_before = len([l for l in f if l.strip()])
        self.assertEqual(lines_before, 3)

        mem.compact()

        # After compact, should have 1 line (latest version)
        with open(jsonl_path) as f:
            lines_after = len([l for l in f if l.strip()])
        self.assertEqual(lines_after, 1)
        mem.close()


class TestFactModel(unittest.TestCase):
    """Test the Fact dataclass itself."""

    def test_to_dict_roundtrip(self):
        """Fact can roundtrip through dict serialization."""
        fact = Fact(
            id="test-f001",
            fact="Test fact",
            source="unit test",
            section="test",
            confidence=0.8,
            labels=["test", "unit"],
            supersedes="test-f000",
        )
        d = fact.to_dict()
        restored = Fact.from_dict(d)
        self.assertEqual(restored.id, fact.id)
        self.assertEqual(restored.fact, fact.fact)
        self.assertEqual(restored.source, fact.source)
        self.assertEqual(restored.confidence, fact.confidence)
        self.assertEqual(restored.labels, fact.labels)
        self.assertEqual(restored.supersedes, fact.supersedes)

    def test_from_dict_defaults(self):
        """Fact.from_dict handles missing optional fields."""
        minimal = {"id": "test-f001", "fact": "Minimal fact"}
        fact = Fact.from_dict(minimal)
        self.assertEqual(fact.source, "")
        self.assertEqual(fact.section, "")
        self.assertEqual(fact.confidence, 1.0)
        self.assertEqual(fact.labels, [])
        self.assertIsNone(fact.supersedes)


if __name__ == "__main__":
    unittest.main()
