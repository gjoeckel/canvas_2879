#!/usr/bin/env python3
"""
Create a reference DOCX template with styles matching the Canvas CSS.

This reference DOCX can be used with Pandoc's --reference-doc option
to apply consistent styling when converting HTML to DOCX.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path

def create_reference_docx(output_path):
    """Create a reference DOCX with custom styles matching Canvas CSS."""
    doc = Document()

    # Remove default content
    doc._body.clear_content()

    # Define styles based on AD-365-V4.css and canvas-custom-overrides.css

    # H1 Style: Centered, 2em, color #1c205b
    h1_style = doc.styles['Heading 1']
    h1_font = h1_style.font
    h1_font.size = Pt(24)  # 2em ≈ 24pt
    h1_font.color.rgb = RGBColor(0x1c, 0x20, 0x5b)  # #1c205b
    h1_style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    h1_style.paragraph_format.space_after = Pt(12)

    # H2 Style: 1.75em, color #bf1722, no border
    h2_style = doc.styles['Heading 2']
    h2_font = h2_style.font
    h2_font.size = Pt(21)  # 1.75em ≈ 21pt
    h2_font.color.rgb = RGBColor(0xbf, 0x17, 0x22)  # #bf1722
    h2_style.paragraph_format.space_before = Pt(6)
    h2_style.paragraph_format.space_after = Pt(6)

    # H3 Style: 1.5em, color #1c205b
    h3_style = doc.styles['Heading 3']
    h3_font = h3_style.font
    h3_font.size = Pt(18)  # 1.5em ≈ 18pt
    h3_font.color.rgb = RGBColor(0x1c, 0x20, 0x5b)  # #1c205b
    h3_style.paragraph_format.left_indent = Inches(0.5)
    h3_style.paragraph_format.space_before = Pt(6)
    h3_style.paragraph_format.space_after = Pt(6)

    # H4 Style: 1.25em, color #111111, dashed border-bottom
    h4_style = doc.styles['Heading 4']
    h4_font = h4_style.font
    h4_font.size = Pt(15)  # 1.25em ≈ 15pt
    h4_font.color.rgb = RGBColor(0x11, 0x11, 0x11)  # #111111
    h4_style.paragraph_format.left_indent = Inches(1.25)
    h4_style.paragraph_format.space_before = Pt(6)
    h4_style.paragraph_format.space_after = Pt(6)
    # Add border-bottom (dashed) - requires XML manipulation
    h4_pPr = h4_style._element.get_or_add_pPr()
    h4_pBdr = OxmlElement('w:pBdr')
    h4_bottom = OxmlElement('w:bottom')
    h4_bottom.set(qn('w:val'), 'dashed')
    h4_bottom.set(qn('w:sz'), '4')
    h4_bottom.set(qn('w:space'), '1')
    h4_bottom.set(qn('w:color'), 'CCCCCC')
    h4_pBdr.append(h4_bottom)
    h4_pPr.append(h4_pBdr)

    # H5 Style: 1em, bold, color #bf1722
    h5_style = doc.styles['Heading 5']
    h5_font = h5_style.font
    h5_font.size = Pt(12)  # 1em = 12pt
    h5_font.bold = True
    h5_font.color.rgb = RGBColor(0xbf, 0x17, 0x22)  # #bf1722
    h5_style.paragraph_format.left_indent = Inches(2)
    h5_style.paragraph_format.space_before = Pt(6)
    h5_style.paragraph_format.space_after = Pt(6)

    # Normal paragraph style: margin-left: 0em, margin-right: 2em
    normal_style = doc.styles['Normal']
    normal_style.paragraph_format.right_indent = Inches(2)

    # Create custom styles for callouts

    # Note style: background #F1F5F7
    if 'Note' not in [s.name for s in doc.styles]:
        note_style = doc.styles.add_style('Note', 1)  # Paragraph style
        note_style.base_style = doc.styles['Normal']
        note_pPr = note_style._element.get_or_add_pPr()
        note_shd = OxmlElement('w:shd')
        note_shd.set(qn('w:fill'), 'F1F5F7')
        note_pPr.append(note_shd)
        note_style.paragraph_format.left_indent = Inches(0)
        note_style.paragraph_format.right_indent = Inches(0)
        note_style.paragraph_format.space_before = Pt(6)
        note_style.paragraph_format.space_after = Pt(6)

    # Important style: background #fafaae
    if 'Important' not in [s.name for s in doc.styles]:
        important_style = doc.styles.add_style('Important', 1)
        important_style.base_style = doc.styles['Normal']
        important_pPr = important_style._element.get_or_add_pPr()
        important_shd = OxmlElement('w:shd')
        important_shd.set(qn('w:fill'), 'FAFAAE')
        important_pPr.append(important_shd)
        important_style.paragraph_format.left_indent = Inches(0)
        important_style.paragraph_format.right_indent = Inches(0)
        important_style.paragraph_format.space_before = Pt(6)
        important_style.paragraph_format.space_after = Pt(6)

    # Instructions style: background #FAFFF0
    if 'Instructions' not in [s.name for s in doc.styles]:
        instructions_style = doc.styles.add_style('Instructions', 1)
        instructions_style.base_style = doc.styles['Normal']
        instructions_pPr = instructions_style._element.get_or_add_pPr()
        instructions_shd = OxmlElement('w:shd')
        instructions_shd.set(qn('w:fill'), 'FAFFF0')
        instructions_pPr.append(instructions_shd)
        instructions_style.paragraph_format.left_indent = Inches(0)
        instructions_style.paragraph_format.right_indent = Inches(0)
        instructions_style.paragraph_format.space_before = Pt(18)
        instructions_style.paragraph_format.space_after = Pt(12)

    # Instructions-callout style: for div.callout.instructions
    if 'instructions-callout' not in [s.name for s in doc.styles]:
        instructions_callout_style = doc.styles.add_style('instructions-callout', 1)
        instructions_callout_style.base_style = doc.styles['Normal']
        instructions_callout_pPr = instructions_callout_style._element.get_or_add_pPr()
        # Background
        instructions_callout_shd = OxmlElement('w:shd')
        instructions_callout_shd.set(qn('w:fill'), 'FAFFF0')
        instructions_callout_pPr.append(instructions_callout_shd)
        # Border
        instructions_callout_pBdr = OxmlElement('w:pBdr')
        for side in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{side}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4')
            border.set(qn('w:space'), '1')
            border.set(qn('w:color'), 'CCCCCC')
            instructions_callout_pBdr.append(border)
        instructions_callout_pPr.append(instructions_callout_pBdr)
        instructions_callout_style.paragraph_format.left_indent = Inches(0.5)
        instructions_callout_style.paragraph_format.right_indent = Inches(0.5)
        instructions_callout_style.paragraph_format.space_before = Pt(12)
        instructions_callout_style.paragraph_format.space_after = Pt(12)

    # Callout-box style: for div.callout
    if 'callout-box' not in [s.name for s in doc.styles]:
        callout_box_style = doc.styles.add_style('callout-box', 1)
        callout_box_style.base_style = doc.styles['Normal']
        callout_box_pPr = callout_box_style._element.get_or_add_pPr()
        # Border
        callout_box_pBdr = OxmlElement('w:pBdr')
        for side in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{side}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4')
            border.set(qn('w:space'), '1')
            border.set(qn('w:color'), 'CCCCCC')
            callout_box_pBdr.append(border)
        callout_box_pPr.append(callout_box_pBdr)
        callout_box_style.paragraph_format.left_indent = Inches(0.5)
        callout_box_style.paragraph_format.right_indent = Inches(0.5)
        callout_box_style.paragraph_format.space_before = Pt(12)
        callout_box_style.paragraph_format.space_after = Pt(12)

    # Question style: background #FFECD5
    if 'Question' not in [s.name for s in doc.styles]:
        question_style = doc.styles.add_style('Question', 1)
        question_style.base_style = doc.styles['Normal']
        question_pPr = question_style._element.get_or_add_pPr()
        question_shd = OxmlElement('w:shd')
        question_shd.set(qn('w:fill'), 'FFECD5')
        question_pPr.append(question_shd)
        question_style.paragraph_format.left_indent = Inches(0)
        question_style.paragraph_format.right_indent = Inches(0)
        question_style.paragraph_format.space_before = Pt(6)
        question_style.paragraph_format.space_after = Pt(6)

    # Callout style: border, padding
    if 'Callout' not in [s.name for s in doc.styles]:
        callout_style = doc.styles.add_style('Callout', 1)
        callout_style.base_style = doc.styles['Normal']
        callout_pPr = callout_style._element.get_or_add_pPr()
        # Border
        callout_pBdr = OxmlElement('w:pBdr')
        for side in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{side}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4')
            border.set(qn('w:space'), '1')
            border.set(qn('w:color'), 'CCCCCC')
            callout_pBdr.append(border)
        callout_pPr.append(callout_pBdr)
        callout_style.paragraph_format.left_indent = Inches(0.5)
        callout_style.paragraph_format.right_indent = Inches(0.5)
        callout_style.paragraph_format.space_before = Pt(12)
        callout_style.paragraph_format.space_after = Pt(12)

    # Hyperlink style: blue and underlined (for "View original page on Canvas" link)
    # Word has a built-in Hyperlink style, but we'll ensure it's properly configured
    try:
        hyperlink_style = doc.styles['Hyperlink']
    except KeyError:
        # If it doesn't exist, create it as a character style
        hyperlink_style = doc.styles.add_style('Hyperlink', WD_STYLE_TYPE.CHARACTER)

    hyperlink_font = hyperlink_style.font
    hyperlink_font.color.rgb = RGBColor(0x00, 0x00, 0xFF)  # Blue (#0000FF)
    hyperlink_font.underline = True

    # Save the document
    doc.save(output_path)
    print(f"✅ Reference DOCX created: {output_path}")
    print(f"\n📋 Styles defined:")
    print(f"   - Heading 1: Centered, 24pt, #1c205b")
    print(f"   - Heading 2: 21pt, #bf1722")
    print(f"   - Heading 3: 18pt, #1c205b, left indent")
    print(f"   - Heading 4: 15pt, #111111, dashed border-bottom")
    print(f"   - Heading 5: 12pt, bold, #bf1722")
    print(f"   - Note: Background #F1F5F7")
    print(f"   - Important: Background #fafaae")
    print(f"   - Instructions: Background #FAFFF0")
    print(f"   - Question: Background #FFECD5")
    print(f"   - Callout: Border, padding")
    print(f"\n💡 You can open this file in Word to further customize styles if needed.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create a reference DOCX template with Canvas CSS styles')
    parser.add_argument('--output', type=Path, default=Path('canvas-reference.docx'),
                       help='Output path for reference DOCX (default: canvas-reference.docx)')
    args = parser.parse_args()

    create_reference_docx(args.output)

