#!/usr/bin/env python3
"""
bench/run_gemini.py

Run the smṛti bench prompt battery against Gemini API.

This runner bridges smṛti's MCP server to Gemini's function calling API,
validating that the memory layer works across model providers.

Usage:
  python bench/run_gemini.py --out bench/results/

Requires:
  pip install google-generativeai mcp advaita-smrti[mcp]
  GEMINI_API_KEY in environment
"""

import asyncio
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / ".memory"
PROMPTS_FILE = Path(__file__).parent / "prompts" / "battery.txt"

SYSTEM_INSTRUCTION = (
    "You are a coding assistant with access to project memory tools. "
    "Use them to answer questions about this project accurately. "
    "If a fact is not in memory, say so — do not guess or invent details."
)


def parse_battery(prompts_file: Path) -> list[dict]:
    """Parse the prompt battery (shared with run_claude.py)."""
    prompts = []
    current = {}
    for line in prompts_file.read_text().splitlines():
        if line.startswith("PROMPT_"):
            if current:
                prompts.append(current)
            current = {"id": line.strip(), "text": "", "expect": "", "trap": ""}
        elif line.startswith("EXPECT:"):
            current["expect"] = line[7:].strip()
        elif line.startswith("TRAP:"):
            current["trap"] = line[5:].strip()
        elif line.startswith("---"):
            continue
        elif current and not line.startswith(("EXPECT:", "TRAP:")):
            current["text"] = (current.get("text", "") + " " + line).strip()
    if current:
        prompts.append(current)
    return prompts


async def load_mcp_tools(memory_dir: Path) -> tuple[list, object]:
    """
    Spin up the smṛti MCP server via stdio and collect its tool definitions.
    Returns (gemini_tools, mcp_session) for use in function calling.
    """
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        import google.generativeai as genai
    except ImportError:
        sys.exit(
            "ERROR: Missing dependencies.\n"
            "Run: pip install google-generativeai mcp advaita-smrti[mcp]"
        )

    server_params = StdioServerParameters(
        command="smrti-mcp",
        args=["--profile", "coding", "--memory-dir", str(memory_dir)],
        env=None,
    )

    # We return the session so the caller can keep it alive during tool calls
    # Caller is responsible for __aenter__/__aexit__
    return server_params


async def run_with_gemini(
    prompt_text: str,
    memory_dir: Path,
    api_key: str,
) -> str:
    """
    Run a single prompt through Gemini with smṛti MCP tools wired in.

    Strategy: load MCP tool schemas once, bridge tool calls back to the
    MCP server during Gemini's function calling loop.
    """
    try:
        import google.generativeai as genai
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        sys.exit("ERROR: pip install google-generativeai mcp advaita-smrti[mcp]")

    genai.configure(api_key=api_key)

    server_params = StdioServerParameters(
        command="smrti-mcp",
        args=["--profile", "coding", "--memory-dir", str(memory_dir)],
        env=None,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools_response = await session.list_tools()
            mcp_tools = mcp_tools_response.tools

            # Convert MCP tool schemas → Gemini function declarations
            gemini_tools = []
            for t in mcp_tools:
                fn_decl = {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema if t.inputSchema else {"type": "object", "properties": {}},
                }
                gemini_tools.append(fn_decl)

            MODEL = "gemini-3-pro"
            model = genai.GenerativeModel(
                model_name=MODEL,
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[{"function_declarations": gemini_tools}] if gemini_tools else [],
            )

            chat = model.start_chat()
            response = chat.send_message(prompt_text)

            # Agentic loop: handle function calls until model returns text
            max_turns = 10
            turns = 0
            while turns < max_turns:
                turns += 1
                fn_calls = [
                    part.function_call
                    for candidate in response.candidates
                    for part in candidate.content.parts
                    if hasattr(part, "function_call") and part.function_call.name
                ]
                if not fn_calls:
                    break

                # Execute each function call via MCP server
                fn_responses = []
                for fn_call in fn_calls:
                    tool_args = dict(fn_call.args) if fn_call.args else {}
                    mcp_result = await session.call_tool(fn_call.name, tool_args)
                    content_text = (
                        mcp_result.content[0].text
                        if mcp_result.content
                        else ""
                    )
                    fn_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fn_call.name,
                                response={"result": content_text},
                            )
                        )
                    )

                response = chat.send_message(fn_responses)

            # Extract final text response
            text_parts = [
                part.text
                for candidate in response.candidates
                for part in candidate.content.parts
                if hasattr(part, "text") and part.text
            ]
            return "\n".join(text_parts).strip()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run smṛti bench against Gemini API")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("bench/results"),
        help="Output directory for results JSON",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY environment variable not set.")

    if not shutil.which("smrti-mcp"):
        sys.exit("ERROR: 'smrti-mcp' not found in PATH. Run: pip install advaita-smrti[mcp]")

    prompts = parse_battery(PROMPTS_FILE)
    results = []

    for p in prompts:
        print(f"  Running {p['id']}...", end=" ", flush=True)
        t0 = time.monotonic()
        try:
            response = asyncio.run(
                run_with_gemini(p["text"], FIXTURE_DIR, api_key)
            )
            elapsed = time.monotonic() - t0
            print(f"OK ({elapsed:.1f}s)")
            results.append(
                {
                    "prompt_id": p["id"],
                    "prompt_text": p["text"],
                    "expect": p["expect"],
                    "trap": p["trap"],
                    "response": response,
                    "elapsed_s": round(elapsed, 2),
                    "error": None,
                }
            )
        except Exception as e:
            elapsed = time.monotonic() - t0
            print(f"ERROR ({e})")
            results.append(
                {
                    "prompt_id": p["id"],
                    "prompt_text": p["text"],
                    "expect": p["expect"],
                    "trap": p["trap"],
                    "response": None,
                    "elapsed_s": round(elapsed, 2),
                    "error": str(e),
                }
            )

    args.out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = args.out / f"gemini_smrti_{ts}.json"
    out_file.write_text(
        json.dumps(
            {
                "platform": "gemini_api",
                "model": "gemini-3-pro",
                "arm": "smrti",
                "timestamp": ts,
                "fixture": str(FIXTURE_DIR),
                "results": results,
            },
            indent=2,
        )
    )
    print(f"\nResults written to {out_file}")


if __name__ == "__main__":
    main()
