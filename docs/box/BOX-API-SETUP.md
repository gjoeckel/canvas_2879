# Box API Setup Guide

## Quick Start: Developer Token Method

### Step 1: Get Developer Token

1. Go to https://app.box.com/developers/console
2. Sign in with your Box account
3. Create a new app or select existing app
4. Choose "Custom App" → "Server Authentication (with JWT)" or use existing
5. In the app settings, find **"Developer Token"**
6. Click "Generate Developer Token" (expires in 60 minutes)

### Step 2: Set Environment Variable

```bash
export BOX_DEVELOPER_TOKEN='your_developer_token_here'
```

Or add to `~/.zshrc`:
```bash
echo 'export BOX_DEVELOPER_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Find Folder ID (Optional)

The script will try to find the folder automatically, but you can also provide the folder ID:

1. Open the folder in Box web interface
2. Copy the folder ID from the URL: `https://usu.app.box.com/folder/FOLDER_ID`
3. Set environment variable:
```bash
export BOX_FOLDER_ID='your_folder_id_here'
```

### Step 4: Run the Script

**Using REST API (Recommended - no SDK needed):**
```bash
cd /Users/a00288946/Projects/canvas_2879
python3 get-box-file-ids-rest.py
```

**Or using Box SDK (if installed):**
```bash
./run-box-api.sh
# or
python3 get-box-file-ids-api.py
```

## Alternative: Config File Method

Create `.box-api-config.json` in the project directory:

```json
{
  "developer_token": "your_developer_token_here",
  "folder_id": "0"
}
```

Or for OAuth2:
```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "access_token": "your_access_token",
  "refresh_token": "your_refresh_token",
  "folder_id": "0"
}
```

## What the Script Does

1. ✅ Connects to Box API
2. ✅ Scans the course folder structure
3. ✅ Finds all .docx files
4. ✅ Extracts file IDs
5. ✅ Matches files to template
6. ✅ Updates `box-file-ids.json`
7. ✅ Ready for link generation

## Troubleshooting

### "No valid credentials found"
- Set `BOX_DEVELOPER_TOKEN` environment variable
- Or create `.box-api-config.json` with credentials

### "Folder not found"
- Set `BOX_FOLDER_ID` to the specific folder ID
- Or the script will try to search for it

### "No .docx files found"
- Check that the folder ID is correct
- Verify files exist in Box
- Check folder permissions

## Next Steps

After running the script successfully:

```bash
# Generate Office Online links
python3 add-box-office-links.py

# Check the updated mapping
open DOCX-HTML-MAPPING.md
```

