#!/usr/bin/env python3
"""
bench/run_claude.py

Run the smṛti bench prompt battery against Claude Code.

Arms:
  --arm baseline   Fresh session, no memory tools, no fixture injection
  --arm smrti      MCP server running against fixture .memory/

Usage:
  python bench/run_claude.py --arm baseline --out bench/results/
  python bench/run_claude.py --arm smrti    --out bench/results/

Requires:
  - claude CLI in PATH (Claude Code)
  - For --arm smrti: `pip install advaita-smrti[mcp]`
  - ANTHROPIC_API_KEY in environment (claude CLI uses this)
"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / ".memory"
PROMPTS_FILE = Path(__file__).parent / "prompts" / "battery.txt"
SYSTEM_PROMPT = (
    "You are a coding assistant with access to project memory tools. "
    "Use them to answer questions about this project accurately. "
    "If a fact is not in memory, say so — do not guess."
)


def parse_battery(prompts_file: Path) -> list[dict]:
    """Parse the prompt battery into structured entries."""
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


def run_claude_headless(
    prompt: str,
    mcp_config: Path | None = None,
    run_dir: Path | None = None,
) -> str:
    """
    Run a single prompt through claude CLI in headless mode.

    run_dir: working directory for the claude process. Should be an isolated
    temp dir containing only the fixture .memory/ so Claude does not read
    the real project codebase and answer about it instead of the fixture.
    """
    MODEL = "claude-sonnet-4-6"
    cmd = ["claude", "--print", "--model", MODEL]
    if mcp_config:
        cmd += ["--mcp-config", str(mcp_config)]
    cmd += ["-p", prompt]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # MCP arm can be slow — 5 min ceiling
        cwd=str(run_dir) if run_dir else None,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr}")
    return result.stdout.strip()


def build_mcp_config() -> dict:
    """Generate mcp_config.json for smṛti (finds .memory/ in cwd via symlink)."""
    return {
        "mcpServers": {
            "advaita-smrti": {
                "command": "smrti-mcp",
                "args": [],
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Run smṛti bench against Claude Code")
    parser.add_argument(
        "--arm",
        choices=["baseline", "smrti"],
        required=True,
        help="Which bench arm to run",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("bench/results"),
        help="Output directory for results JSON",
    )
    args = parser.parse_args()

    if not shutil.which("claude"):
        sys.exit("ERROR: 'claude' CLI not found in PATH. Install Claude Code first.")

    prompts = parse_battery(PROMPTS_FILE)
    results = []

    mcp_config_path = None
    tmp_dir = None

    # Run from an empty temp dir so Claude has no codebase to read.
    # The MCP server points at the fixture by absolute path — no copy needed.
    tmp_dir = tempfile.mkdtemp(prefix="smrti-bench-")
    run_dir = Path(tmp_dir)
    print(f"Isolated run dir: {run_dir}")

    if args.arm == "smrti":
        # Symlink fixture into run_dir so smrti-mcp finds .memory/ at default path
        memory_link = run_dir / ".memory"
        memory_link.symlink_to(FIXTURE_DIR.resolve())
        print(f"smṛti arm: .memory → {FIXTURE_DIR} (symlink)")
        mcp_config_path = run_dir / "mcp_config.json"
        mcp_config = build_mcp_config()
        mcp_config_path.write_text(json.dumps(mcp_config, indent=2))
        print(f"smṛti arm: MCP config → {mcp_config_path}")

    try:
        for p in prompts:
            print(f"  Running {p['id']}...", end=" ", flush=True)
            t0 = time.monotonic()
            try:
                response = run_claude_headless(
                    p["text"],
                    mcp_config=mcp_config_path,
                    run_dir=run_dir,
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
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    args.out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = args.out / f"claude_{args.arm}_{ts}.json"
    out_file.write_text(
        json.dumps(
            {
                "platform": "claude_code",
                "model": "claude-sonnet-4-6",
                "arm": args.arm,
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
