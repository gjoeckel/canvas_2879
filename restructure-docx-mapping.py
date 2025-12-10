#!/usr/bin/env python3
"""
Restructure DOCX-HTML-MAPPING.md into hierarchical format with H2/H3 headings
and ordered lists of Learning Modules based on HTML Learning Activities sections.
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from html import unescape

COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
BOX_FILE_IDS_JSON = COURSE_DIR / "box-file-ids.json"
OUTPUT_FILE = COURSE_DIR / "DOCX-HTML-MAPPING.md"
HTML_BASE_DIR = COURSE_DIR / "WINTER 25-26 COURSE UPDATES"

# Module structure mapping
MODULE_STRUCTURE = {
    "1 Start Here": {
        "sections": ["Course Details", "Course Orientation", "Terms of Use"],
        "module_docx": None  # No module-level docx for Start Here
    },
    "2 Module 1_ Document Content": {
        "sections": [
            "Section 1_ Overview of Document Accessibility",
            "Section 2_ Images",
            "Section 3_ Hyperlinks",
            "Section 4_ Contrast & Color Reliance",
            "Section 5_ Optimizing Writing"
        ],
        "module_docx": "module-1-document-content.docx"
    },
    "3 Module 2_ Document Structure": {
        "sections": [
            "Section 1_ Headings in Word",
            "Section 2_ Optimizing PowerPoint Presentations",
            "Section 3_ Lists & Columns",
            "Section 4_ Tables"
        ],
        "module_docx": "module-2-document-structure.docx"
    },
    "4 Module 3_ Evaluating Accessibility & Creating PDFs": {
        "sections": [
            "Section 1_ Evaluating Accessibility",
            "Section 2_ Practicing Evaluation & Repair",
            "Section 3_ Creating PDFs"
        ],
        "module_docx": "module-3-evaluating-accessibility-and-creating-pdfs.docx"
    },
    "5 Module 4_ Optimizing PDFs in Acrobat": {
        "sections": [
            "Section 1_ Introduction To Optimizing PDFs",
            "Section 2_ Checking Accessibility",
            "Section 3_ Reading Order Tool",
            "Section 4_ Content Order and Tags Order"
        ],
        "module_docx": "module-4-optimizing-pdfs-in-acrobat.docx"
    },
    "7 Module 5_ Accessible Excel": {
        "sections": [
            "Section 1_ Navigating in Excel",
            "Section 2_ Sheets & Tables",
            "Section 3_ Images & Links",
            "Section 4_ Charts",
            "Section 5_ Optimizing Workbooks",
            "Section 6_ Evaluating Accessibility in Excel"
        ],
        "module_docx": "module-5-accessible-excel.docx"
    }
}

def load_box_file_ids():
    """Load Box file IDs from JSON."""
    with open(BOX_FILE_IDS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create lookup dictionaries
    file_id_map = {}  # filename -> file_id
    path_to_id = {}   # relative_path -> file_id

    for file_info in data.get('files', []):
        filename = Path(file_info['relative_path']).name.lower()
        file_id_map[filename] = file_info['file_id']
        path_to_id[file_info['relative_path']] = file_info['file_id']

    return file_id_map, path_to_id

def get_box_office_online_url(file_id):
    """Generate Box Office Online URL from file ID."""
    return f"https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={file_id}&sharedAccessCode="

def normalize_filename(name):
    """Normalize filename for matching."""
    return re.sub(r'[^a-z0-9]+', '', name.lower())

def find_docx_by_title(title, file_id_map, path_to_id):
    """Find DOCX file ID by matching title to filename."""
    # Normalize title - remove common prefixes and clean up
    title_clean = re.sub(r'^(Overview of|Images:|Creating|Adding|Optimizing|Practicing|Evaluating|Filename|Plain|Readability|Legible|The|Modifying|Tables|Creating Accessible Charts|Mac Users|Introduction to|Checking|Reading Order|Content Order|Navigating|Sheets|Optimizing Workbooks)\s+', '', title, flags=re.IGNORECASE)
    normalized_title = normalize_filename(title_clean)

    # Also try with original title
    normalized_title_orig = normalize_filename(title)

    best_match = None
    best_score = 0

    for path, file_id in path_to_id.items():
        filename = Path(path).name.lower()
        normalized_filename = normalize_filename(Path(path).stem)

        score = 0

        # Exact match gets highest score
        if normalized_title == normalized_filename or normalized_title_orig == normalized_filename:
            score = 100
        # One contains the other
        elif normalized_title in normalized_filename or normalized_filename in normalized_title:
            score = 50
        elif normalized_title_orig in normalized_filename or normalized_filename in normalized_title_orig:
            score = 40
        # Partial match on significant words
        elif len(normalized_title) > 5 and len(normalized_filename) > 5:
            # Check first 10 chars
            if normalized_title[:10] in normalized_filename or normalized_filename[:10] in normalized_title:
                score = 20
            # Check if key words match
            title_words = set(normalized_title.split())
            filename_words = set(normalized_filename.split())
            common_words = title_words & filename_words
            if len(common_words) > 0 and len(common_words) >= len(title_words) * 0.5:
                score = 15

        if score > best_score:
            best_score = score
            best_match = file_id

    return best_match

def extract_learning_activities(html_file_path):
    """Extract Learning Activities links from HTML file."""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Find Learning Activities section
        learning_activities = []

        # Try h2 tags first
        h2_tags = soup.find_all('h2')
        for h2 in h2_tags:
            if h2.get_text().strip() == 'Learning Activities':
                # Find the next ul after this h2 (could be sibling or in next div)
                next_ul = h2.find_next_sibling('ul')

                # If not found as sibling, check if h2 is in a div and ul is next sibling of that div
                if not next_ul:
                    parent = h2.parent
                    if parent and parent.name == 'div':
                        next_ul = parent.find_next_sibling('ul')

                # If still not found, search within the parent div
                if not next_ul:
                    parent = h2.parent
                    if parent:
                        next_ul = parent.find('ul')

                # Last resort: find any ul that comes after this h2
                if not next_ul:
                    for sibling in h2.next_siblings:
                        if hasattr(sibling, 'name') and sibling.name == 'ul':
                            next_ul = sibling
                            break

                if next_ul:
                    for li in next_ul.find_all('li', recursive=False):
                        link = li.find('a')
                        if link:
                            title = link.get('title', '')
                            if not title:
                                # Try to get text from strong tag or link text
                                strong = link.find('strong')
                                if strong:
                                    title = strong.get_text().strip()
                                else:
                                    title = link.get_text().strip()

                            # Clean up title - remove extra info like "| Video (6:02) | Guide"
                            title = re.sub(r'\s*\|\s*.*$', '', title).strip()
                            # Also remove HTML entities and clean up
                            title = unescape(title)
                            learning_activities.append(title)

        # If no h2 found, try p tags
        if not learning_activities:
            p_tags = soup.find_all('p')
            for p in p_tags:
                if 'Learning Activities' in p.get_text():
                    # Find the next ul after this p
                    next_ul = p.find_next_sibling('ul')
                    if not next_ul:
                        # Check if p is in a div and ul is in the next sibling div
                        parent = p.parent
                        if parent and parent.name == 'div':
                            # Check next sibling div
                            next_div = parent.find_next_sibling('div')
                            if next_div:
                                next_ul = next_div.find('ul')
                            # Also check if ul is next sibling of parent div
                            if not next_ul:
                                next_ul = parent.find_next_sibling('ul')

                    if next_ul:
                        for li in next_ul.find_all('li', recursive=False):
                            link = li.find('a')
                            if link:
                                title = link.get('title', '')
                                if not title:
                                    strong = link.find('strong')
                                    if strong:
                                        title = strong.get_text().strip()
                                    else:
                                        title = link.get_text().strip()

                                title = re.sub(r'\s*\|\s*.*$', '', title).strip()
                                title = unescape(title)
                                learning_activities.append(title)
                    break

        return learning_activities
    except Exception as e:
        print(f"  ⚠️  Error reading {html_file_path.name}: {e}")
        return []

def get_module_docx_file_id(module_name, file_id_map, path_to_id):
    """Get file ID for module-level DOCX."""
    module_info = MODULE_STRUCTURE.get(module_name, {})
    module_docx = module_info.get("module_docx")

    if not module_docx:
        return None

    # Search for the module DOCX file
    for path, file_id in path_to_id.items():
        if module_docx.lower() in path.lower():
            return file_id

    return None

def get_section_docx_file_id(section_name, module_name, file_id_map, path_to_id):
    """Get file ID for section-level DOCX."""
    # Extract section number
    section_num_match = re.search(r'Section\s+(\d+)', section_name, re.IGNORECASE)
    section_num = section_num_match.group(1) if section_num_match else None

    # Normalize section name - remove "Section X_" prefix
    section_clean = re.sub(r'^Section\s+\d+[:_]\s*', '', section_name, flags=re.IGNORECASE)
    section_normalized = normalize_filename(section_clean.replace('_', '-'))

    # Determine module number from module_name
    module_num_match = re.search(r'Module\s+(\d+)', module_name, re.IGNORECASE)
    module_num = module_num_match.group(1) if module_num_match else None

    # Search for section DOCX files
    best_match = None
    best_score = 0

    for path, file_id in path_to_id.items():
        path_lower = path.lower()
        path_normalized = normalize_filename(Path(path).stem)

        # Must be a section file (contains "section-" in path)
        if 'section-' not in path_lower:
            continue

        # Exclude learning modules (part-, example, etc.)
        if any(x in path_lower for x in ['part-', 'example', '-examples', 'practice']):
            continue

        # Must match module number if available (check both "module-X" and "Module X" formats)
        if module_num:
            module_pattern1 = f'module-{module_num}'
            module_pattern2 = f'module {module_num}'
            if module_pattern1 not in path_lower and module_pattern2 not in path_lower:
                continue

        # Score the match
        score = 0

        # Highest priority: exact section number match AND section name match
        if section_num and f'section-{section_num}' in path_lower:
            score += 20
            # Check if section name also matches
            if section_normalized in path_normalized or path_normalized in section_normalized:
                score += 30
        # Lower priority: just section name match
        elif section_normalized in path_normalized or path_normalized in section_normalized:
            score += 10

        if score > best_score:
            best_score = score
            best_match = file_id

    return best_match

def main():
    print("📝 Restructuring DOCX-HTML-MAPPING.md...")

    # Load Box file IDs
    print("📖 Loading Box file IDs...")
    file_id_map, path_to_id = load_box_file_ids()
    print(f"   Loaded {len(path_to_id)} file mappings")

    # Build the new structure
    output_lines = [
        "# DOCX to HTML File Mapping",
        "",
        "This document maps .docx source files in Box to HTML files in the canvas_2879 GitHub repository.",
        "",
        "## Summary",
        "",
        "- **Total .docx files**: 100",
        "- **Total HTML files**: 30",
        "- **Matched pairs**: 34",
        "- **Unmatched .docx files**: 66",
        "- **Unmatched HTML files**: 0",
        "",
        "---",
        "",
    ]

    # Process each module
    for module_name, module_info in MODULE_STRUCTURE.items():
        print(f"\n📦 Processing {module_name}...")

        # Get module-level DOCX file ID
        module_file_id = get_module_docx_file_id(module_name, file_id_map, path_to_id)

        # Create H2 heading
        if module_name == "1 Start Here":
            h2_text = "## Start Here"
        else:
            # Extract module number and name
            match = re.match(r'(\d+)\s+Module\s+(\d+)[:_]\s*(.+)', module_name)
            if match:
                dir_num = match.group(1)
                module_num = match.group(2)
                module_title = match.group(3)
                h2_text = f"## Module {module_num}: {module_title}"
            else:
                # Fallback for other formats
                match = re.match(r'(\d+)\s+(.+)', module_name)
                if match:
                    module_num = match.group(1)
                    module_title = match.group(2).replace('Module ', '').replace('_', ' ')
                    h2_text = f"## Module {module_num}: {module_title}"
                else:
                    h2_text = f"## {module_name}"

        # Add link if module DOCX exists
        if module_file_id:
            box_url = get_box_office_online_url(module_file_id)
            output_lines.append(f"{h2_text} - [Edit Module Document]({box_url})")
        else:
            output_lines.append(h2_text)

        output_lines.append("")

        # Process each section
        for section_name in module_info["sections"]:
            print(f"  📄 Processing {section_name}...")

            # Get section HTML file path
            html_file_path = HTML_BASE_DIR / module_name / f"{section_name}.html"

            if not html_file_path.exists():
                print(f"    ⚠️  HTML file not found: {html_file_path}")
                continue

            # Get section-level DOCX file ID
            section_file_id = get_section_docx_file_id(section_name, module_name, file_id_map, path_to_id)

            # Create H3 heading
            h3_text = section_name.replace('_', ' ').replace('Section ', '')
            if section_file_id:
                box_url = get_box_office_online_url(section_file_id)
                output_lines.append(f"### {h3_text} - [Edit Section Document]({box_url})")
            else:
                output_lines.append(f"### {h3_text}")

            output_lines.append("")

            # Extract Learning Activities
            learning_activities = extract_learning_activities(html_file_path)

            if learning_activities:
                output_lines.append("#### Learning Modules")
                output_lines.append("")

                for i, activity_title in enumerate(learning_activities, 1):
                    # Find matching DOCX file
                    activity_file_id = find_docx_by_title(activity_title, file_id_map, path_to_id)

                    if activity_file_id:
                        box_url = get_box_office_online_url(activity_file_id)
                        output_lines.append(f"{i}. [{activity_title}]({box_url})")
                    else:
                        output_lines.append(f"{i}. {activity_title} *(DOCX file not found)*")

                output_lines.append("")
            else:
                output_lines.append("*No Learning Activities found in HTML*")
                output_lines.append("")

        output_lines.append("---")
        output_lines.append("")

    # Write output
    print(f"\n💾 Writing to {OUTPUT_FILE.name}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"✅ Restructured mapping file created: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

