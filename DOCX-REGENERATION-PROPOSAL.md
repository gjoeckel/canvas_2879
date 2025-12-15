# Proposal: Recreate DOCX Files from Local HTML Pages

## Overview

Generate DOCX files for all 67 `_local.html` files (excluding the 3 Start-Here files that already have DOCX) using the **established process** documented in:

- `docs/workflow/HTML-TO-DOCX-WORKFLOW.md` - Complete workflow documentation
- `GENERATE-MISSING-SECTION-FILES-PLAN.md` - Phase 3 DOCX generation plan
- `scripts/core/html-to-docx.py` - Main conversion script
- `scripts/core/batch-generate-docx.py` - Batch processing script

This proposal confirms the existing process addresses the requirements:

1. **All images are embedded** (not linked) in the DOCX files - ✅ Handled by Pandoc (see workflow docs)
2. **All CSS styles are replicated** in the DOCX files through the reference template - ✅ Using `assets/templates/canvas-reference.docx` (see workflow docs)

---

## Current Status

### Files to Process
- **Total `_local.html` files**: 67 (excluding Start-Here)
  - Module-level: 5 files
  - Section-level: 22 files
  - LA-level: 40 files

### Existing DOCX Files (to preserve)
- `Start-Here/1-course-orientation/course_orientation.docx`
- `Start-Here/2-course-details/course_details.docx`
- `Start-Here/3-terms-of-use/terms_of_use.docx`

---

## Requirements Analysis

### 1. Image Embedding Verification

**Current Process:**
- `html-to-docx.py` converts relative image paths in HTML to relative paths in DOCX
- Pandoc should embed images automatically when given relative paths from HTML file location

**Potential Issue:**
- Pandoc's default behavior embeds images, but we need to verify this works correctly
- If images are linked (not embedded), the DOCX will be dependent on external files

**Solution:**
- Test Pandoc image embedding behavior with a sample file
- Verify that images are actually embedded (check DOCX file size and internal structure)
- If images are not embedded, add explicit embedding using Python `python-docx` library after Pandoc conversion

**Implementation Steps:**
1. Create a test conversion with images
2. Open DOCX in Word and verify images display without external files
3. Check DOCX XML structure to confirm images are in `word/media/` folder
4. If needed, add post-processing step to explicitly embed images using `python-docx`

### 2. CSS Style Replication Verification

**Current Process:**
- Reference DOCX template (`assets/templates/canvas-reference.docx`) contains Word styles
- HTML-to-DOCX script maps CSS classes to Word styles via `custom-style` attribute
- Pandoc uses reference DOCX to apply styles

**Potential Issues:**
- Not all CSS classes may be mapped to Word styles
- Some CSS properties (colors, fonts, spacing) may not be fully replicated
- Complex CSS (flexbox, grid, borders, shadows) won't translate to Word

**Solution:**
1. **Audit CSS Classes in HTML Files**
   - Scan all `_local.html` files to identify all CSS classes used
   - Compare against Word styles in reference template
   - Identify missing style mappings

2. **Enhance Reference Template**
   - Add any missing Word styles to reference DOCX
   - Ensure all callout styles (Note, Important, Instructions, Question, Callout) are present
   - Verify heading styles (H1-H6) match Canvas CSS exactly

3. **Verify Style Mapping Logic**
   - Review `html-to-docx.py` CSS class mapping (lines 329-378)
   - Ensure all identified CSS classes have corresponding Word style mappings
   - Test that mapped styles are actually applied in generated DOCX

4. **Post-Conversion Style Verification**
   - Open sample DOCX files in Word
   - Compare formatting against original HTML (viewed in browser)
   - Verify colors, fonts, spacing, borders match Canvas CSS

**Style Mapping Requirements:**

