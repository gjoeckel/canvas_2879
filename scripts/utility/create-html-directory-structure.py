#!/usr/bin/env python3
"""
Create directory structure for all HTML pages based on index.html.

This script:
1. Parses docs/index.html to extract all page names
2. Creates directory structure matching the course organization
3. Creates empty HTML and DOCX files with lowercase_with_underscores naming
4. Maps to existing 365_Update image directory structure
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup


def normalize_filename(name):
    """Convert page name to lowercase with underscores."""
    # Remove leading numbers and dots (e.g., "1. Course Orientation" -> "Course Orientation")
    name = re.sub(r'^\d+\.\s*', '', name)

    # Convert to lowercase
    name = name.lower()

    # Replace spaces and special characters with underscores
    name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars except hyphens
    name = re.sub(r'[-\s]+', '_', name)   # Replace spaces and hyphens with underscores
    name = re.sub(r'_+', '_', name)        # Replace multiple underscores with single
    name = name.strip('_')                 # Remove leading/trailing underscores

    return name


def parse_index_html(index_file):
    """Parse index.html and extract page structure."""
    with open(index_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    pages = []
    current_module = None
    current_section = None

    # Process all headings and list items
    for element in soup.find_all(['h2', 'h3', 'li']):
        if element.name == 'h2':
            # Module or special heading
            page_text = element.find('span', class_='page-text')
            if page_text:
                text = page_text.get_text(strip=True)
            else:
                text = element.get_text(strip=True)

            if text == "Start Here":
                current_module = "1 Start Here"
                current_section = None
            else:
                # Extract module name (e.g., "Module 1: Document Content")
                current_module = text
                current_section = None
                # Add module page
                pages.append({
                    'type': 'module',
                    'module': current_module,
                    'section': None,
                    'name': text,
                    'filename': normalize_filename(text)
                })

        elif element.name == 'h3':
            # Section heading
            page_text = element.find('span', class_='page-text')
            if page_text:
                text = page_text.get_text(strip=True)
            else:
                text = element.get_text(strip=True)

            # Extract section name (remove "Section X: " prefix if present)
            section_name = re.sub(r'^Section \d+:\s*', '', text, flags=re.IGNORECASE)
            current_section = section_name

            # Add section page
            pages.append({
                'type': 'section',
                'module': current_module,
                'section': current_section,
                'name': text,
                'filename': normalize_filename(text)
            })

        elif element.name == 'li':
            # Learning module or Start Here page
            page_text = element.find('span', class_='page-text')
            if page_text:
                text = page_text.get_text(strip=True)

                # Determine if it's a Start Here page or learning module
                if current_module == "1 Start Here":
                    pages.append({
                        'type': 'start_here',
                        'module': current_module,
                        'section': None,
                        'name': text,
                        'filename': normalize_filename(text)
                    })
                else:
                    pages.append({
                        'type': 'learning_module',
                        'module': current_module,
                        'section': current_section,
                        'name': text,
                        'filename': normalize_filename(text)
                    })

    return pages


def get_module_directory_name(module_name):
    """Convert module name to directory name."""
    if module_name == "1 Start Here":
        return "1 Start Here"
    elif module_name.startswith("Module 1"):
        return "2 Module 1_ Document Content"
    elif module_name.startswith("Module 2"):
        return "3 Module 2_ Document Structure"
    elif module_name.startswith("Module 3"):
        return "4 Module 3_ Evaluating Accessibility & Creating PDFs"
    elif module_name.startswith("Module 4"):
        return "5 Module 4_ Optimizing PDFs in Acrobat"
    elif module_name.startswith("Module 5"):
        return "7 Module 5_ Accessible Excel"
    else:
        # Fallback: use module name as-is
        return module_name


def create_directory_structure(base_dir, pages, dry_run=False):
    """Create directory structure and empty files."""
    base_path = Path(base_dir)
    created_dirs = set()
    created_files = []

    print(f"📁 Creating directory structure in: {base_path}")
    print(f"   Mode: {'DRY RUN' if dry_run else 'CREATE FILES'}\n")

    for page in pages:
        module_dir_name = get_module_directory_name(page['module'])
        module_path = base_path / module_dir_name

        # Create module directory if needed
        if module_path not in created_dirs:
            if not dry_run:
                module_path.mkdir(parents=True, exist_ok=True)
            created_dirs.add(module_path)
            print(f"📂 {module_path.relative_to(base_path)}/")

        # Create HTML and DOCX files
        html_file = module_path / f"{page['filename']}.html"
        docx_file = module_path / f"{page['filename']}.docx"

        if not dry_run:
            # Create empty HTML file with basic structure
            # Extract Canvas URL from index.html if available (placeholder for now)
            # This will be populated when downloading from Canvas
            canvas_url_placeholder = "#"

            html_content = f"""<!DOCTYPE html>

