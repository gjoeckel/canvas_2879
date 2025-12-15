#!/usr/bin/env python3
"""
Batch process all HTML files to rename images to Canvas IDs and create _local.html versions.

This script:
1. Finds all HTML files (excluding _local.html files)
2. Processes each HTML file with rename-images-by-canvas-id.py
3. Reports summary of processing
"""

import argparse
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import (
    get_project_root,
    get_config_path,
    get_winter_updates_dir,
    get_winter_archive_dir
)

def find_html_files(root_dir, exclude_local=True):
    """Find all HTML files in the directory tree."""
    root = Path(root_dir)
    html_files = []

    for html_file in root.rglob('*.html'):
        if exclude_local and html_file.name.endswith('_local.html'):
            continue
        html_files.append(html_file)

    return sorted(html_files)

def process_html_file(html_file, downloaded_dir, image_dir, config_file, dry_run=False):
    """Process a single HTML file using rename-images-by-canvas-id.py."""
    script_path = Path(__file__).parent / 'rename-images-by-canvas-id.py'

    cmd = [
        'python3',
        str(script_path),
        '--html-file', str(html_file),
        '--downloaded-dir', str(downloaded_dir),
        '--config', str(config_file),
    ]

    if image_dir:
        cmd.extend(['--image-dir', str(image_dir)])

    if dry_run:
        cmd.append('--dry-run')

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': 1
        }

def main():
    parser = argparse.ArgumentParser(
        description='Batch process HTML files to rename images to Canvas IDs'
    )
    parser.add_argument(
        '--html-dir',
        type=Path,
        default=get_winter_updates_dir(),
        help='Directory containing HTML files (default: data/current/WINTER-25-26-UPDATES)'
    )
    parser.add_argument(
        '--downloaded-dir',
        type=Path,
        default=get_winter_archive_dir() / '365_Update',
        help='Directory containing downloaded image files (searched recursively, default: data/archive/WINTER 25-26 COURSE UPDATES/365_Update)'
    )
    parser.add_argument(
        '--image-dir',
        type=Path,
        help='Directory where renamed images should be placed (default: same as downloaded-dir)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=get_config_path(),
        help='Path to config.toml file (default: config.toml in project root)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output for each file'
    )

    args = parser.parse_args()

    # Validate paths
    if not args.html_dir.exists():
        print(f"❌ Error: HTML directory not found: {args.html_dir}")
        sys.exit(1)

    if not args.downloaded_dir.exists():
        print(f"❌ Error: Downloaded directory not found: {args.downloaded_dir}")
        sys.exit(1)

    if not args.config.exists():
        print(f"❌ Error: Config file not found: {args.config}")
        sys.exit(1)

    # Find all HTML files
    print(f"🔍 Finding HTML files in: {args.html_dir}")
    html_files = find_html_files(args.html_dir)

    if not html_files:
        print(f"  ⚠️  No HTML files found")
        sys.exit(0)

    print(f"✅ Found {len(html_files)} HTML files to process\n")

    # Process each file
    results = defaultdict(list)
    processed = 0

    for i, html_file in enumerate(html_files, 1):
        rel_path = html_file.relative_to(args.html_dir)
        print(f"[{i}/{len(html_files)}] Processing: {rel_path}")

        if args.verbose:
            print(f"  Full path: {html_file}")

        result = process_html_file(
            html_file,
            args.downloaded_dir,
            args.image_dir,
            args.config,
            args.dry_run
        )

        if result['success']:
            results['success'].append(html_file)
            if args.verbose:
                print(result['stdout'])
        else:
            results['failed'].append((html_file, result))
            print(f"  ❌ Failed: {result['stderr'][:100] if result['stderr'] else 'Unknown error'}")

        processed += 1
        print()  # Blank line between files

    # Summary
    print("=" * 60)
    print("📊 Processing Summary")
    print("=" * 60)
    print(f"Total files: {len(html_files)}")
    print(f"Successful: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")

    if results['failed']:
        print(f"\n❌ Failed files:")
        for html_file, result in results['failed']:
            rel_path = html_file.relative_to(args.html_dir)
            print(f"  - {rel_path}")
            if args.verbose:
                print(f"    Error: {result['stderr'][:200]}")

    if results['success']:
        print(f"\n✅ Successfully processed {len(results['success'])} files")
        if not args.dry_run:
            print(f"   - Images renamed to Canvas IDs")
            print(f"   - _local.html files created")

if __name__ == '__main__':
    main()
