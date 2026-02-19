#!/usr/bin/env python3
"""Tests for the memory layer (beads/quint-inspired storage)."""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import Memory
from memory.models import Task, Decision, Hypothesis


class TestMemoryInitialization(unittest.TestCase):
    """Test Memory layer initialization."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, ".memory")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_creates_directory(self):
        """Memory creates .memory directory on init."""
        mem = Memory(self.memory_path)
        self.assertTrue(os.path.exists(self.memory_path))
        mem.close()

    def test_creates_config(self):
        """Memory creates config.json on init."""
        mem = Memory(self.memory_path)
        config_path = os.path.join(self.memory_path, "config.json")
        self.assertTrue(os.path.exists(config_path))
        mem.close()

    def test_custom_prefix(self):
        """Memory uses custom prefix for task IDs."""
        mem = Memory(self.memory_path, prefix="test")
        task = mem.tasks.create("Test task")
        self.assertTrue(task.id.startswith("test-"))
        mem.close()


class TestTaskOperations(unittest.TestCase):
    """Test task CRUD operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, ".memory")
        self.mem = Memory(self.memory_path)

    def tearDown(self):
        self.mem.close()
        shutil.rmtree(self.temp_dir)

    def test_create_task(self):
        """Can create a task."""
        task = self.mem.tasks.create("Test task", description="Test description")
        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, "Test task")
        self.assertEqual(task.description, "Test description")
        self.assertEqual(task.status, "open")

    def test_create_task_with_status(self):
        """Can create a task with specific status."""
        task = self.mem.tasks.create("Test", status="in_progress")
        self.assertEqual(task.status, "in_progress")

    def test_create_task_with_labels(self):
        """Can create a task with labels."""
        task = self.mem.tasks.create("Test", labels=["question", "priority:1"])
        self.assertIn("question", task.labels)
        self.assertIn("priority:1", task.labels)

    def test_create_task_with_metadata(self):
        """Can create a task with metadata."""
        task = self.mem.tasks.create("Test", metadata={"question_id": "q1"})
        self.assertEqual(task.metadata["question_id"], "q1")

    def test_get_task(self):
        """Can retrieve a task by ID."""
        task = self.mem.tasks.create("Test task")
        retrieved = self.mem.tasks.get(task.id)
        self.assertEqual(retrieved.id, task.id)
        self.assertEqual(retrieved.title, task.title)

    def test_get_nonexistent_task(self):
        """Getting nonexistent task returns None."""
        result = self.mem.tasks.get("nonexistent-id")
        self.assertIsNone(result)

    def test_update_task(self):
        """Can update task fields."""
        task = self.mem.tasks.create("Original title")
        self.mem.tasks.update(task.id, title="Updated title", status="in_progress")
        retrieved = self.mem.tasks.get(task.id)
        self.assertEqual(retrieved.title, "Updated title")
        self.assertEqual(retrieved.status, "in_progress")

    def test_close_task(self):
        """Can close a task."""
        task = self.mem.tasks.create("Test")
        self.mem.tasks.close(task.id)
        retrieved = self.mem.tasks.get(task.id)
        self.assertEqual(retrieved.status, "closed")

    def test_list_all_tasks(self):
        """Can list all tasks."""
        self.mem.tasks.create("Task 1")
        self.mem.tasks.create("Task 2")
        self.mem.tasks.create("Task 3")
        all_tasks = self.mem.tasks.all()
        self.assertEqual(len(all_tasks), 3)

    def test_list_tasks_by_status(self):
        """Can filter tasks by status."""
        self.mem.tasks.create("Open 1")
        self.mem.tasks.create("Open 2")
        task3 = self.mem.tasks.create("Closed")
        self.mem.tasks.close(task3.id)

        open_tasks = self.mem.tasks.list(status="open")
        self.assertEqual(len(open_tasks), 2)

        closed_tasks = self.mem.tasks.list(status="closed")
        self.assertEqual(len(closed_tasks), 1)

    def test_list_tasks_by_label(self):
        """Can filter tasks by label."""
        self.mem.tasks.create("Question", labels=["question"])
        self.mem.tasks.create("Section", labels=["section"])
        self.mem.tasks.create("Also question", labels=["question"])

        questions = self.mem.tasks.list(label="question")
        self.assertEqual(len(questions), 2)

    def test_ready_tasks(self):
        """Ready returns tasks with no blockers."""
        task1 = self.mem.tasks.create("Task 1")
        task2 = self.mem.tasks.create("Task 2")
        self.mem.tasks.block(task1.id, task2.id)  # task1 blocks task2

        ready = self.mem.tasks.ready()
        ready_ids = [t.id for t in ready]
        self.assertIn(task1.id, ready_ids)
        self.assertNotIn(task2.id, ready_ids)

    def test_task_history(self):
        """History shows all versions of a task."""
        task = self.mem.tasks.create("Original")
        self.mem.tasks.update(task.id, title="Updated")
        self.mem.tasks.update(task.id, status="closed")

        history = self.mem.tasks.history(task.id)
        self.assertEqual(len(history), 3)  # create + 2 updates


