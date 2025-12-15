#!/usr/bin/env python3
"""
Create GitHub page "Canvas Course DOCX Editor" with ordered list of Box Office Online links.
Link text comes from <h1> in <div class="guide"> of each HTML file.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
MAPPING_FILE = COURSE_DIR / "DOCX-HTML-MAPPING.md"
OUTPUT_FILE = COURSE_DIR / "Canvas-Course-DOCX-Editor.md"

def extract_box_url_from_markdown_link(markdown_link):
    """Extract Box Office Online URL from markdown link."""
    match = re.search(r'\(([^)]+)\)', markdown_link)
    if match:
        return match.group(1)
    return None

def extract_h1_from_guide(html_file_path):
    """Extract <h1> text from <div class="guide"> in HTML file."""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        guide_div = soup.find('div', class_='guide')

        if guide_div:
            h1 = guide_div.find('h1')
            if h1:
                return h1.get_text().strip()

        # Fallback: try to find any h1 in the document
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # Last fallback: use filename
        return html_file_path.stem
    except Exception as e:
        print(f"  ⚠️  Error reading {html_file_path.name}: {e}")
        return html_file_path.stem

def parse_mapping_file():
    """Parse DOCX-HTML-MAPPING.md to extract matched pairs with Box Office Online links."""
    matched_pairs = []

    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the matched files section
    in_matched_section = False
    for i, line in enumerate(lines):
        if '## Matched Files' in line:
            in_matched_section = True
            continue

        if in_matched_section and line.startswith('---'):
            break

        if in_matched_section and line.startswith('|') and 'Box Office Online Link' not in line:
            # Parse table row
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:
                html_path = parts[2].strip('`')
                box_link_markdown = parts[4].strip()

                # Extract URL from markdown link
                box_url = extract_box_url_from_markdown_link(box_link_markdown)

                if html_path and box_url:
                    matched_pairs.append({
                        'html_path': html_path,
                        'box_url': box_url
                    })

    return matched_pairs

def main():
    print("📝 Creating Canvas Course DOCX Editor page...")

    # Parse mapping file
    print("📖 Reading mapping file...")
    matched_pairs = parse_mapping_file()
    print(f"   Found {len(matched_pairs)} matched pairs")

    # Extract h1 text from each HTML file
    print("\n🔍 Extracting <h1> text from HTML files...")
    entries = []

    for pair in matched_pairs:
        html_path = COURSE_DIR / pair['html_path']
        if html_path.exists():
            h1_text = extract_h1_from_guide(html_path)
            entries.append({
                'title': h1_text,
                'url': pair['box_url']
            })
            print(f"   ✅ {html_path.name}: '{h1_text}'")
        else:
            print(f"   ⚠️  File not found: {html_path}")

    # Create markdown file
    print(f"\n📄 Creating {OUTPUT_FILE.name}...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Canvas Course DOCX Editor\n\n")
        f.write("This page provides direct links to edit course documents in Microsoft Word Online.\n\n")
        f.write("## Course Documents\n\n")

        for i, entry in enumerate(entries, 1):
            f.write(f"{i}. [{entry['title']}]({entry['url']})\n")

    print(f"✅ Created {OUTPUT_FILE}")
    print(f"   Total entries: {len(entries)}")

if __name__ == "__main__":
    main()

