#!/usr/bin/env python3
"""
Form Application Helper
A tool to help work through multi-section applications and questionnaires
with executive function support for neurodivergent applicants.

Loads questions from questions_config.json - swap this file to use different forms.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class SEAApplicationHelper:
    def __init__(self, db_path="sea_application.db", config_path=None):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Find config file
        if config_path is None:
            config_path = Path(__file__).parent / "questions_config.json"
        self.config_path = Path(config_path)
        self.config = self._load_config()

        self.init_database()

    def _load_config(self):
        """Load questions configuration from JSON file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return None

    def get_form_info(self):
        """Get information about the loaded form"""
        if self.config:
            return {
                'name': self.config.get('form_name', 'Unknown Form'),
                'description': self.config.get('form_description', ''),
                'version': self.config.get('version', '1.0')
            }
        return {'name': 'No form loaded', 'description': '', 'version': ''}

    def init_database(self):
        """Initialize the database schema"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                section_id INTEGER,
                question_text TEXT NOT NULL,
                question_type TEXT DEFAULT 'text',
                priority INTEGER DEFAULT 3,
                depends_on TEXT,
                helper_text TEXT,
                FOREIGN KEY (section_id) REFERENCES sections(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                question_id TEXT PRIMARY KEY,
                answer_text TEXT,
                notes TEXT,
                last_updated TEXT,
                status TEXT DEFAULT 'not_started',
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_directions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                selected INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        self.conn.commit()

    def populate_questions(self):
        """Populate the database from the config file"""
        if not self.config:
            print("No config file found at:", self.config_path)
            return

        # Load sections
        sections = self.config.get('sections', [])
        for section in sections:
            self.cursor.execute("""
                INSERT OR IGNORE INTO sections (id, name, title, description)
                VALUES (?, ?, ?, ?)
            """, (section['id'], section['name'], section['title'], section.get('description', '')))

        # Load questions
        questions = self.config.get('questions', [])
        for q in questions:
            self.cursor.execute("""
                INSERT OR IGNORE INTO questions
                (id, section_id, question_text, question_type, priority, depends_on, helper_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                q['id'],
                q['section_id'],
                q['question_text'],
                q.get('question_type', 'text'),
                q.get('priority', 3),
                q.get('depends_on'),
                q.get('helper_text')
            ))

        # Load business directions if present
        directions = self.config.get('business_directions', [])
        for d in directions:
            self.cursor.execute("""
                INSERT INTO business_directions (name, description, created_at)
                VALUES (?, ?, ?)
            """, (d['name'], d.get('description', ''), datetime.now().isoformat()))

        self.conn.commit()

        form_info = self.get_form_info()
        print(f"Loaded {len(questions)} questions across {len(sections)} sections")
        print(f"Form: {form_info['name']}")

    def add_business_direction(self, name, description):
        """Add a potential business direction to consider"""
        self.cursor.execute("""
            INSERT INTO business_directions (name, description, created_at)
            VALUES (?, ?, ?)
        """, (name, description, datetime.now().isoformat()))
        self.conn.commit()

    def select_business_direction(self, direction_id):
        """Mark a business direction as selected"""
        self.cursor.execute("UPDATE business_directions SET selected = 0")
        self.cursor.execute("""
            UPDATE business_directions SET selected = 1 WHERE id = ?
        """, (direction_id,))
        self.conn.commit()

    def get_business_directions(self):
        """Get all business directions"""
        self.cursor.execute("""
            SELECT * FROM business_directions ORDER BY id
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def save_answer(self, question_id, answer_text, notes=None, status="in_progress"):
        """Save or update an answer"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO answers
            (question_id, answer_text, notes, last_updated, status)
            VALUES (?, ?, ?, ?, ?)
        """, (question_id, answer_text, notes, datetime.now().isoformat(), status))
        self.conn.commit()

    def get_question(self, question_id):
        """Get a specific question with its answer if it exists"""
        self.cursor.execute("""
            SELECT q.*, a.answer_text, a.notes, a.status, a.last_updated,
                   s.title as section_title
            FROM questions q
            LEFT JOIN answers a ON q.id = a.question_id
            LEFT JOIN sections s ON q.section_id = s.id
            WHERE q.id = ?
        """, (question_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_questions_by_section(self, section_id):
        """Get all questions for a section"""
        self.cursor.execute("""
            SELECT q.*, a.answer_text, a.status, s.title as section_title
            FROM questions q
            LEFT JOIN answers a ON q.id = a.question_id
            LEFT JOIN sections s ON q.section_id = s.id
            WHERE q.section_id = ?
            ORDER BY q.id
        """, (section_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_sections(self):
        """Get all sections"""
        self.cursor.execute("""
            SELECT * FROM sections ORDER BY id
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_priority_questions(self, priority=1):
        """Get high priority questions that aren't answered"""
        self.cursor.execute("""
            SELECT q.*, s.title as section_title
            FROM questions q
            LEFT JOIN answers a ON q.id = a.question_id
            LEFT JOIN sections s ON q.section_id = s.id
            WHERE q.priority <= ? AND (a.status IS NULL OR a.status != 'complete')
            ORDER BY q.priority, q.section_id, q.id
        """, (priority,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_progress(self):
        """Get overall progress statistics"""
        self.cursor.execute("SELECT COUNT(*) as total FROM questions")
        total = self.cursor.fetchone()['total']

        self.cursor.execute("""
            SELECT COUNT(*) as complete
            FROM answers
            WHERE status = 'complete'
        """)
        complete = self.cursor.fetchone()['complete']

        self.cursor.execute("""
            SELECT COUNT(*) as in_progress
            FROM answers
            WHERE status = 'in_progress'
        """)
        in_progress = self.cursor.fetchone()['in_progress']

        return {
            'total': total,
            'complete': complete,
            'in_progress': in_progress,
            'not_started': total - complete - in_progress,
            'percent_complete': (complete / total * 100) if total > 0 else 0
        }

    def export_answers(self, filepath="sea_answers.json"):
        """Export all answers to JSON"""
        self.cursor.execute("""
            SELECT q.id, q.question_text, q.section_id, s.title as section_title,
                   a.answer_text, a.notes, a.status, a.last_updated
            FROM questions q
            LEFT JOIN answers a ON q.id = a.question_id
            LEFT JOIN sections s ON q.section_id = s.id
            ORDER BY q.section_id, q.id
        """)

        form_info = self.get_form_info()
        data = {
            'form_name': form_info['name'],
            'form_version': form_info['version'],
            'export_date': datetime.now().isoformat(),
            'progress': self.get_progress(),
            'answers': [dict(row) for row in self.cursor.fetchall()]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return filepath

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main entry point"""
    print("=" * 70)
    print("  Form Application Helper")
    print("=" * 70)
    print()

    helper = SEAApplicationHelper()

    form_info = helper.get_form_info()
    print(f"Form: {form_info['name']}")
    print(f"Description: {form_info['description']}")
    print()

    # Check if database needs population
    helper.cursor.execute("SELECT COUNT(*) as count FROM questions")
    if helper.cursor.fetchone()['count'] == 0:
        print("First time setup: Loading questions from config...")
        helper.populate_questions()
        print("Setup complete!")

    print("\n" + "=" * 70)
    print("Current Progress:")
    progress = helper.get_progress()
    print(f"   Total Questions: {progress['total']}")
    print(f"   Complete: {progress['complete']} ({progress['percent_complete']:.1f}%)")
    print(f"   In Progress: {progress['in_progress']}")
    print(f"   Not Started: {progress['not_started']}")
    print("=" * 70)

    print("\nHigh Priority Questions (Priority 1):")
    priority_qs = helper.get_priority_questions(priority=1)
    for i, q in enumerate(priority_qs[:5], 1):
        status = q.get('status', 'not_started') or 'not_started'
        status_icon = "+" if status == "complete" else "~" if status == "in_progress" else "o"
        print(f"   {status_icon} [{q['id']}] {q['question_text'][:60]}...")
        print(f"      Section: {q['section_title']}")

    if len(priority_qs) > 5:
        print(f"   ... and {len(priority_qs) - 5} more priority questions")

    print("\nDatabase saved to: sea_application.db")
    print("Ready to use! Run: python3 sea_assistant.py\n")

    helper.close()


if __name__ == "__main__":
    main()
