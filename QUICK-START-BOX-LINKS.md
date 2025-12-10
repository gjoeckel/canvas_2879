# Quick Start: Adding Box Office Online Links

## Current Status

✅ **Scripts Ready:**
- `add-box-office-links.py` - Ready to generate links
- `extract-box-file-ids.py` - Ready to extract IDs from URLs
- `box-file-ids-template.json` - Template with all 100 files

⏳ **Need:** Box file IDs to generate links

## Fastest Method: Extract from Box URLs

### Step 1: Get Box URLs

1. Open Box web interface: https://usu.app.box.com
2. Navigate to: `WebAIM Shared/5 Online Courses/Winter 25-25 Course Update`
3. For each .docx file:
   - Right-click → "Share" or open the file
   - Copy the URL from address bar
   - Format: `https://usu.app.box.com/file/2071047961795`

### Step 2: Extract File IDs

**Option A: Interactive (paste URLs)**
```bash
cd /Users/a00288946/Projects/canvas_2879
python3 extract-box-file-ids.py
# Paste URLs one per line, press Enter twice when done
```

**Option B: From file**
```bash
# Create urls.txt with Box URLs (one per line)
python3 extract-box-file-ids.py < urls.txt
```

### Step 3: Generate Links

```bash
python3 add-box-office-links.py
```

This updates `DOCX-HTML-MAPPING.md` with Office Online links!

## Alternative: Manual Entry

1. Copy `box-file-ids-template.json` to `box-file-ids.json`
2. For each file, add the file ID:
   ```json
   {
     "relative_path": "Course Content - Word/Course Support/course-details.docx",
     "file_id": "2071047961795",
     "box_url": "https://usu.app.box.com/file/2071047961795"
   }
   ```
3. Run: `python3 add-box-office-links.py`

## What You'll Get

The updated `DOCX-HTML-MAPPING.md` will have:
- "Box Office Online Link" column in matched files table
- Clickable links like: [Open in Word Online](https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2071047961795&sharedAccessCode=)
- Links for all 100 .docx files

## Need Help?

See `BOX-FILE-ID-WORKFLOW.md` for detailed instructions.

