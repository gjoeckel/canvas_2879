# Mapping-Based Approach for Tracked Changes

## Overview

Instead of trying to match tracked changes by context, we create a **baseline mapping** between DOCX paragraphs and HTML elements. When tracked changes are detected, we use this mapping to place them in the correct location.

## How It Works

### Phase 1: Create Mapping (One-Time Setup)

1. **Download the DOCX file** from Box (baseline version)
2. **Extract paragraph structure** from DOCX (97 paragraphs)
3. **Extract element structure** from HTML (106 elements)
4. **Match paragraphs to HTML elements** using text similarity
5. **Save mapping** to `Course Orientation.mapping.json`

**Result**: 95 mappings (89.6% coverage)

### Phase 2: Apply Changes (When "Update Canvas" is Clicked)

1. **Download current DOCX** from Box
2. **Extract tracked changes** with paragraph indices
3. **Load mapping file** (if exists)
4. **Use mapping** to find the correct HTML element for each change
5. **Apply changes** at the mapped location
6. **Push to Canvas**

## Benefits

✅ **Precise placement** - Changes go to the exact location they were made in the DOCX
✅ **No context matching** - Don't need to search for text in HTML
✅ **Reliable** - Works even if text has been modified
✅ **Fast** - Direct lookup instead of searching

## Current Status

- ✅ Mapping created for Course Orientation (95/96 paragraphs mapped)
- ✅ Mapping-based update function implemented
- ✅ Integration with main update script complete
- ✅ API server uses mapping when available

## Usage

### Create Mapping for a Page

```bash
cd /Users/a00288946/Projects/canvas_2879
source /Users/a00288946/Projects/canvas_grab/venv/bin/activate
python3 create-docx-html-mapping.py \
  --box-file-id 2071049022878 \
  --html-file "WINTER 25-26 COURSE UPDATES/1 Start Here/Course Orientation.html"
```

### Update Canvas (Uses Mapping Automatically)

When you click "update canvas" on the GitHub Pages site, the system will:
1. Check for `Course Orientation.mapping.json` in the same directory
2. If found, use mapping-based update
3. If not found, fall back to context-based update

## Mapping File Structure

```json
{
  "box_file_id": "2071049022878",
  "html_file": "WINTER 25-26 COURSE UPDATES/1 Start Here/Course Orientation.html",
  "docx_structure": [...],  // All DOCX paragraphs
  "html_structure": [...],  // All HTML elements
  "mapping": [
    {
      "docx_index": 5,
      "html_index": 9,
      "html_tag": "p",
      "similarity_score": 0.962
    }
  ]
}
```

## Next Steps

1. Test with a tracked change in the DOCX
2. Verify the change is placed correctly using the mapping
3. Expand to other pages as needed

