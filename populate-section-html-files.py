#!/usr/bin/env python3
"""
Populate Section Canvas HTML files with actual content from Canvas API
and update Local HTML files with local asset paths
"""

import os
import sys
import re
from pathlib import Path
from html import escape
import urllib.parse

# Add canvas_grab to path for Canvas API
sys.path.insert(0, '/Users/a00288946/Projects/canvas_grab')

try:
    from canvasapi import Canvas
    from canvasapi.exceptions import ResourceDoesNotExist
except ImportError:
    print("Error: canvasapi module not found. Install with: pip3 install canvasapi")
    sys.exit(1)

# Configuration
CANVAS_ENDPOINT = "https://usucourses.instructure.com"
COURSE_ID = 2879
BASE_DIR = Path('data/current/WINTER-25-26-UPDATES')

# Section mappings with Canvas URLs
SECTION_MAPPINGS = {
    'Module-2/Section-2-4': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-4-tables',
        'slug': 'section-4-tables',
        'title': 'Section 4: Tables',
        'filename': 'Section 4_ Tables.html'
    },
    'Module-3/Section-3-1': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-1-evaluating-accessibility',
        'slug': 'section-1-evaluating-accessibility',
        'title': 'Section 1: Evaluating Accessibility',
        'filename': 'Section 1_ Evaluating Accessibility.html'
    },
    'Module-3/Section-3-2': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-2-practicing-evaluation-and-repair',
        'slug': 'section-2-practicing-evaluation-and-repair',
        'title': 'Section 2: Practicing Evaluation & Repair',
        'filename': 'Section 2_ Practicing Evaluation & Repair.html'
    },
    'Module-4/Section-4-2': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-2-checking-accessibility',
        'slug': 'section-2-checking-accessibility',
        'title': 'Section 2: Checking Accessibility',
        'filename': 'Section 2_ Checking Accessibility.html'
    },
    'Module-4/Section-4-3': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-3-reading-order-tool',
        'slug': 'section-3-reading-order-tool',
        'title': 'Section 3: Reading Order Tool',
        'filename': 'Section 3_ Reading Order Tool.html'
    },
    'Module-4/Section-4-4': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-4-content-order-and-tags-order',
        'slug': 'section-4-content-order-and-tags-order',
        'title': 'Section 4: Content Order and Tags Order',
        'filename': 'Section 4_ Content Order and Tags Order.html'
    },
    'Module-5/Section-5-1': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-1-navigating-in-excel',
        'slug': 'section-1-navigating-in-excel',
        'title': 'Section 1: Navigating in Excel',
        'filename': 'Section 1_ Navigating in Excel.html'
    },
    'Module-5/Section-5-2': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-2-sheets-and-tables',
        'slug': 'section-2-sheets-and-tables',
        'title': 'Section 2: Sheets & Tables',
        'filename': 'Section 2_ Sheets & Tables.html'
    },
    'Module-5/Section-5-3': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-3-images-and-links',
        'slug': 'section-3-images-and-links',
        'title': 'Section 3: Images & Links',
        'filename': 'Section 3_ Images & Links.html'
    },
    'Module-5/Section-5-5': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-5-optimizing-workbooks',
        'slug': 'section-5-optimizing-workbooks',
        'title': 'Section 5: Optimizing Workbooks',
        'filename': 'Section 5_ Optimizing Workbooks.html'
    },
    'Module-5/Section-5-6': {
        'url': 'https://usucourses.instructure.com/courses/2879/pages/section-6-evaluating-accessibility-in-excel',
        'slug': 'section-6-evaluating-accessibility-in-excel',
        'title': 'Section 6: Evaluating Accessibility in Excel',
        'filename': 'Section 6_ Evaluating Accessibility in Excel.html'
    }
}

def get_canvas_token():
    """Get Canvas token from environment."""
    token = os.environ.get('CANVAS_TOKEN')
    if not token:
        import subprocess
        result = subprocess.run(
            ['bash', '-c', 'source ~/.zshrc 2>/dev/null && echo $CANVAS_TOKEN'],
            capture_output=True, text=True
        )
        token = result.stdout.strip()
    if not token:
        raise ValueError("CANVAS_TOKEN not found in environment")
    return token

