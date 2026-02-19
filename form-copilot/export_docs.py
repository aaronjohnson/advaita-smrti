#!/usr/bin/env python3
"""
Export form-copilot databases to Markdown, Texinfo, or LaTeX format.

Usage:
    python3 export_docs.py                     # Export current form to markdown
    python3 export_docs.py --format texinfo    # Export to texinfo
    python3 export_docs.py --format latex      # Export to LaTeX (Tufte margin notes)
    python3 export_docs.py --all               # Export all databases
    python3 export_docs.py --combine           # Combine all into one document
    python3 export_docs.py db1.db db2.db       # Export specific databases

    # Export from memory layer (no SQLite needed):
    python3 export_docs.py --memory .memory --config questions.json --format latex

Output formats:
    markdown (default) - Good for viewing on GitHub, simple editing
    texinfo            - Build to PDF, HTML, or Info with makeinfo
    latex              - Tufte-style margin notes with clickable cross-references
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

try:
    from memory import Memory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

# SQLite helper is deprecated; only loaded if needed for legacy database export
try:
    from sea_application_helper import SEAApplicationHelper
    SQLITE_HELPER_AVAILABLE = True
except ImportError:
    SQLITE_HELPER_AVAILABLE = False


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


def _load_memory_answers(config_path, memory_path):
    """Load config and answers from memory layer. Returns (config, answers dict)."""
    with open(config_path) as f:
        config = json.load(f)

    mem = Memory(memory_path, prefix="fc")
    answers = {}
    for t in mem.tasks.all():
        qid = t.metadata.get('question_id')
        if qid and t.status == 'closed':
            answers[qid] = t.description
    mem.close()

    return config, answers


def export_markdown_from_memory(config_path, memory_path=".memory",
                                output_path=None):
    """Export answers from memory layer to Markdown.

    Args:
        config_path: Path to JSON config
        memory_path: Path to memory layer directory
        output_path: Output .md path

    Returns:
        Path to output file
    """
    config, answers = _load_memory_answers(config_path, memory_path)

    form_name = config.get('form_name', 'Form Export')
    form_desc = config.get('form_description', '')
    total = len(config['questions'])
    done = len(answers)

    sections = {s['id']: s for s in config['sections']}
    by_section = {}
    for q in config['questions']:
        by_section.setdefault(q['section_id'], []).append(q)

    lines = []
    lines.append(f"# {form_name}")
    lines.append("")
    if form_desc:
        lines.append(f"> {form_desc}")
        lines.append("")
    lines.append(f"**Progress:** {done}/{total} questions answered")
    lines.append(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for sid in sorted(sections.keys()):
        s = sections[sid]
        lines.append(f"## {s['title']}")
        if s.get('description'):
            lines.append(f"*{s['description']}*")
        lines.append("")

        qs = sorted(by_section.get(sid, []), key=lambda x: x['id'])
        for q in qs:
            qid = q['id']
            priority = q.get('priority', 3)
            has_answer = qid in answers
            icon = {True: "\u2713", False: "\u25cb"}[has_answer]

            lines.append(f"### {icon} Q{qid} (P{priority}): {q['question_text']}")
            lines.append("")

            if q.get('helper_text'):
                lines.append(f"*Hint: {q['helper_text']}*")
                lines.append("")

            if has_answer:
                lines.append(answers[qid])
            else:
                lines.append("*No answer yet*")
            lines.append("")
            lines.append("---")
            lines.append("")

    if output_path is None:
        safe_name = form_name.lower().replace(' ', '_').replace('-', '_')
        output_path = f"{safe_name}_export.md"

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Markdown: {output_path}")
    return str(output_path)


def export_texinfo_from_memory(config_path, memory_path=".memory",
                               output_path=None):
    """Export answers from memory layer to Texinfo.

    Args:
        config_path: Path to JSON config
        memory_path: Path to memory layer directory
        output_path: Output .texi path

    Returns:
        Path to output file
    """
    config, answers = _load_memory_answers(config_path, memory_path)

    form_name = config.get('form_name', 'Form Export')
    form_desc = config.get('form_description', '')
    total = len(config['questions'])
    done = len(answers)

    sections = {s['id']: s for s in config['sections']}
    by_section = {}
    for q in config['questions']:
        by_section.setdefault(q['section_id'], []).append(q)

    def esc(text):
        if not text:
            return ""
        return text.replace('@', '@@').replace('{', '@{').replace('}', '@}')

    lines = []
    lines.append("\\input texinfo")
    lines.append(f"@settitle {esc(form_name)}")
    lines.append("@documentencoding UTF-8")
    lines.append("")
    lines.append("@titlepage")
    lines.append(f"@title {esc(form_name)}")
    if form_desc:
        lines.append(f"@subtitle {esc(form_desc)}")
    lines.append(f"@subtitle Progress: {done}/{total} questions answered")
    lines.append(f"@subtitle Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("@end titlepage")
    lines.append("")
    lines.append("@contents")
    lines.append("")
    lines.append("@ifnottex")
    lines.append("@node Top")
    lines.append(f"@top {esc(form_name)}")
    lines.append("@end ifnottex")
    lines.append("")

    # Top-level menu
    lines.append("@menu")
    for sid in sorted(sections.keys()):
        s = sections[sid]
        node = s['title'].replace(' ', '-')
        lines.append(f"* {node}:: {esc(s.get('description', s['title']))}")
    lines.append("@end menu")
    lines.append("")

    for sid in sorted(sections.keys()):
        s = sections[sid]
        node = s['title'].replace(' ', '-')
        lines.append(f"@node {node}")
        lines.append(f"@chapter {esc(s['title'])}")
        lines.append("")
        if s.get('description'):
            lines.append(esc(s['description']))
            lines.append("")

        qs = sorted(by_section.get(sid, []), key=lambda x: x['id'])
        for q in qs:
            qid = q['id']
            priority = q.get('priority', 3)

            lines.append(f"@section Q{qid} (Priority {priority})")
            lines.append("")
            lines.append(f"@strong{{{esc(q['question_text'])}}}")
            lines.append("")

            if q.get('helper_text'):
                lines.append("@quotation Hint")
                lines.append(esc(q['helper_text']))
                lines.append("@end quotation")
                lines.append("")

            if qid in answers:
                lines.append("@quotation Answer")
                lines.append(esc(answers[qid]))
                lines.append("@end quotation")
            else:
                lines.append("@emph{No answer yet}")
            lines.append("")

    lines.append("@bye")

    if output_path is None:
        safe_name = form_name.lower().replace(' ', '_').replace('-', '_')
        output_path = f"{safe_name}_export.texi"

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Texinfo: {output_path}")
    print(f"  Build PDF:  makeinfo --pdf {output_path}")
    print(f"  Build HTML: makeinfo --html {output_path}")
    print(f"  Build Info: makeinfo {output_path}")
    return str(output_path)


def _escape_latex(s):
    """Escape text for safe inclusion in LaTeX"""
    if not s:
        return ''
    s = s.replace('\\', r'\textbackslash{}')
    for c in ['&', '%', '$', '#', '_', '{', '}']:
        s = s.replace(c, '\\' + c)
    s = s.replace('~', r'\textasciitilde{}')
    s = s.replace('^', r'\textasciicircum{}')
    s = s.replace('\u2014', '---')
    s = s.replace('\u2013', '--')
    s = s.replace('\u201c', "``")
    s = s.replace('\u201d', "''")
    s = s.replace('\u2019', "'")
    s = s.replace('\u2018', "`")
    return s


def _format_latex_answer(text):
    """Convert answer text to LaTeX with itemize support and bold headers"""
    if not text:
        return ''
    result = []
    paragraphs = text.strip().split('\n\n')
    for para in paragraphs:
        lines = para.strip().split('\n')
        bullet_lines = [l for l in lines if l.strip().startswith('- ') or l.strip().startswith('* ')]
        non_bullet = [l for l in lines if l.strip() and not l.strip().startswith('- ') and not l.strip().startswith('* ')]
        if bullet_lines and len(bullet_lines) >= len(non_bullet):
            for l in lines:
                stripped = l.strip()
                if stripped and not stripped.startswith('- ') and not stripped.startswith('* '):
                    result.append(_escape_latex(stripped))
                    result.append('')
            result.append(r'\begin{itemize}')
            for l in bullet_lines:
                item_text = l.strip()[2:]
                if ':' in item_text and item_text.index(':') < 40:
                    label, rest = item_text.split(':', 1)
                    result.append(r'\item \textbf{' + _escape_latex(label) + ':}' + _escape_latex(rest))
                else:
                    result.append(r'\item ' + _escape_latex(item_text))
            result.append(r'\end{itemize}')
            result.append('')
        else:
            text_line = ' '.join(l.strip() for l in lines)
            clean = text_line.replace('**', '')
            if ':' in clean and clean.index(':') < 50 and not clean.startswith('http'):
                label, rest = clean.split(':', 1)
                if rest.strip():
                    result.append(r'\textbf{' + _escape_latex(label) + ':}' + _escape_latex(rest))
                else:
                    result.append(r'\textbf{' + _escape_latex(label) + '}')
            else:
                result.append(_escape_latex(clean))
            result.append('')
    return '\n'.join(result)


def export_latex_from_memory(config_path, memory_path=".memory",
                             output_path=None, compile_pdf=True):
    """Export answers from memory layer to LaTeX with Tufte-style margin notes.

    Produces a PDF with:
    - Wide right margins containing helper hints, priority badges,
      and clickable cross-references between questions
    - Clean typeset answers in the main column
    - Internal hyperlinks for navigation

    Args:
        config_path: Path to JSON config defining questions/sections
        memory_path: Path to memory layer directory
        output_path: Output .tex path (default: derived from form name)
        compile_pdf: If True, run pdflatex to produce PDF

    Returns:
        Path to the output file (.pdf if compiled, .tex otherwise)
    """
    with open(config_path) as f:
        config = json.load(f)

    form_name = config.get('form_name', 'Form Export')
    form_desc = config.get('form_description', '')

    mem = Memory(memory_path, prefix="fc")
    answers = {}
    for t in mem.tasks.all():
        qid = t.metadata.get('question_id')
        if qid and t.status == 'closed':
            answers[qid] = t.description
    mem.close()

    sections = {s['id']: s for s in config['sections']}
    by_section = {}
    questions_by_id = {}
    for q in config['questions']:
        sid = q['section_id']
        by_section.setdefault(sid, []).append(q)
        questions_by_id[q['id']] = q

    def find_related(qid):
        q = questions_by_id.get(qid, {})
        section_id = q.get('section_id')
        related = []
        for oq in by_section.get(section_id, []):
            if oq['id'] != qid and oq['id'] in answers:
                related.append(oq['id'])
        return related[:3]

    def qid_anchor(qid):
        return 'q' + str(qid).replace(' ', '')

    esc = _escape_latex
    total = len(config['questions'])
    done = len(answers)

    lines = []
    lines.append(r'\documentclass[letterpaper]{tufte-handout}')
    lines.append(r'')
    lines.append(r'\usepackage[T1]{fontenc}')
    lines.append(r'\usepackage{lmodern}')
    lines.append(r'\usepackage{microtype}')
    lines.append(r'\usepackage{enumitem}')
    lines.append(r'\usepackage{xcolor}')
    lines.append(r'')
    lines.append(r'\hypersetup{')
    lines.append(r'    colorlinks=true,')
    lines.append(r'    linkcolor={blue!60!black},')
    lines.append(r'    urlcolor={blue!60!black},')
    lines.append(r'    pdftitle={' + esc(form_name) + r'},')
    lines.append(r'}')
    lines.append(r'')
    lines.append(r'\definecolor{hint}{RGB}{100,120,80}')
    lines.append(r'\definecolor{priority}{RGB}{160,80,40}')
    lines.append(r'\definecolor{xref}{RGB}{60,80,140}')
    lines.append(r'\definecolor{sectionhead}{RGB}{40,50,80}')
    lines.append(r'')
    lines.append(r'\setlist[itemize]{leftmargin=1.2em,itemsep=0.15em,topsep=0.3em}')
    lines.append(r'')
    lines.append(r'\renewcommand{\section}[1]{'
                 r'\par\bigskip\noindent{\Large\bfseries\color{sectionhead}#1}'
                 r'\par\medskip\noindent\hrule\medskip}')
    lines.append(r'\renewcommand{\subsection}[1]{'
                 r'\par\medskip\noindent{\large\bfseries #1}\par\smallskip}')
    lines.append(r'')
    lines.append(r'\title{\textbf{' + esc(form_name) + r'}'
                 r'\\[0.3em]\Large Application Responses}')
    lines.append(r'\date{' + datetime.now().strftime('%B %Y') + r'}')
    lines.append(r'')
    lines.append(r'\begin{document}')
    lines.append(r'\maketitle')
    lines.append(r'')
    lines.append(r'\begin{abstract}')
    lines.append(r'\noindent ' + esc(form_desc)
                 + r' Progress: ' + str(done) + '/' + str(total)
                 + r' questions answered.')
    lines.append(r'\end{abstract}')
    lines.append(r'\bigskip')
    lines.append(r'')

    for sid in sorted(sections.keys()):
        s = sections[sid]
        lines.append(r'\section{' + esc(s['title']) + r'}')
        if s.get('description'):
            lines.append(r'\marginnote{\textit{' + esc(s['description']) + r'}}')
        lines.append('')

        qs = sorted(by_section.get(sid, []), key=lambda x: x['id'])
        for q in qs:
            qid = q['id']
            anchor = qid_anchor(qid)
            priority = q.get('priority', 3)

            lines.append(r'\hypertarget{' + anchor + r'}{}')
            lines.append(r'\subsection{Q' + esc(qid) + ': '
                         + esc(q['question_text']) + r'}')

            # Build margin content
            margin_parts = []
            plabel = {1: 'Foundation', 2: 'Important', 3: 'Optional'}.get(priority, '')
            margin_parts.append(
                r'{\color{priority}\textsc{Priority ' + str(priority)
                + r' --- ' + plabel + r'}}')

            if q.get('helper_text'):
                margin_parts.append(
                    r'{\color{hint}\small\textit{' + esc(q['helper_text']) + r'}}')

            related = find_related(qid)
            if related:
                xlinks = [r'\hyperlink{' + qid_anchor(r) + r'}{Q' + esc(r) + r'}'
                          for r in related]
                margin_parts.append(
                    r'{\color{xref}\small See also ' + ', '.join(xlinks) + r'}')

            if q.get('depends_on'):
                dep = q['depends_on']
                margin_parts.append(
                    r'{\small Follows \hyperlink{' + qid_anchor(dep)
                    + r'}{Q' + esc(dep) + r'}}')

            lines.append(r'\marginnote{' + r'\\[0.4em]'.join(margin_parts) + r'}')
            lines.append('')

            answer = answers.get(qid, 'No answer provided.')
            lines.append(_format_latex_answer(answer))
            lines.append(r'\bigskip')
            lines.append('')

    lines.append(r'\end{document}')

    # Write .tex
    if output_path is None:
        safe_name = form_name.lower().replace(' ', '_').replace('-', '_')
        output_path = f"{safe_name}_marginal.tex"
    output_path = Path(output_path)

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"LaTeX source: {output_path}")

    # Compile to PDF
    if compile_pdf:
        try:
            for _ in range(2):  # Two passes for hyperlinks
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', str(output_path)],
                    capture_output=True, text=True, timeout=60
                )
            pdf_path = output_path.with_suffix('.pdf')
            if pdf_path.exists():
                print(f"PDF output:   {pdf_path}")
                # Clean auxiliary files
                for ext in ['.aux', '.log', '.out']:
                    aux = output_path.with_suffix(ext)
                    if aux.exists():
                        aux.unlink()
                return str(pdf_path)
            else:
                print("Warning: pdflatex did not produce a PDF. Check the .tex file.")
                return str(output_path)
        except FileNotFoundError:
            print("pdflatex not found. Install texlive-latex-base for PDF output.")
            print(f"You can compile manually: pdflatex {output_path}")
            return str(output_path)
        except subprocess.TimeoutExpired:
            print("pdflatex timed out. You can compile manually.")
            return str(output_path)

    return str(output_path)


def export_latex_from_helper(helper, output_path=None, compile_pdf=True):
    """Export from SEAApplicationHelper (SQLite) to LaTeX with margin notes.

    Args:
        helper: SEAApplicationHelper instance
        output_path: Output .tex path
        compile_pdf: If True, run pdflatex

    Returns:
        Path to output file
    """
    form_info = helper.get_form_info()
    form_name = form_info.get('name', 'Form Export')
    form_desc = form_info.get('description', '')
    sections = helper.get_sections()
    progress = helper.get_progress()

    esc = _escape_latex

    # Collect all questions and answers
    all_questions = {}
    answers = {}
    by_section = {}
    for section in sections:
        qs = helper.get_questions_by_section(section['id'])
        by_section[section['id']] = qs
        for q in qs:
            all_questions[q['id']] = q
            if q.get('answer_text'):
                answers[q['id']] = q['answer_text']

    def find_related(qid):
        q = all_questions.get(qid, {})
        section_id = q.get('section_id')
        related = []
        for oq in by_section.get(section_id, []):
            if oq['id'] != qid and oq['id'] in answers:
                related.append(oq['id'])
        return related[:3]

    def qid_anchor(qid):
        return 'q' + str(qid).replace(' ', '')

    lines = []
    lines.append(r'\documentclass[letterpaper]{tufte-handout}')
    lines.append(r'')
    lines.append(r'\usepackage[T1]{fontenc}')
    lines.append(r'\usepackage{lmodern}')
    lines.append(r'\usepackage{microtype}')
    lines.append(r'\usepackage{enumitem}')
    lines.append(r'\usepackage{xcolor}')
    lines.append(r'')
    lines.append(r'\hypersetup{')
    lines.append(r'    colorlinks=true,')
    lines.append(r'    linkcolor={blue!60!black},')
    lines.append(r'    urlcolor={blue!60!black},')
    lines.append(r'    pdftitle={' + esc(form_name) + r'},')
    lines.append(r'}')
    lines.append(r'')
    lines.append(r'\definecolor{hint}{RGB}{100,120,80}')
    lines.append(r'\definecolor{priority}{RGB}{160,80,40}')
    lines.append(r'\definecolor{xref}{RGB}{60,80,140}')
    lines.append(r'\definecolor{sectionhead}{RGB}{40,50,80}')
    lines.append(r'')
    lines.append(r'\setlist[itemize]{leftmargin=1.2em,itemsep=0.15em,topsep=0.3em}')
    lines.append(r'')
    lines.append(r'\renewcommand{\section}[1]{'
                 r'\par\bigskip\noindent{\Large\bfseries\color{sectionhead}#1}'
                 r'\par\medskip\noindent\hrule\medskip}')
    lines.append(r'\renewcommand{\subsection}[1]{'
                 r'\par\medskip\noindent{\large\bfseries #1}\par\smallskip}')
    lines.append(r'')
    lines.append(r'\title{\textbf{' + esc(form_name) + r'}'
                 r'\\[0.3em]\Large Application Responses}')
    lines.append(r'\date{' + datetime.now().strftime('%B %Y') + r'}')
    lines.append(r'')
    lines.append(r'\begin{document}')
    lines.append(r'\maketitle')
    lines.append(r'')
    lines.append(r'\begin{abstract}')
    lines.append(r'\noindent ' + esc(form_desc)
                 + r' Progress: ' + str(progress['complete'])
                 + '/' + str(progress['total'])
                 + r' questions answered.')
    lines.append(r'\end{abstract}')
    lines.append(r'\bigskip')
    lines.append(r'')

    for section in sections:
        lines.append(r'\section{' + esc(section['title']) + r'}')
        if section.get('description'):
            lines.append(r'\marginnote{\textit{' + esc(section['description']) + r'}}')
        lines.append('')

        for q in by_section.get(section['id'], []):
            qid = q['id']
            anchor = qid_anchor(qid)
            priority = q.get('priority', 3)

            lines.append(r'\hypertarget{' + anchor + r'}{}')
            lines.append(r'\subsection{Q' + esc(str(qid)) + ': '
                         + esc(q['question_text']) + r'}')

            margin_parts = []
            plabel = {1: 'Foundation', 2: 'Important', 3: 'Optional'}.get(priority, '')
            margin_parts.append(
                r'{\color{priority}\textsc{Priority ' + str(priority)
                + r' --- ' + plabel + r'}}')

            if q.get('helper_text'):
                margin_parts.append(
                    r'{\color{hint}\small\textit{' + esc(q['helper_text']) + r'}}')

            related = find_related(qid)
            if related:
                xlinks = [r'\hyperlink{' + qid_anchor(r) + r'}{Q' + esc(str(r)) + r'}'
                          for r in related]
                margin_parts.append(
                    r'{\color{xref}\small See also ' + ', '.join(xlinks) + r'}')

            if q.get('depends_on'):
                dep = q['depends_on']
                margin_parts.append(
                    r'{\small Follows \hyperlink{' + qid_anchor(dep)
                    + r'}{Q' + esc(str(dep)) + r'}}')

            lines.append(r'\marginnote{' + r'\\[0.4em]'.join(margin_parts) + r'}')
            lines.append('')

            answer = q.get('answer_text', 'No answer provided.')
            lines.append(_format_latex_answer(answer or 'No answer provided.'))
            lines.append(r'\bigskip')
            lines.append('')

    lines.append(r'\end{document}')

    if output_path is None:
        safe_name = form_name.lower().replace(' ', '_').replace('-', '_')
        output_path = f"{safe_name}_marginal.tex"
    output_path = Path(output_path)

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"LaTeX source: {output_path}")

    if compile_pdf:
        try:
            for _ in range(2):
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', str(output_path)],
                    capture_output=True, text=True, timeout=60
                )
            pdf_path = output_path.with_suffix('.pdf')
            if pdf_path.exists():
                print(f"PDF output:   {pdf_path}")
                for ext in ['.aux', '.log', '.out']:
                    aux = output_path.with_suffix(ext)
                    if aux.exists():
                        aux.unlink()
                return str(pdf_path)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("pdflatex not available. Compile manually.")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Export form-copilot answers to Markdown, Texinfo, or LaTeX',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # From SQLite database:
    python3 export_docs.py                          # Export current form to markdown
    python3 export_docs.py --format texinfo         # Export to texinfo
    python3 export_docs.py --format latex           # Export to LaTeX (Tufte margins)
    python3 export_docs.py --all --combine          # Combine all into one document

    # From memory layer (preferred):
    python3 export_docs.py --memory .memory --config config.json
    python3 export_docs.py --memory .memory --config config.json --format latex
    python3 export_docs.py --memory .memory --config config.json --format latex --no-pdf

After texinfo export, build with:
    makeinfo --pdf file.texi      # PDF output
    makeinfo --html file.texi     # HTML output
    makeinfo file.texi            # Info format
        """
    )

    parser.add_argument('databases', nargs='*', help='Specific database files to export')
    parser.add_argument('--format', '-f', choices=['markdown', 'texinfo', 'latex'],
                        default='markdown',
                        help='Output format (default: markdown)')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Export all .db files found')
    parser.add_argument('--combine', '-c', action='store_true',
                        help='Combine multiple databases into one document')
    parser.add_argument('--output', '-o', help='Output filename')
    parser.add_argument('--memory', '-m', metavar='PATH',
                        help='Memory layer directory (use instead of SQLite)')
    parser.add_argument('--config', metavar='PATH',
                        help='JSON config file (required with --memory)')
    parser.add_argument('--no-pdf', action='store_true',
                        help='Skip PDF compilation for latex format')

    args = parser.parse_args()

    # Memory layer path: export from memory + config
    if args.memory:
        if not args.config:
            print("Error: --config is required when using --memory")
            sys.exit(1)
        if not Path(args.memory).exists():
            print(f"Error: Memory directory not found: {args.memory}")
            sys.exit(1)
        if not Path(args.config).exists():
            print(f"Error: Config file not found: {args.config}")
            sys.exit(1)

        if args.format == 'latex':
            filepath = export_latex_from_memory(
                args.config, args.memory,
                output_path=args.output,
                compile_pdf=not args.no_pdf
            )
        elif args.format == 'texinfo':
            filepath = export_texinfo_from_memory(
                args.config, args.memory,
                output_path=args.output
            )
        elif args.format == 'markdown':
            filepath = export_markdown_from_memory(
                args.config, args.memory,
                output_path=args.output
            )

        print(f"\nExported: {filepath}")
        return 0

    # SQLite path: existing behavior
    if args.databases:
        db_paths = [Path(db) for db in args.databases]
    elif args.all:
        db_paths = find_databases()
    else:
        config_path = Path('questions_config.json')
        if config_path.exists():
            with open(config_path) as f:
                cfg = json.load(f)
            form_name = cfg.get('form_name', 'form')
            safe_name = form_name.lower().replace(' ', '_').replace('-', '_')
            db_path = Path(f"{safe_name}.db")
            if db_path.exists():
                db_paths = [db_path]
            else:
                db_paths = find_databases()[:1]
        else:
            db_paths = find_databases()[:1]

    if not db_paths:
        print("No databases found.")
        print("Use --memory .memory --config config.json to export from memory layer,")
        print("or run sea_assistant.py first to create a database.")
        sys.exit(1)

    db_paths = [p for p in db_paths if p.exists()]
    if not db_paths:
        print("Specified database files not found.")
        sys.exit(1)

    print(f"Found {len(db_paths)} database(s): {', '.join(str(p) for p in db_paths)}")

    # Export
    if args.format == 'latex':
        for db_path in db_paths:
            helper = SEAApplicationHelper(db_path=str(db_path))
            filepath = export_latex_from_helper(
                helper, output_path=args.output,
                compile_pdf=not args.no_pdf
            )
            helper.close()
            print(f"Exported: {db_path} -> {filepath}")
    elif args.combine and len(db_paths) > 1:
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
