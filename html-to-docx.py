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
import requests
import shutil

def extract_user_content(html_file_path, output_dir=None):
    """Extract and clean the user_content div from HTML."""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    user_content = soup.find('div', class_='user_content')

    if not user_content:
        raise ValueError("Could not find .user_content div in HTML file")

    # Clean the content (with image download if output_dir provided)
    cleaned_content = clean_html_content(user_content, output_dir)

    return cleaned_content

def download_image(img_url, output_dir):
    """Download image from URL and return local path."""
    try:
        # Extract filename from URL or use a hash
        filename = img_url.split('/')[-1].split('?')[0]
        if not filename or '.' not in filename:
            # Generate filename from URL hash
            import hashlib
            filename = hashlib.md5(img_url.encode()).hexdigest() + '.jpg'

        local_path = output_dir / filename

        # Download image
        response = requests.get(img_url, stream=True, timeout=10)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

        return local_path
    except Exception as e:
        print(f"  ⚠️  Could not download image {img_url}: {e}")
        return None

def clean_html_content(element, output_dir=None):
    """Clean HTML content for DOCX conversion, preserving formatting and images."""
    # Create a copy to avoid modifying the original
    cleaned = BeautifulSoup(str(element), 'html.parser')

    # Replace iframes with placeholder text
    for iframe in cleaned.find_all('iframe'):
        title = iframe.get('title', 'Video')
        placeholder = cleaned.new_tag('p')
        placeholder.string = f"[Video: {title}]"
        iframe.replace_with(placeholder)

    # Handle images - download and convert to local references
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / 'images'
        images_dir.mkdir(exist_ok=True)

        for img in cleaned.find_all('img'):
            img_src = img.get('src', '')
            if img_src:
                # Convert relative URLs to absolute if needed
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    img_src = 'https://usucourses.instructure.com' + img_src
                elif not img_src.startswith('http'):
                    # Relative path - might need base URL
                    img_src = 'https://usucourses.instructure.com' + img_src

                # Download image
                print(f"  📥 Downloading image: {img_src[:60]}...")
                local_path = download_image(img_src, images_dir)

                if local_path:
                    # Update img src to just the filename (Pandoc will look in same dir as HTML)
                    img['src'] = local_path.name
                    print(f"     ✅ Saved to: {local_path.name}")
                else:
                    # Keep alt text as placeholder
                    alt_text = img.get('alt', 'Image')
                    img.replace_with(f"[Image: {alt_text}]")
            else:
                # No src, use alt text
                alt_text = img.get('alt', 'Image')
                img.replace_with(f"[Image: {alt_text}]")

    # Preserve some formatting - keep structure but clean up Canvas-specific attributes
    for tag in cleaned.find_all(True):
        # Remove Canvas-specific data attributes
        for attr in list(tag.attrs.keys()):
            if attr.startswith('data-'):
                del tag.attrs[attr]

        # Keep class attributes for headings (h1, h2, h3) - Pandoc uses them
        # But remove Canvas-specific classes
        if 'class' in tag.attrs:
            classes = tag.attrs['class']
            # Keep semantic classes, remove Canvas UI classes
            if isinstance(classes, list):
                filtered_classes = [c for c in classes if c not in ['lti-embed', 'inline_disabled', 'screen', 'callout', 'instructions']]
                if filtered_classes:
                    tag.attrs['class'] = filtered_classes
                else:
                    del tag.attrs['class']

        # Preserve some style attributes that affect formatting
        # (Pandoc can handle some CSS)
        if 'style' in tag.attrs:
            style = tag.attrs['style']
            # Keep important formatting styles
            if 'font-weight' in style or 'font-style' in style or 'text-align' in style:
                # Keep it - Pandoc might use it
                pass
            else:
                # Remove layout styles that won't translate
                del tag.attrs['style']

    # Convert <br/> tags to newlines in paragraphs (but keep them for Pandoc)
    # Actually, let Pandoc handle <br/> tags - they work in HTML

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
    
    # Copy images to same directory as temp HTML so Pandoc can find them
    images_dir = output_docx_path.parent / 'images'
    if images_dir.exists():
        import shutil
        for img_file in images_dir.glob('*'):
            if img_file.is_file():
                # Copy to same directory as temp HTML
                dest = temp_html.parent / img_file.name
                if not dest.exists():
                    shutil.copy2(img_file, dest)
                    print(f"  📋 Copied {img_file.name} to temp directory for Pandoc")
    
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(str(html_content))

    # Build Pandoc command with options to preserve formatting
    cmd = [
        'pandoc',
        str(temp_html),
        '-o', str(output_docx_path),
        '--from', 'html',
        '--to', 'docx',
        '--standalone',  # Include header/footer
        '--wrap=none',   # Don't wrap lines
    ]

    # Add reference document if provided
    if reference_doc and Path(reference_doc).exists():
        cmd.extend(['--reference-doc', str(reference_doc)])

    # Run Pandoc from the HTML file's directory so it can find images
    print(f"🔄 Converting HTML to DOCX using Pandoc...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(temp_html.parent))

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

    # Create output directory for images
    output_dir = args.output_docx.parent

    # Extract user_content from HTML
    print(f"📄 Extracting content from: {args.html_file}")
    html_content = extract_user_content(args.html_file, output_dir)
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

