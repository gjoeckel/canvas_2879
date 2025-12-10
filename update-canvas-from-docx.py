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
    """Get Box access token from environment or config.

    Supports:
    - Developer Token (BOX_DEVELOPER_TOKEN env var or config)
    - OAuth 2.0 Access Token (from config file, preferred for better permissions)

    Returns:
        tuple: (access_token, token_type) where token_type is 'oauth2' or 'developer'
    """
    # Try OAuth 2.0 access token first (better permissions)
    config_file = COURSE_DIR / ".box-api-config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            # Check for OAuth 2.0 access token
            oauth2 = config.get('oauth2', {})
            if oauth2.get('access_token'):
                return oauth2['access_token'], 'oauth2'
            # Fallback to developer token
            if config.get('developer_token'):
                return config.get('developer_token'), 'developer'

    # Try environment variable
    token = os.getenv('BOX_DEVELOPER_TOKEN')
    if token:
        return token, 'developer'

    return None, None

def download_docx_from_box(file_id, access_token):
    """Download DOCX file from Box."""
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # First, try to get file info to check permissions
    info_url = f'{BOX_API_BASE}/files/{file_id}'
    info_response = requests.get(info_url, headers=headers)
    info_response.raise_for_status()
    file_info = info_response.json()

    # Try to get download URL from file info
    download_url = None
    if 'shared_link' in file_info and file_info['shared_link']:
        # If file has a shared link, try using it
        shared_link = file_info['shared_link']
        if shared_link.get('download_url'):
            download_url = shared_link['download_url']

    # Try direct content download first
    content_url = f'{BOX_API_BASE}/files/{file_id}/content'
    try:
        response = requests.get(content_url, headers=headers, stream=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            # If 403, try using download_url if available
            if download_url:
                # Download from shared link (may need to handle authentication differently)
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                return response.content
            else:
                # Try alternative: get a temporary download URL
                download_url_endpoint = f'{BOX_API_BASE}/files/{file_id}?fields=download_url'
                download_response = requests.get(download_url_endpoint, headers=headers)
                if download_response.status_code == 200:
                    download_data = download_response.json()
                    if 'download_url' in download_data:
                        response = requests.get(download_data['download_url'], stream=True)
                        response.raise_for_status()
                        return response.content

                # If all else fails, raise the original error
                raise Exception(f"403 Forbidden: Token does not have permission to download file content. "
                              f"You may need to grant 'Read all files and folders' permission to your Box app, "
                              f"or use a token with higher permissions.")
        else:
            raise

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

        def get_context_around_element(elem, root, namespaces, context_length=100):
            """Get text context before and after an element to help locate it in HTML."""
            # Find parent paragraph by searching up the tree
            parent_p = None
            current = elem
            for _ in range(10):  # Limit search depth
                if current is None:
                    break
                if current.tag == f'{{{namespaces["w"]}}}p':
                    parent_p = current
                    break
                current = current.getparent() if hasattr(current, 'getparent') else None
                # Alternative: search for parent in tree
                if current is None:
                    # Search for paragraph containing this element
                    for p in root.findall('.//w:p', namespaces):
                        if elem in p.iter():
                            parent_p = p
                            break
                    break

            if parent_p is None:
                return None, None

            # Get text before the insertion in the same paragraph
            before_text = ""
            for sibling in list(parent_p):
                if sibling == elem:
                    break
                # Extract text from runs (w:r) and other text-containing elements
                if sibling.tag == f'{{{namespaces["w"]}}}r':
                    for t in sibling.findall('.//w:t', namespaces):
                        if t.text:
                            before_text += t.text
                elif sibling.tag == f'{{{namespaces["w"]}}}ins':
                    # Skip other insertions, but could include their text for context
                    continue
                # Also check for text in other elements
                for t in sibling.findall('.//w:t', namespaces):
                    if t.text:
                        before_text += t.text

            # Get text after the insertion in the same paragraph
            after_text = ""
            found_elem = False
            for sibling in list(parent_p):
                if sibling == elem:
                    found_elem = True
                    continue
                if found_elem:
                    if sibling.tag == f'{{{namespaces["w"]}}}r':
                        for t in sibling.findall('.//w:t', namespaces):
                            if t.text:
                                after_text += t.text
                    elif sibling.tag == f'{{{namespaces["w"]}}}ins':
                        # Skip other insertions
                        continue
                    # Extract text from any text elements
                    for t in sibling.findall('.//w:t', namespaces):
                        if t.text:
                            after_text += t.text
                    if after_text:
                        break  # Stop after getting some context

            # Limit context length and clean up
            before_text = before_text.strip()
            if len(before_text) > context_length:
                before_text = '...' + before_text[-context_length:]

            after_text = after_text.strip()
            if len(after_text) > context_length:
                after_text = after_text[:context_length] + '...'

            return before_text, after_text

        # Find all insertions (w:ins)
        ins_elements = root.findall('.//w:ins', namespaces)
        print(f"  📝 Found {len(ins_elements)} w:ins (insertion) elements in XML")

        for ins in ins_elements:
            text = extract_text_from_element(ins)
            if text.strip():
                # Get context to help locate insertion point in HTML
                before_context, after_context = get_context_around_element(ins, root, namespaces)

                changes['insertions'].append({
                    'text': text,
                    'author': ins.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', 'Unknown'),
                    'date': ins.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', ''),
                    'before_context': before_context,  # Text that comes before this insertion
                    'after_context': after_context      # Text that comes after this insertion
                })

        # Find all deletions (w:del)
        del_elements = root.findall('.//w:del', namespaces)
        print(f"  🗑️  Found {len(del_elements)} w:del (deletion) elements in XML")

        for dele in del_elements:
            text = extract_text_from_element(dele)
            if text.strip():
                changes['deletions'].append({
                    'text': text,
                    'author': dele.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', 'Unknown'),
                    'date': dele.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '')
                })

        # Additional debugging: Check for any revision-related elements
        if len(ins_elements) == 0 and len(del_elements) == 0:
            print("  ℹ️  No tracked changes found. This could mean:")
            print("     - Track Changes is not enabled in Word")
            print("     - The document has no edits with tracking enabled")
            print("     - All changes have been accepted/rejected")

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
    # Try to match context to insert at the correct location
    for insertion in changes['insertions']:
        new_text = insertion['text'].strip()
        if not new_text:
            continue

        # Create a new paragraph for the insertion
        new_p = soup.new_tag('p')
        new_p.string = new_text

        # Try to find insertion point using context
        insertion_point = None
        before_context = insertion.get('before_context', '').strip()
        after_context = insertion.get('after_context', '').strip()

        if before_context or after_context:
            # Search for elements containing the context text
            for element in user_content.find_all(['p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                element_text = element.get_text().strip()

                # Try to find element that contains the "after" context
                # This means the insertion should go BEFORE this element
                if after_context and after_context.lower() in element_text.lower():
                    # Check if before_context also matches (for more precision)
                    if before_context:
                        # Look for the element that comes before this one
                        prev_elem = element.find_previous_sibling(['p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        if prev_elem and before_context.lower() in prev_elem.get_text().lower():
                            insertion_point = element
                            break
                    else:
                        insertion_point = element
                        break

                # Alternative: find element containing "before" context
                # Insertion should go AFTER this element
                elif before_context and before_context.lower() in element_text.lower():
                    insertion_point = element
                    break

        # Insert at the found location, or fallback to end
        if insertion_point:
            print(f"  📍 Found insertion point using context: '{before_context[:30]}...' -> '{after_context[:30]}...'")
            insertion_point.insert_before(new_p)
        else:
            # Fallback: Find the last element inside user_content to append after
            # This ensures the new paragraph is INSIDE user_content, not outside
            direct_children = [child for child in user_content.children if hasattr(child, 'name') and child.name]
            if direct_children:
                # Find the deepest last child
                last_child = direct_children[-1]
                while last_child.children:
                    last_children = [c for c in last_child.children if hasattr(c, 'name') and c.name]
                    if last_children:
                        last_child = last_children[-1]
                    else:
                        break
                last_child.insert_after(new_p)
            else:
                # Final fallback: append directly to user_content
                user_content.append(new_p)
            print(f"  📍 No context match found, appending to end of user_content")

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
        box_token, token_type = get_box_access_token()
        if not box_token:
            raise ValueError("Box access token not found. Set BOX_DEVELOPER_TOKEN environment variable or configure OAuth 2.0 in .box-api-config.json.")

        if token_type == 'oauth2':
            print(f"✅ Using OAuth 2.0 access token (better permissions)")
        else:
            print(f"⚠️  Using Developer Token (may have limited permissions)")

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

