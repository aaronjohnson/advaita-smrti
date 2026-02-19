"""Tests for dependency graph wiring and coherence checks.

Tests P1 (dependency graph activation) and P3 (coherence checks)
from RFC 003.
"""

import json
import os
import shutil
import tempfile
import unittest

from memory import Memory, CoherenceFinding, CoherenceReport
from sea_application_helper import SEAApplicationHelper


class TestDependencyWiring(unittest.TestCase):
    """Test P1: Wire config depends_on into memory layer blocks/blocked_by."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "test_config.json")
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.memory_path = os.path.join(self.tmpdir, ".memory")

        # Config with dependencies
        config = {
            "form_name": "Test Form",
            "sections": [
                {"id": 1, "name": "basics", "title": "Basics", "description": "Basic questions"},
                {"id": 2, "name": "details", "title": "Details", "description": "Detailed questions"},
            ],
            "questions": [
                {"id": "1", "section_id": 1, "question_text": "What is A?", "priority": 1},
                {"id": "2", "section_id": 1, "question_text": "What is B?", "priority": 1, "depends_on": "1"},
                {"id": "3", "section_id": 2, "question_text": "What is C?", "priority": 1, "depends_on": "1"},
                {"id": "4", "section_id": 2, "question_text": "What is D?", "priority": 2, "depends_on": "3"},
            ],
        }
        with open(self.config_path, "w") as f:
            json.dump(config, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _make_helper(self):
        helper = SEAApplicationHelper(
            db_path=self.db_path,
            config_path=self.config_path,
            memory_path=self.memory_path,
        )
        helper.populate_questions()
        # Create memory tasks for each question
        for q in helper.config.get("questions", []):
            helper.save_answer(q["id"], "", status="not_started")
        return helper

    def test_wire_dependencies_creates_block_relationships(self):
        """wire_dependencies should create blocks/blocked_by links."""
        helper = self._make_helper()
        helper.wire_dependencies()

        # Find the tasks
        qid_to_task = {}
        for t in helper.memory.tasks.all():
            qid = t.metadata.get("question_id")
            if qid:
                qid_to_task[qid] = t

        # Q2 depends on Q1, so Q1 should block Q2
        self.assertIn(qid_to_task["2"].id, qid_to_task["1"].blocks)
        self.assertIn(qid_to_task["1"].id, qid_to_task["2"].blocked_by)

        # Q3 depends on Q1
        self.assertIn(qid_to_task["3"].id, qid_to_task["1"].blocks)

        # Q4 depends on Q3
        self.assertIn(qid_to_task["4"].id, qid_to_task["3"].blocks)

        helper.close()

    def test_wire_dependencies_stores_depends_on_metadata(self):
        """wire_dependencies should store depends_on in task metadata."""
        helper = self._make_helper()
        helper.wire_dependencies()

        for t in helper.memory.tasks.all():
            qid = t.metadata.get("question_id")
            if qid == "2":
                self.assertEqual(t.metadata.get("depends_on"), "1")
            elif qid == "4":
                self.assertEqual(t.metadata.get("depends_on"), "3")

        helper.close()

    def test_wire_dependencies_idempotent(self):
        """Calling wire_dependencies twice should not duplicate relationships."""
        helper = self._make_helper()
        helper.wire_dependencies()
        helper.wire_dependencies()  # Second call

        qid_to_task = {}
        for t in helper.memory.tasks.all():
            qid = t.metadata.get("question_id")
            if qid:
                qid_to_task[qid] = t

        # Should still have exactly one block relationship, not two
        block_count = qid_to_task["1"].blocks.count(qid_to_task["2"].id)
        self.assertEqual(block_count, 1)

        helper.close()

    def test_ready_tasks_respects_dependencies(self):
        """Tasks with open blockers should not appear in ready()."""
        helper = self._make_helper()
        helper.wire_dependencies()

        ready = helper.memory.tasks.ready()
        ready_qids = {t.metadata.get("question_id") for t in ready}

        # Q1 has no dependencies, should be ready
        self.assertIn("1", ready_qids)

        # Q2 depends on Q1 (open), should NOT be ready
        self.assertNotIn("2", ready_qids)

        # Q4 depends on Q3 (open), should NOT be ready
        self.assertNotIn("4", ready_qids)

        helper.close()

    def test_closing_dependency_unblocks_downstream(self):
        """Closing a blocker should make downstream tasks ready."""
        helper = self._make_helper()
        helper.wire_dependencies()

        # Close Q1
        qid_to_task = {}
        for t in helper.memory.tasks.all():
            qid = t.metadata.get("question_id")
            if qid:
                qid_to_task[qid] = t

        helper.memory.tasks.close(qid_to_task["1"].id)

        ready = helper.memory.tasks.ready()
        ready_qids = {t.metadata.get("question_id") for t in ready}

        # Q2 depends on Q1 (now closed), should be ready
        self.assertIn("2", ready_qids)

        # Q3 depends on Q1 (now closed), should be ready
        self.assertIn("3", ready_qids)

        # Q4 depends on Q3 (still open), should NOT be ready
        self.assertNotIn("4", ready_qids)

        helper.close()


class TestCoherenceCheck(unittest.TestCase):
    """Test P3: Coherence checks across tasks."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.tmpdir, ".memory")
        self.memory = Memory(self.memory_path, prefix="tc")

    def tearDown(self):
        self.memory.close()
        shutil.rmtree(self.tmpdir)

    def test_empty_coherence_check(self):
        """Coherence check on empty memory should return empty report."""
        report = self.memory.synthesize.coherence_check()
        self.assertEqual(report.tasks_checked, 0)
        self.assertEqual(len(report.findings), 0)

    def test_dependency_violation_detected(self):
        """Should detect when a task is answered but its dependency is not."""
        # Create two tasks: t2 depends on t1
        t1 = self.memory.tasks.create(
            "Q1", description="Answer A", status="open",
            metadata={"question_id": "1"},
        )
        t2 = self.memory.tasks.create(
            "Q2", description="Answer B", status="closed",
            metadata={"question_id": "2", "depends_on": "1"},
        )
        self.memory.tasks.block(t1.id, t2.id)

        report = self.memory.synthesize.coherence_check()

        # Should find the dependency violation
        dep_findings = [f for f in report.findings if f.category == "dependency"]
        self.assertTrue(len(dep_findings) > 0)
        self.assertTrue(any("depends on" in f.message.lower() or
                           "unanswered" in f.message.lower()
                           for f in dep_findings))

    def test_no_finding_when_dependency_satisfied(self):
        """Should NOT flag when dependency is properly satisfied."""
        t1 = self.memory.tasks.create(
            "Q1", description="Answer A", status="closed",
            metadata={"question_id": "1"},
        )
        t2 = self.memory.tasks.create(
            "Q2", description="Answer B", status="closed",
            metadata={"question_id": "2", "depends_on": "1"},
        )
        self.memory.tasks.block(t1.id, t2.id)

        report = self.memory.synthesize.coherence_check()

        # Should NOT find dependency violations
        dep_errors = [f for f in report.findings
                      if f.category == "dependency" and f.severity in ("error", "warning")]
        self.assertEqual(len(dep_errors), 0)

    def test_section_filter(self):
        """Should only check tasks in the specified section."""
        self.memory.tasks.create(
            "Q1", status="open",
            metadata={"question_id": "1", "section": "Basics"},
        )
        self.memory.tasks.create(
            "Q2", status="open",
            metadata={"question_id": "2", "section": "Details"},
        )

        report = self.memory.synthesize.coherence_check(section="Basics")
        self.assertEqual(report.tasks_checked, 1)
        self.assertEqual(report.section, "Basics")

    def test_cross_reference_detection(self):
        """Should detect shared terms between answered tasks."""
        self.memory.tasks.create(
            "Q1", status="closed",
            description="The CACFP funding requires quarterly meal tracking and daily counts for compliance reporting",
            metadata={"question_id": "1", "section": "Reporting"},
        )
        self.memory.tasks.create(
            "Q2", status="closed",
            description="Meals are tracked for CACFP compliance with quarterly reporting to the funding agency",
            metadata={"question_id": "2", "section": "Reporting"},
        )

        report = self.memory.synthesize.coherence_check(section="Reporting")
        xref_findings = [f for f in report.findings if f.category == "cross_reference"]
        self.assertTrue(len(xref_findings) > 0)

    def test_completeness_info(self):
        """Should report section completeness."""
        self.memory.tasks.create(
            "Q1", status="closed",
            metadata={"question_id": "1", "section": "Basics"},
        )
        self.memory.tasks.create(
            "Q2", status="open",
            metadata={"question_id": "2", "section": "Basics"},
        )

        report = self.memory.synthesize.coherence_check(section="Basics")
        completeness = [f for f in report.findings if f.category == "completeness"]
        self.assertTrue(len(completeness) > 0)
        self.assertIn("1 complete", completeness[0].message)

    def test_coherence_report_properties(self):
        """CoherenceReport properties should work correctly."""
        report = CoherenceReport(section="test")
        self.assertFalse(report.has_errors)
        self.assertFalse(report.has_warnings)

        report.findings.append(CoherenceFinding(
            severity="warning", category="dependency",
            message="test warning",
        ))
        self.assertFalse(report.has_errors)
        self.assertTrue(report.has_warnings)

        report.findings.append(CoherenceFinding(
            severity="error", category="dependency",
            message="test error",
        ))
        self.assertTrue(report.has_errors)