def create_canvas_html_page(title, body_content, canvas_url):
    """Create Canvas HTML page with proper structure and CSS paths (../../)."""
    css_prefix = '../../'

    css_links = [
        f'<link href="{css_prefix}canvas-fonts.css" media="screen" rel="stylesheet"/>',
        f'<link href="{css_prefix}canvas-variables.css" media="all" rel="stylesheet"/>',
        f'<link href="{css_prefix}canvas-common.css" media="all" rel="stylesheet"/>',
        f'<link href="{css_prefix}canvas-wiki-page.css" media="screen" rel="stylesheet"/>',
        f'<link href="{css_prefix}catalog_canvas_global.css" media="all" rel="stylesheet"/>',
        f'<link href="{css_prefix}webaimCatalog.css" media="all" rel="stylesheet"/>',
        f'<link href="{css_prefix}AD-365-V4.css" media="all" rel="stylesheet"/>',
        f'<link href="{css_prefix}canvas-custom-overrides.css" media="all" rel="stylesheet"/>',
    ]

    css_section = '\n'.join(css_links)

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
{body_content}
</div> <!-- end user_content -->
</div> <!-- end content -->
<div class="original-link">
<p><a href="{escape(canvas_url)}" target="_blank">View original page on Canvas</a></p>
</div>
</body>
</html>'''

def find_local_image(image_url, html_file_path, base_dir):
    """Find a local image file that matches the Canvas image URL."""
    parsed = urllib.parse.urlparse(image_url)
    filename = os.path.basename(parsed.path)

    if '?' in filename:
        filename = filename.split('?')[0]

    # Search in the section folder and subfolders
    section_folder = html_file_path.parent
    for img_file in section_folder.rglob(filename):
        if img_file.is_file():
            try:
                rel_path = os.path.relpath(img_file, section_folder)
                return rel_path.replace('\\', '/')
            except ValueError:
                pass

    # Also try parent folders (LA folders)
    for img_file in section_folder.parent.rglob(filename):
        if img_file.is_file():
            try:
                rel_path = os.path.relpath(img_file, section_folder)
                return rel_path.replace('\\', '/')
            except ValueError:
                pass

    return None

def replace_image_urls_with_local(body_content, html_file_path):
    """Replace Canvas image URLs with local file paths."""
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
        local_path = find_local_image(url, html_file_path, BASE_DIR)
        if local_path:
            return full_match.replace(url, local_path)

        return full_match

    # Replace img src attributes
    body_content = re.sub(
        r'(<img[^>]+src=["\'])([^"\']+)(["\'][^>]*>)',
        replace_url,
        body_content,
        flags=re.IGNORECASE
    )

    return body_content

def download_page_content(canvas, course, page_slug):
    """Download the actual content of a Canvas page."""
    try:
        full_page = course.get_page(page_slug)
        return full_page.body if hasattr(full_page, 'body') and full_page.body else None
    except ResourceDoesNotExist:
        return None
    except Exception as e:
        print(f"    ⚠️  Error fetching page {page_slug}: {e}")
        return None

def main():
    print("=" * 80)
    print("Phase 1: Populate Canvas HTML Files with Actual Content")
    print("=" * 80)
    print()

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

    success_count = 0
    failed_count = 0

    for section_path, section_info in SECTION_MAPPINGS.items():
        section_folder = BASE_DIR / section_path
        html_file = section_folder / section_info['filename']

        if not section_folder.exists():
            print(f"❌ Section folder does not exist: {section_path}")
            failed_count += 1
            continue

        print(f"📄 {section_path}/{section_info['filename']}")
        print(f"   Canvas: {section_info['title']} ({section_info['slug']})")

        try:
            # Download page content from Canvas
            body_content = download_page_content(canvas, course, section_info['slug'])

            if not body_content:
                print(f"   ❌ No content found")
                failed_count += 1
                continue

            # Create full HTML page
            full_html = create_canvas_html_page(
                section_info['title'],
                body_content,
                section_info['url']
            )

            # Write the content
            html_file.write_text(full_html, encoding='utf-8')
            print(f"   ✅ Downloaded and saved")
            success_count += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_count += 1
        print()

    print("=" * 80)
    print(f"\nPhase 1 Summary:")
    print(f"  ✅ Successfully populated: {success_count} Canvas HTML files")
    print(f"  ❌ Failed: {failed_count}")

    # Phase 2: Update Local HTML files with local asset paths
    print("\n" + "=" * 80)
    print("Phase 2: Update Local HTML Files with Local Asset Paths")
    print("=" * 80)
    print()

    local_success = 0
    local_failed = 0

    for section_path, section_info in SECTION_MAPPINGS.items():
        section_folder = BASE_DIR / section_path
        canvas_html_file = section_folder / section_info['filename']
        local_html_file = section_folder / f"{canvas_html_file.stem}_local.html"

        if not canvas_html_file.exists():
            print(f"⚠️  Canvas HTML not found: {canvas_html_file.name}")
            local_failed += 1
            continue

        if not local_html_file.exists():
            print(f"⚠️  Local HTML not found: {local_html_file.name}")
            local_failed += 1
            continue

        print(f"📄 {section_path}/{local_html_file.name}")

        try:
            # Read Canvas HTML
            content = canvas_html_file.read_text(encoding='utf-8')

            # Extract body content
            body_match = re.search(r'<div class="user_content">(.*?)</div>\s*<!-- end user_content -->', content, re.DOTALL)
            if not body_match:
                print(f"   ⚠️  Could not extract body content")
                local_failed += 1
                continue

            body_content = body_match.group(1)

            # Replace image URLs with local paths
            body_content = replace_image_urls_with_local(body_content, canvas_html_file)

            # Update CSS paths to local (../../../../../assets/css/)
            css_prefix = '../../../../../assets/css/'
            css_files = [
                'canvas-fonts.css',
                'canvas-variables.css',
                'canvas-common.css',
                'canvas-wiki-page.css',
                'catalog_canvas_global.css',
                'webaimCatalog.css',
                'AD-365-V4.css',
                'canvas-custom-overrides.css'
            ]

            for css_file in css_files:
                pattern = rf'href="[^"]*{re.escape(css_file)}"'
                replacement = f'href="{css_prefix}{css_file}"'
                content = re.sub(pattern, replacement, content)

            # Replace body content with updated version
            content = re.sub(
                r'<div class="user_content">.*?</div>\s*<!-- end user_content -->',
                f'<div class="user_content">\n{body_content}\n</div> <!-- end user_content -->',
                content,
                flags=re.DOTALL
            )

            # Write updated local HTML
            local_html_file.write_text(content, encoding='utf-8')
            print(f"   ✅ Updated with local asset paths")
            local_success += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            local_failed += 1
        print()

    print("=" * 80)
    print(f"\nPhase 2 Summary:")
    print(f"  ✅ Successfully updated: {local_success} Local HTML files")
    print(f"  ❌ Failed: {local_failed}")

    print("\n" + "=" * 80)
    print("✅ All tasks completed!")
    print("=" * 80)

if __name__ == '__main__':
    main()