| CSS Class/Element | Word Style | Status |
|------------------|------------|--------|
| `h1` | Heading 1 (centered, 24pt, #1c205b) | ✅ Defined |
| `h2` | Heading 2 (21pt, #bf1722) | ✅ Defined |
| `h3` | Heading 3 (18pt, #1c205b, indent) | ✅ Defined |
| `h4` | Heading 4 (15pt, #111111, dashed border) | ✅ Defined |
| `h5` | Heading 5 (12pt, bold, #bf1722) | ✅ Defined |
| `.note` | Note (background #F1F5F7) | ✅ Defined |
| `.important` | Important (background #fafaae) | ✅ Defined |
| `.instructions` | Instructions (background #FAFFF0) | ✅ Defined |
| `.callout.instructions` | Instructions | ✅ Mapped |
| `.callout` | Callout (border) | ✅ Defined |
| `.question2`, `.questionBullet` | Question (background #FFECD5) | ✅ Mapped |
| `<p>` after H1 | Body Text | ✅ Mapped |
| `<p>` after H2 | Body Text 2 | ✅ Mapped |
| `<p>` after H3+ | Body Text 3 | ✅ Mapped |
| `<ul>` after H1 | List Bullet | ✅ Mapped |
| `<ul>` after H2 | List Bullet 2 | ✅ Mapped |
| `<ul>` after H3+ | List Bullet 3 | ✅ Mapped |
| `<ol>` after H1 | List Number | ✅ Mapped |
| `<ol>` after H2 | List Number 2 | ✅ Mapped |
| `<ol>` after H3+ | List Number 3 | ✅ Mapped |

---

## Established Process (From Existing Documentation)

The process is **already established** and documented. Key components:

### Main Script: `scripts/core/html-to-docx.py`
- Converts HTML to DOCX using Pandoc
- Uses reference DOCX template for styling: `assets/templates/canvas-reference.docx`
- Handles image embedding automatically (Pandoc embeds images when using relative paths)
- Maps CSS classes to Word styles
- Enables Track Changes mode

### Batch Script: `scripts/core/batch-generate-docx.py`
- Finds all `*_local.html` files
- Generates DOCX for each using `html-to-docx.py`
- Skips files that already have DOCX
- Reports success/failure summary

### Reference Documentation:
- **Workflow**: `docs/workflow/HTML-TO-DOCX-WORKFLOW.md`
- **Technical Details**: `docs/technical/DOCX-HTML-MAPPING.md`
- **Conversion Options**: `docs/technical/IMPROVED-CONVERSION-OPTIONS.md`
- **Phase 3 Plan**: `GENERATE-MISSING-SECTION-FILES-PLAN.md` (Phase 3)

### Reference Template: `assets/templates/canvas-reference.docx`
- Contains all Word styles matching Canvas CSS
- Used by Pandoc via `--reference-doc` option
- Ensures consistent styling across all DOCX files

---

## Proposed Implementation Plan (Based on Established Process)

### Phase 1: Verification (Using Established Process)

**Note:** The established process already handles image embedding and CSS style replication. This phase verifies it's working correctly.

#### Step 1.1: Verify Image Embedding
```bash
# Test with a sample file that has images
python3 scripts/core/html-to-docx.py \
  --html-file data/current/WINTER-25-26-UPDATES/Module-1/Section-1-2/section_2_images_local.html

# Verify (per established workflow):
# - Pandoc automatically embeds images when using relative paths
# - Working directory is set to HTML file's directory (line 452 in html-to-docx.py)
# - Open generated DOCX in Word to verify images display
# - Copy DOCX to different location - images should still display (embedded)
```

**Expected Result:** Images embedded in DOCX (Pandoc handles this automatically per workflow docs)

**Note:** The established process already handles this correctly. No modifications needed unless verification shows otherwise.

#### Step 1.2: Audit CSS Classes
```bash
# Create script to scan all _local.html files and extract CSS classes
python3 << 'PYTHON'
from pathlib import Path
from bs4 import BeautifulSoup
from collections import Counter

BASE_DIR = Path('data/current/WINTER-25-26-UPDATES')
local_files = [f for f in BASE_DIR.rglob('*_local.html') if 'Start-Here' not in str(f)]

all_classes = Counter()
for html_file in local_files:
    content = html_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.find_all(True, class_=True):
        classes = tag.get('class', [])
        if isinstance(classes, list):
            all_classes.update(classes)

print("All CSS classes found:")
for cls, count in all_classes.most_common():
    print(f"  {cls}: {count} files")
PYTHON
```

**Action:** Compare against Word styles in reference template, identify gaps

#### Step 1.3: Verify Reference Template Completeness
```bash
# Check what styles are in the reference template (per established process)
python3 << 'PYTHON'
from docx import Document
from pathlib import Path

ref_docx = Path('assets/templates/canvas-reference.docx')
doc = Document(str(ref_docx))
print("Styles in reference template:")
for style in doc.styles:
    print(f"  - {style.name}")
PYTHON
```

**Action:** Verify template has all needed styles. The template is created/updated using `scripts/utility/create-reference-docx.py` (see workflow docs)

#### Step 1.4: Test Style Mapping
```bash
# Convert a sample file with various CSS classes
python3 scripts/core/html-to-docx.py \
  --html-file data/current/WINTER-25-26-UPDATES/Module-1/Section-1-4/section_4_contrast_and_color_reliance_local.html

# Verify in Word:
# - Headings have correct colors and sizes
# - Callouts have correct backgrounds
# - Lists have correct indentation
# - Paragraphs after headings have correct styles
```

### Phase 2: Enhancements (If Needed)

**Note:** Per `docs/technical/IMPROVED-CONVERSION-OPTIONS.md`, the established Pandoc-based process is sufficient for our use case (structure-based mapping). Only enhance if verification reveals specific issues.

#### Step 2.1: Image Embedding Enhancement (if needed)
- Only needed if verification shows images aren't embedded
- The established process (Pandoc with relative paths) should handle this automatically
- See `docs/technical/IMPROVED-CONVERSION-OPTIONS.md` for alternatives if needed

#### Step 2.2: CSS Style Mapping Enhancement (if needed)
- Update reference template using `scripts/utility/create-reference-docx.py`
- Update CSS class mapping in `html-to-docx.py` if gaps identified
- See `docs/workflow/HTML-TO-DOCX-WORKFLOW.md` for current mapping approach

### Phase 3: Batch Generation

#### Step 3.1: Execute Batch Generation (Using Established Script)
```bash
# Use the established batch script (per GENERATE-MISSING-SECTION-FILES-PLAN.md Phase 3)
cd /Users/a00288946/Projects/canvas_2879
python3 scripts/core/batch-generate-docx.py
```

**The established script (`batch-generate-docx.py`) will:**
- Find all `*_local.html` files in `WINTER-25-26-UPDATES` structure
- Generate DOCX for each using `html-to-docx.py` (established process)
- Skip files that already have DOCX (will automatically preserve Start-Here files)
- Report success/failure for each file with detailed output
- Uses the established workflow from `docs/workflow/HTML-TO-DOCX-WORKFLOW.md`

#### Step 3.2: Verification
- Spot-check sample DOCX files from each level (Module, Section, LA)
- Verify images are embedded (test by moving DOCX to different location)
- Verify CSS styles are correctly applied
- Check file counts match expectations

---

## Detailed Requirements

### Requirement 1: Image Embedding

**Acceptance Criteria:**
1. ✅ All images referenced in HTML are present in DOCX
2. ✅ Images are embedded (not linked) - DOCX can be opened independently
3. ✅ Image quality is preserved (no compression artifacts)
4. ✅ Images display correctly in Word

**Technical Implementation:**
- Pandoc automatically embeds images when using relative paths
- Working directory must be set to HTML file's directory for path resolution
- Current implementation already does this (line 452 in `html-to-docx.py`)

**Verification Method:**
```python
# After conversion, verify images are embedded:
from docx import Document
from docx.oxml import OxmlElement
from zipfile import ZipFile

docx_path = Path('path/to/output.docx')
with ZipFile(docx_path, 'r') as zip:
    media_files = [f for f in zip.namelist() if f.startswith('word/media/')]
    print(f"Embedded images: {len(media_files)}")

doc = Document(str(docx_path))
# Count image elements in document
image_count = len(doc.part.rels.keys())
print(f"Image references: {image_count}")
```

### Requirement 2: CSS Style Replication

**Acceptance Criteria:**
1. ✅ All heading styles (H1-H6) match Canvas CSS colors, sizes, alignment
2. ✅ All callout styles (Note, Important, Instructions, Question, Callout) have correct backgrounds/borders
3. ✅ Body text styles after headings match hierarchy (Body Text, Body Text 2, Body Text 3)
4. ✅ List styles match hierarchy (List Bullet/Number, List Bullet/Number 2, List Bullet/Number 3)
5. ✅ Hyperlinks are blue and underlined
6. ✅ Paragraph spacing and indentation match Canvas CSS

**Technical Implementation:**
- Reference DOCX template contains all Word styles
- HTML-to-DOCX script maps CSS classes to Word styles via `custom-style` attribute
- Pandoc applies styles from reference DOCX

**Verification Method:**
```python
# Verify styles in generated DOCX:
from docx import Document

doc = Document('path/to/output.docx')
used_styles = set()
for para in doc.paragraphs:
    if para.style:
        used_styles.add(para.style.name)

print("Styles used in DOCX:")
for style in sorted(used_styles):
    print(f"  - {style}")
```

---

## Risk Mitigation

### Risk 1: Images Not Embedded
**Mitigation:**
- Test with sample file before batch generation
- If Pandoc doesn't embed, add explicit embedding step using `python-docx`
- Verify in Word after generation

### Risk 2: CSS Styles Not Fully Replicated
**Mitigation:**
- Audit all CSS classes before batch generation
- Compare against reference template styles
- Update template if gaps identified
- Test sample conversions

### Risk 3: Batch Generation Failures
**Mitigation:**
- Use existing `batch-generate-docx.py` which has error handling
- Process continues even if individual files fail
- Detailed error reporting for each failure
- Can re-run for failed files only

### Risk 4: Performance Issues (67 files)
**Mitigation:**
- Batch script processes files sequentially
- Each file conversion takes ~10-30 seconds
- Total time estimate: ~15-30 minutes
- Can be interrupted and resumed (skips existing DOCX)

---

## Success Criteria

✅ **All 67 DOCX files generated successfully**

✅ **Images:**
- All images from HTML are embedded in DOCX
- DOCX files can be opened independently (no external image dependencies)
- Image quality preserved

✅ **Styles:**
- Headings match Canvas CSS (colors, sizes, alignment)
- Callouts have correct backgrounds/borders
- Body text and lists follow hierarchy
- Hyperlinks are styled correctly
- Overall formatting matches Canvas appearance

✅ **Process:**
- Batch generation completes without manual intervention
- Failed files are clearly identified
- Process can be resumed if interrupted

---

## Next Steps

1. **Review and approve this proposal**
2. **Execute Phase 1 verification steps** (test image embedding, audit CSS classes)
3. **Implement enhancements** (if needed based on Phase 1 results)
4. **Execute Phase 3 batch generation**
5. **Verify results** (spot-check sample files)
6. **Report completion** with summary of generated files

---

## Estimated Timeline

- **Phase 1 (Verification)**: 30-60 minutes
- **Phase 2 (Enhancements)**: 0-60 minutes (if needed)
- **Phase 3 (Batch Generation)**: 15-30 minutes
- **Verification**: 15-30 minutes

**Total: 1-3 hours** (depending on whether enhancements are needed)

---

## Questions for Review

1. Should we proceed with Phase 1 verification before batch generation?
2. Are there any specific CSS classes or styles that are critical and must be verified?
3. Should we test with a small sample (e.g., 5 files) before processing all 67?
4. Are there any image-specific requirements (max size, format restrictions)?
