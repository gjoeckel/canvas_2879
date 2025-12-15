# Box Office Online Links - Quick Reference

## Status

✅ **Scripts Ready:**
- `get-box-file-ids-rest.py` - Uses Box REST API (no SDK needed) ⭐ **Recommended**
- `get-box-file-ids-api.py` - Uses Box SDK (requires boxsdk package)
- `add-box-office-links.py` - Generates Office Online links and updates mapping
- `extract-box-file-ids.py` - Extracts IDs from Box URLs

## Quick Start

### Option 1: Box REST API (Easiest)

1. **Get Developer Token:**
   - Go to https://app.box.com/developers/console
   - Get Developer Token (expires in 60 minutes)

2. **Set environment variable:**
   ```bash
   export BOX_DEVELOPER_TOKEN='your_token_here'
   ```

3. **Run the script:**
   ```bash
   cd /Users/a00288946/Projects/canvas_2879
   python3 get-box-file-ids-rest.py
   ```

4. **Generate links:**
   ```bash
   python3 add-box-office-links.py
   ```

### Option 2: Extract from URLs

If you have Box file URLs:

```bash
python3 extract-box-file-ids.py
# Paste URLs when prompted
```

Then:
```bash
python3 add-box-office-links.py
```

## What Gets Created

- `box-file-ids.json` - File ID mapping (created automatically)
- Updated `DOCX-HTML-MAPPING.md` - With Office Online links

## Link Format

Generated links look like:
```
https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=2071047961795&sharedAccessCode=
```

These allow authenticated users to view .docx files in Microsoft Word Online.

## Files

- `get-box-file-ids-rest.py` - **Use this one** (REST API, no dependencies)
- `BOX-API-SETUP.md` - Complete setup guide
- `BOX-FILE-ID-WORKFLOW.md` - Detailed workflow
- `IMPLEMENTATION-PLAN.md` - Full implementation plan

