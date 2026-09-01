#!/usr/bin/env python3
"""Tests for the MCP server layer.

These exist because a broken import here is silent: the stdio server dies
before the handshake, and the client cannot tell that from a server it was
never approved to launch. Importing the module in CI is what turns that
silence into a failing test.
"""

import asyncio
import unittest
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import smrti.mcp as mcp_server
except ImportError as exc:  # SDK not installed -- `pip install .[mcp]`
    mcp_server = None
    _import_error = exc


@unittest.skipIf(mcp_server is None, "mcp SDK not installed (pip install .[mcp])")
class TestMCPServer(unittest.TestCase):
    """The server module must import and register its tools."""

    def test_server_constructed(self):
        self.assertEqual(mcp_server.mcp.name, "smrti")

    def test_tools_registered(self):
        tools = asyncio.run(mcp_server.mcp.list_tools())
        names = {t.name for t in tools}
        # A representative tool from each store, plus maintenance.
        for expected in ("task_list", "task_create", "decision_begin",
                         "fact_search", "memory_summary", "rebuild_index"):
            self.assertIn(expected, names)

    def test_every_tool_has_a_description(self):
        """Descriptions come from docstrings; a bare tool is unusable to a client."""
        tools = asyncio.run(mcp_server.mcp.list_tools())
        undocumented = [t.name for t in tools if not t.description]
        self.assertEqual(undocumented, [])


if __name__ == "__main__":
    unittest.main()
