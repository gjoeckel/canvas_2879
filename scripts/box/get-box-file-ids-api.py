#!/usr/bin/env python3
"""
Get Box file IDs using Box API and update box-file-ids.json

This script:
1. Connects to Box API (using developer token or OAuth)
2. Scans the course folder structure
3. Matches .docx files by name/path
4. Extracts file IDs
5. Updates box-file-ids.json
"""

import json
import os
import sys
from pathlib import Path

# Try to import boxsdk - add venv to path if needed
canvas_grab_venv_site = "/Users/a00288946/Projects/canvas_grab/venv/lib/python3.9/site-packages"
if os.path.exists(canvas_grab_venv_site) and canvas_grab_venv_site not in sys.path:
    sys.path.insert(0, canvas_grab_venv_site)

try:
    from boxsdk import Client, OAuth2
    from boxsdk.exception import BoxOAuthException
except ImportError:
    # Try box_sdk_gen (newer Box SDK)
    try:
        from box_sdk_gen import Client, OAuth2
        # box_sdk_gen uses different exception structure
        BoxOAuthException = Exception
    except ImportError:
        print("❌ boxsdk/box_sdk_gen not found in current Python environment")
        print(f"\n💡 Install boxsdk:")
        print(f"   pip install boxsdk")
        print(f"\n   Or use the wrapper script:")
        print(f"   ./run-box-api.sh")
        sys.exit(1)

BOX_DIR = Path("/Users/a00288946/Library/CloudStorage/Box-Box/WebAIM Shared/5 Online Courses/Winter 25-25 Course Update")
CANVAS_DIR = Path("/Users/a00288946/Projects/canvas_2879")
FILE_IDS_JSON = CANVAS_DIR / "box-file-ids.json"
TEMPLATE_FILE_IDS = CANVAS_DIR / "box-file-ids-template.json"
CONFIG_FILE = CANVAS_DIR / ".box-api-config.json"

def load_config():
    """Load Box API configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)

    # Try environment variables
    config = {
        'developer_token': os.getenv('BOX_DEVELOPER_TOKEN'),
        'client_id': os.getenv('BOX_CLIENT_ID'),
        'client_secret': os.getenv('BOX_CLIENT_SECRET'),
        'access_token': os.getenv('BOX_ACCESS_TOKEN'),
        'refresh_token': os.getenv('BOX_REFRESH_TOKEN'),
        'folder_id': os.getenv('BOX_FOLDER_ID', '0')  # '0' is root, or provide specific folder ID
    }

    return config

def create_client(config):
    """Create Box API client from configuration."""
    if config.get('developer_token'):
        # Use developer token (quick testing)
        auth = OAuth2(
            client_id='',
            client_secret='',
            access_token=config['developer_token']
        )
        print("✅ Using developer token authentication")
    elif config.get('access_token'):
        # Use OAuth2 tokens
        auth = OAuth2(
            client_id=config.get('client_id', ''),
            client_secret=config.get('client_secret', ''),
            access_token=config['access_token'],
            refresh_token=config.get('refresh_token')
        )
        print("✅ Using OAuth2 authentication")
    else:
        raise Exception("No valid credentials found. Set BOX_DEVELOPER_TOKEN or configure OAuth2.")

    return Client(auth)

def find_folder_by_path(client, folder_id, target_path_parts):
    """Find a Box folder by path."""
    if not target_path_parts:
        return client.folder(folder_id).get()

    current_folder = client.folder(folder_id).get()

    for part in target_path_parts:
        found = False
        for item in current_folder.get_items():
            if item.type == 'folder' and item.name == part:
                current_folder = item
                found = True
                break
        if not found:
            raise Exception(f"Folder not found: {'/'.join(target_path_parts)}")

    return current_folder

def scan_folder_for_docx(client, folder_id, base_path=""):
    """Recursively scan Box folder for .docx files."""
    files = []

    try:
        folder = client.folder(folder_id).get()

        for item in folder.get_items():
            if item.type == 'file' and item.name.endswith('.docx'):
                # Skip files in Course Export
                if 'Course Export' in base_path:
                    continue
                if '-test' in item.name.lower():
                    continue

                rel_path = f"{base_path}/{item.name}" if base_path else item.name

                file_info = {
                    'relative_path': rel_path,
                    'file_id': str(item.id),
                    'box_url': f"https://usu.app.box.com/file/{item.id}",
                    'name': item.name,
                    'notes': ''
                }

                files.append(file_info)
                print(f"  ✅ Found: {rel_path} (ID: {item.id})")

            elif item.type == 'folder':
                new_path = f"{base_path}/{item.name}" if base_path else item.name
                # Recursively scan subfolder
                subfolder_files = scan_folder_for_docx(client, item.id, new_path)
                files.extend(subfolder_files)

    except Exception as e:
        print(f"  ⚠️  Error scanning folder {folder_id}: {e}")

    return files

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
    print("📦 Box API File ID Extractor")
    print("=" * 60)

    # Load configuration
    print("\n📖 Loading Box API configuration...")
    config = load_config()

    if not config.get('developer_token') and not config.get('access_token'):
        print("\n❌ No Box API credentials found!")
        print("\n📝 Setup options:")
        print("\nOption 1: Developer Token (Quick)")
        print("  1. Go to https://app.box.com/developers/console")
        print("  2. Create/select app → Get Developer Token")
        print("  3. Set environment variable:")
        print("     export BOX_DEVELOPER_TOKEN='your_token_here'")
        print("\nOption 2: Create config file")
        print(f"  Create {CONFIG_FILE} with:")
        print('  {')
        print('    "developer_token": "your_token_here",')
        print('    "folder_id": "0"  // or specific folder ID')
        print('  }')
        print("\nOption 3: OAuth2 (Production)")
        print("  Set: BOX_CLIENT_ID, BOX_CLIENT_SECRET, BOX_ACCESS_TOKEN")
        return

    # Create Box client
    try:
        client = create_client(config)
        # Test connection
        user = client.user().get()
        print(f"✅ Connected as: {user.name}")
    except Exception as e:
        print(f"❌ Failed to connect to Box: {e}")
        return

    # Find the course folder
    print("\n🔍 Finding course folder...")
    folder_id = config.get('folder_id', '0')

    # Try to find folder by path
    target_path = "WebAIM Shared/5 Online Courses/Winter 25-25 Course Update"
    try:
        folder = find_folder_by_path(client, folder_id, target_path.split('/'))
        print(f"✅ Found folder: {folder.name} (ID: {folder.id})")
        folder_id = folder.id
    except Exception as e:
        print(f"⚠️  Could not find folder by path, using folder_id: {folder_id}")
        print(f"   Error: {e}")
        print("\n💡 Tip: Set BOX_FOLDER_ID to the specific folder ID")
        # Try to search for it
        try:
            search_results = client.search().query(
                query="Winter 25-25 Course Update",
                limit=10,
                result_type='folder'
            )
            for result in search_results:
                if 'Winter 25-25' in result.name:
                    print(f"   Found: {result.name} (ID: {result.id})")
                    folder_id = result.id
                    break
        except:
            pass

    # Scan for .docx files
    print(f"\n📂 Scanning folder for .docx files...")
    box_files = scan_folder_for_docx(client, folder_id)

    if not box_files:
        print("❌ No .docx files found in Box folder")
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
