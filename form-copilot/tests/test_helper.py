#!/usr/bin/env python3
"""Tests for SEAApplicationHelper."""

import unittest
import tempfile
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sea_application_helper import SEAApplicationHelper


class TestSEAApplicationHelper(unittest.TestCase):
    """Test database helper operations."""

    def setUp(self):
        """Create a temporary database and config for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'
        self.log_path = Path(self.temp_dir) / 'session_log.json'

        self.helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(self.config_path),
            log_path=str(self.log_path)
        )
        # Populate database from config
        self.helper.populate_questions()

    def tearDown(self):
        """Clean up temporary files."""
        self.helper.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_database(self):
        """Should create database file on init."""
        self.assertTrue(self.db_path.exists())

    def test_get_form_info(self):
        """Should return form metadata."""
        info = self.helper.get_form_info()
        self.assertEqual(info['name'], 'Test Form')
        self.assertEqual(info['version'], '1.0')

    def test_get_sections(self):
        """Should return all sections."""
        sections = self.helper.get_sections()
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0]['title'], 'Basic Information')

    def test_get_questions_by_section(self):
        """Should return questions for a section."""
        questions = self.helper.get_questions_by_section(1)
        self.assertEqual(len(questions), 2)  # Questions 1 and 2

    def test_get_question(self):
        """Should return specific question by ID."""
        q = self.helper.get_question('1')
        self.assertIsNotNone(q)
        self.assertEqual(q['question_text'], 'What is your name?')

    def test_get_nonexistent_question(self):
        """Should return None for nonexistent question."""
        q = self.helper.get_question('999')
        self.assertIsNone(q)

    def test_save_answer(self):
        """Should save and retrieve answer."""
        self.helper.save_answer('1', 'John Doe', status='complete')
        q = self.helper.get_question('1')
        self.assertEqual(q['answer_text'], 'John Doe')
        self.assertEqual(q['status'], 'complete')

    def test_save_answer_with_notes(self):
        """Should save answer with notes."""
        self.helper.save_answer('1', 'John Doe', notes='Check spelling', status='in_progress')
        q = self.helper.get_question('1')
        self.assertEqual(q['notes'], 'Check spelling')
        self.assertEqual(q['status'], 'in_progress')

    def test_update_answer(self):
        """Should update existing answer."""
        self.helper.save_answer('1', 'John Doe')
        self.helper.save_answer('1', 'Jane Doe')
        q = self.helper.get_question('1')
        self.assertEqual(q['answer_text'], 'Jane Doe')

    def test_get_progress(self):
        """Should track progress correctly."""
        progress = self.helper.get_progress()
        self.assertEqual(progress['total'], 4)
        self.assertEqual(progress['complete'], 0)
        self.assertEqual(progress['not_started'], 4)

        self.helper.save_answer('1', 'Answer 1', status='complete')
        self.helper.save_answer('2', 'Answer 2', status='in_progress')

        progress = self.helper.get_progress()
        self.assertEqual(progress['complete'], 1)
        self.assertEqual(progress['in_progress'], 1)
        self.assertEqual(progress['not_started'], 2)

    def test_get_priority_questions(self):
        """Should return questions filtered by priority."""
        p1_questions = self.helper.get_priority_questions(priority=1)
        # Questions 1 and 3 have priority 1
        self.assertEqual(len(p1_questions), 2)

    def test_get_business_directions(self):
        """Should return business directions."""
        directions = self.helper.get_business_directions()
        self.assertEqual(len(directions), 2)
        self.assertEqual(directions[0]['name'], 'Option A')


class TestSessionLogging(unittest.TestCase):
    """Test session logging functionality."""

    def setUp(self):
        """Create a temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'
        self.log_path = Path(self.temp_dir) / 'session_log.json'

        self.helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(self.config_path),
            log_path=str(self.log_path)
        )
        self.helper.populate_questions()

    def tearDown(self):
        """Clean up temporary files."""
        self.helper.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_event(self):
        """Should log events."""
        self.helper.log_event('test_event', question_id='1')
        history = self.helper.get_session_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['event'], 'test_event')

    def test_log_event_with_details(self):
        """Should log events with additional details."""
        self.helper.log_event('claude_session_start', question_id='1', details={'had_draft': True})
        history = self.helper.get_session_history()
        self.assertEqual(history[0]['had_draft'], True)

    def test_get_session_history_filtered(self):
        """Should filter history by question ID."""
        self.helper.log_event('event1', question_id='1')
        self.helper.log_event('event2', question_id='2')
        self.helper.log_event('event3', question_id='1')

        history = self.helper.get_session_history(question_id='1')
        self.assertEqual(len(history), 2)

    def test_get_question_journey(self):
        """Should return journey summary for a question."""
        self.helper.log_event('claude_session_start', question_id='1')
        self.helper.log_event('answer_saved', question_id='1')
        self.helper.log_event('claude_session_start', question_id='1')
        self.helper.log_event('answer_saved', question_id='1')

        journey = self.helper.get_question_journey('1')
        self.assertEqual(journey['total_events'], 4)
        self.assertEqual(journey['claude_sessions'], 2)
        self.assertEqual(journey['revisions'], 2)

    def test_analyze_session_log_empty(self):
        """Should return None for empty log."""
        analysis = self.helper.analyze_session_log()
        self.assertIsNone(analysis)

    def test_analyze_session_log(self):
        """Should analyze session log correctly."""
        self.helper.log_event('claude_session_start', question_id='1')
        self.helper.log_event('answer_saved', question_id='1')
        self.helper.log_event('claude_session_start', question_id='2')
        self.helper.log_event('question_viewed', question_id='1')

        analysis = self.helper.analyze_session_log()
        self.assertEqual(analysis['total_events'], 4)
        self.assertEqual(analysis['claude_sessions_total'], 2)
        self.assertEqual(analysis['questions_with_claude'], 2)
        self.assertEqual(analysis['total_revisions'], 1)


