#!/usr/bin/env python3
"""
Update HTML file using DOCX-HTML mapping and tracked changes.

This uses a pre-created mapping to apply tracked changes to the correct
locations in the HTML file.
"""

import json
import zipfile
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup

def load_mapping(mapping_file_path):
    """Load the DOCX-HTML mapping."""
    with open(mapping_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_tracked_changes_with_paragraph_index(docx_content):
    """Extract tracked changes and identify which paragraph they're in."""
    changes = {
        'insertions': [],
        'deletions': []
    }
    
    with zipfile.ZipFile(io.BytesIO(docx_content)) as docx:
        document_xml = docx.read('word/document.xml')
        root = ET.fromstring(document_xml)
        
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
        
        # Get all paragraphs
        all_paragraphs = root.findall('.//w:p', namespaces)
        
        # Find insertions
        ins_elements = root.findall('.//w:ins', namespaces)
        for ins in ins_elements:
            text = extract_text_from_element(ins)
            if text.strip():
                # Find which paragraph contains this insertion
                para_index = None
                for idx, para in enumerate(all_paragraphs):
                    if ins in para.iter():
                        para_index = idx
                        break
                
                changes['insertions'].append({
                    'text': text,
                    'paragraph_index': para_index
                })
        
        # Find deletions
        del_elements = root.findall('.//w:del', namespaces)
        for dele in del_elements:
            text = extract_text_from_element(dele)
            if text.strip():
                # Find which paragraph contains this deletion
                para_index = None
                for idx, para in enumerate(all_paragraphs):
                    if dele in para.iter():
                        para_index = idx
                        break
                
                changes['deletions'].append({
                    'text': text,
                    'paragraph_index': para_index
                })
    
    return changes

def update_html_using_mapping(html_file_path, mapping, changes):
    """Update HTML file using the mapping to locate changes."""
    # Read HTML
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    user_content = soup.find('div', class_='user_content')
    
    if not user_content:
        raise ValueError("Could not find .user_content div in HTML file")
    
    # Create a lookup: paragraph_index -> HTML element
    para_to_html = {}
    for mapping_entry in mapping['mapping']:
        docx_idx = mapping_entry['docx_index']
        html_idx = mapping_entry['html_index']
        # Find the HTML element by index
        html_elements = list(user_content.find_all(['p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        if html_idx < len(html_elements):
            para_to_html[docx_idx] = html_elements[html_idx]
    
    # Apply deletions
    for deletion in changes['deletions']:
        para_idx = deletion.get('paragraph_index')
        deleted_text = deletion['text'].strip()
        
        if para_idx is not None and para_idx in para_to_html:
            html_elem = para_to_html[para_idx]
            # Remove the deleted text from this element
            elem_text = html_elem.get_text()
            if deleted_text in elem_text:
                # Replace the text
                new_text = elem_text.replace(deleted_text, '')
                html_elem.clear()
                html_elem.string = new_text
                print(f"  🗑️  Deleted text from paragraph {para_idx}")
    
    # Apply insertions
    for insertion in changes['insertions']:
        para_idx = insertion.get('paragraph_index')
        new_text = insertion['text'].strip()
        
        if para_idx is not None and para_idx in para_to_html:
            # Insert after the mapped HTML element
            html_elem = para_to_html[para_idx]
            new_p = soup.new_tag('p')
            new_p.string = new_text
            html_elem.insert_after(new_p)
            print(f"  📝 Inserted text after paragraph {para_idx}")
        else:
            # Fallback: append to end of user_content
            new_p = soup.new_tag('p')
            new_p.string = new_text
            # Find last element in user_content
            last_elem = None
            for elem in user_content.find_all(['p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                last_elem = elem
            if last_elem:
                last_elem.insert_after(new_p)
            else:
                user_content.append(new_p)
            print(f"  📝 Inserted text at end (no mapping for paragraph {para_idx})")
    
    # Write updated HTML
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Update HTML using DOCX-HTML mapping')
    parser.add_argument('--mapping-file', required=True, help='Path to mapping JSON file')
    parser.add_argument('--docx-file', required=True, help='Path to DOCX file')
    parser.add_argument('--html-file', required=True, help='Path to HTML file')
    
    args = parser.parse_args()
    
    # Load mapping
    print(f"📖 Loading mapping from {args.mapping_file}...")
    mapping = load_mapping(args.mapping_file)
    
    # Read DOCX
    print(f"📥 Reading DOCX from {args.docx_file}...")
    with open(args.docx_file, 'rb') as f:
        docx_content = f.read()
    
    # Extract tracked changes
    print("🔍 Extracting tracked changes...")
    changes = extract_tracked_changes_with_paragraph_index(docx_content)
    print(f"   Found {len(changes['insertions'])} insertions and {len(changes['deletions'])} deletions")
    
    # Update HTML
    print(f"📝 Updating HTML file {args.html_file}...")
    update_html_using_mapping(args.html_file, mapping, changes)
    print("✅ HTML updated")

if __name__ == '__main__':
    main()

