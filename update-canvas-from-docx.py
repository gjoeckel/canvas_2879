#!/usr/bin/env python3
"""
Update Canvas page from DOCX tracked changes.

This script:
1. Downloads DOCX file from Box
2. Extracts tracked changes (insertions and deletions)
3. Updates local HTML file
4. Pushes changes to Canvas via API
5. Returns success message with timestamp
"""

import os
import sys
import json
import zipfile
import io
import re
from pathlib import Path
from datetime import datetime
from html import escape
from xml.etree import ElementTree as ET
import requests
import toml
from bs4 import BeautifulSoup

# Add canvas_grab to path
sys.path.insert(0, '/Users/a00288946/Projects/canvas_grab')

from canvasapi import Canvas

# Configuration
COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
CONFIG_FILE = COURSE_DIR / "config.toml"
HTML_DIR = COURSE_DIR / "WINTER 25-26 COURSE UPDATES"
BOX_API_BASE = "https://api.box.com/2.0"

# Box file ID for Course Orientation
COURSE_ORIENTATION_BOX_FILE_ID = "2071049022878"
COURSE_ORIENTATION_CANVAS_PAGE_SLUG = "course-orientation"
COURSE_ORIENTATION_HTML_FILE = HTML_DIR / "1 Start Here" / "Course Orientation.html"

def load_config():
    """Load configuration from config.toml."""
    with open(CONFIG_FILE, 'r') as f:
        return toml.load(f)

def get_box_access_token():
    """Get Box access token from environment or config."""
    token = os.getenv('BOX_DEVELOPER_TOKEN')
    if not token:
        # Try config file
        config_file = COURSE_DIR / ".box-api-config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                token = config.get('developer_token')
    return token

def download_docx_from_box(file_id, access_token):
    """Download DOCX file from Box."""
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    url = f'{BOX_API_BASE}/files/{file_id}/content'
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    return response.content

def extract_tracked_changes_from_docx(docx_content):
    """Extract tracked changes (insertions and deletions) from DOCX file."""
    changes = {
        'insertions': [],
        'deletions': []
    }

    # DOCX is a ZIP file
    with zipfile.ZipFile(io.BytesIO(docx_content)) as docx:
        # Extract main document XML
        document_xml = docx.read('word/document.xml')
        root = ET.fromstring(document_xml)

        # Define namespaces
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        def extract_text_from_element(elem):
            """Extract all text from an element and its children."""
            texts = []
            for t_elem in elem.findall('.//w:t', namespaces):
                if t_elem.text:
                    texts.append(t_elem.text)
            return ' '.join(texts)

        # Find all insertions (w:ins)
        for ins in root.findall('.//w:ins', namespaces):
            text = extract_text_from_element(ins)
            if text.strip():
                changes['insertions'].append({
                    'text': text,
                    'author': ins.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', 'Unknown'),
                    'date': ins.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '')
                })

        # Find all deletions (w:del)
        for dele in root.findall('.//w:del', namespaces):
            text = extract_text_from_element(dele)
            if text.strip():
                changes['deletions'].append({
                    'text': text,
                    'author': dele.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', 'Unknown'),
                    'date': dele.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '')
                })

    return changes

def update_html_with_changes(html_file_path, changes):
    """Update HTML file based on tracked changes.

    - Strikethrough text is deleted
    - New text is added
    """
    if not html_file_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file_path}")

    # Read HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    user_content = soup.find('div', class_='user_content')

    if not user_content:
        raise ValueError("Could not find .user_content div in HTML file")

    # Apply deletions: Remove text that matches deleted content
    # Look for exact text matches in paragraphs and other elements
    for deletion in changes['deletions']:
        deleted_text = deletion['text'].strip()
        if not deleted_text:
            continue
        
        # Find all text nodes and check if they contain the deleted text
        for element in user_content.find_all(['p', 'li', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if element.string and deleted_text in element.string:
                # Replace the deleted text with empty string
                element.string = element.string.replace(deleted_text, '')
            elif element.get_text() and deleted_text in element.get_text():
                # For elements with nested tags, replace in all text nodes
                for text_node in element.find_all(string=True):
                    if deleted_text in text_node:
                        text_node.replace_with(text_node.replace(deleted_text, ''))
    
    # Apply insertions: Add new text as paragraphs
    # In a more sophisticated implementation, we'd try to match context and insert at the right location
    for insertion in changes['insertions']:
        new_text = insertion['text'].strip()
        if not new_text:
            continue
        
        # Create a new paragraph for the insertion
        new_p = soup.new_tag('p')
        new_p.string = new_text
        # Append to the end of user_content
        user_content.append(new_p)

    # Write updated HTML
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    return True

def push_to_canvas(html_file_path, canvas_page_slug, config):
    """Push updated HTML content to Canvas."""
    # Initialize Canvas API
    canvas_url = config['endpoint']['endpoint']
    canvas_token = config['endpoint']['api_key']
    course_id = config['course_filter']['per_filter']['course_id'][0]

    canvas = Canvas(canvas_url, canvas_token)
    course = canvas.get_course(course_id)

    # Get the page
    page = course.get_page(canvas_page_slug)

    # Read updated HTML content
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract body content from HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    user_content_div = soup.find('div', class_='user_content')

    if not user_content_div:
        raise ValueError("Could not find .user_content div in updated HTML")

    # Get the HTML content of user_content
    body_content = str(user_content_div)

    # Update the page
    page.edit(wiki_page={'body': body_content})

    return True

def main():
    """Main function to update Canvas from DOCX tracked changes."""
    import argparse

    parser = argparse.ArgumentParser(description='Update Canvas page from DOCX tracked changes')
    parser.add_argument('--box-file-id', type=str, default=COURSE_ORIENTATION_BOX_FILE_ID,
                       help='Box file ID')
    parser.add_argument('--canvas-page-slug', type=str, default=COURSE_ORIENTATION_CANVAS_PAGE_SLUG,
                       help='Canvas page URL slug')
    parser.add_argument('--html-file', type=str, default=str(COURSE_ORIENTATION_HTML_FILE),
                       help='Path to local HTML file')
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config()

        # Get Box access token
        box_token = get_box_access_token()
        if not box_token:
            raise ValueError("Box access token not found. Set BOX_DEVELOPER_TOKEN environment variable.")

        print("📥 Downloading DOCX from Box...")
        docx_content = download_docx_from_box(args.box_file_id, box_token)

        print("🔍 Extracting tracked changes...")
        changes = extract_tracked_changes_from_docx(docx_content)

        print(f"   Found {len(changes['insertions'])} insertions and {len(changes['deletions'])} deletions")

        if not changes['insertions'] and not changes['deletions']:
            print("ℹ️  No tracked changes found in DOCX file.")
            return {
                'success': True,
                'message': 'No tracked changes found in DOCX file.',
                'timestamp': datetime.now().isoformat()
            }

        print("📝 Updating local HTML file...")
        html_file_path = Path(args.html_file)
        update_html_with_changes(html_file_path, changes)

        print("🚀 Pushing changes to Canvas...")
        push_to_canvas(html_file_path, args.canvas_page_slug, config)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f'Canvas page updated successfully at {timestamp}. Applied {len(changes["insertions"])} insertions and {len(changes["deletions"])} deletions.'

        print(f"✅ {message}")

        return {
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'changes': {
                'insertions': len(changes['insertions']),
                'deletions': len(changes['deletions'])
            }
        }

    except Exception as e:
        error_message = f'Failed to update Canvas: {str(e)}'
        print(f"❌ {error_message}")
        return {
            'success': False,
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    result = main()
    print(json.dumps(result, indent=2))

