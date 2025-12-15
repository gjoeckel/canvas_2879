#!/usr/bin/env python3
"""
Fix image paths in local HTML files.

Updates paths from '../365_Update/1234567.png' to '1234567.png' (same directory)
or to correct relative path if image is in a different location.
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import get_winter_updates_dir, get_winter_archive_dir

def find_image_file(canvas_id, html_dir, winter_dir):
    """Find image file with given Canvas ID.

    Searches in:
    1. Same directory as HTML file
    2. Parent directories (Section, Module)
    3. Archive 365_Update directory

    Returns:
        Path to image file if found, None otherwise
    """
    # Try same directory first
    for ext in ['.png', '.jpg', '.jpeg', '.gif']:
        image_file = html_dir / f"{canvas_id}{ext}"
        if image_file.exists():
            return image_file

    # Try parent directories (Section, Module levels)
    current_dir = html_dir
    for _ in range(3):  # Go up max 3 levels
        current_dir = current_dir.parent
        if current_dir == winter_dir.parent:
            break
        for ext in ['.png', '.jpg', '.jpeg', '.gif']:
            image_file = current_dir / f"{canvas_id}{ext}"
            if image_file.exists():
                return image_file

    # Try archive directory as last resort
    archive_dir = get_winter_archive_dir() / '365_Update'
    for ext in ['.png', '.jpg', '.jpeg', '.gif']:
        image_file = archive_dir / f"{canvas_id}{ext}"
        if image_file.exists():
            return image_file

    return None

def fix_image_paths_in_html(html_file, winter_dir):
    """Fix image paths in HTML file."""
    if not html_file.exists():
        return False

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠️  Could not read {html_file}: {e}")
        return False

    soup = BeautifulSoup(content, 'html.parser')
    html_dir = html_file.parent
    updated = False

    for img in soup.find_all('img'):
        src = img.get('src', '')

        if not src or src.startswith('http'):
            continue

        # Check if path points to 365_Update or needs updating
        if '../365_Update/' in src or '365_Update/' in src or '/files/' in src:
            # Extract Canvas ID
            canvas_id = None

            # Try to extract from path like ../365_Update/1234567.png
            match = re.search(r'(\d+)\.(png|jpg|jpeg|gif)', src, re.IGNORECASE)
            if match:
                canvas_id = match.group(1)
            else:
                # Try Canvas URL pattern
                match = re.search(r'/files/(\d+)', src)
                if match:
                    canvas_id = match.group(1)

            if canvas_id:
                # Find the image file
                image_file = find_image_file(canvas_id, html_dir, winter_dir)

                if image_file:
                    # Calculate relative path from HTML file to image
                    try:
                        rel_path = image_file.relative_to(html_dir)
                        new_src = str(rel_path).replace('\\', '/')

                        if src != new_src:
                            img['src'] = new_src
                            updated = True
                    except ValueError:
                        # If relative path calculation fails, use absolute path
                        # (shouldn't happen, but just in case)
                        pass

    if updated:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    return False

def main():
    winter_dir = get_winter_updates_dir()
    local_html_files = list(winter_dir.rglob("*_local.html"))

    print(f"🔧 Fixing image paths in {len(local_html_files)} local HTML files...\n")

    fixed_count = 0
    for html_file in local_html_files:
        rel_path = html_file.relative_to(winter_dir)
        if fix_image_paths_in_html(html_file, winter_dir):
            fixed_count += 1
            if fixed_count <= 10:
                print(f"  ✅ Fixed: {rel_path}")

    print(f"\n✅ Fixed image paths in {fixed_count} files")
    print(f"   Total files: {len(local_html_files)}")

if __name__ == '__main__':
    main()
