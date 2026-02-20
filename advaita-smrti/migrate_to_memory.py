#!/usr/bin/env python3
"""
Migration tool: SQLite answers → Memory layer

Migrates existing answers from SQLite database to the memory layer.
Run this once to bring historical data into the new storage system.

Usage:
    python3 migrate_to_memory.py                    # Auto-detect database
    python3 migrate_to_memory.py --db myform.db    # Specific database
    python3 migrate_to_memory.py --dry-run         # Preview without changes
"""

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime


def find_databases():
    """Find all .db files in current directory"""
    return list(Path('.').glob('*.db'))


def get_answers_from_sqlite(db_path):
    """Read all answers from SQLite database"""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get answers with question details
    cursor.execute("""
        SELECT
            a.question_id,
            a.answer_text,
            a.notes,
            a.status,
            a.last_updated,
            q.question_text,
            q.priority,
            s.title as section_title
        FROM answers a
        LEFT JOIN questions q ON a.question_id = q.id
        LEFT JOIN sections s ON q.section_id = s.id
        WHERE a.answer_text IS NOT NULL AND a.answer_text != ''
    """)

    answers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return answers


def migrate_answers(db_path, memory_path=".memory", dry_run=False):
    """Migrate answers from SQLite to memory layer"""
    from memory import Memory

    print(f"\nMigrating from: {db_path}")
    print(f"Memory path: {memory_path}")
    print(f"Dry run: {dry_run}\n")

    # Read SQLite answers
    answers = get_answers_from_sqlite(db_path)

    if not answers:
        print("No answers found in database.")
        return 0

    print(f"Found {len(answers)} answers to migrate:\n")

    for answer in answers:
        status_icon = {'complete': '●', 'in_progress': '◐'}.get(answer['status'], '○')
        print(f"  {status_icon} Q:{answer['question_id']} - {answer['question_text'][:50]}...")

    if dry_run:
        print("\n[Dry run - no changes made]")
        return len(answers)

    # Initialize memory layer
    memory = Memory(memory_path, prefix="fc")

    # Check for existing tasks
    existing_questions = set()
    for task in memory.tasks.all():
        q_id = task.metadata.get('question_id')
        if q_id:
            existing_questions.add(q_id)

    # Migrate each answer
    migrated = 0
    skipped = 0

    for answer in answers:
        q_id = answer['question_id']

        if q_id in existing_questions:
            print(f"  Skipping Q:{q_id} (already in memory)")
            skipped += 1
            continue

        # Map status
        status_map = {
            'not_started': 'open',
            'in_progress': 'in_progress',
            'complete': 'closed'
        }
        memory_status = status_map.get(answer['status'], 'open')

        # Create task in memory
        memory.tasks.create(
            title=f"Q:{q_id} - {answer['question_text'][:50]}",
            description=answer['answer_text'] or '',
            status=memory_status,
            labels=[
                'question',
                'migrated',
                f"section:{answer['section_title'] or 'Unknown'}",
                f"priority:{answer['priority'] or 3}"
            ],
            metadata={
                'question_id': q_id,
                'notes': answer['notes'],
                'section': answer['section_title'],
                'migrated_from': str(db_path),
                'migrated_at': datetime.now().isoformat(),
                'original_updated': answer['last_updated'],
            }
        )
        migrated += 1
        print(f"  Migrated Q:{q_id}")

    memory.close()

    print(f"\nMigration complete:")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped (already exists): {skipped}")

    return migrated


def main():
    parser = argparse.ArgumentParser(
        description='Migrate SQLite answers to memory layer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                       # Auto-detect database
    %(prog)s --db myform.db       # Specific database
    %(prog)s --dry-run            # Preview without changes
    %(prog)s --memory .memory     # Custom memory path
        """
    )

    parser.add_argument('--db', '-d', metavar='PATH',
                        help='SQLite database path')
    parser.add_argument('--memory', '-m', metavar='PATH', default='.memory',
                        help='Memory layer directory (default: .memory)')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Preview migration without making changes')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Migrate all .db files found')

    args = parser.parse_args()

    print("=" * 60)
    print("  SQLite → Memory Migration Tool")
    print("=" * 60)

    if args.all:
        # Migrate all databases
        databases = find_databases()
        if not databases:
            print("\nNo .db files found in current directory.")
            return 1

        total_migrated = 0
        for db in databases:
            migrated = migrate_answers(db, args.memory, args.dry_run)
            total_migrated += migrated

        print(f"\n{'=' * 60}")
        print(f"Total migrated: {total_migrated} answers from {len(databases)} databases")

    elif args.db:
        # Specific database
        db_path = Path(args.db)
        if not db_path.exists():
            print(f"\nError: Database not found: {db_path}")
            return 1
        migrate_answers(db_path, args.memory, args.dry_run)

    else:
        # Auto-detect
        databases = find_databases()
        if not databases:
            print("\nNo .db files found. Specify with --db or create answers first.")
            return 1

        if len(databases) == 1:
            migrate_answers(databases[0], args.memory, args.dry_run)
        else:
            print("\nMultiple databases found:")
            for i, db in enumerate(databases, 1):
                print(f"  [{i}] {db}")
            print(f"  [A] Migrate all")
            print()

            choice = input("Select database: ").strip()

            if choice.upper() == 'A':
                for db in databases:
                    migrate_answers(db, args.memory, args.dry_run)
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(databases):
                        migrate_answers(databases[idx], args.memory, args.dry_run)
                    else:
                        print("Invalid choice")
                        return 1
                except ValueError:
                    print("Invalid choice")
                    return 1

    return 0


if __name__ == '__main__':
    exit(main())
