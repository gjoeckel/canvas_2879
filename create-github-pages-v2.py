#!/usr/bin/env python3
"""
Create GitHub Pages HTML site from DOCX-HTML-MAPPING.md with new format:
Page Name: canvas | view docx | edit docx
"""

import re
import json
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup

COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
MAPPING_FILE = COURSE_DIR / "DOCX-HTML-MAPPING.md"
BOX_FILE_IDS_JSON = COURSE_DIR / "box-file-ids.json"
OUTPUT_FILE = COURSE_DIR / "docs" / "index.html"
HTML_DIR = COURSE_DIR / "WINTER 25-26 COURSE UPDATES"

def get_box_file_url(file_id):
    """Get Box file URL (not Office Online)."""
    if file_id:
        return f"https://usu.app.box.com/file/{file_id}"
    return None

def get_box_office_link(file_id):
    """Get Box Office Online link."""
    if file_id:
        return f"https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={file_id}&sharedAccessCode="
    return None

def extract_canvas_url_from_html(html_file_path):
    """Extract Canvas URL from HTML file."""
    if not html_file_path.exists():
        return None
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        original_link = soup.find('div', class_='original-link')
        if original_link:
            a_tag = original_link.find('a')
            if a_tag and 'href' in a_tag.attrs:
                return a_tag['href']
    except Exception as e:
        print(f"  ⚠️  Error reading {html_file_path}: {e}")
    return None

def find_html_file_for_section(section_title, module_title=None):
    """Find the HTML file for a given section."""
    # Normalize section title for matching
    section_normalized = section_title.lower().replace(' ', '-').replace('&', '').replace(':', '')
    
    # Try to find matching HTML file
    if module_title and "Start Here" in module_title:
        base_dir = HTML_DIR / "1 Start Here"
    elif module_title and "Module 1" in module_title:
        base_dir = HTML_DIR / "2 Module 1_ Document Content"
    elif module_title and "Module 2" in module_title:
        base_dir = HTML_DIR / "3 Module 2_ Document Structure"
    elif module_title and "Module 3" in module_title:
        base_dir = HTML_DIR / "4 Module 3_ Evaluating Accessibility & Creating PDFs"
    elif module_title and "Module 4" in module_title:
        base_dir = HTML_DIR / "5 Module 4_ Optimizing PDFs in Acrobat"
    elif module_title and "Module 5" in module_title:
        base_dir = HTML_DIR / "7 Module 5_ Accessible Excel"
    else:
        # Search all directories
        base_dir = HTML_DIR
    
    if not base_dir.exists():
        return None
    
    # Look for HTML files matching the section
    for html_file in base_dir.glob("*.html"):
        if html_file.stem.lower().replace(' ', '-').replace('_', '-').replace('&', '').replace(':', '') == section_normalized:
            return html_file
        # Also try matching with "Section" prefix
        if f"section-{section_normalized}" in html_file.stem.lower().replace(' ', '-').replace('_', '-'):
            return html_file
    
    return None

