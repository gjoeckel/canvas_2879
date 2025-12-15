#!/usr/bin/env python3
"""
Download actual HTML content for Canvas pages.

canvas_grab creates redirect HTML files for pages. This script fetches
the actual page content from Canvas API and replaces the redirect files.
"""

import os
import sys
import re
from pathlib import Path
from html import escape

# Add canvas_grab to path
sys.path.insert(0, '/Users/a00288946/Projects/canvas_grab')

from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

# Configuration
CANVAS_ENDPOINT = "https://usucourses.instructure.com"
COURSE_ID = 2879
BASE_DIR = Path(__file__).parent

def get_canvas_token():
    """Get Canvas token from environment."""
    token = os.environ.get('CANVAS_TOKEN')
    if not token:
        # Try to source from shell config
        import subprocess
        result = subprocess.run(
            ['bash', '-c', 'source ~/.zshrc 2>/dev/null && echo $CANVAS_TOKEN'],
            capture_output=True, text=True
        )
        token = result.stdout.strip()
    if not token:
        raise ValueError("CANVAS_TOKEN not found in environment")
    return token

def find_redirect_html_files(directory):
    """Find all HTML files that are redirects (contain meta refresh)."""
    html_files = []
    for html_file in directory.rglob("*.html"):
        try:
            content = html_file.read_text(encoding='utf-8')
            # Check if it's a redirect file (contains meta refresh)
            if 'meta http-equiv="refresh"' in content or 'meta http-equiv=\'refresh\'' in content:
                html_files.append(html_file)
        except Exception as e:
            print(f"Warning: Could not read {html_file}: {e}")
    return html_files

def extract_canvas_url_from_redirect(html_content):
    """Extract the Canvas URL from a redirect HTML file."""
    # Look for URL in meta refresh tag
    match = re.search(r'content="0; URL=([^"]+)"', html_content)
    if match:
        return match.group(1)
    # Also check for href in anchor tag
    match = re.search(r'<a href="([^"]+)"', html_content)
    if match:
        return match.group(1)
    return None

def get_page_url_from_canvas_url(canvas_url):
    """Extract page URL slug from Canvas HTML URL."""
    # Canvas page URLs look like: https://usucourses.instructure.com/courses/2879/pages/adding-and-editing-hyperlinks
    match = re.search(r'/pages/([^/?]+)', canvas_url)
    if match:
        return match.group(1)
    return None

def get_page_title_from_redirect(html_content):
    """Extract page title from redirect HTML file."""
    from html import unescape

    # Look for title in the redirect link text or title tag
    match = re.search(r'<title>([^<]+)</title>', html_content)
    if match:
        title = match.group(1).strip()
        # Decode HTML entities (e.g., &amp; -> &)
        title = unescape(title)
        return title
    # Also check the redirect link text
    match = re.search(r'<a[^>]*>([^<]+)</a>', html_content)
    if match:
        # Remove module prefix if present (e.g., "1 Introduction - Course Details" -> "Course Details")
        title = match.group(1).strip()
        # Decode HTML entities
        title = unescape(title)
        if ' - ' in title:
            title = title.split(' - ', 1)[1]
        return title
    return None

def find_page_by_title(course, title):
    """Find a Canvas page by matching its title."""
    try:
        pages = list(course.get_pages())
        # Normalize title for comparison (remove extra spaces, handle entities)
        normalized_title = ' '.join(title.split())

        # Try exact match first
        for page in pages:
            if page.title == title or page.title == normalized_title:
                return page
        # Try case-insensitive match
        for page in pages:
            if page.title.lower() == title.lower() or page.title.lower() == normalized_title.lower():
                return page
        # Try partial match (in case of extra characters)
        for page in pages:
            page_title_lower = page.title.lower()
            title_lower = normalized_title.lower()
            if title_lower in page_title_lower or page_title_lower in title_lower:
                # Check if it's a reasonable match (at least 50% of words match)
                title_words = set(title_lower.split())
                page_words = set(page_title_lower.split())
                if len(title_words) > 0 and len(title_words & page_words) / len(title_words) >= 0.5:
                    return page
    except Exception as e:
        print(f"  Error searching pages: {e}")
    return None

