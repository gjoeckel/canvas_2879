#!/usr/bin/env python3
"""
Convert Canvas HTML page to DOCX file using Pandoc.

This creates a DOCX file that structurally matches the HTML,
improving mapping accuracy for tracked changes.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re

def extract_user_content(html_file_path):
    """Extract and clean the user_content div from HTML."""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    user_content = soup.find('div', class_='user_content')

    if not user_content:
        raise ValueError("Could not find .user_content div in HTML file")

    # Clean the content
    cleaned_content = clean_html_content(user_content)

    return cleaned_content

def clean_html_content(element):
    """Clean HTML content for DOCX conversion."""
    # Create a copy to avoid modifying the original
    cleaned = BeautifulSoup(str(element), 'html.parser')

    # Replace iframes with placeholder text
    for iframe in cleaned.find_all('iframe'):
        title = iframe.get('title', 'Video')
        placeholder = cleaned.new_tag('p')
        placeholder.string = f"[Video: {title}]"
        iframe.replace_with(placeholder)

    # Remove Canvas-specific classes that won't translate to DOCX
    # (Keep the structure, just remove class attributes)
    for tag in cleaned.find_all(True):
        # Remove class attributes (they won't translate to DOCX anyway)
        if 'class' in tag.attrs:
            del tag.attrs['class']
        # Remove style attributes (we'll use Word's default styling)
        if 'style' in tag.attrs:
            del tag.attrs['style']
        # Remove data attributes
        for attr in list(tag.attrs.keys()):
            if attr.startswith('data-'):
                del tag.attrs[attr]

    # Convert <br/> tags to newlines in paragraphs
    for br in cleaned.find_all('br'):
        br.replace_with('\n')

    return cleaned

def convert_html_to_docx(html_content, output_docx_path, reference_doc=None):
    """Convert HTML content to DOCX using Pandoc."""
    # Check if Pandoc is installed
    try:
        result = subprocess.run(['pandoc', '--version'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError("Pandoc not found")
    except FileNotFoundError:
        print("❌ Error: Pandoc is not installed.")
        print("   Install with: brew install pandoc")
        print("   Or download from: https://pandoc.org/installing.html")
        sys.exit(1)

    # Write HTML to temporary file
    temp_html = output_docx_path.parent / f"{output_docx_path.stem}.temp.html"
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(str(html_content))

    # Build Pandoc command
    cmd = [
        'pandoc',
        str(temp_html),
        '-o', str(output_docx_path),
        '--from', 'html',
        '--to', 'docx',
    ]

    # Add reference document if provided
    if reference_doc and Path(reference_doc).exists():
        cmd.extend(['--reference-doc', str(reference_doc)])

    # Run Pandoc
    print(f"🔄 Converting HTML to DOCX using Pandoc...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Clean up temp file
    temp_html.unlink()

    if result.returncode != 0:
        print(f"❌ Pandoc conversion failed:")
        print(result.stderr)
        sys.exit(1)

    print(f"✅ DOCX file created: {output_docx_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Convert Canvas HTML page to DOCX file'
    )
    parser.add_argument(
        '--html-file',
        type=Path,
        required=True,
        help='Path to Canvas HTML file'
    )
    parser.add_argument(
        '--output-docx',
        type=Path,
        help='Output DOCX file path (default: same directory as HTML with .docx extension)'
    )
    parser.add_argument(
        '--reference-doc',
        type=Path,
        help='Optional: Reference DOCX template for styling'
    )

    args = parser.parse_args()

    # Set default output path if not provided
    if not args.output_docx:
        args.output_docx = args.html_file.parent / f"{args.html_file.stem}.docx"

    # Extract user_content from HTML
    print(f"📄 Extracting content from: {args.html_file}")
    html_content = extract_user_content(args.html_file)
    print(f"✅ Extracted user_content div")

    # Convert to DOCX
    convert_html_to_docx(html_content, args.output_docx, args.reference_doc)

    print(f"\n📋 Next steps:")
    print(f"   1. Open {args.output_docx} in Word")
    print(f"   2. Review and adjust formatting if needed")
    print(f"   3. Upload to Box (replace existing DOCX)")
    print(f"   4. Run create-docx-html-mapping.py to create new mapping")
    print(f"   5. Test with a tracked change")

if __name__ == '__main__':
    main()

