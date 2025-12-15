#!/usr/bin/env python3
"""
Download all Canvas page content and populate HTML files.

This script:
1. Parses docs/index.html to extract Canvas page URLs
2. Maps URLs to the HTML files created by create-html-directory-structure.py
3. Downloads page content from Canvas API
4. Populates HTML files with actual content, ensuring "View original page on Canvas" link is at the top
"""

import os
import sys
import re
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup

# Add canvas_grab to path
sys.path.insert(0, '/Users/a00288946/Projects/canvas_grab')

from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

# Configuration
CANVAS_ENDPOINT = "https://usucourses.instructure.com"
COURSE_ID = 2879
BASE_DIR = Path(__file__).parent


def normalize_filename(name):
    """Convert page name to lowercase with underscores (same as create-html-directory-structure.py)."""
    # Remove leading numbers and dots (e.g., "1. Course Orientation" -> "Course Orientation")
    name = re.sub(r'^\d+\.\s*', '', name)

    # Convert to lowercase
    name = name.lower()

    # Replace spaces and special characters with underscores
    name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars except hyphens
    name = re.sub(r'[-\s]+', '_', name)   # Replace spaces and hyphens with underscores
    name = re.sub(r'_+', '_', name)        # Replace multiple underscores with single
    name = name.strip('_')                 # Remove leading/trailing underscores

    return name


