#!/usr/bin/env python3
"""Edge case and error handling tests."""

import unittest
import tempfile
import shutil
import json
import sys
from pathlib import Path
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sea_application_helper import SEAApplicationHelper
from validate_config import validate_config, load_config, print_results, main as validate_main


class TestHelperEdgeCases(unittest.TestCase):
    """Edge cases for SEAApplicationHelper."""

    def setUp(self):
        """Create temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_no_config_file(self):
        """Should handle missing config file gracefully."""
        db_path = Path(self.temp_dir) / 'test.db'
        helper = SEAApplicationHelper(
            db_path=str(db_path),
            config_path='/nonexistent/config.json'
        )
        # Should still create database, just no questions
        self.assertTrue(db_path.exists())
        info = helper.get_form_info()
        self.assertEqual(info['name'], 'No form loaded')
        helper.close()

    def test_save_answer_to_nonexistent_question(self):
        """Should handle saving to nonexistent question."""
        db_path = Path(self.temp_dir) / 'test.db'
        helper = SEAApplicationHelper(
            db_path=str(db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()

        # This should work even though question 999 doesn't exist in questions table
        # (answers table has foreign key, but SQLite doesn't enforce by default)
        helper.save_answer('999', 'Answer to nothing')
        helper.close()

    def test_get_question_with_answer(self):
        """Should return question with merged answer data."""
        db_path = Path(self.temp_dir) / 'test.db'
        helper = SEAApplicationHelper(
            db_path=str(db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()
        helper.save_answer('1', 'My answer', notes='My notes', status='complete')

        q = helper.get_question('1')
        self.assertEqual(q['answer_text'], 'My answer')
        self.assertEqual(q['notes'], 'My notes')
        self.assertEqual(q['status'], 'complete')
        helper.close()

    def test_progress_all_complete(self):
        """Should handle 100% completion."""
        db_path = Path(self.temp_dir) / 'test.db'
        helper = SEAApplicationHelper(
            db_path=str(db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()

        # Complete all questions
        for qid in ['1', '2', '3', '3a']:
            helper.save_answer(qid, f'Answer {qid}', status='complete')

        progress = helper.get_progress()
        self.assertEqual(progress['complete'], 4)
        self.assertEqual(progress['percent_complete'], 100.0)
        helper.close()

    def test_unicode_in_answers(self):
        """Should handle unicode characters."""
        db_path = Path(self.temp_dir) / 'test.db'
        helper = SEAApplicationHelper(
            db_path=str(db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()

        unicode_answer = "日本語テスト 🎉 émojis and àccénts"
        helper.save_answer('1', unicode_answer, status='complete')

        q = helper.get_question('1')
        self.assertEqual(q['answer_text'], unicode_answer)
        helper.close()

    def test_empty_answer(self):
        """Should handle empty string answer."""
        db_path = Path(self.temp_dir) / 'test.db'
        helper = SEAApplicationHelper(
            db_path=str(db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()

        helper.save_answer('1', '', status='in_progress')
        q = helper.get_question('1')
        self.assertEqual(q['answer_text'], '')
        helper.close()

    def test_session_log_persistence(self):
        """Session log should persist across helper instances."""
        db_path = Path(self.temp_dir) / 'test.db'
        log_path = Path(self.temp_dir) / 'session.json'

        # First instance - log an event
        helper1 = SEAApplicationHelper(
            db_path=str(db_path),
            config_path=str(self.config_path),
            log_path=str(log_path)
        )
        helper1.log_event('test_event', question_id='1')
        helper1.close()

        # Second instance - should see the event
        helper2 = SEAApplicationHelper(
            db_path=str(db_path),
            config_path=str(self.config_path),
            log_path=str(log_path)
        )
        history = helper2.get_session_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['event'], 'test_event')
        helper2.close()


class TestValidateConfigMain(unittest.TestCase):
    """Tests for validate_config main() and print_results()."""

    def test_print_results_valid(self):
        """Should print valid status."""
        # Capture stdout
        captured = StringIO()
        sys.stdout = captured
        try:
            result = print_results('test.json', True, [], [])
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn('VALID', output)
        self.assertTrue(result)

    def test_print_results_invalid(self):
        """Should print invalid status with errors."""
        captured = StringIO()
        sys.stdout = captured
        try:
            result = print_results('test.json', False, ['Error 1', 'Error 2'], [])
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn('INVALID', output)
        self.assertIn('Error 1', output)
        self.assertIn('Error 2', output)
        self.assertFalse(result)

    def test_print_results_with_warnings(self):
        """Should print warnings."""
        captured = StringIO()
        sys.stdout = captured
        try:
            print_results('test.json', True, [], ['Warning 1'])
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn('Warning 1', output)


class TestValidateConfigEdgeCases(unittest.TestCase):
    """Edge cases for config validation."""

    def test_question_missing_question_text(self):
        """Should error on question without question_text."""
        config = {
            "form_name": "Test",
            "sections": [{"id": 1, "title": "Section"}],
            "questions": [
                {"id": "1", "section_id": 1, "question_text": ""},  # Empty
            ]
        }
        is_valid, errors, warnings = validate_config(config)
        self.assertFalse(is_valid)
        error_text = ' '.join(errors)
        self.assertIn('question_text', error_text.lower())

    def test_section_missing_title(self):
        """Should error on section without title."""
        config = {
            "form_name": "Test",
            "sections": [{"id": 1}],  # Missing title
            "questions": []
        }
        is_valid, errors, warnings = validate_config(config)
        self.assertFalse(is_valid)
        error_text = ' '.join(errors)
        self.assertIn('title', error_text.lower())

    def test_valid_question_types(self):
        """Should accept all valid question types without warnings."""
        config = {
            "form_name": "Test",
            "sections": [{"id": 1, "title": "Section"}],
            "questions": [
                {"id": "1", "section_id": 1, "question_text": "Q1", "question_type": "text"},
                {"id": "2", "section_id": 1, "question_text": "Q2", "question_type": "long_text"},
                {"id": "3", "section_id": 1, "question_text": "Q3", "question_type": "yes_no"},
                {"id": "4", "section_id": 1, "question_text": "Q4", "question_type": "number"},
                {"id": "5", "section_id": 1, "question_text": "Q5", "question_type": "choice"},
            ]
        }
        is_valid, errors, warnings = validate_config(config)
        self.assertTrue(is_valid)
        type_warnings = [w for w in warnings if 'type' in w.lower()]
        self.assertEqual(len(type_warnings), 0)

    def test_unknown_question_type_warns(self):
        """Should warn on unknown question type."""
        config = {
            "form_name": "Test",
            "sections": [{"id": 1, "title": "Section"}],
            "questions": [
                {"id": "1", "section_id": 1, "question_text": "Q1", "question_type": "unknown_type"},
            ]
        }
        is_valid, errors, warnings = validate_config(config)
        self.assertTrue(is_valid)  # Warning, not error
        self.assertGreater(len(warnings), 0)

    def test_circular_depends_on(self):
        """Should handle (but not detect) circular dependencies."""
        # Note: current validator doesn't detect cycles, just invalid refs
        config = {
            "form_name": "Test",
            "sections": [{"id": 1, "title": "Section"}],
            "questions": [
                {"id": "1", "section_id": 1, "question_text": "Q1", "depends_on": "2"},
                {"id": "2", "section_id": 1, "question_text": "Q2", "depends_on": "1"},
            ]
        }
        is_valid, errors, warnings = validate_config(config)
        # Both references are valid (they exist), so it passes
        # Circular dependency detection could be a future enhancement
        self.assertTrue(is_valid)

    def test_null_depends_on(self):
        """Should accept null depends_on."""
        config = {
            "form_name": "Test",
            "sections": [{"id": 1, "title": "Section"}],
            "questions": [
                {"id": "1", "section_id": 1, "question_text": "Q1", "depends_on": None},
            ]
        }
        is_valid, errors, warnings = validate_config(config)
        self.assertTrue(is_valid)


class TestDatabaseErrorHandling(unittest.TestCase):
    """Test database error handling."""

    def test_readonly_directory(self):
        """Should handle inability to create database."""
        # This is tricky to test portably, skip if we can't set up the condition
        pass  # Placeholder for environment-specific test

    def test_concurrent_access(self):
        """Multiple helpers accessing same database."""
        temp_dir = tempfile.mkdtemp()
        try:
            db_path = Path(temp_dir) / 'shared.db'
            config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'

            helper1 = SEAApplicationHelper(
                db_path=str(db_path),
                config_path=str(config_path)
            )
            helper1.populate_questions()

            helper2 = SEAApplicationHelper(
                db_path=str(db_path),
                config_path=str(config_path)
            )

            # Both should be able to read
            q1 = helper1.get_question('1')
            q2 = helper2.get_question('1')
            self.assertEqual(q1['question_text'], q2['question_text'])

            helper1.close()
            helper2.close()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
