#!/usr/bin/env python3
"""
Add Box Office Online links to DOCX-HTML-MAPPING.md

This script:
1. Reads box-file-ids.json (file path -> file ID mapping)
2. Generates Office Online URLs for each .docx file
3. Updates DOCX-HTML-MAPPING.md with the links
"""

import json
import os
import re
from pathlib import Path

BOX_DIR = Path("/Users/a00288946/Library/CloudStorage/Box-Box/WebAIM Shared/5 Online Courses/Winter 25-25 Course Update")
CANVAS_DIR = Path("/Users/a00288946/Projects/canvas_2879")
MAPPING_FILE = CANVAS_DIR / "DOCX-HTML-MAPPING.md"
FILE_IDS_JSON = CANVAS_DIR / "box-file-ids.json"
TEMPLATE_FILE_IDS = CANVAS_DIR / "box-file-ids-template.json"

def generate_office_online_url(file_id):
    """Generate Box Office Online URL from file ID."""
    if not file_id:
        return None
    return f"https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={file_id}&sharedAccessCode="

def get_file_id_from_url(url):
    """Extract file ID from Box file URL."""
    # Pattern: https://usu.app.box.com/file/2071047961795
    match = re.search(r'/file/(\d+)', url)
    if match:
        return match.group(1)
    return None

def load_file_ids():
    """Load file ID mapping from JSON file."""
    if FILE_IDS_JSON.exists():
        with open(FILE_IDS_JSON, 'r') as f:
            return json.load(f)
    return {}

def create_file_id_template():
    """Create a template JSON file for collecting file IDs."""
    # Find all .docx files
    docx_files = []
    for docx_path in BOX_DIR.rglob("*.docx"):
        if "Course Export" in str(docx_path):
            continue
        if "-test" in docx_path.name.lower():
            continue

        relative_path = docx_path.relative_to(BOX_DIR)
        docx_files.append({
            'relative_path': str(relative_path),
            'file_id': None,
            'box_url': None,
            'notes': ''
        })

    template = {
        'instructions': [
            '1. For each .docx file, open it in Box web interface',
            '2. Copy the file ID from the URL (e.g., https://usu.app.box.com/file/2071047961795)',
            '3. Enter the file ID in the "file_id" field',
            '4. Optionally add the full Box URL in "box_url" field',
            '5. Save this file as "box-file-ids.json"'
        ],
        'files': sorted(docx_files, key=lambda x: x['relative_path'])
    }

    with open(TEMPLATE_FILE_IDS, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"✅ Created template: {TEMPLATE_FILE_IDS}")
    print(f"   Total files to process: {len(docx_files)}")
    return template

