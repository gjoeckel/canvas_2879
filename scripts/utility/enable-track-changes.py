#!/usr/bin/env python3
"""
Enable Track Changes mode in a DOCX file.

This script modifies the DOCX file's settings to enable Track Changes,
so that when opened in Microsoft Word Online (Box), it opens in "Reviewing" mode.
"""

import argparse
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def enable_track_changes(docx_path):
    """Enable Track Changes mode in a DOCX file."""
    docx_path = Path(docx_path)

    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")

    # Load the DOCX file
    doc = Document(str(docx_path))

    # Access the settings element
    settings = doc.settings._element

    # Check if trackRevisions already exists
    track_revisions = settings.find(qn('w:trackRevisions'))

    if track_revisions is not None:
        # Update existing element
        track_revisions.set(qn('w:val'), 'true')
        print(f"  ✅ Updated existing trackRevisions setting")
    else:
        # Create new trackRevisions element
        track_revisions = OxmlElement('w:trackRevisions')
        track_revisions.set(qn('w:val'), 'true')

        # Insert it into settings (after w:defaultTabStop, before w:autoHyphenation)
        # We'll append it to the end of settings, which is safe
        settings.append(track_revisions)
        print(f"  ✅ Added trackRevisions setting")

    # Also enable trackMoves (optional, but helps with comprehensive tracking)
    track_moves = settings.find(qn('w:trackMoves'))
    if track_moves is not None:
        track_moves.set(qn('w:val'), 'true')
    else:
        track_moves = OxmlElement('w:trackMoves')
        track_moves.set(qn('w:val'), 'true')
        settings.append(track_moves)

    # Save the modified document
    doc.save(str(docx_path))
    print(f"✅ Track Changes enabled in: {docx_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Enable Track Changes mode in DOCX files'
    )
    parser.add_argument(
        'docx_file',
        type=Path,
        help='Path to DOCX file to modify'
    )

    args = parser.parse_args()

    try:
        enable_track_changes(args.docx_file)
        print(f"\n📋 When opened in Microsoft Word Online (Box),")
        print(f"   the document will open in 'Reviewing' mode with Track Changes enabled.")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())

