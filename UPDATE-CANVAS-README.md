# Update Canvas Functionality

This document describes the "update canvas" functionality for Course Orientation on the GitHub Pages site.

## Overview

The "update canvas" feature allows you to:
1. Review DOCX file for tracked changes
2. Update local HTML file based on changes
3. Push changes to Canvas
4. Display success message with timestamp

## Link Order

For Course Orientation, the links are displayed in this order:
- **view docx**: Opens the DOCX file in Box viewer
- **edit docx**: Opens the DOCX file in Box Microsoft Word Online editor
- **view canvas**: Opens the Canvas course page
- **update canvas**: Triggers the update process (only for Course Orientation)

## How It Works

### 1. User Clicks "update canvas"

When the "update canvas" link is clicked:
- JavaScript prevents default link behavior
- Button shows "updating..." state
- Sends POST request to update API endpoint

### 2. Backend Processing

The backend script (`update-canvas-from-docx.py`) performs:

#### A. Review DOCX for Tracked Changes
- Downloads DOCX file from Box using Box API
- Extracts tracked changes from DOCX XML structure:
  - **Insertions** (`w:ins` elements): New text added
  - **Deletions** (`w:del` elements): Text removed

#### B. Update Local HTML
- Reads the local HTML file (`WINTER 25-26 COURSE UPDATES/1 Start Here/Course Orientation.html`)
- Applies changes:
  - **Deletions**: Removes text matching deleted content
  - **Insertions**: Adds new text as paragraphs at the end of `.user_content`

#### C. Push Changes to Canvas
- Uses Canvas API to update the page content
- Extracts `.user_content` div from updated HTML
- Updates the Canvas page with new body content

#### D. Display Success Message
- Returns JSON response with success status
- JavaScript displays message in `div.note` with timestamp
- Message format: "Canvas page updated successfully at [timestamp]. Applied X insertions and Y deletions."

## Files

### Frontend
- `docs/index.html`: GitHub Pages site with "update canvas" link and JavaScript
- `create-github-pages-v2.py`: Script that generates the HTML with update functionality

### Backend
- `update-canvas-from-docx.py`: Main script that processes DOCX and updates Canvas
- `update-canvas-api.py`: Flask API endpoint wrapper (for local development or serverless)

## Setup

### Prerequisites
1. Box Developer Token (set as `BOX_DEVELOPER_TOKEN` environment variable)
2. Canvas API Token (in `config.toml`)
3. Python dependencies:
   - `requests`
   - `beautifulsoup4`
   - `python-docx` (optional, for text extraction)
   - `canvasapi`
   - `flask` and `flask-cors` (for API endpoint)

### Local Development

1. **Start the API server:**
   ```bash
   cd /Users/a00288946/Projects/canvas_2879
   python3 update-canvas-api.py
   ```

2. **Open the GitHub Pages site locally:**
   ```bash
   # Serve the docs directory
   cd docs
   python3 -m http.server 8000
   ```

3. **Access the site:**
   - Open `http://localhost:8000` in your browser
   - The JavaScript will automatically use `http://localhost:5000/update-canvas-api`

### Production Deployment

For GitHub Pages (static hosting), you'll need to:
1. Deploy the API endpoint as a serverless function (AWS Lambda, Vercel, etc.)
2. Update the JavaScript `apiUrl` to point to your serverless function URL

## Testing

### Test the Update Script Directly

```bash
cd /Users/a00288946/Projects/canvas_2879
python3 update-canvas-from-docx.py \
  --box-file-id 2071049022878 \
  --canvas-page-slug course-orientation \
  --html-file "WINTER 25-26 COURSE UPDATES/1 Start Here/Course Orientation.html"
```

### Expected Output

```json
{
  "success": true,
  "message": "Canvas page updated successfully at 2025-01-XX XX:XX:XX. Applied 2 insertions and 1 deletions.",
  "timestamp": "2025-01-XXTXX:XX:XX.XXXXXX",
  "changes": {
    "insertions": 2,
    "deletions": 1
  }
}
```

## Current Limitations

1. **Insertions**: New text is appended at the end of `.user_content` rather than inserted at the correct location
2. **Deletions**: Text matching is done by exact string match, which may not work for partial matches
3. **Formatting**: Formatting changes (bold, italic, etc.) are not preserved
4. **Context Matching**: No intelligent context matching to insert text at the right location

## Future Improvements

1. Implement context-aware insertion (match surrounding text to find insertion point)
2. Preserve formatting when applying changes
3. Handle partial text matches for deletions
4. Add preview/diff view before applying changes
5. Support for other pages beyond Course Orientation

