#!/usr/bin/env python3
"""
Export form-copilot databases to Markdown or Texinfo format.

Usage:
    python3 export_docs.py                     # Export current form to markdown
    python3 export_docs.py --format texinfo    # Export to texinfo
    python3 export_docs.py --all               # Export all databases
    python3 export_docs.py --combine           # Combine all into one document
    python3 export_docs.py db1.db db2.db       # Export specific databases

Output formats:
    markdown (default) - Good for viewing on GitHub, simple editing
    texinfo            - Build to PDF, HTML, or Info with makeinfo
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from sea_application_helper import SEAApplicationHelper


def find_databases():
    """Find all .db files in the current directory"""
    return sorted(Path('.').glob('*.db'))


def export_single(db_path, format='markdown'):
    """Export a single database"""
    helper = SEAApplicationHelper(db_path=str(db_path))

    if format == 'markdown':
        filepath = helper.export_markdown()
    elif format == 'texinfo':
        filepath = helper.export_texinfo()
    else:
        raise ValueError(f"Unknown format: {format}")

    helper.close()
    return filepath


def combine_markdown(db_paths, output_path="combined_export.md"):
    """Combine multiple databases into a single Markdown document"""
    lines = []
    lines.append("# Combined Form Export")
    lines.append("")
    lines.append(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Forms included:** {len(db_paths)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of contents
    lines.append("## Contents")
    lines.append("")
    for db_path in db_paths:
        helper = SEAApplicationHelper(db_path=str(db_path))
        form_info = helper.get_form_info()
        progress = helper.get_progress()
        lines.append(f"- [{form_info['name']}](#{form_info['name'].lower().replace(' ', '-')}) ({progress['complete']}/{progress['total']} complete)")
        helper.close()
    lines.append("")
    lines.append("---")
    lines.append("")

    # Each form
    for db_path in db_paths:
        helper = SEAApplicationHelper(db_path=str(db_path))
        form_info = helper.get_form_info()
        progress = helper.get_progress()

        lines.append(f"# {form_info['name']}")
        lines.append("")
        if form_info.get('description'):
            lines.append(f"> {form_info['description']}")
            lines.append("")
        lines.append(f"**Database:** `{db_path}`")
        lines.append(f"**Progress:** {progress['complete']}/{progress['total']} complete ({progress['percent_complete']:.1f}%)")
        lines.append("")

        sections = helper.get_sections()

        for section in sections:
            lines.append(f"## {section['title']}")
            if section.get('description'):
                lines.append(f"*{section['description']}*")
            lines.append("")

            questions = helper.get_questions_by_section(section['id'])

            for q in questions:
                status_icon = {"complete": "✓", "in_progress": "◐", "not_started": "○"}.get(q.get('status', 'not_started'), "○")
                lines.append(f"### {status_icon} Question {q['id']}: {q['question_text']}")
                lines.append("")

                if q.get('helper_text'):
                    lines.append(f"*Helper: {q['helper_text']}*")
                    lines.append("")

                if q.get('answer_text'):
                    lines.append("**Answer:**")
                    lines.append("")
                    lines.append(q['answer_text'])
                    lines.append("")
                else:
                    lines.append("*No answer yet*")
                    lines.append("")

                if q.get('notes'):
                    lines.append("**Notes:**")
                    lines.append(f"> {q['notes']}")
                    lines.append("")

                lines.append("---")
                lines.append("")

        lines.append("")
        lines.append("=" * 70)
        lines.append("")
        helper.close()

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    return output_path


def combine_texinfo(db_paths, output_path="combined_export.texi"):
    """Combine multiple databases into a single Texinfo document"""

    def escape_texi(text):
        if not text:
            return ""
        return text.replace('@', '@@').replace('{', '@{').replace('}', '@}')

    lines = []

    # Header
    lines.append("\\input texinfo")
    lines.append("@settitle Combined Form Export")
    lines.append("@documentencoding UTF-8")
    lines.append("")
    lines.append("@titlepage")
    lines.append("@title Combined Form Export")
    lines.append(f"@subtitle {len(db_paths)} forms included")
    lines.append(f"@subtitle Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("@end titlepage")
    lines.append("")
    lines.append("@contents")
    lines.append("")
    lines.append("@ifnottex")
    lines.append("@node Top")
    lines.append("@top Combined Form Export")
    lines.append("@end ifnottex")
    lines.append("")

    # Top-level menu (forms)
    lines.append("@menu")
    for db_path in db_paths:
        helper = SEAApplicationHelper(db_path=str(db_path))
        form_info = helper.get_form_info()
        node_name = form_info['name'].replace(' ', '-')
        lines.append(f"* {node_name}:: {escape_texi(form_info.get('description', form_info['name']))}")
        helper.close()
    lines.append("@end menu")
    lines.append("")

    # Each form as a chapter
    for db_path in db_paths:
        helper = SEAApplicationHelper(db_path=str(db_path))
        form_info = helper.get_form_info()
        progress = helper.get_progress()

        form_node = form_info['name'].replace(' ', '-')
        lines.append(f"@node {form_node}")
        lines.append(f"@chapter {escape_texi(form_info['name'])}")
        lines.append("")
        if form_info.get('description'):
            lines.append(escape_texi(form_info['description']))
            lines.append("")
        lines.append(f"@emph{{Progress: {progress['complete']}/{progress['total']} complete ({progress['percent_complete']:.1f}%)}}")
        lines.append("")

        # Section menu for this form
        sections = helper.get_sections()
        lines.append("@menu")
        for section in sections:
            section_node = f"{form_node}-{section['title'].replace(' ', '-')}"
            lines.append(f"* {section_node}:: {escape_texi(section.get('description', section['title']))}")
        lines.append("@end menu")
        lines.append("")

        # Sections
        for section in sections:
            section_node = f"{form_node}-{section['title'].replace(' ', '-')}"
            lines.append(f"@node {section_node}")
            lines.append(f"@section {escape_texi(section['title'])}")
            lines.append("")
            if section.get('description'):
                lines.append(escape_texi(section['description']))
                lines.append("")

            questions = helper.get_questions_by_section(section['id'])

            for q in questions:
                lines.append(f"@subsection Question {q['id']}")
                lines.append("")
                lines.append(f"@strong{{{escape_texi(q['question_text'])}}}")
                lines.append("")

                if q.get('helper_text'):
                    lines.append("@quotation Helper")
                    lines.append(escape_texi(q['helper_text']))
                    lines.append("@end quotation")
                    lines.append("")

                status = q.get('status', 'not_started')
                status_text = {"complete": "Complete", "in_progress": "In Progress", "not_started": "Not Started"}.get(status, "Not Started")
                lines.append(f"@emph{{Status: {status_text}}}")
                lines.append("")

                if q.get('answer_text'):
                    lines.append("@quotation Answer")
                    lines.append(escape_texi(q['answer_text']))
                    lines.append("@end quotation")
                    lines.append("")

                if q.get('notes'):
                    lines.append("@quotation Notes")
                    lines.append(escape_texi(q['notes']))
                    lines.append("@end quotation")
                    lines.append("")

        helper.close()

    lines.append("@bye")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Export form-copilot databases to Markdown or Texinfo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 export_docs.py                          # Export current form
    python3 export_docs.py --format texinfo         # Export to texinfo
    python3 export_docs.py --all                    # Export all databases separately
    python3 export_docs.py --all --combine          # Combine all into one document
    python3 export_docs.py form1.db form2.db        # Export specific databases
    python3 export_docs.py *.db --combine           # Combine specified databases

After texinfo export, build with:
    makeinfo --pdf file.texi      # PDF output
    makeinfo --html file.texi     # HTML output
    makeinfo file.texi            # Info format
        """
    )

    parser.add_argument('databases', nargs='*', help='Specific database files to export')
    parser.add_argument('--format', '-f', choices=['markdown', 'texinfo'], default='markdown',
                        help='Output format (default: markdown)')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Export all .db files found')
    parser.add_argument('--combine', '-c', action='store_true',
                        help='Combine multiple databases into one document')
    parser.add_argument('--output', '-o', help='Output filename (for combined export)')

    args = parser.parse_args()

    # Determine which databases to export
    if args.databases:
        db_paths = [Path(db) for db in args.databases]
    elif args.all:
        db_paths = find_databases()
    else:
        # Default: look for questions_config.json and associated db
        config_path = Path('questions_config.json')
        if config_path.exists():
            import json
            with open(config_path) as f:
                config = json.load(f)
            form_name = config.get('form_name', 'form')
            safe_name = form_name.lower().replace(' ', '_').replace('-', '_')
            db_path = Path(f"{safe_name}.db")
            if db_path.exists():
                db_paths = [db_path]
            else:
                db_paths = find_databases()[:1]  # Fall back to first found
        else:
            db_paths = find_databases()[:1]

    if not db_paths:
        print("No databases found. Run sea_assistant.py first to create one.")
        sys.exit(1)

    # Filter to existing files
    db_paths = [p for p in db_paths if p.exists()]
    if not db_paths:
        print("Specified database files not found.")
        sys.exit(1)

    print(f"Found {len(db_paths)} database(s): {', '.join(str(p) for p in db_paths)}")

    # Export
    if args.combine and len(db_paths) > 1:
        if args.format == 'markdown':
            output = args.output or 'combined_export.md'
            filepath = combine_markdown(db_paths, output)
        else:
            output = args.output or 'combined_export.texi'
            filepath = combine_texinfo(db_paths, output)
        print(f"\nCombined export: {filepath}")
    else:
        for db_path in db_paths:
            filepath = export_single(db_path, args.format)
            print(f"Exported: {db_path} -> {filepath}")

    if args.format == 'texinfo':
        print("\nTo build PDF:  makeinfo --pdf <file>.texi")
        print("To build HTML: makeinfo --html <file>.texi")


if __name__ == '__main__':
    main()
