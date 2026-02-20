#!/usr/bin/env python3
"""Tests for config validation."""

import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_config import validate_config, load_config


class TestValidateConfig(unittest.TestCase):
    """Test config validation logic."""

    @classmethod
    def setUpClass(cls):
        """Load test fixtures."""
        fixtures = Path(__file__).parent / 'fixtures'
        cls.valid_config = load_config(fixtures / 'valid_config.json')
        cls.invalid_config = load_config(fixtures / 'invalid_config.json')

    def test_valid_config_passes(self):
        """Valid config should pass validation."""
        is_valid, errors, warnings = validate_config(self.valid_config)
        self.assertTrue(is_valid, f"Valid config failed with errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_valid_config_no_warnings(self):
        """Valid config should have no warnings."""
        is_valid, errors, warnings = validate_config(self.valid_config)
        self.assertEqual(len(warnings), 0, f"Unexpected warnings: {warnings}")

    def test_invalid_config_fails(self):
        """Invalid config should fail validation."""
        is_valid, errors, warnings = validate_config(self.invalid_config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_detects_duplicate_section_id(self):
        """Should detect duplicate section IDs."""
        is_valid, errors, warnings = validate_config(self.invalid_config)
        duplicate_errors = [e for e in errors if 'Duplicate section ID' in e]
        self.assertGreater(len(duplicate_errors), 0)

    def test_detects_duplicate_question_id(self):
        """Should detect duplicate question IDs."""
        is_valid, errors, warnings = validate_config(self.invalid_config)
        duplicate_errors = [e for e in errors if 'Duplicate question ID' in e]
        self.assertGreater(len(duplicate_errors), 0)

    def test_detects_invalid_section_reference(self):
        """Should detect questions referencing non-existent sections."""
        is_valid, errors, warnings = validate_config(self.invalid_config)
        ref_errors = [e for e in errors if 'invalid section_id' in e]
        self.assertGreater(len(ref_errors), 0)

    def test_detects_invalid_depends_on(self):
        """Should detect invalid depends_on references."""
        is_valid, errors, warnings = validate_config(self.invalid_config)
        dep_errors = [e for e in errors if 'depends_on invalid' in e]
        self.assertGreater(len(dep_errors), 0)

    def test_warns_on_section_gaps(self):
        """Should warn about gaps in section IDs."""
        is_valid, errors, warnings = validate_config(self.invalid_config)
        gap_warnings = [w for w in warnings if 'gap' in w.lower()]
        self.assertGreater(len(gap_warnings), 0)

    def test_warns_on_unusual_priority(self):
        """Should warn about priority values outside 1-3."""
        is_valid, errors, warnings = validate_config(self.invalid_config)
        priority_warnings = [w for w in warnings if 'priority' in w.lower()]
        self.assertGreater(len(priority_warnings), 0)

    def test_missing_required_fields(self):
        """Should error on missing required fields."""
        incomplete = {"form_name": "Test"}  # Missing sections and questions
        is_valid, errors, warnings = validate_config(incomplete)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_empty_questions(self):
        """Should handle config with empty questions list."""
        config = {
            "form_name": "Empty",
            "sections": [{"id": 1, "title": "Section"}],
            "questions": []
        }
        is_valid, errors, warnings = validate_config(config)
        # Empty questions is technically valid per schema
        self.assertTrue(is_valid)

    def test_valid_depends_on_later_question(self):
        """depends_on can reference a question defined later in the list."""
        config = {
            "form_name": "Forward Reference",
            "sections": [{"id": 1, "title": "Section"}],
            "questions": [
                {"id": "1", "section_id": 1, "question_text": "Q1", "depends_on": "2"},
                {"id": "2", "section_id": 1, "question_text": "Q2"}
            ]
        }
        is_valid, errors, warnings = validate_config(config)
        self.assertTrue(is_valid, f"Forward reference failed: {errors}")


class TestLoadConfig(unittest.TestCase):
    """Test config loading."""

    def test_load_valid_json(self):
        """Should load valid JSON file."""
        fixtures = Path(__file__).parent / 'fixtures'
        config = load_config(fixtures / 'valid_config.json')
        self.assertIsInstance(config, dict)
        self.assertIn('form_name', config)

    def test_load_nonexistent_file(self):
        """Should raise error for nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            load_config(Path('/nonexistent/path.json'))


if __name__ == '__main__':
    unittest.main()
