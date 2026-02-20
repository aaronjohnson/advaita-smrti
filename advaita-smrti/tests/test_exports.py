#!/usr/bin/env python3
"""Tests for export_docs.py - direct import testing."""

import unittest
import tempfile
import shutil
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from export_docs import (
    find_databases,
    export_single,
    combine_markdown,
    combine_texinfo
)
from sea_application_helper import SEAApplicationHelper


class TestFindDatabases(unittest.TestCase):
    """Test database discovery."""

    def setUp(self):
        """Create temp directory with test databases."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        # Create some fake .db files
        (Path(self.temp_dir) / 'form1.db').touch()
        (Path(self.temp_dir) / 'form2.db').touch()
        (Path(self.temp_dir) / 'notadb.txt').touch()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_find_databases_returns_db_files(self):
        """Should find .db files in directory."""
        import os
        os.chdir(self.temp_dir)
        try:
            dbs = find_databases()
            self.assertEqual(len(dbs), 2)
            self.assertTrue(all(str(db).endswith('.db') for db in dbs))
        finally:
            os.chdir(self.original_cwd)


class TestExportSingle(unittest.TestCase):
    """Test single database export."""

    def setUp(self):
        """Create temp database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'

        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()
        helper.save_answer('1', 'Test answer', status='complete')
        helper.close()

        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        import os
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_single_markdown(self):
        """Should export single db to markdown."""
        # Need to copy config to temp dir for export to find it
        import shutil
        shutil.copy(self.config_path, Path(self.temp_dir) / 'config.json')

        from sea_application_helper import SEAApplicationHelper
        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(Path(self.temp_dir) / 'config.json')
        )
        filepath = helper.export_markdown('test_export.md')
        helper.close()

        self.assertTrue(Path(filepath).exists())
        content = Path(filepath).read_text()
        self.assertIn('Test Form', content)

    def test_export_single_texinfo(self):
        """Should export single db to texinfo."""
        import shutil
        shutil.copy(self.config_path, Path(self.temp_dir) / 'config.json')

        from sea_application_helper import SEAApplicationHelper
        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(Path(self.temp_dir) / 'config.json')
        )
        filepath = helper.export_texinfo('test_export.texi')
        helper.close()

        self.assertTrue(Path(filepath).exists())
        content = Path(filepath).read_text()
        self.assertIn('@settitle Test Form', content)


class TestCombineExports(unittest.TestCase):
    """Test combining multiple databases."""

    def setUp(self):
        """Create multiple test databases."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'

        # Create two databases
        self.db_paths = []
        for i in range(2):
            db_path = Path(self.temp_dir) / f'form{i}.db'
            helper = SEAApplicationHelper(
                db_path=str(db_path),
                config_path=str(self.config_path)
            )
            helper.populate_questions()
            helper.save_answer('1', f'Answer from form {i}', status='complete')
            helper.close()
            self.db_paths.append(db_path)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_combine_markdown(self):
        """Should combine multiple dbs into one markdown."""
        output_path = Path(self.temp_dir) / 'combined.md'
        result = combine_markdown(self.db_paths, str(output_path))

        self.assertTrue(output_path.exists())
        content = output_path.read_text()
        self.assertIn('Combined Form Export', content)
        self.assertIn('Answer from form 0', content)
        self.assertIn('Answer from form 1', content)

    def test_combine_texinfo(self):
        """Should combine multiple dbs into one texinfo."""
        output_path = Path(self.temp_dir) / 'combined.texi'
        result = combine_texinfo(self.db_paths, str(output_path))

        self.assertTrue(output_path.exists())
        content = output_path.read_text()
        self.assertIn('Combined Form Export', content)
        self.assertIn('Answer from form 0', content)
        self.assertIn('Answer from form 1', content)
        self.assertIn('@bye', content)


class TestExportEdgeCases(unittest.TestCase):
    """Test edge cases in exports."""

    def setUp(self):
        """Create temp database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test.db'
        self.config_path = Path(__file__).parent / 'fixtures' / 'valid_config.json'

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_empty_database(self):
        """Should handle database with no answers."""
        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()
        # No answers saved

        md_path = Path(self.temp_dir) / 'empty.md'
        helper.export_markdown(str(md_path))

        content = md_path.read_text()
        self.assertIn('0/4 complete', content)
        self.assertIn('No answer yet', content)
        helper.close()

    def test_export_special_characters(self):
        """Should handle special characters in answers."""
        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()

        # Answer with special chars that need escaping in texinfo
        special_answer = "Email: test@example.com, code: {foo}, price: $100 & more"
        helper.save_answer('1', special_answer, status='complete')

        texi_path = Path(self.temp_dir) / 'special.texi'
        helper.export_texinfo(str(texi_path))

        content = texi_path.read_text()
        # @ { } should be escaped
        self.assertIn('@@', content)
        self.assertIn('@{', content)
        self.assertIn('@}', content)
        helper.close()

    def test_export_very_long_answer(self):
        """Should handle very long answers."""
        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()

        long_answer = "This is a test. " * 1000  # ~16KB of text
        helper.save_answer('1', long_answer, status='complete')

        md_path = Path(self.temp_dir) / 'long.md'
        helper.export_markdown(str(md_path))

        content = md_path.read_text()
        self.assertIn('This is a test.', content)
        self.assertGreater(len(content), 10000)
        helper.close()

    def test_export_multiline_answer(self):
        """Should preserve line breaks in answers."""
        helper = SEAApplicationHelper(
            db_path=str(self.db_path),
            config_path=str(self.config_path)
        )
        helper.populate_questions()

        multiline = "Line 1\nLine 2\nLine 3"
        helper.save_answer('1', multiline, status='complete')

        md_path = Path(self.temp_dir) / 'multiline.md'
        helper.export_markdown(str(md_path))

        content = md_path.read_text()
        self.assertIn('Line 1\nLine 2\nLine 3', content)
        helper.close()


if __name__ == '__main__':
    unittest.main()
