#!/usr/bin/env python3
"""
Create directory structure: WINTER-25-26-UPDATES/Module-X/Section-X-Y/LA-X-Y-Z
Based on GitHub Pages structure and user-provided Module 1 structure.
"""

import sys
from pathlib import Path

# Import path utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import get_winter_updates_dir

# Structure based on GitHub Pages and user-provided Module 1
# Format: {module_number: {section_number: [list of LA numbers]}}
STRUCTURE = {
    # Start Here (special case - no module/section/LA structure)
    'Start-Here': [],

    # Module 1: Document Content (from user-provided structure)
    1: {
        1: [1, 2],      # Section-1-1: LA-1-1-1, LA-1-1-2
        2: [1, 2, 3],   # Section-1-2: LA-1-2-1, LA-1-2-2, LA-1-2-3 (corrected duplicate)
        3: [1, 2],      # Section-1-3: LA-1-3-1, LA-1-3-2
        4: [1, 2, 3],   # Section-1-4: LA-1-4-1, LA-1-4-2, LA-1-4-3
        5: [1, 2, 3],   # Section-1-5: LA-1-5-1, LA-1-5-2, LA-1-5-3
    },

    # Module 2: Document Structure (from HTML)
    2: {
        1: [1, 2, 3],   # Section-2-1: 3 LAs
        2: [1, 2, 3],   # Section-2-2: 3 LAs
        3: [1, 2],      # Section-2-3: 2 LAs
        4: [1],         # Section-2-4: 1 LA
    },

    # Module 3: Evaluating Accessibility & Creating PDFs (from HTML)
    3: {
        1: [1],         # Section-3-1: 1 LA
        2: [1, 2],      # Section-3-2: 2 LAs
        3: [1, 2],      # Section-3-3: 2 LAs
    },

    # Module 4: Optimizing PDFs in Acrobat (from HTML)
    4: {
        1: [1, 2],      # Section-4-1: 2 LAs
        2: [1],         # Section-4-2: 1 LA
        3: [1],         # Section-4-3: 1 LA
        4: [1],         # Section-4-4: 1 LA
    },

    # Module 5: Accessible Excel (from HTML)
    5: {
        1: [1],         # Section-5-1: 1 LA
        2: [1],         # Section-5-2: 1 LA
        3: [1],         # Section-5-3: 1 LA
        4: [1, 2, 3],    # Section-5-4: 3 LAs
        5: [1],         # Section-5-5: 1 LA
        6: [1],         # Section-5-6: 1 LA
    },
}

def create_structure(base_dir=None):
    """Create directory structure.

    Args:
        base_dir: Base directory (default: data/current/WINTER-25-26-UPDATES)
    """
    if base_dir is None:
        base_dir = get_winter_updates_dir()
    else:
        base_dir = Path(base_dir)
    """Create the directory structure."""
    base = Path(base_dir)
    base.mkdir(exist_ok=True)

    created = []

    # Create Start-Here directory
    start_here_dir = base / "Start-Here"
    start_here_dir.mkdir(exist_ok=True)
    created.append(str(start_here_dir))

    # Create module directories
    for module_num, sections in STRUCTURE.items():
        if module_num == 'Start-Here':
            continue  # Already created

        for section_num, las in sections.items():
            for la_num in las:
                # Format: Module-1, Section-1-1, LA-1-1-1
                module_dir = base / f"Module-{module_num}"
                section_dir = module_dir / f"Section-{module_num}-{section_num}"
                la_dir = section_dir / f"LA-{module_num}-{section_num}-{la_num}"

                la_dir.mkdir(parents=True, exist_ok=True)
                created.append(str(la_dir))

    return created

if __name__ == '__main__':
    print("📁 Creating directory structure...")
    print(f"   Base: {base_dir}")
    print("   Structure: Start-Here + Module-X/Section-X-Y/LA-X-Y-Z\n")

    created = create_structure()

    print(f"✅ Created {len(created)} directories")
    print(f"\n📊 Summary:")

    # Count by level
    start_here = sum(1 for d in created if 'Start-Here' in d)
    modules = len(set(d.split('/')[1] for d in created if 'Module-' in d))
    sections = len(set('/'.join(d.split('/')[:3]) for d in created if 'Section-' in d))
    las = len([d for d in created if 'LA-' in d])

    print(f"   Start-Here: {start_here} directory")
    print(f"   Modules: {modules}")
    print(f"   Sections: {sections}")
    print(f"   Learning Activities: {las}")
    print(f"\n✅ Directory structure complete!")
    print("\n⏳ Waiting for next steps...")
