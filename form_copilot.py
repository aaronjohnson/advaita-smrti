#!/usr/bin/env python3
"""
Form Copilot - Your AI co-pilot for complex paperwork.

A unified CLI for completing multi-section applications with Claude Code integration.

Usage:
    form_copilot.py                          # Interactive mode (default)
    form_copilot.py --db myform.db           # Use specific database
    form_copilot.py export texinfo           # Export current form
    form_copilot.py export pdf --db form.db  # Export specific db to PDF
    form_copilot.py validate config.json     # Validate a config file
    form_copilot.py status                   # Show progress summary
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime


def get_default_paths():
    """Find default database and config paths"""
    config_path = Path('questions_config.json')
    db_path = None

    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            form_name = config.get('form_name', 'form')
            safe_name = form_name.lower().replace(' ', '_').replace('-', '_')
            db_path = Path(f"{safe_name}.db")
        except (json.JSONDecodeError, IOError):
            pass

    return db_path, config_path


def cmd_interactive(args):
    """Launch interactive assistant"""
    from sea_assistant import InteractiveAssistant, select_config_interactive

    # Handle first-run config selection if no config exists
    config_path = Path(args.config) if args.config else Path('questions_config.json')

    if not config_path.exists() and not args.config:
        select_config_interactive()
        config_path = Path('questions_config.json')

    # Determine database path
    db_path = args.db  # May be None, InteractiveAssistant will derive it

    assistant = InteractiveAssistant(
        config_path=config_path if config_path.exists() else None,
        db_path=db_path
    )
    assistant.run()


def cmd_export(args):
    """Export database to various formats"""
    from sea_application_helper import SEAApplicationHelper

    # Resolve paths
    db_path = args.db
    config_path = args.config

    if not db_path:
        db_path, default_config = get_default_paths()
        if not db_path or not db_path.exists():
            # Try to find any .db file
            dbs = list(Path('.').glob('*.db'))
            if dbs:
                db_path = dbs[0]
            else:
                print("Error: No database found. Specify with --db or run interactive mode first.")
                sys.exit(1)

    db_path = Path(db_path)
    if not db_path.exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)

    # Find config if not specified
    if not config_path:
        # Try to find matching config in examples/
        examples = Path('examples')
        if examples.exists():
            configs = list(examples.glob('*_config.json'))
            if configs:
                # Try to match by name
                db_stem = db_path.stem.replace('_', ' ').lower()
                for cfg in configs:
                    try:
                        with open(cfg) as f:
                            data = json.load(f)
                        if data.get('form_name', '').lower().replace(' ', '_').replace('-', '_') in db_path.stem:
                            config_path = cfg
                            break
                    except:
                        pass
                if not config_path:
                    config_path = configs[0]  # Fall back to first found

    if not config_path:
        print("Error: No config found. Specify with --config")
        sys.exit(1)

    config_path = Path(config_path)
    if not config_path.exists():
        print(f"Error: Config not found: {config_path}")
        sys.exit(1)

    print(f"Database: {db_path}")
    print(f"Config: {config_path}")

    # Determine log path (same directory as db)
    log_path = db_path.parent / 'session_log.json'

    helper = SEAApplicationHelper(
        db_path=str(db_path),
        config_path=str(config_path),
        log_path=str(log_path) if log_path.exists() else None
    )

    # Determine output filename
    form_info = helper.get_form_info()
    safe_name = form_info['name'].lower().replace(' ', '_')

    format_type = args.format
    output = args.output

    if format_type == 'pdf':
        # Export to texinfo first, then build PDF
        if not output:
            output = f"{safe_name}.pdf"
        texi_file = f"{safe_name}.texi"

        helper.export_texinfo(texi_file)
        print(f"Exported: {texi_file}")

        # Build PDF
        import subprocess
        result = subprocess.run(
            ['makeinfo', '--pdf', texi_file, '-o', output],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"Built: {output}")
            # Clean up temp files
            for ext in ['.aux', '.log', '.toc']:
                tmp = Path(safe_name + ext)
                if tmp.exists():
                    tmp.unlink()
        else:
            print(f"PDF build failed: {result.stderr}")
            print("Make sure texinfo and TeX are installed.")
            sys.exit(1)

    elif format_type == 'html':
        if not output:
            output = f"{safe_name}.html"
        texi_file = f"{safe_name}.texi"

        helper.export_texinfo(texi_file)

        import subprocess
        result = subprocess.run(
            ['makeinfo', '--html', '--no-split', texi_file, '-o', output],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"Built: {output}")
        else:
            print(f"HTML build failed: {result.stderr}")
            sys.exit(1)

    elif format_type == 'texinfo':
        if not output:
            output = f"{safe_name}.texi"
        helper.export_texinfo(output)
        print(f"Exported: {output}")
        print(f"\nTo build: makeinfo --pdf {output}")

    elif format_type == 'markdown':
        if not output:
            output = f"{safe_name}.md"
        helper.export_markdown(output)
        print(f"Exported: {output}")

    elif format_type == 'json':
        if not output:
            output = f"{safe_name}_answers.json"
        helper.export_answers(output)
        print(f"Exported: {output}")

    helper.close()


def cmd_validate(args):
    """Validate config file(s)"""
    from validate_config import load_config, validate_config, print_results

    if args.all:
        # Validate all configs in examples/
        examples_dir = Path('examples')
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
        config_path = Path(args.config_file)

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


def cmd_status(args):
    """Show progress summary without entering interactive mode"""
    from sea_application_helper import SEAApplicationHelper

    # Resolve paths
    db_path = args.db
    config_path = args.config

    if not db_path:
        db_path, config_path = get_default_paths()
        if not db_path or not Path(db_path).exists():
            dbs = list(Path('.').glob('*.db'))
            if dbs:
                db_path = dbs[0]
            else:
                print("No database found. Run interactive mode first or specify --db")
                sys.exit(1)

    if not config_path:
        config_path = Path('questions_config.json')

    db_path = Path(db_path)
    config_path = Path(config_path)

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        sys.exit(1)

    helper = SEAApplicationHelper(
        db_path=str(db_path),
        config_path=str(config_path) if config_path.exists() else None
    )

    form_info = helper.get_form_info()
    progress = helper.get_progress()

    print(f"\n{'=' * 60}")
    print(f"  {form_info['name']}")
    print(f"{'=' * 60}")
    print(f"\nDatabase: {db_path}")
    print(f"Config: {config_path}")
    print(f"\nProgress: {progress['complete']}/{progress['total']} complete ({progress['percent_complete']:.1f}%)")
    print(f"  - Complete: {progress['complete']}")
    print(f"  - In Progress: {progress['in_progress']}")
    print(f"  - Not Started: {progress['not_started']}")

    # Section breakdown
    print(f"\nBy Section:")
    sections = helper.get_sections()
    for section in sections:
        questions = helper.get_questions_by_section(section['id'])
        complete = sum(1 for q in questions if q.get('status') == 'complete')
        total = len(questions)
        pct = (complete / total * 100) if total > 0 else 0
        bar = '█' * int(pct / 10) + '░' * (10 - int(pct / 10))
        print(f"  {section['title'][:30]:30} [{bar}] {complete}/{total}")

    # Session analysis if available
    analysis = helper.analyze_session_log()
    if analysis:
        print(f"\nSession Activity:")
        print(f"  - Total events: {analysis['total_events']}")
        print(f"  - Claude sessions: {analysis['claude_sessions_total']}")
        print(f"  - Answer revisions: {analysis['total_revisions']}")
        if analysis['first_event']:
            print(f"  - Active: {analysis['first_event'][:10]} to {analysis['last_event'][:10]}")

    print()
    helper.close()


def cmd_list(args):
    """List available configs and databases"""
    print("\nAvailable Configs (examples/):")
    print("-" * 40)
    examples = Path('examples')
    if examples.exists():
        for cfg in sorted(examples.glob('*_config.json')):
            try:
                with open(cfg) as f:
                    data = json.load(f)
                name = data.get('form_name', 'Unknown')
                questions = len(data.get('questions', []))
                print(f"  {cfg.name:35} {name} ({questions} questions)")
            except:
                print(f"  {cfg.name:35} (error reading)")
    else:
        print("  No examples/ directory found")

    print("\nExisting Databases:")
    print("-" * 40)
    dbs = list(Path('.').glob('*.db'))
    if dbs:
        for db in sorted(dbs):
            size = db.stat().st_size
            print(f"  {db.name:35} ({size:,} bytes)")
    else:
        print("  No databases found")

    print()


def main():
    parser = argparse.ArgumentParser(
        description='Form Copilot - Your AI co-pilot for complex paperwork',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                                    # Interactive mode
    %(prog)s --db myform.db --config cfg.json   # Interactive with specific files
    %(prog)s export pdf                         # Export current form to PDF
    %(prog)s export texinfo --db form.db        # Export specific database
    %(prog)s validate examples/my_config.json   # Validate a config
    %(prog)s validate --all                     # Validate all configs
    %(prog)s status                             # Show progress summary
    %(prog)s list                               # List configs and databases
        """
    )

    parser.add_argument('--db', '-d', metavar='PATH',
                        help='Database file path')
    parser.add_argument('--config', '-c', metavar='PATH',
                        help='Config file path')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export to various formats')
    export_parser.add_argument('format', choices=['json', 'markdown', 'texinfo', 'html', 'pdf'],
                               help='Output format')
    export_parser.add_argument('--output', '-o', metavar='PATH',
                               help='Output file path')
    export_parser.add_argument('--db', '-d', metavar='PATH',
                               help='Database file path')
    export_parser.add_argument('--config', '-c', metavar='PATH',
                               help='Config file path')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate config files')
    validate_parser.add_argument('config_file', nargs='?',
                                 help='Config file to validate')
    validate_parser.add_argument('--all', '-a', action='store_true',
                                 help='Validate all configs in examples/')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show progress summary')
    status_parser.add_argument('--db', '-d', metavar='PATH',
                               help='Database file path')
    status_parser.add_argument('--config', '-c', metavar='PATH',
                               help='Config file path')

    # List command
    list_parser = subparsers.add_parser('list', help='List configs and databases')

    args = parser.parse_args()

    if args.command == 'export':
        cmd_export(args)
    elif args.command == 'validate':
        if not args.config_file and not args.all:
            validate_parser.error('Specify a config file or use --all')
        cmd_validate(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'list':
        cmd_list(args)
    else:
        # Default: interactive mode
        cmd_interactive(args)


if __name__ == '__main__':
    main()
