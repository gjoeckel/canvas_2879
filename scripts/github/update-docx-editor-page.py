#!/usr/bin/env python3
"""
Update Canvas-Course-DOCX-Editor.md using the restructured DOCX-HTML-MAPPING.md
"""

import re
from pathlib import Path

COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
MAPPING_FILE = COURSE_DIR / "DOCX-HTML-MAPPING.md"
OUTPUT_FILE = COURSE_DIR / "Canvas-Course-DOCX-Editor.md"

def extract_link_from_line(line):
    """Extract URL from a markdown link line."""
    match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
    if match:
        return match.group(1), match.group(2)
    return None, None

def convert_markdown_link_to_html(markdown_text):
    """Convert markdown link to HTML anchor with target="_blank"."""
    # Find all markdown links in the text
    def replace_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        return f'<a href="{link_url}" target="_blank" rel="noopener noreferrer">{link_text}</a>'

    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, markdown_text)

def main():
    print("📝 Updating Canvas Course DOCX Editor page...")

    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping_content = f.read()

    output_lines = [
        "# Canvas Course DOCX Editor",
        "",
        "This page provides direct links to edit course documents in Microsoft Word Online.",
        "",
    ]

    # Parse the mapping file
    lines = mapping_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # H2 headings (modules) - convert links to HTML
        if line.startswith('## '):
            h2_text = line[3:].strip()
            h2_text = convert_markdown_link_to_html(h2_text)
            output_lines.append(f"## {h2_text}")
            output_lines.append("")
            i += 1
            continue

        # H3 headings (sections) - convert links to HTML
        if line.startswith('### '):
            h3_text = line[4:].strip()
            h3_text = convert_markdown_link_to_html(h3_text)
            output_lines.append(f"### {h3_text}")
            output_lines.append("")
            i += 1
            continue

        # Learning Modules lists
        if line.startswith('#### Learning Modules'):
            output_lines.append("#### Learning Modules")
            output_lines.append("")
            i += 1
            # Skip blank line if present
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            # Collect numbered list items
            list_num = 1
            while i < len(lines):
                next_line = lines[i].strip()
                # Match numbered list items with links
                match = re.match(r'(\d+)\.\s+\[([^\]]+)\]\(([^)]+)\)', next_line)
                if match:
                    num, link_text, link_url = match.groups()
                    html_link = f'<a href="{link_url}" target="_blank" rel="noopener noreferrer">{link_text}</a>'
                    output_lines.append(f"{list_num}. {html_link}")
                    list_num += 1
                elif next_line.startswith(('---', '##', '###', '*No Learning')):
                    break
                elif next_line == '' and list_num > 1:
                    # Blank line after list items - check if next line is another heading
                    if i + 1 < len(lines):
                        peek = lines[i + 1].strip()
                        if peek.startswith(('---', '##', '###', '*No Learning')):
                            break
                i += 1
            output_lines.append("")
            continue

        # Skip "No Learning Activities" lines and other non-link content
        if line.startswith('*No Learning') or line == '' or line.startswith('---'):
            i += 1
            continue

        i += 1

    # Write output
    print(f"💾 Writing to {OUTPUT_FILE.name}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"✅ Updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