def create_full_html_page(title, body_content, original_url, base_dir):
    """Create a complete HTML page with Canvas styling matching the live site.

    Args:
        title: Page title
        body_content: HTML body content from Canvas
        original_url: Original Canvas URL
        base_dir: Base directory for calculating relative CSS paths
    """
    # Calculate relative paths to CSS files (assuming they're in project root)
    # This will be calculated per-file based on the HTML file's location
    css_links = [
        '<link rel="stylesheet" href="../../canvas-fonts.css" media="screen" />',
        '<link rel="stylesheet" href="../../canvas-variables.css" media="all" />',
        '<link rel="stylesheet" href="../../canvas-common.css" media="all" />',
        '<link rel="stylesheet" href="../../canvas-wiki-page.css" media="screen" />',
        '<link rel="stylesheet" href="../../catalog_canvas_global.css" media="all" />',
        '<link rel="stylesheet" href="../../webaimCatalog.css" media="all" />',
        '<link rel="stylesheet" href="../../AD-365-V4.css" media="all" />',
        '<link rel="stylesheet" href="../../canvas-custom-overrides.css" media="all" />',
    ]

    css_section = '\n    '.join(css_links)

    return f'''<!DOCTYPE html>
<html dir="ltr" lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#f2f2f2">
    <title>{escape(title)}: WINTER 25-26 COURSE UPDATES</title>

    <!-- Canvas Core CSS Files (in order from Canvas source) -->
    {css_section}
</head>
<body class="with-left-side course-menu-expanded padless-content pages primary-nav-expanded context-course_2879">
    <div class="content">
        <div class="user_content">
        {body_content}
        </div> <!-- end user_content -->
    </div> <!-- end content -->
    <div class="original-link">
        <p><a href="{escape(original_url)}" target="_blank">View original page on Canvas</a></p>
    </div>
</body>
</html>'''

def download_page_content(canvas, course, page):
    """Download the actual content of a Canvas page."""
    try:
        # Fetch the full page to get body content
        full_page = course.get_page(page.url)
        return full_page.body if hasattr(full_page, 'body') and full_page.body else None
    except ResourceDoesNotExist:
        return None
    except Exception as e:
        print(f"  Error fetching page {page.url}: {e}")
        return None

def find_local_image(image_url, base_dir):
    """Find a local image file that matches the Canvas image URL.

    Returns the relative path to the local file if found, None otherwise.
    Does NOT download images - only maps to existing files.
    """
    import urllib.parse

    # Extract filename from URL
    parsed = urllib.parse.urlparse(image_url)
    filename = os.path.basename(parsed.path)

    # Remove query parameters from filename if present
    if '?' in filename:
        filename = filename.split('?')[0]

    # Search for the file in the directory structure
    for img_file in base_dir.rglob(filename):
        if img_file.is_file():
            # Return relative path from base_dir
            return img_file.relative_to(base_dir)

    # Also try without query parameters or with different extensions
    base_name = os.path.splitext(filename)[0]
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
        for img_file in base_dir.rglob(base_name + ext):
            if img_file.is_file():
                return img_file.relative_to(base_dir)

    # If not found, return None (image will remain as Canvas URL)
    return None

def replace_image_urls(html_content, html_file_path, base_dir):
    """Replace Canvas image URLs with local file paths."""
    import re
    import urllib.parse

    def replace_url(match):
        full_match = match.group(0)
        url = match.group(1) or match.group(2)

        # Skip data URLs and local paths
        if url.startswith('data:') or url.startswith('#') or not url.startswith('http'):
            return full_match

        # Only process Canvas image URLs
        if 'instructure.com' not in url and 'canvas' not in url.lower():
            return full_match

        # Find local image
        local_path = find_local_image(url, base_dir)
        if local_path:
            # Calculate relative path from HTML file to image
            html_dir = html_file_path.parent
            try:
                rel_path = os.path.relpath(base_dir / local_path, html_dir)
                # Normalize path separators for web
                rel_path = rel_path.replace('\\', '/')
                return full_match.replace(url, rel_path)
            except ValueError:
                # Paths on different drives (Windows) - use absolute-ish path
                return full_match

        return full_match

    # Replace img src attributes
    html_content = re.sub(
        r'(<img[^>]+src=["\'])([^"\']+)(["\'][^>]*>)',
        replace_url,
        html_content,
        flags=re.IGNORECASE
    )

    # Replace background-image URLs in style attributes
    html_content = re.sub(
        r'(background-image:\s*url\(["\']?)([^"\'()]+)(["\']?\))',
        replace_url,
        html_content,
        flags=re.IGNORECASE
    )

    # Replace CSS link hrefs that point to images
    html_content = re.sub(
        r'(<link[^>]+href=["\'])([^"\']+\.(png|jpg|jpeg|gif|svg))(["\'])',
        replace_url,
        html_content,
        flags=re.IGNORECASE
    )

    return html_content

