#!/usr/bin/env python3
"""
Copy missing images from archive and validate missing image IDs.

This script:
1. Copies 31 images found in archive to their HTML directories
2. Validates 48 missing image IDs using original Canvas HTML files
3. Attempts to locate or provides information for redownloading
"""

import sys
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
import re
from collections import defaultdict

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import get_winter_updates_dir, get_winter_archive_dir, get_project_root

def copy_images_from_archive():
    """Copy images found in archive to their HTML directories."""
    winter_dir = get_winter_updates_dir()
    archive_dir = get_winter_archive_dir() / '365_Update'
    local_html_files = list(winter_dir.rglob("*_local.html"))

    print("📋 Step 1: Copying images from archive...")
    print("=" * 60)

    images_to_copy = []

    # Find missing images that exist in archive
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

                # Check if image is missing
                if src.startswith('../'):
                    image_path = (html_dir / src).resolve()
                else:
                    image_path = html_dir / src

                if not image_path.exists():
                    # Extract Canvas ID
                    canvas_id = None
                    match = re.search(r'(\d+)\.(png|jpg|jpeg|gif)', src, re.IGNORECASE)
                    if match:
                        canvas_id = match.group(1)
                        ext = match.group(2).lower()
                    else:
                        match = re.search(r'/files/(\d+)', src)
                        if match:
                            canvas_id = match.group(1)
                            ext = 'png'  # Default

                    if canvas_id:
                        # Check if exists in archive
                        for archive_ext in ['.png', '.jpg', '.jpeg', '.gif']:
                            archive_file = archive_dir / f"{canvas_id}{archive_ext}"
                            if archive_file.exists():
                                dest_file = html_dir / f"{canvas_id}{archive_ext}"
                                images_to_copy.append({
                                    'source': archive_file,
                                    'dest': dest_file,
                                    'canvas_id': canvas_id,
                                    'html_file': html_file.relative_to(winter_dir)
                                })
                                break
        except Exception as e:
            print(f"  ⚠️  Error processing {html_file}: {e}")

    # Copy images
    copied = 0
    failed = 0

    print(f"\nFound {len(images_to_copy)} images to copy from archive\n")

    for img_info in images_to_copy:
        try:
            # Ensure destination directory exists
            img_info['dest'].parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(img_info['source'], img_info['dest'])
            copied += 1

            if copied <= 10:
                print(f"  ✅ Copied: {img_info['canvas_id']}{img_info['dest'].suffix}")
                print(f"     To: {img_info['html_file'].parent}")
        except Exception as e:
            failed += 1
            print(f"  ❌ Failed to copy {img_info['canvas_id']}: {e}")

    print(f"\n✅ Copied {copied} images")
    if failed > 0:
        print(f"❌ Failed to copy {failed} images")

    return copied, failed

def validate_missing_ids_from_canvas_html():
    """Validate missing image IDs using original Canvas HTML files."""
    winter_dir = get_winter_updates_dir()
    archive_html_dir = get_winter_archive_dir()

    print("\n📋 Step 2: Validating missing image IDs from Canvas HTML files...")
    print("=" * 60)

    # Get list of truly missing Canvas IDs
    missing_ids = set()
    local_html_files = list(winter_dir.rglob("*_local.html"))

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

                if src.startswith('../'):
                    image_path = (html_dir / src).resolve()
                else:
                    image_path = html_dir / src

                if not image_path.exists():
                    canvas_id = None
                    match = re.search(r'(\d+)\.(png|jpg|jpeg|gif)', src, re.IGNORECASE)
                    if match:
                        canvas_id = match.group(1)
                    else:
                        match = re.search(r'/files/(\d+)', src)
                        if match:
                            canvas_id = match.group(1)

                    if canvas_id:
                        # Check if it exists anywhere
                        found = False
                        # Check same directory
                        for ext in ['.png', '.jpg', '.jpeg', '.gif']:
                            if (html_dir / f"{canvas_id}{ext}").exists():
                                found = True
                                break
                        # Check archive
                        if not found:
                            archive_dir = get_winter_archive_dir() / '365_Update'
                            for ext in ['.png', '.jpg', '.jpeg', '.gif']:
                                if (archive_dir / f"{canvas_id}{ext}").exists():
                                    found = True
                                    break

                        if not found:
                            missing_ids.add(canvas_id)
        except Exception as e:
            pass

    print(f"\nFound {len(missing_ids)} unique missing Canvas IDs to validate\n")

    # Find original Canvas HTML files (non-local)
    original_html_files = []
    for html_file in winter_dir.rglob("*.html"):
        if not html_file.name.endswith('_local.html'):
            original_html_files.append(html_file)

    # Also check archive HTML files
    archive_html_files = list(archive_html_dir.rglob("*.html"))
    if archive_html_files:
        original_html_files.extend(archive_html_files)

    print(f"Checking {len(original_html_files)} original Canvas HTML files...\n")

    # Validate each missing ID
    validated = {}
    not_found_in_html = []

    for canvas_id in sorted(missing_ids):
        found_in_html = False
        found_files = []

        for html_file in original_html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if Canvas ID is referenced in this HTML
                if f'/files/{canvas_id}' in content or f'data-api-endpoint="/api/v1/files/{canvas_id}' in content:
                    found_in_html = True
                    found_files.append(html_file.relative_to(get_project_root()))

                    # Try to extract image info
                    soup = BeautifulSoup(content, 'html.parser')
                    for img in soup.find_all('img'):
                        src = img.get('src', '')
                        api_endpoint = img.get('data-api-endpoint', '')

                        if f'/files/{canvas_id}' in src or f'/files/{canvas_id}' in api_endpoint:
                            # Get file size if available
                            file_size = None
                            if 'data-api-endpoint' in img.attrs:
                                # Try to get from data attributes
                                pass

                            validated[canvas_id] = {
                                'found_in_html': True,
                                'html_files': found_files,
                                'src': src,
                                'api_endpoint': api_endpoint
                            }
                            break
            except Exception as e:
                pass

        if not found_in_html:
            not_found_in_html.append(canvas_id)
            validated[canvas_id] = {
                'found_in_html': False,
                'html_files': []
            }

    # Report results
    found_count = sum(1 for v in validated.values() if v['found_in_html'])
    not_found_count = len(not_found_in_html)

    print(f"✅ Found in Canvas HTML: {found_count} IDs")
    print(f"❌ Not found in Canvas HTML: {not_found_count} IDs\n")

    if found_count > 0:
        print("Images found in Canvas HTML (can be downloaded):")
        print("-" * 60)
        for canvas_id, info in sorted(validated.items()):
            if info['found_in_html']:
                print(f"\n  Canvas ID: {canvas_id}")
                if info['html_files']:
                    print(f"    Found in: {info['html_files'][0]}")
                if info.get('api_endpoint'):
                    print(f"    API endpoint: {info['api_endpoint']}")

    if not_found_in_html:
        print(f"\n⚠️  IDs not found in any Canvas HTML files:")
        print("-" * 60)
        for canvas_id in sorted(not_found_in_html)[:20]:
            print(f"  - {canvas_id}")
        if len(not_found_in_html) > 20:
            print(f"  ... and {len(not_found_in_html) - 20} more")

    return validated, not_found_in_html

