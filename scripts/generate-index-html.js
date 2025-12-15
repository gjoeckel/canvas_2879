#!/usr/bin/env node
/**
 * Generate index.html from course-map.json on Box
 * Updates the file with all pages and proper styling
 */

import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Import Box client
let getBoxClient;
try {
  const boxClientModule = await import('../../Agents/cursor-ops/mcp-box-minimal/dist/box-client.js');
  getBoxClient = boxClientModule.getBoxClient;
} catch (e) {
  console.error('❌ Box client not available:', e.message);
  process.exit(1);
}

async function downloadCourseMap() {
  const boxClient = getBoxClient();
  const fileStream = await boxClient.downloads.downloadFile('2072524659911');

  const chunks = [];
  for await (const chunk of fileStream) {
    chunks.push(chunk);
  }
  const fileBuffer = Buffer.concat(chunks);
  return JSON.parse(fileBuffer.toString('utf-8'));
}

function generateHTML(courseMap) {
  const pages = courseMap.pages.sort((a, b) => (a.order || 0) - (b.order || 0));

  let html = `<!DOCTYPE html>
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
        h2, h3, h4, li {
            overflow: hidden;
            text-align: right;
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
    </div>`;

  // Group pages by module/section structure
  const modules = [];
  const sections = {};
  const subsections = {};

  pages.forEach(page => {
    const title = page.title;
    const id = page.id;

    // Determine hierarchy from title
    if (title.toLowerCase().startsWith('module ')) {
      modules.push(page);
    } else if (title.toLowerCase().startsWith('section ')) {
      // Find parent module
      const moduleOrder = Math.floor((page.order || 0) / 100) || 1;
      if (!sections[moduleOrder]) sections[moduleOrder] = [];
      sections[moduleOrder].push(page);
    } else {
      // Sub-page - find parent section
      const sectionOrder = Math.floor((page.order || 0) / 10) || 1;
      if (!subsections[sectionOrder]) subsections[sectionOrder] = [];
      subsections[sectionOrder].push(page);
    }
  });

  // Generate HTML structure
  let currentModule = null;
  let currentSection = null;

  pages.forEach((page, index) => {
    const title = page.title;
    const isModule = title.toLowerCase().startsWith('module ');
    const isSection = title.toLowerCase().startsWith('section ');

    if (isModule) {
      if (currentSection) {
        html += '</ol>';
      }
      if (currentModule) {
        html += '</ol>';
      }
      currentModule = page;
      currentSection = null;

      const boxUrl = page.box?.file_url || `https://usu.app.box.com/file/${page.box?.file_id}`;
      const wordUrl = page.box?.word_online_url || `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${page.box?.file_id}`;
      const canvasUrl = page.canvas?.url || `https://usucourses.instructure.com/courses/2879/pages/${page.id}`;
      const githubUrl = page.github?.with_assets?.path ? `https://gjoeckel.github.io/canvas_2879/${page.id}` : '';

      html += `\n    <h2><span class="page-text">${title}</span>`;
      html += ` <span class="page-links">`;
      html += `<span class="docx-links"><a href="${boxUrl}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="${wordUrl}" target="_blank" rel="noopener noreferrer">edit docx</a></span>`;
      if (githubUrl) {
        html += `<span class="canvas-links"><a href="${githubUrl}" target="_blank" rel="noopener noreferrer">view canvas</a></span>`;
      }
      html += `</span></h2>\n    <ol>`;

    } else if (isSection) {
      currentSection = page;

      const boxUrl = page.box?.file_url || `https://usu.app.box.com/file/${page.box?.file_id}`;
      const wordUrl = page.box?.word_online_url || `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${page.box?.file_id}`;
      const canvasUrl = page.canvas?.url || `https://usucourses.instructure.com/courses/2879/pages/${page.id}`;
      const githubUrl = page.github?.with_assets?.path ? `https://gjoeckel.github.io/canvas_2879/${page.id}` : '';

      html += `\n        <li><span class="page-text">${title}</span>`;
      html += ` <span class="page-links">`;
      html += `<span class="docx-links"><a href="${boxUrl}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="${wordUrl}" target="_blank" rel="noopener noreferrer">edit docx</a></span>`;
      if (githubUrl) {
        html += `<span class="canvas-links"><a href="${githubUrl}" target="_blank" rel="noopener noreferrer">view canvas</a></span>`;
      }
      html += `</span></li>`;

    } else {
      // Sub-page
      const boxUrl = page.box?.file_url || `https://usu.app.box.com/file/${page.box?.file_id}`;
      const wordUrl = page.box?.word_online_url || `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${page.box?.file_id}`;
      const canvasUrl = page.canvas?.url || `https://usucourses.instructure.com/courses/2879/pages/${page.id}`;
      const githubUrl = page.github?.with_assets?.path ? `https://gjoeckel.github.io/canvas_2879/${page.id}` : '';

      // Find order within section
      const orderInList = (page.order || 0) % 10 || 1;

      html += `\n        <li><span class="page-text">${orderInList}. ${title}</span>`;
      html += ` <span class="page-links">`;
      html += `<span class="docx-links"><a href="${boxUrl}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="${wordUrl}" target="_blank" rel="noopener noreferrer">edit docx</a></span>`;
      if (githubUrl) {
        html += `<span class="canvas-links"><a href="${githubUrl}" target="_blank" rel="noopener noreferrer">view canvas</a></span>`;
      }
      html += `</span></li>`;
    }
  });

  if (currentSection) {
    html += '\n    </ol>';
  }
  if (currentModule) {
    html += '\n    </ol>';
  }

  html += `\n</body>\n</html>`;

  return html;
}

async function main() {
  try {
    console.log('📥 Downloading course map from Box...');
    const courseMap = await downloadCourseMap();
    console.log(`✓ Loaded course map: ${courseMap.course?.name || 'Unknown'}`);
    console.log(`✓ Total pages: ${courseMap.pages.length}`);

    console.log('\n📝 Generating HTML...');
    const html = generateHTML(courseMap);

    const outputPath = join(__dirname, '../github-pages/index.html');
    writeFileSync(outputPath, html);
    console.log(`\n✅ Generated ${outputPath}`);

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
