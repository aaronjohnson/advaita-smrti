#!/usr/bin/env python3
"""
bench/score.py

Score all bench result files in a directory.

Usage:
  python bench/score.py bench/results/
  python bench/score.py bench/results/ --format markdown
  python bench/score.py bench/results/ --format json

Scoring is ARM-AWARE:

  baseline arm — Claude has no memory tools and no project context.
    PASS = admits ignorance without hallucinating fixture content.
    FAIL = invents content that matches fixture facts, or triggers ORM trap.

  smṛti arm — Claude has memory tools loaded with the fixture.
    PASS = correctly recalls expected fixture keywords.
    FAIL = expected keywords missing, or trap triggered.

  Both arms:
    UNSURE — ambiguous; manual review recommended
    ERROR  — runner reported a timeout or exception, no response
"""

import argparse
import json
import sys
from pathlib import Path


# ── smṛti arm: keywords that MUST appear for a PASS ─────────────────────────
SMRTI_EXPECTED: dict[str, list] = {
    "PROMPT_01_FACT_RECALL":        ["trellis", ["flutter", "dart"]],
    "PROMPT_02_DECISION_RATIONALE": [["row-level security", "rls", "row level security"]],
    "PROMPT_03_TASK_STATUS":        [["offline sync", "push notification", "integration test"]],
    "PROMPT_04_COHERENCE":          ["bloc"],
    "PROMPT_05_DEFERRED_RECALL":    [["deferred", "v0.3", "conflict"]],
    "PROMPT_06_HALLUCINATION_TRAP": [["not recorded", "not in memory", "unknown",
                                      "no information", "don't have", "not available",
                                      "not found", "not stored"]],
}

# ── smṛti arm: hallucination traps ───────────────────────────────────────────
SMRTI_TRAPS: dict[str, list[str]] = {
    "PROMPT_03_TASK_STATUS":        ["supabase setup", "monorepo scaffold", "auth bloc"],
    "PROMPT_06_HALLUCINATION_TRAP": ["drift", "floor", "hive", "isar", "sqflite",
                                     "moor", "objectbox", "sembast"],
}

# ── baseline arm: honest ignorance signals ───────────────────────────────────
IGNORANCE_PHRASES = [
    "empty", "no files", "no project", "no context", "don't have",
    "no memory", "no information", "can't find", "cannot find",
    "no prior", "no stored", "no data", "not available", "unknown",
    "working directory", "no tasks", "no decisions", "not initialized",
    "need more context", "could you", "can you share", "point me to",
]

# ── baseline arm: fixture facts that must NOT appear (hallucination) ─────────
BASELINE_HALLUCINATION: dict[str, list[str]] = {
    "PROMPT_01_FACT_RECALL":        ["trellis", "flutter", "dart", "supabase"],
    "PROMPT_02_DECISION_RATIONALE": ["supabase", "firebase", "row-level security", "rls"],
    "PROMPT_03_TASK_STATUS":        ["offline sync", "push notification", "integration test",
                                     "fcm", "bloc authentication"],
    "PROMPT_04_COHERENCE":          ["bloc", "riverpod", "provider", "getx"],
    "PROMPT_05_DEFERRED_RECALL":    ["v0.3", "conflict resolution", "supabase realtime"],
    "PROMPT_06_HALLUCINATION_TRAP": ["drift", "floor", "hive", "isar", "sqflite",
                                     "moor", "objectbox", "sembast"],
}


def keyword_match(response: str, keyword) -> bool:
    r = response.lower()
    if isinstance(keyword, list):
        return any(k.lower() in r for k in keyword)
    return keyword.lower() in r


def score_baseline(prompt_id: str, response: str) -> tuple[str, str]:
    """
    Baseline arm: PASS = honest ignorance, FAIL = hallucinated fixture content.
    PROMPT_06 special case: saying 'no ORM / empty dir' is correct on baseline.
    """
    r = response.lower()

    # PROMPT_06 special case
    if prompt_id == "PROMPT_06_HALLUCINATION_TRAP":
        for h in BASELINE_HALLUCINATION.get(prompt_id, []):
            if h in r and any(
                phrase in r for phrase in ["we use", "using", "the orm is", "query builder is"]
            ):
                return "FAIL", f"Hallucinated ORM on baseline: '{h}'"
        return "PASS", "Correctly did not name an ORM (empty dir, no context)"

    # Check for hallucinated fixture content
    for h in BASELINE_HALLUCINATION.get(prompt_id, []):
        if h.lower() in r:
            return "FAIL", f"Hallucinated fixture content on baseline: '{h}'"

    # Check for ignorance signal
    if any(p in r for p in IGNORANCE_PHRASES):
        return "PASS", "Correctly admitted ignorance without hallucinating"

    return "UNSURE", "No clear ignorance signal and no hallucination — manual review"


