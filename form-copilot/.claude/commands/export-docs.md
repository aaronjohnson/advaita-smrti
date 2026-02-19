# Export Documentation

Export your form answers to Markdown or Texinfo for review, archival, or presentation.

## Quick Export

Run the export script:

```bash
# Export current form to markdown
python3 export_docs.py

# Export to texinfo (for PDF/HTML)
python3 export_docs.py --format texinfo

# Export all databases
python3 export_docs.py --all

# Combine multiple forms into one document
python3 export_docs.py --all --combine
```

## Building Texinfo Output

After exporting to `.texi`, build your preferred format:

```bash
# PDF (requires TeX installation)
makeinfo --pdf form_export.texi

# HTML (single page)
makeinfo --html --no-split form_export.texi

# HTML (multi-page)
makeinfo --html form_export.texi

# Info format (for Emacs/terminal)
makeinfo form_export.texi
```

## When to Use Each Format

| Format | Best For |
|--------|----------|
| **Markdown** | Quick review, sharing on GitHub, simple editing |
| **Texinfo → PDF** | Printing, formal submission, archival |
| **Texinfo → HTML** | Web viewing, sharing via browser |
| **JSON** | Data backup, importing elsewhere |

## Combining Multiple Forms

If working on related applications (e.g., multiple college apps, several grant proposals):

```bash
# Combine specific databases
python3 export_docs.py college_app.db scholarship.db --combine --format texinfo

# Then build a single PDF with all forms
makeinfo --pdf combined_export.texi
```

## Customizing Output

The export generates standard Texinfo. You can edit the `.texi` file before building:

- Add custom title pages
- Include additional sections
- Adjust formatting
- Add indices or cross-references

## Troubleshooting

**"makeinfo: command not found"**
Install texinfo: `apt install texinfo` (Debian/Ubuntu) or `brew install texinfo` (macOS)

**PDF build fails**
You need a TeX installation. Try `apt install texlive` or install MacTeX on macOS.

**HTML looks plain**
Texinfo HTML is minimal by default. For styled output, consider CSS or use the `--css-ref` option.
