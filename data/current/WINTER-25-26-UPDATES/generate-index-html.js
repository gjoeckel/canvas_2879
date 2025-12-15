#!/usr/bin/env node
/**
 * Generate index.html from course-map.json
 *
 * Preserves exact visual layout and CSS, only updates content from JSON
 */

import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const COURSE_MAP_FILE = join(__dirname, 'course-map.json');
const HTML_TEMPLATE_FILE = join(__dirname, '../../../github-pages/index.html');
const OUTPUT_FILE = join(__dirname, '../../../github-pages/index.html');

/**
 * Escape HTML entities
 */
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Generate page links HTML
 */
function generatePageLinks(page) {
  if (!page.box?.file_id || !page.canvas?.page_id) {
    return '';
  }

  const viewDocxUrl = page.box.file_url || `https://usu.app.box.com/file/${page.box.file_id}`;
  const editDocxUrl = page.box.word_online_url ||
    `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${page.box.file_id}&sharedAccessCode=`;
  // Fix path for GitHub Pages: remove ../ prefix to make it root-relative
  const viewCanvasUrl = page.github?.local_html_path
    ? page.github.local_html_path.replace(/^\.\.\//, '')
    : '';
  const editCanvasUrl = `https://usucourses.instructure.com/courses/2879/pages/${page.canvas.page_id}/edit`;

  return `<span class="page-links"><span class="docx-links"><a href="${escapeHtml(viewDocxUrl)}" target="_blank" rel="noopener noreferrer">view docx</a> | <a href="${escapeHtml(editDocxUrl)}" target="_blank" rel="noopener noreferrer">edit docx</a></span><span class="canvas-links"><a href="${escapeHtml(viewCanvasUrl)}" target="_blank" rel="noopener noreferrer">view canvas</a> | <a href="${escapeHtml(editCanvasUrl)}" target="_blank" rel="noopener noreferrer">edit canvas</a></span></span>`;
}

/**
 * Generate Start Here section HTML
 */
function generateStartHereHTML(startHere) {
  if (!startHere || !startHere.subfolders) {
    return '';
  }

  let html = '    <h2>Start Here</h2>\n    <ol>\n';

  for (const subfolder of startHere.subfolders) {
    const title = escapeHtml(subfolder.title);
    const links = generatePageLinks(subfolder);
    html += `        <li><span class="page-text">${title}</span> ${links}</li>\n`;
  }

  html += '    </ol>\n';
  return html;
}

/**
 * Generate Module HTML
 */
function generateModuleHTML(module) {
  const title = escapeHtml(module.title);
  const links = generatePageLinks(module);

  let html = `    <h2><span class="page-text">${title}</span> ${links}</h2>\n`;

  // Generate sections
  if (module.sections && module.sections.length > 0) {
    for (const section of module.sections) {
      html += generateSectionHTML(section);
    }
  }

  return html;
}

/**
 * Generate Section HTML
 */
function generateSectionHTML(section) {
  const title = escapeHtml(section.title);
  const links = generatePageLinks(section);

  let html = `    <h3><span class="page-text">${title}</span> ${links}</h3>\n`;

  // Generate LAs if they exist
  if (section.las && section.las.length > 0) {
    html += '    <ol>\n';
    for (const la of section.las) {
      const laTitle = escapeHtml(la.title);
      const laLinks = generatePageLinks(la);
      html += `        <li><span class="page-text">${laTitle}</span> ${laLinks}</li>\n`;
    }
    html += '    </ol>\n';
  }

  return html;
}

/**
 * Main function
 */
async function main() {
  console.log('📖 Reading course-map.json...');
  const courseMap = JSON.parse(readFileSync(COURSE_MAP_FILE, 'utf8'));

  console.log('📖 Reading HTML template...');
  const htmlTemplate = readFileSync(HTML_TEMPLATE_FILE, 'utf8');

  // Find the insertion point (after the note div, before closing body)
  const noteEndIndex = htmlTemplate.indexOf('    </div>');
  const bodyStartIndex = htmlTemplate.indexOf('<body>');
  const bodyEndIndex = htmlTemplate.indexOf('</body>');

  if (noteEndIndex === -1 || bodyEndIndex === -1) {
    throw new Error('Could not find HTML structure markers');
  }

  // Extract header and footer
  const header = htmlTemplate.substring(0, htmlTemplate.indexOf('    <h2>Start Here</h2>'));
  const footer = htmlTemplate.substring(bodyEndIndex);

  // Generate content
  console.log('🏗️  Generating HTML content...');
  let content = '';

  // Generate Start Here section
  if (courseMap.start_here) {
    content += generateStartHereHTML(courseMap.start_here);
  }

  // Generate Modules
  if (courseMap.modules && courseMap.modules.length > 0) {
    for (const module of courseMap.modules) {
      content += generateModuleHTML(module);
    }
  }

  // Combine
  const newHTML = header + content + footer;

  // Write output
  console.log('💾 Writing index.html...');
  writeFileSync(OUTPUT_FILE, newHTML, 'utf8');

  console.log('✅ HTML generation complete!');
  console.log(`📄 Updated: ${OUTPUT_FILE}`);
}

main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

