#!/usr/bin/env python3
"""
Batch generate DOCX files from all local HTML files.

This script:
1. Finds all _local.html files in WINTER-25-26-UPDATES structure
2. Generates DOCX files for each using html-to-docx.py
3. Reports summary of successful/failed conversions
"""

import sys
import subprocess
from pathlib import Path
from collections import defaultdict

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import get_winter_updates_dir

def generate_docx_for_html(html_file):
    """Generate DOCX file for a single HTML file."""
    script_path = Path(__file__).parent / 'html-to-docx.py'

    cmd = [
        'python3',
        str(script_path),
        '--html-file', str(html_file),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per file
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Timeout after 120 seconds',
            'returncode': 1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': 1
        }

def main():
    winter_dir = get_winter_updates_dir()
    local_html_files = sorted(list(winter_dir.rglob("*_local.html")))

    print("📄 Batch DOCX Generation")
    print("=" * 60)
    print(f"\nFound {len(local_html_files)} local HTML files to process\n")

    results = defaultdict(list)
    processed = 0

    for i, html_file in enumerate(local_html_files, 1):
        rel_path = html_file.relative_to(winter_dir)
        print(f"[{i}/{len(local_html_files)}] Processing: {rel_path}")

        # Check if DOCX already exists (use same naming logic as html-to-docx.py)
        base_name = html_file.stem.lower().replace(' ', '_')
        if base_name.endswith('_local'):
            base_name = base_name[:-6]
        expected_docx = html_file.parent / f"{base_name}.docx"

        if expected_docx.exists():
            print(f"  ⚠️  DOCX already exists: {expected_docx.name}")
            print(f"  ⏭️  Skipping (already generated)")
            results['skipped'].append(html_file)
            continue

        result = generate_docx_for_html(html_file)

        if result['success']:
            results['success'].append(html_file)
            # Check if DOCX was actually created
            if expected_docx.exists():
                print(f"  ✅ DOCX created: {expected_docx.name}")
            else:
                print(f"  ⚠️  Script succeeded but DOCX not found")
        else:
            results['failed'].append((html_file, result))
            error_msg = result['stderr'][:100] if result['stderr'] else 'Unknown error'
            print(f"  ❌ Failed: {error_msg}")

        processed += 1
        print()  # Blank line between files

    # Summary
    print("=" * 60)
    print("📊 Generation Summary")
    print("=" * 60)
    print(f"Total files: {len(local_html_files)}")
    print(f"✅ Successful: {len(results['success'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⏭️  Skipped (already exists): {len(results['skipped'])}")

    if results['failed']:
        print(f"\n❌ Failed files:")
        for html_file, result in results['failed'][:10]:
            rel_path = html_file.relative_to(winter_dir)
            print(f"  - {rel_path}")
            if result['stderr']:
                print(f"    Error: {result['stderr'][:150]}")
        if len(results['failed']) > 10:
            print(f"  ... and {len(results['failed']) - 10} more")

    if results['success']:
        print(f"\n✅ Successfully generated {len(results['success'])} DOCX files")

    # Count total DOCX files now
    all_docx = list(winter_dir.rglob("*.docx"))
    print(f"\n📊 Total DOCX files in structure: {len(all_docx)}")

if __name__ == '__main__':
    main()
