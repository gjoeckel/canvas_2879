#!/usr/bin/env python3
"""
Map Canvas files to new directory structure and copy them.

This script:
1. Parses GitHub Pages HTML to map page names to module/section/LA
2. Maps existing HTML/DOCX files to their locations
3. Copies files to WINTER-25-26-UPDATES structure
"""

import re
import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import shutil

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import (
    get_project_root,
    get_winter_updates_dir,
    get_winter_archive_dir
)

# Source directories
SOURCE_HTML_DIR = get_winter_archive_dir()
SOURCE_IMAGES_DIR = get_winter_archive_dir() / '365_Update'
GITHUB_PAGES_HTML = get_project_root() / 'github-pages' / 'index.html'

# Target directory
TARGET_DIR = get_winter_updates_dir()

def parse_github_pages_structure():
    """Parse GitHub Pages HTML to extract module/section/LA structure."""
    with open(GITHUB_PAGES_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Structure: {page_name: {'module': X, 'section': Y, 'la': Z, 'level': 'module|section|la'}}
    page_map = {}
    current_module = None
    current_section = None
    la_counter = 0

    # Process Start Here section
    start_here_h2 = soup.find('h2', string='Start Here')
    if start_here_h2:
        ol = start_here_h2.find_next_sibling('ol')
        if ol:
            for li in ol.find_all('li'):
                page_text = li.find('span', class_='page-text')
                if page_text:
                    page_name = page_text.get_text(strip=True)
                    # Extract page number and name (e.g., "1. Course Orientation")
                    match = re.search(r'\d+\.\s*(.+)', page_name)
                    if match:
                        page_name = match.group(1)
                    page_map[page_name] = {
                        'module': None,
                        'section': None,
                        'la': None,
                        'level': 'start-here'
                    }

    # Process modules
    for h2 in soup.find_all('h2'):
        # Get only the page-text span, not the links
        h2_page_text = h2.find('span', class_='page-text')
        if h2_page_text:
            h2_text = h2_page_text.get_text(strip=True)
        else:
            h2_text = h2.get_text(strip=True)
            # If no page-text span, try to get text before any links
            # Remove everything after "view docx" or similar patterns
            h2_text = re.sub(r'\s*view\s+docx.*$', '', h2_text, flags=re.IGNORECASE)

        # Check if it's a module (starts with "Module")
        module_match = re.search(r'Module\s+(\d+):\s*(.+)', h2_text)
        if module_match:
            current_module = int(module_match.group(1))
            current_section = None
            la_counter = 0

            # Module-level page (the module overview)
            module_name = module_match.group(2).strip()
            page_map[module_name] = {
                'module': current_module,
                'section': None,
                'la': None,
                'level': 'module'
            }

        # Process sections (h3) within this module
        if current_module:
            for h3 in h2.find_next_siblings('h3'):
                # Get only the page-text span, not the links
                h3_page_text = h3.find('span', class_='page-text')
                if h3_page_text:
                    section_text = h3_page_text.get_text(strip=True)
                else:
                    section_text = h3.get_text(strip=True)
                    # Remove everything after "view docx" or similar patterns
                    section_text = re.sub(r'\s*view\s+docx.*$', '', section_text, flags=re.IGNORECASE)

                section_match = re.search(r'Section\s+(\d+)\s+(.+)', section_text)
                if section_match:
                    current_section = int(section_match.group(1))
                    la_counter = 0

                    # Section-level page (the section overview)
                    section_name = section_match.group(2).strip()
                    page_map[section_name] = {
                        'module': current_module,
                        'section': current_section,
                        'la': None,
                        'level': 'section'
                    }

                # Process LAs (ordered list items) within this section
                ol = h3.find_next_sibling('ol')
                if ol:
                    for li in ol.find_all('li'):
                        la_counter += 1
                        page_text = li.find('span', class_='page-text')
                        if page_text:
                            page_name = page_text.get_text(strip=True)
                            # Remove numbering if present
                            page_name = re.sub(r'^\d+\.\s*', '', page_name)
                            page_map[page_name] = {
                                'module': current_module,
                                'section': current_section,
                                'la': la_counter,
                                'level': 'la'
                            }

    return page_map

def normalize_filename(name):
    """Convert page name to likely filename format."""
    # Convert to lowercase, replace spaces/special chars with hyphens
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '-', name)
    name = re.sub(r'-+', '-', name)
    return name.strip('-')