class TestExports(unittest.TestCase):
    """Test export functionality."""

    def setUp(self):
        """Create a temporary database with test data."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'
        self.log_path = Path(self.temp_dir) / 'session_log.json'

        self.helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(self.config_path),
            log_path=str(self.log_path)
        )
        self.helper.populate_questions()

        # Add some test data
        self.helper.save_answer('1', 'Test Answer One', notes='Test note', status='complete')
        self.helper.save_answer('2', 'Test Answer Two', status='in_progress')

    def tearDown(self):
        """Clean up temporary files."""
        self.helper.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_json(self):
        """Should export to JSON."""
        output_path = Path(self.temp_dir) / 'export.json'
        self.helper.export_answers(str(output_path))

        self.assertTrue(output_path.exists())
        with open(output_path) as f:
            data = json.load(f)
        self.assertEqual(data['form_name'], 'Test Form')
        self.assertIn('answers', data)

    def test_export_markdown(self):
        """Should export to Markdown."""
        output_path = Path(self.temp_dir) / 'export.md'
        self.helper.export_markdown(str(output_path))

        self.assertTrue(output_path.exists())
        content = output_path.read_text()

        # Check structure
        self.assertIn('# Test Form', content)
        self.assertIn('## Basic Information', content)
        self.assertIn('Test Answer One', content)
        self.assertIn('✓', content)  # Complete status icon

    def test_export_markdown_includes_notes(self):
        """Markdown export should include notes."""
        output_path = Path(self.temp_dir) / 'export.md'
        self.helper.export_markdown(str(output_path))
        content = output_path.read_text()
        self.assertIn('Test note', content)

    def test_export_texinfo(self):
        """Should export to Texinfo."""
        output_path = Path(self.temp_dir) / 'export.texi'
        self.helper.export_texinfo(str(output_path))

        self.assertTrue(output_path.exists())
        content = output_path.read_text()

        # Check texinfo structure
        self.assertIn('\\input texinfo', content)
        self.assertIn('@settitle Test Form', content)
        self.assertIn('@chapter Basic Information', content)
        self.assertIn('@bye', content)

    def test_export_texinfo_escapes_special_chars(self):
        """Texinfo export should escape @ { } characters."""
        self.helper.save_answer('3', 'Email: test@example.com and {braces}')
        output_path = Path(self.temp_dir) / 'export.texi'
        self.helper.export_texinfo(str(output_path))

        content = output_path.read_text()
        self.assertIn('@@', content)  # @ escaped
        self.assertIn('@{', content)  # { escaped

    def test_export_includes_session_analysis(self):
        """Export should include session analysis if log exists."""
        # Add some log events
        self.helper.log_event('claude_session_start', question_id='1')
        self.helper.log_event('answer_saved', question_id='1')

        output_path = Path(self.temp_dir) / 'export.md'
        self.helper.export_markdown(str(output_path))

        content = output_path.read_text()
        self.assertIn('Session Analysis', content)


if __name__ == '__main__':
    unittest.main()
