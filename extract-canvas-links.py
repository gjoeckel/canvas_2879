#!/usr/bin/env python3
"""
Extract all Canvas page links from HTML files in the project.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup
import json

COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
HTML_DIR = COURSE_DIR / "WINTER 25-26 COURSE UPDATES"
OUTPUT_FILE = COURSE_DIR / "canvas-page-links.json"

def extract_canvas_url_from_html(html_file_path):
    """Extract Canvas URL from HTML file."""
    if not html_file_path.exists():
        return None
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        original_link = soup.find('div', class_='original-link')
        if original_link:
            a_tag = original_link.find('a')
            if a_tag and 'href' in a_tag.attrs:
                return a_tag['href']
    except Exception as e:
        print(f"  ⚠️  Error reading {html_file_path}: {e}")
    return None

def extract_page_title_from_html(html_file_path):
    """Extract page title from HTML file."""
    if not html_file_path.exists():
        return None
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            # Remove ": WINTER 25-26 COURSE UPDATES" suffix if present
            title = re.sub(r':\s*WINTER 25-26 COURSE UPDATES', '', title)
            return title
    except Exception as e:
        print(f"  ⚠️  Error reading {html_file_path}: {e}")
    return None

def main():
    print("📝 Extracting Canvas page links from HTML files...")

    canvas_links = {}

    if HTML_DIR.exists():
        for html_file in sorted(HTML_DIR.rglob("*.html")):
            relative_path = html_file.relative_to(HTML_DIR)
            canvas_url = extract_canvas_url_from_html(html_file)
            page_title = extract_page_title_from_html(html_file)

            if canvas_url:
                canvas_links[str(relative_path)] = {
                    "title": page_title or html_file.stem,
                    "canvas_url": canvas_url,
                    "file_path": str(relative_path)
                }
                print(f"  ✅ {relative_path}: {canvas_url}")
            else:
                print(f"  ⚠️  {relative_path}: No Canvas URL found")

    # Write to JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(canvas_links, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Extracted {len(canvas_links)} Canvas page links")
    print(f"💾 Saved to {OUTPUT_FILE}")

    # Also create a simple text list
    text_output = COURSE_DIR / "canvas-page-links.txt"
    with open(text_output, 'w', encoding='utf-8') as f:
        f.write("Canvas Page Links\n")
        f.write("=" * 80 + "\n\n")
        for file_path, info in sorted(canvas_links.items()):
            f.write(f"{info['title']}\n")
            f.write(f"  File: {file_path}\n")
            f.write(f"  URL: {info['canvas_url']}\n\n")

    print(f"💾 Also saved text version to {text_output}")

if __name__ == "__main__":
    main()

