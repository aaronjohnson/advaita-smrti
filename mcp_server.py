#!/usr/bin/env python3
"""Deprecated: use `smrti-mcp` (installed entry point) instead.

This file delegates to smrti.mcp:main for backward compatibility.
"""
import warnings
warnings.warn(
    "mcp_server.py is deprecated. Use `smrti-mcp` or `python -m smrti.mcp` instead.",
    DeprecationWarning,
    stacklevel=1,
)

from smrti.mcp import main
main()
