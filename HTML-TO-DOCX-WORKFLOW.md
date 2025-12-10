# HTML to DOCX Conversion Workflow

## Overview

This workflow converts Canvas HTML pages to DOCX files that structurally match the HTML, improving mapping accuracy from ~90% to near 100%.

## Prerequisites

### Install Pandoc

```bash
# macOS
brew install pandoc

# Verify installation
pandoc --version
```

## Workflow Steps

### Step 1: Convert HTML to DOCX

```bash
cd /Users/a00288946/Projects/canvas_2879
source /Users/a00288946/Projects/canvas_grab/venv/bin/activate

# Convert Course Orientation page
python3 html-to-docx.py \
  --html-file "WINTER 25-26 COURSE UPDATES/1 Start Here/Course Orientation.html" \
  --output-docx "WINTER 25-26 COURSE UPDATES/1 Start Here/Course Orientation-from-html.docx"
```

**What this does:**
- Extracts `div.user_content` from HTML
- Cleans HTML (removes Canvas-specific elements)
- Converts iframes to placeholder text
- Converts HTML → DOCX using Pandoc
- Creates a DOCX file that matches HTML structure

### Step 2: Review in Word

1. Open the generated DOCX file in Microsoft Word
2. Review formatting:
   - Headings should match (h1, h2, h3)
   - Paragraphs should be preserved
   - Lists should be intact
   - Links should work
3. Make any necessary adjustments:
   - Fix any formatting issues
   - Adjust spacing if needed
   - Verify all content is present

### Step 3: Upload to Box

1. Open Box and navigate to the file location
2. Upload the new DOCX file (or replace existing one)
3. Note the Box file ID (if replacing, it should be the same)

### Step 4: Create New Mapping

```bash
# Create mapping with the new DOCX
python3 create-docx-html-mapping.py \
  --box-file-id 2071049022878 \
  --html-file "WINTER 25-26 COURSE UPDATES/1 Start Here/Course Orientation.html"
```

**Expected Results:**
- Mapping coverage: 95-100% (up from 89.6%)
- Fewer unmatched items
- More accurate change placement

### Step 5: Test Workflow

1. Open the DOCX in Word
2. Enable Track Changes
3. Make a small edit (e.g., change a word)
4. Save to Box
5. Click "update canvas" on GitHub Pages
6. Verify the change is placed correctly

## Custom Template (Optional)

For better formatting control, create a custom DOCX template:

1. Create a DOCX file with desired styles:
   - Heading 1, 2, 3 styles
   - Body text style
   - List styles
2. Save as `canvas-template.docx`
3. Use with conversion:

```bash
python3 html-to-docx.py \
  --html-file "WINTER 25-26 COURSE UPDATES/1 Start Here/Course Orientation.html" \
  --output-docx "Course Orientation.docx" \
  --reference-doc canvas-template.docx
```

## What Gets Converted

### ✅ Preserved
- Text content
- Heading hierarchy (h1 → Heading 1, h2 → Heading 2, etc.)
- Paragraphs
- Lists (ul → bullet list, ol → numbered list)
- Links (a → hyperlinks)
- Basic formatting (bold, italic)

### ⚠️ Converted/Replaced
- **Iframes** → Placeholder text: `[Video: Title]`
- **Images** → Placeholder (or download and embed manually)
- **Canvas-specific divs** → Flattened/removed
- **CSS classes** → Removed (Word uses its own styles)

### ❌ Not Preserved
- Complex CSS styling
- Canvas UI elements
- Exact spacing (Word uses default spacing)

## Troubleshooting

### Pandoc Not Found
```bash
# Install Pandoc
brew install pandoc

# Or download from: https://pandoc.org/installing.html
```

### Conversion Issues
- Check HTML file structure
- Verify `div.user_content` exists
- Review Pandoc output for warnings

### Mapping Still Low
- Review DOCX structure in Word
- Check for extra/missing paragraphs
- Manually adjust DOCX if needed
- Re-run mapping creation

## Benefits

**Before (Current):**
- Mapping coverage: 89.6%
- 18 unmatched items
- Manual adjustments needed

**After (With HTML → DOCX):**
- Mapping coverage: 95-100%
- 0-5 unmatched items
- Minimal manual adjustments
- More accurate change placement

## Next Steps

1. Convert all Canvas pages to DOCX
2. Upload to Box
3. Create mappings for all pages
4. Test workflow with multiple pages
5. Document any issues or improvements needed

