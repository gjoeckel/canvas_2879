#!/usr/bin/env python3
"""
Get Box file IDs using Box REST API (no SDK required)

This script uses Box REST API directly with requests library.
"""

import json
import os
import sys
import requests
from pathlib import Path

BOX_DIR = Path("/Users/a00288946/Library/CloudStorage/Box-Box/WebAIM Shared/5 Online Courses/Winter 25-25 Course Update")
CANVAS_DIR = Path("/Users/a00288946/Projects/canvas_2879")
FILE_IDS_JSON = CANVAS_DIR / "box-file-ids.json"
TEMPLATE_FILE_IDS = CANVAS_DIR / "box-file-ids-template.json"
CONFIG_FILE = CANVAS_DIR / ".box-api-config.json"

BOX_API_BASE = "https://api.box.com/2.0"

def load_config():
    """Load Box API configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)

    # Try environment variables
    config = {
        'access_token': os.getenv('BOX_ACCESS_TOKEN'),
        'developer_token': os.getenv('BOX_DEVELOPER_TOKEN'),
        'folder_id': os.getenv('BOX_FOLDER_ID', '0')
    }

    return config

def get_box_headers(config):
    """Get Box API headers."""
    token = config.get('access_token') or config.get('developer_token')
    if not token:
        return None
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def get_folder_items(headers, folder_id='0'):
    """Get items in a Box folder."""
    url = f"{BOX_API_BASE}/folders/{folder_id}/items"
    params = {
        'fields': 'id,name,type,path_collection',
        'limit': 1000
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Error accessing folder {folder_id}: {e}")
        if hasattr(e.response, 'text'):
            print(f"     Response: {e.response.text[:200]}")
        return None

def scan_folder_recursive(headers, folder_id, base_path="", all_files=None):
    """Recursively scan Box folder for .docx files."""
    if all_files is None:
        all_files = []

    data = get_folder_items(headers, folder_id)
    if not data or 'entries' not in data:
        return all_files

    for item in data['entries']:
        if item['type'] == 'file' and item['name'].endswith('.docx'):
            # Skip files in Course Export
            if 'Course Export' in base_path:
                continue
            if '-test' in item['name'].lower():
                continue

            rel_path = f"{base_path}/{item['name']}" if base_path else item['name']

            file_info = {
                'relative_path': rel_path,
                'file_id': str(item['id']),
                'box_url': f"https://usu.app.box.com/file/{item['id']}",
                'name': item['name'],
                'notes': ''
            }

            all_files.append(file_info)
            print(f"  ✅ Found: {rel_path} (ID: {item['id']})")

        elif item['type'] == 'folder':
            new_path = f"{base_path}/{item['name']}" if base_path else item['name']
            # Recursively scan subfolder
            scan_folder_recursive(headers, item['id'], new_path, all_files)

    return all_files

def find_folder_by_name(headers, folder_id, target_name):
    """Find a folder by name in current folder."""
    data = get_folder_items(headers, folder_id)
    if not data or 'entries' not in data:
        return None

    for item in data['entries']:
        if item['type'] == 'folder' and item['name'] == target_name:
            return item['id']
    return None

def match_files_to_template(box_files, template_files):
    """Match Box API files to template entries."""
    # Create lookup by filename
    box_lookup = {}
    for bf in box_files:
        filename = Path(bf['relative_path']).name.lower()
        box_lookup[filename] = bf

    # Update template entries
    updated_count = 0
    for template_entry in template_files:
        rel_path = template_entry['relative_path']
        filename = Path(rel_path).name.lower()

        # Try exact filename match
        if filename in box_lookup:
            box_file = box_lookup[filename]
            template_entry['file_id'] = box_file['file_id']
            template_entry['box_url'] = box_file['box_url']
            updated_count += 1
        else:
            # Try partial match
            for box_file in box_files:
                if filename.replace('.docx', '') in box_file['name'].lower() or \
                   box_file['name'].lower() in filename.replace('.docx', ''):
                    template_entry['file_id'] = box_file['file_id']
                    template_entry['box_url'] = box_file['box_url']
                    updated_count += 1
                    break

    return updated_count

def main():
    print("📦 Box REST API File ID Extractor")
    print("=" * 60)

    # Load configuration
    print("\n📖 Loading Box API configuration...")
    config = load_config()

    # Get access token
    token = config.get('access_token') or config.get('developer_token')
    if not token:
        print("\n❌ No Box API access token found!")
        print("\n📝 Setup:")
        print("  1. Get Developer Token from: https://app.box.com/developers/console")
        print("  2. Set environment variable:")
        print("     export BOX_DEVELOPER_TOKEN='your_token_here'")
        print("\n  Or create .box-api-config.json:")
        print('  {')
        print('    "developer_token": "your_token_here",')
        print('    "folder_id": "0"  // or specific folder ID')
        print('  }')
        return

    headers = get_box_headers(config)
    if not headers:
        print("❌ Could not create API headers")
        return

    # Test connection
    print("\n🔗 Testing Box API connection...")
    try:
        response = requests.get(f"{BOX_API_BASE}/users/me", headers=headers)
        response.raise_for_status()
        user_info = response.json()
        print(f"✅ Connected as: {user_info.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Failed to connect to Box API: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Status: {e.response.status_code}")
            print(f"   Response: {e.response.text[:200]}")
        return

    # Find the course folder
    print("\n🔍 Finding course folder...")
    folder_id = config.get('folder_id', '0')

    # Try to navigate to the course folder
    target_path = ["WebAIM Shared", "5 Online Courses", "Winter 25-25 Course Update"]
    current_folder_id = folder_id

    for folder_name in target_path:
        found_id = find_folder_by_name(headers, current_folder_id, folder_name)
        if found_id:
            print(f"  ✅ Found: {folder_name} (ID: {found_id})")
            current_folder_id = found_id
        else:
            print(f"  ⚠️  Folder '{folder_name}' not found, using folder_id: {current_folder_id}")
            break

    folder_id = current_folder_id

    # Scan for .docx files
    print(f"\n📂 Scanning folder for .docx files...")
    box_files = scan_folder_recursive(headers, folder_id)

    if not box_files:
        print("❌ No .docx files found in Box folder")
        print("\n💡 Tip: Set BOX_FOLDER_ID to the specific course folder ID")
        return

    print(f"\n✅ Found {len(box_files)} .docx files in Box")

    # Load template
    if not TEMPLATE_FILE_IDS.exists():
        print("❌ Template file not found. Run add-box-office-links.py first.")
        return

    with open(TEMPLATE_FILE_IDS, 'r') as f:
        template = json.load(f)

    template_files = template.get('files', [])
    print(f"📋 Template has {len(template_files)} files")

    # Match files
    print("\n🔗 Matching Box files to template...")
    updated_count = match_files_to_template(box_files, template_files)

    print(f"✅ Matched {updated_count}/{len(template_files)} files")

    # Save updated file IDs
    if 'instructions' in template:
        del template['instructions']

    with open(FILE_IDS_JSON, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"\n💾 Saved to: {FILE_IDS_JSON}")
    print(f"   Files with IDs: {updated_count}/{len(template_files)}")

    if updated_count > 0:
        print("\n📝 Next step: Run 'python3 add-box-office-links.py' to update the mapping")
    else:
        print("\n⚠️  No files matched. Check folder path and file names.")

if __name__ == "__main__":
    main()

