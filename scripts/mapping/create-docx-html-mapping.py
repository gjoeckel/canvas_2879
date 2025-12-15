#!/usr/bin/env python3
"""
Create mapping between DOCX file structure and HTML file structure.

This establishes a baseline mapping that can be used to apply tracked changes
to the correct locations in the HTML file.
"""

import argparse
import json
import zipfile
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
import requests

COURSE_DIR = Path("/Users/a00288946/Projects/canvas_2879")
BOX_API_BASE = "https://api.box.com/2.0"

def get_box_access_token():
    """Get Box access token from config."""
    import os
    config_file = COURSE_DIR / ".box-api-config.json"
    if config_file.exists():
        import json as json_lib
        with open(config_file, 'r') as f:
            config = json_lib.load(f)
            oauth2 = config.get('oauth2', {})
            if oauth2.get('access_token'):
                return oauth2['access_token']
            if config.get('developer_token'):
                return config.get('developer_token')
    return os.getenv('BOX_DEVELOPER_TOKEN')

def download_docx_from_box(file_id, access_token):
    """Download DOCX file from Box."""
    headers = {'Authorization': f'Bearer {access_token}'}
    content_url = f'{BOX_API_BASE}/files/{file_id}/content'
    response = requests.get(content_url, headers=headers, stream=True)
    response.raise_for_status()
    return response.content

def extract_docx_structure(docx_content):
    """Extract paragraph structure from DOCX file."""
    structure = []

    with zipfile.ZipFile(io.BytesIO(docx_content)) as docx:
        document_xml = docx.read('word/document.xml')
        root = ET.fromstring(document_xml)

        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        # Extract all paragraphs with their text and position
        for idx, para in enumerate(root.findall('.//w:p', namespaces)):
            # Extract all text from this paragraph
            texts = []
            for t_elem in para.findall('.//w:t', namespaces):
                if t_elem.text:
                    texts.append(t_elem.text)

            para_text = ' '.join(texts).strip()
            if para_text:  # Only include non-empty paragraphs
                structure.append({
                    'index': idx,
                    'text': para_text,
                    'text_hash': hash(para_text[:100])  # Hash for matching
                })

    return structure

def extract_html_structure(html_file_path):
    """Extract paragraph structure from HTML file."""
    structure = []

    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    user_content = soup.find('div', class_='user_content')

    if not user_content:
        raise ValueError("Could not find .user_content div in HTML file")

    # Extract all text elements (p, div, li, headings) with their text
    for idx, element in enumerate(user_content.find_all(['p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
        element_text = element.get_text().strip()
        if element_text:  # Only include non-empty elements
            structure.append({
                'index': idx,
                'tag': element.name,
                'text': element_text,
                'text_hash': hash(element_text[:100]),  # Hash for matching
                'element_id': f"elem_{idx}"  # For later reference
            })

    return structure, soup, user_content

def normalize_text(text):
    """Normalize text for comparison (remove extra whitespace, lowercase, etc.)."""
    import re
    # Remove extra whitespace, normalize to lowercase
    text = re.sub(r'\s+', ' ', text.lower().strip())
    # Remove HTML entities that might be in HTML but not DOCX
    text = text.replace('&amp;', '&').replace('&nbsp;', ' ')
    return text

def calculate_similarity(text1, text2):
    """Calculate similarity between two texts (0-1)."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    if not norm1 or not norm2:
        return 0.0

    # Exact match
    if norm1 == norm2:
        return 1.0

    # Substring match
    if norm1 in norm2 or norm2 in norm1:
        return 0.8

    # Word overlap
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    if words1 and words2:
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        if total > 0:
            return overlap / total

    return 0.0

def create_mapping(docx_structure, html_structure):
    """Create mapping between DOCX paragraphs and HTML elements."""
    mapping = []

    # Use a more flexible matching algorithm
    # Try to match each DOCX paragraph to the best HTML element

    for docx_para in docx_structure:
        best_match = None
        best_score = 0.0
        best_html_idx = -1

        # Search through HTML elements to find best match
        for html_idx, html_elem in enumerate(html_structure):
            # Skip if already mapped
            if any(m['html_index'] == html_elem['index'] for m in mapping):
                continue

            # Calculate similarity
            score = calculate_similarity(docx_para['text'], html_elem['text'])

            if score > best_score and score >= 0.3:  # Minimum threshold
                best_score = score
                best_match = html_elem
                best_html_idx = html_idx

        # If we found a good match, add it to mapping
        if best_match and best_score >= 0.3:
            mapping.append({
                'docx_index': docx_para['index'],
                'docx_text_preview': docx_para['text'][:100],
                'html_index': best_match['index'],
                'html_tag': best_match['tag'],
                'html_text_preview': best_match['text'][:100],
                'html_element_id': best_match['element_id'],
                'similarity_score': round(best_score, 3)
            })

    return mapping

def main():
    parser = argparse.ArgumentParser(description='Create mapping between DOCX and HTML files')
    parser.add_argument('--box-file-id', required=True, help='Box file ID of the DOCX document')
    parser.add_argument('--html-file', required=True, help='Path to HTML file (relative to COURSE_DIR)')
    parser.add_argument('--output', default=None, help='Output JSON file for mapping (default: html_file.mapping.json)')

    args = parser.parse_args()

    # Get access token
    access_token = get_box_access_token()
    if not access_token:
        raise ValueError("Box access token not found")

    # Download DOCX
    print(f"📥 Downloading DOCX from Box (file_id: {args.box_file_id})...")
    docx_content = download_docx_from_box(args.box_file_id, access_token)
    print("✅ DOCX downloaded")

    # Extract structures
    print("🔍 Extracting DOCX structure...")
    docx_structure = extract_docx_structure(docx_content)
    print(f"   Found {len(docx_structure)} paragraphs in DOCX")

    html_file_path = COURSE_DIR / args.html_file
    print(f"🔍 Extracting HTML structure from {html_file_path}...")
    html_structure, soup, user_content = extract_html_structure(html_file_path)
    print(f"   Found {len(html_structure)} elements in HTML")

    # Create mapping
    print("🗺️  Creating mapping...")
    mapping = create_mapping(docx_structure, html_structure)
    print(f"   Created {len(mapping)} mappings")

    # Save mapping
    output_file = args.output or (html_file_path.parent / f"{html_file_path.stem}.mapping.json")
    mapping_data = {
        'box_file_id': args.box_file_id,
        'html_file': str(args.html_file),
        'docx_structure': docx_structure,
        'html_structure': html_structure,
        'mapping': mapping,
        'created_at': str(Path(__file__).stat().st_mtime)  # Simple timestamp
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, indent=2)

    print(f"✅ Mapping saved to {output_file}")
    print(f"\n📊 Mapping Summary:")
    print(f"   DOCX paragraphs: {len(docx_structure)}")
    print(f"   HTML elements: {len(html_structure)}")
    print(f"   Mapped pairs: {len(mapping)}")
    print(f"   Coverage: {len(mapping)/max(len(docx_structure), len(html_structure))*100:.1f}%")

if __name__ == '__main__':
    main()
