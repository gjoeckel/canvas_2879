#!/usr/bin/env python3
"""
Rename downloaded Canvas images to Canvas file IDs and update HTML files.

This script:
1. Extracts Canvas file IDs from all HTML files
2. Matches downloaded images to Canvas IDs using file size
3. Renames images to {canvas_id}.{ext} format
4. Updates HTML files to use relative paths to local images
5. Reports unmatched images
"""

import argparse
import re
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import toml
from collections import defaultdict

def load_canvas_config(config_path):
    """Load Canvas API configuration."""
    config = toml.load(config_path)
    return {
        'token': config['endpoint']['api_key'],
        'base_url': config['endpoint']['endpoint']
    }

def get_canvas_file_info(file_id, canvas_config):
    """Get file metadata from Canvas API."""
    headers = {'Authorization': f'Bearer {canvas_config["token"]}'}
    url = f"{canvas_config['base_url']}/api/v1/files/{file_id}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  ⚠️  Could not get info for file {file_id}: {e}")
        return None

def extract_canvas_file_ids_from_html(html_file):
    """Extract Canvas file IDs and image metadata from HTML."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try other encodings
        try:
            with open(html_file, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"  ⚠️  Could not read {html_file}: {e}")
            return []

    soup = BeautifulSoup(content, 'html.parser')
    user_content = soup.find('div', class_='user_content')

    if not user_content:
        return []

    file_info = []
    for img in user_content.find_all('img'):
        src = img.get('src', '')
        api_endpoint = img.get('data-api-endpoint', '')

        # Try to get Canvas file ID from src URL or data-api-endpoint
        file_id = None
        match = re.search(r'/files/(\d+)', src)
        if match:
            file_id = match.group(1)
        else:
            # Check data-api-endpoint attribute
            match = re.search(r'/files/(\d+)', api_endpoint)
            if match:
                file_id = match.group(1)

        if file_id:
            alt = img.get('alt', 'No alt text')
            file_info.append({
                'file_id': file_id,
                'alt': alt,
                'src': src,
                'img_element': img
            })

    return file_info

def map_html_to_image_directory(html_file, base_dir):
    """Map HTML file location to corresponding 365_Update subdirectory."""
    html_path = Path(html_file)
    relative_path = html_path.relative_to(base_dir)

    # Map HTML structure to 365_Update structure
    parts = relative_path.parts

    if len(parts) >= 2:
        # Examples:
        # "1 Start Here/course_orientation.html" -> "365_Update/Course Orientation"
        # "2 Module 1_ Document Content/section_1.html" -> "365_Update/m1/1-1/..."

        if parts[0] == "1 Start Here":
            # Map to "Course Orientation" or other Start Here pages
            page_name = html_path.stem.lower()
            if "course_orientation" in page_name or "course-orientation" in page_name:
                return base_dir / "365_Update" / "Course Orientation"
            elif "course_details" in page_name or "course-details" in page_name:
                return base_dir / "365_Update" / "Course images"
            else:
                return base_dir / "365_Update" / "Course images"

        elif parts[0].startswith("2 Module 1"):
            # Try to map to nested structure: m1/1-X/...
            module_dir = base_dir / "365_Update" / "m1"
            # Look for matching subdirectory based on section name
            section_name = html_path.stem.lower()
            if "section 1" in section_name or "overview" in section_name:
                # Try 1-1 subdirectory
                for subdir in module_dir.iterdir():
                    if subdir.is_dir() and subdir.name.startswith("1-1"):
                        return subdir
            elif "section 2" in section_name or "images" in section_name:
                for subdir in module_dir.iterdir():
                    if subdir.is_dir() and subdir.name.startswith("1-2"):
                        return subdir
            elif "section 3" in section_name or "hyperlinks" in section_name:
                for subdir in module_dir.iterdir():
                    if subdir.is_dir() and subdir.name.startswith("1-3"):
                        return subdir
            elif "section 4" in section_name or "contrast" in section_name:
                for subdir in module_dir.iterdir():
                    if subdir.is_dir() and subdir.name.startswith("1-4"):
                        return subdir
            elif "section 5" in section_name:
                for subdir in module_dir.iterdir():
                    if subdir.is_dir() and subdir.name.startswith("1-5"):
                        return subdir
            # Fallback to m1 root
            return module_dir

        elif parts[0].startswith("3 Module 2"):
            return base_dir / "365_Update" / "m2"
        elif parts[0].startswith("4 Module 3"):
            return base_dir / "365_Update" / "m3"
        elif parts[0].startswith("5 Module 4"):
            return base_dir / "365_Update" / "m4"
        elif parts[0].startswith("7 Module 5"):
            return base_dir / "365_Update" / "m5"

    # Default fallback
    return base_dir / "365_Update" / "Course images"

def match_images_to_canvas_ids(image_dir, canvas_file_info_list, canvas_config):
    """Match downloaded images to Canvas IDs by file size."""
    if not image_dir.exists():
        return []

    # Search recursively in subdirectories (e.g., m1/1-1/screenshots/)
    downloaded_files = list(image_dir.rglob('*'))
    downloaded_files = [f for f in downloaded_files if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']]

    matches = []
    matched_files = set()

    for canvas_info in canvas_file_info_list:
        file_id = canvas_info['file_id']

        # Get file info from Canvas API
        canvas_file_data = get_canvas_file_info(file_id, canvas_config)

        if canvas_file_data:
            canvas_size = canvas_file_data.get('size', 0)

            # Try to match by size
            size_matches = [f for f in downloaded_files
                          if f not in matched_files and f.stat().st_size == canvas_size]

            if len(size_matches) == 1:
                matched_file = size_matches[0]
                matches.append({
                    'canvas_id': file_id,
                    'local_file': matched_file,
                    'canvas_size': canvas_size,
                    'canvas_info': canvas_file_data
                })
                matched_files.add(matched_file)
            elif len(size_matches) > 1:
                # Multiple files with same size - use first one
                matched_file = size_matches[0]
                matches.append({
                    'canvas_id': file_id,
                    'local_file': matched_file,
                    'canvas_size': canvas_size,
                    'canvas_info': canvas_file_data
                })
                matched_files.add(matched_file)
                print(f"  ⚠️  Multiple files with same size for {file_id}, using first match")

    return matches

def calculate_relative_path(from_file, to_file):
    """Calculate relative path from HTML file to image file."""
    from_path = Path(from_file).parent.resolve()
    to_path = Path(to_file).resolve()

    try:
        rel_path = to_path.relative_to(from_path)
        return str(rel_path)
    except ValueError:
        # Paths don't share a common base, calculate manually
        from_parts = list(from_path.parts)
        to_parts = list(to_path.parts)

        # Find common prefix
        common_len = 0
        for i in range(min(len(from_parts), len(to_parts))):
            if from_parts[i] == to_parts[i]:
                common_len += 1
            else:
                break

        # Calculate how many levels to go up
        up_levels = len(from_parts) - common_len

        # Build relative path: go up, then down
        if up_levels > 0:
            rel_path = Path('../' * up_levels) / Path(*to_parts[common_len:])
        else:
            rel_path = Path(*to_parts[common_len:])

        return str(rel_path)

def rename_image_file(old_path, canvas_id, keep_extension=True):
    """Rename image file to Canvas ID format."""
    if keep_extension:
        ext = old_path.suffix
        new_name = f"{canvas_id}{ext}"
    else:
        new_name = str(canvas_id)

    new_path = old_path.parent / new_name

    if new_path.exists() and new_path != old_path:
        print(f"  ⚠️  {new_name} already exists, skipping rename")
        return old_path

    old_path.rename(new_path)
    return new_path

def update_html_image_paths(html_file, matches, image_dir, base_dir):
    """Update HTML file to use local image paths."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    user_content = soup.find('div', class_='user_content')

    if not user_content:
        return False

    # Create mapping: canvas_id -> new file path
    canvas_to_path = {}
    for match in matches:
        canvas_id = match['canvas_id']
        new_file = match.get('new_path', match['local_file'])
        rel_path = calculate_relative_path(html_file, new_file)
        canvas_to_path[canvas_id] = rel_path

    # Update img src attributes
    updated = False
    for img in user_content.find_all('img'):
        src = img.get('src', '')
        api_endpoint = img.get('data-api-endpoint', '')

        # Get Canvas file ID from src URL or data-api-endpoint
        file_id = None
        match = re.search(r'/files/(\d+)', src)
        if match:
            file_id = match.group(1)
        else:
            # Check data-api-endpoint attribute
            match = re.search(r'/files/(\d+)', api_endpoint)
            if match:
                file_id = match.group(1)

        if file_id and file_id in canvas_to_path:
            new_src = canvas_to_path[file_id]
            # Only update if the path is different (avoid unnecessary updates)
            if src != new_src:
                img['src'] = new_src
                updated = True

    if updated:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    return False

