#!/usr/bin/env python3
"""
Create a mapping between .docx files in Box and HTML files in canvas_2879 project.
"""

import os
from pathlib import Path
import re

BOX_DIR = Path("/Users/a00288946/Library/CloudStorage/Box-Box/WebAIM Shared/5 Online Courses/Winter 25-25 Course Update")
CANVAS_DIR = Path("/Users/a00288946/Projects/canvas_2879")

def normalize_name(name):
    """Normalize a filename for comparison."""
    # Remove extension
    name = name.replace('.docx', '').replace('.html', '')
    # Convert to lowercase
    name = name.lower()
    # Replace underscores and hyphens with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    # Remove "and" variations
    name = name.replace(' & ', ' and ')
    # Remove extra spaces
    name = ' '.join(name.split())
    return name

def extract_base_name(path):
    """Extract a meaningful base name from a path."""
    name = path.stem
    # Remove common prefixes/suffixes
    name = re.sub(r'^section-\d+-', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^module-\d+-', '', name, flags=re.IGNORECASE)
    return name

def find_docx_files(base_dir):
    """Find all .docx files in Box directory."""
    docx_files = []
    for docx_path in base_dir.rglob("*.docx"):
        # Skip files in Annotation Options/Course Export (those are exports, not source)
        if "Course Export" in str(docx_path):
            continue
        # Skip test files
        if "-test" in docx_path.name.lower():
            continue

        relative_path = docx_path.relative_to(base_dir)
        docx_files.append({
            'path': docx_path,
            'relative_path': str(relative_path),
            'name': docx_path.stem,
            'normalized': normalize_name(docx_path.stem),
            'base_name': extract_base_name(docx_path)
        })
    return sorted(docx_files, key=lambda x: x['relative_path'])

def find_html_files(base_dir):
    """Find all HTML files in canvas_2879 directory."""
    html_files = []
    for html_path in base_dir.rglob("*.html"):
        # Skip files in .git
        if ".git" in str(html_path):
            continue
        # Skip README and other non-course files
        if html_path.name.lower().startswith(('readme', 'custom-css', 'quick')):
            continue

        relative_path = html_path.relative_to(base_dir)
        html_files.append({
            'path': html_path,
            'relative_path': str(relative_path),
            'name': html_path.stem,
            'normalized': normalize_name(html_path.stem),
            'base_name': extract_base_name(html_path)
        })
    return sorted(html_files, key=lambda x: x['relative_path'])

def match_files(docx_files, html_files):
    """Match docx files to HTML files."""
    matches = []
    unmatched_docx = []
    unmatched_html = []

    # Create lookup dictionaries
    html_by_normalized = {h['normalized']: h for h in html_files}
    html_by_base = {h['base_name']: h for h in html_files}

    for docx in docx_files:
        matched = False

        # Try exact normalized match
        if docx['normalized'] in html_by_normalized:
            matches.append({
                'docx': docx,
                'html': html_by_normalized[docx['normalized']],
                'match_type': 'exact_normalized'
            })
            matched = True
        # Try base name match
        elif docx['base_name'] in html_by_base:
            matches.append({
                'docx': docx,
                'html': html_by_base[docx['base_name']],
                'match_type': 'base_name'
            })
            matched = True
        # Try partial match
        else:
            for html in html_files:
                if docx['base_name'] in html['normalized'] or html['base_name'] in docx['normalized']:
                    matches.append({
                        'docx': docx,
                        'html': html,
                        'match_type': 'partial'
                    })
                    matched = True
                    break

        if not matched:
            unmatched_docx.append(docx)

    # Find unmatched HTML files
    matched_html_names = {m['html']['name'] for m in matches}
    unmatched_html = [h for h in html_files if h['name'] not in matched_html_names]

    return matches, unmatched_docx, unmatched_html

def main():
    print("🔍 Finding .docx files in Box...")
    docx_files = find_docx_files(BOX_DIR)
    print(f"   Found {len(docx_files)} .docx files")

    print("\n🔍 Finding HTML files in canvas_2879...")
    html_files = find_html_files(CANVAS_DIR)
    print(f"   Found {len(html_files)} HTML files")

    print("\n🔗 Matching files...")
    matches, unmatched_docx, unmatched_html = match_files(docx_files, html_files)
    print(f"   Matched: {len(matches)}")
    print(f"   Unmatched .docx: {len(unmatched_docx)}")
    print(f"   Unmatched HTML: {len(unmatched_html)}")

    # Create mapping file
    mapping_file = CANVAS_DIR / "DOCX-HTML-MAPPING.md"
    print(f"\n📝 Creating mapping file: {mapping_file}")

    with open(mapping_file, 'w') as f:
        f.write("# DOCX to HTML File Mapping\n\n")
        f.write("This document maps .docx source files in Box to HTML files in the canvas_2879 GitHub repository.\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total .docx files**: {len(docx_files)}\n")
        f.write(f"- **Total HTML files**: {len(html_files)}\n")
        f.write(f"- **Matched pairs**: {len(matches)}\n")
        f.write(f"- **Unmatched .docx files**: {len(unmatched_docx)}\n")
        f.write(f"- **Unmatched HTML files**: {len(unmatched_html)}\n\n")

        f.write("---\n\n")
        f.write("## Matched Files\n\n")
        f.write("| .docx File (Box) | HTML File (GitHub) | Match Type |\n")
        f.write("|------------------|---------------------|------------|\n")

        for match in sorted(matches, key=lambda x: x['docx']['relative_path']):
            docx_rel = match['docx']['relative_path']
            html_rel = match['html']['relative_path']
            match_type = match['match_type']
            f.write(f"| `{docx_rel}` | `{html_rel}` | {match_type} |\n")

        if unmatched_docx:
            f.write("\n---\n\n")
            f.write("## Unmatched .docx Files\n\n")
            f.write("These .docx files in Box don't have a corresponding HTML file:\n\n")
            for docx in unmatched_docx:
                f.write(f"- `{docx['relative_path']}`\n")

        if unmatched_html:
            f.write("\n---\n\n")
            f.write("## Unmatched HTML Files\n\n")
            f.write("These HTML files don't have a corresponding .docx file:\n\n")
            for html in unmatched_html:
                f.write(f"- `{html['relative_path']}`\n")

        f.write("\n---\n\n")
        f.write("## Notes\n\n")
        f.write("- Match types:\n")
        f.write("  - `exact_normalized`: Exact match after normalization\n")
        f.write("  - `base_name`: Match based on base name (removed prefixes)\n")
        f.write("  - `partial`: Partial match (one name contains the other)\n")
        f.write("\n- Box directory: `/Users/a00288946/Library/CloudStorage/Box-Box/WebAIM Shared/5 Online Courses/Winter 25-25 Course Update`\n")
        f.write("- GitHub directory: `/Users/a00288946/Projects/canvas_2879`\n")

    print(f"✅ Mapping file created: {mapping_file}")

    # Also create a JSON mapping for programmatic use
    import json
    json_file = CANVAS_DIR / "docx-html-mapping.json"
    mapping_data = {
        'matches': [
            {
                'docx': {
                    'path': str(m['docx']['path']),
                    'relative_path': m['docx']['relative_path'],
                    'name': m['docx']['name']
                },
                'html': {
                    'path': str(m['html']['path']),
                    'relative_path': m['html']['relative_path'],
                    'name': m['html']['name']
                },
                'match_type': m['match_type']
            }
            for m in matches
        ],
        'unmatched_docx': [
            {
                'path': str(d['path']),
                'relative_path': d['relative_path'],
                'name': d['name']
            }
            for d in unmatched_docx
        ],
        'unmatched_html': [
            {
                'path': str(h['path']),
                'relative_path': h['relative_path'],
                'name': h['name']
            }
            for h in unmatched_html
        ]
    }

    with open(json_file, 'w') as f:
        json.dump(mapping_data, f, indent=2)

    print(f"✅ JSON mapping file created: {json_file}")

if __name__ == "__main__":
    main()

