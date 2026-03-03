# smrti-export — Export from Memory

Render completed work from structured memory into documents.

## Instructions

1. Call `memory_summary` to see what's available
2. Call `task_list` with status `closed` to gather completed items
3. Ask the user what format they want:
   - **Markdown** — quick review, sharing
   - **Texinfo** — PDF/HTML builds
   - **JSON** — data backup, interop

## Export Methods

### Using the export script (full-featured)

```bash
# Markdown
python3 advaita-smrti/export_docs.py --format markdown

# Texinfo (for PDF/HTML via makeinfo)
python3 advaita-smrti/export_docs.py --format texinfo

# All formats
python3 advaita-smrti/export_docs.py --all
```

### Building from Texinfo

```bash
# PDF (requires texlive)
makeinfo --pdf form_export.texi

# HTML (single page)
makeinfo --html --no-split form_export.texi
```

### Direct from MCP (for custom output)

If the export script doesn't cover the need, gather data
via MCP tools and render directly:

1. `task_list` with status filter → get completed items
2. `fact_list` by section → get supporting facts
3. `decision_list` → get decision rationale
4. Compose into the target format

## Format Guide

| Format | Best For |
|--------|----------|
| Markdown | Quick review, GitHub, editing |
| Texinfo → PDF | Printing, formal submission |
| Texinfo → HTML | Web viewing, sharing |
| JSON | Backup, importing elsewhere |