<html dir="ltr" lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<meta content="#f2f2f2" name="theme-color"/>
<title>{page['name']}: WINTER 25-26 COURSE UPDATES</title>
<!-- Canvas Core CSS Files (in order from Canvas source) -->
<link href="../../canvas-fonts.css" media="screen" rel="stylesheet"/>
<link href="../../canvas-variables.css" media="all" rel="stylesheet"/>
<link href="../../canvas-common.css" media="all" rel="stylesheet"/>
<link href="../../canvas-wiki-page.css" media="screen" rel="stylesheet"/>
<link href="../../catalog_canvas_global.css" media="all" rel="stylesheet"/>
<link href="../../webaimCatalog.css" media="all" rel="stylesheet"/>
<link href="../../AD-365-V4.css" media="all" rel="stylesheet"/>
<link href="../../canvas-custom-overrides.css" media="all" rel="stylesheet"/>
</head>
<body class="with-left-side course-menu-expanded padless-content pages primary-nav-expanded context-course_2879">
<div class="content" style="margin-left: 30px; margin-right: 30px;">
<div class="user_content">
<div class="original-link">
<p><a href="{canvas_url_placeholder}" target="_blank">View original page on Canvas</a></p>
</div>
<!-- Content will be populated from Canvas -->
</div>
</div>
</body>
</html>
"""
            html_file.write_text(html_content, encoding='utf-8')

            # Create empty DOCX file (just a placeholder - will be generated by html-to-docx.py)
            # We'll create an empty file as a marker
            docx_file.touch()

        created_files.append({
            'page': page,
            'html': html_file,
            'docx': docx_file
        })

        rel_html = html_file.relative_to(base_path)
        rel_docx = docx_file.relative_to(base_path)
        print(f"   ✅ {rel_html}")
        print(f"   ✅ {rel_docx}")

    return created_files


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Create directory structure for HTML pages based on index.html'
    )
    parser.add_argument(
        '--base-dir',
        type=Path,
        default=Path('WINTER 25-26 COURSE UPDATES'),
        help='Base directory for course files (default: WINTER 25-26 COURSE UPDATES)'
    )
    parser.add_argument(
        '--index-file',
        type=Path,
        default=Path('docs/index.html'),
        help='Path to index.html file (default: docs/index.html)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating files'
    )

    args = parser.parse_args()

    # Parse index.html
    print(f"📄 Parsing: {args.index_file}")
    pages = parse_index_html(args.index_file)
    print(f"   Found {len(pages)} pages\n")

    # Show page breakdown
    page_types = {}
    for page in pages:
        page_type = page['type']
        page_types[page_type] = page_types.get(page_type, 0) + 1

    print("📊 Page Breakdown:")
    for page_type, count in sorted(page_types.items()):
        print(f"   {page_type}: {count}")
    print()

    # Create directory structure
    created_files = create_directory_structure(args.base_dir, pages, args.dry_run)

    print(f"\n{'='*60}")
    print(f"✅ Summary")
    print(f"{'='*60}")
    print(f"Total pages: {len(pages)}")
    print(f"HTML files: {len(created_files)}")
    print(f"DOCX files: {len(created_files)}")

    if args.dry_run:
        print(f"\n💡 Run without --dry-run to create the files")
    else:
        print(f"\n✅ Directory structure created successfully!")
        print(f"   Next steps:")
        print(f"   1. Download HTML content from Canvas for each page")
        print(f"   2. Run rename-and-update-images.py to organize images")
        print(f"   3. Run html-to-docx.py to generate DOCX files")


if __name__ == '__main__':
    main()

