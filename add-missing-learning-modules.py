#!/usr/bin/env python3
"""
Add Learning Modules to sections that are missing them.
Excludes DOCX files with "example" in the filename.
"""

import json
import re
from pathlib import Path

COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
MAPPING_FILE = COURSE_DIR / "DOCX-HTML-MAPPING.md"
BOX_FILE_IDS_JSON = COURSE_DIR / "box-file-ids.json"

def get_box_office_link(file_id):
    """Generates a Box Office Online link."""
    if file_id:
        return f"https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={file_id}&sharedAccessCode="
    return None

def load_box_file_ids():
    """Loads Box file IDs from the JSON file."""
    if BOX_FILE_IDS_JSON.exists():
        with open(BOX_FILE_IDS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {item['relative_path']: item['file_id'] for item in data['files'] 
                if 'example' not in item['relative_path'].lower()}
    return {}

def find_matching_docx_files(box_file_ids, section_path_pattern):
    """Find DOCX files matching a section path pattern, excluding examples."""
    matches = []
    for docx_path, file_id in box_file_ids.items():
        if section_path_pattern in docx_path.lower():
            # Extract filename without path
            filename = Path(docx_path).name
            # Skip if it's the section document itself (starts with "section-")
            if filename.startswith('section-') or filename.startswith('module-'):
                continue
            matches.append((filename.replace('.docx', '').replace('-', ' ').title(), file_id, docx_path))
    return matches

def main():
    print("📝 Adding Learning Modules to sections missing them...")
    
    box_file_ids = load_box_file_ids()
    print(f"📖 Loaded {len(box_file_ids)} Box file mappings (excluding examples)")
    
    # Read the mapping file
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Define sections that need Learning Modules and their matching patterns
    section_updates = {
        # Module 1, Section 4: Contrast & Color Reliance
        "### 4  Contrast & Color Reliance": {
            "pattern": "module 1/section 4 contrast",
            "files": [
                ("Contrast Part 1", "2071058307624"),
                ("Contrast Part 2", "2071050450474"),
                ("Color Reliance", "2071059095632"),
            ]
        },
        # Module 2, Section 3: Lists & Columns
        "### 3  Lists & Columns": {
            "pattern": "module 2/section 3 lists",
            "files": [
                ("Lists", "2071060682150"),
                ("Columns", "2071060732439"),
            ]
        },
        # Module 5, Section 1: Navigating in Excel
        "### 1  Navigating in Excel": {
            "pattern": "module 5/section 1 navigating",
            "files": [
                ("Navigating in Excel", "2071058456462"),
            ]
        },
        # Module 5, Section 2: Sheets & Tables
        "### 2  Sheets & Tables": {
            "pattern": "module 5/section 2 sheets",
            "files": [
                ("Sheets & Tables", "2071054772518"),
            ]
        },
        # Module 5, Section 3: Images & Links
        "### 3  Images & Links": {
            "pattern": "module 5/section 3 images",
            "files": [
                ("Images & Links", "2071055435167"),
            ]
        },
        # Module 5, Section 5: Optimizing Workbooks
        "### 5  Optimizing Workbooks": {
            "pattern": "module 5/section 5 optimizing",
            "files": [
                ("Optimizing Workbooks", "2071057410242"),
            ]
        },
        # Module 5, Section 6: Evaluating Accessibility in Excel
        "### 6  Evaluating Accessibility in Excel": {
            "pattern": "module 5/section 6 evaluating",
            "files": [
                ("Evaluating Accessibility in Excel", "2071060861274"),
            ]
        },
    }
    
    output_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this is a section that needs Learning Modules
        section_found = None
        for section_header, update_info in section_updates.items():
            if stripped.startswith(section_header):
                section_found = (section_header, update_info)
                break
        
        if section_found:
            section_header, update_info = section_found
            output_lines.append(line)  # Add the section header
            i += 1
            
            # Skip the "Edit Section Document" line if present
            if i < len(lines) and 'Edit Section Document' in lines[i]:
                output_lines.append(lines[i])
                i += 1
            
            # Skip blank line
            if i < len(lines) and lines[i].strip() == '':
                output_lines.append(lines[i])
                i += 1
            
            # Check if "*No Learning Activities found in HTML*" is present
            if i < len(lines) and '*No Learning Activities found in HTML*' in lines[i]:
                # Replace with Learning Modules
                output_lines.append("\n#### Learning Modules\n\n")
                for idx, (title, file_id) in enumerate(update_info['files'], 1):
                    link = get_box_office_link(file_id)
                    output_lines.append(f"{idx}. [{title}]({link})\n")
                output_lines.append("\n")
                i += 1  # Skip the "*No Learning Activities found in HTML*" line
            else:
                # If Learning Modules already exist, keep them
                while i < len(lines) and not lines[i].strip().startswith(('---', '##', '###')):
                    output_lines.append(lines[i])
                    i += 1
                continue
        else:
            output_lines.append(line)
            i += 1
    
    # Write the updated file
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"✅ Updated {MAPPING_FILE}")
    print(f"   Added Learning Modules to {len(section_updates)} sections")

if __name__ == "__main__":
    main()