class TestDecisionOperations(unittest.TestCase):
    """Test decision trail operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, ".memory")
        self.mem = Memory(self.memory_path)

    def tearDown(self):
        self.mem.close()
        shutil.rmtree(self.temp_dir)

    def test_begin_decision(self):
        """Can begin a decision."""
        decision = self.mem.decisions.begin("How to frame the answer")
        self.assertIsNotNone(decision.id)
        self.assertTrue(decision.id.startswith("qt-"))
        self.assertEqual(decision.context, "How to frame the answer")
        self.assertEqual(decision.phase, "abduction")

    def test_begin_decision_with_task(self):
        """Can link decision to a task."""
        task = self.mem.tasks.create("Answer question")
        decision = self.mem.decisions.begin("How to frame", task_id=task.id)
        self.assertEqual(decision.task_id, task.id)

    def test_add_hypothesis(self):
        """Can add hypotheses to a decision."""
        decision = self.mem.decisions.begin("Test decision")
        self.mem.decisions.hypothesize(decision.id, "Option A", rationale="Because A")
        self.mem.decisions.hypothesize(decision.id, "Option B", confidence=0.8)

        retrieved = self.mem.decisions.get(decision.id)
        self.assertEqual(len(retrieved.hypotheses), 2)
        self.assertEqual(retrieved.hypotheses[0].id, "h1")
        self.assertEqual(retrieved.hypotheses[1].id, "h2")

    def test_decide(self):
        """Can select a hypothesis and close decision."""
        decision = self.mem.decisions.begin("Test")
        self.mem.decisions.hypothesize(decision.id, "Option A")
        self.mem.decisions.hypothesize(decision.id, "Option B")
        self.mem.decisions.decide(decision.id, "h2", rationale="B is better")

        retrieved = self.mem.decisions.get(decision.id)
        self.assertEqual(retrieved.selected, "h2")
        self.assertEqual(retrieved.phase, "decided")
        self.assertIsNotNone(retrieved.decided_at)

    def test_list_decisions_by_task(self):
        """Can filter decisions by task."""
        task = self.mem.tasks.create("Question")
        self.mem.decisions.begin("Decision 1", task_id=task.id)
        self.mem.decisions.begin("Decision 2", task_id=task.id)
        self.mem.decisions.begin("Unrelated")

        task_decisions = self.mem.decisions.for_task(task.id)
        self.assertEqual(len(task_decisions), 2)


class TestSynthesis(unittest.TestCase):
    """Test synthesis operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, ".memory")
        self.mem = Memory(self.memory_path)

    def tearDown(self):
        self.mem.close()
        shutil.rmtree(self.temp_dir)

    def test_patterns_empty(self):
        """Patterns returns empty list when no tasks."""
        patterns = self.mem.synthesize.patterns()
        self.assertEqual(patterns, [])

    def test_patterns_detects_labels(self):
        """Patterns detects recurring labels."""
        self.mem.tasks.create("Q1", labels=["question"])
        self.mem.tasks.create("Q2", labels=["question"])
        self.mem.tasks.create("Q3", labels=["question"])

        patterns = self.mem.synthesize.patterns()
        label_patterns = [p for p in patterns if "question" in p.description]
        self.assertGreater(len(label_patterns), 0)

    def test_connections_finds_dependencies(self):
        """Connections finds task dependencies."""
        task1 = self.mem.tasks.create("Task 1")
        task2 = self.mem.tasks.create("Task 2")
        self.mem.tasks.block(task1.id, task2.id)

        connections = self.mem.synthesize.connections(task1.id)
        block_connections = [c for c in connections if c.relationship == "blocks"]
        self.assertEqual(len(block_connections), 1)

    def test_summary(self):
        """Summary returns correct counts."""
        self.mem.tasks.create("Open task")
        closed = self.mem.tasks.create("Closed task")
        self.mem.tasks.close(closed.id)
        self.mem.decisions.begin("A decision")

        summary = self.mem.summary()
        self.assertEqual(summary["tasks"]["total"], 2)
        self.assertEqual(summary["decisions"]["total"], 1)