class TestCoherenceWithHelper(unittest.TestCase):
    """Integration test: coherence check through SEAApplicationHelper."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "test_config.json")
        self.db_path = os.path.join(self.tmpdir, "test.db")
        self.memory_path = os.path.join(self.tmpdir, ".memory")

        config = {
            "form_name": "Test Form",
            "sections": [
                {"id": 1, "name": "basics", "title": "Basics"},
            ],
            "questions": [
                {"id": "1", "section_id": 1, "question_text": "Q1?", "priority": 1},
                {"id": "2", "section_id": 1, "question_text": "Q2?", "priority": 1, "depends_on": "1"},
            ],
        }
        with open(self.config_path, "w") as f:
            json.dump(config, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_full_workflow(self):
        """Test: populate, wire deps, answer out of order, check coherence."""
        helper = SEAApplicationHelper(
            db_path=self.db_path,
            config_path=self.config_path,
            memory_path=self.memory_path,
        )
        helper.populate_questions()

        # Create initial tasks
        helper.save_answer("1", "", status="not_started")
        helper.save_answer("2", "", status="not_started")

        # Wire dependencies
        helper.wire_dependencies()

        # Answer Q2 before Q1 (out of order)
        helper.save_answer("2", "Answer to Q2", status="complete")

        # Run coherence check
        report = helper.coherence_check(section="Basics")
        self.assertIsNotNone(report)

        # Should detect that Q2 is complete but Q1 (dependency) is not
        dep_findings = [f for f in report.findings if f.category == "dependency"]
        self.assertTrue(len(dep_findings) > 0)

        helper.close()


if __name__ == "__main__":
    unittest.main()
