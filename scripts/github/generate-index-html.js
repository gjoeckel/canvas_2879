#!/usr/bin/env node
/**
 * Generate clean index.html from course map
 *
 * Preserves the page list structure from GitHub Pages with new link format:
 * view docx | edit docx [10px whitespace] view canvas | edit canvas
 */

import { readFileSync, writeFileSync } from 'fs';

// Configuration
const COURSE_MAP_PATH = '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/course-map.json';
const HTML_FILE_PATH = '/Users/a00288946/Projects/canvas_2879/github-pages/index.html';
const GITHUB_PAGES_BASE = 'https://gjoeckel.github.io/canvas_2879';

// Read course map
const courseMap = JSON.parse(readFileSync(COURSE_MAP_PATH, 'utf-8'));

// Function to generate GitHub Pages URL from course map path
function getGitHubPagesUrl(githubPath) {
  if (!githubPath) return null;
  // Remove 'pages/' prefix if present, as GitHub Pages serves from repo root
  const cleanPath = githubPath.replace(/^pages\//, '').replace(/\/index\.html$/, '');
  return `${GITHUB_PAGES_BASE}/${cleanPath}`;
}

// Function to generate link HTML
function generateLinks(page) {
  const viewDocxUrl = page.box?.file_url || '#';
  const editDocxUrl = page.box?.word_online_url || '#';
  const viewCanvasUrl = page.github?.with_assets?.path
    ? getGitHubPagesUrl(page.github.with_assets.path)
    : null;
  const editCanvasUrl = page.canvas?.url || '#';

  let links = `<a href="${viewDocxUrl}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="${editDocxUrl}" target="_blank" rel="noopener noreferrer">edit docx</a>`;
  links += ' <span style="margin-left: 10px;"></span> ';

  if (viewCanvasUrl) {
    links += `<a href="${viewCanvasUrl}" target="_blank" rel="noopener noreferrer">view canvas</a>`;
  } else {
    links += `<span style="color: #999;">view canvas</span>`;
  }

  links += ' | ';
  links += `<a href="${editCanvasUrl}" target="_blank" rel="noopener noreferrer">edit canvas</a>`;

  return links;
}

// Organize pages by type and order
const modules = courseMap.pages.filter(p => p.metadata?.type === 'module').sort((a, b) => a.order - b.order);
const sections = courseMap.pages.filter(p => p.metadata?.type === 'section').sort((a, b) => a.order - b.order);
const pages = courseMap.pages.filter(p => !p.metadata?.type || (p.metadata?.type !== 'module' && p.metadata?.type !== 'section')).sort((a, b) => a.order - b.order);

// Group sections by module (based on order)
// For now, we'll organize based on the structure from the web page
// Module 1: Sections 1-5 (orders 6-10)
// Module 2: Sections 11-13 (orders 11-13)
// Module 3: Section 14 (order 14)
// Module 4: Section 15 (order 15)
// Module 5: Section 16 (order 16)

const module1Sections = sections.filter(s => s.order >= 6 && s.order <= 10);
const module2Sections = sections.filter(s => s.order >= 11 && s.order <= 13);
const module3Sections = sections.filter(s => s.order === 14);
const module4Sections = sections.filter(s => s.order === 15);
const module5Sections = sections.filter(s => s.order === 16);

// Build HTML
let html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canvas Course DOCX Editor</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
            border-left: 4px solid #0066cc;
            padding-left: 15px;
        }
        h3 {
            color: #666;
            margin-top: 20px;
            margin-left: 20px;
        }
        .note {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
        }
        .page-text {
            font-weight: 500;
        }
        .page-links {
            font-size: 0.9em;
            margin-left: 10px;
        }
        .page-links a {
            color: #0066cc;
            text-decoration: none;
        }
        .page-links a:hover {
            text-decoration: underline;
        }
        ol {
            margin-left: 40px;
        }
        li {
            margin: 8px 0;
        }
    </style>
</head>
<body>
    <h1>Canvas Course DOCX Editor</h1>
    <p>Each page in the Canvas course has been converted into a DOCX file and uploaded to Box. Each page listed below has four links:</p>
    <ul>
        <li><strong>view docx:</strong> opens the docx file in the Box viewer.</li>
        <li><strong>edit docx:</strong> opens the docx file in the Box Microsoft Word Online editor.</li>
        <li><strong>view canvas:</strong> opens an HTML file with page content.</li>
        <li><strong>edit canvas:</strong> opens the Canvas page for editing.</li>
    </ul>
    <div class="note">
        <strong>Note:</strong> You will need to authenticate to Canvas and Box to use the links.
    </div>`;

// Add modules
modules.forEach(module => {
  html += `\n    <h2><span class="page-text">${module.title.replace(/_/g, ' ')}</span> <span class="page-links">${generateLinks(module)}</span></h2>`;

  // Add sections for this module
  let moduleSections = [];
  if (module.order === 1) moduleSections = module1Sections;
  else if (module.order === 2) moduleSections = module2Sections;
  else if (module.order === 3) moduleSections = module3Sections;
  else if (module.order === 4) moduleSections = module4Sections;
  else if (module.order === 5) moduleSections = module5Sections;

  if (moduleSections.length > 0) {
    html += `\n    <ol>`;
    moduleSections.forEach(section => {
      html += `\n        <li><span class="page-text">${section.title.replace(/_/g, ' ')}</span> <span class="page-links">${generateLinks(section)}</span></li>`;
    });
    html += `\n    </ol>`;
  }
});

html += `\n</body>\n</html>`;

// Write HTML file
writeFileSync(HTML_FILE_PATH, html, 'utf-8');

console.log('✅ Generated clean index.html from course map');
console.log(`   File: ${HTML_FILE_PATH}`);
console.log(`   Modules: ${modules.length}`);
console.log(`   Sections: ${sections.length}`);
console.log(`   Pages: ${pages.length}`);
