#!/usr/bin/env python3
"""
Upload entire directory to Box folder using Box API.

This script:
1. Recursively walks through a directory
2. Creates folder structure in Box
3. Uploads all files to Box, preserving directory structure
"""

import os
import json
import sys
import time
from pathlib import Path
import requests
from urllib.parse import urlparse

# Box API endpoints
BOX_API_BASE = "https://api.box.com/2.0"
BOX_UPLOAD_API = "https://upload.box.com/api/2.0"

# Configuration
COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
CONFIG_FILE = COURSE_DIR / ".box-api-config.json"

def load_config():
    """Load Box OAuth configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def get_access_token():
    """Get Box access token from config or environment."""
    config = load_config()

    # Try config file first
    if config:
        # Check top-level keys
        access_token = config.get('access_token') or config.get('developer_token')
        if access_token:
            return access_token

        # Check nested oauth2 structure
        oauth2 = config.get('oauth2', {})
        access_token = oauth2.get('access_token')
        if access_token:
            return access_token

    # Try environment variables
    access_token = os.getenv('BOX_ACCESS_TOKEN') or os.getenv('BOX_DEVELOPER_TOKEN')
    if access_token:
        return access_token

    print("❌ Box API configuration not found!")
    print(f"   Please run get-box-oauth-token.py first")
    print(f"   Or set BOX_ACCESS_TOKEN or BOX_DEVELOPER_TOKEN environment variable")
    print(f"   Config file should be at: {CONFIG_FILE}")
    sys.exit(1)

def refresh_token_if_needed():
    """Refresh access token if expired."""
    config = load_config()
    if not config:
        return None

    # Try to refresh if we have refresh token
    if 'refresh_token' in config and config.get('refresh_token'):
        # For now, just return current token
        # In production, you'd check expiration and refresh
        return config.get('access_token')

    return config.get('access_token')

def create_box_folder(parent_folder_id, folder_name, access_token, max_retries=3):
    """Create a folder in Box with rate limit handling."""
    url = f"{BOX_API_BASE}/folders"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': folder_name,
        'parent': {'id': parent_folder_id}
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt)
                time.sleep(wait_time)
                continue
            else:
                print(f"  ⚠️  Network error creating folder '{folder_name}': {e}")
                return None

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get('retry-after', 60))
            if attempt < max_retries - 1:
                time.sleep(retry_after)
                continue
            else:
                print(f"  ⚠️  Rate limited creating folder '{folder_name}'")
                return None

        if response.status_code == 201:
            return response.json()['id']
        elif response.status_code == 409:
            # Folder already exists, get its ID
            url = f"{BOX_API_BASE}/folders/{parent_folder_id}/items"
            params = {'limit': 1000}
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                items = response.json().get('entries', [])
                for item in items:
                    if item['type'] == 'folder' and item['name'] == folder_name:
                        return item['id']
            return None
        else:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt)
                time.sleep(wait_time)
                continue
            else:
                print(f"  ⚠️  Error creating folder '{folder_name}': {response.status_code}")
                print(f"     Response: {response.text[:200]}")
                return None

    return None

def upload_file_to_box(folder_id, file_path, access_token):
    """Upload a file to Box folder."""
    file_name = file_path.name
    file_size = file_path.stat().st_size

    # Box best practice: Use chunked upload for files > 50MB
    # For files <= 50MB, use direct upload (more efficient)
    if file_size > 50 * 1024 * 1024:  # 50MB
        # Use chunked upload for large files
        return upload_file_chunked(folder_id, file_path, access_token)
    else:
        # Direct upload for smaller files
        return upload_file_direct(folder_id, file_path, access_token)

def upload_file_direct(folder_id, file_path, access_token, max_retries=3):
    """Upload file directly (for files <= 50MB) with rate limit handling."""
    url = f"{BOX_UPLOAD_API}/files/content"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    for attempt in range(max_retries):
        # Prepare multipart form data
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, 'application/octet-stream')
            }
            data = {
                'parent_id': folder_id
            }

            try:
                response = requests.post(url, headers=headers, files=files, data=data, timeout=300)
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    print(f"     ⚠️  Network error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"  ❌ Network error after {max_retries} attempts: {e}")
                    return None

        # Handle rate limiting (429 Too Many Requests)
        if response.status_code == 429:
            retry_after = int(response.headers.get('retry-after', 60))
            if attempt < max_retries - 1:
                print(f"     ⚠️  Rate limited, waiting {retry_after}s...")
                time.sleep(retry_after)
                continue
            else:
                print(f"  ❌ Rate limited after {max_retries} attempts")
                return None

        if response.status_code == 201:
            file_info = response.json()['entries'][0]
            return file_info['id']
        elif response.status_code == 409:
            # File already exists, get its ID
            url = f"{BOX_API_BASE}/folders/{folder_id}/items"
            params = {'limit': 1000}
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                items = response.json().get('entries', [])
                for item in items:
                    if item['type'] == 'file' and item['name'] == file_path.name:
                        return item['id']
            return None
        else:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt)
                print(f"     ⚠️  Error {response.status_code}, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"  ⚠️  Error uploading '{file_path.name}': {response.status_code}")
                print(f"     Response: {response.text[:200]}")
                return None

    return None

def upload_file_chunked(folder_id, file_path, access_token):
    """Upload large file using chunked upload."""
    # For simplicity, we'll use direct upload even for large files
    # In production, implement proper chunked upload
    return upload_file_direct(folder_id, file_path, access_token)

def upload_directory_recursive(source_dir, box_folder_id, access_token, base_path=None):
    """Recursively upload directory structure to Box."""
    if base_path is None:
        base_path = source_dir

    uploaded_files = 0
    uploaded_folders = 0
    errors = []

    # Walk through directory
    for root, dirs, files in os.walk(source_dir):
        # Calculate relative path
        rel_path = Path(root).relative_to(base_path)

        # Create folder structure in Box
        current_box_folder_id = box_folder_id
        if str(rel_path) != '.':
            # Create nested folders
            path_parts = rel_path.parts
            for part in path_parts:
                print(f"  📁 Creating folder: {part}")
                folder_id = create_box_folder(current_box_folder_id, part, access_token)
                if folder_id:
                    current_box_folder_id = folder_id
                    uploaded_folders += 1
                else:
                    print(f"  ❌ Failed to create folder: {part}")
                    errors.append(f"Failed to create folder: {rel_path / part}")
                    break

        # Upload files in current directory
        for file_name in files:
            file_path = Path(root) / file_name
            rel_file_path = file_path.relative_to(base_path)

            print(f"  📄 Uploading: {rel_file_path}")
            file_id = upload_file_to_box(current_box_folder_id, file_path, access_token)

            if file_id:
                uploaded_files += 1
                print(f"     ✅ Uploaded (ID: {file_id})")
            else:
                errors.append(f"Failed to upload: {rel_file_path}")
                print(f"     ❌ Failed to upload")

            # Rate limiting: Box allows 240 file uploads per minute
            # Add delay to stay under limit (250ms = ~240 uploads/minute)
            time.sleep(0.25)

    return uploaded_files, uploaded_folders, errors

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Upload directory to Box folder')
    parser.add_argument('--source-dir', type=str,
                       default='/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES',
                       help='Source directory to upload')
    parser.add_argument('--folder-id', type=str, required=True,
                       help='Box folder ID to upload to')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run - show what would be uploaded without actually uploading')

    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"❌ Source directory does not exist: {source_dir}")
        sys.exit(1)

    if not source_dir.is_dir():
        print(f"❌ Source path is not a directory: {source_dir}")
        sys.exit(1)

    print("📦 Box Directory Upload")
    print("=" * 60)
    print(f"Source: {source_dir}")
    print(f"Box Folder ID: {args.folder_id}")
    print(f"Dry Run: {args.dry_run}")
    print()

    if args.dry_run:
        print("🔍 Dry Run - Counting files...")
        file_count = sum(1 for _ in source_dir.rglob('*') if _.is_file())
        dir_count = sum(1 for _ in source_dir.rglob('*') if _.is_dir())
        print(f"   Files: {file_count}")
        print(f"   Directories: {dir_count}")
        print("\n✅ Dry run complete. Run without --dry-run to upload.")
        return

    # Get access token
    print("🔑 Getting Box access token...")
    access_token = get_access_token()
    print("   ✅ Token loaded")
    print()

    # Upload directory
    print("📤 Starting upload...")
    print()

    start_time = time.time()
    uploaded_files, uploaded_folders, errors = upload_directory_recursive(
        source_dir, args.folder_id, access_token
    )
    elapsed_time = time.time() - start_time

    # Summary
    print()
    print("=" * 60)
    print("📊 Upload Summary")
    print("=" * 60)
    print(f"✅ Files uploaded: {uploaded_files}")
    print(f"✅ Folders created: {uploaded_folders}")
    print(f"❌ Errors: {len(errors)}")
    print(f"⏱️  Time elapsed: {elapsed_time:.1f} seconds")

    if errors:
        print(f"\n⚠️  Errors encountered:")
        for error in errors[:10]:
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")

    print(f"\n✅ Upload complete!")
    print(f"   View folder: https://usu.app.box.com/folder/{args.folder_id}")

if __name__ == '__main__':
    main()
