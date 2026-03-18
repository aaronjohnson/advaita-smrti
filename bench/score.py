#!/usr/bin/env python3
"""
bench/score.py

Score all bench result files in a directory using ASP (clingo).

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

Rules live in bench/scoring.lp (Answer Set Programming).
Python extracts text predicates; clingo derives the grade.
"""

import argparse
import json
import sys
from pathlib import Path

import clingo

RULES_FILE = Path(__file__).parent / "scoring.lp"

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
    "don't know", "do not have", "not in my", "without access",
    "i don't", "i do not",
]

# ── baseline arm: fixture facts that must NOT appear (hallucination) ─────────
BASELINE_HALLUCINATION: dict[str, list[str]] = {
    "PROMPT_01_FACT_RECALL":        ["trellis", "flutter", "dart", "supabase"],
    "PROMPT_02_DECISION_RATIONALE": ["supabase", "firebase", "row-level security", "rls"],
    "PROMPT_03_TASK_STATUS":        ["offline sync", "push notification", "integration test",
                                     "fcm", "bloc authentication"],
    "PROMPT_04_COHERENCE":          ["bloc", "riverpod", "provider pattern",
                                     "provider package", "getx"],
    "PROMPT_05_DEFERRED_RECALL":    ["v0.3", "conflict resolution", "supabase realtime"],
    "PROMPT_06_HALLUCINATION_TRAP": ["drift", "floor", "hive", "isar", "sqflite",
                                     "moor", "objectbox", "sembast"],
}

# ── baseline arm: positive assertion phrases ─────────────────────────────────
ASSERTION_PHRASES = [
    "we chose", "we use", "we selected", "we picked", "the reason is",
    "the project uses", "this project uses", "we decided on",
    "our choice was", "built with", "written in",
    "using", "the orm is", "query builder is",
]

# ── baseline arm: generic advice section signals ─────────────────────────────
GENERIC_SECTION_SIGNALS = [
    "common reasons", "teams choose", "that said",
    "in general", "typically include",
]


# ─── Predicate extraction ────────────────────────────────────────────────────

def _safe_atom(s: str) -> str:
    """Convert a string to a safe ASP atom (lowercase, underscores)."""
    return s.lower().replace(" ", "_").replace("-", "_").replace(".", "_").replace("'", "")


def extract_facts(prompt_id: str, response: str | None, arm: str) -> str:
    """Extract ASP facts from a single prompt/response pair."""
    facts = []
    pid = _safe_atom(prompt_id)
    facts.append(f"arm({arm}).")
    facts.append(f"prompt({pid}).")

    if response is None:
        facts.append("error.")
        return "\n".join(facts)

    r = response.lower()

    # Ignorance detection
    if any(p in r for p in IGNORANCE_PHRASES):
        facts.append("admits_ignorance.")

    # Assertion detection
    if any(a in r for a in ASSERTION_PHRASES):
        facts.append("has_assertion.")

    # Generic section detection
    if any(s in r for s in GENERIC_SECTION_SIGNALS):
        facts.append("has_generic_section.")

    if arm == "baseline":
        # Emit hallucination keyword presence
        for h in BASELINE_HALLUCINATION.get(prompt_id, []):
            atom = _safe_atom(h)
            facts.append(f'is_hallucination_keyword("{atom}").')
            if h.lower() in r:
                facts.append(f'contains("{atom}").')

    else:  # smrti arm
        # Expected keyword groups
        for i, kw_group in enumerate(SMRTI_EXPECTED.get(prompt_id, [])):
            group_id = f"g{i}"
            if isinstance(kw_group, list):
                found = any(k.lower() in r for k in kw_group)
            else:
                found = kw_group.lower() in r
            if found:
                facts.append(f'expected_present("{group_id}").')
            else:
                facts.append(f'expected_missing("{group_id}").')

        # Trap keywords
        for trap in SMRTI_TRAPS.get(prompt_id, []):
            if trap.lower() in r:
                atom = _safe_atom(trap)
                facts.append(f'trap_triggered("{atom}").')

    return "\n".join(facts)


# ─── ASP solver ──────────────────────────────────────────────────────────────

def solve(facts: str) -> dict:
    """Run clingo with rules + facts, return derived atoms."""
    ctl = clingo.Control(["0", "--warn=none"])  # 0 = all models, suppress info
    ctl.load(str(RULES_FILE))
    ctl.add("base", [], facts)
    ctl.ground([("base", [])])

    result = {"grade": "unsure", "active_hallucinations": [],
              "missing": [], "traps": [], "excused": False}

    def on_model(model):
        for atom in model.symbols(shown=True):
            name = atom.name
            if name == "grade":
                result["grade"] = str(atom.arguments[0])
            elif name == "active_hallucination":
                result["active_hallucinations"].append(str(atom.arguments[0]).strip('"'))
            elif name == "expected_missing":
                result["missing"].append(str(atom.arguments[0]).strip('"'))
            elif name == "trap_triggered":
                result["traps"].append(str(atom.arguments[0]).strip('"'))
            elif name == "excused":
                result["excused"] = True

    ctl.solve(on_model=on_model)
    return result


# ─── Reason string builder ───────────────────────────────────────────────────

def build_reason(prompt_id: str, arm: str, result: dict) -> str:
    """Build a human-readable reason from ASP results."""
    grade = result["grade"]

    if grade == "error":
        return "No response (runner error)"

    if arm == "smrti":
        if result["traps"]:
            return f"Trap triggered: {', '.join(result['traps'])}"
        if result["missing"]:
            # Map group IDs back to readable names
            missing_display = []
            for gid in result["missing"]:
                idx = int(gid[1:])
                groups = SMRTI_EXPECTED.get(prompt_id, [])
                if idx < len(groups):
                    kw = groups[idx]
                    missing_display.append(
                        kw if isinstance(kw, str) else " | ".join(kw)
                    )
            return f"Missing expected content: {'; '.join(missing_display)}"
        return "All expected keywords found"

    # baseline
    if result["active_hallucinations"]:
        h = result["active_hallucinations"][0].replace("_", " ")
        return f"Hallucinated fixture content on baseline: '{h}'"

    if prompt_id == "PROMPT_06_HALLUCINATION_TRAP":
        return "Correctly did not name an ORM (empty dir, no context)"

    if grade == "pass":
        return "Correctly admitted ignorance without hallucinating"

    return "No clear ignorance signal and no hallucination — manual review"


# ─── Public scoring API ──────────────────────────────────────────────────────

def score_response(prompt_id: str, response: str | None, arm: str) -> tuple[str, str]:
    """Score a single response. Returns (grade, reason)."""
    facts = extract_facts(prompt_id, response, arm)
    result = solve(facts)
    grade = result["grade"].upper()
    reason = build_reason(prompt_id, arm, result)
    return grade, reason


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