def find_matching_files(source_dir, base_name, page_name=None, page_info=None):
    """Find HTML, local HTML, and DOCX files matching a base name."""
    files = {
        'html': None,
        'local_html': None,
        'docx': None
    }

    # Try various filename patterns
    patterns = [
        base_name,
        base_name.replace('-', '_'),
        base_name.replace('_', '-'),
        base_name.replace('-', ' '),
    ]

    # Add module/section specific patterns
    if page_name and page_info:
        level = page_info.get('level', '')
        module_num = page_info.get('module')
        section_num = page_info.get('section')

        # For module pages: "Document Content" -> try "Module 1_ Document Content", "module_1_document_content", etc.
        if level == 'module' and module_num:
            module_patterns = [
                f"Module {module_num}_ {page_name}",
                f"module_{module_num}_{base_name}",
                f"module {module_num} {base_name}",
                f"Module {module_num}_ Document Content",  # Special case for Module 1
            ]
            patterns.extend(module_patterns)

        # For section pages: "Overview of Document Accessibility" -> try "Section 1_ Overview of Document Accessibility"
        if level == 'section' and module_num and section_num:
            section_patterns = [
                f"Section {section_num}_ {page_name}",
                f"section_{section_num}_{base_name}",
                f"section {section_num} {base_name}",
            ]
            patterns.extend(section_patterns)

        # Also try direct patterns from page name
        # "Module 1: Document Content" -> "Module 1_ Document Content"
        module_match = re.search(r'Module\s+(\d+):\s*(.+)', page_name, re.IGNORECASE)
        if module_match:
            module_num = module_match.group(1)
            module_title = module_match.group(2)
            patterns.extend([
                f"Module {module_num}_ {module_title}",
                f"module_{module_num}_{normalize_filename(module_title)}",
            ])

        # "Section 1 Overview of Document Accessibility" -> "Section 1_ Overview of Document Accessibility"
        section_match = re.search(r'Section\s+(\d+)\s+(.+)', page_name, re.IGNORECASE)
        if section_match:
            section_num = section_match.group(1)
            section_title = section_match.group(2)
            patterns.extend([
                f"Section {section_num}_ {section_title}",
                f"section_{section_num}_{normalize_filename(section_title)}",
            ])

    for pattern in patterns:
        # Look for HTML
        html_files = list(source_dir.rglob(f"{pattern}.html"))
        for f in html_files:
            if not f.name.endswith('_local.html'):
                files['html'] = f
                break
        if files['html']:
            break

        # Look for local HTML
        local_html_files = list(source_dir.rglob(f"{pattern}_local.html"))
        if local_html_files:
            files['local_html'] = local_html_files[0]
            break

        # Look for DOCX
        docx_files = list(source_dir.rglob(f"{pattern}.docx"))
        if docx_files:
            files['docx'] = docx_files[0]
            break

    return files

def get_target_path(page_info, file_type):
    """Get target path for a file based on its page info."""
    module = page_info['module']
    section = page_info['section']
    la = page_info['la']
    level = page_info['level']

    if level == 'start-here':
        return TARGET_DIR / "Start-Here"
    elif level == 'module':
        return TARGET_DIR / f"Module-{module}"
    elif level == 'section':
        return TARGET_DIR / f"Module-{module}" / f"Section-{module}-{section}"
    elif level == 'la':
        return TARGET_DIR / f"Module-{module}" / f"Section-{module}-{section}" / f"LA-{module}-{section}-{la}"

    return None

def fix_css_paths_in_html(html_file, project_root=None):
    """Fix CSS paths in HTML file to be relative to its location."""
    if not html_file or not html_file.exists():
        return False

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠️  Could not read {html_file}: {e}")
        return False

    soup = BeautifulSoup(content, 'html.parser')
    html_dir = html_file.parent.resolve()

    # Find project root (where CSS files are)
    if project_root is None:
        project_root = html_file.resolve()
        while project_root.parent != project_root:
            css_files = list(project_root.glob('*.css'))
            if css_files:
                break
            project_root = project_root.parent

    project_root = Path(project_root).resolve()

    # Calculate relative path from HTML file directory to project root
    try:
        css_rel_path = os.path.relpath(project_root, html_dir)
        if css_rel_path == '.':
            css_rel_path = ''
        else:
            css_rel_path = css_rel_path.replace('\\', '/') + '/'
    except ValueError:
        # Fallback: calculate based on depth from data/current/WINTER-25-26-UPDATES
        winter_dir = get_winter_updates_dir()
        try:
            depth = len(html_dir.parts) - len(winter_dir.parts)
            css_rel_path = '../' * (depth + 3)  # +3 for data/current/WINTER-25-26-UPDATES -> project root
        except:
            css_rel_path = '../' * 5  # Safe fallback

    updated = False
    # Update all CSS link hrefs
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href', '')
        # Skip external URLs
        if href.startswith('http://') or href.startswith('https://'):
            continue

        # Update relative CSS paths
        if href.startswith('../') or (not href.startswith('/') and not href.startswith('http')):
            css_filename = Path(href).name
            new_href = f"{css_rel_path}{css_filename}"
            if href != new_href:
                link['href'] = new_href
                updated = True

    if updated:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    return False

def copy_file(source_file, target_dir, file_type):
    """Copy a file to target directory."""
    if source_file and source_file.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / source_file.name
        shutil.copy2(source_file, target_file)

        # If it's a local HTML file, fix CSS paths
        if file_type == 'local_html' and target_file.suffix == '.html':
            fix_css_paths_in_html(target_file)

        return target_file
    return None