class TestPersistence(unittest.TestCase):
    """Test that data persists across Memory instances."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory_path = os.path.join(self.temp_dir, ".memory")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_tasks_persist(self):
        """Tasks persist after closing and reopening."""
        # Create and close
        mem1 = Memory(self.memory_path)
        task = mem1.tasks.create("Persistent task")
        task_id = task.id
        mem1.close()

        # Reopen and verify
        mem2 = Memory(self.memory_path)
        retrieved = mem2.tasks.get(task_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Persistent task")
        mem2.close()

    def test_decisions_persist(self):
        """Decisions persist after closing and reopening."""
        # Create and close
        mem1 = Memory(self.memory_path)
        decision = mem1.decisions.begin("Persistent decision")
        decision_id = decision.id
        mem1.close()

        # Reopen and verify
        mem2 = Memory(self.memory_path)
        retrieved = mem2.decisions.get(decision_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.context, "Persistent decision")
        mem2.close()

    def test_rebuild_index(self):
        """Index can be rebuilt from JSONL."""
        # Create data
        mem1 = Memory(self.memory_path)
        mem1.tasks.create("Task 1")
        mem1.tasks.create("Task 2")
        mem1.close()

        # Delete index
        index_path = os.path.join(self.memory_path, "index.db")
        os.remove(index_path)

        # Reopen and rebuild
        mem2 = Memory(self.memory_path)
        mem2.rebuild_index()
        all_tasks = mem2.tasks.all()
        self.assertEqual(len(all_tasks), 2)
        mem2.close()


class TestIntegrationWithHelper(unittest.TestCase):
    """Test memory layer integration with SEAApplicationHelper."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.memory_path = os.path.join(self.temp_dir, ".memory")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_helper_uses_memory(self):
        """SEAApplicationHelper writes answers to memory layer."""
        from sea_application_helper import SEAApplicationHelper

        helper = SEAApplicationHelper(
            db_path=self.db_path,
            memory_path=self.memory_path
        )

        # Save an answer
        helper.save_answer("q1", "Test answer", status="in_progress")

        # Verify in memory
        tasks = [t for t in helper.memory.tasks.all()
                 if t.metadata.get("question_id") == "q1"]
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, "Test answer")
        self.assertEqual(tasks[0].status, "in_progress")

        helper.close()

    def test_helper_reads_from_memory(self):
        """SEAApplicationHelper reads answers from memory layer."""
        from sea_application_helper import SEAApplicationHelper

        # First, we need a config with a question
        config_path = os.path.join(self.temp_dir, "config.json")
        config = {
            "form_name": "Test Form",
            "sections": [{"id": 1, "name": "test", "title": "Test Section"}],
            "questions": [{
                "id": "q1",
                "section_id": 1,
                "question_text": "Test question?"
            }]
        }
        with open(config_path, "w") as f:
            json.dump(config, f)

        helper = SEAApplicationHelper(
            db_path=self.db_path,
            config_path=config_path,
            memory_path=self.memory_path
        )
        helper.populate_questions()

        # Save answer
        helper.save_answer("q1", "My answer", status="complete")

        # Read it back
        question = helper.get_question("q1")
        self.assertEqual(question["answer_text"], "My answer")
        self.assertEqual(question["status"], "complete")

        helper.close()


if __name__ == "__main__":
    unittest.main()
