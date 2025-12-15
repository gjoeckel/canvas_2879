"""
Path utility functions for consistent path handling across scripts.

All paths are relative to the project root directory.
"""

from pathlib import Path

def get_project_root():
    """Get the project root directory.

    Assumes this file is in scripts/utils/, so goes up 2 levels.
    """
    return Path(__file__).parent.parent.parent

def get_config_path(filename='config.toml'):
    """Get path to a config file.

    Args:
        filename: Name of config file (default: 'config.toml')

    Returns:
        Path to config file
    """
    return get_project_root() / filename

def get_config_dir():
    """Get path to config directory.

    Returns:
        Path to config/ directory
    """
    return get_project_root() / 'config'

def get_data_dir(subdir='current'):
    """Get path to data directory.

    Args:
        subdir: Subdirectory ('current' or 'archive')

    Returns:
        Path to data subdirectory
    """
    return get_project_root() / 'data' / subdir

def get_assets_dir(subdir='css'):
    """Get path to assets directory.

    Args:
        subdir: Subdirectory ('css', 'templates', 'js')

    Returns:
        Path to assets subdirectory
    """
    return get_project_root() / 'assets' / subdir

def get_scripts_dir(category='core'):
    """Get path to scripts directory.

    Args:
        category: Script category ('core', 'canvas', 'box', etc.)

    Returns:
        Path to scripts category directory
    """
    return get_project_root() / 'scripts' / category

def get_winter_updates_dir():
    """Get path to WINTER-25-26-UPDATES directory.

    Returns:
        Path to data/current/WINTER-25-26-UPDATES/
    """
    return get_data_dir('current') / 'WINTER-25-26-UPDATES'

def get_winter_archive_dir():
    """Get path to archived WINTER 25-26 COURSE UPDATES directory.

    Returns:
        Path to data/archive/WINTER 25-26 COURSE UPDATES/
    """
    return get_data_dir('archive') / 'WINTER 25-26 COURSE UPDATES'

def get_canvas_reference_docx():
    """Get path to canvas-reference.docx template.

    Returns:
        Path to assets/templates/canvas-reference.docx
    """
    return get_assets_dir('templates') / 'canvas-reference.docx'

def get_css_file(filename):
    """Get path to a CSS file.

    Args:
        filename: Name of CSS file (e.g., 'canvas-fonts.css')

    Returns:
        Path to CSS file in assets/css/
    """
    return get_assets_dir('css') / filename
