#!/usr/bin/env python3
"""
Form Application Helper
A tool to help work through multi-section applications and questionnaires
with structured support for anyone who benefits from breaking big tasks into steps.

Loads questions from questions_config.json - swap this file to use different forms.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class SEAApplicationHelper:
    def __init__(self, db_path="sea_application.db", config_path=None, log_path=None):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        # Find config file
        if config_path is None:
            config_path = Path(__file__).parent / "questions_config.json"
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Session logging
        if log_path is None:
            log_path = Path(__file__).parent / "session_log.json"
        self.log_path = Path(log_path)
        self.session_log = self._load_session_log()

        self.init_database()

    def _load_config(self):
        """Load questions configuration from JSON file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return None

    def _load_session_log(self):
        """Load existing session log or create new one"""
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"sessions": []}
        return {"sessions": []}

    def _save_session_log(self):
        """Save session log to file"""
        with open(self.log_path, 'w') as f:
            json.dump(self.session_log, f, indent=2)

    def log_event(self, event_type, question_id=None, details=None):
        """Log a session event for tracking user journey"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
        }
        if question_id:
            event["question_id"] = question_id
        if details:
            event.update(details)

        self.session_log["sessions"].append(event)
        self._save_session_log()

    def get_session_history(self, question_id=None):
        """Get session history, optionally filtered by question"""
        events = self.session_log.get("sessions", [])
        if question_id:
            events = [e for e in events if e.get("question_id") == question_id]
        return events

    def get_question_journey(self, question_id):
        """Get the full journey for a specific question"""
        events = self.get_session_history(question_id)
        return {
            "question_id": question_id,
            "total_events": len(events),
            "events": events,
            "claude_sessions": len([e for e in events if e.get("event") == "claude_session_start"]),
            "revisions": len([e for e in events if e.get("event") == "answer_saved"])
        }

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

    def export_markdown(self, filepath=None):
        """Export all answers to Markdown format"""
        form_info = self.get_form_info()
        progress = self.get_progress()

        if filepath is None:
            safe_name = form_info['name'].lower().replace(' ', '_')
            filepath = f"{safe_name}_export.md"

        lines = []
        lines.append(f"# {form_info['name']}")
        lines.append("")
        if form_info.get('description'):
            lines.append(f"> {form_info['description']}")
            lines.append("")
        lines.append(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Progress:** {progress['complete']}/{progress['total']} complete ({progress['percent_complete']:.1f}%)")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Get sections
        sections = self.get_sections()

        for section in sections:
            lines.append(f"## {section['title']}")
            if section.get('description'):
                lines.append(f"*{section['description']}*")
            lines.append("")

            questions = self.get_questions_by_section(section['id'])

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

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        return filepath

    def export_texinfo(self, filepath=None):
        """Export all answers to Texinfo format"""
        form_info = self.get_form_info()
        progress = self.get_progress()

        if filepath is None:
            safe_name = form_info['name'].lower().replace(' ', '_')
            filepath = f"{safe_name}_export.texi"

        # Escape special texinfo characters
        def escape_texi(text):
            if not text:
                return ""
            return text.replace('@', '@@').replace('{', '@{').replace('}', '@}')

        lines = []

        # Texinfo header
        lines.append("\\input texinfo")
        lines.append(f"@settitle {escape_texi(form_info['name'])}")
        lines.append("@documentencoding UTF-8")
        lines.append("")
        lines.append("@titlepage")
        lines.append(f"@title {escape_texi(form_info['name'])}")
        if form_info.get('description'):
            lines.append(f"@subtitle {escape_texi(form_info['description'])}")
        lines.append(f"@subtitle Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"@subtitle Progress: {progress['complete']}/{progress['total']} complete ({progress['percent_complete']:.1f}%)")
        lines.append("@end titlepage")
        lines.append("")
        lines.append("@contents")
        lines.append("")
        lines.append("@ifnottex")
        lines.append(f"@node Top")
        lines.append(f"@top {escape_texi(form_info['name'])}")
        lines.append("@end ifnottex")
        lines.append("")

        # Menu
        lines.append("@menu")
        sections = self.get_sections()
        for section in sections:
            node_name = section['title'].replace(' ', '-')
            lines.append(f"* {node_name}:: {escape_texi(section.get('description', section['title']))}")
        lines.append("@end menu")
        lines.append("")

        # Sections and questions
        for section in sections:
            node_name = section['title'].replace(' ', '-')
            lines.append(f"@node {node_name}")
            lines.append(f"@chapter {escape_texi(section['title'])}")
            lines.append("")
            if section.get('description'):
                lines.append(escape_texi(section['description']))
                lines.append("")

            questions = self.get_questions_by_section(section['id'])

            for q in questions:
                q_node = f"Question-{q['id']}"
                lines.append(f"@section Question {q['id']}")
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

        lines.append("@bye")

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

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
