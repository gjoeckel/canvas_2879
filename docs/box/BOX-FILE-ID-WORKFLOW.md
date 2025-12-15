# Box File ID Collection Workflow

## Overview
This workflow helps you collect Box file IDs and add Office Online links to the DOCX-HTML-MAPPING.md file.

## Step 1: Get Box File IDs

### Option A: Manual Collection (Recommended for Small Sets)

1. **Open Box web interface** and navigate to the course folder
2. **For each .docx file**:
   - Right-click the file → "Share" or open the file
   - Copy the URL from the address bar
   - The URL format is: `https://usu.app.box.com/file/2071047961795`
   - The number at the end is the file ID

3. **Use the extractor script**:
   ```bash
   # Create a text file with URLs (one per line)
   # Then run:
   python3 extract-box-file-ids.py < urls.txt

   # Or paste URLs interactively:
   python3 extract-box-file-ids.py
   ```

### Option B: Box API (For Bulk Collection)

If you have Box API credentials:

1. **Set up Box API**:
   ```bash
   # Install Box SDK
   pip install boxsdk
   ```

2. **Use Box API script** (to be created if needed):
   ```bash
   python3 get-box-file-ids-api.py
   ```

### Option C: Box CLI

If Box CLI is installed:

```bash
box files:get --id <folder_id> --fields id,name,path_collection
```

## Step 2: Update File ID Mapping

1. **Edit `box-file-ids.json`**:
   - Fill in `file_id` for each file
   - Optionally add `box_url` for reference
   - Save the file

2. **Or use the extractor**:
   ```bash
   python3 extract-box-file-ids.py
   # Paste URLs when prompted
   ```

## Step 3: Generate Office Online Links

Run the link generator:

```bash
python3 add-box-office-links.py
```

This will:
- Read file IDs from `box-file-ids.json`
- Generate Office Online URLs
- Update `DOCX-HTML-MAPPING.md` with links

## Step 4: Verify

1. **Check the mapping file**:
   ```bash
   open DOCX-HTML-MAPPING.md
   ```

2. **Verify links work**:
   - Click a few Office Online links
   - Ensure they open in Microsoft Word Online

## File Structure

```
canvas_2879/
├── box-file-ids-template.json    # Template (auto-generated)
├── box-file-ids.json              # Your file ID mapping (create this)
├── extract-box-file-ids.py        # Helper to extract IDs from URLs
├── add-box-office-links.py        # Main script to add links
└── DOCX-HTML-MAPPING.md           # Updated with Office Online links
```

## Quick Start

1. **Get file IDs** (choose one method):
   - Manual: Open files in Box, copy URLs, use extractor script
   - API: Use Box API to bulk retrieve (if available)

2. **Update mapping**:
   ```bash
   python3 add-box-office-links.py
   ```

3. **Done!** Links are now in DOCX-HTML-MAPPING.md

## Tips

- **Batch processing**: Collect URLs in a text file, then pipe to extractor
- **Partial updates**: You can update `box-file-ids.json` incrementally
- **Verification**: The script shows how many files have IDs vs. total files

## Example

```bash
# 1. Collect URLs (paste into urls.txt)
cat > urls.txt << EOF
https://usu.app.box.com/file/2071047961795
https://usu.app.box.com/file/2071047961796
EOF

# 2. Extract file IDs
python3 extract-box-file-ids.py < urls.txt

# 3. Generate links
python3 add-box-office-links.py

# 4. Check results
open DOCX-HTML-MAPPING.md
```

