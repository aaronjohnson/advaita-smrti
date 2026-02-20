#!/usr/bin/env python3
"""Tests for smrti CLI."""

import unittest
import subprocess
import tempfile
import shutil
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCLIHelp(unittest.TestCase):
    """Test CLI help and basic invocation."""

    def test_help_flag(self):
        """Should display help with --help."""
        result = subprocess.run(
            ['python3', 'smrti.py', '--help'],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('smrti', result.stdout)
        self.assertIn('export', result.stdout)
        self.assertIn('validate', result.stdout)

    def test_export_help(self):
        """Should display export subcommand help."""
        result = subprocess.run(
            ['python3', 'smrti.py', 'export', '--help'],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('json', result.stdout)
        self.assertIn('markdown', result.stdout)
        self.assertIn('texinfo', result.stdout)


class TestCLIValidate(unittest.TestCase):
    """Test CLI validate command."""

    def test_validate_valid_config(self):
        """Should validate a valid config successfully."""
        result = subprocess.run(
            ['python3', 'smrti.py', 'validate', 'tests/fixtures/valid_config.json'],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('VALID', result.stdout)

    def test_validate_invalid_config(self):
        """Should fail on invalid config."""
        result = subprocess.run(
            ['python3', 'smrti.py', 'validate', 'tests/fixtures/invalid_config.json'],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn('INVALID', result.stdout)

    def test_validate_all(self):
        """Should validate all configs in examples/."""
        result = subprocess.run(
            ['python3', 'smrti.py', 'validate', '--all'],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('ALL VALID', result.stdout)

    def test_validate_nonexistent_file(self):
        """Should fail for nonexistent file."""
        result = subprocess.run(
            ['python3', 'smrti.py', 'validate', 'nonexistent.json'],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 1)


class TestCLIList(unittest.TestCase):
    """Test CLI list command."""

    def test_list_shows_configs(self):
        """Should list available configs."""
        result = subprocess.run(
            ['python3', 'smrti.py', 'list'],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('Available Configs', result.stdout)
        self.assertIn('oregon_sea_config.json', result.stdout)


class TestCLIExport(unittest.TestCase):
    """Test CLI export command."""

    def setUp(self):
        """Create temporary directory and test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()

        # Create a test database
        from sea_application_helper import SEAApplicationHelper
        config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'
        self.db_path = Path(self.temp_dir) / 'test.db'

        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(config_path)
        )
        helper.save_answer('1', 'Test answer', status='complete')
        helper.close()

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_json(self):
        """Should export to JSON."""
        output = Path(self.temp_dir) / 'output.json'
        result = subprocess.run(
            [
                'python3', 'smrti.py', 'export', 'json',
                '--db', str(self.db_path),
                '--config', 'tests/fixtures/valid_config.json',
                '-o', str(output)
            ],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0, f"Export failed: {result.stderr}")
        self.assertTrue(output.exists())

    def test_export_markdown(self):
        """Should export to Markdown."""
        output = Path(self.temp_dir) / 'output.md'
        result = subprocess.run(
            [
                'python3', 'smrti.py', 'export', 'markdown',
                '--db', str(self.db_path),
                '--config', 'tests/fixtures/valid_config.json',
                '-o', str(output)
            ],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0, f"Export failed: {result.stderr}")
        self.assertTrue(output.exists())
        content = output.read_text()
        self.assertIn('# Test Form', content)

    def test_export_texinfo(self):
        """Should export to Texinfo."""
        output = Path(self.temp_dir) / 'output.texi'
        result = subprocess.run(
            [
                'python3', 'smrti.py', 'export', 'texinfo',
                '--db', str(self.db_path),
                '--config', 'tests/fixtures/valid_config.json',
                '-o', str(output)
            ],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0, f"Export failed: {result.stderr}")
        self.assertTrue(output.exists())
        content = output.read_text()
        self.assertIn('@settitle Test Form', content)


class TestCLIStatus(unittest.TestCase):
    """Test CLI status command."""

    def setUp(self):
        """Create temporary database."""
        self.temp_dir = tempfile.mkdtemp()

        from sea_application_helper import SEAApplicationHelper
        config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'
        self.db_path = Path(self.temp_dir) / 'test.db'

        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(config_path)
        )
        helper.populate_questions()
        helper.save_answer('1', 'Test', status='complete')
        helper.close()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_status_shows_progress(self):
        """Should show progress summary."""
        result = subprocess.run(
            [
                'python3', 'smrti.py', 'status',
                '--db', str(self.db_path),
                '--config', 'tests/fixtures/valid_config.json'
            ],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('Test Form', result.stdout)
        self.assertIn('Progress:', result.stdout)
        self.assertIn('1/4', result.stdout)  # 1 complete of 4 total


if __name__ == '__main__':
    unittest.main()
