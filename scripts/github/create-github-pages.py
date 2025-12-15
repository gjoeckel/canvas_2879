#!/usr/bin/env python3
"""
Create GitHub Pages HTML site from DOCX-HTML-MAPPING.md
"""

import re
from pathlib import Path
from html import escape

COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
MAPPING_FILE = COURSE_DIR / "DOCX-HTML-MAPPING.md"
OUTPUT_FILE = COURSE_DIR / "docs" / "index.html"

def extract_link_from_line(line):
    """Extract URL and text from a markdown link line."""
    match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
    if match:
        return match.group(1), match.group(2)
    return None, None

def main():
    print("📝 Creating GitHub Pages HTML site...")

    # Create docs directory if it doesn't exist
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping_content = f.read()

    html_lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Canvas Course DOCX Editor</title>',
        '    <style>',
        '        body {',
        '            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;',
        '            line-height: 1.6;',
        '            max-width: 1200px;',
        '            margin: 0 auto;',
        '            padding: 20px;',
        '            color: #24292e;',
        '            background-color: #ffffff;',
        '        }',
        '        h1 {',
        '            color: #0366d6;',
        '            border-bottom: 1px solid #eaecef;',
        '            padding-bottom: 10px;',
        '        }',
        '        h2 {',
        '            color: #0366d6;',
        '            margin-top: 30px;',
        '            border-bottom: 1px solid #eaecef;',
        '            padding-bottom: 8px;',
        '        }',
        '        h3 {',
        '            color: #24292e;',
        '            margin-top: 20px;',
        '        }',
        '        h4 {',
        '            color: #586069;',
        '            margin-top: 15px;',
        '            font-size: 1.1em;',
        '        }',
        '        a {',
        '            color: #0366d6;',
        '            text-decoration: none;',
        '        }',
        '        a:hover {',
        '            text-decoration: underline;',
        '        }',
        '        ol, ul {',
        '            margin-left: 20px;',
        '        }',
        '        li {',
        '            margin: 5px 0;',
        '        }',
        '        .note {',
        '            background-color: #fff3cd;',
        '            border: 1px solid #ffc107;',
        '            border-radius: 4px;',
        '            padding: 10px;',
        '            margin: 20px 0;',
        '        }',
        '        .summary {',
        '            background-color: #f6f8fa;',
        '            border: 1px solid #d1d5db;',
        '            border-radius: 4px;',
        '            padding: 15px;',
        '            margin: 20px 0;',
        '        }',
        '    </style>',
        '</head>',
        '<body>',
        '    <h1>Canvas Course DOCX Editor</h1>',
        '    <p>This page provides direct links to edit course documents in Microsoft Word Online.</p>',
        '    <div class="note">',
        '        <strong>Note:</strong> All links open in new tabs automatically.',
        '    </div>',
    ]

    # Parse the mapping file
    lines = mapping_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip summary section
        if line.startswith('## Summary'):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('---'):
                i += 1
            continue

        # H2 headings (modules)
        if line.startswith('## '):
            h2_text = line[3:].strip()
            # Convert markdown links to HTML
            h2_text = re.sub(
                r'\[([^\]]+)\]\(([^)]+)\)',
                r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
                h2_text
            )
            html_lines.append(f'    <h2>{h2_text}</h2>')
            i += 1
            continue

        # H3 headings (sections)
        if line.startswith('### '):
            h3_text = line[4:].strip()
            # Convert markdown links to HTML
            h3_text = re.sub(
                r'\[([^\]]+)\]\(([^)]+)\)',
                r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
                h3_text
            )
            html_lines.append(f'    <h3>{h3_text}</h3>')
            i += 1
            continue

        # H4 Learning Modules
        if line.startswith('#### Learning Modules'):
            html_lines.append('    <h4>Learning Modules</h4>')
            html_lines.append('    <ol>')
            i += 1
            # Skip blank line if present
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            # Collect numbered list items
            while i < len(lines):
                next_line = lines[i].strip()
                # Match numbered list items with links
                match = re.match(r'(\d+)\.\s+\[([^\]]+)\]\(([^)]+)\)', next_line)
                if match:
                    num, link_text, link_url = match.groups()
                    html_lines.append(
                        f'        <li><a href="{escape(link_url)}" target="_blank" rel="noopener noreferrer">{escape(link_text)}</a></li>'
                    )
                elif next_line.startswith(('---', '##', '###', '*No Learning')):
                    break
                elif next_line == '':
                    # Check if next line is another heading
                    if i + 1 < len(lines):
                        peek = lines[i + 1].strip()
                        if peek.startswith(('---', '##', '###', '*No Learning')):
                            break
                i += 1
            html_lines.append('    </ol>')
            continue

        # Skip "No Learning Activities" and other non-content lines
        if line.startswith('*No Learning') or line == '' or line.startswith('---'):
            i += 1
            continue

        i += 1

    html_lines.extend([
        '</body>',
        '</html>'
    ])

    # Write output
    print(f"💾 Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))

    print(f"✅ Created GitHub Pages site: {OUTPUT_FILE}")
    print(f"\n📝 Next steps:")
    print(f"   1. Commit and push the docs/ folder to GitHub")
    print(f"   2. Enable GitHub Pages in repository settings")
    print(f"   3. Select 'docs' folder as the source")

if __name__ == "__main__":
    main()

