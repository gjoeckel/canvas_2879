#!/usr/bin/env python3
"""
Locate missing image files referenced in local HTML files.

This script:
1. Identifies images referenced in local HTML files that don't exist
2. Searches for them in various locations (archive, current structure, etc.)
3. Reports where they are found or if they're truly missing
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re
from collections import defaultdict

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import get_winter_updates_dir, get_winter_archive_dir, get_project_root

def find_image_file(canvas_id, html_file, winter_dir):
    """Find image file with given Canvas ID.

    Searches in:
    1. Same directory as HTML file
    2. Parent directories (Section, Module, etc.)
    3. Archive 365_Update directory
    4. Anywhere in current structure

    Returns:
        Tuple of (Path to image file if found, location description)
    """
    html_dir = html_file.parent

    # Try same directory first
    for ext in ['.png', '.jpg', '.jpeg', '.gif']:
        image_file = html_dir / f"{canvas_id}{ext}"
        if image_file.exists():
            return image_file, "same directory"

    # Try parent directories (Section, Module levels)
    current_dir = html_dir
    level = 0
    while current_dir != winter_dir.parent and level < 5:
        current_dir = current_dir.parent
        level += 1
        for ext in ['.png', '.jpg', '.jpeg', '.gif']:
            image_file = current_dir / f"{canvas_id}{ext}"
            if image_file.exists():
                return image_file, f"parent directory ({level} levels up)"

    # Try archive directory
    archive_dir = get_winter_archive_dir() / '365_Update'
    for ext in ['.png', '.jpg', '.jpeg', '.gif']:
        image_file = archive_dir / f"{canvas_id}{ext}"
        if image_file.exists():
            return image_file, "archive (365_Update)"

    # Search recursively in current structure
    for ext in ['.png', '.jpg', '.jpeg', '.gif']:
        matches = list(winter_dir.rglob(f"{canvas_id}{ext}"))
        if matches:
            return matches[0], f"elsewhere in structure ({matches[0].relative_to(winter_dir).parent})"

    return None, "not found"

def locate_missing_images():
    """Locate all missing image files."""
    winter_dir = get_winter_updates_dir()
    local_html_files = list(winter_dir.rglob("*_local.html"))

    print(f"🔍 Locating missing images referenced in {len(local_html_files)} local HTML files...\n")

    missing_images = []
    found_locations = defaultdict(list)

    for html_file in local_html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')

            html_dir = html_file.parent

            for img in soup.find_all('img'):
                src = img.get('src', '')

                if not src or src.startswith('http'):
                    continue

                # Resolve image path
                if src.startswith('../'):
                    image_path = (html_dir / src).resolve()
                else:
                    image_path = html_dir / src

                # Check if file exists
                if not image_path.exists():
                    # Extract Canvas ID
                    canvas_id = None
                    match = re.search(r'(\d+)\.(png|jpg|jpeg|gif)', src, re.IGNORECASE)
                    if match:
                        canvas_id = match.group(1)
                    else:
                        match = re.search(r'/files/(\d+)', src)
                        if match:
                            canvas_id = match.group(1)

                    if canvas_id:
                        # Search for the image
                        found_file, location = find_image_file(canvas_id, html_file, winter_dir)

                        rel_html = html_file.relative_to(winter_dir)
                        missing_images.append({
                            'canvas_id': canvas_id,
                            'html_file': rel_html,
                            'html_dir': html_dir,
                            'expected_path': src,
                            'found_file': found_file,
                            'location': location
                        })

                        if found_file:
                            found_locations[location].append({
                                'canvas_id': canvas_id,
                                'html_file': rel_html,
                                'found_file': found_file
                            })
        except Exception as e:
            print(f"  ⚠️  Error processing {html_file}: {e}")

    return missing_images, found_locations

def main():
    missing_images, found_locations = locate_missing_images()

    print("=" * 60)
    print("📊 Missing Image Location Report")
    print("=" * 60)
    print(f"\nTotal missing images: {len(missing_images)}\n")

    # Group by location
    truly_missing = []
    by_location = defaultdict(list)

    for img_info in missing_images:
        if img_info['found_file']:
            by_location[img_info['location']].append(img_info)
        else:
            truly_missing.append(img_info)

    # Report found images
    if by_location:
        print("✅ Images Found in Other Locations:")
        print("-" * 60)
        for location, images in sorted(by_location.items()):
            print(f"\n📍 {location}: {len(images)} images")
            for img_info in images[:5]:  # Show first 5
                print(f"   Canvas ID {img_info['canvas_id']}")
                print(f"      Referenced in: {img_info['html_file']}")
                found_path = img_info['found_file']
                try:
                    # Try to show relative to project root
                    project_root = get_project_root()
                    rel_path = found_path.relative_to(project_root)
                    print(f"      Found at: {rel_path}")
                except ValueError:
                    # If not in project, show absolute path
                    print(f"      Found at: {found_path}")
            if len(images) > 5:
                print(f"   ... and {len(images) - 5} more")

    # Report truly missing images
    if truly_missing:
        print(f"\n❌ Truly Missing Images: {len(truly_missing)}")
        print("-" * 60)

        # Group by HTML file
        by_html = defaultdict(list)
        for img_info in truly_missing:
            by_html[img_info['html_file']].append(img_info['canvas_id'])

        print(f"\nMissing images by HTML file:")
        for html_file, canvas_ids in sorted(by_html.items())[:10]:
            print(f"\n  📄 {html_file}")
            print(f"     Missing Canvas IDs: {', '.join(canvas_ids[:10])}")
            if len(canvas_ids) > 10:
                print(f"     ... and {len(canvas_ids) - 10} more")

        if len(by_html) > 10:
            print(f"\n  ... and {len(by_html) - 10} more HTML files with missing images")

    # Summary
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)
    print(f"Total missing images: {len(missing_images)}")
    print(f"✅ Found in other locations: {len(missing_images) - len(truly_missing)}")
    print(f"❌ Truly missing: {len(truly_missing)}")

    if by_location:
        print(f"\n📍 Found locations:")
        for location, images in sorted(by_location.items()):
            print(f"   {location}: {len(images)} images")

    # Generate copy commands for found images
    if by_location:
        print(f"\n💡 Suggested Actions:")
        print("-" * 60)

        # Images in archive that should be copied
        if 'archive (365_Update)' in by_location:
            archive_images = by_location['archive (365_Update)']
            print(f"\n1. Copy {len(archive_images)} images from archive to their HTML directories:")
            print("   (These images need to be copied to match the new structure)")

            # Group by destination
            by_dest = defaultdict(list)
            for img_info in archive_images:
                by_dest[img_info['html_dir']].append(img_info)

            print(f"\n   Copy commands (sample):")
            for html_dir, images in list(by_dest.items())[:5]:
                for img_info in images[:3]:
                    src = img_info['found_file']
                    dst = html_dir / src.name
                    print(f"   cp '{src}' '{dst}'")
                if len(images) > 3:
                    print(f"   ... and {len(images) - 3} more for this directory")

        # Images in parent directories
        if any('parent directory' in loc for loc in by_location.keys()):
            parent_images = [img for img in missing_images if 'parent directory' in img['location']]
            print(f"\n2. {len(parent_images)} images are in parent directories")
            print("   (Paths are correct, images just need to be verified)")

if __name__ == '__main__':
    main()
