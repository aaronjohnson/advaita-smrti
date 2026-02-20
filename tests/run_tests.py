#!/usr/bin/env python3
"""
Run all tests for smrti.

Usage:
    python3 tests/run_tests.py           # Run all tests
    python3 tests/run_tests.py -v        # Verbose output
    python3 -m pytest tests/             # If pytest is installed
"""

import unittest
import sys
from pathlib import Path

# Ensure we can import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests(verbosity=1):
    """Discover and run all tests."""
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=Path(__file__).parent,
        pattern='test_*.py'
    )

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    verbosity = 2 if '-v' in sys.argv or '--verbose' in sys.argv else 1
    sys.exit(run_tests(verbosity))