def parse_index_html_for_canvas_urls(index_file):
    """Parse index.html and extract Canvas URLs mapped to page names."""
    with open(index_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    page_urls = {}

    # Extract URLs from all links with "view canvas" text
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'instructure.com/courses/2879/pages/' in href:
            # Find the page name from parent elements
            # Look for span.page-text in the same li or heading
            parent = link.parent
            while parent:
                page_text = parent.find('span', class_='page-text')
                if page_text:
                    page_name = page_text.get_text(strip=True)
                    # Extract page slug from URL
                    match = re.search(r'/pages/([^/?]+)', href)
                    if match:
                        page_slug = match.group(1)
                        filename = normalize_filename(page_name)
                        page_urls[filename] = {
                            'name': page_name,
                            'slug': page_slug,
                            'url': href
                        }
                    break
                parent = parent.parent

    return page_urls


def find_html_files(base_dir):
    """Find all HTML files created by create-html-directory-structure.py."""
    html_files = {}

    for html_file in base_dir.rglob("*.html"):
        # Skip docs directory and old files with spaces in names
        if 'docs' in str(html_file) or ' ' in html_file.stem:
            continue

        # Get the filename without extension
        filename = html_file.stem
        html_files[filename] = html_file

    return html_files


def get_canvas_token():
    """Get Canvas token from environment or config.toml."""
    token = os.environ.get('CANVAS_TOKEN')
    if not token:
        # Try to source from shell config
        import subprocess
        result = subprocess.run(
            ['bash', '-c', 'source ~/.zshrc 2>/dev/null && echo $CANVAS_TOKEN'],
            capture_output=True, text=True
        )
        token = result.stdout.strip()

    # Fallback to config.toml
    if not token:
        try:
            import toml
            config_path = BASE_DIR / 'config.toml'
            if config_path.exists():
                config = toml.load(config_path)
                token = config.get('endpoint', {}).get('api_key')
        except Exception:
            pass

    if not token:
        raise ValueError("CANVAS_TOKEN not found in environment or config.toml")
    return token


def create_full_html_page(title, body_content, original_url, html_file_path):
    """Create a complete HTML page with Canvas styling.

    Ensures "View original page on Canvas" link is at the TOP of user_content.
    """
    # Calculate relative paths to CSS files (2 levels up from module directories)
    css_links = [
        '<link href="../../canvas-fonts.css" media="screen" rel="stylesheet"/>',
        '<link href="../../canvas-variables.css" media="all" rel="stylesheet"/>',
        '<link href="../../canvas-common.css" media="all" rel="stylesheet"/>',
        '<link href="../../canvas-wiki-page.css" media="screen" rel="stylesheet"/>',
        '<link href="../../catalog_canvas_global.css" media="all" rel="stylesheet"/>',
        '<link href="../../webaimCatalog.css" media="all" rel="stylesheet"/>',
        '<link href="../../AD-365-V4.css" media="all" rel="stylesheet"/>',
        '<link href="../../canvas-custom-overrides.css" media="all" rel="stylesheet"/>',
    ]

    css_section = '\n    '.join(css_links)

    # Ensure original-link is at the TOP of user_content
    # Remove any existing original-link from body_content
    body_content_clean = re.sub(
        r'<div\s+class=["\']original-link["\'][^>]*>.*?</div>',
        '',
        body_content,
        flags=re.DOTALL | re.IGNORECASE
    )
    body_content_clean = body_content_clean.strip()

    return f'''<!DOCTYPE html>

<html dir="ltr" lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<meta content="#f2f2f2" name="theme-color"/>
<title>{escape(title)}: WINTER 25-26 COURSE UPDATES</title>
<!-- Canvas Core CSS Files (in order from Canvas source) -->
{css_section}
</head>
<body class="with-left-side course-menu-expanded padless-content pages primary-nav-expanded context-course_2879">
<div class="content" style="margin-left: 30px; margin-right: 30px;">
<div class="user_content">
<div class="original-link">
<p><a href="{escape(original_url)}" target="_blank">View original page on Canvas</a></p>
</div>
{body_content_clean}
</div>
</div>
</body>
</html>'''


def download_page_content(canvas, course, page_slug):
    """Download the actual content of a Canvas page."""
    try:
        # Fetch the full page to get body content
        full_page = course.get_page(page_slug)
        return full_page.body if hasattr(full_page, 'body') and full_page.body else None
    except ResourceDoesNotExist:
        return None
    except Exception as e:
        print(f"  ⚠️  Error fetching page {page_slug}: {e}")
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Download all Canvas page content and populate HTML files'
    )
    parser.add_argument(
        '--base-dir',
        type=Path,
        default=Path('WINTER 25-26 COURSE UPDATES'),
        help='Base directory for course files'
    )
    parser.add_argument(
        '--index-file',
        type=Path,
        default=Path('docs/index.html'),
        help='Path to index.html file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be downloaded without actually downloading'
    )

    args = parser.parse_args()

    # Parse index.html to get Canvas URLs
    print(f"📄 Parsing: {args.index_file}")
    page_urls = parse_index_html_for_canvas_urls(args.index_file)
    print(f"   Found {len(page_urls)} Canvas page URLs\n")

    # Find all HTML files
    print(f"🔍 Finding HTML files in: {args.base_dir}")
    html_files = find_html_files(args.base_dir)
    print(f"   Found {len(html_files)} HTML files\n")

    # Match HTML files to Canvas URLs
    matched = []
    unmatched_html = []
    unmatched_urls = []

    for filename, html_file in html_files.items():
        if filename in page_urls:
            matched.append({
                'filename': filename,
                'html_file': html_file,
                'page_info': page_urls[filename]
            })
        else:
            unmatched_html.append((filename, html_file))

    for filename, page_info in page_urls.items():
        if filename not in html_files:
            unmatched_urls.append((filename, page_info))

    print(f"📊 Matching Results:")
    print(f"   Matched: {len(matched)}")
    if unmatched_html:
        print(f"   Unmatched HTML files: {len(unmatched_html)}")
        for filename, _ in unmatched_html[:5]:
            print(f"     - {filename}")
        if len(unmatched_html) > 5:
            print(f"     ... and {len(unmatched_html) - 5} more")
    if unmatched_urls:
        print(f"   Unmatched Canvas URLs: {len(unmatched_urls)}")
        for filename, _ in unmatched_urls[:5]:
            print(f"     - {filename}")
        if len(unmatched_urls) > 5:
            print(f"     ... and {len(unmatched_urls) - 5} more")
    print()

    if args.dry_run:
        print("💡 DRY RUN - No files will be modified")
        print("\n📋 Pages that would be downloaded:")
        for match in matched[:10]:
            print(f"   ✅ {match['html_file'].relative_to(args.base_dir)}")
            print(f"      Canvas: {match['page_info']['name']} ({match['page_info']['slug']})")
        if len(matched) > 10:
            print(f"   ... and {len(matched) - 10} more")
        return

    # Initialize Canvas API
    print("🔗 Connecting to Canvas...")
    try:
        token = get_canvas_token()
        canvas = Canvas(CANVAS_ENDPOINT, token)
        course = canvas.get_course(COURSE_ID)
        print(f"✅ Connected to course: {course.name}\n")
    except Exception as e:
        print(f"❌ Error connecting to Canvas: {e}")
        return

    # Download content for each matched page
    print(f"📥 Downloading page content...\n")
    success_count = 0
    failed_count = 0

    for match in matched:
        html_file = match['html_file']
        page_info = match['page_info']
        page_slug = page_info['slug']
        page_name = page_info['name']
        canvas_url = page_info['url']

        try:
            print(f"  📄 {html_file.relative_to(args.base_dir)}")
            print(f"     Canvas: {page_name} ({page_slug})")

            # Download page content
            body_content = download_page_content(canvas, course, page_slug)

            if not body_content:
                print(f"     ❌ No content found")
                failed_count += 1
                continue

            # Create full HTML page with original-link at the top
            full_html = create_full_html_page(
                page_name,
                body_content,
                canvas_url,
                html_file
            )

            # Write the content
            html_file.write_text(full_html, encoding='utf-8')
            print(f"     ✅ Downloaded and saved (with 'View original page on Canvas' link at top)")
            success_count += 1

        except Exception as e:
            print(f"     ❌ Error: {e}")
            failed_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Summary")
    print(f"{'='*60}")
    print(f"Successfully downloaded: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(matched)}")

    if success_count > 0:
        print(f"\n📋 Next steps:")
        print(f"   1. Run rename-and-update-images.py to organize images with Canvas IDs")
        print(f"   2. Run html-to-docx.py to generate DOCX files (will include 'View original' link)")


if __name__ == '__main__':
    main()
