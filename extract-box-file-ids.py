#!/usr/bin/env python3
"""
Helper script to extract Box file IDs from URLs and update box-file-ids.json

Usage:
1. Copy Box file URLs (one per line) into a text file
2. Run: python3 extract-box-file-ids.py < urls.txt
3. Or paste URLs directly when prompted
"""

import json
import sys
import re
from pathlib import Path

CANVAS_DIR = Path("/Users/a00288946/Projects/canvas_2879")
FILE_IDS_JSON = CANVAS_DIR / "box-file-ids.json"
TEMPLATE_FILE_IDS = CANVAS_DIR / "box-file-ids-template.json"

def extract_file_id_from_url(url):
    """Extract file ID from Box URL."""
    # Pattern: https://usu.app.box.com/file/2071047961795
    # Or: https://usu.app.box.com/file/2071047961795/view
    match = re.search(r'/file/(\d+)', url)
    if match:
        return match.group(1)
    return None

def extract_file_name_from_url(url):
    """Try to extract file name from Box URL or metadata."""
    # Box URLs sometimes have the filename
    # Pattern: https://usu.app.box.com/file/2071047961795/view/.../filename.docx
    match = re.search(r'/([^/]+\.docx)', url)
    if match:
        return match.group(1)
    return None

def load_file_ids():
    """Load existing file ID mapping."""
    if FILE_IDS_JSON.exists():
        with open(FILE_IDS_JSON, 'r') as f:
            return json.load(f)
    elif TEMPLATE_FILE_IDS.exists():
        with open(TEMPLATE_FILE_IDS, 'r') as f:
            return json.load(f)
    return {'files': []}

def find_file_by_name(files, filename):
    """Find file entry by filename."""
    for f in files:
        if filename.lower() in f['relative_path'].lower():
            return f
    return None

def main():
    print("📋 Box File ID Extractor")
    print("=" * 50)
    print("\nPaste Box file URLs (one per line). Press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done.\n")

    # Read URLs from stdin or prompt
    urls = []
    if not sys.stdin.isatty():
        # Reading from pipe/file
        urls = [line.strip() for line in sys.stdin if line.strip()]
    else:
        # Interactive input
        print("Paste URLs (one per line, empty line to finish):")
        while True:
            try:
                line = input()
                if not line.strip():
                    break
                urls.append(line.strip())
            except EOFError:
                break

    if not urls:
        print("❌ No URLs provided")
        return

    print(f"\n📖 Processing {len(urls)} URLs...")

    # Load existing file IDs
    file_ids_data = load_file_ids()
    files = file_ids_data.get('files', [])

    # Create lookup by filename
    file_lookup = {}
    for f in files:
        filename = Path(f['relative_path']).name.lower()
        file_lookup[filename] = f

    # Process URLs
    updated_count = 0
    new_count = 0

    for url in urls:
        file_id = extract_file_id_from_url(url)
        if not file_id:
            print(f"⚠️  Could not extract file ID from: {url}")
            continue

        filename = extract_file_name_from_url(url)
        if filename:
            filename = filename.lower()
            if filename in file_lookup:
                file_entry = file_lookup[filename]
                if not file_entry.get('file_id'):
                    file_entry['file_id'] = file_id
                    file_entry['box_url'] = url
                    updated_count += 1
                    print(f"✅ Updated: {file_entry['relative_path']} -> {file_id}")
            else:
                # Try to find by partial match
                found = False
                for f in files:
                    if filename.replace('.docx', '') in f['relative_path'].lower():
                        if not f.get('file_id'):
                            f['file_id'] = file_id
                            f['box_url'] = url
                            updated_count += 1
                            print(f"✅ Updated (partial match): {f['relative_path']} -> {file_id}")
                            found = True
                            break
                if not found:
                    print(f"⚠️  Could not find file entry for: {filename}")
        else:
            # No filename in URL, just add as note
            print(f"ℹ️  Extracted ID {file_id} but couldn't match to file (URL: {url})")

    # Save updated file IDs
    if updated_count > 0:
        # Remove template instructions if present
        if 'instructions' in file_ids_data:
            del file_ids_data['instructions']

        with open(FILE_IDS_JSON, 'w') as f:
            json.dump(file_ids_data, f, indent=2)

        print(f"\n✅ Updated {updated_count} file entries")
        print(f"   Saved to: {FILE_IDS_JSON}")
        print(f"\n📝 Next step: Run 'python3 add-box-office-links.py' to update the mapping")
    else:
        print("\n⚠️  No files were updated. Make sure the filenames match.")

if __name__ == "__main__":
    main()

