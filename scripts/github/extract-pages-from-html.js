#!/usr/bin/env node
/**
 * Extract all pages from HTML and update course map
 *
 * Parses the HTML structure to extract:
 * - Start Here pages
 * - Module pages
 * - Section pages
 * - Individual pages within sections
 */

import { readFileSync, writeFileSync } from 'fs';

const HTML_FILE_PATH = '/Users/a00288946/Projects/canvas_2879/github-pages/index.html';
const COURSE_MAP_PATH = '/Users/a00288946/Projects/canvas_2879/data/current/WINTER-25-26-UPDATES/course-map.json';

// Read HTML
const html = readFileSync(HTML_FILE_PATH, 'utf-8');

// Extract pages from HTML - handle both old format (view docx | edit docx | view canvas)
// and new format (view docx | edit docx [10px] view canvas | edit canvas)
const pages = [];

// Pattern to match page entries in various formats
// Matches: <li><span class="page-text">Title</span> <span class="page-links">...</span></li>
// or: <h2/h3><span class="page-text">Title</span> <span class="page-links">...</span></h2/h3>
const pagePattern = /<(?:h2|h3|li)><span class="page-text">([^<]+)<\/span>\s*<span class="page-links">([^<]*(?:<[^>]+>[^<]*<\/[^>]+>[^<]*)*?)<\/span><\/(?:h2|h3|li)>/g;

let match;
while ((match = pagePattern.exec(html)) !== null) {
  const title = match[1].trim();
  const linksHtml = match[2];

  // Extract Box file ID from view docx link
  const viewDocxMatch = linksHtml.match(/href="([^"]*\/file\/(\d+)[^"]*)"[^>]*>view docx<\/a>/);
  if (!viewDocxMatch) continue;

  const viewDocxUrl = viewDocxMatch[1];
  const boxFileId = viewDocxMatch[2];

  // Extract edit docx URL
  const editDocxMatch = linksHtml.match(/href="([^"]*fileId=(\d+)[^"]*)"[^>]*>edit docx<\/a>/);
  const editDocxUrl = editDocxMatch ? editDocxMatch[1] : `https://usu.app.box.com/integrations/officeonline/openOfficeOnline?fileId=${boxFileId}`;

  // Extract view canvas URL (GitHub Pages)
  const viewCanvasMatch = linksHtml.match(/href="([^"]*github\.io[^"]*)"[^>]*>view canvas<\/a>/);
  const viewCanvasUrl = viewCanvasMatch ? viewCanvasMatch[1] : null;

  // Extract edit canvas URL (Canvas)
  const editCanvasMatch = linksHtml.match(/href="([^"]*usucourses\.instructure\.com[^"]*)"[^>]*>(?:edit|view) canvas<\/a>/);
  const editCanvasUrl = editCanvasMatch ? editCanvasMatch[1] : null;

  // Extract Canvas page slug from URL
  const canvasSlugMatch = editCanvasUrl ? editCanvasUrl.match(/\/pages\/([^"?#]+)/) : null;
  const canvasSlug = canvasSlugMatch ? canvasSlugMatch[1] : null;

  // Determine page type based on context
  let pageType = 'page';
  if (title.toLowerCase().startsWith('module')) {
    pageType = 'module';
  } else if (title.toLowerCase().startsWith('section')) {
    pageType = 'section';
  }

  pages.push({
    title,
    boxFileId,
    boxViewUrl: viewDocxUrl,
    boxEditUrl: editDocxUrl,
    viewCanvasUrl,
    canvasEditUrl: editCanvasUrl,
    canvasSlug,
    type: pageType
  });
}

console.log(`Found ${pages.length} pages in HTML`);
console.log('\nSample pages:');
pages.slice(0, 10).forEach((p, i) => {
  console.log(`${i + 1}. [${p.type}] ${p.title} (Box: ${p.boxFileId}, Canvas: ${p.canvasSlug || 'N/A'})`);
});

// Read the course map
const courseMap = JSON.parse(readFileSync(COURSE_MAP_PATH, 'utf-8'));

// Create maps for quick lookup
const existingPagesByBoxId = new Map();
const existingPagesByCanvasSlug = new Map();

courseMap.pages.forEach(page => {
  if (page.box?.file_id) {
    existingPagesByBoxId.set(page.box.file_id, page);
  }
  if (page.canvas?.page_id) {
    existingPagesByCanvasSlug.set(page.canvas.page_id, page);
  }
});

// Update or add pages
let updated = 0;
let added = 0;
let order = 1;

pages.forEach((htmlPage) => {
  const existingPage = existingPagesByBoxId.get(htmlPage.boxFileId) ||
                       existingPagesByCanvasSlug.get(htmlPage.canvasSlug);

  if (existingPage) {
    // Update existing page
    existingPage.title = htmlPage.title;
    if (existingPage.box) {
      existingPage.box.file_url = htmlPage.boxViewUrl;
      existingPage.box.word_online_url = htmlPage.boxEditUrl;
    } else {
      existingPage.box = {
        file_id: htmlPage.boxFileId,
        file_name: `${htmlPage.title}.docx`,
        file_url: htmlPage.boxViewUrl,
        word_online_url: htmlPage.boxEditUrl,
        folder_id: null,
        modified_at: null,
        version: 1
      };
    }
    if (htmlPage.canvasSlug && existingPage.canvas) {
      existingPage.canvas.url = htmlPage.canvasEditUrl;
      existingPage.canvas.page_id = htmlPage.canvasSlug;
    }
    if (!existingPage.metadata) {
      existingPage.metadata = {};
    }
    existingPage.metadata.type = htmlPage.type;
    if (!existingPage.order) {
      existingPage.order = order++;
    }
    updated++;
  } else {
    // Add new page
    const newPage = {
      id: htmlPage.canvasSlug || `page-${htmlPage.boxFileId}`,
      slug: htmlPage.canvasSlug || `page-${htmlPage.boxFileId}`,
      title: htmlPage.title,
      order: order++,
      status: "draft",
      canvas: {
        url: htmlPage.canvasEditUrl || null,
        page_id: htmlPage.canvasSlug || null,
        published: false,
        published_at: null
      },
      github: {
        repository: "main",
        source_docx: {
          path: null,
          branch: "main"
        },
        canvas_copy: {
          path: null,
          branch: "main"
        },
        with_assets: {
          path: htmlPage.viewCanvasUrl ?
            htmlPage.viewCanvasUrl.replace('https://gjoeckel.github.io/canvas_2879/', '') : null,
          branch: "main"
        }
      },
      box: {
        file_id: htmlPage.boxFileId,
        file_name: `${htmlPage.title}.docx`,
        file_url: htmlPage.boxViewUrl,
        word_online_url: htmlPage.boxEditUrl,
        folder_id: null,
        modified_at: null,
        version: 1
      },
      sync: {
        last_synced: null,
        sync_status: "pending",
        sync_errors: []
      },
      metadata: {
        type: htmlPage.type,
        created: new Date().toISOString()
      }
    };

    courseMap.pages.push(newPage);
    added++;
  }
});

// Sort pages by order
courseMap.pages.sort((a, b) => (a.order || 999) - (b.order || 999));

// Update metadata
courseMap.metadata.last_updated = new Date().toISOString();

// Write updated course map
writeFileSync(COURSE_MAP_PATH, JSON.stringify(courseMap, null, 2), 'utf-8');

console.log(`\n✅ Course map updated:`);
console.log(`   Updated: ${updated} pages`);
console.log(`   Added: ${added} pages`);
console.log(`   Total pages: ${courseMap.pages.length}`);
