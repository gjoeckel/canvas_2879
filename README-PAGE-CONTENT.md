# Downloading Actual Page Content

## Overview

By default, `canvas_grab` creates redirect HTML files for Canvas pages that just redirect to the Canvas website. This script downloads the actual HTML content and maps images to local files.

## Usage

After running `setup-and-download.sh` to download course materials, run:

```bash
cd /Users/a00288946/Projects/canvas_2879
python3 download-page-content.py
```

## What It Does

1. **Finds redirect HTML files** - Locates all HTML files that contain redirect meta tags
2. **Fetches actual page content** - Uses Canvas API to get the full HTML body of each page
3. **Maps images to local files** - Replaces Canvas image URLs with relative paths to locally downloaded images
4. **Creates complete HTML pages** - Generates standalone HTML files with:
   - Full page content from Canvas
   - Local image references
   - Link back to original Canvas page
   - Clean, readable styling

## Features

- ✅ Downloads actual HTML content (not just redirects)
- ✅ Maps Canvas image URLs to local files
- ✅ Handles images in `<img>` tags, CSS backgrounds, and link hrefs
- ✅ Creates standalone HTML files that work offline
- ✅ Preserves original Canvas styling where possible

## Image Mapping

The script searches for images in:
- `<img src="...">` tags
- CSS `background-image: url(...)` styles
- `<link href="...">` tags pointing to images

Images are matched by filename and mapped to local files in the `unmoduled/` directory or module folders.

## Notes

- Some pages may not be found if their titles don't match exactly
- Images must be downloaded first by `canvas_grab` for mapping to work
- The script preserves Canvas CSS links but maps image URLs to local files

## Integration with Workflow

Add this to your update workflow:

```bash
# Download course materials
./setup-and-download.sh

# Download actual page content and map images
python3 download-page-content.py

# Commit changes
git add .
git commit -m "Update course materials with actual page content"
git push
```