def update_mapping_file(file_ids):
    """Update DOCX-HTML-MAPPING.md with Office Online links."""
    if not MAPPING_FILE.exists():
        print(f"❌ Mapping file not found: {MAPPING_FILE}")
        return False

    # Read current mapping
    with open(MAPPING_FILE, 'r') as f:
        content = f.read()

    # Parse existing matches from JSON (easier than parsing markdown)
    json_mapping = CANVAS_DIR / "docx-html-mapping.json"
    if json_mapping.exists():
        with open(json_mapping, 'r') as f:
            mapping_data = json.load(f)
    else:
        print("❌ JSON mapping file not found. Run create-docx-html-mapping.py first.")
        return False

    # Create file ID lookup
    file_id_lookup = {}
    for file_info in file_ids.get('files', []):
        rel_path = file_info.get('relative_path')
        file_id = file_info.get('file_id')
        if rel_path and file_id:
            file_id_lookup[rel_path] = file_id

    # Update matches with links
    updated_matches = []
    for match in mapping_data['matches']:
        docx_rel = match['docx']['relative_path']
        file_id = file_id_lookup.get(docx_rel)
        office_url = generate_office_online_url(file_id)

        match_with_link = match.copy()
        match_with_link['box_file_id'] = file_id
        match_with_link['box_office_online_url'] = office_url
        updated_matches.append(match_with_link)

    # Rebuild the markdown file
    new_content = []
    lines = content.split('\n')
    in_table = False
    table_started = False

    for i, line in enumerate(lines):
        # Check if we're in the matched files table
        if '## Matched Files' in line:
            in_table = True
            new_content.append(line)
            new_content.append('')
            # Update table header
            new_content.append('| .docx File (Box) | HTML File (GitHub) | Match Type | Box Office Online Link |')
            new_content.append('|------------------|---------------------|------------|------------------------|')
            table_started = True
            continue

        if in_table and table_started:
            # Skip old table rows
            if line.startswith('|') and 'docx File' not in line and '---' not in line:
                continue
            # Stop at end of table
            if line.startswith('---') and table_started:
                # Add updated table rows
                for match in updated_matches:
                    docx_rel = match['docx']['relative_path']
                    html_rel = match['html']['relative_path']
                    match_type = match['match_type']
                    office_url = match.get('box_office_online_url', '')

                    if office_url:
                        link_text = f"[Open in Word Online]({office_url})"
                    else:
                        link_text = "*File ID needed*"

                    new_content.append(f"| `{docx_rel}` | `{html_rel}` | {match_type} | {link_text} |")

                new_content.append('')
                in_table = False
                table_started = False
                new_content.append(line)
                continue

        # Add unmatched .docx section with links
        if '## Unmatched .docx Files' in line:
            new_content.append(line)
            new_content.append('')
            new_content.append('These .docx files in Box don\'t have a corresponding HTML file:\n')

            for docx_info in mapping_data.get('unmatched_docx', []):
                docx_rel = docx_info['relative_path']
                file_id = file_id_lookup.get(docx_rel)
                office_url = generate_office_online_url(file_id)

                if office_url:
                    new_content.append(f"- `{docx_rel}` - [Open in Word Online]({office_url})")
                else:
                    new_content.append(f"- `{docx_rel}` - *File ID needed*")

            new_content.append('')
            continue

        # Skip old unmatched .docx list
        if in_table == False and 'These .docx files in Box don\'t have' in line:
            # Skip until we hit the next section
            continue

        new_content.append(line)

    # Write updated content
    with open(MAPPING_FILE, 'w') as f:
        f.write('\n'.join(new_content))

    # Count files with links
    files_with_links = sum(1 for m in updated_matches if m.get('box_office_online_url'))
    print(f"✅ Updated {MAPPING_FILE}")
    print(f"   Files with Office Online links: {files_with_links}/{len(updated_matches)}")

    return True

def main():
    print("🔗 Box Office Online Link Generator")
    print("=" * 50)

    # Check if file IDs JSON exists
    if not FILE_IDS_JSON.exists():
        print(f"\n⚠️  File ID mapping not found: {FILE_IDS_JSON}")
        print("Creating template file...")
        create_file_id_template()
        print("\n📝 Next steps:")
        print("   1. Open each .docx file in Box web interface")
        print("   2. Copy the file ID from the URL")
        print("   3. Fill in box-file-ids.json with the file IDs")
        print("   4. Run this script again to update the mapping")
        return

    # Load file IDs
    print(f"\n📖 Loading file IDs from: {FILE_IDS_JSON}")
    file_ids = load_file_ids()

    if not file_ids or 'files' not in file_ids:
        print("❌ Invalid file ID structure. Please check box-file-ids.json")
        return

    # Count files with IDs
    files_with_ids = sum(1 for f in file_ids['files'] if f.get('file_id'))
    total_files = len(file_ids['files'])
    print(f"   Files with IDs: {files_with_ids}/{total_files}")

    # Update mapping file
    print(f"\n📝 Updating mapping file: {MAPPING_FILE}")
    if update_mapping_file(file_ids):
        print("\n✅ Complete!")
    else:
        print("\n❌ Failed to update mapping file")

if __name__ == "__main__":
    main()