def main():
    parser = argparse.ArgumentParser(
        description='Rename Canvas images to file IDs and update HTML files'
    )
    parser.add_argument(
        '--base-dir',
        type=Path,
        default=Path('WINTER 25-26 COURSE UPDATES'),
        help='Base directory containing HTML files and 365_Update'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('config.toml'),
        help='Path to config.toml file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    base_dir = args.base_dir.resolve()
    canvas_config = load_canvas_config(args.config)

    # Find HTML files (exclude temporary files and old files with spaces)
    all_html_files = [f for f in base_dir.rglob('*.html')
                      if not f.name.startswith('~$')
                      and not f.name.startswith('.~')
                      and ' ' not in f.stem  # Skip old files with spaces in names
                      and 'docs' not in str(f)]  # Skip docs directory

    # Process all HTML files
    html_files = all_html_files
    print(f"📄 Found {len(html_files)} HTML files to process")

    # Track unmatched images by HTML file
    unmatched_by_html = defaultdict(list)

    # Process each HTML file
    total_renamed = 0
    total_updated = 0

    for html_file in html_files:
        print(f"\n📄 Processing: {html_file.relative_to(base_dir)}")

        # Extract Canvas file IDs
        file_info_list = extract_canvas_file_ids_from_html(html_file)
        if not file_info_list:
            print("  ℹ️  No Canvas images found")
            continue

        print(f"  Found {len(file_info_list)} Canvas image references")

        # Map to image directory
        image_dir = map_html_to_image_directory(html_file, base_dir)
        print(f"  Image directory: {image_dir.relative_to(base_dir)}")

        # Match images to Canvas IDs
        matches = match_images_to_canvas_ids(image_dir, file_info_list, canvas_config)

        # Track unmatched
        matched_ids = {m['canvas_id'] for m in matches}
        for file_info in file_info_list:
            if file_info['file_id'] not in matched_ids:
                unmatched_by_html[html_file].append(file_info['file_id'])

        if not matches:
            print("  ⚠️  No images matched")
            continue

        # Rename images
        print(f"  📝 Renaming {len(matches)} images...")
        for match in matches:
            canvas_id = match['canvas_id']
            old_file = match['local_file']

            if args.dry_run:
                print(f"    Would rename: {old_file.name} → {canvas_id}{old_file.suffix}")
            else:
                new_file = rename_image_file(old_file, canvas_id)
                match['new_path'] = new_file
                print(f"    ✅ Renamed: {old_file.name} → {new_file.name}")
                total_renamed += 1

        # Update HTML file
        if not args.dry_run:
            if update_html_image_paths(html_file, matches, image_dir, base_dir):
                print(f"  ✅ Updated HTML file")
                total_updated += 1
            else:
                print(f"  ⚠️  HTML file not updated (no changes needed?)")

    # Report unmatched images
    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    print(f"Images renamed: {total_renamed}")
    print(f"HTML files updated: {total_updated}")
    print(f"HTML files with unmatched images: {len(unmatched_by_html)}")

    if unmatched_by_html:
        print(f"\n⚠️  Unmatched Images by HTML File:")
        print(f"{'='*60}")
        for html_file, file_ids in unmatched_by_html.items():
            rel_path = html_file.relative_to(base_dir)
            print(f"\n📄 {rel_path}")
            for file_id in file_ids:
                print(f"   - Canvas ID: {file_id}")

if __name__ == '__main__':
    main()

