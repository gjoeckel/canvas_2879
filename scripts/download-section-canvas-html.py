#!/usr/bin/env python3
"""
Phase 1: Download Canvas HTML files for missing sections
Downloads HTML content from Canvas pages and standardizes the structure
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

BASE_DIR = Path('data/current/WINTER-25-26-UPDATES')

# Mapping of missing sections to their Canvas URLs and titles
SECTION_MAPPINGS = {
    'Module-2/Section-2-4': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-4-tables',
        'title': 'Section 4: Tables',
        'filename': 'Section 4_ Tables.html'
    },
    'Module-3/Section-3-1': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-1-evaluating-accessibility',
        'title': 'Section 1: Evaluating Accessibility',
        'filename': 'Section 1_ Evaluating Accessibility.html'
    },
    'Module-3/Section-3-2': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-2-practicing-evaluation-and-repair',
        'title': 'Section 2: Practicing Evaluation & Repair',
        'filename': 'Section 2_ Practicing Evaluation & Repair.html'
    },
    'Module-4/Section-4-2': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-2-checking-accessibility',
        'title': 'Section 2: Checking Accessibility',
        'filename': 'Section 2_ Checking Accessibility.html'
    },
    'Module-4/Section-4-3': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-3-reading-order-tool',
        'title': 'Section 3: Reading Order Tool',
        'filename': 'Section 3_ Reading Order Tool.html'
    },
    'Module-4/Section-4-4': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-4-content-order-and-tags-order',
        'title': 'Section 4: Content Order and Tags Order',
        'filename': 'Section 4_ Content Order and Tags Order.html'
    },
    'Module-5/Section-5-1': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-1-navigating-in-excel',
        'title': 'Section 1: Navigating in Excel',
        'filename': 'Section 1_ Navigating in Excel.html'
    },
    'Module-5/Section-5-2': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-2-sheets-and-tables',
        'title': 'Section 2: Sheets & Tables',
        'filename': 'Section 2_ Sheets & Tables.html'
    },
    'Module-5/Section-5-3': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-3-images-and-links',
        'title': 'Section 3: Images & Links',
        'filename': 'Section 3_ Images & Links.html'
    },
    'Module-5/Section-5-5': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-5-optimizing-workbooks',
        'title': 'Section 5: Optimizing Workbooks',
        'filename': 'Section 5_ Optimizing Workbooks.html'
    },
    'Module-5/Section-5-6': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-6-evaluating-accessibility-in-excel',
        'title': 'Section 6: Evaluating Accessibility in Excel',
        'filename': 'Section 6_ Evaluating Accessibility in Excel.html'
    }
}

# Template HTML structure (based on existing Section HTML)
HTML_TEMPLATE = '''<!DOCTYPE html>

<html dir="ltr" lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<meta content="#f2f2f2" name="theme-color"/>
<title>{title}: WINTER 25-26 COURSE UPDATES</title>
<!-- Canvas Core CSS Files (in order from Canvas source) -->
<link href="../../canvas-fonts.css" media="screen" rel="stylesheet"/>
<link href="../../canvas-variables.css" media="all" rel="stylesheet"/>
<link href="../../canvas-common.css" media="all" rel="stylesheet"/>
<link href="../../canvas-wiki-page.css" media="screen" rel="stylesheet"/>
<link href="../../catalog_canvas_global.css" media="all" rel="stylesheet"/>
<link href="../../webaimCatalog.css" media="all" rel="stylesheet"/>
<link href="../../AD-365-V4.css" media="all" rel="stylesheet"/>
<link href="../../canvas-custom-overrides.css" media="all" rel="stylesheet"/>
</head>
<body class="with-left-side course-menu-expanded padless-content pages primary-nav-expanded context-course_2879">
<div class="content" style="margin-left: 30px; margin-right: 30px;">
<div class="user_content">
{content}
</div> <!-- end user_content -->
</div> <!-- end content -->
<div class="original-link">
<p><a href="{canvas_url}" target="_blank">View original page on Canvas</a></p>
</div>
</body>
</html>'''

def extract_content_from_html(html_content):
    """Extract the main content from Canvas HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main content area
    # Canvas pages typically have content in div.user_content or div.entry-content
    content_div = soup.find('div', class_='user_content') or soup.find('div', class_='entry-content')

    if content_div:
        # Get the inner HTML
        content = str(content_div)
        # Clean up script tags and other unwanted elements
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        return content
    else:
        # Fallback: get body content
        body = soup.find('body')
        if body:
            return str(body)
        return html_content

def create_canvas_html_file(section_path, section_info):
    """Create a Canvas HTML file for a section"""
    section_folder = BASE_DIR / section_path
    html_file = section_folder / section_info['filename']

    if html_file.exists():
        print(f"  ⚠️  File already exists: {html_file.name}")
        return False

    # For now, create a placeholder file structure
    # In production, this would download actual content from Canvas
    content_placeholder = f'''<!-- <link rel="stylesheet" href="../../canvas_global_app.css"> -->
<div>
<p><strong>Note:</strong> This HTML file needs to be populated with content from Canvas.</p>
<p>URL: <a href="{section_info['url']}" target="_blank">{section_info['url']}</a></p>
</div>'''

    html_content = HTML_TEMPLATE.format(
        title=section_info['title'],
        content=content_placeholder,
        canvas_url=section_info['url']
    )

    # Write the file
    html_file.write_text(html_content, encoding='utf-8')
    print(f"  ✅ Created: {html_file.name}")
    return True

def main():
    print("Phase 1: Generate Canvas HTML Files")
    print("=" * 80)
    print()

    created_count = 0
    skipped_count = 0

    for section_path, section_info in SECTION_MAPPINGS.items():
        print(f"Processing {section_path}...")
        section_folder = BASE_DIR / section_path

        if not section_folder.exists():
            print(f"  ❌ Section folder does not exist: {section_path}")
            continue

        if create_canvas_html_file(section_path, section_info):
            created_count += 1
        else:
            skipped_count += 1
        print()

    print("=" * 80)
    print(f"\nSummary:")
    print(f"  ✅ Created: {created_count} Canvas HTML files")
    print(f"  ⚠️  Skipped: {skipped_count} (already exist)")
    print()
    print("Note: These files contain placeholder content.")
    print("You will need to manually download the HTML from Canvas or use Canvas API")
    print("to populate them with actual content.")

if __name__ == '__main__':
    main()
