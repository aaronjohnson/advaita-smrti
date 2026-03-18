#!/usr/bin/env python3
"""
Build a combined Texinfo document from all RFC markdown files.

Usage:
    python docs/rfcs/build_texi.py              # writes smrti-rfcs.texi
    python docs/rfcs/build_texi.py --info       # also runs makeinfo
    python docs/rfcs/build_texi.py --pdf        # also runs texi2pdf
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

RFC_DIR = Path(__file__).parent
RFC_FILES = sorted(RFC_DIR.glob("[0-9]*.md"),
                   key=lambda f: int(re.match(r"(\d+)", f.name).group(1)))
OUTPUT = RFC_DIR / "smrti-rfcs.texi"


def _clean_inline(text: str) -> str:
    """Convert inline markdown to Texinfo."""
    text = text.replace("@", "@@").replace("{", "@{").replace("}", "@}")
    text = re.sub(r"\*\*(.+?)\*\*", r"@strong{\1}", text)
    text = re.sub(r"\*(.+?)\*", r"@emph{\1}", text)
    text = re.sub(r"`([^`]+)`", r"@code{\1}", text)

    def replace_link(m):
        label, url = m.group(1), m.group(2)
        label = label.replace("@@", "@").replace("@{", "{").replace("@}", "}")
        if url.endswith(".md"):
            return f"@strong{{{label}}}"
        return f"@uref{{{url}, {label}}}"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)
    return text


def _flush_table(rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    ncols = len(rows[0])
    col_spec = " ".join(f"{1/ncols:.2f}" for _ in range(ncols))
    out = [f"\n@multitable @columnfractions {col_spec}"]
    for i, row in enumerate(rows):
        cells = [_clean_inline(c) for c in row]
        joined = " @tab ".join(cells)
        if i == 0:
            out.append(f"@headitem {joined}")
        else:
            out.append(f"@item {joined}")
    out.append("@end multitable\n")
    return out


def _is_ul(line: str) -> bool:
    return bool(re.match(r"^(\s*)[-*]\s", line))


def _is_ol(line: str) -> bool:
    return bool(re.match(r"^(\s*)\d+\.\s", line))


def _list_indent(line: str) -> int:
    m = re.match(r"^(\s*)", line)
    return len(m.group(1)) if m else 0


def md_to_texi(md: str) -> str:
    """Convert markdown content to Texinfo body text."""
    lines = md.split("\n")
    out = []
    in_code = False
    in_table = False
    table_rows = []
    list_stack = []  # stack of ("ul"|"ol", indent_level)

    def close_lists_to(indent):
        """Close list environments back to the given indent level."""
        while list_stack and list_stack[-1][1] >= indent:
            kind = list_stack.pop()[0]
            if kind == "ul":
                out.append("@end itemize")
            else:
                out.append("@end enumerate")

    def close_all_lists():
        close_lists_to(-1)

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                out.append("@end example")
                in_code = False
            else:
                close_all_lists()
                out.append("\n@example")
                in_code = True
            continue
        if in_code:
            line = line.replace("@", "@@").replace("{", "@{").replace("}", "@}")
            out.append(line)
            continue

        # Flush table if we leave table context
        if in_table and not line.strip().startswith("|"):
            close_all_lists()
            out.extend(_flush_table(table_rows))
            table_rows = []
            in_table = False

        # Tables
        if line.strip().startswith("|"):
            close_all_lists()
            if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            table_rows.append(cells)
            in_table = True
            continue

        # List items
        is_unordered = _is_ul(line)
        is_ordered = _is_ol(line)

        if is_unordered or is_ordered:
            indent = _list_indent(line)
            kind = "ul" if is_unordered else "ol"

            # Close deeper or same-level lists of different kind
            while list_stack and list_stack[-1][1] >= indent:
                if list_stack[-1][1] == indent and list_stack[-1][0] == kind:
                    break
                old_kind = list_stack.pop()[0]
                out.append("@end itemize" if old_kind == "ul" else "@end enumerate")

            # Open new list if needed
            if not list_stack or list_stack[-1][1] < indent or list_stack[-1][0] != kind:
                out.append("@itemize @bullet" if kind == "ul" else "@enumerate")
                list_stack.append((kind, indent))

            # Extract item text
            if is_unordered:
                text = re.sub(r"^\s*[-*]\s+", "", line)
            else:
                text = re.sub(r"^\s*\d+\.\s+", "", line)
            out.append(f"@item\n{_clean_inline(text)}")
            continue

        # Non-list line: close lists if we're in one and hit a blank or heading
        if list_stack and (line.strip() == "" or line.startswith("#")):
            # Continuation paragraphs within list items are tricky;
            # close on blank lines for simplicity
            if line.strip() == "":
                close_all_lists()
                out.append("")
                continue

        # If we're still in a list but hit a non-list, non-blank line,
        # treat it as continuation text
        if list_stack and line.strip() and not line.startswith("#"):
            out.append(_clean_inline(line))
            continue

        # Close any remaining lists for headings
        if line.startswith("#"):
            close_all_lists()

        # Skip H1 (handled by chapter node)
        if line.startswith("# ") and not line.startswith("## "):
            continue

        if line.startswith("## "):
            out.append(f"\n@section {_clean_inline(line[3:].strip())}")
            continue

        if line.startswith("### "):
            out.append(f"\n@subsection {_clean_inline(line[4:].strip())}")
            continue

        if line.startswith("#### "):
            out.append(f"\n@subsubsection {_clean_inline(line[5:].strip())}")
            continue

        # Metadata lines
        m = re.match(r"^\*\*(\w[\w\s]*):\*\*\s*(.*)", line)
        if m:
            key, val = m.group(1), _clean_inline(m.group(2))
            out.append(f"@noindent\n@strong{{{key}:}} {val}\n")
            continue

        # Blockquotes
        if line.startswith("> "):
            text = _clean_inline(line[2:])
            out.append(f"@quotation\n{text}\n@end quotation")
            continue

        # Horizontal rules
        if line.strip() == "---":
            continue

        # Regular text
        out.append(_clean_inline(line))

    close_all_lists()
    if in_table:
        out.extend(_flush_table(table_rows))

    return "\n".join(out)


def extract_title(md: str) -> str:
    for line in md.split("\n"):
        if line.startswith("# "):
            return _clean_inline(line[2:].strip())
    return "Untitled"


def rfc_node_name(filename: str) -> str:
    num = re.match(r"(\d+)", filename).group(1)
    return f"RFC {num}"


def build():
    rfcs = []
    for f in RFC_FILES:
        md = f.read_text()
        node = rfc_node_name(f.name)
        title = extract_title(md)
        body = md_to_texi(md)
        rfcs.append((node, title, body))

    menu_lines = [f"* {node}:: {title}" for node, title, _ in rfcs]

    texi = rf"""\input texinfo
