# Plan: Add Box Office Online Links to DOCX-HTML-MAPPING.md

## Overview
Add Microsoft Word Online viewing links for all .docx files in Box to the mapping document.

## Link Pattern
```
https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=FILE_ID&sharedAccessCode=
```

Where `FILE_ID` is extracted from Box file URLs like:
```
https://usu.app.box.com/file/2071047961795
```

## Implementation Steps

### Step 1: Get Box File IDs
**Option A: Manual Collection (Initial)**
- Open each .docx file in Box web interface
- Copy the file ID from the URL
- Enter into a CSV or JSON file

**Option B: Box API (Automated)**
- Use Box API to get file metadata
- Requires Box API credentials
- Can bulk retrieve file IDs

**Option C: Box CLI (If Available)**
- Use Box command-line tools
- Can list files with IDs

### Step 2: Create File ID Mapping
- Create `box-file-ids.json` with structure:
```json
{
  "file_path": "file_id",
  "Course Content - Word/Course Support/course-details.docx": "2071047961795"
}
```

### Step 3: Generate Office Online URLs
- Script reads file IDs
- Generates Office Online URLs
- Validates URL format

### Step 4: Update DOCX-HTML-MAPPING.md
- Add "Box Office Online Link" column to matched files table
- Include links for all matched .docx files
- Add section for unmatched .docx files with their links

## Files to Create
1. `box-file-ids.json` - Mapping of file paths to Box file IDs
2. `add-box-links.py` - Script to generate URLs and update mapping
3. Updated `DOCX-HTML-MAPPING.md` - With Office Online links

## Next Steps
1. Determine method for getting file IDs (manual vs API)
2. Create file ID collection script/template
3. Generate Office Online URLs
4. Update mapping document

