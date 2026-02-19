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

# Memory layer import (primary storage)
try:
    from memory import Memory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("Warning: Memory layer not found. Install or check import path.")

# SQLite is now optional - for backwards compatibility or fallback
SQLITE_ENABLED = False  # Set True to enable legacy SQLite backing store


class SEAApplicationHelper:
    def __init__(self, db_path="sea_application.db", config_path=None, log_path=None,
                 memory_path=None, use_sqlite=None):
        """Initialize the application helper.

        Args:
            db_path: SQLite database path (for questions/sections config cache)
            config_path: JSON config file path
            log_path: Session log file path
            memory_path: Memory layer directory path
            use_sqlite: Override SQLITE_ENABLED for answers storage
        """
        self.db_path = db_path
        self.use_sqlite = use_sqlite if use_sqlite is not None else SQLITE_ENABLED

        # SQLite for questions/sections (config cache - always needed)
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

        # Memory layer (PRIMARY storage for answers and decisions)
        self.memory = None
        if MEMORY_AVAILABLE:
            if memory_path is None:
                memory_path = Path(__file__).parent / ".memory"
            try:
                self.memory = Memory(str(memory_path), prefix="fc")
            except Exception as e:
                print(f"Error: Memory layer failed: {e}")
                if not self.use_sqlite:
                    raise RuntimeError("Memory layer required but unavailable")

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
        """Log a session event for tracking user journey

        Dual-writes to:
        1. session_log.json (primary) - existing behavior
        2. Memory layer (shadow) - for future synthesis
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
        }
        if question_id:
            event["question_id"] = question_id
        if details:
            event.update(details)

        # Primary: session_log.json
        self.session_log["sessions"].append(event)
        self._save_session_log()

        # Shadow: Memory layer - log as task comment or metadata
        if self.memory and question_id:
            self._memory_log_event(event_type, question_id, details)

    def _memory_log_event(self, event_type, question_id, details=None):
        """Shadow log event to memory layer"""
        # Find the task for this question
        existing_tasks = [t for t in self.memory.tasks.all()
                         if t.metadata.get('question_id') == question_id]

        if not existing_tasks:
            return  # No task yet, event will be captured when answer is saved

        task = existing_tasks[0]

        # Add event to task's event history in metadata
        events = task.metadata.get('events', [])
        events.append({
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        })

        self.memory.tasks.update(
            task.id,
            metadata={**task.metadata, 'events': events}
        )

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

    def analyze_session_log(self):
        """Analyze session log and return summary statistics"""
        events = self.session_log.get("sessions", [])

        if not events:
            return None

        # Basic stats
        total_events = len(events)
        timestamps = [e.get("timestamp") for e in events if e.get("timestamp")]

        # Date range
        first_event = min(timestamps) if timestamps else None
        last_event = max(timestamps) if timestamps else None

        # Event type counts
        event_types = {}
        for e in events:
            etype = e.get("event", "unknown")
            event_types[etype] = event_types.get(etype, 0) + 1

        # Questions with most activity
        question_activity = {}
        for e in events:
            qid = e.get("question_id")
            if qid:
                question_activity[qid] = question_activity.get(qid, 0) + 1

        # Top questions by activity
        top_questions = sorted(question_activity.items(), key=lambda x: x[1], reverse=True)[:5]

        # Claude session stats
        claude_sessions = [e for e in events if e.get("event") == "claude_session_start"]
        questions_with_claude = set(e.get("question_id") for e in claude_sessions if e.get("question_id"))

        # Revision stats
        revisions = [e for e in events if e.get("event") == "answer_saved"]
        questions_revised = {}
        for e in revisions:
            qid = e.get("question_id")
            if qid:
                questions_revised[qid] = questions_revised.get(qid, 0) + 1
        most_revised = sorted(questions_revised.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "total_events": total_events,
            "first_event": first_event,
            "last_event": last_event,
            "event_types": event_types,
            "top_questions": top_questions,
            "claude_sessions_total": len(claude_sessions),
            "questions_with_claude": len(questions_with_claude),
            "total_revisions": len(revisions),
            "most_revised": most_revised
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

    def wire_dependencies(self):
        """Wire config depends_on relationships into memory layer blocks/blocked_by.

        Reads depends_on from the question config and creates corresponding
        block relationships between memory tasks. Also stores depends_on
        in task metadata for coherence checking.

        Call after populate_questions() and after memory tasks exist.
        """
        if not self.memory or not self.config:
            return

        questions = self.config.get('questions', [])

        # Build question_id -> memory task lookup
        qid_to_task = {}
        for task in self.memory.tasks.all():
            qid = task.metadata.get('question_id')
            if qid:
                qid_to_task[qid] = task

        wired = 0
        for q in questions:
            depends_on = q.get('depends_on')
            if not depends_on:
                continue

            qid = q['id']
            task = qid_to_task.get(qid)
            dep_task = qid_to_task.get(depends_on)

            if not task or not dep_task:
                continue

            # Store depends_on in metadata for coherence checking
            if task.metadata.get('depends_on') != depends_on:
                self.memory.tasks.update(
                    task.id,
                    metadata={**task.metadata, 'depends_on': depends_on}
                )

            # Wire block relationship if not already set
            if dep_task.id not in task.blocked_by:
                self.memory.tasks.block(dep_task.id, task.id)
                wired += 1

        if wired > 0:
            print(f"Wired {wired} dependency relationships")

    def coherence_check(self, section=None):
        """Run a coherence check on the current answers.

        Returns a CoherenceReport with findings about dependency violations,
        gaps, and cross-reference opportunities.

        Args:
            section: Section title to check, or None for all sections.
        """
        if not self.memory:
            return None

        return self.memory.synthesize.coherence_check(section=section)

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
        """Save or update an answer

        Primary: Memory layer (beads-style task tracking)
        Optional: SQLite (legacy backing store, off by default)
        """
        # Primary: Memory layer
        if self.memory:
            self._memory_save_answer(question_id, answer_text, notes, status)

        # Optional: SQLite backing store
        if self.use_sqlite:
            self.cursor.execute("""
                INSERT OR REPLACE INTO answers
                (question_id, answer_text, notes, last_updated, status)
                VALUES (?, ?, ?, ?, ?)
            """, (question_id, answer_text, notes, datetime.now().isoformat(), status))
            self.conn.commit()

    def _memory_save_answer(self, question_id, answer_text, notes=None, status="in_progress"):
        """Shadow write to memory layer as beads-style task"""
        # Get question details for context
        question = self.get_question(question_id)
        section_title = question.get('section_title', 'Unknown') if question else 'Unknown'
        question_text = question.get('question_text', '') if question else ''

        # Map status to memory layer status
        memory_status = {
            'not_started': 'open',
            'in_progress': 'in_progress',
            'complete': 'closed'
        }.get(status, 'open')

        # Check if task exists for this question
        existing_tasks = [t for t in self.memory.tasks.all()
                         if t.metadata.get('question_id') == question_id]

        if existing_tasks:
            # Update existing task
            task = existing_tasks[0]
            self.memory.tasks.update(
                task.id,
                description=answer_text or '',
                status=memory_status,
                metadata={
                    **task.metadata,
                    'question_id': question_id,
                    'notes': notes,
                    'section': section_title,
                }
            )
        else:
            # Create new task with correct status
            self.memory.tasks.create(
                title=f"Q:{question_id} - {question_text[:50]}",
                description=answer_text or '',
                status=memory_status,
                labels=['question', f'section:{section_title}', f'priority:{question.get("priority", 3)}'] if question else ['question'],
                metadata={
                    'question_id': question_id,
                    'notes': notes,
                    'section': section_title,
                }
            )

    def get_question(self, question_id):
        """Get a specific question with its answer if it exists

        Question metadata from SQLite (config cache).
        Answer from Memory layer (primary) or SQLite (fallback).
        """
        # Get question metadata from SQLite (config-driven)
        self.cursor.execute("""
            SELECT q.*, s.title as section_title
            FROM questions q
            LEFT JOIN sections s ON q.section_id = s.id
            WHERE q.id = ?
        """, (question_id,))
        row = self.cursor.fetchone()
        if not row:
            return None

        result = dict(row)

        # Get answer from Memory layer (primary)
        if self.memory:
            answer_data = self._memory_get_answer(question_id)
            if answer_data:
                result.update(answer_data)
                return result

        # Fallback: SQLite answers table
        if self.use_sqlite:
            self.cursor.execute("""
                SELECT answer_text, notes, status, last_updated
                FROM answers WHERE question_id = ?
            """, (question_id,))
            answer_row = self.cursor.fetchone()
            if answer_row:
                result.update(dict(answer_row))

        return result

    def _memory_get_answer(self, question_id):
        """Get answer data from memory layer"""
        if not self.memory:
            return None

        # Find task for this question
        for task in self.memory.tasks.all():
            if task.metadata.get('question_id') == question_id:
                # Map memory status to legacy status
                status_map = {
                    'open': 'not_started',
                    'in_progress': 'in_progress',
                    'closed': 'complete',
                    'archived': 'complete'
                }
                return {
                    'answer_text': task.description,
                    'notes': task.metadata.get('notes'),
                    'status': status_map.get(task.status, 'not_started'),
                    'last_updated': task.updated_at
                }
        return None

    def get_questions_by_section(self, section_id):
        """Get all questions for a section

        Question metadata from SQLite, answers from Memory layer.
        """
        self.cursor.execute("""
            SELECT q.*, s.title as section_title
            FROM questions q
            LEFT JOIN sections s ON q.section_id = s.id
            WHERE q.section_id = ?
            ORDER BY q.id
        """, (section_id,))

        questions = []
        for row in self.cursor.fetchall():
            q = dict(row)
            # Merge answer from memory layer
            if self.memory:
                answer_data = self._memory_get_answer(q['id'])
                if answer_data:
                    q.update(answer_data)
            elif self.use_sqlite:
                # Fallback to SQLite answers
                self.cursor.execute("""
                    SELECT answer_text, notes, status
                    FROM answers WHERE question_id = ?
                """, (q['id'],))
                answer_row = self.cursor.fetchone()
                if answer_row:
                    q.update(dict(answer_row))
            questions.append(q)

        return questions

    def get_sections(self):
        """Get all sections"""
        self.cursor.execute("""
            SELECT * FROM sections ORDER BY id
        """)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_priority_questions(self, priority=1):
        """Get high priority questions that aren't complete"""
        # Get all questions at or above priority level
        self.cursor.execute("""
            SELECT q.*, s.title as section_title
            FROM questions q
            LEFT JOIN sections s ON q.section_id = s.id
            WHERE q.priority <= ?
            ORDER BY q.priority, q.section_id, q.id
        """, (priority,))

        questions = []
        for row in self.cursor.fetchall():
            q = dict(row)
            # Check answer status from memory
            if self.memory:
                answer_data = self._memory_get_answer(q['id'])
                if answer_data:
                    q.update(answer_data)
                    if answer_data.get('status') == 'complete':
                        continue  # Skip complete questions
            elif self.use_sqlite:
                self.cursor.execute("""
                    SELECT answer_text, notes, status
                    FROM answers WHERE question_id = ?
                """, (q['id'],))
                answer_row = self.cursor.fetchone()
                if answer_row:
                    q.update(dict(answer_row))
                    if answer_row['status'] == 'complete':
                        continue
            questions.append(q)

        return questions

    def get_progress(self):
        """Get overall progress statistics

        Counts from Memory layer (primary) or SQLite (fallback).
        """
        self.cursor.execute("SELECT COUNT(*) as total FROM questions")
        total = self.cursor.fetchone()['total']

        complete = 0
        in_progress = 0

        if self.memory:
            # Count from memory layer
            for task in self.memory.tasks.all():
                if task.metadata.get('question_id'):  # Only count question tasks
                    if task.status == 'closed':
                        complete += 1
                    elif task.status == 'in_progress':
                        in_progress += 1
        elif self.use_sqlite:
            # Fallback to SQLite
            self.cursor.execute("""
                SELECT COUNT(*) as complete FROM answers WHERE status = 'complete'
            """)
            complete = self.cursor.fetchone()['complete']

            self.cursor.execute("""
                SELECT COUNT(*) as in_progress FROM answers WHERE status = 'in_progress'
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

        # Appendix: Session Log Analysis
        analysis = self.analyze_session_log()
        if analysis:
            lines.append("## Appendix: Session Analysis")
            lines.append("")
            lines.append("Summary of your journey through this form.")
            lines.append("")

            # Timeline
            if analysis['first_event'] and analysis['last_event']:
                first = analysis['first_event'][:10]
                last = analysis['last_event'][:10]
                lines.append(f"**Timeline:** {first} to {last}")
                lines.append("")

            # Stats table
            lines.append("### Activity Summary")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Events | {analysis['total_events']} |")
            lines.append(f"| Claude Sessions | {analysis['claude_sessions_total']} across {analysis['questions_with_claude']} questions |")
            lines.append(f"| Answer Revisions | {analysis['total_revisions']} |")
            lines.append("")

            # Most active questions
            if analysis['top_questions']:
                lines.append("### Most Active Questions")
                lines.append("")
                for qid, count in analysis['top_questions']:
                    lines.append(f"- Question {qid}: {count} events")
                lines.append("")

            # Most revised
            if analysis['most_revised']:
                lines.append("### Most Revised Answers")
                lines.append("")
                for qid, count in analysis['most_revised']:
                    lines.append(f"- Question {qid}: {count} revisions")
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
        # Add appendix if we have session data
        if self.analyze_session_log():
            lines.append("* Session-Analysis:: Summary of your journey")
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

        # Appendix: Session Log Analysis
        analysis = self.analyze_session_log()
        if analysis:
            lines.append("@node Session-Analysis")
            lines.append("@appendix Session Analysis")
            lines.append("")
            lines.append("Summary of your journey through this form.")
            lines.append("")

            # Timeline
            if analysis['first_event'] and analysis['last_event']:
                first = analysis['first_event'][:10]  # Just date
                last = analysis['last_event'][:10]
                lines.append(f"@strong{{Timeline:}} {first} to {last}")
                lines.append("")

            # Overall stats
            lines.append("@section Activity Summary")
            lines.append("")
            lines.append("@table @strong")
            lines.append(f"@item Total Events")
            lines.append(f"{analysis['total_events']}")
            lines.append(f"@item Claude Sessions")
            lines.append(f"{analysis['claude_sessions_total']} sessions across {analysis['questions_with_claude']} questions")
            lines.append(f"@item Answer Revisions")
            lines.append(f"{analysis['total_revisions']} total saves")
            lines.append("@end table")
            lines.append("")

            # Most active questions
            if analysis['top_questions']:
                lines.append("@section Most Active Questions")
                lines.append("")
                lines.append("Questions that received the most attention:")
                lines.append("")
                lines.append("@enumerate")
                for qid, count in analysis['top_questions']:
                    lines.append(f"@item Question {qid}: {count} events")
                lines.append("@end enumerate")
                lines.append("")

            # Most revised
            if analysis['most_revised']:
                lines.append("@section Most Revised Answers")
                lines.append("")
                lines.append("Questions that went through multiple iterations:")
                lines.append("")
                lines.append("@enumerate")
                for qid, count in analysis['most_revised']:
                    lines.append(f"@item Question {qid}: {count} revisions")
                lines.append("@end enumerate")
                lines.append("")

            # Event breakdown
            if analysis['event_types']:
                lines.append("@section Event Breakdown")
                lines.append("")
                lines.append("@table @code")
                for etype, count in sorted(analysis['event_types'].items()):
                    lines.append(f"@item {etype}")
                    lines.append(f"{count}")
                lines.append("@end table")
                lines.append("")

        lines.append("@bye")

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        return filepath

    def get_memory_summary(self):
        """Get summary from memory layer (if available)"""
        if not self.memory:
            return None
        return self.memory.summary()

    def synthesize_patterns(self, label=None):
        """Run pattern synthesis on memory layer (if available)"""
        if not self.memory:
            return []
        return self.memory.synthesize.patterns(label=label)

    def close(self):
        """Close database and memory connections"""
        self.conn.close()
        if self.memory:
            self.memory.close()


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