def attempt_download_missing_images(validated_ids):
    """Attempt to download missing images using Canvas API."""
    print("\n📋 Step 3: Attempting to download missing images...")
    print("=" * 60)

    # Load Canvas config
    try:
        import toml
        config_path = get_project_root() / 'config.toml'
        config = toml.load(config_path)
        canvas_token = config['endpoint']['api_key']
        canvas_base_url = config['endpoint']['endpoint']
    except Exception as e:
        print(f"  ⚠️  Could not load Canvas config: {e}")
        print("  Skipping download step")
        return

    print(f"\nCanvas API configured: {canvas_base_url}\n")

    # Download images that were found in HTML
    downloaded = 0
    failed = 0

    winter_dir = get_winter_updates_dir()
    local_html_files = list(winter_dir.rglob("*_local.html"))

    # Map Canvas IDs to their HTML directories
    id_to_dirs = defaultdict(set)
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

                canvas_id = None
                match = re.search(r'(\d+)\.(png|jpg|jpeg|gif)', src, re.IGNORECASE)
                if match:
                    canvas_id = match.group(1)
                else:
                    match = re.search(r'/files/(\d+)', src)
                    if match:
                        canvas_id = match.group(1)

                if canvas_id and canvas_id in validated_ids:
                    id_to_dirs[canvas_id].add(html_dir)
        except:
            pass

    # Download each image
    import requests

    for canvas_id, info in validated_ids.items():
        if not info['found_in_html']:
            continue

        if canvas_id not in id_to_dirs:
            continue

        # Get file info from Canvas API
        try:
            api_url = f"{canvas_base_url}/api/v1/files/{canvas_id}"
            headers = {'Authorization': f'Bearer {canvas_token}'}

            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                file_info = response.json()
                download_url = file_info.get('url')
                filename = file_info.get('filename', f'{canvas_id}.png')

                # Determine extension
                ext = Path(filename).suffix or '.png'

                # Download file
                download_response = requests.get(download_url, headers=headers, timeout=30)
                if download_response.status_code == 200:
                    # Save to each directory that needs it
                    for html_dir in id_to_dirs[canvas_id]:
                        dest_file = html_dir / f"{canvas_id}{ext}"
                        dest_file.parent.mkdir(parents=True, exist_ok=True)

                        with open(dest_file, 'wb') as f:
                            f.write(download_response.content)

                        downloaded += 1
                        if downloaded <= 5:
                            print(f"  ✅ Downloaded: {canvas_id}{ext}")
                            print(f"     To: {html_dir.relative_to(winter_dir)}")
                else:
                    failed += 1
                    if failed <= 3:
                        print(f"  ❌ Failed to download {canvas_id}: HTTP {download_response.status_code}")
            else:
                failed += 1
                if failed <= 3:
                    print(f"  ❌ Failed to get file info for {canvas_id}: HTTP {response.status_code}")
        except Exception as e:
            failed += 1
            if failed <= 3:
                print(f"  ❌ Error downloading {canvas_id}: {e}")

    print(f"\n✅ Downloaded {downloaded} images")
    if failed > 0:
        print(f"❌ Failed to download {failed} images")

def main():
    print("🔧 Copy and Validate Missing Images")
    print("=" * 60)

    # Step 1: Copy images from archive
    copied, failed = copy_images_from_archive()

    # Step 2: Validate missing IDs
    validated, not_found = validate_missing_ids_from_canvas_html()

    # Step 3: Attempt to download missing images
    if validated:
        attempt_download_missing_images(validated)

    # Final summary
    print("\n" + "=" * 60)
    print("📊 Final Summary")
    print("=" * 60)
    print(f"✅ Images copied from archive: {copied}")
    print(f"✅ Images found in Canvas HTML: {sum(1 for v in validated.values() if v['found_in_html'])}")
    print(f"❌ Images not found in Canvas HTML: {len(not_found)}")

    if not_found:
        print(f"\n⚠️  {len(not_found)} image IDs were not found in any Canvas HTML files.")
        print("   These may be:")
        print("   - Incorrect Canvas IDs")
        print("   - Images that were deleted from Canvas")
        print("   - Images referenced in a different way")

if __name__ == '__main__':
    main()