def download_canvas_css(canvas_url, base_dir):
    """Download Canvas CSS file if referenced in page content."""
    import requests
    import re

    # Extract CSS URL from Canvas page
    css_url = "https://instructure-uploads.s3.amazonaws.com/account_43980000000000001/attachments/1016014/canvas_global_app.css"
    css_filename = "canvas_global_app.css"
    css_path = base_dir / css_filename

    if css_path.exists():
        return css_filename

    try:
        print(f"  📥 Downloading Canvas CSS...")
        response = requests.get(css_url, timeout=10)
        response.raise_for_status()
        css_path.write_text(response.text, encoding='utf-8')
        print(f"  ✅ Downloaded {css_filename}")
        return css_filename
    except Exception as e:
        print(f"  ⚠️  Could not download Canvas CSS: {e}")
        return None

def main():
    """Main function to download page content."""
    import argparse

    parser = argparse.ArgumentParser(description='Download actual Canvas page content and map images')
    parser.add_argument('--css-file', type=str, help='Path to custom CSS file (relative to HTML files)')
    parser.add_argument('--css-content', type=str, help='Custom CSS content to embed')
    parser.add_argument('--download-canvas-css', action='store_true', help='Download Canvas CSS file automatically')
    parser.add_argument('--apply-to-all', action='store_true', help='Apply CSS to all HTML files, not just redirects')
    parser.add_argument('--use-canvas-css', action='store_true', help='Use Canvas CSS (loads canvas_global_app.css if it exists)')
    args = parser.parse_args()

    if args.apply_to_all:
        print("🔍 Finding all HTML files...")
        html_files = list(BASE_DIR.rglob("*.html"))
        # Filter out config files and scripts
        html_files = [f for f in html_files if 'config.toml' not in str(f) and 'setup' not in str(f)]
        print(f"Found {len(html_files)} HTML files")
    else:
        print("🔍 Finding redirect HTML files...")
        html_files = find_redirect_html_files(BASE_DIR)
        print(f"Found {len(html_files)} redirect HTML files")

    if not html_files:
        if args.apply_to_all:
            print("No HTML files found. Nothing to do.")
        else:
            print("No redirect HTML files found. Use --apply-to-all to update all HTML files.")
        return

    # Check for required CSS files
    required_css_files = [
        "canvas-fonts.css",
        "canvas-variables.css",
        "canvas-common.css",
        "canvas-wiki-page.css",
        "catalog_canvas_global.css",
        "webaimCatalog.css",
        "AD-365-V4.css",
        "canvas-custom-overrides.css"
    ]

    missing_files = [f for f in required_css_files if not (BASE_DIR / f).exists()]
    if missing_files:
        print(f"⚠️  Warning: Missing CSS files: {', '.join(missing_files)}")
        print("   Some styling may not work correctly.")
    else:
        print(f"✅ All required CSS files found")

    print(f"📝 Using Canvas styling structure (matching live Canvas pages)")

    # Initialize Canvas API
    print("\n🔗 Connecting to Canvas...")
    try:
        token = get_canvas_token()
        canvas = Canvas(CANVAS_ENDPOINT, token)
        course = canvas.get_course(COURSE_ID)
        print(f"✅ Connected to course: {course.name}")
    except Exception as e:
        print(f"❌ Error connecting to Canvas: {e}")
        return

    # Process each HTML file
    print(f"\n📥 Downloading page content...")
    success_count = 0
    failed_count = 0

    # No need to store CSS settings - using fixed Canvas structure

    for html_file in html_files:
        try:
            # Read the HTML file
            content = html_file.read_text(encoding='utf-8')

            # Check if it's a redirect file or already processed
            is_redirect = 'meta http-equiv="refresh"' in content or 'meta http-equiv=\'refresh\'' in content

            if is_redirect:
                # Extract Canvas URL
                canvas_url = extract_canvas_url_from_redirect(content)
                if not canvas_url:
                    print(f"  ⚠️  Could not extract URL from {html_file.name}")
                    failed_count += 1
                    continue

                # Extract page title from redirect file
                page_title = get_page_title_from_redirect(content)
                if not page_title:
                    print(f"  ⚠️  Could not extract page title from {html_file.name}")
                    failed_count += 1
                    continue

                print(f"  📄 Processing: {html_file.name} (title: {page_title})")

                # Try to find page by URL first
                page_url = get_page_url_from_canvas_url(canvas_url)
                page = None
                if page_url:
                    try:
                        page = course.get_page(page_url)
                    except:
                        pass

                # If not found by URL, try to find by title
                if not page:
                    page = find_page_by_title(course, page_title)

                if not page:
                    print(f"  ❌ Could not find page '{page_title}' in Canvas")
                    failed_count += 1
                    continue

                # Get page body content (need to fetch full page)
                body_content = download_page_content(canvas, course, page)
                if not body_content:
                    print(f"  ❌ Page '{page_title}' has no body content")
                    failed_count += 1
                    continue

                title = page.title
            else:
                # Already processed file - extract content from user_content div if present
                print(f"  📄 Updating CSS in: {html_file.name}")

                # Try to extract content from user_content div first
                user_content_match = re.search(r'<div class="user_content">(.*?)</div>\s*<!-- end user_content -->', content, re.DOTALL)
                if user_content_match:
                    body_content = user_content_match.group(1)
                else:
                    # Fallback: extract from content div
                    body_match = re.search(r'<div class="content">(.*?)<div class="original-link">', content, re.DOTALL)
                    if body_match:
                        body_content = body_match.group(1)
                        # Remove any existing user_content wrapper
                        body_content = re.sub(r'<div class="user_content">(.*?)</div>', r'\1', body_content, flags=re.DOTALL)
                    else:
                        # Fallback: extract everything between body tags
                        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
                        if body_match:
                            body_content = body_match.group(1)
                            # Remove any existing user_content wrapper
                            body_content = re.sub(r'<div class="user_content">(.*?)</div>', r'\1', body_content, flags=re.DOTALL)
                        else:
                            print(f"  ⚠️  Could not extract body content from {html_file.name}")
                            failed_count += 1
                            continue

                # Extract title
                title_match = re.search(r'<title>([^<]+)</title>', content)
                if title_match:
                    title = title_match.group(1)
                    # Clean up title (remove ": WINTER 25-26 COURSE UPDATES" if present)
                    title = re.sub(r':\s*WINTER 25-26 COURSE UPDATES.*$', '', title)
                else:
                    title = html_file.stem

                # Extract original URL if present
                url_match = re.search(r'<a href="([^"]+)"[^>]*target="_blank"[^>]*>View original', content)
                canvas_url = url_match.group(1) if url_match else "#"

            # Remove any existing user_content wrapper from body content (we'll add our own)
            # Remove opening user_content divs
            body_content = re.sub(r'<div\s+class=["\']user_content["\']>\s*', '', body_content, flags=re.IGNORECASE)
            # Remove closing user_content divs and comments
            body_content = re.sub(r'</div>\s*<!--\s*end\s+user_content\s*-->', '', body_content, flags=re.IGNORECASE)
            body_content = re.sub(r'</div>\s*<!--\s*end user_content\s*-->', '', body_content, flags=re.IGNORECASE)
            # Also remove any standalone closing divs that might be leftover
            body_content = body_content.strip()

            # Replace image URLs with local paths
            print(f"    🔍 Mapping images to local files...")
            body_content = replace_image_urls(body_content, html_file, BASE_DIR)

            # Create full HTML page with Canvas styling
            full_html = create_full_html_page(
                title,
                body_content,
                canvas_url,
                BASE_DIR
            )

            # Write the new content
            html_file.write_text(full_html, encoding='utf-8')
            print(f"  ✅ Updated {html_file.name}")
            success_count += 1

        except Exception as e:
            print(f"  ❌ Error processing {html_file.name}: {e}")
            failed_count += 1

    print(f"\n✅ Complete!")
    print(f"   Successfully updated: {success_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Total: {len(html_files)}")

if __name__ == "__main__":
    main()