@settitle smrti RFCs
@documentencoding UTF-8

@copying
Design decisions for smrti (advaita-smrti).
@end copying

@titlepage
@title smrti RFCs
@subtitle Design decisions for advaita-smrti
@author Aaron Johnson
@end titlepage

@contents

@ifnottex
@node Top
@top smrti RFCs

Design decisions for smrti --- structured project memory
for collaborative AI sessions.
@end ifnottex

@menu
{chr(10).join(menu_lines)}
@end menu

"""

    for node, title, body in rfcs:
        texi += f"""
@node {node}
@chapter {title}

{body}

"""

    texi += "@bye\n"
    return texi


def main():
    parser = argparse.ArgumentParser(description="Build Texinfo from RFC markdown")
    parser.add_argument("--info", action="store_true", help="Run makeinfo to produce .info")
    parser.add_argument("--pdf", action="store_true", help="Run texi2pdf to produce .pdf")
    args = parser.parse_args()

    texi = build()
    OUTPUT.write_text(texi)
    print(f"Wrote {OUTPUT}")

    if args.info:
        info_file = OUTPUT.with_suffix(".info")
        subprocess.run(["makeinfo", str(OUTPUT), "-o", str(info_file)], check=True)
        print(f"Wrote {info_file}")

    if args.pdf:
        subprocess.run(["texi2pdf", str(OUTPUT), "-o", str(OUTPUT.with_suffix(".pdf"))],
                        cwd=RFC_DIR, check=True)
        print(f"Wrote {OUTPUT.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
