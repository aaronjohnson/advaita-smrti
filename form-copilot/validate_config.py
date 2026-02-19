#!/usr/bin/env python3
"""
Validate a form-copilot configuration file.

Checks:
1. JSON structure (via schema)
2. Unique question IDs
3. Valid section_id references
4. Valid depends_on references
5. Section ID gaps/duplicates

Usage:
    python3 validate_config.py examples/college_app_config.json
    python3 validate_config.py --all  # validate all examples
"""

import json
import sys
from pathlib import Path


def load_config(path):
    """Load and parse a config file."""
    with open(path, 'r') as f:
        return json.load(f)


def validate_config(config, filename="config"):
    """Validate a config dict. Returns (is_valid, errors)."""
    errors = []
    warnings = []

    # Check required top-level fields
    for field in ['form_name', 'sections', 'questions']:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors, warnings

    # Extract IDs
    section_ids = set()
    question_ids = set()

    # Validate sections
    for i, section in enumerate(config.get('sections', [])):
        if 'id' not in section:
            errors.append(f"Section {i} missing 'id'")
            continue

        sid = section['id']
        if sid in section_ids:
            errors.append(f"Duplicate section ID: {sid}")
        section_ids.add(sid)

        if 'title' not in section:
            errors.append(f"Section {sid} missing 'title'")

    # Check for section ID gaps
    if section_ids:
        expected = set(range(1, max(section_ids) + 1))
        gaps = expected - section_ids
        if gaps:
            warnings.append(f"Section ID gaps: {sorted(gaps)}")

    # Validate questions
    for i, q in enumerate(config.get('questions', [])):
        if 'id' not in q:
            errors.append(f"Question {i} missing 'id'")
            continue

        qid = q['id']

        # Check duplicate IDs
        if qid in question_ids:
            errors.append(f"Duplicate question ID: {qid}")
        question_ids.add(qid)

        # Check section_id reference
        if 'section_id' not in q:
            errors.append(f"Question {qid} missing 'section_id'")
        elif q['section_id'] not in section_ids:
            errors.append(f"Question {qid} references invalid section_id: {q['section_id']}")

        # Check question_text
        if not q.get('question_text'):
            errors.append(f"Question {qid} missing or empty 'question_text'")

        # Check depends_on reference
        depends = q.get('depends_on')
        if depends and depends not in question_ids:
            # depends_on might reference a later question, defer check
            pass

    # Second pass: check depends_on references
    for q in config.get('questions', []):
        depends = q.get('depends_on')
        if depends and depends not in question_ids:
            errors.append(f"Question {q['id']} depends_on invalid question: {depends}")

    # Check priority values
    for q in config.get('questions', []):
        priority = q.get('priority')
        if priority is not None and priority not in [1, 2, 3]:
            warnings.append(f"Question {q['id']} has unusual priority: {priority}")

    # Check question_type values
    valid_types = {'text', 'long_text', 'yes_no', 'number', 'choice'}
    for q in config.get('questions', []):
        qtype = q.get('question_type')
        if qtype and qtype not in valid_types:
            warnings.append(f"Question {q['id']} has unknown type: {qtype}")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def print_results(filename, is_valid, errors, warnings):
    """Print validation results."""
    status = "VALID" if is_valid else "INVALID"
    print(f"\n{filename}: {status}")
    print("-" * 50)

    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if is_valid and not warnings:
        print("  No issues found.")

    return is_valid


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_config.py <config.json>")
        print("       python3 validate_config.py --all")
        sys.exit(1)

    if sys.argv[1] == '--all':
        # Validate all configs in examples/
        examples_dir = Path(__file__).parent / 'examples'
        configs = list(examples_dir.glob('*_config.json'))

        if not configs:
            print("No config files found in examples/")
            sys.exit(1)

        all_valid = True
        for config_path in sorted(configs):
            try:
                config = load_config(config_path)
                is_valid, errors, warnings = validate_config(config, config_path.name)
                if not print_results(config_path.name, is_valid, errors, warnings):
                    all_valid = False
            except json.JSONDecodeError as e:
                print(f"\n{config_path.name}: INVALID JSON")
                print(f"  - Parse error: {e}")
                all_valid = False

        print("\n" + "=" * 50)
        print(f"Overall: {'ALL VALID' if all_valid else 'SOME INVALID'}")
        sys.exit(0 if all_valid else 1)

    else:
        # Validate single config
        config_path = Path(sys.argv[1])

        if not config_path.exists():
            print(f"File not found: {config_path}")
            sys.exit(1)

        try:
            config = load_config(config_path)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            sys.exit(1)

        is_valid, errors, warnings = validate_config(config, config_path.name)
        print_results(config_path.name, is_valid, errors, warnings)

        # Summary
        sections = len(config.get('sections', []))
        questions = len(config.get('questions', []))
        print(f"\nSummary: {sections} sections, {questions} questions")

        sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
