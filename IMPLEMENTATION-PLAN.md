# Implementation Plan: Box Office Online Links

## Goal
Add Microsoft Word Online viewing links to DOCX-HTML-MAPPING.md for all .docx files in Box.

## Link Format
```
https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=FILE_ID&sharedAccessCode=
```

Where `FILE_ID` is extracted from Box file URLs like:
```
https://usu.app.box.com/file/2071047961795
```

## Files Created

### 1. Scripts
- **`add-box-office-links.py`** - Main script to generate URLs and update mapping
- **`extract-box-file-ids.py`** - Helper to extract file IDs from Box URLs

### 2. Templates & Data
- **`box-file-ids-template.json`** - Template with all 100 .docx files (auto-generated)
- **`box-file-ids.json`** - Your file ID mapping (create this by filling template)

### 3. Documentation
- **`BOX-FILE-ID-WORKFLOW.md`** - Complete workflow guide
- **`add-box-office-links.md`** - Implementation plan details

## Implementation Steps

### Phase 1: Collect File IDs

**Option A: Manual (Recommended)**
1. Open Box web interface
2. For each .docx file, copy the URL
3. Use extractor script:
   ```bash
   python3 extract-box-file-ids.py
   # Paste URLs when prompted
   ```

**Option B: Batch Processing**
1. Collect URLs in a text file (`urls.txt`)
2. Run:
   ```bash
   python3 extract-box-file-ids.py < urls.txt
   ```

**Option C: Box API (Future)**
- If Box API credentials available
- Can bulk retrieve file IDs automatically

### Phase 2: Generate Links

Once `box-file-ids.json` is populated:

```bash
python3 add-box-office-links.py
```

This will:
- Read file IDs from `box-file-ids.json`
- Generate Office Online URLs
- Update `DOCX-HTML-MAPPING.md` with:
  - New "Box Office Online Link" column in matched files table
  - Links for all matched .docx files
  - Links for unmatched .docx files section

### Phase 3: Verify

1. Open `DOCX-HTML-MAPPING.md`
2. Check that links are present
3. Test a few links to ensure they work

## Expected Output

The updated `DOCX-HTML-MAPPING.md` will have:

### Matched Files Table
| .docx File (Box) | HTML File (GitHub) | Match Type | Box Office Online Link |
|------------------|---------------------|------------|------------------------|
| `Course Content - Word/Course Support/course-details.docx` | `.../Course Details.html` | exact_normalized | [Open in Word Online](https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2071047961795&sharedAccessCode=) |

### Unmatched .docx Files Section
- `Course Content - Word/Module 1/Section 2 Images/images-part-1.docx` - [Open in Word Online](https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2071047961796&sharedAccessCode=)

## Current Status

✅ **Completed:**
- Template file created (`box-file-ids-template.json`) with all 100 .docx files
- Scripts created for extracting IDs and generating links
- Workflow documentation created

⏳ **Next Steps:**
1. Collect Box file IDs (manual or via API)
2. Populate `box-file-ids.json`
3. Run `add-box-office-links.py` to update mapping

## Quick Start

```bash
# 1. Get file IDs (paste Box URLs)
python3 extract-box-file-ids.py

# 2. Generate and add links
python3 add-box-office-links.py

# 3. Check results
open DOCX-HTML-MAPPING.md
```

## Notes

- **File ID format**: Numeric ID from Box file URL
- **Link pattern**: Fixed format with file ID parameter
- **Incremental updates**: Can update `box-file-ids.json` incrementally
- **Verification**: Script shows progress (X/100 files with IDs)

