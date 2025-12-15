#!/usr/bin/env python3
"""
Fix CSS paths in all local HTML files in WINTER-25-26-UPDATES structure.

This script updates relative CSS paths to point to the project root where CSS files are located.
"""

import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import get_project_root, get_winter_updates_dir, get_assets_dir

TARGET_DIR = get_winter_updates_dir()
PROJECT_ROOT = get_project_root()

def fix_css_paths_in_html(html_file):
    """Fix CSS paths in HTML file to be relative to project root."""
    if not html_file.exists():
        return False

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠️  Could not read {html_file}: {e}")
        return False

    soup = BeautifulSoup(content, 'html.parser')
    html_dir = html_file.parent.resolve()
    assets_css_dir = get_assets_dir('css').resolve()

    # Calculate relative path from HTML file directory to assets/css/
    try:
        css_rel_path = os.path.relpath(assets_css_dir, html_dir)
        if css_rel_path == '.':
            css_rel_path = ''
        else:
            css_rel_path = css_rel_path.replace('\\', '/') + '/'
    except ValueError:
        # Fallback: calculate based on depth from data/current/WINTER-25-26-UPDATES
        # Count levels: data/current/WINTER-25-26-UPDATES/Module-X/Section-X-Y/LA-X-Y-Z
        # Need to go up to project root, then into assets/css/
        winter_dir = get_winter_updates_dir()
        try:
            depth = len(html_dir.parts) - len(winter_dir.parts)
            # +3 for data/current/WINTER-25-26-UPDATES -> project root, then assets/css/
            css_rel_path = '../' * (depth + 3) + 'assets/css/'
        except:
            css_rel_path = '../../../../../../assets/css/'  # Safe fallback

    updated = False
    # Update all CSS link hrefs
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href', '')
        # Skip external URLs
        if href.startswith('http://') or href.startswith('https://'):
            continue

        # Update relative CSS paths
        if href.startswith('../') or (not href.startswith('/') and not href.startswith('http')):
            css_filename = Path(href).name
            new_href = f"{css_rel_path}{css_filename}"
            # Always update if path doesn't already contain assets/css/
            if 'assets/css' not in href and href != new_href:
                link['href'] = new_href
                updated = True

    if updated:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    return False

def main():
    print("🔧 Fixing CSS paths in local HTML files...")
    print(f"   Target directory: {TARGET_DIR}")
    print(f"   Project root: {PROJECT_ROOT}\n")

    # Find all local HTML files
    local_html_files = list(TARGET_DIR.rglob("*_local.html"))

    if not local_html_files:
        print("  ⚠️  No local HTML files found")
        return

    print(f"📄 Found {len(local_html_files)} local HTML files\n")

    fixed = 0
    for html_file in local_html_files:
        rel_path = html_file.relative_to(TARGET_DIR)
        if fix_css_paths_in_html(html_file):
            print(f"  ✅ Fixed: {rel_path}")
            fixed += 1

    print(f"\n✅ Fixed CSS paths in {fixed} files")
    print(f"   Total files: {len(local_html_files)}")

if __name__ == '__main__':
    main()
