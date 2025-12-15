#!/usr/bin/env python3
"""
Generate index.html from course-map.json on Box
"""
import json
import subprocess
import sys
import os

# Download course map using the verification script output
def get_course_map():
    """Get course map data by running the verification script"""
    script_path = os.path.join(os.path.dirname(__file__), '../../Agents/cursor-ops/canvas-courses/scripts/verify-course-map-box.js')

    # Instead, let's use curl to download directly
    import urllib.request
    import os

    token = os.environ.get('BOX_ACCESS_TOKEN')
    if not token:
        print("Error: BOX_ACCESS_TOKEN not set")
        sys.exit(1)

    url = "https://api.box.com/2.0/files/2072524659911/content"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error downloading course map: {e}")
        sys.exit(1)

def generate_html(course_map):
    """Generate HTML from course map"""
    pages = sorted(course_map.get('pages', []), key=lambda x: x.get('order', 0))

    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canvas Course DOCX Editor</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #24292e;
            background-color: #ffffff;
        }
        /* Canvas heading styles */
        h1 {
            text-align: center;
            font-size: 2em;
            color: #1c205b;
            margin: 0.5em 0;
        }
        h2 {
            font-size: 1.75em;
            line-height: 1.5;
            color: #bf1722;
            margin: 0.5em 0;
            border-bottom: none;
            text-align: right;
        }
        h3 {
            font-size: 1.5em;
            color: #1c205b;
            margin: 0.5em 0 0.5em 0.5em;
            text-align: right;
        }
        h4 {
            font-size: 1.25em;
            color: #111111;
            margin: 0.5em 0 0.5em 1.25em;
            border-bottom: 1px dashed #ccc;
            text-align: right;
        }
        a {
            color: #0366d6;
            text-decoration: none;
            font-size: 1em;
        }
        a:hover {
            text-decoration: underline;
        }
        ol, ul {
            margin-left: 20px;
        }
        li {
            margin: 5px 0;
            text-align: right;
        }
        .note {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 10px;
            margin: 20px 0;
        }
        /* Layout: text right aligned, links right aligned */
        .page-text {
            display: inline-block;
            text-align: right;
            margin-right: 50px;
        }
        .page-links {
            display: inline-block;
            margin-left: 0;
        }
        .docx-links {
            display: inline-block;
            margin-right: 30px;
        }
        .canvas-links {
            display: inline-block;
        }
        h2 .page-text, h3 .page-text, li .page-text {
            margin-right: 50px;
        }
    </style>
</head>
<body>
    <h1>Canvas Course DOCX Editor</h1>
    <p>Each page in the Canvas course has been converted into a docx file. All docx files are uploaded to Box. Each page has three links:</p>
    <ol>
        <li><strong>canvas:</strong> opens the Canvas course page in a new tab.</li>
        <li><strong>view docx:</strong> opens the docx file in the Box viewer.</li>
        <li><strong>edit docx:</strong> opens the docx file in the Box Microsoft Word Online editor.</li>
    </ol>
    <div class="note">
        <strong>Note:</strong> You will need to authenticate to Canvas and Box to use the links.
    </div>'''

    # Group pages by hierarchy
    current_module = None
    current_section = None
    subsection_count = 0

    for page in pages:
        title = page.get('title', '')
        page_id = page.get('id', '')
        box = page.get('box', {})
        canvas = page.get('canvas', {})
        github = page.get('github', {})

        box_url = box.get('file_url') or f"https://usu.app.box.com/file/{box.get('file_id', '')}"
        word_url = box.get('word_online_url') or f"https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId={box.get('file_id', '')}"
        canvas_url = canvas.get('url') or f"https://usucourses.instructure.com/courses/2879/pages/{page_id}"
        github_path = github.get('with_assets', {}).get('path', '')
        github_url = f"https://gjoeckel.github.io/canvas_2879/{page_id}" if github_path else ''

        is_module = title.lower().startswith('module ')
        is_section = title.lower().startswith('section ')

        if is_module:
            # Close previous lists
            if current_section:
                html += '\n    </ol>'
            if current_module:
                html += '\n    </ol>'

            current_module = page
            current_section = None
            subsection_count = 0

            html += f'\n    <h2><span class="page-text">{title}</span>'
            html += f' <span class="page-links">'
            html += f'<span class="docx-links"><a href="{box_url}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="{word_url}" target="_blank" rel="noopener noreferrer">edit docx</a></span>'
            if github_url:
                html += f'<span class="canvas-links"><a href="{canvas_url}" target="_blank" rel="noopener noreferrer">view canvas</a></span>'
            html += '</span></h2>\n    <ol>'

        elif is_section:
            current_section = page
            subsection_count = 0

            html += f'\n        <li><span class="page-text">{title}</span>'
            html += f' <span class="page-links">'
            html += f'<span class="docx-links"><a href="{box_url}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="{word_url}" target="_blank" rel="noopener noreferrer">edit docx</a></span>'
            if github_url:
                html += f'<span class="canvas-links"><a href="{canvas_url}" target="_blank" rel="noopener noreferrer">view canvas</a></span>'
            html += '</span></li>'

        else:
            # Regular page
            subsection_count += 1
            html += f'\n        <li><span class="page-text">{subsection_count}. {title}</span>'
            html += f' <span class="page-links">'
            html += f'<span class="docx-links"><a href="{box_url}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="{word_url}" target="_blank" rel="noopener noreferrer">edit docx</a></span>'
            if github_url:
                html += f'<span class="canvas-links"><a href="{canvas_url}" target="_blank" rel="noopener noreferrer">view canvas</a></span>'
            html += '</span></li>'

    # Close remaining lists
    if current_section:
        html += '\n    </ol>'
    if current_module:
        html += '\n    </ol>'

    html += '\n</body>\n</html>'

    return html

def main():
    print("📥 Downloading course map from Box...")
    course_map = get_course_map()
    print(f"✓ Loaded course map: {course_map.get('course', {}).get('name', 'Unknown')}")
    print(f"✓ Total pages: {len(course_map.get('pages', []))}")

    print("\n📝 Generating HTML...")
    html = generate_html(course_map)

    output_path = os.path.join(os.path.dirname(__file__), '../github-pages/index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ Generated {output_path}")

if __name__ == '__main__':
    main()
