#!/usr/bin/env python3
"""
Interactive Form Application Assistant
Choose Your Own Adventure style interface for completing applications
with AI-assisted collaboration via Claude Code.

Tracks your journey through session logging - see how your thinking evolves.
"""

import sys
import json
import subprocess
import shutil
from pathlib import Path
from sea_application_helper import SEAApplicationHelper


def get_config_path():
    """Get the path to the active config file"""
    return Path(__file__).parent / "questions_config.json"


def get_examples_dir():
    """Get the path to the examples directory"""
    return Path(__file__).parent / "examples"


def list_available_configs():
    """List all available config files"""
    examples_dir = get_examples_dir()
    configs = []

    if examples_dir.exists():
        for f in sorted(examples_dir.glob("*_config.json")):
            try:
                with open(f, 'r') as file:
                    data = json.load(file)
                    configs.append({
                        'path': f,
                        'name': data.get('form_name', f.stem),
                        'description': data.get('form_description', ''),
                        'questions': len(data.get('questions', []))
                    })
            except (json.JSONDecodeError, IOError):
                pass

    return configs


def select_config_interactive():
    """Interactive config selection for first run"""
    print("\n" + "=" * 70)
    print("  FORM COPILOT - First Time Setup")
    print("=" * 70)
    print("\nNo active form found. Let's choose one to get started.\n")

    configs = list_available_configs()

    if not configs:
        print("No example configs found in examples/ directory.")
        print("Create a questions_config.json file to get started.")
        print("See README.md for the config file format.")
        sys.exit(1)

    print("Available forms:\n")
    for i, cfg in enumerate(configs, 1):
        print(f"  [{i}] {cfg['name']}")
        print(f"      {cfg['description']}")
        print(f"      ({cfg['questions']} questions)")
        print()

    print("  [C] Create a new custom form")
    print("  [Q] Quit")
    print()

    while True:
        choice = input("Select a form to start with: ").strip()

        if choice.upper() == 'Q':
            print("\nGoodbye!")
            sys.exit(0)

        if choice.upper() == 'C':
            print("\nTo create a custom form:")
            print("1. Copy an example: cp examples/college_app_config.json questions_config.json")
            print("2. Edit questions_config.json with your sections and questions")
            print("3. Run this assistant again")
            print("\nSee README.md for the full config file format.")
            sys.exit(0)

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(configs):
                selected = configs[idx]

                # Copy to active config
                config_path = get_config_path()
                shutil.copy(selected['path'], config_path)

                print(f"\nActivated: {selected['name']}")
                print(f"Config copied to: {config_path.name}")
                print()
                return config_path
        except ValueError:
            pass

        print("Invalid choice. Try again.")


def get_db_path_for_config(config_path):
    """Generate database path based on config name"""
    # Use config filename (without _config.json) as db name
    config_name = config_path.stem.replace('_config', '')
    if config_name == 'questions':
        # For the generic questions_config.json, read the form name
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                form_name = data.get('form_name', 'default')
                # Sanitize for filename
                config_name = form_name.lower().replace(' ', '_')[:30]
        except (json.JSONDecodeError, IOError):
            config_name = 'default'

    return Path(__file__).parent / f"{config_name}.db"


