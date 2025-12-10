# Using Custom CSS with Downloaded Canvas Pages

## Overview

The `download-page-content.py` script now supports using custom CSS to style the downloaded Canvas pages. You can:

1. **Download Canvas CSS automatically** - Gets the official Canvas CSS file
2. **Use a custom CSS file** - Provide your own CSS file
3. **Embed CSS directly** - Include CSS content in the HTML

## Option 1: Download Canvas CSS Automatically

This downloads the Canvas CSS file that's used on the course pages:

```bash
cd /Users/a00288946/Projects/canvas_2879
python3 download-page-content.py --download-canvas-css
```

**What it does:**
- Downloads `canvas_global_app.css` from Canvas
- Saves it to the project root
- Links it in all HTML files

## Option 2: Use a Custom CSS File

If you have your own CSS file:

```bash
python3 download-page-content.py --css-file "path/to/your/custom.css"
```

**Example:**
```bash
# CSS file in project root
python3 download-page-content.py --css-file "custom-styles.css"

# CSS file in a subdirectory
python3 download-page-content.py --css-file "styles/canvas-theme.css"
```

The CSS file path will be calculated relative to each HTML file automatically.

## Option 3: Embed CSS Content Directly

To embed CSS directly in the HTML (no external file needed):

```bash
python3 download-page-content.py --css-content "$(cat your-styles.css)"
```

Or using the helper script:

```bash
./apply-custom-css.sh
# Choose option 3 and provide the CSS file path
```

## Interactive Helper Script

Use the helper script for an interactive experience:

```bash
./apply-custom-css.sh
```

This will prompt you to:
1. Download Canvas CSS automatically
2. Use a custom CSS file
3. Embed CSS content from a file

## Getting Canvas CSS

If you want to extract the CSS from Canvas:

1. **From Canvas page source:**
   - Open a Canvas page in your browser
   - View page source
   - Find the CSS link: `<link rel="stylesheet" href="...canvas_global_app.css">`
   - Download that CSS file

2. **From downloaded HTML:**
   - The Canvas CSS URL is: `https://instructure-uploads.s3.amazonaws.com/account_43980000000000001/attachments/1016014/canvas_global_app.css`
   - You can download it manually or use the `--download-canvas-css` option

## Example: Creating Custom CSS

Create a file `canvas-custom.css`:

```css
/* Custom Canvas Course Styling */
body {
    font-family: "Your Font", sans-serif;
    background-color: #f0f0f0;
}

.content {
    max-width: 1400px;
    padding: 40px;
}

/* Add your custom styles here */
```

Then apply it:

```bash
python3 download-page-content.py --css-file "canvas-custom.css"
```

## Updating Existing Pages

If you've already downloaded pages and want to apply CSS to all of them:

```bash
# Apply CSS to all HTML files (not just redirects)
python3 download-page-content.py --css-file "your-styles.css" --apply-to-all
```

This will:
- Find all HTML files in the project
- Update them with the custom CSS
- Preserve existing content
- Map images to local files

## Notes

- CSS file paths are automatically calculated relative to each HTML file
- If using an external CSS file, make sure it's accessible from the HTML file locations
- Embedded CSS is included directly in each HTML file (larger files but no external dependency)
- Canvas CSS will preserve the original Canvas styling
- Custom CSS allows you to customize the appearance

## Workflow

1. **Download course materials:**
   ```bash
   ./setup-and-download.sh
   ```

2. **Download page content with Canvas CSS:**
   ```bash
   python3 download-page-content.py --download-canvas-css
   ```

3. **Or use custom CSS:**
   ```bash
   python3 download-page-content.py --css-file "my-custom.css"
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Add CSS styling to course pages"
   git push
   ```

