#!/usr/bin/env python3
"""
bench/score.py

Score all bench result files in a directory.

Usage:
  python bench/score.py bench/results/
  python bench/score.py bench/results/ --format markdown
  python bench/score.py bench/results/ --format json

Scoring rules per prompt:
  PASS   — response contains expected keywords, no trap triggered
  FAIL   — expected keywords missing, or trap triggered
  UNSURE — ambiguous; manual review recommended
  ERROR  — runner reported an error, no response
"""

import argparse
import json
import sys
from pathlib import Path


# Keyword sets that must appear (case-insensitive) for a PASS
EXPECTED_KEYWORDS: dict[str, list[str]] = {
    "PROMPT_01_FACT_RECALL": ["trellis", ["flutter", "dart"]],
    "PROMPT_02_DECISION_RATIONALE": [["row-level security", "rls", "row level security"]],
    "PROMPT_03_TASK_STATUS": [["offline sync", "push notification", "integration test"]],
    "PROMPT_04_COHERENCE": ["bloc"],
    "PROMPT_05_DEFERRED_RECALL": [["deferred", "v0.3", "conflict"]],
    "PROMPT_06_HALLUCINATION_TRAP": [
        ["not recorded", "not in memory", "unknown", "no information", "don't have", "not available", "not found"]
    ],
}

# Words that, if present in a response, indicate a trap was triggered
TRAP_WORDS: dict[str, list[str]] = {
    "PROMPT_03_TASK_STATUS": ["supabase setup", "monorepo scaffold", "auth bloc"],
    "PROMPT_04_COHERENCE": [],  # Nuanced — score as UNSURE if BLoC missing
    "PROMPT_06_HALLUCINATION_TRAP": ["drift", "floor", "hive", "isar", "sqflite", "moor", "objectbox"],
}


def keyword_match(response: str, keyword) -> bool:
    """Check if a keyword (str) or any keyword in a list matches the response."""
    r = response.lower()
    if isinstance(keyword, list):
        return any(k.lower() in r for k in keyword)
    return keyword.lower() in r


def score_response(prompt_id: str, response: str | None) -> tuple[str, str]:
    """
    Returns (grade, reason) where grade is PASS/FAIL/UNSURE/ERROR.
    """
    if response is None:
        return "ERROR", "No response (runner error)"

    r = response.lower()
    expected = EXPECTED_KEYWORDS.get(prompt_id, [])
    traps = TRAP_WORDS.get(prompt_id, [])

    # Check trap first
    for trap in traps:
        if trap.lower() in r:
            return "FAIL", f"Trap triggered: '{trap}' found in response"

    # Check all expected keyword groups
    missing = []
    for kw_group in expected:
        if not keyword_match(response, kw_group):
            group_display = kw_group if isinstance(kw_group, str) else " | ".join(kw_group)
            missing.append(group_display)

    if missing:
        return "FAIL", f"Missing expected content: {'; '.join(missing)}"

    # Hallucination trap special case: if keywords found but also named a specific ORM
    if prompt_id == "PROMPT_06_HALLUCINATION_TRAP":
        orm_names = ["drift", "floor", "hive", "isar", "sqflite", "moor", "objectbox", "sembast"]
        for orm in orm_names:
            if orm in r:
                return "FAIL", f"Hallucinated ORM: '{orm}'"

    return "PASS", "All expected keywords found"


def load_results(results_dir: Path) -> list[dict]:
    """Load all result JSON files, skip templates and schema."""
    runs = []
    for f in sorted(results_dir.glob("*.json")):
        if "TEMPLATE" in f.name or "schema" in f.name:
            continue
        try:
            data = json.loads(f.read_text())
            data["_file"] = f.name
            runs.append(data)
        except json.JSONDecodeError as e:
            print(f"WARNING: Could not parse {f.name}: {e}", file=sys.stderr)
    return runs


def score_run(run: dict) -> list[dict]:
    scored = []
    for r in run.get("results", []):
        grade, reason = score_response(r["prompt_id"], r.get("response"))
        scored.append({**r, "grade": grade, "reason": reason})
    return scored


def summary_stats(scored: list[dict]) -> dict:
    grades = [s["grade"] for s in scored]
    total = len(grades)
    return {
        "total": total,
        "PASS": grades.count("PASS"),
        "FAIL": grades.count("FAIL"),
        "UNSURE": grades.count("UNSURE"),
        "ERROR": grades.count("ERROR"),
        "pass_rate": f"{grades.count('PASS') / total * 100:.0f}%" if total else "N/A",
    }


def print_markdown(runs: list[dict]) -> None:
    print("# smṛti-bench Results\n")

    # Summary table
    print("## Summary\n")
    print("| File | Platform | Arm | PASS | FAIL | UNSURE | ERROR | Pass% |")
    print("|------|----------|-----|------|------|--------|-------|-------|")
    for run in runs:
        scored = score_run(run)
        s = summary_stats(scored)
        print(
            f"| {run['_file']} | {run.get('platform','?')} | {run.get('arm','?')} "
            f"| {s['PASS']} | {s['FAIL']} | {s['UNSURE']} | {s['ERROR']} | {s['pass_rate']} |"
        )

    # Detail per run
    print("\n## Detail\n")
    for run in runs:
        scored = score_run(run)
        print(f"### {run['_file']} — {run.get('platform','?')} / {run.get('arm','?')}\n")
        for s in scored:
            icon = {"PASS": "✅", "FAIL": "❌", "UNSURE": "🟡", "ERROR": "💥"}.get(s["grade"], "?")
            print(f"{icon} **{s['prompt_id']}** — {s['reason']}")
            if s.get("response"):
                preview = s["response"][:200].replace("\n", " ")
                print(f"   > {preview}{'…' if len(s['response']) > 200 else ''}")
        print()


def print_json_output(runs: list[dict]) -> None:
    output = []
    for run in runs:
        scored = score_run(run)
        output.append(
            {
                "file": run["_file"],
                "platform": run.get("platform"),
                "arm": run.get("arm"),
                "timestamp": run.get("timestamp"),
                "summary": summary_stats(scored),
                "results": scored,
            }
        )
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Score smṛti-bench results")
    parser.add_argument("results_dir", type=Path, help="Directory containing result JSON files")
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "text"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args()

    if not args.results_dir.exists():
        sys.exit(f"ERROR: {args.results_dir} does not exist")

    runs = load_results(args.results_dir)
    if not runs:
        print("No result files found (templates and schema files are skipped).")
        return

    if args.format == "markdown":
        print_markdown(runs)
    elif args.format == "json":
        print_json_output(runs)
    else:
        # Plain text summary
        for run in runs:
            scored = score_run(run)
            s = summary_stats(scored)
            print(f"\n{run['_file']}  [{run.get('platform','?')} / {run.get('arm','?')}]")
            print(f"  {s['PASS']}/{s['total']} PASS  ({s['pass_rate']})")
            for item in scored:
                icon = {"PASS": "✓", "FAIL": "✗", "UNSURE": "?", "ERROR": "!"}.get(item["grade"], "?")
                print(f"  {icon} {item['prompt_id']}: {item['reason']}")


if __name__ == "__main__":
    main()
