# Quick CSS Reference

## Three Ways to Use Custom CSS

### 1. Download Canvas CSS Automatically

```bash
python3 download-page-content.py --download-canvas-css
```

Downloads the official Canvas CSS file and applies it to all pages.

### 2. Use Your Own CSS File

```bash
python3 download-page-content.py --css-file "my-styles.css"
```

Uses your custom CSS file. Path is calculated relative to each HTML file.

### 3. Apply CSS to All Existing Pages

```bash
python3 download-page-content.py --css-file "my-styles.css" --apply-to-all
```

Updates all HTML files (not just redirects) with your CSS.

## Example Workflow

```bash
# 1. Create your CSS file
cat > canvas-custom.css << 'EOF'
body {
    font-family: "Your Font", sans-serif;
    background: #f0f0f0;
}
.content {
    max-width: 1400px;
}
EOF

# 2. Apply to all pages
python3 download-page-content.py --css-file "canvas-custom.css" --apply-to-all

# 3. Commit
git add .
git commit -m "Apply custom CSS to course pages"
git push
```

## Getting Canvas CSS

The Canvas CSS URL is:
```
https://instructure-uploads.s3.amazonaws.com/account_43980000000000001/attachments/1016014/canvas_global_app.css
```

You can download it manually or use `--download-canvas-css`.

