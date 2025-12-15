#!/usr/bin/env python3
"""
Rename downloaded Canvas image files to match Canvas file IDs and create local HTML versions.

This script:
1. Extracts Canvas file IDs from HTML (from both src and data-api-endpoint attributes)
2. Matches downloaded images to Canvas IDs (by checking file size)
3. Renames images to <canvas_id>.<ext> format (no "file_" prefix)
4. Creates a _local.html version with paths pointing to local image files
5. Keeps original HTML file unchanged (for pushing text content back to Canvas)
"""

import argparse
import re
import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import toml

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import get_config_path, get_winter_updates_dir, get_project_root

def get_canvas_file_ids_from_html(html_file):
    """Extract Canvas file IDs and metadata from HTML.

    Checks both src attribute and data-api-endpoint attribute for file IDs.
    """
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
                'api_endpoint': api_endpoint,
                'img_element': img
            })

    return file_info

def download_canvas_file_info(file_id, canvas_token, canvas_base_url):
    """Get file metadata from Canvas API."""
    headers = {'Authorization': f'Bearer {canvas_token}'}
    url = f"{canvas_base_url}/api/v1/files/{file_id}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  ⚠️  Could not get info for file {file_id}: {e}")
        return None

def match_files_to_canvas_ids(downloaded_dir, canvas_file_info_list, canvas_token, canvas_base_url):
    """Match downloaded files to Canvas IDs by file size.

    Searches recursively in downloaded_dir and subdirectories.
    """
    if not downloaded_dir.exists():
        print(f"  ⚠️  Directory does not exist: {downloaded_dir}")
        return []

    # Search recursively for image files
    downloaded_files = list(downloaded_dir.rglob('*'))
    downloaded_files = [f for f in downloaded_files
                       if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']]

    matches = []
    matched_files = set()

    for canvas_info in canvas_file_info_list:
        file_id = canvas_info['file_id']
        print(f"\n🔍 Looking for Canvas file ID: {file_id}")

        # Get file info from Canvas API
        canvas_file_data = download_canvas_file_info(file_id, canvas_token, canvas_base_url)

        if canvas_file_data:
            canvas_size = canvas_file_data.get('size', 0)
            canvas_filename = canvas_file_data.get('filename', '')
            canvas_content_type = canvas_file_data.get('content-type', '')

            print(f"   Canvas size: {canvas_size} bytes")
            print(f"   Canvas filename: {canvas_filename}")

            # Try to match by size (exclude already matched files)
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
                print(f"   ✅ Matched by size: {matched_file.name}")
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
                print(f"   ⚠️  Multiple files with same size, using first match: {matched_file.name}")
            else:
                print(f"   ❌ No size match found")

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

def rename_images(matches, image_dir):
    """Rename matched image files to <canvas_id>.<ext> format (no "file_" prefix).

    Returns mapping of canvas_id -> new file path.
    """
    image_dir.mkdir(parents=True, exist_ok=True)

    renamed = {}
    for match in matches:
        canvas_id = match['canvas_id']
        local_file = match['local_file']
        ext = local_file.suffix.lower()

        # Use <canvas_id>.<ext> format (no "file_" prefix)
        new_name = f"{canvas_id}{ext}"

        # Determine where to place the renamed file
        # If image is already in the target directory, rename in place
        # Otherwise, move to image_dir
        if local_file.parent == image_dir:
            new_path = image_dir / new_name
        else:
            new_path = image_dir / new_name

        if new_path.exists() and new_path != local_file:
            print(f"  ⚠️  {new_name} already exists, skipping")
            # Use existing file
            renamed[canvas_id] = new_path
            continue

        # Move/rename the file
        if local_file.parent != image_dir:
            # Move to image directory
            local_file.rename(new_path)
        else:
            # Just rename in place
            local_file.rename(new_path)

        renamed[canvas_id] = new_path
        print(f"  ✅ Renamed: {local_file.name} → {new_name}")

    return renamed

def create_local_html(html_file, matches, renamed_images, image_dir):
    """Create _local.html version with paths pointing to local image files.

    Original HTML file is kept unchanged.
    In the new structure, images are in the same directory as HTML, so paths are simpler.
    """
    # Read original HTML
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(html_file, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"  ⚠️  Could not read {html_file}: {e}")
            return False

    soup = BeautifulSoup(content, 'html.parser')
    user_content = soup.find('div', class_='user_content')

    if not user_content:
        print(f"  ⚠️  No user_content div found in HTML")
        return False

    # Create mapping: canvas_id -> relative path to local image
    # In new structure, images are in same directory, so just use filename
    canvas_to_path = {}
    for match in matches:
        canvas_id = match['canvas_id']
        if canvas_id in renamed_images:
            new_file = renamed_images[canvas_id]
            # If image is in same directory as HTML, use just filename
            # Otherwise calculate relative path
            if new_file.parent == Path(html_file).parent:
                rel_path = new_file.name
            else:
                rel_path = calculate_relative_path(html_file, new_file)
            canvas_to_path[canvas_id] = rel_path

    # Update img src attributes to point to local files
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
            match = re.search(r'/files/(\d+)', api_endpoint)
            if match:
                file_id = match.group(1)

        if file_id and file_id in canvas_to_path:
            new_src = canvas_to_path[file_id]
            # Only update if the path is different
            if src != new_src:
                img['src'] = new_src
                updated = True

    # Update CSS link paths to be relative to the new HTML file location
    html_path = Path(html_file)
    html_dir = html_path.parent

    # Find the project root (where CSS files are located)
    # CSS files are in the project root directory
    project_root = html_path
    while project_root.parent != project_root:
        # Check if this directory contains CSS files
        css_files = list(project_root.glob('*.css'))
        if css_files:
            break
        project_root = project_root.parent

    # Calculate relative path from HTML file to project root, then to assets/css
    # HTML is in: data/current/WINTER-25-26-UPDATES/Module-X/Section-X-Y/LA-X-Y-Z/
    # CSS is in: assets/css/
    # Need to go: up to project root, then into assets/css/
    try:
        project_root = get_project_root()
        assets_css_dir = project_root / 'assets' / 'css'
        css_rel_path = os.path.relpath(assets_css_dir, html_dir)
        if css_rel_path == '.':
            css_rel_path = ''
        else:
            css_rel_path = css_rel_path.replace('\\', '/') + '/'
    except ValueError:
        # Fallback: calculate based on depth
        # data/current/WINTER-25-26-UPDATES/Module-X/Section-X-Y/LA-X-Y-Z = 6 levels
        # Need to go up 6 levels to project root, then down to assets/css
        winter_dir = get_winter_updates_dir()
        try:
            depth = len(html_dir.parts) - len(winter_dir.parts)
            css_rel_path = '../' * (depth + 3) + 'assets/css/'  # +3 for data/current/WINTER-25-26-UPDATES
        except:
            css_rel_path = '../../../../../../assets/css/'  # Safe fallback

    # Update all CSS link hrefs in the head section
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href', '')
        # Skip external URLs (S3, CDN, etc.)
        if href.startswith('http://') or href.startswith('https://'):
            continue

        # Update relative CSS paths
        if href.startswith('../'):
            # Calculate new relative path
            # Original: ../../canvas-fonts.css
            # New: ../../../../canvas-fonts.css (for LA files)
            css_filename = Path(href).name
            new_href = f"{css_rel_path}{css_filename}"
            link['href'] = new_href
            updated = True
            print(f"  ✅ Updated CSS path: {href} -> {new_href}")

    if updated:
        # Create _local.html filename
        html_path = Path(html_file)
        local_html_path = html_path.parent / f"{html_path.stem}_local{html_path.suffix}"

        # Write local HTML file
        with open(local_html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        print(f"  ✅ Created local HTML: {local_html_path.name}")
        return True

    return False

def main():
    parser = argparse.ArgumentParser(
        description='Rename Canvas images to Canvas file IDs and create local HTML versions'
    )
    parser.add_argument(
        '--html-file',
        type=Path,
        required=True,
        help='Path to Canvas HTML file'
    )
    parser.add_argument(
        '--downloaded-dir',
        type=Path,
        required=True,
        help='Directory containing downloaded image files (searched recursively)'
    )
    parser.add_argument(
        '--image-dir',
        type=Path,
        help='Directory where renamed images should be placed (default: same as downloaded-dir)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=get_config_path(),
        help='Path to config.toml file (default: config.toml in project root)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Load Canvas config
    config = toml.load(args.config)
    canvas_token = config['endpoint']['api_key']
    canvas_base_url = config['endpoint']['endpoint']

    # Get Canvas file IDs from HTML
    print(f"📄 Extracting Canvas file IDs from: {args.html_file}")
    canvas_file_info = get_canvas_file_ids_from_html(args.html_file)

    if not canvas_file_info:
        print("  ⚠️  No Canvas file IDs found in HTML")
        return

    print(f"✅ Found {len(canvas_file_info)} Canvas image references")

    # Match downloaded files to Canvas IDs
    print(f"\n🔍 Matching downloaded files in: {args.downloaded_dir}")
    matches = match_files_to_canvas_ids(
        args.downloaded_dir,
        canvas_file_info,
        canvas_token,
        canvas_base_url
    )

    if not matches:
        print("  ⚠️  No images matched")
        return

    # Set image directory
    image_dir = args.image_dir or args.downloaded_dir

    # Rename images
    print(f"\n📝 Renaming images to: {image_dir}")
    if args.dry_run:
        print("  [DRY RUN] Would rename:")
        for match in matches:
            canvas_id = match['canvas_id']
            local_file = match['local_file']
            ext = local_file.suffix.lower()
            print(f"    {local_file.name} → {canvas_id}{ext}")
    else:
        renamed_images = rename_images(matches, image_dir)

        # Create local HTML version
        print(f"\n📄 Creating local HTML version...")
        if create_local_html(args.html_file, matches, renamed_images, image_dir):
            print(f"  ✅ Local HTML created: {args.html_file.stem}_local.html")
        else:
            print(f"  ⚠️  Local HTML not created (no changes needed?)")

    print(f"\n✅ Processing complete")
    print(f"\n📋 Summary:")
    print(f"   Images matched: {len(matches)}")
    if not args.dry_run:
        print(f"   Original HTML: {args.html_file.name} (unchanged)")
        print(f"   Local HTML: {args.html_file.stem}_local.html")

if __name__ == '__main__':
    main()