def find_images_for_html(html_file, source_images_dir):
    """Find images referenced in HTML file."""
    if not html_file or not html_file.exists():
        return []

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        images = []
        found_ids = set()  # Avoid duplicates

        for img in soup.find_all('img'):
            src = img.get('src', '')
            # Extract Canvas ID from src
            # Can be: "../365_Update/1235852.png", "1235852.png", or Canvas URL with /files/1235852/
            canvas_id = None
            ext = None

            # Try Canvas URL pattern first: /files/1235852/preview
            url_match = re.search(r'/files/(\d+)', src)
            if url_match:
                canvas_id = url_match.group(1)
                # Try to determine extension from URL or default to png
                ext_match = re.search(r'\.(png|jpg|jpeg|gif)', src, re.IGNORECASE)
                if ext_match:
                    ext = ext_match.group(1).lower()
                else:
                    ext = 'png'  # Default
            else:
                # Try local path pattern: "../365_Update/1235852.png" or "1235852.png"
                path_match = re.search(r'(\d+)\.(png|jpg|jpeg|gif)', src, re.IGNORECASE)
                if path_match:
                    canvas_id = path_match.group(1)
                    ext = path_match.group(2).lower()

            if canvas_id and ext:
                # Skip if we already found this image
                if canvas_id in found_ids:
                    continue
                found_ids.add(canvas_id)

                # Look for image file recursively
                image_files = list(source_images_dir.rglob(f"{canvas_id}.{ext}"))
                if image_files:
                    images.append(image_files[0])  # Take first match

        return images
    except Exception as e:
        print(f"  ⚠️  Error reading {html_file}: {e}")
        return []

def main():
    print("📋 Step 1: Parsing GitHub Pages structure...")
    page_map = parse_github_pages_structure()
    print(f"✅ Found {len(page_map)} pages mapped\n")

    print("📋 Step 2: Finding and copying files...")

    copied = defaultdict(int)
    not_found = []

    for page_name, page_info in page_map.items():
        base_name = normalize_filename(page_name)
        target_path = get_target_path(page_info, 'html')

        if not target_path:
            continue

        print(f"\n📄 {page_name}")
        print(f"   Base name: {base_name}")
        print(f"   Target: {target_path.relative_to(TARGET_DIR)}")

        # Find files
        files = find_matching_files(SOURCE_HTML_DIR, base_name, page_name, page_info)

        # Copy HTML
        if files['html']:
            copied_file = copy_file(files['html'], target_path, 'html')
            if copied_file:
                print(f"   ✅ Copied HTML: {files['html'].name}")
                copied['html'] += 1

                # Find and copy images for this HTML
                images = find_images_for_html(files['html'], SOURCE_IMAGES_DIR)
                for img in images:
                    copied_img = copy_file(img, target_path, 'image')
                    if copied_img:
                        print(f"   ✅ Copied image: {img.name}")
                        copied['images'] += 1
        else:
            print(f"   ⚠️  HTML not found: {base_name}.html")
            # Still try to find local HTML and DOCX even if HTML not found
            if not files['local_html'] and not files['docx']:
                not_found.append(page_name)

        # Copy local HTML (try even if HTML not found)
        if files['local_html']:
            copied_file = copy_file(files['local_html'], target_path, 'local_html')
            if copied_file:
                print(f"   ✅ Copied local HTML: {files['local_html'].name}")
                copied['local_html'] += 1
        elif files['html']:
            # If we found HTML but not local HTML, try to find it based on HTML filename
            html_stem = files['html'].stem
            local_html_path = files['html'].parent / f"{html_stem}_local.html"
            if local_html_path.exists():
                copied_file = copy_file(local_html_path, target_path, 'local_html')
                if copied_file:
                    print(f"   ✅ Copied local HTML: {local_html_path.name}")
                    copied['local_html'] += 1

        # Copy DOCX (try even if HTML not found)
        if files['docx']:
            copied_file = copy_file(files['docx'], target_path, 'docx')
            if copied_file:
                print(f"   ✅ Copied DOCX: {files['docx'].name}")
                copied['docx'] += 1
        elif files['html']:
            # If we found HTML but not DOCX, try to find it based on HTML filename
            html_stem = files['html'].stem
            # Try various DOCX naming patterns
            docx_patterns = [
                files['html'].parent / f"{html_stem}.docx",
                files['html'].parent / f"{html_stem.replace('_', ' ')}.docx",
                files['html'].parent / f"{html_stem.replace(' ', '_')}.docx",
            ]
            for docx_path in docx_patterns:
                if docx_path.exists():
                    copied_file = copy_file(docx_path, target_path, 'docx')
                    if copied_file:
                        print(f"   ✅ Copied DOCX: {docx_path.name}")
                        copied['docx'] += 1
                    break

    # Summary
    print("\n" + "="*60)
    print("📊 Copy Summary")
    print("="*60)
    print(f"HTML files copied: {copied['html']}")
    print(f"Local HTML files copied: {copied['local_html']}")
    print(f"DOCX files copied: {copied['docx']}")
    print(f"Images copied: {copied['images']}")
    print(f"Files not found: {len(not_found)}")

    if not_found:
        print(f"\n⚠️  Files not found:")
        for name in not_found[:10]:  # Show first 10
            print(f"   - {name}")
        if len(not_found) > 10:
            print(f"   ... and {len(not_found) - 10} more")

if __name__ == '__main__':
    main()
