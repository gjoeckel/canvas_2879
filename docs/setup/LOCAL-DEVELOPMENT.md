# Local Development Setup

## Problem

The GitHub Pages site (https://gjoeckel.github.io/canvas_2879/) cannot access `localhost:5000` because:
- GitHub Pages is served from a different domain (github.io)
- Browsers block cross-origin requests to localhost
- The API server runs on your local machine

## Solution: Run Locally

To test the "update canvas" functionality, you need to run the site locally.

### Quick Start

1. **Start the local development server:**
   ```bash
   cd /Users/a00288946/Projects/canvas_2879
   ./run-local-server.sh
   ```

   This will:
   - Start the API server on port 5000
   - Start a local web server on port 8000
   - Serve the docs directory

2. **Open in your browser:**
   ```
   http://localhost:8000
   ```

3. **Test the "update canvas" button:**
   - Click on "Course Orientation"
   - Click "update canvas"
   - It should now work!

### Manual Setup

If you prefer to run servers separately:

**Terminal 1 - API Server:**
```bash
cd /Users/a00288946/Projects/canvas_2879
source /Users/a00288946/Projects/canvas_grab/venv/bin/activate
python3 update-canvas-api.py
```

**Terminal 2 - Web Server:**
```bash
cd /Users/a00288946/Projects/canvas_2879/docs
python3 -m http.server 8000
```

Then open: http://localhost:8000

## Production Deployment

For production use, you would need to:

1. **Deploy the API server** to a cloud service (Heroku, AWS, etc.)
2. **Update the API URL** in `create-github-pages-v2.py` to point to the deployed server
3. **Regenerate the HTML** with the new API URL

### Example: Update API URL for Production

Edit `create-github-pages-v2.py` and change:
```python
const apiUrl = isLocal
    ? "http://localhost:5000/update-canvas-api"
    : "https://your-api-server.com/update-canvas-api";
```

Then regenerate:
```bash
python3 create-github-pages-v2.py
git add docs/index.html
git commit -m "Update API URL for production"
git push origin main
```

## Troubleshooting

**"update canvas" button doesn't work:**
- Make sure the API server is running on port 5000
- Check browser console for errors (F12 → Console)
- Verify OAuth token is configured: `python3 get-box-oauth-token.py --refresh`

**CORS errors:**
- The API server has CORS enabled, but make sure Flask-CORS is installed
- Check that `update-canvas-api.py` has `CORS(app)` enabled

**Port already in use:**
- Kill existing processes: `lsof -ti:5000 | xargs kill`
- Or use different ports and update the code accordingly