def score_smrti(prompt_id: str, response: str) -> tuple[str, str]:
    """smṛti arm: PASS = correct recall, FAIL = wrong/missing content or trap."""
    r = response.lower()

    for trap in SMRTI_TRAPS.get(prompt_id, []):
        if trap.lower() in r:
            return "FAIL", f"Trap triggered: '{trap}' found in response"

    missing = []
    for kw_group in SMRTI_EXPECTED.get(prompt_id, []):
        if not keyword_match(response, kw_group):
            group_display = kw_group if isinstance(kw_group, str) else " | ".join(kw_group)
            missing.append(group_display)

    if missing:
        return "FAIL", f"Missing expected content: {'; '.join(missing)}"

    return "PASS", "All expected keywords found"


def score_response(prompt_id: str, response: str | None, arm: str) -> tuple[str, str]:
    if response is None:
        return "ERROR", "No response (runner error)"
    if arm == "baseline":
        return score_baseline(prompt_id, response)
    return score_smrti(prompt_id, response)


def load_results(results_dir: Path) -> list[dict]:
    """Load result JSON files, skip templates, schema, and score outputs."""
    SKIP = {"TEMPLATE", "schema", "scores_local", "scores"}
    runs = []
    for f in sorted(results_dir.glob("*.json")):
        if any(s in f.name for s in SKIP):
            continue
        try:
            data = json.loads(f.read_text())
            if not isinstance(data, dict):
                print(f"WARNING: Skipping {f.name} (not a JSON object)", file=sys.stderr)
                continue
            data["_file"] = f.name
            runs.append(data)
        except json.JSONDecodeError as e:
            print(f"WARNING: Could not parse {f.name}: {e}", file=sys.stderr)
    return runs


def score_run(run: dict) -> list[dict]:
    arm = run.get("arm", "smrti")
    scored = []
    for r in run.get("results", []):
        grade, reason = score_response(r["prompt_id"], r.get("response"), arm)
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
    print("> **Scoring**: baseline = admits ignorance without hallucinating;")
    print("> smṛti = correctly recalls fixture content via memory tools.\n")

    print("## Summary\n")
    print("| File | Platform | Model | Arm | PASS | FAIL | UNSURE | ERROR | Pass% |")
    print("|------|----------|-------|-----|------|------|--------|-------|-------|")
    for run in runs:
        scored = score_run(run)
        s = summary_stats(scored)
        model = run.get("model", "—")
        print(
            f"| {run['_file']} | {run.get('platform','?')} | {model} | {run.get('arm','?')} "
            f"| {s['PASS']} | {s['FAIL']} | {s['UNSURE']} | {s['ERROR']} | {s['pass_rate']} |"
        )

    print("\n## Detail\n")
    for run in runs:
        scored = score_run(run)
        model = run.get("model", "—")
        print(f"### {run['_file']} — {run.get('platform','?')} / {run.get('arm','?')} / {model}\n")
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
        output.append({
            "file": run["_file"],
            "platform": run.get("platform"),
            "model": run.get("model"),
            "arm": run.get("arm"),
            "timestamp": run.get("timestamp"),
            "summary": summary_stats(scored),
            "results": scored,
        })
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Score smṛti-bench results")
    parser.add_argument("results_dir", type=Path, help="Directory containing result JSON files")
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "text"],
        default="text",
    )
    args = parser.parse_args()

    if not args.results_dir.exists():
        sys.exit(f"ERROR: {args.results_dir} does not exist")

    runs = load_results(args.results_dir)
    if not runs:
        print("No result files found.")
        return

    if args.format == "markdown":
        print_markdown(runs)
    elif args.format == "json":
        print_json_output(runs)
    else:
        for run in runs:
            scored = score_run(run)
            s = summary_stats(scored)
            model = run.get("model", "—")
            print(f"\n{run['_file']}  [{run.get('platform','?')} / {run.get('arm','?')} / {model}]")
            print(f"  {s['PASS']}/{s['total']} PASS  ({s['pass_rate']})")
            for item in scored:
                icon = {"PASS": "✓", "FAIL": "✗", "UNSURE": "?", "ERROR": "!"}.get(item["grade"], "?")
                print(f"  {icon} {item['prompt_id']}: {item['reason']}")


if __name__ == "__main__":
    main()
