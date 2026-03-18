# smṛti MCP profile flag — implementation sketch
#
# This is a proposed patch to smrti/mcp.py to add --profile and --memory-dir
# flags to the `smrti-mcp` entry point.
#
# The patch assumes the existing main() function registers tools via
# @mcp.tool() decorators. The profile flag filters which tools are exposed
# at server startup, without changing the tool implementation code.
#
# Drop this into a PR against the sutra branch.

# ── In pyproject.toml, entry point is already: ──────────────────────────────
# [project.scripts]
# smrti-mcp = "smrti.mcp:main"
#
# ── Patch for smrti/mcp.py ───────────────────────────────────────────────────

PATCH = r"""
--- a/smrti/mcp.py
+++ b/smrti/mcp.py
@@ -1,6 +1,8 @@
 #!/usr/bin/env python3
 """smṛti MCP server entry point."""
+import argparse
 import sys
+from pathlib import Path
 from mcp.server.fastmcp import FastMCP

 # Tool categories by profile
+PROFILE_TOOLS = {
+    "full": None,   # None = all tools registered
+    "coding": {
+        # Core recall + write (what an agent needs mid-session)
+        "memory_status",
+        "tasks_list",
+        "tasks_create",
+        "tasks_close",
+        "decisions_record",
+        "facts_set",
+        "facts_get",
+        "memory_search",
+        # Ephemeral scratch
+        "ephemeral_set",
+        "ephemeral_get",
+    },
+}
+
+def parse_args():
+    p = argparse.ArgumentParser(prog="smrti-mcp")
+    p.add_argument(
+        "--profile",
+        choices=list(PROFILE_TOOLS.keys()),
+        default="full",
+        help="Tool profile: 'full' (all 21 tools) or 'coding' (~10 tools, Antigravity-safe)",
+    )
+    p.add_argument(
+        "--memory-dir",
+        type=Path,
+        default=None,
+        help="Override .memory/ directory path (default: .memory/ in cwd)",
+    )
+    return p.parse_args()
+
 def main():
-    from smrti.mcp_impl import create_server
-    server = create_server()
+    args = parse_args()
+    from smrti.mcp_impl import create_server
+    server = create_server(
+        memory_dir=args.memory_dir,
+        tool_allowlist=PROFILE_TOOLS[args.profile],
+    )
     server.run(transport="stdio")
"""

# ── What create_server() needs to support ───────────────────────────────────
#
# def create_server(
#     memory_dir: Path | None = None,
#     tool_allowlist: set[str] | None = None,
# ) -> FastMCP:
#     mcp = FastMCP("advaita-smrti")
#     memory = Memory(memory_dir or Path(".memory"))
#
#     # Register each tool conditionally:
#     def register(name: str, fn):
#         if tool_allowlist is None or name in tool_allowlist:
#             mcp.tool(name=name)(fn)
#
#     register("memory_status", lambda: memory.status())
#     register("tasks_list",    lambda status=None: memory.tasks.list(status))
#     # ... etc for all 21 tools
#
#     return mcp
#
# Tool count by profile:
#   full    → 21 tools  (current behavior, unchanged)
#   coding  → 10 tools  (fits within Antigravity's 25-tool budget alongside Firebase etc.)
#
# ── mcp_config.json for Antigravity (coding profile) ────────────────────────
ANTIGRAVITY_MCP_CONFIG = {
    "mcpServers": {
        "advaita-smrti": {
            "command": "smrti-mcp",
            "args": ["--profile", "coding"]
        }
    }
}

# ── mcp_config.json for Claude Code (full profile, default) ─────────────────
CLAUDE_CODE_MCP_CONFIG = {
    "mcpServers": {
        "advaita-smrti": {
            "command": "smrti-mcp"
            # no --profile flag = full (all 21 tools)
        }
    }
}

if __name__ == "__main__":
    import json
    print("Antigravity config:")
    print(json.dumps(ANTIGRAVITY_MCP_CONFIG, indent=2))
    print("\nClaude Code config:")
    print(json.dumps(CLAUDE_CODE_MCP_CONFIG, indent=2))
