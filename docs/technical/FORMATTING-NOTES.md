# Formatting Preservation Notes

## Current Status

The improved `html-to-docx.py` script now:
- ✅ Downloads and embeds images
- ✅ Preserves heading structure (h1, h2, h3, etc.)
- ✅ Keeps semantic class attributes
- ✅ Preserves some style attributes (font-weight, text-align, etc.)

## Formatting Limitations

**Pandoc has limitations** when converting HTML to DOCX:

### What Pandoc Preserves Well:
- ✅ Heading hierarchy (h1 → Heading 1, h2 → Heading 2, etc.)
- ✅ Paragraphs
- ✅ Lists (ul, ol)
- ✅ Links (hyperlinks)
- ✅ Basic formatting (bold, italic)
- ✅ Images (if local paths are provided)

### What Pandoc Doesn't Preserve:
- ❌ Complex CSS styling
- ❌ Custom colors
- ❌ Exact spacing/margins
- ❌ Canvas-specific formatting classes
- ❌ Some inline styles

## Solutions for Better Formatting

### Option 1: Use a Reference DOCX Template

Create a DOCX file with your desired styles:
1. Open Word
2. Create styles for:
   - Heading 1, 2, 3 (matching Canvas styles)
   - Body text
   - Lists
   - Callouts/instructions
3. Save as `canvas-template.docx`
4. Use with conversion:

```bash
python3 html-to-docx.py \
  --html-file "Course Orientation.html" \
  --output-docx "Course Orientation.docx" \
  --reference-doc canvas-template.docx
```

### Option 2: Manual Formatting in Word

After conversion:
1. Open the DOCX in Word
2. Apply styles manually:
   - Select headings → Apply Heading styles
   - Format callouts/instructions
   - Adjust spacing
3. Save as the final version

### Option 3: Post-Process with python-docx

We could add a script to:
- Apply Word styles programmatically
- Set formatting (colors, spacing)
- Add custom styles

## Current Workflow Recommendation

1. **Convert HTML → DOCX** (with images)
2. **Open in Word**
3. **Apply styles manually** (one-time setup)
4. **Save as template** for future conversions
5. **Use template** for subsequent conversions

## Testing the New DOCX

The new DOCX file (`Course Orientation-from-html-v2.docx`) should have:
- ✅ All 6 images embedded
- ✅ Proper heading structure
- ✅ Better formatting than v1

**Next steps:**
1. Open in Word and review
2. Apply any needed formatting
3. Compare with original HTML
4. If good, use as template for future conversions