def load_box_file_ids():
    """Load Box file IDs from JSON."""
    if BOX_FILE_IDS_JSON.exists():
        with open(BOX_FILE_IDS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {item['relative_path']: item for item in data['files']}
    return {}

def find_box_file_for_title(title, box_files, section_path_hint=None):
    """Find Box file ID for a given title."""
    title_normalized = title.lower().replace(' ', '-').replace('&', '').replace(':', '').replace(',', '')
    
    # Try exact match first
    for path, file_info in box_files.items():
        filename = Path(path).stem.lower().replace(' ', '-').replace('_', '-')
        if filename == title_normalized:
            return file_info['file_id'], file_info.get('box_url', f"https://usu.app.box.com/file/{file_info['file_id']}")
    
    # Try partial match
    for path, file_info in box_files.items():
        filename = Path(path).stem.lower()
        if title_normalized in filename or filename in title_normalized:
            # Skip example files
            if 'example' in filename:
                continue
            return file_info['file_id'], file_info.get('box_url', f"https://usu.app.box.com/file/{file_info['file_id']}")
    
    return None, None

def format_page_with_links(page_name, canvas_url=None, box_file_id=None, box_url=None):
    """Format a page name with three links."""
    links = []
    
    if canvas_url:
        links.append(f'<a href="{escape(canvas_url)}" target="_blank" rel="noopener noreferrer">canvas</a>')
    else:
        links.append('<span style="color: #999;">canvas</span>')
    
    if box_file_id and box_url:
        links.append(f'<a href="{escape(box_url)}" target="_blank" rel="noopener noreferrer">view docx</a>')
    elif box_file_id:
        box_url = get_box_file_url(box_file_id)
        links.append(f'<a href="{escape(box_url)}" target="_blank" rel="noopener noreferrer">view docx</a>')
    else:
        links.append('<span style="color: #999;">view docx</span>')
    
    if box_file_id:
        edit_url = get_box_office_link(box_file_id)
        links.append(f'<a href="{escape(edit_url)}" target="_blank" rel="noopener noreferrer">edit docx</a>')
    else:
        links.append('<span style="color: #999;">edit docx</span>')
    
    return f'{escape(page_name)}: {" | ".join(links)}'

def main():
    print("📝 Creating GitHub Pages HTML site with new format...")
    
    # Load Box file IDs
    box_files = load_box_file_ids()
    print(f"📖 Loaded {len(box_files)} Box file mappings")
    
    # Create a mapping of page titles to Canvas URLs by scanning HTML files
    canvas_url_map = {}
    if HTML_DIR.exists():
        for html_file in HTML_DIR.rglob("*.html"):
            canvas_url = extract_canvas_url_from_html(html_file)
            if canvas_url:
                # Use filename as key (without extension)
                page_key = html_file.stem
                canvas_url_map[page_key] = canvas_url
                # Also try normalized versions
                canvas_url_map[page_key.lower().replace(' ', '-').replace('_', '-')] = canvas_url
    
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping_content = f.read()
    
    html_lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Canvas Course DOCX Editor</title>',
        '    <style>',
        '        body {',
        '            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;',
        '            line-height: 1.6;',
        '            max-width: 1200px;',
        '            margin: 0 auto;',
        '            padding: 20px;',
        '            color: #24292e;',
        '            background-color: #ffffff;',
        '        }',
        '        h1 {',
        '            color: #0366d6;',
        '            border-bottom: 1px solid #eaecef;',
        '            padding-bottom: 10px;',
        '        }',
        '        h2 {',
        '            color: #0366d6;',
        '            margin-top: 30px;',
        '            border-bottom: 1px solid #eaecef;',
        '            padding-bottom: 8px;',
        '        }',
        '        h3 {',
        '            color: #24292e;',
        '            margin-top: 20px;',
        '        }',
        '        h4 {',
        '            color: #586069;',
        '            margin-top: 15px;',
        '            font-size: 1.1em;',
        '        }',
        '        a {',
        '            color: #0366d6;',
        '            text-decoration: none;',
        '        }',
        '        a:hover {',
        '            text-decoration: underline;',
        '        }',
        '        ol, ul {',
        '            margin-left: 20px;',
        '        }',
        '        li {',
        '            margin: 5px 0;',
        '        }',
        '        .note {',
        '            background-color: #fff3cd;',
        '            border: 1px solid #ffc107;',
        '            border-radius: 4px;',
        '            padding: 10px;',
        '            margin: 20px 0;',
        '        }',
        '    </style>',
        '</head>',
        '<body>',
        '    <h1>Canvas Course DOCX Editor</h1>',
        '    <p>This page provides direct links to edit course documents in Microsoft Word Online.</p>',
        '    <div class="note">',
        '        <strong>Note:</strong> All links open in new tabs automatically.',
        '    </div>',
    ]
    
    # Parse the mapping file
    lines = mapping_content.split('\n')
    i = 0
    current_module = None
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip summary section
        if line.startswith('## Summary'):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('---'):
                i += 1
            continue
        
        # H2 headings (modules)
        if line.startswith('## '):
            h2_text = line[3:].strip()
            # Remove markdown links from module title
            h2_text = re.sub(r'\s*-\s*\[([^\]]+)\]\([^)]+\)', '', h2_text)
            html_lines.append(f'    <h2>{escape(h2_text)}</h2>')
            current_module = h2_text
            i += 1
            continue
        
        # H3 headings (sections)
        if line.startswith('### '):
            h3_text = line[4:].strip()
            # Extract section name and links - match everything before " - [" or end of line
            section_match = re.match(r'^(.+?)(?:\s*-\s*\[([^\]]+)\]\(([^)]+)\))?$', h3_text)
            if section_match:
                section_name = section_match.group(1).strip()
                edit_link_url = section_match.group(3) if section_match.group(3) else None
                
                # Extract Box file ID from edit link
                box_file_id = None
                if edit_link_url:
                    match = re.search(r'fileId=(\d+)', edit_link_url)
                    if match:
                        box_file_id = match.group(1)
                
                # Get Box URL
                box_url = None
                if box_file_id:
                    box_url = get_box_file_url(box_file_id)
                
                # Find Canvas URL
                canvas_url = None
                html_file = find_html_file_for_section(section_name, current_module)
                if html_file:
                    canvas_url = extract_canvas_url_from_html(html_file)
                
                # Format with links
                formatted = format_page_with_links(section_name, canvas_url, box_file_id, box_url)
                html_lines.append(f'    <h3>{formatted}</h3>')
            else:
                html_lines.append(f'    <h3>{escape(h3_text)}</h3>')
            i += 1
            continue
        
        # H4 Learning Modules
        if line.startswith('#### Learning Modules'):
            html_lines.append('    <h4>Learning Modules</h4>')
            html_lines.append('    <ol>')
            i += 1
            # Skip blank line if present
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            # Collect numbered list items
            while i < len(lines):
                next_line = lines[i].strip()
                # Match numbered list items with links
                match = re.match(r'(\d+)\.\s+\[([^\]]+)\]\(([^)]+)\)', next_line)
                if match:
                    num, link_text, link_url = match.groups()
                    # Extract Box file ID
                    box_file_id = None
                    box_match = re.search(r'fileId=(\d+)', link_url)
                    if box_match:
                        box_file_id = box_match.group(1)
                    
                    # Get Box URL
                    box_url = None
                    if box_file_id:
                        box_url = get_box_file_url(box_file_id)
                    
                    # Find Canvas URL for learning module
                    canvas_url = None
                    html_file = find_html_file_for_section(link_text, current_module)
                    if html_file:
                        canvas_url = extract_canvas_url_from_html(html_file)
                    
                    # Format with links
                    formatted = format_page_with_links(link_text, canvas_url, box_file_id, box_url)
                    html_lines.append(f'        <li>{formatted}</li>')
                elif next_line.startswith(('---', '##', '###', '*No Learning')):
                    break
                elif next_line == '':
                    if i + 1 < len(lines):
                        peek = lines[i + 1].strip()
                        if peek.startswith(('---', '##', '###', '*No Learning')):
                            break
                i += 1
            html_lines.append('    </ol>')
            continue
        
        # Skip other lines
        if line.startswith('*No Learning') or line == '' or line.startswith('---'):
            i += 1
            continue
        
        i += 1
    
    html_lines.extend([
        '</body>',
        '</html>'
    ])
    
    # Write output
    print(f"💾 Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
    
    print(f"✅ Created GitHub Pages site: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

