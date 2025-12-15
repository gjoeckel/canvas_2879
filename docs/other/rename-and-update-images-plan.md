# Plan: Rename Images to Canvas IDs and Update HTML Files

## Current Situation

- **472 image files** in `WINTER 25-26 COURSE UPDATES/365_Update/` (organized in subdirectories)
- **31 HTML files** in `WINTER 25-26 COURSE UPDATES/` (various subdirectories)
- **47 unique Canvas file IDs** referenced across all HTML files
- Images currently have descriptive names (e.g., `gradesFilterClick.png`)
- HTML files reference Canvas URLs (e.g., `https://usucourses.instructure.com/courses/2879/files/1235615/preview?...`)

## Goal

1. **Rename image files** to Canvas file IDs (e.g., `1235615.png`) while preserving extensions
2. **Update HTML files** to reference local image paths instead of Canvas URLs
3. Keep images in their current directory structure within `365_Update/`

## Proposed Process

### Step 1: Map HTML Files to Image Directories

Match HTML file locations to `365_Update` subdirectories:
- `1 Start Here/Course Orientation.html` → `365_Update/Course Orientation/`
- `2 Module 1_ Document Content/...` → `365_Update/m1/...`
- `3 Module 2_ Document Structure/...` → `365_Update/m2/...`
- etc.

### Step 2: Extract Canvas File IDs from Each HTML File

For each HTML file:
- Parse HTML to find all `<img>` tags
- Extract Canvas file IDs from `src` attributes (pattern: `/files/(\d+)/`)
- Store mapping: HTML file → list of Canvas file IDs

### Step 3: Match Downloaded Images to Canvas IDs

For each HTML file's corresponding image directory:
- Get file sizes from Canvas API for each file ID
- Match downloaded images by file size
- Rename matched files to `{canvas_id}.{original_extension}`

### Step 4: Update HTML Files

For each HTML file:
- Replace Canvas URLs with local paths
- Path format: `365_Update/{subdirectory}/{canvas_id}.{ext}`
- Keep relative paths (relative to HTML file location)

## Example Transformation

**Before:**
- File: `365_Update/Course Orientation/gradesFilterClick.png`
- HTML: `<img src="https://usucourses.instructure.com/courses/2879/files/1235615/preview?verifier=..." />`

**After:**
- File: `365_Update/Course Orientation/1235615.png` (renamed)
- HTML: `<img src="../../365_Update/Course Orientation/1235615.png" />` (relative path)

## Questions/Considerations

1. **Path format**: Should we use:
   - Absolute paths: `/Users/a00288946/Projects/canvas_2879/WINTER 25-26 COURSE UPDATES/365_Update/...`
   - Relative paths: `../../365_Update/Course Orientation/1235615.png`
   - **Recommendation**: Relative paths (more portable)

2. **Directory structure**: Keep images in `365_Update/` subdirectories or flatten?
   - **Recommendation**: Keep current structure (organized by module/page)

3. **Multiple HTML files referencing same image**: Some images might be used in multiple HTML files
   - **Solution**: Rename once, update all HTML files that reference it

4. **Unmatched images**: What if we can't match a downloaded image to a Canvas ID?
   - **Solution**: Report and leave unchanged, or use manual mapping

## Implementation Script

Create `rename-and-update-images.py` that:
1. Scans all HTML files
2. Extracts Canvas file IDs
3. Matches images by size (using Canvas API)
4. Renames images to Canvas IDs
5. Updates HTML files with local paths

## Expected Outcome

- All images renamed to `{canvas_id}.{ext}` format
- All HTML files updated to use local image paths
- Images display correctly when HTML files are opened locally
- DOCX conversion can use these local images

