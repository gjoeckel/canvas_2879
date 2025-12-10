# HTML to DOCX Conversion Plan

## Current Problem

**Mismatch Analysis:**
- DOCX paragraphs: 96
- HTML elements: 106
- Mapped pairs: 95 (89.6% coverage)
- Unmatched items: 6 DOCX paragraphs, 12 HTML elements

**Root Cause:**
The DOCX files were created independently from the Canvas HTML pages, leading to structural differences:
- Different paragraph breaks
- Missing/extra elements
- Formatting differences
- Content organization mismatches

## Proposed Solution: HTML → DOCX Conversion

### Approach 1: Pandoc HTML → DOCX (Recommended)

**Benefits:**
- ✅ Creates DOCX that structurally matches HTML
- ✅ Preserves paragraph structure
- ✅ Maintains headings hierarchy
- ✅ Handles lists, links, and basic formatting
- ✅ Can achieve near-100% mapping accuracy

**Workflow:**
1. Extract `div.user_content` from Canvas HTML
2. Clean HTML (remove Canvas-specific elements like iframes, or convert to placeholders)
3. Convert HTML → DOCX using Pandoc
4. Upload DOCX to Box
5. Create new mapping (should be much more accurate)
6. Edit DOCX with tracked changes
7. Apply changes using improved mapping

### Approach 2: Pandoc with Custom Template

**Benefits:**
- ✅ More control over DOCX structure
- ✅ Can preserve Canvas-specific formatting
- ✅ Custom styling for headings, paragraphs, etc.

**Workflow:**
1. Create Pandoc DOCX template matching Canvas styles
2. Extract and clean HTML content
3. Convert using custom template
4. Upload to Box

### Approach 3: Hybrid Approach

**Benefits:**
- ✅ Best of both worlds
- ✅ Preserve Canvas structure while allowing Word editing

**Workflow:**
1. Convert HTML → DOCX with Pandoc
2. Manually adjust in Word for perfect alignment
3. Save as new baseline DOCX
4. Use for all future edits

## Implementation Plan

### Step 1: Install Pandoc

```bash
# macOS
brew install pandoc

# Or download from: https://pandoc.org/installing.html
```

### Step 2: Create HTML Extraction Script

Extract just the `div.user_content` content, clean it:
- Remove iframes (or convert to placeholders)
- Preserve headings, paragraphs, lists
- Keep links
- Handle images (download and reference locally, or use placeholders)

### Step 3: Convert HTML → DOCX

```bash
pandoc extracted-content.html -o course-orientation.docx \
  --reference-doc=canvas-template.docx  # Optional: custom template
```

### Step 4: Upload to Box

Replace existing DOCX file in Box with the new one.

### Step 5: Recreate Mapping

Run `create-docx-html-mapping.py` again - should see much higher coverage.

### Step 6: Test Workflow

1. Make tracked change in new DOCX
2. Click "update canvas"
3. Verify change is placed correctly

## Considerations

### What to Preserve
- ✅ Text content
- ✅ Heading hierarchy (h1, h2, h3)
- ✅ Paragraph structure
- ✅ Lists (ul, ol)
- ✅ Links (convert to Word hyperlinks)
- ✅ Basic formatting (bold, italic)

### What to Handle Differently
- ⚠️ **Iframes** (videos): Convert to placeholder text like "[Video: Course Orientation]"
- ⚠️ **Images**: Download and embed, or use placeholder
- ⚠️ **Canvas-specific divs**: Remove or flatten
- ⚠️ **Special formatting**: May need manual adjustment

### What Might Be Lost
- ❌ Complex CSS styling (but that's okay - we apply CSS separately)
- ❌ Canvas-specific UI elements (intentional)
- ❌ Exact spacing (Word will use its own spacing)

## Expected Results

**Before:**
- Mapping coverage: 89.6%
- Unmatched items: 18 total
- Manual adjustments needed: Frequent

**After:**
- Mapping coverage: 95-100%
- Unmatched items: 0-5 (mostly edge cases)
- Manual adjustments: Rare

## Alternative: Two-Way Sync

Instead of just HTML → DOCX, we could also support DOCX → HTML:

1. Edit DOCX in Word with tracked changes
2. Convert DOCX → HTML using Pandoc
3. Replace `div.user_content` in Canvas HTML
4. Push to Canvas

This would eliminate the need for mapping entirely, but requires:
- Perfect DOCX → HTML conversion
- Handling of Canvas-specific elements
- Preserving Canvas styling

## Recommendation

**Start with Approach 1 (Pandoc HTML → DOCX):**
- Simplest to implement
- Good enough for most cases
- Can refine later if needed

**If issues arise, try Approach 2 (Custom Template):**
- More control
- Better formatting preservation

**Consider Approach 3 (Hybrid) for critical pages:**
- Manual fine-tuning for perfect alignment
- Use as baseline for future edits