class InteractiveAssistant:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = get_config_path()

        # Check if active config exists
        if not config_path.exists():
            select_config_interactive()

        # Determine database path based on form
        db_path = get_db_path_for_config(config_path)

        self.config_path = config_path
        self.helper = SEAApplicationHelper(db_path=str(db_path), config_path=str(config_path))
        self.running = True
        self.form_info = self.helper.get_form_info()

    def clear_screen(self):
        """Clear screen (optional, can comment out if disorienting)"""
        # print("\033[H\033[J", end="")
        pass

    def show_header(self):
        """Show consistent header"""
        print("\n" + "=" * 70)
        print(f"  {self.form_info['name']}")
        progress = self.helper.get_progress()
        print(f"  Progress: {progress['complete']}/{progress['total']} complete ({progress['percent_complete']:.1f}%)")
        print("=" * 70 + "\n")

    def has_business_directions(self):
        """Check if this form has business directions configured"""
        directions = self.helper.get_business_directions()
        return len(directions) > 0

    def show_menu(self):
        """Show main menu - Choose Your Own Adventure style"""
        self.show_header()
        print("What would you like to do?")
        print()
        print("  [1] Work on high-priority questions (recommended to start)")
        if self.has_business_directions():
            print("  [2] Review business directions")
        print("  [3] Browse by section")
        print("  [4] View specific question by ID")
        print("  [5] Show progress dashboard")
        print("  [6] Export answers to file")
        print("  [7] Tips for answering questions")
        print("  [8] View session history")
        print("  [9] Switch to different form")
        print()
        print("  [C] Work with Claude on a question (collaborative AI session)")
        print()
        print("  [Q] Quit and save")
        print()

    def work_on_priorities(self):
        """Work through priority questions one at a time"""
        self.clear_screen()
        self.show_header()

        questions = self.helper.get_priority_questions(priority=1)

        if not questions:
            print("All priority questions are complete!")
            print("Consider reviewing Section 2 priority questions next.")
            input("\nPress Enter to continue...")
            return

        print(f"{len(questions)} high-priority questions remaining\n")
        print("Working through these first will give you a solid foundation.\n")

        for i, q in enumerate(questions, 1):
            self.clear_screen()
            self.show_header()

            print(f"Question {i} of {len(questions)}")
            print(f"Priority: {'*' * q['priority']}")
            print(f"Section: {q['section_title']}")
            print(f"ID: {q['id']}")
            print("-" * 70)
            print(f"\n{q['question_text']}\n")

            if q.get('helper_text'):
                print(f"Hint: {q['helper_text']}\n")

            current_answer = q.get('answer_text', '')
            if current_answer:
                print(f"Current answer:\n{current_answer}\n")

            print("Options:")
            print("  [C] Work with Claude (recommended - collaborative AI session)")
            print("  [A] Answer/Edit this question manually")
            print("  [N] Add notes/thoughts for later")
            print("  [S] Skip to next question")
            print("  [M] Mark as complete and continue")
            print("  [B] Back to main menu")
            print()

            choice = input("Your choice: ").strip().upper()

            if choice == 'C':
                self.work_with_claude(q['id'])
            elif choice == 'A':
                self.answer_question(q['id'])
            elif choice == 'N':
                self.add_notes(q['id'])
            elif choice == 'S':
                continue
            elif choice == 'M':
                if current_answer:
                    self.helper.save_answer(q['id'], current_answer, status='complete')
                    print("Marked as complete!")
                else:
                    print("Can't mark as complete without an answer")
                input("\nPress Enter to continue...")
            elif choice == 'B':
                return

    def answer_question(self, question_id):
        """Answer a specific question manually"""
        q = self.helper.get_question(question_id)

        print("\n" + "=" * 70)
        print(f"Answering Question {q['id']}")
        print("=" * 70)
        print(f"\n{q['question_text']}\n")

        if q.get('helper_text'):
            print(f"Hint: {q['helper_text']}\n")

        current = q.get('answer_text', '')
        if current:
            print(f"Current answer:\n{current}\n")
            print("Enter new answer (or press Enter to keep current):")
        else:
            print("Enter your answer (or 'draft' for a placeholder):")

        print("(Type 'END' on a new line when done, or Ctrl+D)")
        print("-" * 70)

        lines = []
        try:
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
        except EOFError:
            pass

        answer = '\n'.join(lines).strip()

        if answer or not current:
            final_answer = answer if answer else current
            if answer.lower() == 'draft':
                final_answer = f"[DRAFT] {q['question_text'][:50]}..."
                status = 'in_progress'
            else:
                status = 'in_progress' if '[DRAFT]' in final_answer else 'complete'

            self.helper.save_answer(question_id, final_answer, status=status)
            self.helper.log_event("answer_saved", question_id, {
                "source": "manual",
                "status": status,
                "answer_length": len(final_answer)
            })
            print("\nSaved!")
        else:
            print("\nNo changes made")

        input("\nPress Enter to continue...")

    def add_notes(self, question_id):
        """Add notes to a question"""
        q = self.helper.get_question(question_id)

        print(f"\nAdding notes for question {q['id']}")
        print("These are just for you - not part of the official answer")
        print("(Type 'END' on a new line when done)")
        print("-" * 70)

        lines = []
        try:
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
        except EOFError:
            pass

        notes = '\n'.join(lines).strip()

        if notes:
            current_answer = q.get('answer_text', '[NOTES ONLY]')
            self.helper.save_answer(question_id, current_answer, notes=notes)
            self.helper.log_event("notes_added", question_id, {
                "notes_length": len(notes)
            })
            print("\nNotes saved!")

        input("\nPress Enter to continue...")

    def get_related_answers(self, question_id):
        """Get answers to related questions for context"""
        related = {}
        q = self.helper.get_question(question_id)
        if not q:
            return related

        # Get other answered questions from the same section
        section_questions = self.helper.get_questions_by_section(q['section_id'])
        for sq in section_questions:
            if sq['id'] != question_id and sq.get('answer_text'):
                related[sq['id']] = {
                    'question': sq['question_text'][:100],
                    'answer': sq['answer_text'][:500]
                }
        return related

    def work_with_claude(self, question_id):
        """Launch Claude Code session to collaboratively work on a question"""
        q = self.helper.get_question(question_id)
        if not q:
            print(f"\nQuestion '{question_id}' not found")
            input("Press Enter to continue...")
            return

        # Log session start
        self.helper.log_event("claude_session_start", question_id, {
            "had_draft": bool(q.get('answer_text')),
            "had_notes": bool(q.get('notes')),
            "section": q.get('section_title')
        })

        # Prepare context file
        context = {
            "question_id": q['id'],
            "question_text": q['question_text'],
            "helper_text": q.get('helper_text'),
            "section": q.get('section_title', 'Unknown'),
            "priority": q.get('priority', 3),
            "current_answer": q.get('answer_text'),
            "notes": q.get('notes'),
            "related_answers": self.get_related_answers(question_id)
        }

        context_file = Path(__file__).parent / '.sea_question_context.json'
        answer_file = Path(__file__).parent / '.sea_answer.md'

        # Write context
        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2)

        # Clear any previous answer file
        if answer_file.exists():
            answer_file.unlink()

        print("\n" + "=" * 70)
        print("LAUNCHING CLAUDE CODE SESSION")
        print("=" * 70)
        print(f"\nQuestion {q['id']}: {q['question_text'][:60]}...")
        print(f"Section: {q.get('section_title', 'Unknown')}")
        print("\nInstructions:")
        print("  - Discuss and refine your answer collaboratively")
        print("  - When satisfied, tell Claude 'done' or 'save'")
        print("  - Claude will write the final answer to .sea_answer.md")
        print("  - Exit Claude Code (Ctrl+C or /exit) to return here")
        print("=" * 70)
        input("\nPress Enter to launch Claude Code...")

        # Build the initial prompt for Claude
        prompt = f"""I'm working on question {q['id']} from the application.

**Question:** {q['question_text']}

**Section:** {q.get('section_title', 'Unknown')}
"""
        if q.get('helper_text'):
            prompt += f"\n**Helper hint:** {q['helper_text']}\n"

        if q.get('answer_text'):
            prompt += f"\n**Current draft:**\n{q['answer_text']}\n"

        if q.get('notes'):
            prompt += f"\n**My notes:**\n{q['notes']}\n"

        prompt += "\nLet's work on this together. When we're done, write the final answer to .sea_answer.md"

        # Launch Claude Code (interactive session)
        try:
            subprocess.run(
                ['claude', prompt],
                cwd=Path(__file__).parent
            )
        except FileNotFoundError:
            print("\nCould not find 'claude' command.")
            print("Make sure Claude Code CLI is installed and in your PATH.")
            input("Press Enter to continue...")
            return
        except KeyboardInterrupt:
            pass

        # Check for answer file
        print("\n" + "=" * 70)
        print("RETURNING FROM CLAUDE CODE SESSION")
        print("=" * 70)

        if answer_file.exists():
            with open(answer_file, 'r') as f:
                answer = f.read().strip()

            if answer:
                print(f"\nFound answer ({len(answer)} characters):\n")
                print("-" * 50)
                preview = answer[:500] + "..." if len(answer) > 500 else answer
                print(preview)
                print("-" * 50)

                save_choice = input("\nSave this answer? [Y/n]: ").strip().lower()
                if save_choice != 'n':
                    self.helper.save_answer(question_id, answer, status='complete')
                    self.helper.log_event("answer_saved", question_id, {
                        "source": "claude_session",
                        "answer_length": len(answer)
                    })
                    print("Answer saved to database!")
                    # Clean up
                    answer_file.unlink()
                else:
                    self.helper.log_event("answer_declined", question_id)
                    print("Answer not saved. File preserved at .sea_answer.md")
            else:
                print("\nAnswer file was empty. No changes made.")
        else:
            print("\nNo answer file found (.sea_answer.md)")
            print("The collaborative session may not have produced a final answer.")
            print("You can still work on this question later.")

        # Clean up context file
        if context_file.exists():
            context_file.unlink()

        input("\nPress Enter to continue...")

    def review_business_directions(self):
        """Review and select business direction"""
        self.clear_screen()
        self.show_header()

        print("BUSINESS DIRECTION\n")

        directions = self.helper.get_business_directions()

        if not directions:
            print("No business directions configured.")
            print("Add them to questions_config.json or use the helper programmatically.")
            input("\nPress Enter to continue...")
            return

        for d in directions:
            selected = "[x]" if d['selected'] else "[ ]"
            print(f"{selected} {d['id']}. {d['name']}")
            print(f"    {d['description']}\n")

        print("\nThoughts to consider:")
        print("- Multiple directions can coexist")
        print("- Start with one as primary, other as secondary")
        print("- They can complement each other\n")

        print("Options:")
        for d in directions:
            print(f"  [{d['id']}] Select Direction {d['id']} as primary")
        print("  [B] Back to menu")
        print()

        choice = input("Your choice: ").strip().upper()

        if choice == 'B':
            return

        try:
            direction_id = int(choice)
            self.helper.select_business_direction(direction_id)
            print(f"\nDirection {direction_id} selected as primary focus")
            input("\nPress Enter to continue...")
        except ValueError:
            pass

    def browse_sections(self):
        """Browse questions by section"""
        while True:
            self.clear_screen()
            self.show_header()

            print("SECTIONS\n")

            sections = self.helper.get_sections()

            for section in sections:
                questions = self.helper.get_questions_by_section(section['id'])
                complete = sum(1 for q in questions if q.get('status') == 'complete')
                total = len(questions)
                print(f"  [{section['id']}] {section['title']:30} ({complete}/{total} complete)")

            print("\n  [B] Back to main menu\n")

            choice = input("Select section: ").strip()

            if choice.upper() == 'B':
                return

            try:
                section_id = int(choice)
                sections_ids = [s['id'] for s in sections]
                if section_id in sections_ids:
                    self.view_section(section_id)
            except ValueError:
                pass

    def view_section(self, section_id):
        """View all questions in a section"""
        questions = self.helper.get_questions_by_section(section_id)

        if not questions:
            print("No questions in this section")
            input("\nPress Enter to continue...")
            return

        section_name = questions[0].get('section_title', f'Section {section_id}')

        while True:
            self.clear_screen()
            self.show_header()

            print(f"{section_name}\n")

            for i, q in enumerate(questions, 1):
                status = q.get('status', 'not_started') or 'not_started'
                icon = "+" if status == 'complete' else "~" if status == 'in_progress' else "o"
                print(f"  {icon} [{q['id']}] {q['question_text'][:55]}...")

            print("\n  [ID] Work on specific question (e.g., '1', '2a')")
            print("  [c:ID] Work with Claude on question (e.g., 'c:1', 'c:2a')")
            print("  [B] Back to sections\n")

            choice = input("Your choice: ").strip()

            if choice.upper() == 'B':
                return

            # Check for Claude prefix
            if choice.lower().startswith('c:'):
                q_id = choice[2:]
                q_match = [q for q in questions if q['id'] == q_id]
                if q_match:
                    self.work_with_claude(q_id)
                continue

            # Check if it's a valid question ID
            q_match = [q for q in questions if q['id'] == choice]
            if q_match:
                self.answer_question(choice)

    def show_dashboard(self):
        """Show detailed progress dashboard"""
        self.clear_screen()
        self.show_header()

        print("PROGRESS DASHBOARD\n")

        progress = self.helper.get_progress()

        # Overall progress
        bar_length = 50
        filled = int(bar_length * progress['complete'] / progress['total']) if progress['total'] > 0 else 0
        bar = '#' * filled + '-' * (bar_length - filled)

        print(f"Overall: [{bar}] {progress['percent_complete']:.1f}%")
        print(f"         {progress['complete']} complete, {progress['in_progress']} in progress, {progress['not_started']} not started\n")

        # Progress by section
        print("By Section:")
        sections = self.helper.get_sections()
        for section in sections:
            questions = self.helper.get_questions_by_section(section['id'])
            if questions:
                complete = sum(1 for q in questions if q.get('status') == 'complete')
                total = len(questions)
                pct = (complete / total * 100) if total > 0 else 0
                mini_bar = '#' * int(20 * complete / total) if total > 0 else ''
                mini_bar += '-' * (20 - len(mini_bar))
                print(f"  {section['title']:30} [{mini_bar}] {complete}/{total} ({pct:.0f}%)")

        print("\n")
        input("Press Enter to continue...")

    def export_answers(self):
        """Export answers to JSON file"""
        self.clear_screen()
        self.show_header()

        print("EXPORT ANSWERS\n")

        filepath = self.helper.export_answers()

        print(f"Answers exported to: {filepath}")
        print("\nThis JSON file contains all your answers and notes.")
        print("You can review it, share it, or use it to fill out the paper form.\n")

        input("Press Enter to continue...")

    def show_tips(self):
        """Show tips for answering questions"""
        self.clear_screen()
        self.show_header()

        print("TIPS FOR SUCCESS\n")

        tips = [
            ("Start with priorities", "Focus on Priority 1 questions first. These are the foundation."),
            ("Use Claude for help", "Press [C] to launch a collaborative AI session for any question."),
            ("Use 'draft' mode", "Type 'draft' as an answer to mark questions you need to return to."),
            ("Break it down", "Long questions? Break them into bullet points, then write prose later."),
            ("Be specific", "Use concrete examples, names, numbers, dates."),
            ("Show your math", "When they ask numbers, show your calculations. It builds confidence."),
            ("Take breaks", "Work in focused sprints, then rest. Progress beats perfection."),
            ("Save notes", "Random thoughts? Save as notes. Don't lose ideas."),
            ("Export often", "Export your progress regularly. Backup your work."),
        ]

        for i, (title, desc) in enumerate(tips, 1):
            print(f"{i}. {title}")
            print(f"   {desc}\n")

        input("Press Enter to continue...")

    def show_session_history(self):
        """Show session history - track your journey"""
        self.clear_screen()
        self.show_header()

        print("SESSION HISTORY\n")
        print("Your journey through the application:\n")

        events = self.helper.get_session_history()

        if not events:
            print("No session history yet. Start working on questions to build your journey!")
            input("\nPress Enter to continue...")
            return

        # Show recent events
        recent = events[-20:] if len(events) > 20 else events
        print(f"Showing {len(recent)} most recent events (of {len(events)} total):\n")

        for event in recent:
            timestamp = event.get('timestamp', '')[:16].replace('T', ' ')
            event_type = event.get('event', 'unknown')
            q_id = event.get('question_id', '')

            # Format event nicely
            if event_type == 'claude_session_start':
                print(f"  [{timestamp}] Started Claude session for Q{q_id}")
            elif event_type == 'answer_saved':
                source = event.get('source', 'unknown')
                length = event.get('answer_length', 0)
                print(f"  [{timestamp}] Saved answer for Q{q_id} ({source}, {length} chars)")
            elif event_type == 'answer_declined':
                print(f"  [{timestamp}] Declined Claude answer for Q{q_id}")
            elif event_type == 'notes_added':
                print(f"  [{timestamp}] Added notes for Q{q_id}")
            else:
                print(f"  [{timestamp}] {event_type} - Q{q_id}")

        # Summary stats
        print("\n" + "-" * 50)
        print("Summary:")
        claude_sessions = len([e for e in events if e.get('event') == 'claude_session_start'])
        answers_saved = len([e for e in events if e.get('event') == 'answer_saved'])
        notes_added = len([e for e in events if e.get('event') == 'notes_added'])
        print(f"  Claude sessions: {claude_sessions}")
        print(f"  Answers saved: {answers_saved}")
        print(f"  Notes added: {notes_added}")

        # Questions with most activity
        question_counts = {}
        for e in events:
            q_id = e.get('question_id')
            if q_id:
                question_counts[q_id] = question_counts.get(q_id, 0) + 1

        if question_counts:
            print("\nMost worked-on questions:")
            sorted_qs = sorted(question_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for q_id, count in sorted_qs:
                print(f"  Q{q_id}: {count} events")

        input("\nPress Enter to continue...")

    def switch_form(self):
        """Switch to a different form/config"""
        self.clear_screen()
        self.show_header()

        print("SWITCH FORM\n")
        print(f"Current form: {self.form_info['name']}\n")

        configs = list_available_configs()

        if not configs:
            print("No other forms available in examples/ directory.")
            input("\nPress Enter to continue...")
            return

        print("Available forms:\n")
        for i, cfg in enumerate(configs, 1):
            current = " (current)" if cfg['name'] == self.form_info['name'] else ""
            print(f"  [{i}] {cfg['name']}{current}")
            print(f"      {cfg['questions']} questions")
            print()

        print("  [B] Back to menu")
        print()

        print("Note: Each form has its own database. Your progress is saved separately.")
        print()

        choice = input("Select form: ").strip()

        if choice.upper() == 'B':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(configs):
                selected = configs[idx]

                # Copy to active config
                config_path = get_config_path()
                shutil.copy(selected['path'], config_path)

                # Reinitialize with new config
                db_path = get_db_path_for_config(config_path)
                self.helper.close()
                self.helper = SEAApplicationHelper(db_path=str(db_path), config_path=str(config_path))
                self.form_info = self.helper.get_form_info()

                print(f"\nSwitched to: {selected['name']}")
                print(f"Database: {db_path.name}")
                input("\nPress Enter to continue...")
                return
        except ValueError:
            pass

        print("Invalid choice.")
        input("\nPress Enter to continue...")

    def run(self):
        """Main application loop - Choose Your Own Adventure!"""
        while self.running:
            self.show_menu()

            choice = input("Your choice: ").strip()

            if choice == '1':
                self.work_on_priorities()
            elif choice == '2':
                if self.has_business_directions():
                    self.review_business_directions()
                else:
                    print("\nThis form doesn't have business directions configured.")
                    input("Press Enter to continue...")
            elif choice == '3':
                self.browse_sections()
            elif choice == '4':
                q_id = input("\nEnter question ID (e.g., '1', '2a', '34b'): ").strip()
                q = self.helper.get_question(q_id)
                if q:
                    self.answer_question(q_id)
                else:
                    print(f"\nQuestion '{q_id}' not found")
                    input("Press Enter to continue...")
            elif choice == '5':
                self.show_dashboard()
            elif choice == '6':
                self.export_answers()
            elif choice == '7':
                self.show_tips()
            elif choice == '8':
                self.show_session_history()
            elif choice == '9':
                self.switch_form()
            elif choice.upper() == 'C':
                q_id = input("\nEnter question ID to work on with Claude (e.g., '1', '2a', '34b'): ").strip()
                q = self.helper.get_question(q_id)
                if q:
                    self.work_with_claude(q_id)
                else:
                    print(f"\nQuestion '{q_id}' not found")
                    input("Press Enter to continue...")
            elif choice.upper() == 'Q':
                print("\nSaving and exiting...")
                self.helper.export_answers()
                self.helper.close()
                self.running = False
                print("Done! Your work is saved.\n")
            else:
                print("\nInvalid choice. Try again.")
                input("Press Enter to continue...")


def main():
    assistant = InteractiveAssistant()
    try:
        assistant.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Saving your work...")
        assistant.helper.export_answers()
        assistant.helper.close()
        print("Done!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
