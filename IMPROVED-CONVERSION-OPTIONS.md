# Improved HTML to DOCX Conversion Options

## Current Status

**Current Approach:** Pandoc direct HTML → DOCX
- ✅ Handles images well (downloads and embeds)
- ⚠️ Limited CSS formatting support
- ✅ Good structural conversion (headings, lists, paragraphs)
- ✅ Works for mapping purposes (structure is what matters)

## Formatting Fidelity Requirements

For our use case (creating DOCX files that match HTML structure for tracked changes mapping), we need:

**Priority 1: Structure** ✅
- Heading hierarchy (h1, h2, h3) - **Pandoc handles this well**
- Paragraph breaks - **Pandoc handles this well**
- Lists (ul, ol) - **Pandoc handles this well**
- Text content - **Pandoc handles this well**

**Priority 2: Images** ✅
- Image embedding - **Pandoc handles this well** (we download images first)

**Priority 3: Formatting** ⚠️
- Colors, fonts, spacing - **Nice to have, not critical for mapping**
- Visual fidelity - **Not critical for mapping**

## Assessment

**For mapping purposes, Pandoc is sufficient** because:
- The mapping system matches text content and structure, not visual formatting
- We need structural alignment (paragraphs, headings) which Pandoc provides
- Visual formatting can be adjusted manually in Word if needed

**However, if we want better formatting preservation**, we have these options:

## Option 1: Headless Chrome/Chromium (Best CSS Fidelity)

**Pros:**
- Most accurate CSS rendering
- Pixel-perfect visual fidelity
- Handles all CSS (external, inline, complex layouts)

**Cons:**
- More complex setup
- Requires Chrome/Chromium installation
- Converts HTML → PDF → DOCX (two-step process)
- PDF → DOCX conversion may lose some editability

**Implementation:**
```bash
# Install Chrome headless (if not already installed)
# macOS: Chrome is usually installed

# Convert HTML → PDF
google-chrome --headless --disable-gpu --print-to-pdf=output.pdf input.html

# Convert PDF → DOCX (using Pandoc or other tool)
pandoc output.pdf -o output.docx
```

**Or using Puppeteer/Playwright:**
```python
from playwright.sync_api import sync_playwright

def html_to_pdf_to_docx(html_file, output_docx):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_file}")
        page.pdf(path="temp.pdf")
        browser.close()
    
    # Then convert PDF → DOCX
    subprocess.run(['pandoc', 'temp.pdf', '-o', output_docx])
```

## Option 2: LibreOffice Writer (Better CSS than Pandoc)

**Pros:**
- Better CSS support than Pandoc
- Direct HTML → DOCX conversion
- Handles more formatting than Pandoc
- Free and open source

**Cons:**
- Requires LibreOffice installation
- May not handle all CSS perfectly
- Still not pixel-perfect

**Implementation:**
```bash
# Install LibreOffice (macOS)
brew install --cask libreoffice

# Convert HTML → DOCX
soffice --headless --convert-to docx input.html --outdir output/
```

**Python wrapper:**
```python
def convert_with_libreoffice(html_file, output_docx):
    subprocess.run([
        'soffice',
        '--headless',
        '--convert-to', 'docx',
        '--outdir', str(output_docx.parent),
        str(html_file)
    ])
```

## Option 3: wkhtmltopdf + Pandoc

**Pros:**
- Good CSS rendering
- Converts HTML → PDF with CSS preserved

**Cons:**
- Two-step process (HTML → PDF → DOCX)
- PDF → DOCX loses some editability
- Requires wkhtmltopdf installation

**Implementation:**
```bash
# Install wkhtmltopdf
brew install wkhtmltopdf

# Convert HTML → PDF
wkhtmltopdf input.html output.pdf

# Convert PDF → DOCX
pandoc output.pdf -o output.docx
```

## Recommendation

### For Current Use Case (Mapping System)

**Stick with Pandoc** because:
1. ✅ Structure is what matters for mapping (Pandoc excels at this)
2. ✅ Images are handled well (we download them first)
3. ✅ Simple and reliable
4. ✅ Fast conversion
5. ⚠️ Formatting can be manually adjusted in Word if needed

### If Better Formatting is Needed

**Use LibreOffice Writer** because:
1. ✅ Better CSS support than Pandoc
2. ✅ Still direct HTML → DOCX (no PDF intermediate)
3. ✅ Maintains editability
4. ✅ Relatively simple setup
5. ⚠️ May need some manual adjustments still

### If Pixel-Perfect Fidelity is Required

**Use Headless Chrome** because:
1. ✅ Best CSS rendering
2. ✅ Handles complex layouts
3. ⚠️ More complex setup
4. ⚠️ Two-step conversion (HTML → PDF → DOCX)

## Implementation Plan

### Phase 1: Keep Pandoc (Current)
- Continue using Pandoc for structure-based conversion
- Document that formatting may need manual adjustment
- Focus on structural accuracy for mapping

### Phase 2: Add LibreOffice Option (If Needed)
- Add `--use-libreoffice` flag to `html-to-docx.py`
- Fallback to Pandoc if LibreOffice not available
- Test formatting preservation

### Phase 3: Add Chrome Headless Option (If Pixel-Perfect Needed)
- Add `--use-chrome` flag
- Implement HTML → PDF → DOCX pipeline
- Use for pages requiring perfect formatting

## Current Script Enhancement

We could enhance `html-to-docx.py` to support multiple backends:

```python
def convert_html_to_docx(html_content, output_docx_path, method='pandoc'):
    if method == 'pandoc':
        # Current implementation
        ...
    elif method == 'libreoffice':
        # Use LibreOffice
        ...
    elif method == 'chrome':
        # Use headless Chrome
        ...
```

## Decision

**For now: Keep Pandoc** - It's sufficient for our mapping use case.

**If formatting issues arise:** Add LibreOffice as an option.

**If pixel-perfect needed:** Implement Chrome headless option.

